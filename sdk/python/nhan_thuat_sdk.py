"""
Official NhanThuat Python SDK (Enterprise Client).
Supports both direct local engine execution (in-process offline) and HTTP REST Gateway communication.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class NhanThuatClient:
    """
    Enterprise Python Client for NhanThuat Knowledge Platform.
    Allows seamless integration into CRM, ERP, HRM, and custom operational platforms.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        api_key: str | None = None,
        mode: str = "local",  # 'local' (direct in-process) or 'http' (REST API)
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.mode = mode

        if self.mode == "local":
            from backend.app.engine.nhan_thuat_api import process_nhan_thuat_analysis
            from nhan_thuat.council.council_engine import CouncilEngine
            from nhan_thuat.engine.sparring_engine import SparringEngine
            from nhan_thuat.export.executive_brief import ExecutiveBriefExporter
            from nhan_thuat.knowledge_engine import KnowledgeEngine
            from nhan_thuat.storage.db import DatabaseManager

            self._ke = KnowledgeEngine()
            self._db = DatabaseManager()
            self._sparring = SparringEngine(db_manager=self._db, knowledge_engine=self._ke)
            self._council = CouncilEngine(knowledge_engine=self._ke)
            self._exporter = ExecutiveBriefExporter()
            self._process_analysis = process_nhan_thuat_analysis

    def _http_request(self, method: str, endpoint: str, data: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                content_type = response.headers.get("Content-Type", "")
                res_bytes = response.read()
                if "application/json" in content_type:
                    return json.loads(res_bytes.decode("utf-8"))
                return res_bytes.decode("utf-8")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                return json.loads(err_body)
            except Exception:
                raise RuntimeError(f"HTTP {e.code} Error: {err_body}") from e
        except Exception as e:
            raise RuntimeError(f"Connection to NhanThuat Gateway failed at {url}: {e}") from e

    def analyze_scenario(self, scenario_text: str, scenario_type: str = "general") -> dict[str, Any]:
        """Analyze an operational scenario and synthesize an actionable 3-step script."""
        if self.mode == "local":
            return self._process_analysis(scenario_text, scenario_type)
        return self._http_request("POST", "/api/v1/nhan-thuat/analyze", {
            "scenario_text": scenario_text,
            "scenario_type": scenario_type,
        })

    def start_sparring_session(self, title: str, philosophy_lens: str = "auto", context: str | None = None) -> dict[str, Any]:
        """Start a new stateful adversarial sparring session."""
        if self.mode == "local":
            sess = self._sparring.start_session(title=title, philosophy_lens=philosophy_lens, initial_context=context)
            return {"status": "success", "session": sess.to_dict()}
        return self._http_request("POST", "/api/v1/sparring/sessions", {
            "title": title,
            "philosophy_lens": philosophy_lens,
            "context": context,
        })

    def send_sparring_message(self, session_id: str, message: str, philosophy_lens: str | None = None) -> dict[str, Any]:
        """Send a statement/decision in an active sparring session and receive adversarial critique."""
        if self.mode == "local":
            return self._sparring.process_turn(session_id=session_id, user_message=message, override_lens=philosophy_lens)
        return self._http_request("POST", "/api/v1/sparring/messages", {
            "session_id": session_id,
            "message": message,
            "philosophy_lens": philosophy_lens,
        })

    def deliberate_council(self, scenario_text: str) -> dict[str, Any]:
        """Submit a scenario to the 5-Agent Philosophical Advisory Council for multi-perspective deliberation."""
        if self.mode == "local":
            res = self._council.deliberate(scenario_text)
            return {"status": "success", "deliberation": res.to_dict()}
        return self._http_request("POST", "/api/v1/council/deliberate", {
            "scenario_text": scenario_text,
        })

    def list_case_studies(self, domain: str | None = None) -> list[dict[str, Any]]:
        """List enterprise case studies stored in the repository."""
        if self.mode == "local":
            cases = self._db.list_case_studies(domain=domain)
            return [c.to_dict() for c in cases]
        endpoint = f"/api/v1/cases?domain={domain}" if domain else "/api/v1/cases"
        res = self._http_request("GET", endpoint)
        return res.get("cases", [])

    def export_executive_brief(
        self,
        title: str,
        situation_summary: str,
        philosophy_analysis: str,
        action_script: dict[str, Any],
        knowledge_units: list[dict[str, Any]] | None = None,
        directives: list[str] | None = None,
        format: str = "markdown",
    ) -> str:
        """Export executive decision brief into standardized Markdown or standalone printable HTML."""
        if self.mode == "local":
            return self._exporter.export_brief(
                title=title,
                situation_summary=situation_summary,
                philosophy_analysis=philosophy_analysis,
                action_script=action_script,
                knowledge_units=knowledge_units or [],
                directives=directives or [],
                format=format,
            )
        res = self._http_request("POST", "/api/v1/export/brief", {
            "title": title,
            "situation_summary": situation_summary,
            "philosophy_analysis": philosophy_analysis,
            "action_script": action_script,
            "knowledge_units": knowledge_units or [],
            "directives": directives or [],
            "format": format,
        })
        if isinstance(res, str):
            return res
        return res.get("document", "")
