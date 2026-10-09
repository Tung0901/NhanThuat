(function () {
    'use strict';

    const STORAGE_KEY = 'nhan_thuat_active_scenario_v1';
    const WORKSPACES = [
        ['advisory', 'view-advisory', 'Tham mưu'],
        ['diagnostics', 'view-diagnostics', 'Chẩn đoán'],
        ['council', 'view-council', 'Hội đồng'],
        ['sparring', 'view-sparring', 'Đấu trí'],
        ['warRoom', 'view-war-room', 'Sa bàn'],
        ['references', 'view-codex', 'Căn cứ'],
    ];

    let state = loadState();

    function now() {
        return new Date().toISOString();
    }

    function createId() {
        if (window.crypto && typeof window.crypto.randomUUID === 'function') {
            return `SCN-${window.crypto.randomUUID().slice(0, 8).toUpperCase()}`;
        }
        return `SCN-${Date.now().toString(36).toUpperCase()}`;
    }

    function cleanText(value) {
        return String(value || '').replace(/\s+/g, ' ').trim();
    }

    function makeTitle(text) {
        const value = cleanText(text);
        return value.length > 76 ? `${value.slice(0, 73)}...` : value;
    }

    function blankProgress() {
        return Object.fromEntries(WORKSPACES.map(([key]) => [key, false]));
    }

    function normalize(candidate) {
        if (!candidate || typeof candidate !== 'object' || !cleanText(candidate.scenarioText)) {
            return null;
        }
        return {
            version: 1,
            id: cleanText(candidate.id) || createId(),
            title: cleanText(candidate.title) || makeTitle(candidate.scenarioText),
            scenarioText: cleanText(candidate.scenarioText),
            source: cleanText(candidate.source) || 'advisory',
            status: candidate.status === 'closed' ? 'closed' : 'active',
            activeWorkspace: cleanText(candidate.activeWorkspace) || 'advisory',
            progress: { ...blankProgress(), ...(candidate.progress || {}) },
            workspaceInputs: { ...(candidate.workspaceInputs || {}) },
            outputs: { ...(candidate.outputs || {}) },
            createdAt: candidate.createdAt || now(),
            updatedAt: candidate.updatedAt || now(),
        };
    }

    function loadState() {
        try {
            return normalize(JSON.parse(sessionStorage.getItem(STORAGE_KEY)));
        } catch (_error) {
            return null;
        }
    }

    function persist() {
        if (state) {
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } else {
            sessionStorage.removeItem(STORAGE_KEY);
        }
    }

    function notify() {
        render();
        window.dispatchEvent(new CustomEvent('nhanthuat:scenario-change', {
            detail: getState(),
        }));
    }

    function start(scenarioText, options) {
        const text = cleanText(scenarioText);
        if (!text) return null;
        const config = options || {};
        state = {
            version: 1,
            id: createId(),
            title: cleanText(config.title) || makeTitle(text),
            scenarioText: text,
            source: cleanText(config.source) || 'advisory',
            status: 'active',
            activeWorkspace: cleanText(config.workspace) || 'advisory',
            progress: blankProgress(),
            workspaceInputs: {
                [cleanText(config.workspace) || 'advisory']: text,
            },
            outputs: {},
            createdAt: now(),
            updatedAt: now(),
        };
        persist();
        syncInputs();
        notify();
        return getState();
    }

    function capture(workspace, scenarioText, options) {
        const key = cleanText(workspace) || 'advisory';
        const text = cleanText(scenarioText);
        const config = options || {};
        if (!state) {
            return start(text, { ...config, workspace: key });
        }
        if (text) state.workspaceInputs[key] = text;
        state.activeWorkspace = key;
        state.status = 'active';
        state.updatedAt = now();
        persist();
        notify();
        return getState();
    }

    function mark(workspace, output) {
        if (!state) return null;
        const key = cleanText(workspace);
        if (key && Object.prototype.hasOwnProperty.call(state.progress, key)) {
            state.progress[key] = true;
            state.activeWorkspace = key;
        }
        if (key && output !== undefined) state.outputs[key] = output;
        state.updatedAt = now();
        persist();
        notify();
        return getState();
    }

    function getState() {
        return state ? JSON.parse(JSON.stringify(state)) : null;
    }

    function clear() {
        if (state && !window.confirm('Bắt đầu hồ sơ mới và bỏ bản nháp hiện tại trong phiên này?')) {
            return;
        }
        state = null;
        persist();
        ['hero-advisory-input', 'advisory-input', 'council-scenario-input', 'sparring-input', 'war-scenario-input']
            .forEach(id => {
                const input = document.getElementById(id);
                if (input) input.value = '';
            });
        notify();
        const input = document.getElementById('hero-advisory-input') || document.getElementById('advisory-input');
        input?.focus();
    }

    function openWorkspace(viewId, key) {
        if (state) {
            state.activeWorkspace = key;
            state.updatedAt = now();
            persist();
            render();
        }
        if (typeof window.switchWorkspace === 'function') {
            window.switchWorkspace(viewId);
        } else {
            document.getElementById(viewId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function activateView(viewId) {
        const match = WORKSPACES.find(([, candidateViewId]) => candidateViewId === viewId);
        if (!state || !match) return;
        state.activeWorkspace = match[0];
        state.updatedAt = now();
        persist();
        render();
    }

    function syncInputs() {
        if (!state) return;
        const values = {
            'advisory-input': state.workspaceInputs.advisory || state.scenarioText,
            'council-scenario-input': state.workspaceInputs.council || state.scenarioText,
            'sparring-input': state.workspaceInputs.sparring || state.scenarioText,
            'war-scenario-input': state.workspaceInputs.warRoom || state.scenarioText,
        };
        Object.entries(values).forEach(([id, value]) => {
            const input = document.getElementById(id);
            if (input && !cleanText(input.value)) input.value = value;
        });
    }

    function render() {
        const root = document.getElementById('scenario-workspace');
        if (!root) return;
        document.documentElement.classList.toggle('scenario-active', Boolean(state));
        root.classList.toggle('is-active', Boolean(state));
        root.setAttribute('aria-hidden', state ? 'false' : 'true');
        if (!state) return;

        const title = root.querySelector('[data-scenario-title]');
        const meta = root.querySelector('[data-scenario-meta]');
        const epistemic = root.querySelector('[data-scenario-epistemic]');
        if (title) title.textContent = state.title;
        if (meta) meta.textContent = `Bản nháp trong phiên · ${state.id}`;
        if (epistemic) {
            const output = state.outputs[state.activeWorkspace] || {};
            const labels = {
                engine_inference: 'Kết quả: suy luận của hệ thống',
                recommendation: 'Kết quả: khuyến nghị',
                simulation: 'Kết quả: mô phỏng',
            };
            epistemic.textContent = labels[output.epistemicStatus] || 'Đầu vào: trình bày của người dùng';
        }

        root.querySelectorAll('[data-scenario-step]').forEach(button => {
            const key = button.dataset.scenarioStep;
            button.classList.toggle('is-complete', Boolean(state.progress[key]));
            button.classList.toggle('is-current', state.activeWorkspace === key);
            button.setAttribute('aria-current', state.activeWorkspace === key ? 'step' : 'false');
        });
    }

    function bind() {
        const root = document.getElementById('scenario-workspace');
        if (!root) return;
        root.querySelectorAll('[data-scenario-step]').forEach(button => {
            button.addEventListener('click', () => {
                openWorkspace(button.dataset.viewId, button.dataset.scenarioStep);
            });
        });
        root.querySelector('[data-scenario-sync]')?.addEventListener('click', () => {
            syncInputs();
            const current = WORKSPACES.find(([key]) => key === state?.activeWorkspace) || WORKSPACES[0];
            openWorkspace(current[1], current[0]);
        });
        root.querySelector('[data-scenario-clear]')?.addEventListener('click', clear);
        syncInputs();
        render();
    }

    window.NhanThuatScenario = {
        activateView,
        capture,
        clear,
        getState,
        mark,
        start,
        syncInputs,
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bind, { once: true });
    } else {
        bind();
    }
})();
