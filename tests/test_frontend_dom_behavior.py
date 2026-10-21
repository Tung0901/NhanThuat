"""
Behavioral DOM and JavaScript execution tests for NhanThuat frontend (Phase 2).
Executes the actual functions from `frontend/app.html` inside a Node.js VM DOM harness
and verifies:
1. 64-hexagram palace filter single-active state, search+palace composition, detail drawer.
2. Loading, empty, and API error states on `/api/v1/iching/hexagrams`.
3. Cross-room transfer workflows (`transferAdvisoryToSparring`, `transferCouncilToSparring`,
   `transferCouncilToWarRoom`) only populate inputs and open configuration without auto-calling APIs.
4. Typo fix ("ĐỘI NGŨ TIẾP NHẬN") and desktop/mobile responsive stylesheet rules.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from lxml import html as lxml_html

from backend.app.engine.philosophies.iching_service import iching_service

APP_HTML_PATH = Path(__file__).resolve().parent.parent / "frontend" / "app.html"


def test_dom_structure_palace_pills_and_typo_fix() -> None:
    """Parse frontend/app.html into a real DOM tree and verify structure, classes, and typo fix."""
    raw_html = APP_HTML_PATH.read_text(encoding="utf-8")
    assert "ĐỘI NGŨ TIẾẬN NHẬN" not in raw_html
    assert "ĐỘI NGŨ TIẾP NHẬN (TARGET TEAM)" in raw_html

    doc = lxml_html.fromstring(raw_html)

    # Verify #iching-palace-tabs buttons all carry .iching-palace-pill and only the first is .active
    palace_buttons = doc.xpath(
        '//*[@id="iching-palace-tabs"]//button[contains(concat(" ", normalize-space(@class), " "), " iching-palace-pill ")]'
    )
    assert len(palace_buttons) == 9
    active_buttons = [
        btn for btn in palace_buttons if "active" in (btn.get("class") or "").split()
    ]
    assert len(active_buttons) == 1
    assert active_buttons[0].get("data-palace") == ""

    # Verify initial loading state attribute on #iching-hexagrams-grid
    loading_boxes = doc.xpath('//*[@id="iching-hexagrams-grid"]//*[@data-state="loading"]')
    assert len(loading_boxes) == 1

    # Verify desktop & mobile responsive CSS rules exist in stylesheet
    style_texts = "\n".join(el.text_content() for el in doc.xpath("//style"))
    assert ".iching-hexagrams-grid" in style_texts
    assert "@media (max-width: 640px)" in style_texts
    assert "grid-template-columns: 1fr;" in style_texts


def test_frontend_js_behavioral_execution_in_dom_harness(tmp_path: Path) -> None:
    """Execute actual JS functions extracted from frontend/app.html in Node.js VM against a live DOM model."""
    hexagrams_payload = iching_service.list_hexagrams()
    assert len(hexagrams_payload) == 64

    harness_js = tmp_path / "dom_harness.js"
    data_json = tmp_path / "hexagrams.json"
    data_json.write_text(json.dumps(hexagrams_payload, ensure_ascii=False), encoding="utf-8")

    harness_code = r"""
const fs = require('fs');
const vm = require('vm');

const htmlPath = process.argv[2];
const hexJsonPath = process.argv[3];
const html = fs.readFileSync(htmlPath, 'utf-8');
const hexagramsData = JSON.parse(fs.readFileSync(hexJsonPath, 'utf-8'));

// Extract the main application script block containing loadIChingHexagrams and transfer functions
const scriptBlocks = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
const mainScript = scriptBlocks.find(s => s.includes('function loadIChingHexagrams') && s.includes('function transferAdvisoryToSparring'));
if (!mainScript) {
    throw new Error('Could not locate main application script block in frontend/app.html');
}

