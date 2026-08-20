const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const state = { user: null, quota: null, workspaces: [], currentId: null, workspaceData: null, currentGeneration: null, kimiConfigured: false, model: "moonshotai/kimi-k2.5", editingEvidenceId: null, editingWorkspace: false, thinkingTimer: null };

document.addEventListener("DOMContentLoaded", boot);

async function boot() {
  bindEvents();
  try {
    const data = await api("/api/auth/me");
    Object.assign(state, { user: data.user, quota: data.quota, kimiConfigured: data.kimiConfigured, model: data.model });
    await enterApp();
  } catch { showAuth(); }
}

function bindEvents() {
  $$("[data-auth-tab]").forEach((button) => button.addEventListener("click", () => showAuthForm(button.dataset.authTab)));
  $("[data-show-recover]").addEventListener("click", () => showAuthForm("recover"));
  $("[data-back-login]").addEventListener("click", () => showAuthForm("login"));
  $("#login-form").addEventListener("submit", login);
  $("#register-form").addEventListener("submit", register);
  $("#recover-form").addEventListener("submit", recover);
  $("#logout-button").addEventListener("click", logout);
  $("#menu-button").addEventListener("click", () => toggleSidebar(true));
  $("#side-close").addEventListener("click", () => toggleSidebar(false));
  $("#side-scrim").addEventListener("click", () => toggleSidebar(false));
  $("#new-workspace-button").addEventListener("click", openWorkspaceDialog);
  $$("[data-create-workspace]").forEach((button) => button.addEventListener("click", openWorkspaceDialog));
  $$("[data-close-workspace]").forEach((button) => button.addEventListener("click", () => $("#workspace-dialog").close()));
  $("#workspace-form").addEventListener("submit", saveWorkspace);
  $("#add-evidence-button").addEventListener("click", () => openEvidenceDialog());
  $$("[data-close-evidence]").forEach((button) => button.addEventListener("click", () => $("#evidence-dialog").close()));
  $("#evidence-form").addEventListener("submit", saveEvidence);
  $("#generate-form").addEventListener("submit", generate);
  $("#generate-form textarea").addEventListener("input", (event) => $("#question-count").textContent = event.target.value.length);
  $("#workspace-menu").addEventListener("click", () => $("#workspace-actions-dialog").showModal());
  $$("[data-close-actions]").forEach((button) => button.addEventListener("click", () => $("#workspace-actions-dialog").close()));
  $("#edit-workspace-button").addEventListener("click", editWorkspace);
  $("#delete-workspace-button").addEventListener("click", deleteWorkspace);
  $$("[data-show-settings]").forEach((button) => button.addEventListener("click", showSettings));
  $$("[data-back-workspace]").forEach((button) => button.addEventListener("click", () => state.currentId ? openWorkspace(state.currentId) : showHome()));
  $("#delete-account-form").addEventListener("submit", deleteAccount);
  $("#saved-recovery").addEventListener("change", (event) => $("#finish-recovery").disabled = !event.target.checked);
  $("#copy-recovery").addEventListener("click", () => copyText($("#recovery-code").textContent, "Recovery code copied"));
  $("#finish-recovery").addEventListener("click", async () => { $("#recovery-dialog").close(); await enterApp(); });
}

async function login(event) {
  event.preventDefault(); clearError("#auth-error"); const button = event.submitter; setBusy(button, true, "Signing in…");
  try { const data = await api("/api/auth/login", { method: "POST", body: formObject(event.currentTarget) }); Object.assign(state, { user: data.user, quota: data.quota, kimiConfigured: data.kimiConfigured, model: data.model }); event.currentTarget.reset(); await enterApp(); }
  catch (error) { showError("#auth-error", error.message); } finally { setBusy(button, false); }
}

async function register(event) {
  event.preventDefault(); clearError("#auth-error"); const button = event.submitter; setBusy(button, true, "Creating workspace…");
  try {
    const data = await api("/api/auth/register", { method: "POST", body: formObject(event.currentTarget) });
    Object.assign(state, { user: data.user, quota: data.quota, kimiConfigured: data.kimiConfigured, model: data.model });
    showRecoveryCode(data.recoveryCode); event.currentTarget.reset();
  } catch (error) { showError("#auth-error", error.message); } finally { setBusy(button, false); }
}

