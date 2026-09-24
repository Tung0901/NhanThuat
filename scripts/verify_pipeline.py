#!/usr/bin/env python3
"""
End-to-End Verification Harness for BusinessOS & Nhân Thuật Pipeline.
Demonstrates and validates complete lifecycle:
Raw Human Input -> Jev AI Decider -> Nhân Thuật Analysis -> BusinessOS Action Router.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Configure UTF-8 stdout/stderr for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Tự động kích hoạt môi trường ảo .venv nếu chạy từ Python hệ thống thiếu thư viện
try:
    import requests  # noqa: F401
except ImportError:
    import os
    venv_py = (
        WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
        if os.name == "nt"
        else WORKSPACE_ROOT / ".venv" / "bin" / "python"
    )
    if venv_py.exists() and sys.executable != str(venv_py):
        import subprocess
        sys.exit(subprocess.call([str(venv_py), str(Path(__file__).resolve()), *sys.argv[1:]]))
    raise

from modules.business_os.router import BusinessOSActionRouter
from modules.decider.adapter import JevDecisionAdapter
from modules.nhan_thuat.service import HumanInputRecord, NhanThuatBehavioralService


def run_pipeline_scenario(
    scenario_name: str,
    raw_message: str,
    author_id: str,
    task_context: str,
    decider: JevDecisionAdapter,
    nhan_thuat: NhanThuatBehavioralService,
    router: BusinessOSActionRouter,
) -> dict:
    print("\n" + "=" * 75)
    print(f"▶ SCENARIO: {scenario_name}")
    print("=" * 75)

    # 1. RAW INPUT STAGE
    print("\n[1. RAW INPUT STAGE]")
    print(f"  • Author ID: {author_id}")
    print(f"  • Content:   \"{raw_message}\"")
    print(f"  • Task:      \"{task_context}\"")
    input_record = HumanInputRecord(content=raw_message, author_id=author_id)

    # 2 & 3. DECIDER & NHÂN THUẬT EVALUATION STAGE
    print("\n[2 & 3. JEV DECIDER & NHÂN THUẬT EVALUATION STAGE]")
    event = nhan_thuat.evaluate(input_record)
    print(f"  • Event ID:                  {event.event_id}")
    print(f"  • Burnout Risk (Noul):       {event.burnout_risk} (Confidence: {event.burnout_risk_confidence:.2f})")
    print(f"  • Stress Score (1-5):        {event.stress_score} (Confidence: {event.stress_score_confidence:.2f})")
    print(f"  • Behavioral Style (DISC):   {event.behavior_style} (Confidence: {event.behavior_style_confidence:.2f})")

    # 4. BUSINESSOS ACTION ROUTING STAGE
    print("\n[4. BUSINESSOS ACTION ROUTING STAGE]")
    result = router.route(event, task_context=task_context)
    print(f"  • Router ID:                 {result.router_id}")
    print(f"  • Alerts Triggered ({len(result.alerts_triggered)}):")
    for alert in result.alerts_triggered:
        print(f"    ⚠️  {alert}")

    print(f"  • Executed Actions ({len(result.actions)}):")
    for action in result.actions:
        print(f"    ⚡ [{action.priority}] {action.action_type}: {action.rationale}")

    print("\n  • Dispatch Output Preview:")
    for line in result.dispatch_text.strip().splitlines():
        print(f"    | {line}")

    return {
        "scenario": scenario_name,
        "event": event,
        "result": result,
    }


def main() -> int:
    print("===========================================================================")
    print("   BUSINESSOS & NHÂN THUẬT END-TO-END PIPELINE VERIFICATION HARNESS")
    print("===========================================================================")

    # Initialize Services
    decider = JevDecisionAdapter()
    print(f"✔ Jev Decision Adapter initialized (Mock Mode: {decider.is_mock})")

    nhan_thuat = NhanThuatBehavioralService(decider=decider)
    print("✔ Nhân Thuật Behavioral Service initialized")

    router = BusinessOSActionRouter(confidence_threshold=0.85)
    print("✔ BusinessOS Action Router initialized (Confidence Threshold: P > 0.85)")

    # --- TEST CASE 1: OVERWORKED / BURNOUT EMPLOYEE ---
    res1 = run_pipeline_scenario(
        scenario_name="Overworked / High-Stress Employee Alert",
        raw_message="Tôi đang quá tải và kiệt sức nghiêm trọng với khối lượng công việc này, áp lực liên tục không kịp thở và mệt mỏi cùng cực.",
        author_id="EMP-101-ANH",
        task_context="Bàn giao module thanh toán cổng quốc tế",
        decider=decider,
        nhan_thuat=nhan_thuat,
        router=router,
    )
    # Verification Assertions
    assert res1["event"].burnout_risk is True, "Scenario 1 must detect burnout risk"
    assert res1["event"].stress_score >= 4, "Scenario 1 must detect stress >= 4"
    action_types_1 = [a.action_type for a in res1["result"].actions]
    assert "URGENT_MANAGER_ALERT" in action_types_1, "Must trigger URGENT_MANAGER_ALERT"
    assert "TASK_PRIORITY_ADJUSTMENT" in action_types_1, "Must trigger TASK_PRIORITY_ADJUSTMENT"
    print("\n  >>> SCENARIO 1 VALIDATION: PASSED ✔")

    # --- TEST CASE 2: DIRECT EXECUTIVE STYLE (DISC: D) ---
    res2 = run_pipeline_scenario(
        scenario_name="Direct Executive Task Dispatch (Style D)",
        raw_message="Cần chốt mục tiêu KPI ngay hôm nay, thực thi nhanh quyết định dứt điểm để hoàn thành deadline.",
        author_id="EMP-202-MINH",
        task_context="Chiến dịch mở rộng thị trường miền Trung",
        decider=decider,
        nhan_thuat=nhan_thuat,
        router=router,
    )
    # Verification Assertions
    assert res2["event"].behavior_style == "D", "Scenario 2 must identify Style D"
    assert res2["event"].burnout_risk is False, "Scenario 2 should not flag burnout"
    action_types_2 = [a.action_type for a in res2["result"].actions]
    assert "TASK_DISPATCH_DIRECT_BULLETS" in action_types_2, "Must trigger TASK_DISPATCH_DIRECT_BULLETS"
    print("\n  >>> SCENARIO 2 VALIDATION: PASSED ✔")

    # --- TEST CASE 3: ANALYTICAL TECHNICAL SPECIFICATION STYLE (DISC: C) ---
    res3 = run_pipeline_scenario(
        scenario_name="Analytical & Quality Specification Task Dispatch (Style C)",
        raw_message="Đã hoàn thành kiểm tra chi tiết dữ liệu, phân tích quy trình và đặc tả các tiêu chuẩn nghiệm thu chính xác.",
        author_id="EMP-303-LINH",
        task_context="Kiểm thử hệ thống và bảo mật dữ liệu khách hàng",
        decider=decider,
        nhan_thuat=nhan_thuat,
        router=router,
    )
    # Verification Assertions
    assert res3["event"].behavior_style == "C", "Scenario 3 must identify Style C"
    action_types_3 = [a.action_type for a in res3["result"].actions]
    assert "TASK_DISPATCH_TECH_SPEC" in action_types_3, "Must trigger TASK_DISPATCH_TECH_SPEC"
    print("\n  >>> SCENARIO 3 VALIDATION: PASSED ✔")

    print("\n" + "=" * 75)
    print("🎉 ALL PIPELINE SCENARIOS PASSED WITH ZERO CRASHES & STRICT STATE TRANSITIONS!")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    sys.exit(main())