function extractFunctionSource(source, fnName) {
    const asyncIdx = source.indexOf('async function ' + fnName + '(');
    const syncIdx = source.indexOf('function ' + fnName + '(');
    const startIdx = asyncIdx !== -1 ? asyncIdx : syncIdx;
    if (startIdx === -1) {
        throw new Error('Function not found: ' + fnName);
    }
    let braceDepth = 0;
    let started = false;
    for (let i = startIdx; i < source.length; i++) {
        const ch = source[i];
        if (ch === '{') {
            braceDepth++;
            started = true;
        } else if (ch === '}') {
            braceDepth--;
            if (started && braceDepth === 0) {
                return source.slice(startIdx, i + 1);
            }
        }
    }
    throw new Error('Unbalanced braces for function: ' + fnName);
}

class ClassList {
    constructor(initial = []) {
        this._set = new Set(initial.filter(Boolean));
    }
    add(...names) { names.forEach(n => this._set.add(n)); }
    remove(...names) { names.forEach(n => this._set.delete(n)); }
    contains(name) { return this._set.has(name); }
    toArray() { return Array.from(this._set); }
}

class MockElement {
    constructor(id, classes = [], attrs = {}) {
        this.id = id;
        this.classList = new ClassList(classes);
        this.attrs = { ...attrs };
        this.style = { display: attrs.display || '' };
        this.value = attrs.value || '';
        this.innerHTML = '';
        this.textContent = '';
        this.focused = false;
        this.children = [];
    }
    getAttribute(k) { return this.attrs[k] ?? null; }
    focus() { this.focused = true; }
    appendChild(child) { this.children.push(child); }
}

const elementsById = new Map();
function registerEl(id, classes = [], attrs = {}) {
    const el = new MockElement(id, classes, attrs);
    elementsById.set(id, el);
    return el;
}

registerEl('iching-hexagrams-grid', ['iching-hexagrams-grid']);
registerEl('iching-search-input', ['iching-search-input'], { value: '' });
registerEl('iching-count-badge', [], {});
registerEl('iching-detail-drawer', ['iching-detail-drawer'], { display: 'none' });
registerEl('sparring-setup-panel', [], { display: 'none' });
registerEl('sparring-context-input', [], { value: '' });
registerEl('sparring-lens-select', [], { value: 'auto' });
registerEl('sparring-opening-input', [], { value: '' });
registerEl('sparring-active-badge', [], {});
registerEl('sparring-feed', [], {});
registerEl('sparring-input', [], { value: '' });
registerEl('council-scenario-input', [], { value: '' });
registerEl('war-scenario-input', [], { value: '' });
registerEl('war-status-badge', [], {});

// Build the 9 palace filter buttons matching frontend/app.html
const palaceValues = ['', 'Càn', 'Khôn', 'Khảm', 'Ly', 'Chấn', 'Tốn', 'Cấn', 'Đoài'];
const palacePills = palaceValues.map((p, idx) => {
    return new MockElement(
        `palace-pill-${idx}`,
        idx === 0 ? ['mode-pill', 'iching-palace-pill', 'active'] : ['mode-pill', 'iching-palace-pill'],
        { 'data-palace': p }
    );
});

const fetchCalls = [];
let mockFetchBehavior = 'success';

