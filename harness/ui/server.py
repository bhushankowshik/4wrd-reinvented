"""FastAPI server — structured web app for the 4WRD harness.

Spawns the harness CLI inside a pty, parses its stdout line-by-line into
typed JSON events, and streams those events over WebSocket to a single-page
web app. No raw terminal — all operator interaction happens through forms
and panels rendered by the browser.

Run with: ./run.sh    (or: uvicorn ui.server:app --port 8080)
"""
from __future__ import annotations

import asyncio
import fcntl
import json
import os
import pty
import re
import signal
import struct
import termios
import time
from pathlib import Path
from typing import Any, Awaitable, Callable

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


HERE = Path(__file__).parent
STATIC = HERE / "static"
REPO_ROOT = HERE.parent  # the harness/ directory — where `uv run` resolves


app = FastAPI(title="4WRD Harness UI")
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


# ---- Canonical skill names ----

SKILL_NAMES: dict[str, str] = {
    "S1": "Problem Crystallisation",
    "S2": "Context and Constraint Mapping",
    "S3": "Option Generation",
    "S4": "Option Evaluation",
    "S5": "Solution Selection",
    "S6": "Solution Brief",
    "E1": "Problem Definition",
    "E2": "Requirements",
    "E3": "Architecture",
    "E4": "Security and Compliance",
    "E5": "Data",
    "E6": "Build",
    "E7": "Test",
    "E8": "Deployment",
    "E9": "Operations",
    "E10": "Feedback and Learning",
}


# ---- Static routes ----


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/skills")
def list_skills() -> JSONResponse:
    from harness.orchestrator.skill_sequence import (
        EXECUTION_SEQUENCE,
        SOLUTIONING_SEQUENCE,
    )
    skills: list[dict[str, str]] = []
    for seq in (SOLUTIONING_SEQUENCE, EXECUTION_SEQUENCE):
        for sid in seq.skill_ids:
            skills.append({
                "skill_id": sid,
                "sequence": seq.name,
                "name": SKILL_NAMES.get(sid, sid),
            })
    return JSONResponse({"skills": skills})


@app.get("/api/skills/names")
def skill_names() -> JSONResponse:
    return JSONResponse({"names": SKILL_NAMES})


@app.get("/api/skills/predecessor")
def skill_predecessor(skill: str) -> JSONResponse:
    from harness.skills import predecessor_of
    return JSONResponse({
        "skill_id": skill,
        "predecessor": predecessor_of(skill),
    })


@app.get("/api/gate")
def gate_status() -> JSONResponse:
    """Per-skill gate status. Gracefully returns empty on DB failure."""
    try:
        from harness.orchestrator.gate import gate_is_open
        from harness.orchestrator.skill_sequence import (
            EXECUTION_SEQUENCE,
            SOLUTIONING_SEQUENCE,
        )
    except Exception as exc:
        return JSONResponse({
            "gates": [],
            "warning": f"gate module import failed: {exc}",
        })
    rows: list[dict[str, Any]] = []
    try:
        for seq in (SOLUTIONING_SEQUENCE, EXECUTION_SEQUENCE):
            for sid in seq.skill_ids:
                try:
                    result = gate_is_open(skill_id=sid, sequence=seq)
                    rows.append({
                        "skill_id": sid, "sequence": seq.name,
                        "open": result.open, "reason": result.reason,
                        "blocking_skill_id": result.blocking_skill_id,
                    })
                except Exception as exc:
                    rows.append({
                        "skill_id": sid, "sequence": seq.name,
                        "open": False, "reason": f"error: {exc}",
                        "blocking_skill_id": None, "error": True,
                    })
    except Exception as exc:
        return JSONResponse({
            "gates": [],
            "warning": f"gate query failed (DB unavailable?): {exc}",
        })
    return JSONResponse({"gates": rows})


@app.get("/api/replay")
def replay() -> JSONResponse:
    """Session replay. Gracefully returns empty on DB failure."""
    try:
        from harness.layer2.views import session_replay_view
        view = session_replay_view()
    except Exception as exc:
        return JSONResponse({
            "generated_at": None,
            "skill_frames": [],
            "warning": f"replay query failed (DB unavailable?): {exc}",
        })
    return JSONResponse({
        "generated_at": view.generated_at.isoformat(),
        "skill_frames": [
            {
                "skill_id": f.skill_id,
                "last_cycle_id": f.last_cycle_id,
                "last_convergence_state": f.last_convergence_state,
                "last_outcome": f.last_outcome,
                "last_direction": f.last_direction,
                "last_closed_at_exact": f.last_closed_at_exact,
                "last_artefact_path": f.last_artefact_path,
                "unresolved_partial": f.unresolved_partial,
                "last_activity_at": (
                    f.last_activity_at.isoformat() if f.last_activity_at else None
                ),
            }
            for f in view.skill_frames
        ],
    })


