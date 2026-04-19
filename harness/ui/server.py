"""FastAPI server — local web UI wrapper around the harness CLI.

Spawns the existing `uv run harness ...` CLI inside a pty and streams
it bidirectionally to an xterm.js terminal in the browser. Read-only
JSON endpoints expose gate status (per skill in both sequences) and
the cold-start session replay.

Run with: ./run.sh    (or: uvicorn server:app --port 8080)
"""
from __future__ import annotations

import asyncio
import fcntl
import json
import os
import pty
import signal
import struct
import termios
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from harness.layer2.views import session_replay_view
from harness.orchestrator.gate import gate_is_open
from harness.orchestrator.skill_sequence import (
    EXECUTION_SEQUENCE,
    SOLUTIONING_SEQUENCE,
)


HERE = Path(__file__).parent
STATIC = HERE / "static"
REPO_ROOT = HERE.parent  # the harness/ directory — where `uv run` resolves

ALL_SEQUENCES = (SOLUTIONING_SEQUENCE, EXECUTION_SEQUENCE)


app = FastAPI(title="4WRD Harness UI")
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/skills")
def list_skills() -> JSONResponse:
    skills: list[dict[str, str]] = []
    for seq in ALL_SEQUENCES:
        for sid in seq.skill_ids:
            skills.append({"skill_id": sid, "sequence": seq.name})
    return JSONResponse({"skills": skills})


@app.get("/api/gate")
def gate_status() -> JSONResponse:
    rows: list[dict[str, Any]] = []
    for seq in ALL_SEQUENCES:
        for sid in seq.skill_ids:
            try:
                result = gate_is_open(skill_id=sid, sequence=seq)
                rows.append({
                    "skill_id": sid,
                    "sequence": seq.name,
                    "open": result.open,
                    "reason": result.reason,
                    "blocking_skill_id": result.blocking_skill_id,
                })
            except Exception as exc:  # surface DB / config issues to UI
                rows.append({
                    "skill_id": sid,
                    "sequence": seq.name,
                    "open": False,
                    "reason": f"error: {exc}",
                    "blocking_skill_id": None,
                    "error": True,
                })
    return JSONResponse({"gates": rows})


@app.get("/api/replay")
def replay() -> JSONResponse:
    view = session_replay_view()
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


# ---- pty bridge --------------------------------------------------------


def _set_winsize(fd: int, rows: int, cols: int) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


def _build_run_argv(payload: dict[str, Any]) -> list[str]:
    """Build a `uv run harness run ...` argv from a start payload."""
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


@app.websocket("/ws/terminal")
async def ws_terminal(ws: WebSocket) -> None:
    """Bidirectional bridge between an xterm.js client and a pty subprocess.

    Protocol (text frames are JSON, binary frames are raw stdin bytes):

      → client sends JSON {"type": "start", "skill": ..., "convergence": ...,
                            "direction": ..., "knowledge": ..., "pdi": [...],
                            "rows": 40, "cols": 120}
      → client sends JSON {"type": "resize", "rows": R, "cols": C}
      → client sends JSON {"type": "input", "data": "..."}  (utf-8 keystrokes)
      → client sends JSON {"type": "kill"}
      ← server sends JSON {"type": "output", "data": "..."}  (utf-8 pty output)
      ← server sends JSON {"type": "exit", "code": N}
      ← server sends JSON {"type": "error", "message": "..."}
    """
    await ws.accept()

    pid: int | None = None
    fd: int | None = None
    reader_task: asyncio.Task[None] | None = None

    async def pump_pty_to_ws(pty_fd: int) -> None:
        loop = asyncio.get_running_loop()
        try:
            while True:
                data = await loop.run_in_executor(None, _read_some, pty_fd)
                if not data:
                    break
                try:
                    text = data.decode("utf-8", errors="replace")
                except Exception:
                    text = ""
                await ws.send_text(json.dumps({"type": "output", "data": text}))
        except Exception:
            pass

    def _read_some(pty_fd: int) -> bytes:
        try:
            return os.read(pty_fd, 4096)
        except OSError:
            return b""

    async def cleanup() -> None:
        nonlocal pid, fd, reader_task
        if reader_task and not reader_task.done():
            reader_task.cancel()
            try:
                await reader_task
            except Exception:
                pass
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
        reader_task = None

    try:
        while True:
            msg = await ws.receive()
            if msg.get("type") == "websocket.disconnect":
                break

            if "text" in msg and msg["text"] is not None:
                try:
                    data = json.loads(msg["text"])
                except json.JSONDecodeError:
                    continue
                kind = data.get("type")

                if kind == "start":
                    if pid is not None:
                        await ws.send_text(json.dumps({
                            "type": "error",
                            "message": "process already running — kill it first.",
                        }))
                        continue
                    try:
                        argv = _build_run_argv(data)
                    except KeyError as exc:
                        await ws.send_text(json.dumps({
                            "type": "error",
                            "message": f"missing field: {exc}",
                        }))
                        continue

                    rows = int(data.get("rows", 40))
                    cols = int(data.get("cols", 120))
                    pid, fd = pty.fork()
                    if pid == 0:  # child
                        try:
                            os.chdir(REPO_ROOT)
                            os.execvp(argv[0], argv)
                        except Exception as exc:
                            os.write(2, f"exec failed: {exc}\n".encode())
                            os._exit(127)

                    _set_winsize(fd, rows, cols)
                    await ws.send_text(json.dumps({
                        "type": "started",
                        "argv": argv,
                        "pid": pid,
                    }))
                    reader_task = asyncio.create_task(pump_pty_to_ws(fd))
                    asyncio.create_task(_wait_and_notify(ws, pid, lambda: cleanup_marker()))

                elif kind == "input" and fd is not None:
                    payload = data.get("data", "")
                    if isinstance(payload, str):
                        try:
                            os.write(fd, payload.encode("utf-8"))
                        except OSError:
                            pass

                elif kind == "resize" and fd is not None:
                    try:
                        _set_winsize(
                            fd,
                            int(data.get("rows", 40)),
                            int(data.get("cols", 120)),
                        )
                    except Exception:
                        pass

                elif kind == "kill":
                    await cleanup()
                    await ws.send_text(json.dumps({
                        "type": "exit", "code": -1, "killed": True,
                    }))

            elif msg.get("bytes") is not None and fd is not None:
                try:
                    os.write(fd, msg["bytes"])
                except OSError:
                    pass

    except WebSocketDisconnect:
        pass
    finally:
        await cleanup()


def cleanup_marker() -> None:
    """No-op — placeholder so _wait_and_notify can take a callback."""


async def _wait_and_notify(ws: WebSocket, pid: int, _cb) -> None:
    """Reap the child and tell the client when it exits."""
    loop = asyncio.get_running_loop()
    try:
        _, status = await loop.run_in_executor(None, os.waitpid, pid, 0)
    except ChildProcessError:
        return
    if os.WIFEXITED(status):
        code = os.WEXITSTATUS(status)
    elif os.WIFSIGNALED(status):
        code = -os.WTERMSIG(status)
    else:
        code = -1
    try:
        await ws.send_text(json.dumps({"type": "exit", "code": code}))
    except Exception:
        pass


if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
