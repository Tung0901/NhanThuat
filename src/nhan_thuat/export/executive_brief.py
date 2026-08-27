"""
Executive Briefing Export Engine for NhanThuat (Milestone Phase 3).
Generates standardized Markdown and standalone printable HTML executive briefs
for board decisions, sparring transcripts, and department case studies.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from nhan_thuat.storage.models import CaseStudy, SparringMessage, SparringSession


class ExecutiveBriefExporter:
    """
    Exports decision briefing packages into Markdown and printable HTML formats.
    """

    def export_brief(
        self,
        title: str,
        situation_summary: str,
        philosophy_analysis: str,
        action_script: dict[str, Any],
        knowledge_units: list[dict[str, Any]],
        directives: list[str] | None = None,
        lessons_learned: list[str] | None = None,
        format: str = "markdown",
    ) -> str:
        """Export executive decision brief in Markdown or HTML."""
        if format.lower() == "html":
            return self._render_html_brief(
                title=title,
                situation_summary=situation_summary,
                philosophy_analysis=philosophy_analysis,
                action_script=action_script,
                knowledge_units=knowledge_units,
                directives=directives or [],
                lessons_learned=lessons_learned or [],
            )
        return self._render_markdown_brief(
            title=title,
            situation_summary=situation_summary,
            philosophy_analysis=philosophy_analysis,
            action_script=action_script,
            knowledge_units=knowledge_units,
            directives=directives or [],
            lessons_learned=lessons_learned or [],
        )

    def export_case_study(self, case: CaseStudy, format: str = "markdown") -> str:
        """Export a CaseStudy instance."""
        script = case.decision_script
        pos_analysis = script.get("position_analysis", "Căn cứ hợp đồng và kỷ luật vận hành.")
        units = [{"id": tag, "title": tag, "domain": case.domain} for tag in case.tags]

        return self.export_brief(
            title=case.title,
            situation_summary=case.context_description,
            philosophy_analysis=pos_analysis,
            action_script=script,
            knowledge_units=units,
            directives=script.get("financial_and_operational_directives", []),
            lessons_learned=case.lessons_learned,
            format=format,
        )

    def export_sparring_session(
        self,
        session: SparringSession,
        messages: list[SparringMessage],
        format: str = "markdown",
    ) -> str:
        """Export a complete multi-turn Sparring Session transcript."""
        if format.lower() == "html":
            return self._render_sparring_html(session, messages)

        lines = [
            f"# BIÊN BẢN ĐẤU TRÍ ĐIỀU HÀNH - {session.title.upper()}",
            f"- **Mã phiên:** `{session.id}`",
            f"- **Lăng kính triết học:** `{session.philosophy_lens}`",
            f"- **Thời gian khởi tạo:** {session.created_at}",
            f"- **Trạng thái:** `{session.status.upper()}`",
            "",
            "---",
            "",
            "## DIỄN BIẾN PHIÊN ĐỐI THOẠI PHẢN BIỆN",
            "",
        ]

        for i, msg in enumerate(messages, 1):
            role_badge = "👔 CHỦ TỊCH / NGƯỜI DÙNG" if msg.role == "user" else ("⚔️ CỐ VẤN ĐẤU TRÍ NHÂN THUẬT" if msg.role == "assistant" else "⚙️ HỆ THỐNG")
            lines.append(f"### Lượt #{i} • {role_badge} ({msg.created_at})")
            lines.append(msg.content)
            if msg.matched_unit_ids:
                lines.append(f"\n*Căn cứ tri thức viện dẫn: {', '.join(msg.matched_unit_ids)}*")
            lines.append("\n---\n")

        return "\n".join(lines)

    def _render_markdown_brief(
        self,
        title: str,
        situation_summary: str,
        philosophy_analysis: str,
        action_script: dict[str, Any],
        knowledge_units: list[dict[str, Any]],
        directives: list[str],
        lessons_learned: list[str],
    ) -> str:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        lines = [
            f"# BẢN THAM MƯU & CHỈ ĐẠO ĐIỀU HÀNH: {title.upper()}",
            f"- **Ngày phát hành:** {now}",
            "- **Phân loại bảo mật:** LƯU HÀNH NỘI BỘ • BUSINESSOS EXECUTIVE",
            "",
            "---",
            "",
            "## 1. TÓM TẮT TÌNH HUỐNG HIỆN TRƯỜNG / TÁC NGHIỆP",
            situation_summary,
            "",
            "## 2. NHẬN ĐỊNH VỊ THẾ & CHẨN ĐOÁN TRIẾT HỌC",
            philosophy_analysis,
            "",
            "## 3. KỊCH BẢN ĐỐI THOẠI 3 BƯỚC THỰC CHIẾN (ACTION SCRIPT)",
        ]

        step1 = action_script.get("step_1_anchor", action_script.get("step_1", {}))
        step2 = action_script.get("step_2_deadline_consequence", action_script.get("step_2", {}))
        step3 = action_script.get("step_3_way_out_plan_b", action_script.get("step_3", {}))

        def _get_txt(st: Any) -> str:
            if isinstance(st, dict):
                return f"**{st.get('title', 'Bước')}:**\n> {st.get('verbatim', '')}"
            return f"> {st}"

        lines.extend([
            f"### Bước 1: Thiết lập Vị thế & Căn cứ Pháp lý / Quy chuẩn\n{_get_txt(step1)}\n",
            f"### Bước 2: Ấn định Thời hạn & Chế tài Ràng buộc\n{_get_txt(step2)}\n",
            f"### Bước 3: Mở Đường lui & Kích hoạt Phương án Dự phòng (Plan B)\n{_get_txt(step3)}\n",
        ])

        if directives:
            lines.extend([
                "## 4. CHỈ THỊ TÀI CHÍNH & VẬN HÀNH BẮT BUỘC",
                *[f"- {d}" for d in directives],
                "",
            ])

        if knowledge_units:
            lines.extend([
                "## 5. CĂN CỨ TRI THỨC NHÂN THUẬT ĐÃ KIỂM ĐỊNH (FOUNDATIONS)",
                *[f"- **`{u.get('id', u.get('unit_id', ''))}`** - {u.get('title', '')} *({u.get('domain', '')})*" for u in knowledge_units],
                "",
            ])

        if lessons_learned:
            lines.extend([
                "## 6. BÀI HỌC QUẢN TRỊ RÚT RA (LESSONS LEARNED)",
                *[f"- {l}" for l in lessons_learned],
                "",
            ])

        return "\n".join(lines)

    def _render_html_brief(
        self,
        title: str,
        situation_summary: str,
        philosophy_analysis: str,
        action_script: dict[str, Any],
        knowledge_units: list[dict[str, Any]],
        directives: list[str],
        lessons_learned: list[str],
    ) -> str:
        now = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
        
        step1_title = action_script.get("step_1_anchor", {}).get("title", "Bước 1: Thiết lập vị thế") if isinstance(action_script.get("step_1_anchor"), dict) else "Bước 1: Thiết lập vị thế"
        step1_verb = action_script.get("step_1_anchor", {}).get("verbatim", str(action_script.get("step_1", ""))) if isinstance(action_script.get("step_1_anchor"), dict) else str(action_script.get("step_1", ""))
        
        step2_title = action_script.get("step_2_deadline_consequence", {}).get("title", "Bước 2: Ấn định thời hạn") if isinstance(action_script.get("step_2_deadline_consequence"), dict) else "Bước 2: Ấn định thời hạn"
        step2_verb = action_script.get("step_2_deadline_consequence", {}).get("verbatim", str(action_script.get("step_2", ""))) if isinstance(action_script.get("step_2_deadline_consequence"), dict) else str(action_script.get("step_2", ""))

        step3_title = action_script.get("step_3_way_out_plan_b", {}).get("title", "Bước 3: Mở đường lui & Plan B") if isinstance(action_script.get("step_3_way_out_plan_b"), dict) else "Bước 3: Mở đường lui & Plan B"
        step3_verb = action_script.get("step_3_way_out_plan_b", {}).get("verbatim", str(action_script.get("step_3", ""))) if isinstance(action_script.get("step_3_way_out_plan_b"), dict) else str(action_script.get("step_3", ""))

        directives_html = "".join([f"<li style='margin-bottom:8px;'><strong>{d.split(':')[0] if ':' in d else ''}</strong>{d.split(':', 1)[1] if ':' in d else d}</li>" for d in directives])
        units_html = "".join([f"<div style='background:#f8fafc; border:1px solid #e2e8f0; padding:10px 14px; border-radius:8px; margin-bottom:8px;'><span style='font-family:monospace; font-weight:bold; color:#d97706;'>{u.get('id', u.get('unit_id', ''))}</span> - <span style='font-weight:600;'>{u.get('title', '')}</span> <span style='color:#64748b; font-size:12px;'>({u.get('domain', '')})</span></div>" for u in knowledge_units])
        lessons_html = "".join([f"<li style='margin-bottom:6px;'>{l}</li>" for l in lessons_learned])

        return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>BẢN THAM MƯU ĐIỀU HÀNH - {title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');
        body {{ font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px auto; max-width: 900px; color: #0f172a; line-height: 1.65; background: #ffffff; }}
        .header-box {{ border-bottom: 3px solid #f59e0b; padding-bottom: 20px; margin-bottom: 30px; }}
        .badge {{ background: #0f172a; color: #f59e0b; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }}
        h1 {{ font-family: 'Playfair Display', serif; font-size: 26px; color: #0f172a; margin: 12px 0 6px 0; }}
        .meta-line {{ color: #64748b; font-size: 13px; }}
        .section-title {{ font-size: 16px; font-weight: 700; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px; border-left: 4px solid #f59e0b; padding-left: 10px; margin: 26px 0 12px 0; }}
        .callout-box {{ background: #fffbeb; border: 1px solid #fef3c7; padding: 16px 20px; border-radius: 12px; font-style: italic; color: #92400e; margin-bottom: 16px; }}
        .step-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; padding: 14px 18px; border-radius: 8px; margin-bottom: 12px; }}
        .step-title {{ font-weight: 700; color: #1e3a8a; margin-bottom: 6px; font-size: 14px; }}
        .step-verbatim {{ font-size: 14px; color: #1e293b; font-style: italic; line-height: 1.6; }}
        .directives-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; padding: 16px 20px; border-radius: 12px; color: #166534; }}
        @media print {{
            body {{ margin: 20px; max-width: 100%; font-size: 12pt; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header-box">
        <span class="badge">BusinessOS Executive Briefing • NhanThuat Core</span>
        <h1>{title}</h1>
        <div class="meta-line">Thời gian phát hành: {now} • Phân loại: LƯU HÀNH NỘI BỘ BAN ĐIỀU HÀNH</div>
    </div>

    <div class="section-title">1. Tóm Tắt Tình Huống Hiện Trường / Vận Hành</div>
    <p style="font-size:15px; color:#334155;">{situation_summary}</p>

    <div class="section-title">2. Nhận Định Vị Thế & Chẩn Đoán Lãnh Đạo</div>
    <div class="callout-box">{philosophy_analysis}</div>

    <div class="section-title">3. Kịch Bản Đối Thoại 3 Bước Thực Chiến (Verbatim Script)</div>
    <div class="step-card">
        <div class="step-title">{step1_title}</div>
        <div class="step-verbatim">"{step1_verb}"</div>
    </div>
    <div class="step-card" style="border-left-color: #f59e0b;">
        <div class="step-title" style="color: #b45309;">{step2_title}</div>
        <div class="step-verbatim">"{step2_verb}"</div>
    </div>
    <div class="step-card" style="border-left-color: #10b981;">
        <div class="step-title" style="color: #047857;">{step3_title}</div>
        <div class="step-verbatim">"{step3_verb}"</div>
    </div>

    {f'''<div class="section-title">4. Chỉ Thị Tài Chính & Vận Hành Bắt Buộc</div>
    <div class="directives-box"><ul style="margin:0; padding-left:20px;">{directives_html}</ul></div>''' if directives else ''}

    {f'''<div class="section-title">5. Căn Cứ Tri Thức Đã Kiểm Định</div>
    <div>{units_html}</div>''' if knowledge_units else ''}

    {f'''<div class="section-title">6. Bài Học Quản Trị Rút Ra</div>
    <ul style="color:#334155; padding-left:20px;">{lessons_html}</ul>''' if lessons_learned else ''}

    <div style="margin-top: 40px; padding-top: 14px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; text-align: center;">
        Hệ thống Tri thức Nhân Thuật • BusinessOS Executive Kernel 1.1.0 • Xuất bản tự động
    </div>
</body>
</html>"""

    def _render_sparring_html(self, session: SparringSession, messages: list[SparringMessage]) -> str:
        now = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
        msgs_html = ""
        for i, msg in enumerate(messages, 1):
            is_user = msg.role == "user"
            bg = "#f8fafc" if is_user else "#0f172a"
            color = "#0f172a" if is_user else "#ffffff"
            border = "#e2e8f0" if is_user else "#f59e0b"
            role_text = "👔 CHỦ TỊCH / NGƯỜI DÙNG" if is_user else "⚔️ CỐ VẤN ĐẤU TRÍ NHÂN THUẬT"
            
            msgs_html += f"""
            <div style="background:{bg}; color:{color}; border:1px solid {border}; border-radius:12px; padding:16px 20px; margin-bottom:16px;">
                <div style="font-size:12px; font-weight:700; color:{'#64748b' if is_user else '#fbbf24'}; margin-bottom:8px;">
                    Lượt #{i} • {role_text} ({msg.created_at})
                </div>
                <div style="font-size:14px; line-height:1.6; white-space:pre-wrap;">{msg.content}</div>
                {f"<div style='margin-top:10px; font-size:11px; color:#94a3b8;'>Tri thức viện dẫn: {', '.join(msg.matched_unit_ids)}</div>" if msg.matched_unit_ids else ""}
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>BIÊN BẢN ĐẤU TRÍ - {session.title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px auto; max-width: 900px; color: #0f172a; line-height: 1.6; }}
        h1 {{ border-bottom: 2px solid #f59e0b; padding-bottom: 10px; font-size: 24px; }}
    </style>
</head>
<body>
    <h1>BIÊN BẢN ĐẤU TRÍ ĐIỀU HÀNH: {session.title}</h1>
    <p style="color:#64748b; font-size:13px;">Mã phiên: <code>{session.id}</code> • Lăng kính: <strong>{session.philosophy_lens}</strong> • Khởi tạo: {session.created_at}</p>
    <hr style="border:none; border-top:1px solid #e2e8f0; margin:20px 0;">
    {msgs_html}
</body>
</html>"""