@app.get("/api/project-name")
def project_name() -> JSONResponse:
    """Project name from the S1 exit artefact's '## Problem name' section."""
    fallback = {"project_name": "New Project"}
    try:
        from harness.layer2.views import session_replay_view
        view = session_replay_view()
    except Exception:
        return JSONResponse(fallback)
    s1 = next((f for f in view.skill_frames if f.skill_id == "S1"), None)
    if not s1 or not s1.last_artefact_path:
        return JSONResponse(fallback)
    p = Path(s1.last_artefact_path)
    if not p.is_absolute():
        p = (REPO_ROOT / p).resolve()
    else:
        p = p.resolve()
    try:
        p.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return JSONResponse(fallback)
    if not p.is_file():
        return JSONResponse(fallback)
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return JSONResponse(fallback)
    lines = text.splitlines()
    heading = re.compile(r"^##\s*Problem\s+name\s*(?::\s*(.*))?\s*$", re.IGNORECASE)
    for i, line in enumerate(lines):
        m = heading.match(line)
        if not m:
            continue
        inline = (m.group(1) or "").strip()
        if inline:
            return JSONResponse({"project_name": inline})
        for j in range(i + 1, len(lines)):
            s = lines[j].strip()
            if not s:
                continue
            if s.startswith("#"):
                break
            return JSONResponse({"project_name": s})
        break
    return JSONResponse(fallback)


@app.get("/api/artefact")
def artefact(path: str) -> JSONResponse:
    """Return exit-artefact markdown. Refuses paths outside the repo."""
    p = Path(path)
    if not p.is_absolute():
        p = (REPO_ROOT / p).resolve()
    else:
        p = p.resolve()
    try:
        p.relative_to(REPO_ROOT.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="path escapes repo root")
    if p.suffix != ".md":
        raise HTTPException(status_code=400, detail="only .md files allowed")
    if not p.is_file():
        raise HTTPException(status_code=404, detail=f"not found: {path}")
    return JSONResponse({
        "path": str(p.relative_to(REPO_ROOT.resolve())),
        "markdown": p.read_text(encoding="utf-8"),
    })


# ---- pty + parser --------------------------------------------------------


ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]")
CHALLENGE_RE = re.compile(
    r"^\s*\d+\.\s+\[(CRITICAL|MAJOR|MINOR)\]\s+\(([^)]+)\)\s+(.+)$"
)
EVIDENCE_RE = re.compile(r"^\s+evidence:\s+(.+)$")
SUMMARY_KEYS = {
    "cycle_id": "cycle_id",
    "iterations": "iterations",
    "convergence at exit": "convergence",
    "chain entries written": "chain_entries",
    "exit artefact": "artefact_path",
    "master anchor chain_id": "anchor_chain_id",
    "frame change recorded": "frame_change",
}


def _set_winsize(fd: int, rows: int, cols: int) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


def _build_run_argv(payload: dict[str, Any]) -> list[str]:
    skill = str(payload["skill"]).strip()
    convergence = str(payload["convergence"]).strip()
    direction = str(payload.get("direction") or "").strip()
    knowledge = str(payload.get("knowledge") or "").strip()
    pdis = payload.get("pdi") or []
    if isinstance(pdis, str):
        pdis = [p.strip() for p in pdis.splitlines() if p.strip()]
    argv = [
        "uv", "run", "harness", "run",
        "--skill", skill,
        "--convergence", convergence,
        "--direction", direction,
    ]
    if knowledge:
        argv += ["--knowledge", knowledge]
    for ref in pdis:
        ref = str(ref).strip()
        if ref:
            argv += ["--pdi", ref]
    return argv


