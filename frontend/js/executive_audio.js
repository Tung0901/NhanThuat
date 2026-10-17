/**
 * Nhân Thuật Executive Audio Controller
 * Converts strategic advisory reports and verbatim scripts into spoken audio.
 * Zero-cost, zero-latency, offline-capable via Web Speech API with sentence chunking.
 */

(function () {
    'use strict';

    window.__advisoryStore = window.__advisoryStore || {};

    const ABBR_MAP = {
        'KPI': 'chỉ số hiệu suất',
        'KPIs': 'các chỉ số hiệu suất',
        'OKR': 'mục tiêu then chốt',
        'OKRs': 'các mục tiêu then chốt',
        'DISC': 'mô hình D I S C',
        'CEO': 'Giám đốc điều hành',
        'COO': 'Giám đốc vận hành',
        'CFO': 'Giám đốc tài chính',
        'HR': 'nhân sự',
        'PO': 'chủ sản phẩm',
        'Plan B': 'Phương án dự phòng B',
        'Plan A': 'Phương án A',
        'RCA': 'phân tích nguyên nhân gốc rễ',
        'Verbatim': 'Lời thoại mẫu từng câu chữ'
    };

    function cleanMarkdownForSpeech(text) {
        if (!text || typeof text !== 'string') return '';
        let s = text;
        // Strip code blocks & inline code
        s = s.replace(/```[\s\S]*?```/g, '');
        s = s.replace(/`([^`]+)`/g, '$1');
        // Strip markdown links & images
        s = s.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');
        s = s.replace(/!\[[^\]]*\]\([^\)]+\)/g, '');
        // Strip headers, bold, italics, blockquotes, hr
        s = s.replace(/^#{1,6}\s*/gm, '');
        s = s.replace(/\*\*([^*]+)\*\*/g, '$1');
        s = s.replace(/\*([^*]+)\*/g, '$1');
        s = s.replace(/^>\s*/gm, '');
        s = s.replace(/^[-\*=_]{3,}\s*$/gm, '');
        // Bullets & numbers to natural pauses
        s = s.replace(/^[\*\-\+]\s+/gm, '  ');
        s = s.replace(/^\d+\.\s+/gm, '  ');
        // Table bars
        s = s.replace(/\|[-:\s|]+\|/g, '');
        s = s.replace(/\|/g, ' , ');
        // Probabilities & percentages
        s = s.replace(/P\s*>\s*0?\.(\d+)/g, 'xác suất trên $1 phần trăm');
        s = s.replace(/P\s*<\s*0?\.(\d+)/g, 'xác suất dưới $1 phần trăm');
        s = s.replace(/(\d+)%/g, '$1 phần trăm');
        // Abbreviations
        for (const [k, v] of Object.entries(ABBR_MAP)) {
            const reg = new RegExp(`\\b${k}\\b`, 'g');
            s = s.replace(reg, v);
        }
        // Remove extraneous decorative symbols
        s = s.replace(/[^\w\s\.,;:!?'"()\-–—àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]/gi, ' ');
        s = s.replace(/[ \t]+/g, ' ');
        s = s.replace(/\n\s*\n+/g, '\n\n');
        return s.trim();
    }

    function splitIntoChunks(text, maxWords = 35) {
        const clean = cleanMarkdownForSpeech(text);
        if (!clean) return [];
        const sentences = clean.split(/(?<=[.!?])\s+|\n\n+/);
        const chunks = [];

        for (const sent of sentences) {
            const trimmed = sent.trim();
            if (!trimmed) continue;
            const words = trimmed.split(/\s+/);
            if (words.length <= maxWords) {
                chunks.push(trimmed);
            } else {
                const parts = trimmed.split(/(?<=[,;:])\s+/);
                let current = [];
                let count = 0;
                for (const p of parts) {
                    const pTrim = p.trim();
                    if (!pTrim) continue;
                    const pWords = pTrim.split(/\s+/);
                    if (count + pWords.length > maxWords && current.length) {
                        chunks.push(current.join(' '));
                        current = [pTrim];
                        count = pWords.length;
                    } else {
                        current.push(pTrim);
                        count += pWords.length;
                    }
                }
                if (current.length) chunks.push(current.join(' '));
            }
        }
        return chunks;
    }

    class ExecutiveAudioController {
        constructor() {
            this.synth = window.speechSynthesis;
            this.chunks = [];
            this.currentChunkIndex = 0;
            this.isPlaying = false;
            this.isPaused = false;
            this.activeTitle = 'Tham Mưu Điều Hành';
            this.activeMode = 'full';
            this.rate = 1.0;
            this.selectedVoice = null;
            this.availableVoices = [];
            this.rates = [0.85, 1.0, 1.25, 1.5];
            this.rateIndex = 1;

            this.initVoices();
            if (this.synth && this.synth.onvoiceschanged !== undefined) {
                this.synth.onvoiceschanged = () => this.initVoices();
            }
            this.ensureUI();
            this.populateVoiceSelect();
        }

        initVoices() {
            if (!this.synth) return;
            const voices = this.synth.getVoices();
            const vietnamese = voices.filter(v => v.lang && v.lang.toLowerCase().startsWith('vi'));
            const fallback = voices.filter(v => !vietnamese.includes(v));
            this.availableVoices = [...vietnamese, ...fallback];
            const previousUri = this.selectedVoice?.voiceURI;
            this.selectedVoice = this.availableVoices.find(v => v.voiceURI === previousUri)
                || vietnamese.find(v => v.default)
                || vietnamese[0]
                || voices.find(v => v.default)
                || voices[0]
                || null;
            this.populateVoiceSelect();
        }

        populateVoiceSelect() {
            const select = document.getElementById('exec-audio-voice-select');
            if (!select) return;
            select.innerHTML = '';
            this.availableVoices.forEach((voice, index) => {
                const option = document.createElement('option');
                option.value = String(index);
                option.textContent = `${voice.name} (${voice.lang})`;
                option.selected = voice.voiceURI === this.selectedVoice?.voiceURI;
                select.appendChild(option);
            });
            select.disabled = this.availableVoices.length === 0;
        }

        selectVoice(indexValue) {
            const index = Number(indexValue);
            if (Number.isInteger(index) && this.availableVoices[index]) {
                this.selectedVoice = this.availableVoices[index];
                if (this.isPlaying && !this.isPaused) {
                    this.synth.cancel();
                    this.speakCurrentChunk();
                }
            }
        }

        playAdvisory(respId, mode = 'full') {
            const entry = window.__advisoryStore[respId];
            if (!entry) {
                console.warn('Advisory entry not found for', respId);
                return;
            }
            const data = entry.data || {};
            const script = data.action_script || {};
            const syn = data.synthesis_result || {};

            let title = 'Tham Mưu Điều Hành';
            let speechText = '';

            const step1 = script.step_1_anchor || {};
            const step2 = script.step_2_deadline_consequence || {};
            const step3 = script.step_3_way_out_plan_b || {};
            const pos = script.position_analysis || syn.synthesis || '';

            if (mode === 'verbatim') {
                title = 'Kịch Bản Lời Thoại Đối Đáp';
                speechText = `Sau đây là Kịch bản lời thoại mẫu ba bước trong tình huống này. ${step1.title || 'Bước 1'}: ${step1.verbatim || ''}. ${step2.title || 'Bước 2'}: ${step2.verbatim || ''}. ${step3.title || 'Bước 3'}: ${step3.verbatim || ''}.`;
            } else if (mode === 'summary') {
                title = 'Tóm Tắt Tình Thế Điều Hành';
                speechText = `Bản tóm tắt tình thế điều hành. ${pos}. Chỉ đạo then chốt: ${step1.verbatim || ''}`;
            } else {
                title = 'Toàn Văn Tham Mưu Chiến Lược';
                const directives = (script.financial_and_operational_directives || []).join('. ');
                speechText = `Báo cáo tham mưu điều hành Nhân Thuật. Đánh giá vị thế và thế trận: ${pos}. Kịch bản lời thoại ba bước: ${step1.title || 'Bước 1'}: ${step1.verbatim || ''}. ${step2.title || 'Bước 2'}: ${step2.verbatim || ''}. ${step3.title || 'Bước 3'}: ${step3.verbatim || ''}. Chỉ đạo tác chiến vận hành: ${directives}.`;
            }

            this.activeTitle = title;
            this.activeMode = mode;
            this.playText(title, speechText);
        }

        playCouncil(councilData) {
            let data = councilData;
            if (typeof data === 'string') {
                try {
                    data = JSON.parse(decodeURIComponent(data));
                } catch (e) {
                    console.error('Failed to parse council data', e);
                    return;
                }
            }
            if (!data) return;

            const pitches = data.pitches || [];
            const debates = data.cross_debates || [];
            const matrix = data.decision_matrix || {};
            const parts = [
                'Hội đồng tham mưu bảy lăng kính Nhân Thuật.',
                'Giai đoạn một: Bảy bản tham mưu đầy đủ.'
            ];

            for (const p of pitches) {
                const name = p.title || p.agent_id || 'Thấu kính';
                parts.push(`Góc nhìn ${name}.`);
                if (p.situation_read) parts.push(`Đọc tình thế: ${p.situation_read}`);
                if (p.stance) parts.push(`Lập trường: ${p.stance}`);
                if ((p.assumptions || []).length) {
                    parts.push(`Các giả định đang dùng: ${p.assumptions.join('. ')}`);
                }
                if ((p.core_arguments || []).length) {
                    parts.push(`Các lập luận chính: ${p.core_arguments.join('. ')}`);
                }
                if ((p.recommended_actions || []).length) {
                    parts.push(`Hành động đề xuất: ${p.recommended_actions.join('. ')}`);
                }
                if ((p.evidence_needed || []).length) {
                    parts.push(`Bằng chứng cần kiểm: ${p.evidence_needed.join('. ')}`);
                }
                if (p.risk_warning) parts.push(`Cảnh báo rủi ro: ${p.risk_warning}`);
                if (p.confidence_note) parts.push(`Ghi chú độ tin cậy: ${p.confidence_note}`);
            }

            parts.push('Giai đoạn hai: Phản biện chéo.');
            for (const debate of debates) {
                parts.push(
                    `${debate.challenger_id || 'Một lăng kính'} phản biện ${debate.target_id || 'lăng kính đối diện'}: `
                    + `${debate.critique || ''}. Đề xuất hóa giải: ${debate.counter_recommendation || ''}`
                );
            }

            parts.push('Giai đoạn ba: Quyết sách hợp nhất và ma trận đồng thuận.');
            if (matrix.highest_consensus) {
                parts.push(`Chiến lược đồng thuận cao nhất: ${matrix.highest_consensus}`);
            }
            const plans = [
                ['Kế hoạch A', matrix.plan_a_primary],
                ['Kế hoạch B', matrix.plan_b_fallback],
                ['Kế hoạch C', matrix.plan_c_containment]
            ];
            for (const [label, plan] of plans) {
                if (!plan) continue;
                parts.push(`${label}: ${plan.name || ''}. ${plan.summary || ''}`);
                if ((plan.action_steps || []).length) {
                    parts.push(`Các bước thực hiện: ${plan.action_steps.join('. ')}`);
                }
            }
            if ((matrix.core_conflicts || []).length) {
                parts.push(`Mâu thuẫn cốt lõi: ${matrix.core_conflicts.join('. ')}`);
            }
            if ((matrix.critical_caveats || []).length) {
                parts.push(`Điều kiện thận trọng: ${matrix.critical_caveats.join('. ')}`);
            }
            if ((matrix.execution_directives || []).length) {
                parts.push(`Chỉ thị thực thi: ${matrix.execution_directives.join('. ')}`);
            }

            this.activeTitle = 'Hội Đồng 7 Lăng Kính';
            this.activeMode = 'council';
            this.playText(this.activeTitle, parts.join('. '));
        }

        playText(title, rawText) {
            if (!this.synth) {
                alert('Trình duyệt của bạn không hỗ trợ tính năng Web Speech API.');
                return;
            }

            this.stop();
            this.activeTitle = title || 'Bản Ghi Âm Tham Mưu';
            this.chunks = splitIntoChunks(rawText);
            this.currentChunkIndex = 0;

            if (!this.chunks.length) {
                console.warn('No text chunks to speak.');
                return;
            }

            this.showPlayer();
            this.speakCurrentChunk();
        }

        speakCurrentChunk() {
            if (this.currentChunkIndex >= this.chunks.length) {
                this.stop();
                return;
            }

            const chunkText = this.chunks[this.currentChunkIndex];
            const utterance = new SpeechSynthesisUtterance(chunkText);

            if (this.selectedVoice) {
                utterance.voice = this.selectedVoice;
            }
            utterance.lang = (this.selectedVoice && this.selectedVoice.lang) || 'vi-VN';
            utterance.rate = this.rate;
            utterance.pitch = 0.95; // Authoritative executive tone

            utterance.onstart = () => {
                this.isPlaying = true;
                this.isPaused = false;
                this.updateUI();
            };

            utterance.onend = () => {
                this.currentChunkIndex++;
                if (this.currentChunkIndex < this.chunks.length && this.isPlaying) {
                    this.speakCurrentChunk();
                } else {
                    this.stop();
                }
            };

            utterance.onerror = (e) => {
                console.error('Speech synthesis error:', e);
                this.currentChunkIndex++;
                if (this.currentChunkIndex < this.chunks.length && this.isPlaying) {
                    this.speakCurrentChunk();
                } else {
                    this.stop();
                }
            };

            this.synth.cancel(); // clear previous
            this.synth.speak(utterance);
            this.isPlaying = true;
            this.isPaused = false;
            this.updateUI();
        }

        togglePlay() {
            if (!this.isPlaying && this.chunks.length) {
                this.speakCurrentChunk();
            } else if (this.isPaused) {
                this.synth.resume();
                this.isPaused = false;
                this.isPlaying = true;
                this.updateUI();
            } else if (this.isPlaying) {
                this.synth.pause();
                this.isPaused = true;
                this.updateUI();
            }
        }

        seekRelative(delta) {
            // delta in chunks (-1 or +1)
            this.currentChunkIndex = Math.max(0, Math.min(this.chunks.length - 1, this.currentChunkIndex + delta));
            if (this.isPlaying) {
                this.synth.cancel();
                this.speakCurrentChunk();
            } else {
                this.updateUI();
            }
        }

        cycleRate() {
            this.rateIndex = (this.rateIndex + 1) % this.rates.length;
            this.rate = this.rates[this.rateIndex];
            const btn = document.getElementById('exec-audio-rate-btn');
            if (btn) btn.textContent = `${this.rate}x`;

            if (this.isPlaying && !this.isPaused) {
                this.synth.cancel();
                this.speakCurrentChunk();
            }
        }

        stop() {
            if (this.synth) this.synth.cancel();
            this.isPlaying = false;
            this.isPaused = false;
            this.currentChunkIndex = 0;
            this.updateUI();
            const player = document.getElementById('executive-audio-bar');
            if (player) player.classList.remove('active');
        }

        ensureUI() {
            if (document.getElementById('executive-audio-bar')) return;

            const bar = document.createElement('div');
            bar.id = 'executive-audio-bar';
            bar.className = 'executive-audio-bar';
            bar.innerHTML = `
                <div class="audio-bar-inner">
                    <div class="audio-meta">
                        <div class="audio-wave">
                            <span class="wave-bar"></span>
                            <span class="wave-bar"></span>
                            <span class="wave-bar"></span>
                            <span class="wave-bar"></span>
                        </div>
                        <div class="audio-text-group">
                            <div class="audio-title-line">
                                <span class="audio-badge" id="exec-audio-mode-badge">Tham mưu</span>
                                <strong id="exec-audio-title">Bản Ghi Âm Tham Mưu</strong>
                            </div>
                            <div class="audio-snippet" id="exec-audio-snippet">Đang nạp giọng đọc...</div>
                        </div>
                    </div>

                    <div class="audio-controls">
                        <label class="audio-voice-label" for="exec-audio-voice-select">Giọng</label>
                        <select class="audio-voice-select" id="exec-audio-voice-select" title="Chọn giọng đọc" onchange="window.NhanThuatAudio.selectVoice(this.value)"></select>
                        <button class="audio-ctrl-btn" id="exec-audio-prev-btn" title="Lùi lại 1 câu" onclick="window.NhanThuatAudio.seekRelative(-1)">
                            ◀
                        </button>
                        <button class="audio-ctrl-btn primary" id="exec-audio-play-btn" title="Phát / Dừng" onclick="window.NhanThuatAudio.togglePlay()">
                            ▶
                        </button>
                        <button class="audio-ctrl-btn" id="exec-audio-next-btn" title="Tiến tới 1 câu" onclick="window.NhanThuatAudio.seekRelative(1)">
                            ▶|
                        </button>
                        <button class="audio-ctrl-btn rate-pill" id="exec-audio-rate-btn" title="Chỉnh tốc độ đọc" onclick="window.NhanThuatAudio.cycleRate()">
                            1.0x
                        </button>
                        <button class="audio-ctrl-btn close-btn" id="exec-audio-close-btn" title="Đóng trình phát" onclick="window.NhanThuatAudio.stop()">
                            ×
                        </button>
                    </div>
                </div>
                <div class="audio-progress-rail">
                    <div class="audio-progress-fill" id="exec-audio-progress-fill"></div>
                </div>
            `;
            document.body.appendChild(bar);
        }

        showPlayer() {
            this.ensureUI();
            const player = document.getElementById('executive-audio-bar');
            if (player) player.classList.add('active');
        }

        updateUI() {
            const player = document.getElementById('executive-audio-bar');
            if (!player) return;

            const playBtn = document.getElementById('exec-audio-play-btn');
            const titleEl = document.getElementById('exec-audio-title');
            const snippetEl = document.getElementById('exec-audio-snippet');
            const modeBadge = document.getElementById('exec-audio-mode-badge');
            const progressFill = document.getElementById('exec-audio-progress-fill');
            const wave = player.querySelector('.audio-wave');

            if (titleEl) titleEl.textContent = this.activeTitle;

            const modeLabels = {
                'full': 'Toàn văn',
                'verbatim': 'Lời thoại',
                'summary': 'Tóm tắt',
                'council': '7 lăng kính'
            };
            if (modeBadge) modeBadge.textContent = modeLabels[this.activeMode] || 'Tham mưu';

            const currentText = this.chunks[this.currentChunkIndex] || '';
            if (snippetEl) snippetEl.textContent = currentText ? `"${currentText}"` : 'Hoàn tất nghe tham mưu.';

            if (playBtn) {
                if (this.isPlaying && !this.isPaused) {
                    playBtn.textContent = 'Ⅱ';
                    if (wave) wave.classList.add('playing');
                } else {
                    playBtn.textContent = '▶';
                    if (wave) wave.classList.remove('playing');
                }
            }

            if (progressFill) {
                const pct = this.chunks.length ? ((this.currentChunkIndex + 1) / this.chunks.length) * 100 : 0;
                progressFill.style.width = `${Math.min(100, Math.max(0, pct))}%`;
            }
        }
    }

    // Export to global scope
    window.NhanThuatAudio = new ExecutiveAudioController();
})();