async function recover(event) {
  event.preventDefault(); clearError("#auth-error"); const button = event.submitter; setBusy(button, true, "Checking code…");
  try { const data = await api("/api/auth/recover", { method: "POST", body: formObject(event.currentTarget) }); showRecoveryCode(data.recoveryCode); event.currentTarget.reset(); }
  catch (error) { showError("#auth-error", error.message); } finally { setBusy(button, false); }
}

function showRecoveryCode(code) { $("#recovery-code").textContent = code; $("#saved-recovery").checked = false; $("#finish-recovery").disabled = true; $("#recovery-dialog").showModal(); }

async function enterApp() {
  $("#auth-view").hidden = true; $("#app-view").hidden = false;
  $("#profile-name").textContent = state.user.username; $("#avatar").textContent = state.user.username.charAt(0).toUpperCase();
  updateQuota(state.quota); await loadWorkspaces();
  if (state.workspaces.length) await openWorkspace(state.workspaces[0].id); else showHome();
}

function showAuth() { $("#app-view").hidden = true; $("#auth-view").hidden = false; showAuthForm("login"); }
function showAuthForm(name) {
  $$(".auth-form").forEach((form) => form.hidden = true); const target = $(`#${name}-form`); if (target) target.hidden = false;
  $$(".auth-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.authTab === name));
  $(".auth-tabs").hidden = name === "recover"; clearError("#auth-error");
}
async function logout() { try { await api("/api/auth/logout", { method: "POST", body: {} }); } catch {} Object.assign(state, { user: null, workspaces: [], currentId: null, workspaceData: null }); showAuth(); }

async function loadWorkspaces() {
  try { const data = await api("/api/workspaces"); state.workspaces = data.workspaces; updateQuota(data.quota); renderWorkspaceList(); }
  catch (error) { toast(error.message, "error"); }
}

function renderWorkspaceList() {
  $("#workspace-count").textContent = state.workspaces.length;
  $("#workspace-list").innerHTML = state.workspaces.map((workspace) => `<button class="workspace-nav ${workspace.id === state.currentId ? "active" : ""}" data-workspace-id="${workspace.id}"><span class="workspace-icon">${escapeHtml(workspace.name.charAt(0).toUpperCase())}</span><span><strong>${escapeHtml(workspace.name)}</strong><small>${workspace.evidence_count} proofs · ${workspace.generation_count} answers</small></span><span>›</span></button>`).join("");
  $$("[data-workspace-id]").forEach((button) => button.addEventListener("click", () => openWorkspace(Number(button.dataset.workspaceId))));
}

function openWorkspaceDialog() {
  state.editingWorkspace = false; const form = $("#workspace-form"); form.reset(); clearError("#workspace-error");
  $("#workspace-dialog h2").textContent = "What are you applying for?"; $("#workspace-dialog form button[type='submit']").innerHTML = "Create application <span>→</span>"; $("#workspace-dialog").showModal();
}

async function saveWorkspace(event) {
  event.preventDefault(); clearError("#workspace-error"); const button = event.submitter; setBusy(button, true, state.editingWorkspace ? "Saving…" : "Creating…");
  try {
    const data = await api(state.editingWorkspace ? `/api/workspaces/${state.currentId}` : "/api/workspaces", { method: state.editingWorkspace ? "PATCH" : "POST", body: formObject(event.currentTarget) });
    $("#workspace-dialog").close(); await loadWorkspaces(); await openWorkspace(data.workspace.id); toast(state.editingWorkspace ? "Application updated" : "Application created");
  } catch (error) { showError("#workspace-error", error.message); } finally { setBusy(button, false); }
}

async function openWorkspace(id) {
  try {
    const data = await api(`/api/workspaces/${id}`); state.currentId = id; state.workspaceData = data; state.kimiConfigured = data.kimiConfigured; state.model = data.model; updateQuota(data.quota);
    $("#workspace-name").textContent = data.workspace.name; $("#workspace-target").textContent = data.workspace.target.toUpperCase();
    $("#workspace-description").textContent = data.workspace.description || "Evidence-backed answers for this application.";
    updateKimiStatus(); renderEvidence(); renderGenerations(); renderWorkspaceList(); showView("workspace"); toggleSidebar(false);
  } catch (error) { toast(error.message, "error"); }
}

function updateKimiStatus() {
  const el = $("#kimi-status"); el.classList.toggle("connected", state.kimiConfigured); el.classList.toggle("disconnected", !state.kimiConfigured);
  el.lastChild.textContent = state.kimiConfigured ? " Kimi K2.5 connected" : " Kimi connection pending";
}

function renderEvidence() {
  const items = state.workspaceData.evidence; $("#evidence-ready-count").textContent = `${items.length} proof${items.length === 1 ? "" : "s"} ready`;
  if (!items.length) { $("#evidence-list").innerHTML = `<div class="empty-vault"><span>⌁</span><h3>No work added yet</h3><p>Start with your strongest project, contribution, article, event, or measurable result.</p><button class="button secondary" data-empty-add>＋ Add first item</button></div>`; $("[data-empty-add]").addEventListener("click", () => openEvidenceDialog()); return; }
  $("#evidence-list").innerHTML = items.map((item) => {
    const read = ["public_text_read", "public_api_read"].includes(item.source_status); const label = read ? "Link checked" : item.proof_url ? "Link saved" : "Your notes only";
    return `<article class="evidence-card"><div class="evidence-top"><span class="type-badge">${escapeHtml(typeLabel(item.type))}</span><span class="source-state ${read ? "read" : ""}">${label}</span></div><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.details)}</p>${item.metric ? `<span class="metric">${escapeHtml(item.metric)}</span>` : ""}<div class="evidence-footer">${item.proof_url ? `<a href="${escapeHtml(item.proof_url)}" target="_blank" rel="noopener">Open proof ↗</a>` : `<span></span>`}<div class="card-actions"><button class="mini-action" data-edit-evidence="${item.id}">Edit</button><button class="mini-action danger-text" data-delete-evidence="${item.id}">Delete</button></div></div></article>`;
  }).join("");
  $$('[data-edit-evidence]').forEach((button) => button.addEventListener("click", () => openEvidenceDialog(Number(button.dataset.editEvidence))));
  $$('[data-delete-evidence]').forEach((button) => button.addEventListener("click", () => removeEvidence(Number(button.dataset.deleteEvidence))));
}

function openEvidenceDialog(id = null) {
  state.editingEvidenceId = id; const form = $("#evidence-form"); form.reset(); clearError("#evidence-error");
  if (id) { const item = state.workspaceData.evidence.find((entry) => entry.id === id); if (!item) return; Object.entries({ type: item.type, title: item.title, details: item.details, metric: item.metric, proofUrl: item.proof_url }).forEach(([name, value]) => { if (form.elements[name]) form.elements[name].value = value || ""; }); }
  $("#evidence-dialog h2").textContent = id ? "Update this item." : "Add something you have actually done.";
  $("#evidence-dialog form button[type='submit']").innerHTML = id ? "Save changes <span>→</span>" : "Add this work <span>＋</span>"; $("#evidence-dialog").showModal();
}

async function saveEvidence(event) {
  event.preventDefault(); clearError("#evidence-error"); const button = event.submitter; setBusy(button, true, "Reading proof…");
  try {
    const path = state.editingEvidenceId ? `/api/evidence/${state.editingEvidenceId}` : `/api/workspaces/${state.currentId}/evidence`;
    await api(path, { method: state.editingEvidenceId ? "PATCH" : "POST", body: formObject(event.currentTarget) });
    $("#evidence-dialog").close(); await openWorkspace(state.currentId); toast(state.editingEvidenceId ? "Evidence updated" : "Evidence added");
  } catch (error) { showError("#evidence-error", error.message); } finally { setBusy(button, false); }
}

async function removeEvidence(id) {
  const item = state.workspaceData.evidence.find((entry) => entry.id === id); if (!item || !confirm(`Delete “${item.title}” from this application?`)) return;
  try { await api(`/api/evidence/${id}`, { method: "DELETE", body: {} }); await openWorkspace(state.currentId); toast("Evidence deleted"); } catch (error) { toast(error.message, "error"); }
}

async function generate(event) {
  event.preventDefault(); clearError("#generate-error");
  if (!state.kimiConfigured) return showError("#generate-error", "Kimi is temporarily unavailable. Please try again later.");
  if (state.workspaceData.evidence.length < 2) return showError("#generate-error", "Add at least two evidence items first.");
  if (state.quota.remaining <= 0) return showError("#generate-error", "You have used today’s 10 Kimi answers.");
  const button = event.submitter; setBusy(button, true, "Kimi is reading…"); showThinking();
  try {
    const data = await api(`/api/workspaces/${state.currentId}/generate`, { method: "POST", body: formObject(event.currentTarget) });
    clearInterval(state.thinkingTimer); state.currentGeneration = data.generation; updateQuota(data.quota); renderAnswer(data.generation); await openWorkspace(state.currentId); state.currentGeneration = data.generation; renderAnswer(data.generation);
  } catch (error) { clearInterval(state.thinkingTimer); $("#answer-loading").hidden = true; $("#answer-empty").hidden = false; showError("#generate-error", error.message); } finally { setBusy(button, false); }
}

function showThinking() {
  $("#answer-empty").hidden = true; $("#answer-result").hidden = true; $("#answer-loading").hidden = false;
  const messages = [["Separating facts from claims…", "Checking what can be said confidently and what still needs proof."], ["Mapping proof to the question…", "Finding the strongest evidence for this exact application."], ["Writing in your requested tone…", "Keeping the language simple, human, and specific."], ["Running the honesty check…", "Looking for unsupported metrics, roles, dates, and outcomes."]]; let index = 0;
  const update = () => { $("#thinking-title").textContent = messages[index][0]; $("#thinking-detail").textContent = messages[index][1]; }; update(); state.thinkingTimer = setInterval(() => { index = Math.min(index + 1, messages.length - 1); update(); }, 1800);
}

function renderAnswer(generation) {
  $("#answer-loading").hidden = true; $("#answer-empty").hidden = true; $("#answer-result").hidden = false;
  const facts = generation.factsUsed.length ? generation.factsUsed : ["Kimi did not list specific evidence references."];
  const warnings = generation.warnings.length ? generation.warnings : ["No major unsupported claims were detected."];
  $("#answer-result").innerHTML = `<div class="answer-result-head"><div><span class="section-index">✦</span><h3>Answer based on your work</h3></div><div class="confidence"><span>${generation.confidence}% confidence</span><span class="confidence-track"><i style="width:${generation.confidence}%"></i></span></div></div><div class="answer-copy">${escapeHtml(generation.answer)}</div><div class="answer-toolbar"><small>Written with Kimi K2.5 · Check it before submitting</small><button class="button secondary" data-copy-answer>Copy answer</button></div><div class="answer-insights"><section class="insight-panel"><h4>FACTS USED</h4><div class="insight-list">${facts.map((item) => `<div class="insight-item"><span>✓</span><div>${escapeHtml(item)}</div></div>`).join("")}</div></section><section class="insight-panel"><h4>CHECK BEFORE SUBMITTING</h4><div class="insight-list">${warnings.map((item) => `<div class="insight-item warning"><span>!</span><div>${escapeHtml(item)}</div></div>`).join("")}</div></section></div><section class="next-proof"><h4>WHAT WOULD MAKE THIS STRONGER</h4>${generation.nextProof.length ? `<ol>${generation.nextProof.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>` : `<p>No additional proof was requested.</p>`}</section>`;
  $("[data-copy-answer]").addEventListener("click", () => copyText(generation.answer, "Answer copied"));
}

function renderGenerations() {
  const items = state.workspaceData.generations;
  if (!items.length) { $("#generation-list").innerHTML = `<div class="empty-history">No answers yet. Your first Kimi generation will be saved here.</div>`; return; }
  $("#generation-list").innerHTML = items.map((item) => `<article class="generation-card" data-generation-id="${item.id}" tabindex="0"><div><strong>${escapeHtml(item.question)}</strong><small>${formatDate(item.created_at)} · ${item.confidence}% confidence · ${escapeHtml(item.tone)}</small></div><span>→</span></article>`).join("");
  $$('[data-generation-id]').forEach((card) => { const open = () => openGeneration(Number(card.dataset.generationId)); card.addEventListener("click", open); card.addEventListener("keydown", (event) => event.key === "Enter" && open()); });
}

async function openGeneration(id) { try { const data = await api(`/api/generations/${id}`); state.currentGeneration = data.generation; renderAnswer(data.generation); $("#answer-result").scrollIntoView({ behavior: "smooth", block: "start" }); } catch (error) { toast(error.message, "error"); } }

function editWorkspace() {
  $("#workspace-actions-dialog").close(); state.editingWorkspace = true; const form = $("#workspace-form"); const w = state.workspaceData.workspace;
  form.elements.name.value = w.name; form.elements.target.value = w.target; form.elements.description.value = w.description || "";
  $("#workspace-dialog h2").textContent = "Update application details."; $("#workspace-dialog form button[type='submit']").innerHTML = "Save changes <span>→</span>"; clearError("#workspace-error"); $("#workspace-dialog").showModal();
}

async function deleteWorkspace() {
  $("#workspace-actions-dialog").close(); const name = state.workspaceData.workspace.name;
  if (!confirm(`Delete “${name}”, all its evidence, and every generated answer?`)) return;
  try { await api(`/api/workspaces/${state.currentId}`, { method: "DELETE", body: {} }); state.currentId = null; state.workspaceData = null; await loadWorkspaces(); if (state.workspaces.length) await openWorkspace(state.workspaces[0].id); else showHome(); toast("Application deleted"); } catch (error) { toast(error.message, "error"); }
}

function showSettings() { showView("settings"); toggleSidebar(false); }
function showHome() { state.currentId = null; renderWorkspaceList(); showView("home"); }
function showView(name) { $$(".page-view").forEach((view) => view.hidden = true); $(`#${name}-view`).hidden = false; window.scrollTo({ top: 0, behavior: "smooth" }); }

async function deleteAccount(event) {
  event.preventDefault(); clearError("#delete-account-error"); if (!confirm("Permanently delete your account, every evidence item, and every Kimi answer?")) return;
  const button = event.submitter; setBusy(button, true, "Deleting…");
  try { await api("/api/account", { method: "DELETE", body: formObject(event.currentTarget) }); event.currentTarget.reset(); showAuth(); toast("Account and all stored work deleted"); }
  catch (error) { showError("#delete-account-error", error.message); } finally { setBusy(button, false); }
}

function updateQuota(quota) { if (!quota) return; state.quota = quota; $("#quota-remaining").textContent = quota.remaining; $("#mobile-quota").textContent = `${quota.remaining} left`; $("#quota-bar").style.width = `${(quota.remaining / quota.limit) * 100}%`; }
function toggleSidebar(open) { $("#sidebar").classList.toggle("open", open); $("#side-scrim").classList.toggle("show", open); }
function typeLabel(type) { return ({ project: "Project", open_source: "Open source", article: "Article", event: "Event", work: "Work", education: "Education", other: "Other" })[type] || "Other"; }
function formObject(form) { return Object.fromEntries(new FormData(form).entries()); }
function showError(selector, message) { const el = $(selector); el.textContent = message; el.hidden = false; el.scrollIntoView({ behavior: "smooth", block: "nearest" }); }
function clearError(selector) { const el = $(selector); el.hidden = true; el.textContent = ""; }
function setBusy(button, busy, label = "Working…") { if (!button) return; if (busy) { button.dataset.original = button.innerHTML; button.textContent = label; button.disabled = true; } else { button.innerHTML = button.dataset.original || button.innerHTML; button.disabled = false; } }
async function copyText(value, message) { try { await navigator.clipboard.writeText(value); toast(message); } catch { toast("Copy failed. Select the text manually.", "error"); } }
function toast(message, type = "") { const el = document.createElement("div"); el.className = `toast ${type}`; el.textContent = message; $("#toast-region").append(el); setTimeout(() => el.remove(), 3500); }
function formatDate(value) { const normalized = typeof value === "string" && !value.endsWith("Z") ? `${value}Z` : value; const date = new Date(normalized); return Number.isNaN(date.getTime()) ? "Unknown" : new Intl.DateTimeFormat("en", { day: "numeric", month: "short", year: "numeric" }).format(date); }
function escapeHtml(value) { return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]); }

async function api(path, options = {}) {
  const response = await fetch(path, { method: options.method || "GET", credentials: "same-origin", headers: options.body ? { "Content-Type": "application/json" } : {}, body: options.body ? JSON.stringify(options.body) : undefined });
  let data = {}; try { data = await response.json(); } catch {}
  if (!response.ok) throw new Error(data.error || "The request could not be completed.");
  return data;
}
