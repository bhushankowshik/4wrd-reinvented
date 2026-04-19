/* 4WRD Harness UI — terminal + sidebar wiring. */
(function () {
  "use strict";

  const VERDICT_MARKER = 'Verdict options: CONFIRMED | PARTIAL | REJECTED';
  const ANSI_RE = /\x1b\[[0-9;?]*[a-zA-Z]/g;

  const term = new window.Terminal({
    cursorBlink: true,
    fontFamily: 'JetBrains Mono, Menlo, monospace',
    fontSize: 13,
    theme: {
      background: '#000000',
      foreground: '#ffffff',
      cursor: '#4fc3f7',
    },
    convertEol: true,
    scrollback: 5000,
  });
  const fitAddon = new window.FitAddon.FitAddon();
  term.loadAddon(fitAddon);
  term.open(document.getElementById('terminal'));
  fitAddon.fit();

  // ---- WebSocket setup ----
  const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${wsProto}//${location.host}/ws/terminal`);
  let running = false;

  const statusPill = document.getElementById('status-pill');
  const runBtn = document.getElementById('run-btn');
  const killBtn = document.getElementById('kill-btn');

  function setStatus(label, klass) {
    statusPill.textContent = label;
    statusPill.className = 'status ' + klass;
  }

  function setRunning(isRunning) {
    running = isRunning;
    runBtn.disabled = isRunning;
    killBtn.disabled = !isRunning;
  }

  ws.addEventListener('open', () => {
    setStatus('idle', 'idle');
    term.writeln('\x1b[1;36m4WRD Harness UI ready.\x1b[0m');
    term.writeln('Pick a skill + convergence above, fill direction, then Run Cycle.');
    term.writeln('');
  });
  ws.addEventListener('close', () => {
    setStatus('disconnected', 'error');
    setRunning(false);
    term.writeln('\r\n\x1b[1;31m[ws closed]\x1b[0m');
  });
  ws.addEventListener('error', () => setStatus('ws error', 'error'));

  // Rolling buffer of recent plaintext pty output used to detect prompts.
  let outputBuffer = '';
  function appendToBuffer(data) {
    outputBuffer += data.replace(ANSI_RE, '');
    if (outputBuffer.length > 8192) {
      outputBuffer = outputBuffer.slice(-8192);
    }
  }

  ws.addEventListener('message', (ev) => {
    let msg;
    try { msg = JSON.parse(ev.data); } catch { return; }
    switch (msg.type) {
      case 'output':
        term.write(msg.data);
        appendToBuffer(msg.data);
        maybeShowVerifyPanel();
        break;
      case 'started':
        setRunning(true);
        setStatus('running', 'running');
        hideVerifyPanel();
        outputBuffer = '';
        term.writeln(`\x1b[2;37m[pid ${msg.pid}] ${msg.argv.join(' ')}\x1b[0m`);
        break;
      case 'exit':
        setRunning(false);
        setStatus(msg.killed ? 'killed' : `exit ${msg.code}`, 'exited');
        hideVerifyPanel();
        term.writeln(`\r\n\x1b[2;37m[process exited code=${msg.code}]\x1b[0m`);
        refreshSidebar();
        break;
      case 'error':
        term.writeln(`\r\n\x1b[1;31m[error] ${msg.message}\x1b[0m`);
        // If server says a process is already running, sync our state so the
        // Kill button becomes clickable without forcing the operator to the
        // macOS terminal.
        if (msg.message && /already running/i.test(msg.message)) {
          setRunning(true);
          setStatus('running', 'running');
        } else {
          setStatus('error', 'error');
        }
        break;
    }
  });

  // ---- Send keystrokes ----
  term.onData((data) => {
    if (ws.readyState !== WebSocket.OPEN) return;
    if (!running) return;  // ignore typing before a process is up
    ws.send(JSON.stringify({ type: 'input', data }));
  });

  // ---- Resize handling ----
  function syncSize() {
    fitAddon.fit();
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'resize',
        rows: term.rows,
        cols: term.cols,
      }));
    }
  }
  window.addEventListener('resize', syncSize);

  // ---- Run / Kill buttons ----
  runBtn.addEventListener('click', () => {
    if (running) return;
    const skill = document.getElementById('skill-select').value;
    const convergence = document.getElementById('convergence-select').value;
    const direction = document.getElementById('direction').value.trim();
    const knowledge = document.getElementById('knowledge').value.trim();
    const pdiRaw = document.getElementById('pdi').value.trim();
    if (!direction) {
      term.writeln('\r\n\x1b[1;33m[need a direction before Run Cycle]\x1b[0m');
      return;
    }
    if (convergence === 'Explorative' && !knowledge) {
      term.writeln('\r\n\x1b[1;33m[Explorative cycles require knowledge contribution]\x1b[0m');
      return;
    }
    fitAddon.fit();
    ws.send(JSON.stringify({
      type: 'start',
      skill,
      convergence,
      direction,
      knowledge,
      pdi: pdiRaw,
      rows: term.rows,
      cols: term.cols,
    }));
  });
  killBtn.addEventListener('click', () => {
    ws.send(JSON.stringify({ type: 'kill' }));
  });

  // ---- Verification panel ----
  const verifyPanel = document.getElementById('verify-panel');
  const verifyNotes = document.getElementById('verify-notes');
  const verifyRefined = document.getElementById('verify-refined');
  const verifyRefinedWrap = document.getElementById('verify-refined-wrap');
  const verifySubmit = document.getElementById('verify-submit');
  const verifyError = document.getElementById('verify-error');
  const verdictButtons = Array.from(
    verifyPanel.querySelectorAll('.verify-verdicts .verdict'),
  );

  let awaitingVerdict = false;
  let selectedVerdict = null;

  function maybeShowVerifyPanel() {
    if (awaitingVerdict) return;
    if (!outputBuffer.includes(VERDICT_MARKER)) return;
    awaitingVerdict = true;
    outputBuffer = '';  // consume the trigger so we don't re-fire
    showVerifyPanel();
  }

  function showVerifyPanel() {
    verifyPanel.hidden = false;
    verifyNotes.value = '';
    verifyRefined.value = '';
    verifyRefinedWrap.hidden = true;
    verifySubmit.hidden = true;
    verifyError.hidden = true;
    selectedVerdict = null;
    verdictButtons.forEach((b) => b.classList.remove('selected'));
    setTimeout(() => verifyNotes.focus(), 0);
  }

  function hideVerifyPanel() {
    verifyPanel.hidden = true;
    awaitingVerdict = false;
    selectedVerdict = null;
  }

  function oneLine(s) {
    return (s || '').replace(/[\r\n]+/g, ' ').trim();
  }

  function sendVerdict(verdict) {
    const notes = oneLine(verifyNotes.value);
    const refined = oneLine(verifyRefined.value);
    if (verdict !== 'CONFIRMED' && !refined) {
      verifyError.textContent =
        'Refined direction is required for PARTIAL / REJECTED.';
      verifyError.hidden = false;
      verifyRefined.focus();
      return;
    }
    // Build a single stdin payload answering all three sequential prompts:
    //   Outcome → verification notes → (if not CONFIRMED) refined direction
    let payload = verdict + '\n' + notes + '\n';
    if (verdict !== 'CONFIRMED') {
      payload += refined + '\n';
    }
    ws.send(JSON.stringify({ type: 'input', data: payload }));
    hideVerifyPanel();
  }

  verdictButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const v = btn.dataset.verdict;
      verifyError.hidden = true;
      if (v === 'CONFIRMED') {
        sendVerdict('CONFIRMED');
        return;
      }
      // PARTIAL / REJECTED — stage the verdict, reveal refined field.
      selectedVerdict = v;
      verdictButtons.forEach((b) => b.classList.toggle('selected', b === btn));
      verifyRefinedWrap.hidden = false;
      verifySubmit.hidden = false;
      verifySubmit.textContent = `Submit ${v}`;
      setTimeout(() => verifyRefined.focus(), 0);
    });
  });

  verifySubmit.addEventListener('click', () => {
    if (!selectedVerdict) return;
    sendVerdict(selectedVerdict);
  });

  // ---- Sidebar (gate + replay + skills) ----
  const skillSelect = document.getElementById('skill-select');
  const gateList = document.getElementById('gate-list');
  const replayList = document.getElementById('replay-list');
  const pdiField = document.getElementById('pdi');

  let replayCache = null;
  let initialPdiPopulated = false;

  async function loadSkills() {
    const r = await fetch('/api/skills');
    const j = await r.json();
    skillSelect.innerHTML = '';
    let lastSeq = null;
    for (const s of j.skills) {
      if (s.sequence !== lastSeq) {
        const og = document.createElement('optgroup');
        og.label = s.sequence;
        skillSelect.appendChild(og);
        lastSeq = s.sequence;
      }
      const opt = document.createElement('option');
      opt.value = s.skill_id;
      opt.textContent = s.skill_id;
      skillSelect.lastElementChild.appendChild(opt);
    }
  }

  async function loadGate() {
    try {
      const r = await fetch('/api/gate');
      const j = await r.json();
      gateList.innerHTML = '';
      if (!j.gates || !j.gates.length) {
        gateList.innerHTML = '<li class="empty">no skills</li>';
        return;
      }
      for (const g of j.gates) {
        const li = document.createElement('li');
        const stateClass = g.error ? 'error' : (g.open ? 'open' : 'blocked');
        const stateLabel = g.error ? 'ERR' : (g.open ? 'OPEN' : 'BLOCKED');
        const blocker = g.blocking_skill_id
          ? `← blocked by ${g.blocking_skill_id}`
          : '';
        li.innerHTML = `
          <div class="gate-row">
            <span class="gate-skill">${g.skill_id}</span>
            <span class="gate-state ${stateClass}">${stateLabel}</span>
          </div>
          ${blocker ? `<span class="gate-blocker">${blocker}</span>` : ''}
        `;
        li.title = g.reason || '';
        gateList.appendChild(li);
      }
    } catch (e) {
      gateList.innerHTML = `<li class="empty">gate fetch failed: ${e}</li>`;
    }
  }

  async function loadReplay() {
    try {
      const r = await fetch('/api/replay');
      const j = await r.json();
      replayCache = j.skill_frames || [];
      replayList.innerHTML = '';
      if (!replayCache.length) {
        replayList.innerHTML = '<li class="empty">no cycles yet</li>';
      } else {
        for (const f of replayCache) {
          const li = document.createElement('li');
          const ts = f.last_activity_at
            ? new Date(f.last_activity_at).toLocaleString()
            : '—';
          li.innerHTML = `
            <div class="row1">
              <strong>${f.skill_id}</strong>
              <span>${f.last_convergence_state || '—'}</span>
            </div>
            <span class="ts">${f.last_outcome || '—'} · ${ts}</span>
          `;
          li.title = f.last_direction || '';
          replayList.appendChild(li);
        }
      }
      // One-shot: after the first replay fetch, populate PDI for the default
      // skill. Subsequent replay refreshes never clobber operator edits — they
      // only happen on explicit skill change.
      if (!initialPdiPopulated && skillSelect.value) {
        autoPopulatePdi();
        initialPdiPopulated = true;
      }
    } catch (e) {
      replayList.innerHTML = `<li class="empty">replay fetch failed: ${e}</li>`;
    }
  }

  function autoPopulatePdi() {
    if (!replayCache) return;
    const skill = skillSelect.value;
    if (!skill) return;
    const frame = replayCache.find((f) => f.skill_id === skill);
    pdiField.value = (frame && frame.last_artefact_path)
      ? frame.last_artefact_path
      : '';
  }

  skillSelect.addEventListener('change', autoPopulatePdi);

  function refreshSidebar() {
    loadGate();
    loadReplay();
  }

  document.getElementById('refresh-btn').addEventListener('click', refreshSidebar);

  loadSkills().then(refreshSidebar);
  setInterval(refreshSidebar, 30000);

  // settle xterm to its container after all assets settle
  setTimeout(syncSize, 100);
})();
