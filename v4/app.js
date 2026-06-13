/* =============================================================
 * Community Diary v4 — app logic
 * Single global namespace. No frameworks, no build step.
 * ============================================================= */
(function () {
  "use strict";

  // ── Constants ────────────────────────────────────────────
  const STORE_KEY    = "sod2-diary-v4";
  const HISTORY_KEY  = "sod2-diary-v4-history";
  const PREFS_KEY    = "sod2-diary-v4-prefs";
  const ROSTER_KEY   = "sod2-diary-v4-roster";
  const TIES_KEY     = "sod2-diary-v4-ties";
  const SHARE_BUDGET = 2048;

  const RESOURCES = [
    { id: "food",      label: "Food" },
    { id: "med",       label: "Medicine" },
    { id: "ammo",      label: "Ammo" },
    { id: "mat",       label: "Materials" },
    { id: "fuel",      label: "Fuel" },
    { id: "parts",     label: "Parts" },
    { id: "influence", label: "Influence" }
  ];

  const MAP_BASES = {
    cascade: ["Vogel House (Starter)", "River Fort", "Loch & Keogh Self Storage", "Bridge Fort", "Container Fort", "Prescott Fire Station"],
    drucker: ["Justineau House (Starter)", "Mohr & Mohr Distributing", "Wally's Bar and Grill", "Rural Police Station", "Barricaded Strip Mall", "Fort Marshall"],
    meagher: ["Clarington House (Starter)", "Camp Kelenqua", "Squelones Brewing Company", "Knight's Family Drive-In", "The Corner Office", "Whitney Field"],
    providence: ["Lutz's Lot (Starter)", "Fir Lounge", "Lundegaard Lumber Mill", "Rusty Rosie's", "Firewatch Fortress", "Fortified Truck Stop"],
    trumbull: ["Savini Residence (Starter)", "Snyder Trucking Warehouse", "The Farmland Compound", "Marshall Manor"]
  };
  const MAP_NAMES = {
    cascade: "Cascade Hills", drucker: "Drucker County", meagher: "Meagher Valley",
    providence: "Providence Ridge", trumbull: "Trumbull Valley"
  };

  const COLOR_MOODS = {
    sepia:  { paper: "#e6dbc4", paperWarm: "#c9b896", ink: "#29261b", inkSoft: "#6b5d3f", inkBlue: "#2d4a68", inkRed: "#8b3b2e", inkPencil: "#7a6848", amber: "#d4a24c" },
    bone:   { paper: "#dfe8e8", paperWarm: "#b0c4c4", ink: "#1b2626", inkSoft: "#4a5a5a", inkBlue: "#234058", inkRed: "#7a3535", inkPencil: "#5a6a6a", amber: "#d49a3c" },
    coffee: { paper: "#f3ede3", paperWarm: "#d4c9b8", ink: "#3a3530", inkSoft: "#7a6f5f", inkBlue: "#3d5870", inkRed: "#9a4b3e", inkPencil: "#8a7a65", amber: "#daa958" },
    olive:  { paper: "#dfe3d0", paperWarm: "#bcc4a8", ink: "#262a1f", inkSoft: "#545a45", inkBlue: "#2d4552", inkRed: "#7d3f2e", inkPencil: "#65704e", amber: "#c9a03d" }
  };

  // Randomized placeholder samples
  const SAMPLES = {
    communityNames: ["The Holdfast", "Phoenix Squad", "Haven Collective", "Red Valley Survivors", "The Coalition", "Last Stand Crew"],
    events: [
      "Cleared the police station. Lost Marcus to a feral ambush. Lily traded a med kit for two rifle rounds.",
      "Scavenged the library—found antibiotics. Nadia broke her arm during a horde escape. Recruited a mechanic named Sam.",
      "Moved to Whitney Field. Fought off a blood plague horde at dawn. Maya's becoming a leader.",
      "Infirmary upgrade finished. Ed killed a juggernaut solo—took three pipe bombs. Morale's improving.",
      "Lost contact with the enclave near the bridge. Found a cache of fuel and building materials. Reinforced the fence line."
    ],
    deaths: [
      "Marcus — feral ambush at the station.",
      "Ed — blood plague, Day 8. Went down fighting a screamer pack.",
      "Jin — friendly fire during a siege. Accident. We're all shaken.",
      "Nadia — ran out of stamina clearing infestations. Didn't make it back."
    ],
    newSurvivors: [
      "Nadia — found at the hardware store, good with tools.",
      "Sam — ex-firefighter, joined at the truck stop.",
      "Riley — showed up asking for shelter. Says they're ex-military.",
      "Jordan — trader from another enclave. Staying with us now."
    ],
    notes: [
      "Should reinforce east fence. Stay sharp.",
      "People getting tired—need more rest rotations. Good day overall.",
      "Low on meds. Need to scout the clinic tomorrow.",
      "Plague hearts getting aggressive. Consider hitting two in one run.",
      "Morale's fragile. Maya suggested movie night. Might help."
    ],
    survivorNames: ["Maya Brooks", "Jin Park", "Marcus Webb", "Ed Santos", "Nadia Cole", "Riley Cross", "Sam Torres", "Jordan Lee", "Lily Chen", "Alex Kim"],
    bios: ["Black F, retired EMT", "Asian M, ex-cop", "White M, construction worker", "Latino M, mechanic", "White F, librarian", "Mixed NB, ex-military", "Latino M, firefighter", "Asian F, engineer"],
    traits: ["Tough · Leader", "Asthma · Quirky", "Hopeful · Night Owl", "Pessimist · Skilled Labor", "Close Combat · Determined", "Resourceful · Insomniac"],
    skills: ["Shooting · Medicine", "Wits · Repair", "Cardio · Cooking", "Fighting · Construction", "Chemistry · Gardening", "Driving · Mechanics"]
  };

  // ── State ───────────────────────────────────────────────
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

  let saveTimer = null;
  let history = [];
  let roster = [];
  let ties = [];
  let editingId = null;
  let lastEditedId = null;

  // ── Resources list build ────────────────────────────────
  function buildResources() {
    const list = $("#resourceList");
    list.innerHTML = RESOURCES.map(r => `
      <li class="resource" data-id="${r.id}">
        <span class="resource__name">${r.label}</span>
        <span class="resource__delta">
          <input type="number" id="${r.id}From" placeholder="—" inputmode="numeric" aria-label="${r.label} start">
          <span class="resource__arrow">→</span>
          <input type="number" id="${r.id}To" placeholder="—" inputmode="numeric" aria-label="${r.label} end">
          <span class="resource__diff" id="${r.id}Diff"></span>
        </span>
      </li>
    `).join("");

    RESOURCES.forEach(r => {
      const from = $("#" + r.id + "From");
      const to = $("#" + r.id + "To");
      [from, to].forEach(el => el.addEventListener("input", () => {
        updateResourceDiff(r.id);
        scheduleSave();
      }));
    });
  }
  function updateResourceDiff(id) {
    const a = parseFloat($("#" + id + "From").value);
    const b = parseFloat($("#" + id + "To").value);
    const el = $("#" + id + "Diff");
    el.className = "resource__diff";
    if (isNaN(a) || isNaN(b)) { el.textContent = ""; return; }
    const d = b - a;
    if (d === 0) { el.textContent = "0"; return; }
    el.textContent = (d > 0 ? "+" : "") + d;
    el.classList.add(d > 0 ? "resource__diff--up" : "resource__diff--down");
  }

  // ── Map / base linkage ──────────────────────────────────
  function refreshBaseSelect(keepValue) {
    const map = $("#mapSelect").value;
    const sel = $("#baseSelect");
    const prev = keepValue || sel.value;
    sel.innerHTML = "";
    if (!map) {
      sel.disabled = true;
      sel.innerHTML = '<option value="">Pick map first…</option>';
      return;
    }
    sel.disabled = false;
    sel.appendChild(new Option("—", ""));
    (MAP_BASES[map] || []).forEach(b => sel.appendChild(new Option(b, b)));
    if (prev && Array.from(sel.options).some(o => o.value === prev)) sel.value = prev;
  }

  // ── Steppers (Day, Plague Hearts, Survivors) ────────────
  function setupSteppers() {
    $$("[data-step]").forEach(btn => {
      btn.addEventListener("click", () => {
        const target = $("#" + (btn.dataset.step === "day" ? "dayNumber" : btn.dataset.step));
        if (!target) return;
        const delta = parseInt(btn.dataset.delta, 10);
        const val = (parseInt(target.value, 10) || 0) + delta;
        const min = parseInt(target.min, 10);
        target.value = Number.isFinite(min) ? Math.max(min, val) : val;
        target.dispatchEvent(new Event("input"));
        scheduleSave();
      });
    });
  }

  // ── Morale ──────────────────────────────────────────────
  function updateDiaryTitle() {
    const name = ($("#communityName").value || "").trim();
    const main = $("#diaryTitleMain");
    const sub = $("#diaryTitleSub");
    if (name) {
      main.textContent = name;
      sub.textContent = "COMMUNITY DIARY · STATE OF DECAY 2";
      sub.className = "diary__title-sub diary__title-sub--alt";
      // Auto-scale long names
      if (name.length > 16) main.classList.add("diary__title-main--small");
      else main.classList.remove("diary__title-main--small");
    } else {
      main.textContent = "Community Diary";
      sub.textContent = "STATE OF DECAY 2 · NARRATIVE LOGBOOK";
      sub.className = "diary__title-sub";
      main.classList.remove("diary__title-main--small");
    }
  }

  function updateMorale() {
    const slider = $("#morale");
    const valInput = $("#moraleValue");
    const v = parseInt(slider.value, 10) || 0;
    valInput.value = v;
    const faces = { neg: v <= -33, pos: v >= 33 };
    const mid = !faces.neg && !faces.pos;
    $(".face--neg").classList.toggle("is-on", faces.neg);
    $(".face--mid").classList.toggle("is-on", mid);
    $(".face--pos").classList.toggle("is-on", faces.pos);
  }

  // ── State serialize / load ──────────────────────────────
  function collectFormState() {
    const s = {
      communityName: $("#communityName").value.trim(),
      map: $("#mapSelect").value,
      base: $("#baseSelect").value,
      difficulty: $("#difficultySelect").value,
      dayNumber: parseInt($("#dayNumber").value, 10) || 1,
      plagueHearts: parseInt($("#plagueHearts").value, 10) || 0,
      survivors: parseInt($("#survivors").value, 10) || 0,
      morale: parseInt($("#morale").value, 10) || 0,
      events: $("#events").value,
      deaths: $("#deaths").value,
      newSurvivors: $("#newSurvivors").value,
      notes: $("#notes").value,
      resources: {}
    };
    RESOURCES.forEach(r => {
      s.resources[r.id] = {
        from: $("#" + r.id + "From").value,
        to:   $("#" + r.id + "To").value
      };
    });
    return s;
  }
  function applyFormState(s) {
    if (!s) return;
    const setIf = (id, v) => { if (typeof v !== "undefined" && v !== null) $("#" + id).value = v; };
    setIf("communityName", s.communityName);
    setIf("mapSelect", s.map);
    refreshBaseSelect(s.base);
    setIf("baseSelect", s.base);
    setIf("difficultySelect", s.difficulty);
    setIf("dayNumber", s.dayNumber || 1);
    setIf("plagueHearts", s.plagueHearts || 0);
    setIf("survivors", s.survivors || 0);
    setIf("morale", s.morale || 0);
    setIf("events", s.events);
    setIf("deaths", s.deaths);
    setIf("newSurvivors", s.newSurvivors);
    setIf("notes", s.notes);
    if (s.resources) {
      RESOURCES.forEach(r => {
        const v = s.resources[r.id] || {};
        $("#" + r.id + "From").value = v.from || "";
        $("#" + r.id + "To").value   = v.to   || "";
        updateResourceDiff(r.id);
      });
    }
    updateMorale();
  }
  function persist() {
    try {
      localStorage.setItem(STORE_KEY,   JSON.stringify(collectFormState()));
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
      localStorage.setItem(ROSTER_KEY,  JSON.stringify(roster));
      localStorage.setItem(TIES_KEY,    JSON.stringify(ties));
    } catch (e) { /* ignore quota errors */ }
  }
  function scheduleSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(persist, 500);
  }
  function loadAll() {
    try {
      const f = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
      if (f) applyFormState(f);
    } catch (e) {}
    try {
      history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    } catch (e) { history = []; }
    try {
      roster = JSON.parse(localStorage.getItem(ROSTER_KEY) || "[]");
    } catch (e) { roster = []; }
    try {
      ties = JSON.parse(localStorage.getItem(TIES_KEY) || "[]");
    } catch (e) { ties = []; }
    migrateLegacyTies();
    normalizeTies(); // backfill status on ties saved under the old boolean model
  }

  function migrateLegacyTies() {
    const prefs = loadPrefs();
    if (prefs.tiesMigrated) return;
    try {
      const legacy = JSON.parse(localStorage.getItem("sod2.relationships") || "[]");
      if (!legacy.length) { savePrefs(Object.assign(loadPrefs(), { tiesMigrated: true })); return; }
      const seen = new Set();
      legacy.forEach(function (rel) {
        if (!rel.fromSurvivorId || !rel.toSurvivorId) return;
        const pk = pairKey(rel.fromSurvivorId, rel.toSurvivorId) + "|" + (rel.kind || "friend");
        if (seen.has(pk)) return;
        seen.add(pk);
        const [a, b] = [rel.fromSurvivorId, rel.toSurvivorId].sort();
        ties.push({
          id: "tie-" + Math.random().toString(36).slice(2, 9),
          a, b,
          kind: rel.kind || "friend",
          label: rel.label || "",
          since: rel.since || 1,
          status: rel.status === "strained" ? "strained" : "active"
        });
      });
      savePrefs(Object.assign(loadPrefs(), { tiesMigrated: true }));
    } catch (e) {
      savePrefs(Object.assign(loadPrefs(), { tiesMigrated: true }));
    }
  }

  // ── Roster ──────────────────────────────────────────────
  function uid() { return "s-" + Math.random().toString(36).slice(2, 9); }

  function addSurvivor(data) {
    roster.push({
      id: uid(),
      name: data.name,
      age: data.age,
      bio: data.bio,
      traits: data.traits,
      skills: data.skills,
      dayJoined: data.dayJoined || $("#dayNumber").value || 1,
      status: "active" // active | fallen | exiled | legacy
    });
    renderRoster();
    persist();
  }
  function setStatus(id, status) {
    const s = roster.find(s => s.id === id);
    if (!s) return;
    s.status = status;
    // Death/exile converts this survivor's living ties to `mourned`.
    if (status === "fallen" || status === "exiled") mournTiesFor(id);
    renderRoster();
    persist();
  }
  function removeSurvivor(id) {
    roster = roster.filter(s => s.id !== id);
    renderRoster();
    persist();
  }
  function renderRoster() {
    const list = $("#rosterList");
    const active = roster.filter(s => s.status === "active");
    const fallen = roster.filter(s => s.status === "fallen" || s.status === "exiled");
    const legacy = roster.filter(s => s.status === "legacy");
    $("#rosterCount").textContent = active.length;
    $("#kiaCount").textContent    = fallen.length;
    $("#legacyCount").textContent = legacy.length;

    if (!roster.length) {
      list.innerHTML = '<div class="roster__empty">No one in the community yet. Add your first survivor below.</div>';
      return;
    }
    const grouped = [
      { tag: "active", items: active, title: "" },
      { tag: "legacy", items: legacy, title: "Legacy Pool" },
      { tag: "fallen", items: fallen, title: "The Fallen / Exiled" }
    ];
    list.innerHTML = grouped
      .filter(g => g.items.length)
      .map(g => {
        const heading = g.title ? `<div class="roster__group-title" style="grid-column:1/-1;font-family:var(--font-stamp);font-size:11px;letter-spacing:2px;color:var(--ink-soft);text-transform:uppercase;margin:8px 0 -4px;">${g.title}</div>` : "";
        return heading + g.items.map(s => survivorCard(s, g.tag)).join("");
      })
      .join("");

    // Focus management: edit open → first field; edit closed → Edit button
    if (editingId) {
      const firstField = $(`#edit-name-${editingId}`);
      if (firstField) firstField.focus();
    } else if (lastEditedId) {
      const editBtn = $(`[data-act="edit"][data-id="${lastEditedId}"]`);
      if (editBtn) editBtn.focus();
      lastEditedId = null;
    }

    // Desktop pencil-line overlay (PHA-396). rAF so card rects are settled.
    if (typeof requestAnimationFrame === "function") {
      requestAnimationFrame(renderTieOverlays);
    } else {
      renderTieOverlays();
    }
  }

  // ── Ties That Bind — desktop pencil-line overlay (PHA-396) ──
  // Desktop-only SVG connecting partner/family pairs across the roster
  // grid. Wrapped end-to-end in try/catch: a bad render must NEVER take
  // down the diary (the prior overlay attempt broke the deploy).
  const TIE_OVERLAY_MQ = (typeof window.matchMedia === "function")
    ? window.matchMedia("(hover: hover) and (min-width: 1100px)")
    : { matches: false, addEventListener: null };
  const OVERLAY_KINDS = { partner: true, family: true }; // highest-priority kinds only
  const SVG_NS = "http://www.w3.org/2000/svg";

  function renderTieOverlays() {
    try {
      const list = document.getElementById("rosterList");
      if (!list) return;
      // Always clear the prior overlay first, even when we won't redraw.
      const stale = list.querySelector(".tie-line-overlay");
      if (stale) stale.remove();

      if (!TIE_OVERLAY_MQ.matches) return;          // desktop / hover only
      if (!Array.isArray(ties) || !ties.length) return;

      const box = list.getBoundingClientRect();
      if (!box.width || !box.height) return;        // grid hidden / not laid out

      const svg = document.createElementNS(SVG_NS, "svg");
      svg.setAttribute("class", "tie-line-overlay");
      svg.setAttribute("aria-hidden", "true");
      svg.setAttribute("width", box.width);
      svg.setAttribute("height", box.height);
      svg.setAttribute("viewBox", "0 0 " + box.width + " " + box.height);

      let drawn = 0;
      ties.forEach(function (t) {
        if (!t || !OVERLAY_KINDS[t.kind]) return;
        const ca = document.getElementById("card-" + t.a);
        const cb = document.getElementById("card-" + t.b);
        if (!ca || !cb) return;
        const ra = ca.getBoundingClientRect();
        const rb = cb.getBoundingClientRect();
        if (!ra.width || !rb.width) return;         // a card is display:none
        const aSurv = roster.find(function (r) { return r.id === t.a; });
        const bSurv = roster.find(function (r) { return r.id === t.b; });
        const deadParty = (aSurv && aSurv.status !== "active") ||
                          (bSurv && bSurv.status !== "active");
        const line = document.createElementNS(SVG_NS, "line");
        let cls = "tie-line tie-line--" + t.kind;
        // Status drives the treatment: severed = tear-away, mourned = its own
        // faint stroke, strained = dotted. deadParty is a defensive fallback for
        // legacy ties that never got converted to mourned.
        if (t.status === "severed")      cls += " tie-line--severed";
        else if (t.status === "mourned") cls += " tie-line--mourned";
        else if (t.status === "strained" || deadParty) cls += " tie-line--strained";
        line.setAttribute("class", cls);
        // Endpoints for hover-reveal: light only the hovered survivor's ties.
        line.setAttribute("data-a", t.a);
        line.setAttribute("data-b", t.b);
        line.setAttribute("x1", ra.left + ra.width / 2 - box.left);
        line.setAttribute("y1", ra.top + ra.height / 2 - box.top);
        line.setAttribute("x2", rb.left + rb.width / 2 - box.left);
        line.setAttribute("y2", rb.top + rb.height / 2 - box.top);
        svg.appendChild(line);
        drawn++;
      });

      if (drawn) list.appendChild(svg);
    } catch (e) {
      if (window.console && console.warn) console.warn("tie overlay skipped:", e);
    }
  }

  // Light up just the ties touching survivor `id` (pass null to hide all).
  function lightTiesFor(id) {
    try {
      const list = document.getElementById("rosterList");
      const svg = list && list.querySelector(".tie-line-overlay");
      if (!svg) return;
      const lines = svg.querySelectorAll(".tie-line");
      for (let i = 0; i < lines.length; i++) {
        const l = lines[i];
        const on = id != null && (l.getAttribute("data-a") === id || l.getAttribute("data-b") === id);
        l.classList.toggle("is-lit", on);
      }
    } catch (e) { /* never break hover */ }
  }
  function esc(s) { return (s == null ? "" : String(s)).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c]); }

  function survivorCard(s, tag) {
    if (editingId === s.id) return survivorCardEdit(s);
    const isActive = tag === "active";
    let actionHtml = "";
    if (isActive) {
      actionHtml = `
        <button data-act="edit"   data-id="${s.id}" aria-label="Edit ${esc(s.name)}">Edit</button>
        <button data-act="kill"   data-id="${s.id}" class="dangerous">Killed</button>
        <button data-act="exile"  data-id="${s.id}" class="dangerous">Exiled</button>
        <button data-act="legacy" data-id="${s.id}">→ Legacy</button>
        <button data-act="remove" data-id="${s.id}">Remove</button>
      `;
    } else {
      actionHtml = `
        <button data-act="restore" data-id="${s.id}">Restore</button>
        <button data-act="remove"  data-id="${s.id}">Remove</button>
      `;
    }
    const cls = "card-survivor"
      + (s.status === "fallen" ? " is-fallen" : "")
      + (s.status === "exiled" ? " is-exiled" : "")
      + (s.status === "legacy" ? " is-legacy" : "");
    const tiesHtml = isActive ? buildTiesHtml(s) : "";
    return `
      <article class="${cls}" id="card-${esc(s.id)}">
        <h3>${esc(s.name)}${s.age ? `, ${esc(s.age)}` : ""}</h3>
        <div class="joined">Joined D${esc(s.dayJoined)}${s.status === "fallen" ? " · KIA" : s.status === "exiled" ? " · Exiled" : s.status === "legacy" ? " · Retired" : ""}</div>
        ${s.bio ? `<p class="line"><span class="lbl">Bio</span>${esc(s.bio)}</p>` : ""}
        ${s.traits ? `<p class="line"><span class="lbl">Traits</span>${esc(s.traits)}</p>` : ""}
        ${s.skills ? `<p class="line"><span class="lbl">Skills</span>${esc(s.skills)}</p>` : ""}
        <div class="actions">${actionHtml}</div>
        ${tiesHtml}
      </article>
    `;
  }

  function survivorCardEdit(s) {
    return `
      <article class="card-survivor is-editing" id="card-${esc(s.id)}">
        <form class="edit-form" id="edit-form-${esc(s.id)}">
          <label for="edit-name-${esc(s.id)}">
            <span class="lbl">Name</span>
            <input id="edit-name-${esc(s.id)}" name="name" type="text" value="${esc(s.name)}" required autocomplete="off" class="edit-field">
          </label>
          <label for="edit-age-${esc(s.id)}">
            <span class="lbl">Age</span>
            <input id="edit-age-${esc(s.id)}" name="age" type="number" min="0" max="120" value="${esc(s.age || "")}" inputmode="numeric" class="edit-field">
          </label>
          <label for="edit-bio-${esc(s.id)}">
            <span class="lbl">Bio</span>
            <input id="edit-bio-${esc(s.id)}" name="bio" type="text" value="${esc(s.bio || "")}" autocomplete="off" class="edit-field">
          </label>
          <label for="edit-traits-${esc(s.id)}">
            <span class="lbl">Traits</span>
            <input id="edit-traits-${esc(s.id)}" name="traits" type="text" value="${esc(s.traits || "")}" autocomplete="off" class="edit-field">
          </label>
          <label for="edit-skills-${esc(s.id)}">
            <span class="lbl">Skills</span>
            <input id="edit-skills-${esc(s.id)}" name="skills" type="text" value="${esc(s.skills || "")}" autocomplete="off" class="edit-field">
          </label>
          <div class="actions">
            <button type="submit" data-act="edit-save" data-id="${esc(s.id)}" class="ink-btn">Save</button>
            <button type="button" data-act="edit-cancel" data-id="${esc(s.id)}">Cancel</button>
          </div>
        </form>
      </article>
    `;
  }
  function setupRosterEvents() {
    $("#rosterForm").addEventListener("submit", function (e) {
      e.preventDefault();
      const fd = new FormData(this);
      addSurvivor({
        name: fd.get("name").toString().trim(),
        age: fd.get("age"),
        bio: fd.get("bio").toString().trim(),
        traits: fd.get("traits").toString().trim(),
        skills: fd.get("skills").toString().trim(),
        dayJoined: fd.get("dayJoined")
      });
      this.reset();
      notify("Added to roster");
    });
    $("#rosterList").addEventListener("click", function (e) {
      const btn = e.target.closest("[data-act]");
      if (!btn) return;
      const id = btn.dataset.id;
      const tieId = btn.dataset.tie;
      switch (btn.dataset.act) {
        case "kill":    setStatus(id, "fallen"); notify("Marked fallen"); break;
        case "exile":   setStatus(id, "exiled"); notify("Marked exiled"); break;
        case "legacy":  setStatus(id, "legacy"); notify("Sent to legacy pool"); break;
        case "restore": setStatus(id, "active"); notify("Restored"); break;
        case "remove":
          if (confirm("Remove this survivor permanently?")) { removeSurvivor(id); notify("Removed"); }
          break;
        case "edit":
          editingId = id;
          renderRoster();
          break;
        case "edit-cancel":
          lastEditedId = editingId;
          editingId = null;
          renderRoster();
          break;
        case "sever":
          if (tieId && confirm("Sever this tie?")) { severTie(tieId); notify("Tie severed"); }
          break;
        case "strained":
          if (tieId) { toggleStrained(tieId); const t = ties.find(x => x.id === tieId); notify(t && t.status === "strained" ? "Marked strained" : "Strain cleared"); }
          break;
      }
    });

    // Hover-reveal: ties stay invisible until you hover a survivor card,
    // then only that survivor's connections fade in. Keeps the grid clean.
    const rosterEl = $("#rosterList");
    rosterEl.addEventListener("pointerover", function (e) {
      const card = e.target.closest && e.target.closest(".card-survivor");
      if (!card || !card.id) return;
      lightTiesFor(card.id.replace(/^card-/, ""));
    });
    rosterEl.addEventListener("pointerout", function (e) {
      const card = e.target.closest && e.target.closest(".card-survivor");
      const to = e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest(".card-survivor");
      if (card && card !== to) lightTiesFor(null); // left the card → hide again
    });

    // edit-save via form submit
    $("#rosterList").addEventListener("submit", function (e) {
      const form = e.target.closest(".edit-form");
      if (!form) return;
      e.preventDefault();
      const sid = form.id.replace("edit-form-", "");
      const s = roster.find(r => r.id === sid);
      if (!s) return;
      const fd = new FormData(form);
      s.name   = fd.get("name").toString().trim() || s.name;
      s.age    = fd.get("age").toString().trim();
      s.bio    = fd.get("bio").toString().trim();
      s.traits = fd.get("traits").toString().trim();
      s.skills = fd.get("skills").toString().trim();
      lastEditedId = sid;
      editingId = null;
      renderRoster();
      persist();
      notify("Saved " + s.name);
    });

    // tie add form submit
    $("#rosterList").addEventListener("submit", function (e) {
      const form = e.target.closest(".tie-add-form");
      if (!form) return;
      e.preventDefault();
      const fromId = form.dataset.from;
      const fd = new FormData(form);
      const toId = fd.get("to");
      if (!toId) return;
      addTie(fromId, toId, fd.get("kind") || "friend", fd.get("label") || "", parseInt(fd.get("since"), 10) || 1);
      notify("Tie added");
      form.reset();
    });

    // Esc cancels edit
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && editingId) {
        lastEditedId = editingId;
        editingId = null;
        renderRoster();
      }
    });
  }

  // ── Ties ─────────────────────────────────────────────────
  // Tie lifecycle is no-DELETE: a tie is a permanent emotional record.
  // status ∈ active | strained | severed | mourned. You don't erase a
  // relationship when it ends — you mark how it ended (PHA-1057 / PHA-347).
  const TIE_STATUSES = ["active", "strained", "severed", "mourned"];

  function pairKey(a, b) { return [a, b].sort().join("|"); }

  function currentDay() { return parseInt($("#dayNumber").value, 10) || 1; }

  // Backfill the status field on a tie loaded from older saves: the old model
  // carried a boolean `strained`; absence of both → active. Idempotent.
  function normalizeTie(t) {
    if (!t || typeof t !== "object") return t;
    if (!t.status || TIE_STATUSES.indexOf(t.status) === -1) {
      t.status = t.strained ? "strained" : "active";
    }
    delete t.strained;
    return t;
  }
  function normalizeTies() {
    if (Array.isArray(ties)) ties = ties.map(normalizeTie);
  }
  const TIE_STATUS_LABEL = { strained: "STRAINED", severed: "SEVERED", mourned: "MOURNED" };

  function addTie(fromId, toId, kind, label, since) {
    const pk = pairKey(fromId, toId);
    const existing = ties.find(t => pairKey(t.a, t.b) === pk && t.kind === kind);
    if (existing) {
      existing.label = label;
      existing.since = since;
    } else {
      const sorted = [fromId, toId].sort();
      ties.push({ id: "tie-" + Math.random().toString(36).slice(2, 9), a: sorted[0], b: sorted[1], kind: kind, label: label, since: since, status: "active" });
    }
    renderRoster();
    persist();
  }

  // No-DELETE: severing marks how the tie ended, it doesn't erase the row.
  // The record stays so it can still render (tear-away overlay, report history).
  function severTie(id) {
    const t = ties.find(t => t.id === id);
    if (!t || t.status === "severed") return;
    t.status = "severed";
    t.endedDay = currentDay();
    renderRoster();
    persist();
  }

  // Strain is a status now, toggled between active ⇄ strained. Severed and
  // mourned are terminal end-states and aren't re-strainable.
  function toggleStrained(id) {
    const t = ties.find(t => t.id === id);
    if (!t || t.status === "severed" || t.status === "mourned") return;
    t.status = t.status === "strained" ? "active" : "strained";
    renderRoster();
    persist();
  }

  // The one sanctioned automation (PHA-347): when a survivor dies or is exiled,
  // their living ties become `mourned`. Severed ties are left as-is — that
  // history already records how they ended.
  function mournTiesFor(sid) {
    let changed = false;
    const day = currentDay();
    ties.forEach(function (t) {
      if (t.a !== sid && t.b !== sid) return;
      if (t.status === "active" || t.status === "strained") {
        t.status = "mourned";
        if (t.endedDay == null) t.endedDay = day;
        changed = true;
      }
    });
    return changed;
  }

  function tiesForSurvivor(sid) {
    return ties.filter(t => t.a === sid || t.b === sid);
  }

  function buildTiesHtml(s) {
    const myTies = tiesForSurvivor(s.id);
    const partners = roster.filter(r => r.id !== s.id && r.status === "active");
    const listHtml = myTies.length
      ? myTies.map(t => {
          const partnerId = (t.a === s.id ? t.b : t.a);
          const partnerSurv = roster.find(r => r.id === partnerId);
          const partnerName = partnerSurv ? partnerSurv.name : "Unknown";
          const status = t.status || "active";
          const ended = (status === "severed" || status === "mourned") && t.endedDay
            ? ` · ended D${t.endedDay}` : "";
          const statusTag = TIE_STATUS_LABEL[status]
            ? `<span class="tie-status tie-status--${status}" aria-label="${TIE_STATUS_LABEL[status].toLowerCase()} tie">${TIE_STATUS_LABEL[status]}</span>`
            : "";
          const kindLabel = t.kind.charAt(0).toUpperCase() + t.kind.slice(1);
          const displayLabel = t.label ? ` — "${esc(t.label)}"` : "";
          // Severed/mourned are terminal records — no destructive affordance to
          // re-strain or re-sever them. Active/strained still toggle.
          const isTerminal = status === "severed" || status === "mourned";
          const acts = isTerminal ? "" : `
              <span class="tie-acts">
                <button type="button" data-act="strained" data-tie="${esc(t.id)}" class="tie-btn" aria-label="${status === "strained" ? "Clear strained" : "Mark strained"} tie with ${esc(partnerName)}">${status === "strained" ? "✓ Strained" : "Strain"}</button>
                <button type="button" data-act="sever" data-tie="${esc(t.id)}" class="tie-btn tie-btn--sever" aria-label="Sever tie with ${esc(partnerName)}">Sever</button>
              </span>`;
          return `
            <div class="tie-row tie-row--${status}">
              <span class="tie-info">${kindLabel}: <strong>${esc(partnerName)}</strong>${displayLabel}${t.since ? ` · D${t.since}` : ""}${ended}${statusTag}</span>${acts}
            </div>`;
        }).join("")
      : `<div class="tie-empty">No ties yet.</div>`;

    const day = parseInt($("#dayNumber").value, 10) || 1;
    const partnerOptions = partners.length
      ? partners.map(p => `<option value="${esc(p.id)}">${esc(p.name)}</option>`).join("")
      : "";

    const addForm = partners.length ? `
      <form class="tie-add-form" data-from="${esc(s.id)}">
        <label class="sr-only" for="tie-to-${esc(s.id)}">Tied to</label>
        <select id="tie-to-${esc(s.id)}" name="to" class="tie-select" required>
          <option value="">Tied to…</option>
          ${partnerOptions}
        </select>
        <label class="sr-only" for="tie-kind-${esc(s.id)}">Kind</label>
        <select id="tie-kind-${esc(s.id)}" name="kind" class="tie-select">
          <option value="partner">Partner</option>
          <option value="family">Family</option>
          <option value="mentor">Mentor</option>
          <option value="rival">Rival</option>
          <option value="friend">Friend</option>
        </select>
        <label class="sr-only" for="tie-label-${esc(s.id)}">Label</label>
        <input id="tie-label-${esc(s.id)}" name="label" type="text" class="tie-input" placeholder="Label…" autocomplete="off" maxlength="40">
        <label class="sr-only" for="tie-since-${esc(s.id)}">Day formed</label>
        <input id="tie-since-${esc(s.id)}" name="since" type="number" class="tie-input tie-input--day" min="1" value="${day}" inputmode="numeric" aria-label="Day formed">
        <button type="submit" class="tie-btn tie-btn--add">+ Tie</button>
      </form>` : `<p class="tie-empty">Add more survivors to create ties.</p>`;

    return `
      <details class="tie-panel">
        <summary class="tie-panel__toggle">Ties ▾ <span class="tie-count" aria-label="${myTies.length} ties">${myTies.length}</span></summary>
        <div class="tie-list" aria-live="polite" aria-atomic="false">${listHtml}</div>
        ${addForm}
      </details>`;
  }

  // ── Report generation ───────────────────────────────────
  function generateReport() {
    const s = collectFormState();
    const lines = [];
    const cn = s.communityName || "The Survivors";
    lines.push(`${cn} — Day ${s.dayNumber} Report`);
    const where = [];
    if (s.map) where.push(MAP_NAMES[s.map] || s.map);
    if (s.difficulty) where.push(s.difficulty);
    if (s.base) where.push(s.base);
    if (where.length) lines.push(where.join(" | "));
    lines.push("");
    if (s.plagueHearts) lines.push(`Plague Hearts: ${s.plagueHearts}`);
    if (s.survivors)    lines.push(`Survivors: ${s.survivors}`);
    if (s.morale)       lines.push(`Morale: ${formatMorale(s.morale)} (${s.morale})`);
    if (s.plagueHearts || s.survivors || s.morale) lines.push("");

    // Resources
    const rows = RESOURCES.map(r => {
      const v = s.resources[r.id];
      if (!v || (v.from === "" && v.to === "")) return null;
      const a = v.from === "" ? "?" : v.from;
      const b = v.to   === "" ? "?" : v.to;
      return `${r.label}: ${a} → ${b}`;
    }).filter(Boolean);
    if (rows.length) {
      lines.push(...rows, "");
    }

    if (s.events.trim())       lines.push("Events:", s.events.trim(), "");
    if (s.deaths.trim())       lines.push("Lost:", s.deaths.trim(), "");
    if (s.newSurvivors.trim()) lines.push("New arrivals:", s.newSurvivors.trim(), "");
    if (s.notes.trim())        lines.push("Notes:", s.notes.trim(), "");

    // Roster summaries
    const active = roster.filter(r => r.status === "active");
    const fallen = roster.filter(r => r.status === "fallen" || r.status === "exiled");
    if (active.length) {
      lines.push(`Active Roster (${active.length}):`);
      active.forEach(r => lines.push("- " + survivorLine(r)));
      lines.push("");
    }
    if (fallen.length) {
      lines.push(`Lost & Exiled (${fallen.length}):`);
      fallen.forEach(r => lines.push("- " + survivorLine(r)));
      lines.push("");
    }

    // Relationships — feeds the social graph to the diary-writing LLM.
    const tieLines = (Array.isArray(ties) ? ties : [])
      .map(t => relationshipLine(t))
      .filter(Boolean);
    if (tieLines.length) {
      lines.push(`Relationships (${tieLines.length}):`);
      lines.push(...tieLines, "");
    }
    return lines.join("\n").trim();
  }
  function relationshipLine(t) {
    if (!t) return null;
    const a = roster.find(r => r.id === t.a);
    const b = roster.find(r => r.id === t.b);
    if (!a || !b) return null; // skip orphaned ties
    const kind = t.kind ? t.kind.charAt(0).toUpperCase() + t.kind.slice(1) : "Tie";
    const meta = [];
    if (t.label) meta.push(t.label);
    if (t.since) meta.push("since Day " + t.since);
    const status = t.status || "active";
    if (status === "strained") meta.push("strained");
    else if (status === "severed") meta.push("severed" + (t.endedDay ? " Day " + t.endedDay : ""));
    else if (status === "mourned") meta.push("mourned" + (t.endedDay ? " Day " + t.endedDay : ""));
    const aTag = a.status !== "active" ? " (" + a.status + ")" : "";
    const bTag = b.status !== "active" ? " (" + b.status + ")" : "";
    return `- ${a.name}${aTag} & ${b.name}${bTag} — ${kind}${meta.length ? " (" + meta.join(", ") + ")" : ""}`;
  }
  function survivorLine(r) {
    const tags = [r.bio, r.traits, r.skills].filter(Boolean).join(" | ");
    const joined = r.dayJoined ? ` | Joined Day ${r.dayJoined}` : "";
    const status = r.status === "fallen" ? " | Killed" : r.status === "exiled" ? " | Exiled" : "";
    return `${r.name}${r.age ? ", " + r.age : ""}${tags ? " | " + tags : ""}${joined}${status}`;
  }
  function formatMorale(v) {
    if (v >= 60) return "Soaring";
    if (v >= 33) return "Good";
    if (v >= -32) return "Holding";
    if (v >= -59) return "Low";
    return "Crushed";
  }

  // ── History ─────────────────────────────────────────────
  function renderHistory() {
    const list = $("#historyList");
    $("#histCount").textContent = history.length;
    $("#historyEmpty").style.display = history.length ? "none" : "";
    list.innerHTML = history.map((h, i) => `
      <li class="history__entry" data-i="${i}">
        <header>
          <strong>Day ${esc(h.dayNumber || "?")}</strong>
          <span>${esc(h.savedAt || "")}</span>
          <button class="expand" data-act="expand">View ▾</button>
          <button class="expand" data-act="copy-one">Copy</button>
          <button class="expand" data-act="delete-one" style="color:var(--ink-red);">Delete</button>
        </header>
        <pre>${esc(h.text || "")}</pre>
      </li>
    `).join("");
  }
  function saveToHistory(text) {
    const s = collectFormState();
    const now = new Date();
    const stamp = now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate()) + " " + pad(now.getHours()) + ":" + pad(now.getMinutes());
    history.unshift({
      dayNumber: s.dayNumber,
      savedAt: stamp,
      text: text
    });
    if (history.length > 365) history = history.slice(0, 365);
    renderHistory();
    persist();
  }
  function pad(n) { return String(n).padStart(2, "0"); }
  function setupHistoryEvents() {
    $("#historyList").addEventListener("click", function (e) {
      const btn = e.target.closest("[data-act]");
      if (!btn) return;
      const li = btn.closest(".history__entry");
      const idx = parseInt(li.dataset.i, 10);
      const entry = history[idx];
      if (!entry) return;
      switch (btn.dataset.act) {
        case "expand":
          li.classList.toggle("is-open");
          btn.textContent = li.classList.contains("is-open") ? "Hide ▴" : "View ▾";
          break;
        case "copy-one":
          copyText(entry.text); notify("Report copied");
          break;
        case "delete-one":
          if (confirm("Delete this report?")) {
            history.splice(idx, 1); renderHistory(); persist(); notify("Deleted");
          }
          break;
      }
    });
    $("#exportBtn").addEventListener("click", exportJson);
    $("#importBtn").addEventListener("click", () => $("#importInput").click());
    $("#importInput").addEventListener("change", importJson);
    $("#copyAllBtn").addEventListener("click", () => {
      const all = history.map(h => `=== Day ${h.dayNumber} (${h.savedAt}) ===\n${h.text}`).join("\n\n");
      copyText(all);
      notify("All reports copied");
    });
    $("#clearBtn").addEventListener("click", () => {
      if (history.length && confirm("Clear all history? This cannot be undone.")) {
        history = []; renderHistory(); persist(); notify("History cleared");
      }
    });
    $("#newBookBtn").addEventListener("click", () => {
      if (confirm("Start a new book? Today's entry, community name, roster, history, and footer will all be cleared. This cannot be undone.")) {
        resetEverything();
        notify("New book started");
      }
    });
  }

  function resetEverything() {
    // Clear in-memory state
    history = [];
    roster = [];
    ties = [];
    editingId = null;

    // Clear localStorage data keys (keep prefs — color mood is a UI preference, not book data)
    localStorage.removeItem(STORE_KEY);
    localStorage.removeItem(HISTORY_KEY);
    localStorage.removeItem(ROSTER_KEY);
    localStorage.removeItem(TIES_KEY);
    localStorage.removeItem(FOOTER_KEY);

    // Explicitly clear every form field
    [
      "communityName", "mapSelect", "baseSelect", "difficultySelect",
      "events", "deaths", "newSurvivors", "notes"
    ].forEach(id => { const el = $("#" + id); if (el) el.value = ""; });

    $("#dayNumber").value = "1";
    $("#plagueHearts").value = "0";
    $("#survivors").value = "0";
    $("#morale").value = "0";
    $("#moraleValue").value = "0";

    RESOURCES.forEach(r => {
      $("#" + r.id + "From").value = "";
      $("#" + r.id + "To").value = "";
      updateResourceDiff(r.id);
    });

    // Reset linked UI
    refreshBaseSelect();
    updateMorale();
    updateDiaryTitle();
    renderRoster();
    renderHistory();

    // Reset footer to a new random quote
    const foot = $("#diaryFoot");
    if (foot) {
      foot.value = pick(FOOTER_QUOTES);
      foot.style.width = "1px";
      foot.style.width = Math.min(foot.scrollWidth + 4, 600) + "px";
    }

    // New randomized placeholders
    randomizePlaceholders();
  }

  function exportJson() {
    const payload = {
      version: "v4",
      exportedAt: new Date().toISOString(),
      current: collectFormState(),
      roster: roster,
      ties: ties,
      history: history
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "diary-export-" + new Date().toISOString().slice(0, 10) + ".json";
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(a.href);
    notify("Exported");
  }
  function importJson(e) {
    const f = e.target.files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = function () {
      try {
        const data = JSON.parse(reader.result);
        if (data.current) applyFormState(data.current);
        if (Array.isArray(data.roster))  { roster  = data.roster;  renderRoster(); }
        if (Array.isArray(data.ties))    { ties    = data.ties; normalizeTies(); }
        if (Array.isArray(data.history)) { history = data.history; renderHistory(); }
        persist();
        notify("Imported");
      } catch (err) {
        alert("Could not parse that JSON file.");
      }
    };
    reader.readAsText(f);
    e.target.value = "";
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
    } else {
      fallbackCopy(text);
    }
  }
  function fallbackCopy(text) {
    const ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    ta.remove();
  }

  // ── Notifications ───────────────────────────────────────
  let notifTimer = null;
  function notify(msg) {
    const el = $("#notif");
    el.textContent = msg;
    el.classList.add("is-on");
    clearTimeout(notifTimer);
    notifTimer = setTimeout(() => el.classList.remove("is-on"), 1800);
  }

  // ── Tweaks panel ────────────────────────────────────────
  function loadPrefs() {
    try { return JSON.parse(localStorage.getItem(PREFS_KEY) || "{}"); }
    catch (e) { return {}; }
  }
  function savePrefs(p) {
    localStorage.setItem(PREFS_KEY, JSON.stringify(p));
  }
  function applyPrefs(p) {
    const mood = p.mood || "sepia";
    const pal = COLOR_MOODS[mood] || COLOR_MOODS.sepia;
    const root = document.documentElement.style;
    root.setProperty("--paper",       pal.paper);
    root.setProperty("--paper-warm",  pal.paperWarm);
    root.setProperty("--ink",         pal.ink);
    root.setProperty("--ink-soft",    pal.inkSoft);
    root.setProperty("--ink-blue",    pal.inkBlue);
    root.setProperty("--ink-red",     pal.inkRed);
    root.setProperty("--ink-pencil",  pal.inkPencil);
    root.setProperty("--amber",       pal.amber);

    $$(".swatch").forEach(s => s.classList.toggle("is-on", s.dataset.mood === mood));

    const grain = p.grain != null ? p.grain : 55;
    root.setProperty("--grain", String(grain / 100));
    $("#grainSlider").value = grain;
    $("#grainValue").textContent = grain;

    const hand = p.hand || "script";
    $$("#handSeg button").forEach(b => b.classList.toggle("is-on", b.dataset.hand === hand));
    const fontHandMap = {
      script: '"Patrick Hand", "Caveat", cursive',
      indie:  '"Caveat Brush", "Caveat", cursive',
      off:    '"IBM Plex Mono", ui-monospace, "SFMono-Regular", monospace'
    };
    root.setProperty("--font-hand", fontHandMap[hand] || fontHandMap.script);
  }
  function setupTweaks() {
    const panel = $("#tweaksPanel");
    const toggle = $("#tweaksToggle");
    const close = $("#tweaksClose");
    let prefs = loadPrefs();
    applyPrefs(prefs);

    const open = () => { panel.classList.add("is-on"); toggle.classList.add("is-hidden"); };
    const shut = () => { panel.classList.remove("is-on"); toggle.classList.remove("is-hidden"); };
    toggle.addEventListener("click", open);
    close.addEventListener("click", shut);

    $("#moodSwatches").addEventListener("click", e => {
      const b = e.target.closest("[data-mood]");
      if (!b) return;
      prefs.mood = b.dataset.mood;
      applyPrefs(prefs); savePrefs(prefs);
    });
    $("#grainSlider").addEventListener("input", e => {
      prefs.grain = parseInt(e.target.value, 10);
      applyPrefs(prefs); savePrefs(prefs);
    });
    $("#handSeg").addEventListener("click", e => {
      const b = e.target.closest("[data-hand]");
      if (!b) return;
      prefs.hand = b.dataset.hand;
      applyPrefs(prefs); savePrefs(prefs);
    });
  }

  // ── Dock active state on scroll ─────────────────────────
  function setupDockHighlight() {
    const links = $$(".dock a");
    const targets = links.map(a => $(a.getAttribute("href")));
    function update() {
      const y = window.scrollY + 120;
      let active = 0;
      targets.forEach((el, i) => { if (el && el.offsetTop <= y) active = i; });
      links.forEach((a, i) => a.classList.toggle("is-active", i === active));
    }
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  // ── Rollover: when generating, advance day +1 and shift "to" → "from" ──
  function rollover() {
    const day = parseInt($("#dayNumber").value, 10) || 1;
    $("#dayNumber").value = day + 1;
    RESOURCES.forEach(r => {
      const to = $("#" + r.id + "To").value;
      if (to !== "") {
        $("#" + r.id + "From").value = to;
        $("#" + r.id + "To").value = "";
        updateResourceDiff(r.id);
      }
    });
    // Clear single-day fields
    ["events", "deaths", "newSurvivors", "notes"].forEach(id => {
      $("#" + id).value = "";
    });
    persist();
  }

  // ── Footer tagline (random SoD2-flavored, persists once edited) ──
  const FOOTER_KEY = "sod2-diary-v4-foot";
  const FOOTER_QUOTES = [
    "shared today, stronger tomorrow",
    "every survivor matters",
    "weathered, not broken",
    "we hold the line",
    "carry each other home",
    "the dead don't bury themselves",
    "morale is a resource too",
    "what we lose, we remember",
    "one more day, one less heart",
    "watch the perimeter",
    "the road provides",
    "rebuild, repair, repeat",
    "trust the people, not the plan",
    "scavenge, scout, survive",
    "the night ends. so do we.",
    "leave nothing for the dead",
    "fortify before nightfall",
    "we are the cure",
    "no one walks alone",
    "loud is dead",
    "the radio still works",
    "burn what you can't carry",
    "ammo over food, food over comfort",
    "today's run is tomorrow's story"
  ];
  function setupFooter() {
    const el = $("#diaryFoot");
    if (!el) return;
    const saved = localStorage.getItem(FOOTER_KEY);
    if (saved) {
      el.value = saved;
    } else {
      el.value = pick(FOOTER_QUOTES);
    }
    // Auto-size input to content
    const sizeToContent = () => {
      el.style.width = "1px";
      el.style.width = Math.min(el.scrollWidth + 4, 600) + "px";
    };
    sizeToContent();
    el.addEventListener("input", () => {
      sizeToContent();
      localStorage.setItem(FOOTER_KEY, el.value);
    });
    // Re-randomize unless user has set their own
    if (!saved) {
      // Don't persist the default; only persist when user types
      el.addEventListener("focus", () => {
        if (!localStorage.getItem(FOOTER_KEY)) el.select();
      });
    }
  }

  // ── LZString (inlined, single-edge sync compression) ────
  /* eslint-disable */
  const LZString=(function(){var _=String.fromCharCode,M="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",S="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$",x={};function O(o,r){if(!x[o]){x[o]={};for(var c=0;c<o.length;c++)x[o][o.charAt(c)]=c}return x[o][r]}var h={compressToBase64:function(o){if(o==null)return"";var r=h._compress(o,6,function(c){return M.charAt(c)});switch(r.length%4){default:case 0:return r;case 1:return r+"===";case 2:return r+"==";case 3:return r+"="}},decompressFromBase64:function(o){return o==null?"":o==""?null:h._decompress(o.length,32,function(r){return O(M,o.charAt(r))})},compressToEncodedURIComponent:function(o){return o==null?"":h._compress(o,6,function(r){return S.charAt(r)})},decompressFromEncodedURIComponent:function(o){return o==null?"":o==""?null:(o=o.replace(/ /g,"+"),h._decompress(o.length,32,function(r){return O(S,o.charAt(r))}))},compress:function(o){return h._compress(o,16,function(r){return _(r)})},_compress:function(o,r,c){if(o==null)return"";var i,f,a={},w={},v="",y="",u="",p=2,A=3,s=2,l=[],n=0,e=0,d;for(d=0;d<o.length;d+=1)if(v=o.charAt(d),Object.prototype.hasOwnProperty.call(a,v)||(a[v]=A++,w[v]=!0),y=u+v,Object.prototype.hasOwnProperty.call(a,y))u=y;else{if(Object.prototype.hasOwnProperty.call(w,u)){if(u.charCodeAt(0)<256){for(i=0;i<s;i++)n=n<<1,e==r-1?(e=0,l.push(c(n)),n=0):e++;for(f=u.charCodeAt(0),i=0;i<8;i++)n=n<<1|f&1,e==r-1?(e=0,l.push(c(n)),n=0):e++,f=f>>1}else{for(f=1,i=0;i<s;i++)n=n<<1|f,e==r-1?(e=0,l.push(c(n)),n=0):e++,f=0;for(f=u.charCodeAt(0),i=0;i<16;i++)n=n<<1|f&1,e==r-1?(e=0,l.push(c(n)),n=0):e++,f=f>>1}p--,p==0&&(p=Math.pow(2,s),s++),delete w[u]}else for(f=a[u],i=0;i<s;i++)n=n<<1|f&1,e==r-1?(e=0,l.push(c(n)),n=0):e++,f=f>>1;p--,p==0&&(p=Math.pow(2,s),s++),a[y]=A++,u=String(v)}if(u!==""){if(Object.prototype.hasOwnProperty.call(w,u)){if(u.charCodeAt(0)<256){for(i=0;i<s;i++)n=n<<1,e==r-1?(e=0,l.push(c(n)),n=0):e++;for(f=u.charCodeAt(0),i=0;i<8;i++)n=n<<1|f&1,e==r-1?(e=0,l.push(c(n)),n=0):e++,f=f>>1}else{for(f=1,i=0;i<s;i++)n=n<<1|f,e==r-1?(e=0,l.push(c(n)),n=0):e++,f=0;for(f=u.charCodeAt(0),i=0;i<16;i++)n=n<<1|f&1,e==r-1?(e=0,l.push(c(n)),n=0):e++,f=f>>1}p--,p==0&&(p=Math.pow(2,s),s++),delete w[u]}else for(f=a[u],i=0;i<s;i++)n=n<<1|f&1,e==r-1?(e=0,l.push(c(n)),n=0):e++,f=f>>1;p--,p==0&&(p=Math.pow(2,s),s++)}for(f=2,i=0;i<s;i++)n=n<<1|f&1,e==r-1?(e=0,l.push(c(n)),n=0):e++,f=f>>1;for(;;)if(n=n<<1,e==r-1){l.push(c(n));break}else e++;return l.join("")},decompress:function(o){return o==null?"":o==""?null:h._decompress(o.length,32768,function(r){return o.charCodeAt(r)})},_decompress:function(o,r,c){var i=[],f,a=4,w=4,v=3,y="",u=[],p,A,s,l,n,e,d,t={val:c(0),position:r,index:1};for(p=0;p<3;p+=1)i[p]=p;for(s=0,n=Math.pow(2,2),e=1;e!=n;)l=t.val&t.position,t.position>>=1,t.position==0&&(t.position=r,t.val=c(t.index++)),s|=(l>0?1:0)*e,e<<=1;switch(f=s){case 0:for(s=0,n=Math.pow(2,8),e=1;e!=n;)l=t.val&t.position,t.position>>=1,t.position==0&&(t.position=r,t.val=c(t.index++)),s|=(l>0?1:0)*e,e<<=1;d=_(s);break;case 1:for(s=0,n=Math.pow(2,16),e=1;e!=n;)l=t.val&t.position,t.position>>=1,t.position==0&&(t.position=r,t.val=c(t.index++)),s|=(l>0?1:0)*e,e<<=1;d=_(s);break;case 2:return""}for(i[3]=d,A=d,u.push(d);;){if(t.index>o)return"";for(s=0,n=Math.pow(2,v),e=1;e!=n;)l=t.val&t.position,t.position>>=1,t.position==0&&(t.position=r,t.val=c(t.index++)),s|=(l>0?1:0)*e,e<<=1;switch(d=s){case 0:for(s=0,n=Math.pow(2,8),e=1;e!=n;)l=t.val&t.position,t.position>>=1,t.position==0&&(t.position=r,t.val=c(t.index++)),s|=(l>0?1:0)*e,e<<=1;i[w++]=_(s),d=w-1,a--;break;case 1:for(s=0,n=Math.pow(2,16),e=1;e!=n;)l=t.val&t.position,t.position>>=1,t.position==0&&(t.position=r,t.val=c(t.index++)),s|=(l>0?1:0)*e,e<<=1;i[w++]=_(s),d=w-1,a--;break;case 2:return u.join("")}if(a==0&&(a=Math.pow(2,v),v++),i[d])y=i[d];else if(d===w)y=A+A.charAt(0);else return null;u.push(y),i[w++]=A+y.charAt(0),a--,A=y,a==0&&(a=Math.pow(2,v),v++)}}};return h})();
  /* eslint-enable */

  // ── Radio Sync ──────────────────────────────────────────
  function hashStr(s) {
    let h = 5381;
    for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0;
    return h.toString(36);
  }

  function buildSyncPayload() {
    return { v: 4, state: collectFormState(), roster: roster, ties: ties };
  }

  function encodeSync(payload) {
    try {
      const json = JSON.stringify(payload);
      const compressed = LZString.compressToEncodedURIComponent(json);
      const checksum = hashStr(json);
      return compressed + "." + checksum;
    } catch (e) { return null; }
  }

  function decodeSync(encoded) {
    try {
      const dot = encoded.lastIndexOf(".");
      const body = dot > 0 ? encoded.slice(0, dot) : encoded;
      const checksum = dot > 0 ? encoded.slice(dot + 1) : "";
      const json = LZString.decompressFromEncodedURIComponent(body);
      if (!json) return null;
      const payload = JSON.parse(json);
      const integrity = checksum ? (hashStr(json) === checksum ? "ok" : "mismatch") : "none";
      return { payload, integrity };
    } catch (e) { return null; }
  }

  function setupSync() {
    const block = $("#syncBlock");
    if (!block) return;

    block.addEventListener("toggle", function () {
      if (!block.open) return;
      refreshSyncLink();
    });

    const copyBtn = $("#syncCopyBtn");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        const link = $("#syncLinkOutput").value;
        if (!link) return;
        copyText(link);
        const meta = $("#syncMeta");
        if (meta) meta.textContent = "Link copied!";
        notify("Sync link copied");
        setTimeout(() => { if (meta) meta.textContent = ""; }, 2000);
      });
    }
  }

  function refreshSyncLink() {
    const input = $("#syncLinkOutput");
    const meta = $("#syncMeta");
    if (!input) return;
    const payload = buildSyncPayload();
    const encoded = encodeSync(payload);
    if (!encoded) { if (meta) meta.textContent = "Could not encode state."; return; }
    const bytes = new TextEncoder().encode(encoded).length;
    const link = window.location.href.split("#")[0] + "#sync=" + encoded;
    input.value = link;
    if (meta) {
      if (bytes > SHARE_BUDGET) {
        meta.textContent = "Warning: payload is " + bytes + " B (budget " + SHARE_BUDGET + " B). Link may be very long.";
      } else {
        meta.textContent = bytes + " B — ready to share";
      }
    }
  }

  function checkSyncHash() {
    const hash = window.location.hash;
    if (!hash || !hash.startsWith("#sync=")) return;
    const encoded = hash.slice(6);
    const result = decodeSync(encoded);
    const banner = $("#syncBanner");
    if (!banner) return;
    if (!result) {
      banner.hidden = false;
      const msg = $("#syncBannerMsg");
      if (msg) msg.textContent = "Sync link appears corrupt — cannot import.";
      const yesBtn = $("#syncBannerYes");
      if (yesBtn) yesBtn.hidden = true;
      const noBtn = $("#syncBannerNo");
      if (noBtn) noBtn.focus();
      setupBannerDismiss();
      return;
    }
    if (result.integrity === "mismatch") {
      banner.hidden = false;
      const msg = $("#syncBannerMsg");
      if (msg) msg.textContent = "Sync link checksum mismatch — import anyway?";
    } else {
      banner.hidden = false;
    }
    const yesBtn = $("#syncBannerYes");
    if (yesBtn) {
      yesBtn.focus();
      yesBtn.addEventListener("click", function () {
        const p = result.payload;
        if (p.state) applyFormState(p.state);
        if (Array.isArray(p.roster)) { roster = p.roster; }
        if (Array.isArray(p.ties))   { ties   = p.ties; normalizeTies(); }
        renderRoster();
        persist();
        notify("Diary synced");
        banner.hidden = true;
        window.history.replaceState(null, "", window.location.pathname + window.location.search);
      }, { once: true });
    }
    setupBannerDismiss();
  }

  function setupBannerDismiss() {
    const noBtn = $("#syncBannerNo");
    if (noBtn) {
      noBtn.addEventListener("click", function () {
        const banner = $("#syncBanner");
        if (banner) banner.hidden = true;
        window.history.replaceState(null, "", window.location.pathname + window.location.search);
      }, { once: true });
    }
  }

  // ── Boot ────────────────────────────────────────────────
  function boot() {
    buildResources();
    setupSteppers();
    setupRosterEvents();
    setupHistoryEvents();
    setupTweaks();

    loadAll();
    renderRoster();
    renderHistory();
    refreshBaseSelect();
    updateMorale();
    randomizePlaceholders();

    // Input listeners → autosave
    $$("#diary input, #diary select, #diary textarea").forEach(el => {
      el.addEventListener("input", scheduleSave);
      el.addEventListener("change", scheduleSave);
    });
    $("#morale").addEventListener("input", updateMorale);

    // Sync community name → header title
    $("#communityName").addEventListener("input", updateDiaryTitle);
    updateDiaryTitle();

    // Re-draw tie overlay on resize (debounced) — re-positions/clears lines.
    let tieResizeRaf = 0;
    window.addEventListener("resize", function () {
      if (tieResizeRaf) cancelAnimationFrame(tieResizeRaf);
      tieResizeRaf = requestAnimationFrame(renderTieOverlays);
    }, { passive: true });
    // Redraw once the page (fonts/layout) has fully settled — the boot-time
    // rAF can fire before the grid has measurable card rects.
    window.addEventListener("load", renderTieOverlays);

    // Allow typing directly into morale value
    $("#moraleValue").addEventListener("input", () => {
      const v = Math.max(-100, Math.min(100, parseInt($("#moraleValue").value, 10) || 0));
      $("#morale").value = v;
      updateMorale();
      scheduleSave();
    });
    $("#moraleValue").addEventListener("blur", () => {
      const v = Math.max(-100, Math.min(100, parseInt($("#moraleValue").value, 10) || 0));
      $("#morale").value = v;
      $("#moraleValue").value = v;
      updateMorale();
    });
    $("#mapSelect").addEventListener("change", () => { refreshBaseSelect(); scheduleSave(); });

    // Generate button
    $("#generateBtn").addEventListener("click", () => {
      const text = generateReport();
      const out = $("#reportOutput");
      out.textContent = text;
      out.hidden = false;
      $("#reportEmpty").style.display = "none";
      copyText(text);
      saveToHistory(text);
      rollover();
      notify("Stamped & copied");
      // Smooth-scroll report card into view without using scrollIntoView
      const top = $("#reportCard").getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top, behavior: "smooth" });
    });
    $("#copyReportBtn").addEventListener("click", () => {
      const text = $("#reportOutput").textContent;
      if (!text) { notify("No report yet"); return; }
      copyText(text); notify("Copied");
    });

    setupDockHighlight();
    setupFooter();
    setupSync();
    checkSyncHash();
  }

  function randomizePlaceholders() {
    const cName = $("#communityName");
    const evt = $("#events");
    const dth = $("#deaths");
    const newS = $("#newSurvivors");
    const nts = $("#notes");
    const rName = $('input[name="name"]');
    const rBio = $('input[name="bio"]');
    const rTraits = $('input[name="traits"]');
    const rSkills = $('input[name="skills"]');

    if (cName) cName.placeholder = pick(SAMPLES.communityNames) + "…";
    if (evt) evt.placeholder = pick(SAMPLES.events);
    if (dth) dth.placeholder = pick(SAMPLES.deaths);
    if (newS) newS.placeholder = pick(SAMPLES.newSurvivors);
    if (nts) nts.placeholder = pick(SAMPLES.notes);
    if (rName) rName.placeholder = pick(SAMPLES.survivorNames);
    if (rBio) rBio.placeholder = pick(SAMPLES.bios);
    if (rTraits) rTraits.placeholder = pick(SAMPLES.traits);
    if (rSkills) rSkills.placeholder = pick(SAMPLES.skills);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
