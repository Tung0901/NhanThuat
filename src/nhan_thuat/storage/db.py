"""
SQLite Database Manager & Storage Repository for NhanThuat Stateful Operations.
Handles session management, message logging, case study records, and default seeding.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from nhan_thuat.storage.models import CaseStudy, SparringMessage, SparringSession


class DatabaseManager:
    """
    Thread-safe SQLite Database Manager for NhanThuat Knowledge Platform.
    Supports in-memory mode (':memory:') for fast unit testing and file persistence for production.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            db_path = repo_root / "knowledge" / "nhan_thuat.db"
        
        self.db_path = str(db_path)
        self._mem_conn: sqlite3.Connection | None = None
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._mem_conn.row_factory = sqlite3.Row
        else:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _close_connection(self, conn: sqlite3.Connection) -> None:
        if self._mem_conn is None:
            conn.close()

    def init_db(self) -> None:
        """Create tables and indexes if they do not exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 1. Sparring Sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sparring_sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                philosophy_lens TEXT DEFAULT 'auto',
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                summary TEXT DEFAULT '',
                metadata TEXT DEFAULT '{}'
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created ON sparring_sessions(created_at DESC)")

        # 2. Sparring Messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sparring_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                matched_unit_ids TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY(session_id) REFERENCES sparring_sessions(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON sparring_messages(session_id, created_at ASC)")

        # 3. Case Studies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_studies (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                title TEXT NOT NULL,
                context_description TEXT NOT NULL,
                decision_script TEXT DEFAULT '{}',
                lessons_learned TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                tags TEXT DEFAULT '[]'
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_domain ON case_studies(domain)")

        conn.commit()
        self._seed_default_case_studies(cursor, conn)
        self._close_connection(conn)

    def _seed_default_case_studies(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
        """Seed foundational executive case studies if empty."""
        cursor.execute("SELECT COUNT(*) FROM case_studies")
        count = cursor.fetchone()[0]
        if count > 0:
            return

        sample_cases = [
            {
                "id": "CASE-OPS-001",
                "domain": "OPS",
                "title": "Nhà cung cấp vật tư giao trễ 48h tại công trình Nhà Bè",
                "context_description": "Vật tư bê tông và cốt thép giao trễ làm ngưng trệ 100% tổ đội công nhân hiện trường. Nhà cung cấp nại lý do tắc biên và khan hiếm nguồn nguyên liệu.",
                "decision_script": {
                    "position_analysis": "Áp dụng lăng kính Pháp Gia ('Hình Danh Tương Phù') kết hợp Chế tài Nhị Bỉnh: Không nhượng bộ cảm tính, kích hoạt biên bản vi phạm và phạt 0.5%/ngày.",
                    "step_1": "Thiết lập vị thế và đối chiếu điều khoản hợp đồng bằng văn bản.",
                    "step_2": "Ấn định thời hạn tối hậu 24h giao bù 100% khối lượng.",
                    "step_3": "Kích hoạt đơn vị cung ứng dự phòng Plan B và cấn trừ thiệt hại vào đợt thanh toán."
                },
                "lessons_learned": [
                    "Quy luật NT-LAW-0005: Động lực và chế tài quyết định thứ tự ưu tiên của nhà cung cấp.",
                    "Nguyên tắc NT-PRINCIPLE-0064: Luôn chuẩn bị sẵn đơn vị cung ứng dự phòng Plan B trước khi khởi công."
                ],
                "tags": ["operations", "contract", "material", "legalism"]
            },
            {
                "id": "CASE-SALES-001",
                "domain": "SALES",
                "title": "Khách hàng doanh nghiệp từ chối báo giá do chênh lệch 15% so với đối thủ",
                "context_description": "Khách hàng liên tục gây áp lực chiết khấu sâu 15%, dọa sẽ ký hợp đồng với đơn vị thi công giá rẻ trên thị trường.",
                "decision_script": {
                    "position_analysis": "Áp dụng thuật Hùng Biện (Rhetoric Reframing): Bẻ gãy khung chi phí ban đầu, chuyển đổi sang bảng phân tích dòng tiền và TCO 3 năm.",
                    "step_1": "Đồng thuận với tiêu chí ngân sách, nhưng bóc tách rủi ro gián đoạn hệ thống giá rẻ.",
                    "step_2": "Chứng minh chi phí vận hành và rủi ro gián đoạn của giải pháp giá rẻ cao gấp 3 lần.",
                    "step_3": "Cam kết bảo hành hiệu năng 100% và tặng gói bảo trì chuyên sâu thay vì chiết khấu tiền mặt."
                },
                "lessons_learned": [
                    "Quy luật NT-LAW-0054: Định khung giá trị (Framing) quyết định nhận thức về giá đắt hay rẻ.",
                    "Nguyên tắc NT-PRINCIPLE-0086: Thiết lập khung giá trị minh bạch trước khi bước vào bàn đàm phán."
                ],
                "tags": ["sales", "negotiation", "rhetoric", "pricing"]
            },
            {
                "id": "CASE-HR-001",
                "domain": "HR",
                "title": "Tổ đội thi công ngưng việc tự phát yêu cầu tăng đơn giá khoán",
                "context_description": "Tổ đội hoàn thiện hiện trường tổ chức ngưng việc tập thể đòi tăng 20% đơn giá khoán giữa giai đoạn nước rút của dự án.",
                "decision_script": {
                    "position_analysis": "Áp dụng kết hợp Tuân Tử (Lễ định phần) và Pháp Gia: Phân tách rõ ràng giữa cá nhân kích động và công nhân làm việc, đối thoại trên cơ sở hợp đồng khoán.",
                    "step_1": "Chốt khối lượng hiện trạng và khẳng định giá trị pháp lý của Hợp đồng khoán.",
                    "step_2": "Ấn định thời hạn 12h quay lại vị trí công tác kèm chế tài chấm dứt hợp đồng.",
                    "step_3": "Dành quỹ thưởng tiến độ cho các cá nhân hoàn thành vượt định mức để hóa giải liên minh ngưng việc."
                },
                "lessons_learned": [
                    "Quy luật NT-LAW-0038: Suy giảm quyền lực xảy ra khi không thực thi kỷ luật kịp thời.",
                    "Nguyên tắc NT-PRINCIPLE-0061: Tái cấu trúc cơ chế khoán và vai trò trước khi yêu cầu thay đổi thái độ."
                ],
                "tags": ["hr", "labor_dispute", "discipline", "xunzi"]
            }
        ]

        now = datetime.utcnow().isoformat()
        for case in sample_cases:
            cursor.execute("""
                INSERT INTO case_studies (id, domain, title, context_description, decision_script, lessons_learned, created_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case["id"],
                case["domain"],
                case["title"],
                case["context_description"],
                json.dumps(case["decision_script"], ensure_ascii=False),
                json.dumps(case["lessons_learned"], ensure_ascii=False),
                now,
                json.dumps(case["tags"], ensure_ascii=False)
            ))
        conn.commit()

    # --- Sparring Sessions CRUD ---
    def create_session(self, title: str, philosophy_lens: str = "auto", metadata: dict[str, Any] | None = None) -> SparringSession:
        conn = self._get_connection()
        cursor = conn.cursor()
        session_id = f"SPAR-SESS-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.utcnow().isoformat()
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)

        cursor.execute("""
            INSERT INTO sparring_sessions (id, title, philosophy_lens, created_at, status, summary, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, title, philosophy_lens, now, "active", "", meta_str))
        conn.commit()
        self._close_connection(conn)

        return SparringSession(
            id=session_id,
            title=title,
            philosophy_lens=philosophy_lens,
            created_at=now,
            status="active",
            summary="",
            metadata=metadata or {},
        )

    def get_session(self, session_id: str) -> SparringSession | None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sparring_sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        self._close_connection(conn)
        return SparringSession.from_row(dict(row)) if row else None

    def list_sessions(self, limit: int = 50) -> list[SparringSession]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sparring_sessions ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        self._close_connection(conn)
        return [SparringSession.from_row(dict(r)) for r in rows]

    def update_session(self, session_id: str, title: str | None = None, status: str | None = None, summary: str | None = None) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if summary is not None:
            updates.append("summary = ?")
            params.append(summary)

        if not updates:
            self._close_connection(conn)
            return False

        params.append(session_id)
        cursor.execute(f"UPDATE sparring_sessions SET {', '.join(updates)} WHERE id = ?", tuple(params))
        conn.commit()
        affected = cursor.rowcount > 0
        self._close_connection(conn)
        return affected

    def delete_session(self, session_id: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sparring_messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sparring_sessions WHERE id = ?", (session_id,))
        conn.commit()
        affected = cursor.rowcount > 0
        self._close_connection(conn)
        return affected

    # --- Sparring Messages CRUD ---
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        matched_unit_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SparringMessage:
        conn = self._get_connection()
        cursor = conn.cursor()
        msg_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.utcnow().isoformat()
        units_str = json.dumps(matched_unit_ids or [], ensure_ascii=False)
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)

        cursor.execute("""
            INSERT INTO sparring_messages (id, session_id, role, content, matched_unit_ids, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, session_id, role, content, units_str, now, meta_str))
        conn.commit()
        self._close_connection(conn)

        return SparringMessage(
            id=msg_id,
            session_id=session_id,
            role=role,
            content=content,
            matched_unit_ids=matched_unit_ids or [],
            created_at=now,
            metadata=metadata or {},
        )

    def list_messages(self, session_id: str) -> list[SparringMessage]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sparring_messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
        rows = cursor.fetchall()
        self._close_connection(conn)
        return [SparringMessage.from_row(dict(r)) for r in rows]

    # --- Case Studies CRUD ---
    def create_case_study(
        self,
        domain: str,
        title: str,
        context_description: str,
        decision_script: dict[str, Any] | None = None,
        lessons_learned: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> CaseStudy:
        conn = self._get_connection()
        cursor = conn.cursor()
        case_id = f"CASE-{domain.upper()}-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.utcnow().isoformat()
        script_str = json.dumps(decision_script or {}, ensure_ascii=False)
        lessons_str = json.dumps(lessons_learned or [], ensure_ascii=False)
        tags_str = json.dumps(tags or [], ensure_ascii=False)

        cursor.execute("""
            INSERT INTO case_studies (id, domain, title, context_description, decision_script, lessons_learned, created_at, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (case_id, domain.upper(), title, context_description, script_str, lessons_str, now, tags_str))
        conn.commit()
        self._close_connection(conn)

        return CaseStudy(
            id=case_id,
            domain=domain.upper(),
            title=title,
            context_description=context_description,
            decision_script=decision_script or {},
            lessons_learned=lessons_learned or [],
            created_at=now,
            tags=tags or [],
        )

    def get_case_study(self, case_id: str) -> CaseStudy | None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM case_studies WHERE id = ?", (case_id,))
        row = cursor.fetchone()
        self._close_connection(conn)
        return CaseStudy.from_row(dict(row)) if row else None

    def list_case_studies(self, domain: str | None = None, limit: int = 50) -> list[CaseStudy]:
        conn = self._get_connection()
        cursor = conn.cursor()
        if domain:
            cursor.execute("SELECT * FROM case_studies WHERE domain = ? ORDER BY created_at DESC LIMIT ?", (domain.upper(), limit))
        else:
            cursor.execute("SELECT * FROM case_studies ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        self._close_connection(conn)
        return [CaseStudy.from_row(dict(r)) for r in rows]

    def delete_case_study(self, case_id: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM case_studies WHERE id = ?", (case_id,))
        conn.commit()
        affected = cursor.rowcount > 0
        self._close_connection(conn)
        return affected
