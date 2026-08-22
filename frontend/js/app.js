const state = {
    currentView: 'explore',
    dataCache: {},
    chatHistory: []
};

// DOM Elements
const els = {
    navItems: document.querySelectorAll('.nav-item'),
    viewContainer: document.getElementById('view-container'),
    pageTitle: document.getElementById('page-title'),
    globalSearch: document.getElementById('global-search')
};

// Templates
const templates = {
    loader: `<div class="loader">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                </svg>
                <style>.spin { animation: spin 1s linear infinite; } @keyframes spin { 100% { transform: rotate(360deg); } }</style>
             </div>`,
    
    error: (msg) => `<div class="glass-panel fade-in" style="padding: 2rem; border-radius: 24px; text-align: center; color: #ff5555; margin: 2rem;">
                        <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 1rem;">Lỗi</h3>
                        <p>${msg}</p>
                     </div>`,
                     
    unitCard: (unit, delay) => `
        <div class="bento-card fade-in" style="animation-delay: ${delay}ms" onclick="app.navigateToUnit('${unit.id}')">
            <div class="card-tag">${unit.type || 'Unit'} • ${unit.domain || 'N/A'}</div>
            <h3 class="card-title">${unit.title || unit.id}</h3>
            <p class="card-excerpt">${unit.summary ? unit.summary.substring(0, 120) + '...' : 'Không có tóm tắt.'}</p>
        </div>
    `
};

