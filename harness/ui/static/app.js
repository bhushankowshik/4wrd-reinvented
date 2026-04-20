/* 4WRD Harness — structured web app.
 *
 * WebSocket contract with /ws/cycle:
 *   → client: {type:"start", skill, convergence, direction, knowledge, pdi}
 *   → client: {type:"verdict", outcome, notes, refined}
 *   → client: {type:"kill"}
 *   ← server: {type:"moment", moment, label}
 *   ← server: {type:"producing_output", markdown, reasoning_trace}
 *   ← server: {type:"adversarial_challenges", challenges:[…], frame_change}
 *   ← server: {type:"verification_required"}
 *   ← server: {type:"cycle_complete", cycle_id, convergence, iterations,
 *              chain_entries, artefact_path, …}
 *   ← server: {type:"thinking", agent, elapsed_s}
 *   ← server: {type:"started"|"exit"|"error"|"log"}
 */
(function () {
  "use strict";

  const SEQUENCES = {
    solutioning: ["S1", "S2", "S3", "S4", "S5", "S6"],
    execution: ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10"],
  };
  const ALL_SKILLS = [...SEQUENCES.solutioning, ...SEQUENCES.execution];

  const SHORT_NAMES = {
    S1: "Problem Cryst.",
    S2: "Context & Constraints",
    S3: "Option Generation",
    S4: "Option Evaluation",
    S5: "Solution Selection",
    S6: "Solution Brief",
    E1: "Problem Definition",
    E2: "Requirements",
    E3: "Architecture",
    E4: "Security & Compliance",
    E5: "Data",
    E6: "Build",
    E7: "Test",
    E8: "Deployment",
    E9: "Operations",
    E10: "Feedback & Learning",
  };

  const $ = (id) => document.getElementById(id);

  // ---- State ----
  const state = {
    skills: [],                 // [{skill_id, sequence, name}]
    names: {},                  // {S1: "Problem Crystallisation", …}
    gates: [],                  // /api/gate rows
    frames: [],                 // /api/replay skill_frames
    history: [],                // cycle history for the currently-viewed skill (stub)
    projectName: "New Project",
    running: false,
    selectedSkill: null,        // which skill the left-pane is viewing
    currentMoment: 0,
    thinkingStart: null,
  };

  const ws = (() => {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    return new WebSocket(`${proto}//${location.host}/ws/cycle`);
  })();

  // ---- WebSocket handlers ----
  ws.addEventListener("open", () => setStatus("idle", "idle"));
  ws.addEventListener("close", () => { setStatus("disconnected", "error"); setRunning(false); });
  ws.addEventListener("error", () => setStatus("ws error", "error"));
  ws.addEventListener("message", (ev) => {
    let m; try { m = JSON.parse(ev.data); } catch { return; }
    handleEvent(m);
  });

  function sendWs(obj) {
    if (ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify(obj));
  }

  function handleEvent(m) {
    switch (m.type) {
      case "started":
        setRunning(true);
        setStatus("running", "running");
        resetOutputs();
        break;
      case "moment":
        if (verifyState === "submitted" || verifyState === "active") {
          hideVerifyPanel();
        }
        setMoment(m.moment, m.label);
        break;
      case "producing_output":
        renderProducingOutput(m.markdown, m.reasoning_trace);
        break;
      case "adversarial_challenges":
        renderChallenges(m.challenges, m.frame_change);
        break;
      case "verification_required":
        showVerifyPanel();
        break;
      case "thinking":
        renderThinking(m.agent, m.elapsed_s);
        break;
      case "cycle_complete":
        if (verifyState === "submitted" || verifyState === "active") {
          hideVerifyPanel();
        }
        renderCycleComplete(m);
        break;
      case "exit":
        setRunning(false);
        setStatus(m.killed ? "killed" : `exit ${m.code}`, "exited");
        hideThinking();
        hideVerifyPanel();
        refreshSidebar();
        break;
      case "error":
        setStatus("error", "error");
        flashError(m.message || "error");
        if (m.message && /already running/i.test(m.message)) {
          setRunning(true);
          setStatus("running", "running");
        }
        break;
      case "log":
        // Currently swallowed. Surfaced via small footer if debugging needed.
        break;
    }
  }

  // ---- Status / running ----
  function setStatus(label, klass) {
    const pill = $("status-pill");
    pill.textContent = label;
    pill.className = "status " + klass;
  }
  function setRunning(isRunning) {
    state.running = isRunning;
    $("run-btn").disabled = isRunning;
    $("kill-btn").disabled = !isRunning;
    if (!isRunning) setMoment(0);
  }
  function flashError(msg) {
    const pill = $("status-pill");
    pill.title = msg;
  }

  // ---- Moment indicator ----
  function setMoment(n, label) {
    state.currentMoment = n;
    document.querySelectorAll(".moment-steps li").forEach((li) => {
      const mn = parseInt(li.dataset.moment, 10);
      li.classList.toggle("active", mn === n);
      li.classList.toggle("done", n > mn && n !== 0);
      if (label && mn === n) {
        li.querySelector(".step-lbl").textContent = label;
      }
    });
  }

  function renderThinking(agent, elapsed) {
    const ind = $("thinking-indicator");
    ind.hidden = false;
    $("thinking-label").textContent =
      `${agent.replace(/_/g, " ")} thinking · ${elapsed}s`;
  }
  function hideThinking() {
    $("thinking-indicator").hidden = true;
  }

  // ---- Output rendering ----
  function mdToHtml(md) {
    if (!md) return "";
    try {
      return window.marked.parse(md);
    } catch {
      const esc = document.createElement("div");
      esc.textContent = md;
      return `<pre>${esc.innerHTML}</pre>`;
    }
  }

  function resetOutputs() {
    $("output-body").innerHTML = "<p class='placeholder'>AI producing — output will render here.</p>";
    $("reasoning-body").innerHTML = "<p class='placeholder'>Reasoning trace renders after production.</p>";
    $("challenges-body").innerHTML = "<p class='placeholder'>Adversarial challenges render after production.</p>";
    $("frame-change-banner").hidden = true;
    const badge = $("challenges-count");
    badge.hidden = true; badge.textContent = "0";
    activateTab("output");
  }

  function renderProducingOutput(markdown, reasoning) {
    $("output-body").innerHTML = mdToHtml(markdown);
    $("reasoning-body").innerHTML = mdToHtml(reasoning);
    hideThinking();
  }

  function renderChallenges(challenges, frameChange) {
    const body = $("challenges-body");
    const banner = $("frame-change-banner");
    const badge = $("challenges-count");
    banner.hidden = !frameChange;
    if (!challenges || !challenges.length) {
      body.innerHTML = "<p class='placeholder'>No challenges raised.</p>";
      badge.hidden = true;
      return;
    }
    badge.hidden = false;
    badge.textContent = String(challenges.length);
    body.innerHTML = challenges.map((c) => `
      <article class="challenge-card sev-${c.severity.toLowerCase()}">
        <header>
          <span class="badge sev-${c.severity.toLowerCase()}">${c.severity}</span>
          <span class="axis">${escapeHtml(c.axis || "")}</span>
        </header>
        <p class="challenge-text">${escapeHtml(c.challenge || "")}</p>
        ${c.evidence ? `<p class="evidence"><strong>evidence:</strong> ${escapeHtml(c.evidence)}</p>` : ""}
      </article>
    `).join("");
  }

  function renderCycleComplete(m) {
    const meta = [
      `<dt>cycle_id</dt><dd>${escapeHtml(m.cycle_id || "—")}</dd>`,
      `<dt>iterations</dt><dd>${escapeHtml(String(m.iterations ?? "—"))}</dd>`,
      `<dt>convergence</dt><dd>${escapeHtml(m.convergence || "—")}</dd>`,
      `<dt>chain entries</dt><dd>${escapeHtml(String(m.chain_entries ?? "—"))}</dd>`,
      m.artefact_path ? `<dt>artefact</dt><dd class="path">${escapeHtml(m.artefact_path)}</dd>` : "",
    ].filter(Boolean).join("");
    const metaEl = $("artefact-meta");
    metaEl.innerHTML = `<dl class="kv">${meta}</dl>`;
    metaEl.hidden = false;
    if (m.artefact_path) {
      loadArtefact(m.artefact_path);
    }
    activateTab("artefact");
    setMoment(4, "Cycle Closes");
  }

  async function loadArtefact(path) {
    const body = $("artefact-body");
    body.innerHTML = "<p class='placeholder'>loading artefact…</p>";
    try {
      const r = await fetch(`/api/artefact?path=${encodeURIComponent(path)}`);
      if (!r.ok) {
        body.innerHTML = `<p class='placeholder'>failed to load: ${r.status}</p>`;
        return;
      }
      const j = await r.json();
      body.innerHTML = mdToHtml(j.markdown);
    } catch (e) {
      body.innerHTML = `<p class='placeholder'>artefact fetch failed: ${escapeHtml(String(e))}</p>`;
    }
  }

  // ---- Tabs ----
  document.querySelectorAll(".tab-bar .tab").forEach((tab) => {
    tab.addEventListener("click", () => activateTab(tab.dataset.tab));
  });
  function activateTab(name) {
    document.querySelectorAll(".tab-bar .tab").forEach((t) => {
      t.classList.toggle("active", t.dataset.tab === name);
    });
    document.querySelectorAll(".tab-body").forEach((b) => {
      b.classList.toggle("active", b.id === `tab-${name}`);
    });
  }

  // ---- Verification panel (strict state machine) ----
  //   hidden    — panel not visible
  //   active    — panel visible, buttons enabled, accepts clicks
  //   submitted — panel visible, all buttons disabled, awaiting server
  let verifyState = "hidden";
  let stagedVerdict = null;
  function resetVerifyPanelState() {
    const panel = $("verify-panel");
    panel.classList.remove("verify-submitted");
    const submit = $("verify-submit");
    submit.disabled = false;
    submit.classList.remove("btn-submitting");
    submit.textContent = "Submit verdict";
    submit.hidden = true;
    document.querySelectorAll(".verdict-btn").forEach((b) => {
      b.disabled = false;
      b.classList.remove("selected");
    });
    const msg = $("verify-error");
    msg.hidden = true;
    msg.textContent = "";
    msg.classList.remove("info-text");
    msg.classList.add("error-text");
  }
  function showVerifyPanel() {
    resetVerifyPanelState();
    stagedVerdict = null;
    $("verify-notes").value = "";
    $("verify-refined").value = "";
    $("verify-refined-wrap").hidden = true;
    $("verify-panel").hidden = false;
    $("verify-panel").scrollIntoView({ behavior: "smooth", block: "center" });
    verifyState = "active";
  }
  function hideVerifyPanel() {
    resetVerifyPanelState();
    stagedVerdict = null;
    $("verify-panel").hidden = true;
    verifyState = "hidden";
  }
  document.querySelectorAll(".verdict-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (verifyState !== "active") return;
      const v = btn.dataset.verdict;
      $("verify-error").hidden = true;
      if (v === "CONFIRMED") {
        submitVerdict("CONFIRMED");
        return;
      }
      stagedVerdict = v;
      document.querySelectorAll(".verdict-btn").forEach((b) =>
        b.classList.toggle("selected", b === btn));
      $("verify-refined-wrap").hidden = false;
      const sub = $("verify-submit");
      sub.hidden = false;
      sub.textContent = `Submit ${v}`;
      setTimeout(() => $("verify-refined").focus(), 0);
    });
  });
  $("verify-submit").addEventListener("click", () => {
    if (verifyState !== "active") return;
    if (stagedVerdict) submitVerdict(stagedVerdict);
  });
  function submitVerdict(outcome) {
    if (verifyState !== "active") return;
    const notes = $("verify-notes").value;
    const refined = $("verify-refined").value;
    const msg = $("verify-error");
    if (outcome !== "CONFIRMED" && !refined.trim()) {
      msg.textContent = "Refined direction required for PARTIAL / REJECTED.";
      msg.classList.add("error-text");
      msg.classList.remove("info-text");
      msg.hidden = false;
      return;
    }
    verifyState = "submitted";
    const submit = $("verify-submit");
    submit.disabled = true;
    submit.classList.add("btn-submitting");
    submit.innerHTML = '<span class="spinner"></span> Submitting…';
    document.querySelectorAll(".verdict-btn").forEach((b) => { b.disabled = true; });
    $("verify-panel").classList.add("verify-submitted");
    sendWs({ type: "verdict", outcome, notes, refined });
    msg.textContent = "Verdict submitted — agents processing…";
    msg.classList.remove("error-text");
    msg.classList.add("info-text");
    msg.hidden = false;
  }

  // ---- Run / Kill ----
  $("run-btn").addEventListener("click", () => {
    if (state.running) return;
    const skill = $("skill-select").value;
    const convergence = $("convergence-select").value;
    const direction = $("direction").value.trim();
    const knowledge = $("knowledge").value.trim();
    const pdi = $("pdi").value.trim();
    if (!direction) { flashError("direction required"); return; }
    if (convergence === "Explorative" && !knowledge) {
      flashError("Explorative cycles require knowledge contribution");
      return;
    }
    sendWs({ type: "start", skill, convergence, direction, knowledge, pdi });
  });
  $("kill-btn").addEventListener("click", () => sendWs({ type: "kill" }));

  // ---- Skill / convergence selection ----
  $("skill-select").addEventListener("change", () => {
    onSkillSelected($("skill-select").value);
  });
  $("convergence-select").addEventListener("change", () => {
    applyTemplateIfEmpty();
  });
  $("apply-template-btn").addEventListener("click", (ev) => {
    ev.preventDefault();
    applyTemplate(true);
  });

  let lastAppliedTemplate = "";
  function applyTemplateIfEmpty() {
    const t = currentTemplate();
    if (!t) return;
    const cur = $("direction").value;
    if (!cur.trim() || cur === lastAppliedTemplate) {
      $("direction").value = t;
      lastAppliedTemplate = t;
    }
  }
  function applyTemplate(force) {
    const t = currentTemplate();
    if (!t) return;
    const cur = $("direction").value;
    if (force || !cur.trim() || cur === lastAppliedTemplate) {
      $("direction").value = t;
      lastAppliedTemplate = t;
    }
  }
  function currentTemplate() {
    const skill = $("skill-select").value;
    const conv = $("convergence-select").value;
    const tpl = (window.DIRECTION_TEMPLATES || {})[skill];
    return tpl ? tpl[conv] : null;
  }

  function onSkillSelected(skill) {
    state.selectedSkill = skill;
    $("run-skill-name").textContent = state.names[skill]
      ? `${skill} — ${state.names[skill]}`
      : skill;
    $("current-skill").textContent = state.names[skill]
      ? `${skill} — ${state.names[skill]}`
      : skill;
    $("history-heading").textContent = `${skill} Cycle History`;
    updateCycleHistory(skill);
    autoPopulatePdi();
    applyTemplateIfEmpty();
    highlightPipelineRow(skill);
  }

  // ---- PDI auto-populate (with predecessor fallback) ----
  async function autoPopulatePdi() {
    const skill = $("skill-select").value;
    const pdiField = $("pdi");
    const src = $("pdi-source");
    if (!skill) return;
    const frame = state.frames.find((f) => f.skill_id === skill);
    if (frame && frame.last_artefact_path) {
      pdiField.value = frame.last_artefact_path;
      src.textContent = `Auto-populated from last ${skill} exit artefact`;
      return;
    }
    let predecessor = null;
    try {
      const r = await fetch(`/api/skills/predecessor?skill=${encodeURIComponent(skill)}`);
      predecessor = (await r.json()).predecessor;
    } catch { /* ignore */ }
    if (predecessor) {
      const pf = state.frames.find((f) => f.skill_id === predecessor);
      if (pf && pf.last_artefact_path) {
        pdiField.value = pf.last_artefact_path;
        src.textContent = `Auto-populated from last ${predecessor} exit artefact (predecessor)`;
        return;
      }
    }
    pdiField.value = "";
    src.textContent = "";
  }

  // ---- Sidebar rendering ----
  async function loadSkills() {
    try {
      const r = await fetch("/api/skills");
      const j = await r.json();
      state.skills = j.skills || [];
    } catch { state.skills = []; }
    try {
      const r2 = await fetch("/api/skills/names");
      const j2 = await r2.json();
      state.names = j2.names || {};
    } catch { state.names = {}; }

    const sel = $("skill-select");
    sel.innerHTML = "";
    const sols = state.skills.filter((s) => s.sequence === "solutioning");
    const execs = state.skills.filter((s) => s.sequence === "execution");
    [["Solutioning", sols], ["Execution", execs]].forEach(([label, list]) => {
      if (!list.length) return;
      const og = document.createElement("optgroup");
      og.label = label;
      list.forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s.skill_id;
        opt.textContent = `${s.skill_id} — ${s.name}`;
        og.appendChild(opt);
      });
      sel.appendChild(og);
    });
    if (sel.options.length) {
      sel.selectedIndex = 0;
    }
    renderPipeline();
    renderProgressRail();
  }

  async function loadGate() {
    try {
      const r = await fetch("/api/gate");
      const j = await r.json();
      state.gates = j.gates || [];
    } catch { state.gates = []; }
    renderPipeline();
    renderProgressRail();
  }

  async function loadReplay() {
    try {
      const r = await fetch("/api/replay");
      const j = await r.json();
      state.frames = j.skill_frames || [];
    } catch { state.frames = []; }
    loadProjectName();
    renderPipeline();
    renderProgressRail();
    if (state.selectedSkill) updateCycleHistory(state.selectedSkill);
    autoPopulatePdi();
  }

  async function loadProjectName() {
    try {
      const r = await fetch("/api/project-name");
      const j = await r.json();
      state.projectName = j.project_name || "New Project";
    } catch {
      state.projectName = "New Project";
    }
    $("project-name").textContent = state.projectName;
  }

  function renderPipeline() {
    const ul = $("skill-pipeline");
    ul.innerHTML = "";
    ALL_SKILLS.forEach((sid) => {
      const gate = state.gates.find((g) => g.skill_id === sid);
      const frame = state.frames.find((f) => f.skill_id === sid);
      const stateInfo = skillStateFor(sid, gate, frame);
      const li = document.createElement("li");
      li.className = `pipeline-row ${stateInfo.cls}`;
      if (sid === state.selectedSkill) li.classList.add("selected");
      li.title = state.names[sid] || "";
      li.innerHTML = `
        <span class="mark">${stateInfo.mark}</span>
        <span class="sid">${sid}</span>
        <span class="sname">${escapeHtml(SHORT_NAMES[sid] || state.names[sid] || "")}</span>
        <span class="sstate">${stateInfo.label}</span>
      `;
      li.addEventListener("click", () => {
        $("skill-select").value = sid;
        onSkillSelected(sid);
      });
      ul.appendChild(li);
    });
  }

  function renderProgressRail() {
    const rail = $("progress-rail");
    rail.innerHTML = "";
    ALL_SKILLS.forEach((sid) => {
      const gate = state.gates.find((g) => g.skill_id === sid);
      const frame = state.frames.find((f) => f.skill_id === sid);
      const s = skillStateFor(sid, gate, frame);
      const node = document.createElement("span");
      node.className = `progress-node ${s.cls}`;
      node.title = `${sid} — ${state.names[sid] || ""}: ${s.label}`;
      node.textContent = sid;
      rail.appendChild(node);
    });
  }

  function skillStateFor(sid, gate, frame) {
    if (frame && frame.last_outcome === "CONFIRMED" && frame.last_convergence_state === "Exact") {
      return { cls: "exact", mark: "✓", label: "Exact" };
    }
    if (frame && frame.last_outcome === "CONFIRMED" &&
        ["Explorative", "Targeted"].includes(frame.last_convergence_state)) {
      return { cls: "progress", mark: "◐", label: `${frame.last_convergence_state} ✓` };
    }
    if (gate && gate.error) {
      return { cls: "blocked", mark: "!", label: "ERR" };
    }
    if (gate && gate.open) {
      return { cls: "open", mark: "●", label: "Open" };
    }
    return { cls: "blocked", mark: "○", label: "Blocked" };
  }

  function highlightPipelineRow(sid) {
    document.querySelectorAll(".pipeline-row").forEach((row) => {
      row.classList.toggle("selected",
        row.querySelector(".sid")?.textContent === sid);
    });
  }

  function updateCycleHistory(skill) {
    const ul = $("cycle-history");
    ul.innerHTML = "";
    const frame = state.frames.find((f) => f.skill_id === skill);
    if (!frame) {
      ul.innerHTML = `<li class="empty">no cycles for ${skill}</li>`;
      return;
    }
    const ts = frame.last_activity_at
      ? new Date(frame.last_activity_at).toLocaleString()
      : "—";
    const li = document.createElement("li");
    li.className = `history-row ${frame.last_outcome === "CONFIRMED" ? "ok" : "pending"}`;
    const path = frame.last_artefact_path || "";
    li.innerHTML = `
      <div class="history-row1">
        <span class="hstate">${escapeHtml(frame.last_convergence_state || "—")}</span>
        <span class="houtcome">${escapeHtml(frame.last_outcome || "—")}</span>
      </div>
      <span class="hts">${escapeHtml(ts)}</span>
      ${path
        ? `<button class="btn btn-ghost btn-xs load-art" data-path="${escapeAttr(path)}">open artefact</button>`
        : ""}
    `;
    ul.appendChild(li);
    if (path) {
      li.addEventListener("click", () => openArtefactFromHistory(li, path));
      const btn = li.querySelector(".load-art");
      if (btn) btn.addEventListener("click", (ev) => {
        ev.stopPropagation();
        openArtefactFromHistory(li, path);
      });
    }
  }

  function openArtefactFromHistory(row, path) {
    document.querySelectorAll("#cycle-history .history-row").forEach((r) =>
      r.classList.toggle("selected", r === row));
    activateTab("artefact");
    loadArtefact(path);
  }

  // ---- Utilities ----
  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  }
  function escapeAttr(s) { return escapeHtml(s); }

  function refreshSidebar() {
    loadGate();
    loadReplay();
  }

  // ---- Boot ----
  loadSkills().then(() => {
    const firstSkill = $("skill-select").value;
    if (firstSkill) onSkillSelected(firstSkill);
  }).then(refreshSidebar);
  setInterval(refreshSidebar, 30000);
})();