class CycleParser:
    """Line-by-line state machine over the harness CLI stdout.

    Known markers drive state transitions; buffered content is emitted as
    typed events. Anything we don't recognise during an active block is
    discarded (agent token streams are noisy by design).
    """

    def __init__(self, emit: Callable[[dict], Awaitable[None]]):
        self._emit = emit
        self._state = "WAIT_M3"
        self._producing: list[str] = []
        self._reasoning: list[str] = []
        self._challenges: list[dict] = []
        self._frame_change = False
        self._summary: dict[str, Any] = {}
        self._thinking_task: asyncio.Task[None] | None = None
        self._thinking_start: float | None = None
        self._thinking_agent = "producing_agent"

    # --- lifecycle ---

    async def on_start(self) -> None:
        await self._emit({"type": "moment", "moment": 1, "label": "Direction Capture"})
        await self._emit({"type": "moment", "moment": 2, "label": "AI Produces"})
        self._start_thinking("producing_agent")

    async def on_verdict_submitted(self, outcome: str) -> None:
        """Server-side hook fired when a verdict payload is written to stdin."""
        if outcome != "CONFIRMED":
            await self._emit({"type": "moment", "moment": 2, "label": "AI Produces"})
            self._start_thinking("producing_agent")
            self._state = "WAIT_M3"

    async def stop(self) -> None:
        self._stop_thinking()
        if self._summary:
            await self._emit({"type": "cycle_complete", **self._summary})
            self._summary = {}

    # --- thinking timer ---

    def _start_thinking(self, agent: str) -> None:
        self._stop_thinking()
        self._thinking_agent = agent
        self._thinking_start = time.monotonic()
        self._thinking_task = asyncio.create_task(self._thinking_loop())

    def _stop_thinking(self) -> None:
        if self._thinking_task and not self._thinking_task.done():
            self._thinking_task.cancel()
        self._thinking_task = None
        self._thinking_start = None

    async def _thinking_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(2)
                if self._thinking_start is None:
                    return
                elapsed = int(time.monotonic() - self._thinking_start)
                await self._emit({
                    "type": "thinking",
                    "agent": self._thinking_agent,
                    "elapsed_s": elapsed,
                })
        except asyncio.CancelledError:
            return

    # --- main feed ---

    async def feed(self, raw: str) -> None:
        line = raw.rstrip("\r")

        # Universal markers — evaluate before state-specific branches.
        if "==================== Moment 3" in line:
            self._stop_thinking()
            await self._emit({"type": "moment", "moment": 3, "label": "Human Verifies"})
            self._state = "IN_M3"
            return
        if "==================== Cycle summary" in line:
            self._stop_thinking()
            await self._emit({"type": "moment", "moment": 4, "label": "Cycle Closes"})
            self._state = "SUMMARY"
            self._summary = {}
            return
        if "[sidecar] Tier 2 frame change detected" in line:
            self._frame_change = True
            await self._emit({"type": "log", "text": line.strip()})
            return
        if line.lstrip().startswith("[sidecar]"):
            await self._emit({"type": "log", "text": line.strip()})
            return
        if "Must be one of CONFIRMED" in line:
            await self._emit({"type": "log", "text": line.strip()})
            return

        if self._state == "IN_M3":
            if line.strip() == "--- Producing Agent output ---":
                self._state = "PROD_OUT"
                self._producing = []
                self._reasoning = []
                self._challenges = []
                self._frame_change = False
            return

        if self._state == "PROD_OUT":
            if line.strip() == "--- Producing Agent reasoning trace ---":
                self._state = "REASONING"
                return
            self._producing.append(line)
            return

        if self._state == "REASONING":
            if line.strip() == "--- Adversarial challenges ---":
                await self._emit({
                    "type": "producing_output",
                    "markdown": "\n".join(self._producing).rstrip(),
                    "reasoning_trace": "\n".join(self._reasoning).rstrip(),
                })
                self._state = "CHALL"
                return
            self._reasoning.append(line)
            return

        if self._state == "CHALL":
            if "Verdict options: CONFIRMED | PARTIAL | REJECTED" in line:
                await self._emit({
                    "type": "adversarial_challenges",
                    "challenges": self._challenges,
                    "frame_change": self._frame_change,
                })
                await self._emit({"type": "verification_required"})
                self._state = "AWAIT_VERDICT"
                return
            m = CHALLENGE_RE.match(line)
            if m:
                self._challenges.append({
                    "severity": m.group(1),
                    "axis": m.group(2),
                    "challenge": m.group(3),
                    "evidence": "",
                })
                return
            e = EVIDENCE_RE.match(line)
            if e and self._challenges:
                self._challenges[-1]["evidence"] = e.group(1)
                return
            if "[!] Adversarial agent raised a CRITICAL FRAME_CHANGE" in line:
                self._frame_change = True
            return

        if self._state == "SUMMARY":
            s = line.strip()
            if not s:
                if self._summary:
                    await self._emit({"type": "cycle_complete", **self._summary})
                    self._summary = {}
                    self._state = "WAIT_M3"
                return
            m = re.match(
                r"(cycle_id|iterations|convergence at exit|chain entries written"
                r"|exit artefact|master anchor chain_id|frame change recorded):"
                r"\s*(.*)$",
                s,
            )
            if m:
                out_key = SUMMARY_KEYS[m.group(1)]
                val: Any = m.group(2).strip()
                if out_key in ("iterations", "chain_entries"):
                    try:
                        val = int(val)
                    except ValueError:
                        pass
                if out_key == "artefact_path" and str(val).startswith("("):
                    val = None
                self._summary[out_key] = val
            return

        # AWAIT_VERDICT / WAIT_M3 / any unknown — swallow (agent token noise).