const sandbox = {
    console,
    decodeURIComponent,
    encodeURIComponent,
    Number,
    String,
    Array,
    escapeHtml: (str) => String(str ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;'),
    allIChingHexagrams: [],
    selectedIChingPalace: 'all',
    activeWorkspace: 'view-advisory',
    alerts: [],
    alert: (msg) => sandbox.alerts.push(msg),
    switchWorkspace: (viewId) => { sandbox.activeWorkspace = viewId; },
    window: {
        lastCouncilDeliberation: null,
        NhanThuatScenario: {
            capture: () => {},
            mark: () => {},
            getState: () => ({}),
        },
    },
    document: {
        getElementById: (id) => elementsById.get(id) || null,
        querySelectorAll: (selector) => {
            if (selector === '.iching-palace-pill') return palacePills;
            return [];
        },
        createElement: (tag) => new MockElement(tag),
    },
    fetch: async (url, options = {}) => {
        fetchCalls.push({ url, options });
        if (mockFetchBehavior === 'network_error') {
            throw new Error('Network disconnected');
        }
        if (mockFetchBehavior === 'http_500') {
            return {
                ok: false,
                status: 500,
                json: async () => ({ status: 'error', message: 'Internal Server Error' }),
            };
        }
        if (url === '/api/v1/iching/hexagrams') {
            return {
                ok: true,
                status: 200,
                json: async () => ({ status: 'success', hexagrams: hexagramsData }),
            };
        }
        return {
            ok: true,
            status: 200,
            json: async () => ({ status: 'success' }),
        };
    },
};
sandbox.window.document = sandbox.document;

const fnNames = [
    'toggleSparringSetup',
    'loadIChingHexagrams',
    'selectIChingPalace',
    'filterIChingHexagrams',
    'showIChingHexagramDetail',
    'transferAdvisoryToSparring',
    'transferCouncilToSparring',
    'transferCouncilToWarRoom',
];

const combinedCode = fnNames.map(fn => extractFunctionSource(mainScript, fn)).join('\n\n');
vm.createContext(sandbox);
vm.runInContext(combinedCode, sandbox);

(async () => {
    // 1. Test loadIChingHexagrams success
    await sandbox.loadIChingHexagrams(true);
    const grid = elementsById.get('iching-hexagrams-grid');
    const countBadge = elementsById.get('iching-count-badge');
    const initialCards = (grid.innerHTML.match(/class="iching-hex-card"/g) || []).length;
    if (initialCards !== 64 || countBadge.textContent !== '64') {
        throw new Error(`Expected 64 hexagrams initially, got cards=${initialCards}, badge=${countBadge.textContent}`);
    }

    // 2. Test selectIChingPalace('Càn', palacePills[1]) -> single active pill + 8 Càn hexagrams
    sandbox.selectIChingPalace('Càn', palacePills[1]);
    const activeAfterCan = palacePills.filter(p => p.classList.contains('active'));
    if (activeAfterCan.length !== 1 || activeAfterCan[0] !== palacePills[1]) {
        throw new Error(`Expected exactly 1 active pill (Càn), got ${activeAfterCan.length}`);
    }
    const canCards = (grid.innerHTML.match(/class="iching-hex-card"/g) || []).length;
    if (canCards !== 8 || countBadge.textContent !== '8') {
        throw new Error(`Expected 8 Càn hexagrams, got cards=${canCards}, badge=${countBadge.textContent}`);
    }

    // 3. Test switching palace to Khảm -> Càn deactivated, Khảm activated
    sandbox.selectIChingPalace('Khảm', palacePills[3]);
    const activeAfterKham = palacePills.filter(p => p.classList.contains('active'));
    if (activeAfterKham.length !== 1 || activeAfterKham[0] !== palacePills[3] || palacePills[1].classList.contains('active')) {
        throw new Error('Palace active state did not switch exclusively to Khảm');
    }

    // 4. Test search + palace composition (Càn + 'Kháng Long')
    sandbox.selectIChingPalace('Càn', palacePills[1]);
    elementsById.get('iching-search-input').value = 'Kháng Long';
    sandbox.filterIChingHexagrams();
    const composedCards = (grid.innerHTML.match(/class="iching-hex-card"/g) || []).length;
    if (composedCards < 1 || !grid.innerHTML.includes('Thuần Càn')) {
        throw new Error('Composed search + palace filter failed to find Thuần Càn');
    }

    // 5. Test empty state when search matches nothing
    elementsById.get('iching-search-input').value = 'khong-ton-tai-que-nay-9999';
    sandbox.filterIChingHexagrams();
    if (!grid.innerHTML.includes('data-state="empty"') || countBadge.textContent !== '0') {
        throw new Error('Empty state was not rendered properly when filter matched 0 hexagrams');
    }

    // Reset search and test detail drawer
    elementsById.get('iching-search-input').value = '';
    sandbox.selectIChingPalace('', palacePills[0]);
    sandbox.showIChingHexagramDetail(1);
    const drawer = elementsById.get('iching-detail-drawer');
    if (drawer.style.display !== 'block' || !drawer.innerHTML.includes('Thuần Càn')) {
        throw new Error('showIChingHexagramDetail(1) did not open detail drawer with Hexagram #1');
    }

    // 6. Test API error state (HTTP 500)
    mockFetchBehavior = 'http_500';
    await sandbox.loadIChingHexagrams(true);
    if (!grid.innerHTML.includes('data-state="error"') || !grid.innerHTML.includes('HTTP 500')) {
        throw new Error('API error state was not rendered on HTTP 500');
    }

    // 7. Test Cross-Room Transfer Workflows do NOT auto-call API
    fetchCalls.length = 0;
    mockFetchBehavior = 'success';

    sandbox.transferAdvisoryToSparring(encodeURIComponent('Nhà thầu phụ đòi tăng giá 25% ngay giữa dự án'));
    if (sandbox.activeWorkspace !== 'view-sparring') {
        throw new Error('transferAdvisoryToSparring did not switch to view-sparring');
    }
    if (elementsById.get('sparring-setup-panel').style.display !== 'block') {
        throw new Error('transferAdvisoryToSparring did not open sparring-setup-panel');
    }
    if (elementsById.get('sparring-context-input').value !== 'Nhà thầu phụ đòi tăng giá 25% ngay giữa dự án') {
        throw new Error('transferAdvisoryToSparring did not populate sparring-context-input');
    }
    if (fetchCalls.length !== 0) {
        throw new Error(`transferAdvisoryToSparring must not call API automatically, but made ${fetchCalls.length} fetch calls`);
    }

    sandbox.window.lastCouncilDeliberation = {
        scenario_text: 'Xung đột quyền lực giữa Giám đốc Kinh doanh và Giám đốc Vận hành',
        deliberation: {
            decision_matrix: {
                highest_consensus: 'Tách bạch quyền phán quyết ngân sách và thiết lập KPIs chéo.',
                plan_a_primary: { summary: 'Áp dụng Pháp gia định ranh giới quyền hạn.' }
            }
        }
    };

    sandbox.transferCouncilToSparring();
    if (!elementsById.get('sparring-context-input').value.includes('Áp dụng Pháp gia định ranh giới quyền hạn.')) {
        throw new Error('transferCouncilToSparring did not populate Council plan summary');
    }
    if (fetchCalls.length !== 0) {
        throw new Error(`transferCouncilToSparring must not call API automatically, but made ${fetchCalls.length} fetch calls`);
    }

    sandbox.transferCouncilToWarRoom();
    if (sandbox.activeWorkspace !== 'view-war-room') {
        throw new Error('transferCouncilToWarRoom did not switch to view-war-room');
    }
    if (!elementsById.get('war-scenario-input').value.includes('Tách bạch quyền phán quyết ngân sách')) {
        throw new Error('transferCouncilToWarRoom did not populate war-scenario-input');
    }
    if (elementsById.get('war-status-badge').textContent !== 'CHỜ XÁC NHẬN KHỞI TẠO') {
        throw new Error('transferCouncilToWarRoom did not set war-status-badge to CHỜ XÁC NHẬN KHỞI TẠO');
    }
    if (fetchCalls.length !== 0) {
        throw new Error(`transferCouncilToWarRoom must not call API automatically, but made ${fetchCalls.length} fetch calls`);
    }

    console.log('DOM_HARNESS_OK');
})().catch(err => {
    console.error(err);
    process.exit(1);
});
"""
    harness_js.write_text(harness_code, encoding="utf-8")
    proc = subprocess.run(
        ["node", str(harness_js), str(APP_HTML_PATH), str(data_json)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert proc.returncode == 0, f"DOM Harness failed:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
    assert "DOM_HARNESS_OK" in proc.stdout
