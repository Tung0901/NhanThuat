"""
BusinessOS API Gateway Server Main Application.
Exposes REST API endpoints for BusinessOS Kernel, SalesOS Plugin, CPQ Quote Generator, 5 Digital Books Reader & PDF Exporter, and Web App Dashboard:
- GET  / (Web App Dashboard HTML)
- POST /api/v1/nhan-thuat/analyze
- GET  /api/v1/salesos/leads
- POST /api/v1/salesos/cpq/generate-quote
- POST /api/v1/salesos/cpq/export-pdf
- GET  /api/v1/knowledge/books/{book_name}
- GET  /api/v1/knowledge/books/{book_name}/export-pdf
- GET  /health
- GET  /version
- GET  /knowledge/units/{unit_id}
- GET  /knowledge/units/{unit_id}/export?format=json|markdown
- GET  /knowledge/domains/{domain_slug}
- POST /knowledge/query
- POST /runtime/execute
- GET  /runtime/executions/{correlation_id}/provenance
- POST /salesos/leads
- GET  /salesos/leads/{lead_id}
- GET  /salesos/health
"""

import json
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from backend.app.engine.nhan_thuat_api import process_nhan_thuat_analysis
from backend.app.engine.runtime import BusinessOSRuntimeOrchestrator, RuntimeRequestPayload
from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.public.v1.adapter import KnowledgeEngineAdapterV1
from nhan_thuat.public.v1.contracts import KnowledgeQuery
from salesos_pack.plugin import SalesOSPlugin

from dotenv import load_dotenv
load_dotenv()

# Global Engine & Plugin Instances
runtime_orchestrator = BusinessOSRuntimeOrchestrator()
knowledge_engine = KnowledgeEngine()
nhan_thuat_public_v1 = KnowledgeEngineAdapterV1(knowledge_engine)
salesos_plugin = SalesOSPlugin()

# Execution History Store for Provenance Lookup
execution_provenance_store: dict[str, dict[str, Any]] = {}

STATIC_DIR = Path(__file__).resolve().parent / "static"
DOCS_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent / "docs" / "knowledge"


def export_unit(engine: KnowledgeEngine, unit_id: str, fmt: str = "markdown") -> dict[str, Any]:
    """Export a knowledge unit as JSON or Markdown (EPIC 6)."""
    unit_res = engine.resolve_latest_active_unit(unit_id)
    if unit_res["status"] != "success":
        return {"status": "error", "code": 404, "payload": unit_res}
    raw = unit_res["unit"].raw_data
    if fmt == "json":
        return {"status": "success", "code": 200, "payload": {"status": "success", "format": "json", "unit": raw}}
    lines = [
        f"# {raw.get('title', unit_id)}",
        f"- ID: {raw.get('id', unit_id)}",
        f"- Type: {raw.get('type', '')}",
        f"- Status: {raw.get('status', '')}",
        f"- Domain: {raw.get('primary_domain', '')}",
        f"- Domain Area: {raw.get('domain_area', '')}",
        "",
        "## Summary",
        str(raw.get("summary", "")),
        "",
        "## Definition",
        str(raw.get("definition", "")),
    ]
    return {"status": "success", "code": 200, "payload": "\n".join(lines)}


class BusinessOSGatewayHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for BusinessOS API Gateway and Web App Dashboard."""

    def _send_json_response(self, status_code: int, data: dict[str, Any]) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        response_bytes = json.dumps(data, indent=2, default=str, ensure_ascii=False).encode("utf-8")
        self.wfile.write(response_bytes)

    def _send_html_response(self, status_code: int, html_content: str) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # 0. Serve Landing Page, App Dashboard, and Static Assets
        if path == "/" or path == "/index.html":
            index_file = Path(__file__).resolve().parent.parent.parent / "index.html"
            if index_file.exists():
                self._send_html_response(200, index_file.read_text(encoding="utf-8"))
            else:
                self._send_html_response(404, "<h1>Landing HTML static file not found</h1>")
            return

        if path == "/app" or path == "/dashboard":
            app_file = Path(__file__).resolve().parent.parent.parent / "frontend" / "app.html"
            if app_file.exists():
                self._send_html_response(200, app_file.read_text(encoding="utf-8"))
            else:
                self._send_html_response(404, "<h1>App HTML not found</h1>")
            return

        if path.startswith("/css/") or path.startswith("/js/"):
            asset_file = Path(__file__).resolve().parent.parent.parent / "frontend" / path.lstrip("/")
            content_type = "text/css" if path.endswith(".css") else "application/javascript"
            if asset_file.exists():
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.end_headers()
                self.wfile.write(asset_file.read_bytes())
            else:
                self.send_response(404)
                self.end_headers()
            return

        # 1. Health & Version Endpoints
        if path == "/health" or path == "/salesos/health":
            self._send_json_response(200, {
                "status": "HEALTHY",
                "kernel_version": "1.1.0",
                "knowledge_units_indexed": len(knowledge_engine.units_by_id),
                "salesos_plugin": salesos_plugin.health_check(),
            })
            return

        if path == "/version":
            self._send_json_response(200, {
                "system": "BusinessOS Kernel",
                "version": "1.1.0",
                "status": "FROZEN_ACTIVE",
                "api_spec": "v1.0",
            })
            return

        # 2. 5 Digital Books Export PDF: GET /api/v1/knowledge/books/{book_name}/export-pdf
        if path.startswith("/api/v1/knowledge/books/") and path.endswith("/export-pdf"):
            book_name = path.replace("/api/v1/knowledge/books/", "").replace("/export-pdf", "")
            if not book_name.endswith(".md"):
                book_name += ".md"

            book_file = DOCS_KNOWLEDGE_DIR / book_name
            if book_file.exists():
                text = book_file.read_text(encoding="utf-8")
                title = text.splitlines()[0].replace("#", "").strip() if text.startswith("#") else book_name
                html_doc = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{title} - BUSINESSOS DIGITAL BOOK</title>
    <style>
        body {{ font-family: 'Plus Jakarta Sans', Arial, sans-serif; margin: 40px; color: #0f172a; line-height: 1.7; }}
        h1 {{ color: #0f172a; border-bottom: 3px solid #f59e0b; padding-bottom: 12px; font-size: 24px; }}
        h2 {{ color: #1e293b; margin-top: 24px; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; font-size: 18px; }}
        blockquote {{ background: #f8fafc; border-left: 4px solid #f59e0b; margin: 16px 0; padding: 12px 16px; font-style: italic; color: #334155; }}
        pre {{ background: #0f172a; color: #34d399; padding: 16px; border-radius: 8px; font-family: monospace; overflow-x: auto; }}
        .header-meta {{ background: #fffbe0; border: 1px solid #fef08a; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="header-meta">
        <strong>ẤN BẢN SÁCH SỐ TRI THỨC NHÂN THUẬT CORE • BUSINESSOS</strong><br>
        Tài liệu lưu hành nội bộ - Mã sách: {book_name}
    </div>
    <pre style="background:transparent; color:#0f172a; font-family:inherit; whitespace:pre-wrap;">{text}</pre>
</body>
</html>"""
                self._send_html_response(200, html_doc)
            else:
                self._send_json_response(404, {"status": "error", "message": f"Book file '{book_name}' not found."})
            return

        # 3. 5 Digital Books Reader API: GET /api/v1/knowledge/books/{book_name}
        if path.startswith("/api/v1/knowledge/books/"):
            book_name = path.replace("/api/v1/knowledge/books/", "")
            if not book_name.endswith(".md"):
                book_name += ".md"

            book_file = DOCS_KNOWLEDGE_DIR / book_name
            if book_file.exists():
                text = book_file.read_text(encoding="utf-8")
                title = text.splitlines()[0].replace("#", "").strip() if text.startswith("#") else book_name
                self._send_json_response(200, {
                    "status": "success",
                    "book_name": book_name,
                    "title": title,
                    "content": text,
                })
            else:
                self._send_json_response(404, {"status": "error", "message": f"Book file '{book_name}' not found."})
            return

        # 4. SalesOS Active Leads Pipeline: GET /api/v1/salesos/leads
        if path == "/api/v1/salesos/leads":
            leads_data = [
                {
                    "lead_id": "LEAD-NB-2026",
                    "project_name": "Dự án Công trình Nhà Bè (Giai đoạn 2)",
                    "client_name": "Công ty Cổ phần Đầu tư Xây dựng Nam Sài Gòn",
                    "contract_value_est": "12,500,000,000 VNĐ",
                    "status": "NEGOTIATING",
                    "primary_issue": "Chậm tiến độ vật tư / Áp dụng phạt chế tài",
                    "rhetoric_recommended": "LEGALISM & RHETORIC",
                },
                {
                    "lead_id": "LEAD-TD-2026",
                    "project_name": "Biệt thự Cao cấp Thảo Điền (Quận 2)",
                    "client_name": "Tập đoàn Phát triển Đô thị Quốc tế",
                    "contract_value_est": "4,800,000,000 VNĐ",
                    "status": "QUOTE_SENT",
                    "primary_issue": "Khách hàng chê báo giá đắt hơn đối thủ 15%",
                    "rhetoric_recommended": "RHETORIC (Reframing TCO 3 năm)",
                },
                {
                    "lead_id": "LEAD-LA-2026",
                    "project_name": "Dự án Xưởng sản xuất Nhà máy Long An",
                    "client_name": "Công ty TNHH Công nghiệp Nặng Việt Mỹ",
                    "contract_value_est": "18,200,000,000 VNĐ",
                    "status": "CONTRACT_PENDING",
                    "primary_issue": "Tổ đội thi công đòi tăng đơn giá đột xuất",
                    "rhetoric_recommended": "XUNZI & LEGALISM",
                }
            ]
            self._send_json_response(200, {
                "status": "success",
                "total_leads": len(leads_data),
                "leads": leads_data,
            })
            return

        # NhanThuat Public Contract V1 Endpoints
        if path.startswith("/api/v1/knowledge/units/"):
            unit_id = path.split("/api/v1/knowledge/units/")[1]
            unit_res = nhan_thuat_public_v1.get_unit(unit_id)
            if unit_res:
                import dataclasses
                unit_dict = dataclasses.asdict(unit_res) if dataclasses.is_dataclass(unit_res) else unit_res
                self._send_json_response(200, {"status": "success", "unit": unit_dict})
            else:
                self._send_json_response(404, {"status": "error", "message": "Unit not found"})
            return

        if path == "/api/v1/knowledge/units":
            units = list(knowledge_engine.units_by_id.values())
            self._send_json_response(200, {
                "status": "success",
                "count": len(units),
                "units": [{"id": u.unit_id, "title": u.title, "domain": u.domain, "type": u.unit_type, "summary": u.raw_data.get("summary", "")} for u in units],
            })
            return

        if path.startswith("/api/v1/knowledge/domains/"):
            domain_slug = path.split("/api/v1/knowledge/domains/")[1]
            units = nhan_thuat_public_v1.list_domain_units(domain_slug)
            self._send_json_response(200, {
                "status": "success",
                "domain": domain_slug,
                "count": len(units),
                "units": [u.__dict__ for u in units],
            })
            return

        if path == "/api/v1/capabilities":
            capabilities = nhan_thuat_public_v1.list_capabilities()
            self._send_json_response(200, {
                "status": "success",
                "capabilities": [c.__dict__ for c in capabilities],
            })
            return

        if path == "/api/v1/contract":
            contract = nhan_thuat_public_v1.get_contract_metadata()
            self._send_json_response(200, {
                "status": "success",
                "contract_version": contract.__dict__,
            })
            return