# ---- WebSocket ----------------------------------------------------------


@app.websocket("/ws/cycle")
async def ws_cycle(ws: WebSocket) -> None:
    """Structured cycle channel. Replaces the raw pty stream."""
    await ws.accept()

    pid: int | None = None
    fd: int | None = None
    reader_task: asyncio.Task[None] | None = None
    waiter_task: asyncio.Task[None] | None = None
    parser: CycleParser | None = None

    async def emit(event: dict) -> None:
        try:
            await ws.send_text(json.dumps(event))
        except Exception:
            pass

    def _read_some(pty_fd: int) -> bytes:
        try:
            return os.read(pty_fd, 4096)
        except OSError:
            return b""

    async def pump(pty_fd: int) -> None:
        loop = asyncio.get_running_loop()
        buffer = ""
        while True:
            data = await loop.run_in_executor(None, _read_some, pty_fd)
            if not data:
                break
            text = ANSI_RE.sub("", data.decode("utf-8", errors="replace"))
            buffer += text
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if parser:
                    try:
                        await parser.feed(line)
                    except Exception as exc:
                        await emit({"type": "error", "message": f"parser: {exc}"})

    async def wait_and_notify(child_pid: int) -> None:
        loop = asyncio.get_running_loop()
        try:
            _, status = await loop.run_in_executor(None, os.waitpid, child_pid, 0)
        except ChildProcessError:
            return
        if os.WIFEXITED(status):
            code = os.WEXITSTATUS(status)
        elif os.WIFSIGNALED(status):
            code = -os.WTERMSIG(status)
        else:
            code = -1
        if parser:
            await parser.stop()
        await emit({"type": "exit", "code": code})

    async def cleanup() -> None:
        nonlocal pid, fd, reader_task, waiter_task, parser
        if parser:
            try:
                await parser.stop()
            except Exception:
                pass
            parser = None
        for t in (reader_task, waiter_task):
            if t and not t.done():
                t.cancel()
                try:
                    await t
                except Exception:
                    pass
        reader_task = None
        waiter_task = None
        if pid is not None:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        pid = None
        fd = None

    try:
        while True:
            msg = await ws.receive()
            if msg.get("type") == "websocket.disconnect":
                break
            if "text" not in msg or msg["text"] is None:
                continue
            try:
                data = json.loads(msg["text"])
            except json.JSONDecodeError:
                continue
            kind = data.get("type")

            if kind == "start":
                if pid is not None:
                    await emit({"type": "error", "message": "already running"})
                    continue
                try:
                    argv = _build_run_argv(data)
                except KeyError as exc:
                    await emit({"type": "error", "message": f"missing field: {exc}"})
                    continue
                pid, fd = pty.fork()
                if pid == 0:
                    try:
                        os.chdir(REPO_ROOT)
                        os.execvp(argv[0], argv)
                    except Exception as exc:
                        os.write(2, f"exec failed: {exc}\n".encode())
                        os._exit(127)
                _set_winsize(fd, 40, 120)
                parser = CycleParser(emit)
                await parser.on_start()
                await emit({"type": "started", "pid": pid, "argv": argv})
                reader_task = asyncio.create_task(pump(fd))
                waiter_task = asyncio.create_task(wait_and_notify(pid))

            elif kind == "verdict" and fd is not None:
                outcome = str(data.get("outcome", "")).strip().upper()
                if outcome not in ("CONFIRMED", "PARTIAL", "REJECTED"):
                    await emit({"type": "error", "message": "invalid outcome"})
                    continue
                notes = re.sub(r"[\r\n]+", " ", str(data.get("notes") or "")).strip()
                refined = re.sub(r"[\r\n]+", " ", str(data.get("refined") or "")).strip()
                if outcome != "CONFIRMED" and not refined:
                    await emit({
                        "type": "error",
                        "message": "Refined direction required for PARTIAL / REJECTED.",
                    })
                    continue
                payload = f"{outcome}\n{notes}\n"
                if outcome != "CONFIRMED":
                    payload += f"{refined}\n"
                try:
                    os.write(fd, payload.encode("utf-8"))
                except OSError as exc:
                    await emit({"type": "error", "message": f"write failed: {exc}"})
                    continue
                if parser:
                    await parser.on_verdict_submitted(outcome)

            elif kind == "kill":
                await cleanup()
                await emit({"type": "exit", "code": -1, "killed": True})

    except WebSocketDisconnect:
        pass
    finally:
        await cleanup()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