// App Logic
const app = {
    init() {
        this.bindEvents();
        
        // Check hash for initial routing
        const hash = window.location.hash.replace('#', '');
        if (hash) {
            const navEl = document.querySelector(`.nav-item[data-view="${hash}"]`);
            if (navEl) this.switchNav(navEl);
            this.loadView(hash);
        } else {
            this.loadView(state.currentView);
        }
    },

    bindEvents() {
        els.navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const view = e.currentTarget.dataset.view;
                if(view) {
                    this.switchNav(e.currentTarget);
                    this.loadView(view);
                }
            });
        });

        if (els.globalSearch) {
            els.globalSearch.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                    // Quick transition to explore if not there, or filter
                    this.loadView('explore');
                    // We can implement actual filter later
                }
            });
        }
    },

    switchNav(activeEl) {
        els.navItems.forEach(el => el.classList.remove('active'));
        if(activeEl) activeEl.classList.add('active');
    },

    async loadView(view) {
        state.currentView = view;
        window.location.hash = view;
        els.viewContainer.innerHTML = templates.loader;

        try {
            if (view === 'explore') {
                els.pageTitle.textContent = "Khám phá Tri thức";
                await this.renderExplore();
            } else if (view === 'domains') {
                els.pageTitle.textContent = "Lĩnh vực";
                await this.renderDomains();
            } else if (view === 'ask') {
                els.pageTitle.textContent = "Hỏi Nhân Thuật";
                this.renderAsk();
            }
        } catch (error) {
            els.viewContainer.innerHTML = templates.error(error.message);
        }
    },

    async renderExplore() {
        try {
            const res = await fetch('/api/v1/knowledge/units');
            if (!res.ok) throw new Error('API request failed');
            const data = await res.json();
            
            let html = '<div class="bento-grid">';
            if (data.units && data.units.length > 0) {
                data.units.forEach((unit, index) => {
                    html += templates.unitCard(unit, index * 50);
                });
            } else {
                html += '<div class="glass-panel" style="padding: 2rem; grid-column: 1 / -1; text-align: center;">Chưa có dữ liệu tri thức.</div>';
            }
            html += '</div>';
            els.viewContainer.innerHTML = html;
        } catch (e) {
            els.viewContainer.innerHTML = templates.error("Không thể kết nối Backend API.");
            console.error(e);
        }
    },

    async renderDomains() {
        try {
            const res = await fetch('/api/v1/knowledge/units');
            if (!res.ok) throw new Error('API request failed');
            const data = await res.json();
            
            // Group by domain
            const domainsMap = {};
            (data.units || []).forEach(u => {
                if (!domainsMap[u.domain]) domainsMap[u.domain] = { count: 0, title: u.domain };
                domainsMap[u.domain].count++;
            });

            let html = '<div class="bento-grid">';
            let idx = 0;
            for (const [slug, info] of Object.entries(domainsMap)) {
                html += `
                    <div class="bento-card fade-in" style="animation-delay: ${idx * 100}ms;" onclick="app.loadView('explore')">
                        <div class="card-tag">Lĩnh vực</div>
                        <h3 class="card-title" style="text-transform: capitalize;">${info.title}</h3>
                        <p class="card-excerpt">Gồm ${info.count} đơn vị tri thức chuyên sâu.</p>
                    </div>
                `;
                idx++;
            }
            html += '</div>';
            els.viewContainer.innerHTML = html;
        } catch (e) {
            els.viewContainer.innerHTML = templates.error("Lỗi tải danh mục Lĩnh vực.");
            console.error(e);
        }
    },

    renderAsk() {
        els.viewContainer.innerHTML = `
            <div class="glass-panel fade-in" style="padding: 2rem; border-radius: 24px; flex: 1; display: flex; flex-direction: column; margin-bottom: 2rem;">
                <div style="flex: 1; overflow-y: auto; margin-bottom: 1.5rem; display: flex; flex-direction: column;" id="chat-history">
                    ${state.chatHistory.length > 0 ? state.chatHistory.join('') : `
                    <div style="text-align: center; color: var(--text-secondary); margin-top: auto; margin-bottom: auto;" id="ask-empty-state">
                        <span style="font-size: 3rem; display: block; margin-bottom: 1rem;">♟️</span>
                        <h2 style="font-family: 'Playfair Display', serif; color: white; margin-bottom: 0.5rem; font-weight: 400;">Xin chào,</h2>
                        <p>Hãy hỏi tôi bất cứ điều gì về nghệ thuật quản trị con người.</p>
                    </div>`}
                </div>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <input type="text" id="ask-input" placeholder="Nhập tình huống hoặc câu hỏi của bạn..." style="flex: 1; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); border-radius: 99px; padding: 1.25rem 1.5rem; color: white; font-family: inherit; font-size: 1rem; outline: none; transition: all 0.3s ease;">
                    <button id="ask-btn" style="background: var(--text-primary); color: var(--bg-color); border: none; border-radius: 99px; padding: 1.25rem 2.5rem; font-weight: 600; font-family: 'Outfit', sans-serif; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(255,255,255,0.2);">
                        Phân tích
                    </button>
                </div>
            </div>
        `;
        
        document.getElementById('ask-btn').addEventListener('click', async () => {
            const input = document.getElementById('ask-input');
            const val = input.value.trim();
            if (!val) return;
            
            const history = document.getElementById('chat-history');
            const emptyState = document.getElementById('ask-empty-state');
            if (emptyState) emptyState.remove();
            
            // Add user message
            const userHtml = `<div style="margin-bottom: 1rem; text-align: right;"><div style="display: inline-block; background: var(--glass-bg); padding: 1rem 1.5rem; border-radius: 20px 20px 0 20px; border: 1px solid var(--glass-border);">${val}</div></div>`;
            history.innerHTML += userHtml;
            state.chatHistory.push(userHtml);
            input.value = '';
            
            // Loading indicator
            const loaderId = 'loader-' + Date.now();
            history.innerHTML += `<div id="${loaderId}" style="margin-bottom: 1rem; text-align: left;"><div style="display: inline-block; color: var(--accent);">Đang phân tích...</div></div>`;
            history.scrollTop = history.scrollHeight;
            
            try {
                const res = await fetch('/api/v1/nhan-thuat/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ scenario_text: val, scenario_type_hint: 'leadership' })
                });
                const data = await res.json();
                document.getElementById(loaderId).remove();
                
                const responseHtml = app.formatAnalysisResponse(data);
                const botHtml = `<div style="margin-bottom: 1rem; text-align: left;"><div style="display: inline-block; background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 20px 20px 20px 0; border: 1px solid var(--glass-border); max-width: 85%; font-family: 'Outfit', sans-serif; line-height: 1.6;">${responseHtml}</div></div>`;
                history.innerHTML += botHtml;
                state.chatHistory.push(botHtml);
            } catch (e) {
                document.getElementById(loaderId).remove();
                const errorHtml = `<div style="margin-bottom: 1rem; text-align: left; color: #ff5555;">Lỗi kết nối API.</div>`;
                history.innerHTML += errorHtml;
                state.chatHistory.push(errorHtml);
            }
            history.scrollTop = history.scrollHeight;
        });
    },

    async navigateToUnit(unitId) {
        state.currentView = 'unitDetail';
        window.location.hash = 'unitDetail-' + unitId;
        els.viewContainer.innerHTML = templates.loader;
        
        try {
            const res = await fetch(`/api/v1/knowledge/units/${unitId}`);
            if (!res.ok) throw new Error('Không thể tải dữ liệu tri thức');
            const data = await res.json();
            
            if (data.status === 'success' && data.unit) {
                this.renderUnitDetail(data.unit);
            } else {
                throw new Error(data.message || 'Lỗi dữ liệu');
            }
        } catch (e) {
            els.viewContainer.innerHTML = templates.error(e.message);
        }
    },

    renderUnitDetail(unit) {
        // Handle different nested structures if necessary
        const unitData = unit.unit || unit;
        els.pageTitle.textContent = unitData.title || unitData.id;
        
        let html = `
            <div class="glass-panel fade-in" style="padding: 2.5rem; border-radius: 24px; position: relative;">
                <button onclick="app.loadView('explore')" style="background: transparent; color: var(--text-secondary); border: 1px solid var(--glass-border); padding: 0.5rem 1rem; border-radius: 99px; cursor: pointer; margin-bottom: 2rem; font-family: 'Outfit', sans-serif; display: flex; align-items: center; gap: 8px; transition: all 0.3s ease;">
                    <span style="font-size: 1.2rem;">←</span> Quay lại
                </button>
                
                <div style="display: flex; gap: 10px; margin-bottom: 1.5rem; flex-wrap: wrap;">
                    <span class="card-tag">${unitData.type || 'Tri thức'}</span>
                    <span class="card-tag" style="color: #34d399; background: rgba(52, 211, 153, 0.1); border-color: rgba(52, 211, 153, 0.2);">${unitData.primary_domain || unitData.domain || ''}</span>
                    <span class="card-tag" style="color: #60a5fa; background: rgba(96, 165, 250, 0.1); border-color: rgba(96, 165, 250, 0.2);">${unitData.id || ''}</span>
                </div>
                
                <h1 style="font-family: 'Playfair Display', serif; color: white; font-size: 2.5rem; margin-bottom: 1.5rem; font-weight: 500;">
                    ${unitData.title || 'Không có tiêu đề'}
                </h1>
                
                <div class="markdown-body" style="color: rgba(255,255,255,0.9); font-family: 'Times New Roman', Times, serif; font-size: 1.15rem; line-height: 1.7;">
                    ${unitData.summary ? `<h3 style="color: var(--accent); font-family: 'Playfair Display', serif; margin-top: 1.5rem; margin-bottom: 1rem;">Tóm tắt (Summary)</h3><p>${unitData.summary.replace(/\\n/g, '<br>')}</p>` : ''}
                    
                    ${unitData.definition ? `<h3 style="color: var(--accent); font-family: 'Playfair Display', serif; margin-top: 2rem; margin-bottom: 1rem;">Định nghĩa bản chất (Definition)</h3><p>${unitData.definition.replace(/\\n/g, '<br>')}</p>` : ''}
                    
                    ${unitData.mechanism && unitData.mechanism.length > 0 ? `
                        <h3 style="color: var(--accent); font-family: 'Playfair Display', serif; margin-top: 2rem; margin-bottom: 1rem;">Cơ chế hoạt động (Mechanism)</h3>
                        <ul style="padding-left: 1.5rem;">
                            ${unitData.mechanism.map(m => `<li style="margin-bottom: 0.5rem;">${m}</li>`).join('')}
                        </ul>
                    ` : ''}
                    
                    ${unitData.conditions && unitData.conditions.length > 0 ? `
                        <h3 style="color: var(--accent); font-family: 'Playfair Display', serif; margin-top: 2rem; margin-bottom: 1rem;">Điều kiện kích hoạt (Conditions)</h3>
                        <ul style="padding-left: 1.5rem;">
                            ${unitData.conditions.map(c => `<li style="margin-bottom: 0.5rem;">${c}</li>`).join('')}
                        </ul>
                    ` : ''}
                    
                    ${unitData.risks && unitData.risks.length > 0 ? `
                        <h3 style="color: var(--accent); font-family: 'Playfair Display', serif; margin-top: 2rem; margin-bottom: 1rem;">Rủi ro (Risks)</h3>
                        <ul style="padding-left: 1.5rem;">
                            ${unitData.risks.map(r => `<li style="margin-bottom: 0.5rem; color: #fca5a5;">${r}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            </div>
        `;
        els.viewContainer.innerHTML = html;
    },

    generateMockCards(count) {
        let cards = '';
        for (let i = 0; i < count; i++) {
            cards += templates.unitCard({
                id: `NT-LAW-00${i+1}`,
                type: 'Principle',
                domain: 'Leadership',
                title: 'Nguyên tắc Vận hành Đội ngũ',
                summary: 'Một nguyên tắc cốt lõi giúp tối ưu hóa hiệu suất làm việc nhóm thông qua sự thấu hiểu và phân bổ nguồn lực hợp lý.'
            }, i * 100);
        }
        return cards;
    },

    formatAnalysisResponse(data) {
        if (!data || data.status === 'error') {
            return `<div style="color: #ff5555;">${data.message || 'Lỗi không xác định từ server.'}</div>`;
        }

        // If using KnowledgeSynthesizer, render exactly like Streamlit
        if (data.synthesis_result) {
            let html = '';
            
            // Ambiguity Warning
            if (data.is_ambiguous && data.ambiguity_warning) {
                html += `<div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 1rem; margin-bottom: 1.5rem; border-radius: 0 8px 8px 0;">
                            <strong style="color: #f59e0b; display: block; margin-bottom: 0.5rem;">⚠️ CẢNH BÁO THIẾU BỐI CẢNH</strong>
                            <div style="color: rgba(255,255,255,0.9); white-space: pre-line; font-family: 'Times New Roman', Times, serif; font-size: 1.1rem;">${data.ambiguity_warning.replace('⚠️ CẢNH BẢO THIẾU BỐI CẢNH (AMBIGUOUS CONTEXT WARNING):', '').trim()}</div>
                        </div>`;
            }

            // 1. Synthesis content (Markdown)
            html += `<div class="markdown-body" style="color: rgba(255,255,255,0.9); font-family: 'Times New Roman', Times, serif; font-size: 1.1rem; line-height: 1.6;">
                ${marked.parse(data.synthesis_result.synthesis || '')}
            </div>`;
            
            // 2. Knowledge Flow UI (Dòng truy xuất tri thức)
            html += `<div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
                        <h4 style="color: var(--accent); font-family: 'Playfair Display', serif; margin-bottom: 1rem; font-size: 1.3rem;">Dòng truy xuất tri thức</h4>
                        <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
                            <span>Câu hỏi</span> <span style="opacity: 0.5">→</span>
                            <span>Tìm tri thức liên quan</span> <span style="opacity: 0.5">→</span>
                            <span>Kiểm tra tri thức nền</span> <span style="opacity: 0.5">→</span>
                            <span>Xây dựng bối cảnh</span> <span style="opacity: 0.5">→</span>
                            <span>Đánh giá rủi ro</span>
                        </div>
                    </div>`;

            // 3. Citations UI
            if (data.synthesis_result.citations && data.synthesis_result.citations.length > 0) {
                html += `<div style="margin-top: 2rem;">
                            <h4 style="color: var(--accent); font-family: 'Playfair Display', serif; margin-bottom: 1rem; font-size: 1.3rem;">Trích dẫn</h4>
                            <ul style="list-style-type: none; padding: 0; margin: 0; font-family: 'Times New Roman', Times, serif; font-size: 1.05rem;">`;
                data.synthesis_result.citations.forEach(cit => {
                    html += `<li style="margin-bottom: 0.5rem; color: rgba(255,255,255,0.8);">
                                ${cit.title} — <strong>${cit.id}</strong> <span style="opacity: 0.6">(${cit.domain})</span>
                             </li>`;
                });
                html += `</ul></div>`;
            }

            // 4. Audit Info (Kiểm tra)
            if (data.synthesis_result.audit) {
                const audit = data.synthesis_result.audit;
                html += `<div style="margin-top: 2rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px; font-size: 0.85rem; color: rgba(255,255,255,0.5); font-family: 'Outfit', sans-serif;">
                            Kiểm tra: ${audit.correlation_id} | Nhà cung cấp: ${audit.provider} | Mô hình: ${audit.model} | ${audit.latency_ms} ms
                         </div>`;
            }

            // 5. Risk Assessment (Đánh giá rủi ro)
            html += `<div style="margin-top: 1rem;">
                        <h4 style="color: var(--accent); font-family: 'Playfair Display', serif; margin-bottom: 0.5rem; font-size: 1.1rem;">Đánh giá rủi ro</h4>
                        <div style="color: rgba(255,255,255,0.7); font-family: 'Times New Roman', Times, serif; font-size: 1.05rem;">Độ phù hợp: 100.0%</div>
                     </div>`;

            return html;
        }

        let html = '';

        // Ambiguity Warning
        if (data.is_ambiguous && data.ambiguity_warning) {
            html += `<div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 1rem; margin-bottom: 1.5rem; border-radius: 0 8px 8px 0;">
                        <strong style="color: #f59e0b; display: block; margin-bottom: 0.5rem;">⚠️ CẢNH BÁO THIẾU BỐI CẢNH</strong>
                        <div style="color: rgba(255,255,255,0.9); white-space: pre-line;">${data.ambiguity_warning.replace('⚠️ CẢNH BẢO THIẾU BỐI CẢNH (AMBIGUOUS CONTEXT WARNING):', '').trim()}</div>
                     </div>`;
        }

        const script = data.action_script;
        if (script) {
            // Position Analysis
            if (script.position_analysis) {
                html += `<div style="margin-bottom: 1.5rem;">
                            <h4 style="color: var(--accent); margin-bottom: 0.5rem; font-family: 'Playfair Display', serif; font-size: 1.2rem;">Phân tích vị thế</h4>
                            <p style="color: rgba(255,255,255,0.85);">${script.position_analysis}</p>
                         </div>`;
            }

            // Steps
            html += `<div style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.5rem;">`;
            const steps = [script.step_1_anchor, script.step_2_deadline_consequence, script.step_3_way_out_plan_b];
            steps.forEach((step, idx) => {
                if (step && step.title) {
                    html += `<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem;">
                                <strong style="color: white; display: block; margin-bottom: 0.5rem;">${step.title}</strong>
                                <div style="color: rgba(255,255,255,0.7); font-style: italic;">${step.verbatim}</div>
                             </div>`;
                }
            });
            html += `</div>`;

            // Official Communication
            if (script.draft_official_communication) {
                html += `<div style="margin-bottom: 1.5rem;">
                            <h4 style="color: var(--accent); margin-bottom: 0.5rem; font-family: 'Playfair Display', serif; font-size: 1.2rem;">Dự thảo Truyền thông</h4>
                            <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; font-family: monospace; color: rgba(255,255,255,0.8); white-space: pre-line; font-size: 0.9rem;">
                                ${script.draft_official_communication}
                            </div>
                         </div>`;
            }

            // Directives & Principles
            if (script.financial_and_operational_directives && script.financial_and_operational_directives.length > 0) {
                html += `<div style="margin-bottom: 1rem;">
                            <strong style="color: white; display: block; margin-bottom: 0.5rem;">Chỉ đạo Vận hành & Tài chính:</strong>
                            <ul style="color: rgba(255,255,255,0.8); padding-left: 1.5rem; margin: 0;">
                                ${script.financial_and_operational_directives.map(d => `<li style="margin-bottom: 0.25rem;">${d}</li>`).join('')}
                            </ul>
                         </div>`;
            }
        }

        // Philosophy & Knowledge Match
        if (data.philosophy_routing || (data.matched_knowledge_units && data.matched_knowledge_units.length > 0)) {
            html += `<hr style="border-color: rgba(255,255,255,0.1); margin: 1.5rem 0;">
                     <div style="font-size: 0.85rem; color: rgba(255,255,255,0.5);">`;
            
            if (data.philosophy_routing) {
                html += `<div><strong>Hệ tư tưởng:</strong> ${data.philosophy_routing.primary_philosophy}</div>`;
            }
            if (data.matched_knowledge_units && data.matched_knowledge_units.length > 0) {
                html += `<div style="margin-top: 0.5rem;"><strong>Tri thức liên quan:</strong> ${data.matched_knowledge_units.map(u => u.title).join(', ')}</div>`;
            }
            html += `</div>`;
        }

        return html;
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