# 4b. Knowledge Unit Export: GET /knowledge/units/{unit_id}/export?format=json|markdown
        if path.startswith("/knowledge/units/") and path.endswith("/export"):
            unit_id = path.split("/knowledge/units/")[1].replace("/export", "")
            fmt = (parse_qs(parsed_url.query).get("format") or ["markdown"])[0]
            export_res = export_unit(knowledge_engine, unit_id, fmt)
            if export_res["status"] == "success":
                if isinstance(export_res["payload"], str):
                    self._send_html_response(200, export_res["payload"])
                else:
                    self._send_json_response(200, export_res["payload"])
            else:
                self._send_json_response(404, export_res["payload"])
            return

        # 5. Knowledge Unit Lookup: GET /knowledge/units/{unit_id}
        if path.startswith("/knowledge/units/"):
            unit_id = path.split("/knowledge/units/")[1]
            unit_res = knowledge_engine.resolve_latest_active_unit(unit_id)
            if unit_res["status"] == "success":
                self._send_json_response(200, unit_res)
            else:
                self._send_json_response(404, unit_res)
            return

        # 6. Knowledge Domain Lookup: GET /knowledge/domains/{domain_slug}
        if path.startswith("/knowledge/domains/"):
            domain_slug = path.split("/knowledge/domains/")[1]
            units = knowledge_engine.query(domain=domain_slug)
            self._send_json_response(200, {
                "status": "success",
                "domain": domain_slug,
                "count": len(units),
                "units": [u.unit_id for u in units],
            })
            return

        # 7. Runtime Execution Provenance: GET /runtime/executions/{correlation_id}/provenance
        if path.startswith("/runtime/executions/") and path.endswith("/provenance"):
            parts = path.split("/")
            correlation_id = parts[3]
            prov = execution_provenance_store.get(correlation_id)
            if prov:
                self._send_json_response(200, {
                    "status": "success",
                    "correlation_id": correlation_id,
                    "provenance": prov,
                })
            else:
                self._send_json_response(404, {
                    "status": "error",
                    "error_code": "PROVENANCE_NOT_FOUND",
                    "message": f"No execution provenance recorded for correlation ID '{correlation_id}'.",
                })
            return

        # 8. SalesOS Lead Retrieval: GET /salesos/leads/{lead_id}
        if path.startswith("/salesos/leads/"):
            lead_id = path.split("/salesos/leads/")[1]
            matching_lead = next(
                (lead for lead in salesos_plugin.capability.lead_repository if lead.object_id == lead_id),
                None
            )
            if matching_lead:
                self._send_json_response(200, {
                    "status": "SUCCESS",
                    "lead": matching_lead.__dict__,
                })
            else:
                self._send_json_response(404, {
                    "status": "NOT_FOUND",
                    "error_code": "LEAD_NOT_FOUND",
                    "message": f"Lead with ID '{lead_id}' not found.",
                })
            return

        self._send_json_response(404, {"error": "Endpoint not found"})

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception as e:  # noqa: BLE001 - malformed client payload
            self._send_json_response(400, {
                "status": "VALIDATION_ERROR",
                "error_code": "INVALID_JSON_PAYLOAD",
                "message": f"Malformed JSON payload: {e!s}",
            })
            return

        # 0. Web App Dashboard API Endpoint: POST /api/v1/nhan-thuat/analyze
        if path == "/api/v1/nhan-thuat/analyze":
            scenario_text = payload.get("scenario_text", "")
            scenario_type_hint = payload.get("scenario_type", "general")

            if not scenario_text:
                self._send_json_response(400, {
                    "status": "VALIDATION_ERROR",
                    "error_code": "MISSING_SCENARIO_TEXT",
                    "message": "Field 'scenario_text' is required.",
                })
                return

            try:
                result = process_nhan_thuat_analysis(scenario_text, scenario_type_hint)
                self._send_json_response(200, result)
            except Exception as e:
                self._send_json_response(500, {
                    "status": "INTERNAL_ERROR",
                    "error_code": "ANALYSIS_FAILED",
                    "message": f"Server error: {e!s}"
                })
            return

        # 1. CPQ Quote Generator: POST /api/v1/salesos/cpq/generate-quote
        if path == "/api/v1/salesos/cpq/generate-quote":
            client_name = payload.get("client_name", "Công ty Cổ phần Đầu tư Xây dựng Nam Sài Gòn")
            project_name = payload.get("project_name", "Dự án Công trình Nhà Bè")
            items = payload.get("items", [
                {"name": "Vật tư bê tông chịu lực M300", "qty": 500, "unit_price": 1450000},
                {"name": "Tổ đội thi công lắp dựng khung thép", "qty": 1, "unit_price": 250000000},
                {"name": "Gói bảo trì & Giám sát chất lượng 12 tháng", "qty": 1, "unit_price": 85000000},
            ])
            discount_pct = float(payload.get("discount_pct", 3.0))

            subtotal = sum(item["qty"] * item["unit_price"] for item in items)
            discount_amount = subtotal * (discount_pct / 100.0)
            net_before_vat = subtotal - discount_amount
            vat_amount = net_before_vat * 0.08
            total_amount = net_before_vat + vat_amount

            quote_id = f"CPQ-QUOTE-{uuid.uuid4().hex[:6].upper()}"

            self._send_json_response(200, {
                "status": "success",
                "quote_id": quote_id,
                "client_name": client_name,
                "project_name": project_name,
                "items": items,
                "subtotal": subtotal,
                "discount_pct": discount_pct,
                "discount_amount": discount_amount,
                "net_before_vat": net_before_vat,
                "vat_rate": "8%",
                "vat_amount": vat_amount,
                "total_amount": total_amount,
                "rhetoric_objection_strategy": {
                    "price_reframing": "Đã nhúng cấu trúc TCO 3 năm. Nếu khách hàng so sánh với đối thủ giá rẻ, dùng luận điểm bóc tách rủi ro gián đoạn hiện trường.",
                    "closing_incentive": f"Chiết khấu {discount_pct}% áp dụng khi duyệt hợp đồng trước 17h00 thứ 6.",
                }
            })
            return

        # 2. CPQ Export PDF / Printable HTML: POST /api/v1/salesos/cpq/export-pdf
        if path == "/api/v1/salesos/cpq/export-pdf":
            quote_id = payload.get("quote_id", "CPQ-QUOTE-DEMO")
            client_name = payload.get("client_name", "Công ty Cổ phần Đầu tư Xây dựng Nam Sài Gòn")
            project_name = payload.get("project_name", "Dự án Công trình Nhà Bè")
            total_amount = payload.get("total_amount", 1053000000)

            html_doc = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>BÁO GIÁ DỰ ÁN BUSINESSOS CPQ - {quote_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #1e293b; }}
        h1 {{ color: #0f172a; border-bottom: 2px solid #f59e0b; padding-bottom: 10px; }}
        .meta {{ margin-bottom: 20px; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 12px; text-align: left; }}
        th {{ background: #0f172a; color: #ffffff; }}
        .total {{ text-align: right; font-size: 18px; font-weight: bold; color: #059669; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>BÁO GIÁ THƯƠNG MẠI & DỰ TOÁN THI CÔNG BUSINESSOS CPQ</h1>
    <div class="meta">
        <p><strong>Mã Báo Giá:</strong> {quote_id}</p>
        <p><strong>Dự Án:</strong> {project_name}</p>
        <p><strong>Khách Hàng:</strong> {client_name}</p>
        <p><strong>Ngày Phát Hành:</strong> 23/07/2026</p>
    </div>
    <h2>BẢNG CHI TIẾT DANH MỤC THI CÔNG & VẬT TƯ</h2>
    <table>
        <thead>
            <tr><th>STT</th><th>Danh Mục Công Việc / Vật Tư</th><th>Số Lượng</th><th>Đơn Giá (VNĐ)</th><th>Thành Tiền (VNĐ)</th></tr>
        </thead>
        <tbody>
            <tr><td>1</td><td>Vật tư bê tông chịu lực M300</td><td>500 m3</td><td>1,450,000</td><td>725,000,000</td></tr>
            <tr><td>2</td><td>Tổ đội thi công lắp dựng khung thép</td><td>1 Gói</td><td>250,000,000</td><td>250,000,000</td></tr>
            <tr><td>3</td><td>Gói bảo trì & Giám sát chất lượng 12 tháng</td><td>1 Gói</td><td>85,000,000</td><td>85,000,000</td></tr>
        </tbody>
    </table>
    <div class="total">
        TỔNG GIÁ TRỊ THANH TOÁN (ĐÃ BAO GỒM VAT 8%): {total_amount:,.0f} VNĐ
    </div>
    <div style="margin-top: 40px; font-size: 12px; color: #64748b;">
        * Báo giá có hiệu lực trong vòng 15 ngày. Phát hành bởi BusinessOS Executive CPQ Engine.
    </div>
</body>
</html>"""
            self._send_html_response(200, html_doc)
            return

        # NhanThuat Public Contract V1 POST Endpoints
        if path == "/api/v1/knowledge/query":
            q_domain = payload.get("domain")
            q_type = payload.get("unit_type")
            q_tag = payload.get("tag")
            q_status = payload.get("status")
            q_limit = payload.get("limit", 100)
            query = KnowledgeQuery(domain_slug=q_domain, unit_type=q_type, tag=q_tag, status=q_status, limit=q_limit)
            result = nhan_thuat_public_v1.query_knowledge(query)
            # Serialize dataclass manually since json default doesn't handle all nested dataclasses perfectly
            self._send_json_response(200, {
                "status": "success",
                "query_filter": result.query_filter,
                "total_matches": result.total_matches,
                "units": [u.__dict__ for u in result.units],
                "contract_version": result.contract_version.__dict__,
            })
            return

        if path == "/api/v1/reason":
            from nhan_thuat.public.v1.contracts import ReasoningRequest
            from nhan_thuat.public.v1.errors import PublicError
            req = ReasoningRequest(
                session_id=payload.get("session_id", ""),
                correlation_id=payload.get("correlation_id", ""),
                intent_action=payload.get("intent_action", ""),
                scenario_type=payload.get("scenario_type", ""),
                context_stack=payload.get("context_stack", {}),
                requested_knowledge_ids=payload.get("requested_knowledge_ids", [])
            )
            try:
                res = nhan_thuat_public_v1.reason(req)
                self._send_json_response(200, res.__dict__)
            except PublicError as e:
                self._send_json_response(501, {"status": "error", "error_code": e.error_code, "message": e.message})
            return

        # 3. Knowledge Query: POST /knowledge/query
        if path == "/knowledge/query":
            domain = payload.get("domain")
            unit_type = payload.get("unit_type")
            tag = payload.get("tag")
            status = payload.get("status")

            results = knowledge_engine.query(
                domain=domain, unit_type=unit_type, tag=tag, status=status
            )
            self._send_json_response(200, {
                "status": "success",
                "query_filter": {"domain": domain, "unit_type": unit_type, "tag": tag, "status": status},
                "total_matches": len(results),
                "units": [r.unit_id for r in results],
            })
            return

        # 4. Runtime Execution: POST /runtime/execute
        if path == "/runtime/execute":
            session_id = payload.get("session_id", f"SESS-{uuid.uuid4().hex[:8].upper()}")
            correlation_id = payload.get("correlation_id", f"CORR-{uuid.uuid4().hex[:8].upper()}")
            intent_action = payload.get("intent_action", "general_query")
            scenario_type = payload.get("scenario_type", "general")
            context_stack = payload.get("context_stack", {})
            requested_knowledge_ids = payload.get("requested_knowledge_ids", [])

            req = RuntimeRequestPayload(
                session_id=session_id,
                correlation_id=correlation_id,
                intent_action=intent_action,
                scenario_type=scenario_type,
                context_stack=context_stack,
                requested_knowledge_ids=requested_knowledge_ids,
            )

            response = runtime_orchestrator.execute(req)

            # Store provenance in memory store
            if response.causal_provenance:
                execution_provenance_store[correlation_id] = response.causal_provenance

            res_dict = response.__dict__
            if response.status_code == "SUCCESS":
                self._send_json_response(200, res_dict)
            else:
                self._send_json_response(422, res_dict)
            return

        # 5. SalesOS Lead Intake: POST /salesos/leads
        if path == "/salesos/leads":
            workflow_result = salesos_plugin.process_lead(payload)

            if workflow_result.status == "SUCCESS":
                self._send_json_response(201, {
                    "status": workflow_result.status,
                    "lead": workflow_result.lead.__dict__ if workflow_result.lead else None,
                    "customer": workflow_result.customer.__dict__ if workflow_result.customer else None,
                    "assignment": workflow_result.assignment.__dict__ if workflow_result.assignment else None,
                    "next_action": workflow_result.next_action.__dict__ if workflow_result.next_action else None,
                    "audit_event": workflow_result.audit_event.__dict__ if workflow_result.audit_event else None,
                    "provenance_trace": workflow_result.provenance_trace.__dict__ if workflow_result.provenance_trace else None,
                    "message": workflow_result.message,
                })
            elif workflow_result.status == "INSUFFICIENT_VERIFIED_KNOWLEDGE":
                self._send_json_response(422, {
                    "status": workflow_result.status,
                    "error_code": workflow_result.error_code,
                    "message": workflow_result.message,
                })
            elif workflow_result.status == "DUPLICATE_REJECTED":
                self._send_json_response(409, {
                    "status": workflow_result.status,
                    "lead": workflow_result.lead.__dict__ if workflow_result.lead else None,
                    "error_code": workflow_result.error_code,
                    "message": workflow_result.message,
                })
            else:
                self._send_json_response(400, {
                    "status": workflow_result.status,
                    "error_code": workflow_result.error_code,
                    "message": workflow_result.message,
                })
            return

        self._send_json_response(404, {"error": "Endpoint not found"})


def create_app_server(host: str = "127.0.0.1", port: int = 8000) -> HTTPServer:
    """Create HTTPServer app instance for local server or test suite execution."""
    return HTTPServer((host, port), BusinessOSGatewayHandler)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting BusinessOS & NhanThuat Web Dashboard Server on http://{host}:{port}...")
    server = create_app_server(host=host, port=port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()
