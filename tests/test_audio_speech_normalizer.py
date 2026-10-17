"""
Unit tests for Speech Normalizer and Audio Briefing preparation.
"""

from nhan_thuat.audio.speech_normalizer import (
    clean_markdown_for_speech,
    extract_speech_modes,
    split_into_utterance_chunks,
)


def test_clean_markdown_headers_and_styling() -> None:
    raw_md = (
        "### 1. Phân Tích Thế Trận\n"
        "Đối phương đang áp dụng chiến thuật **thao túng thông tin** và *thăm dò* phản ứng.\n"
        "> Đây là ranh giới bất biến cần giữ vững.\n"
        "---"
    )
    cleaned = clean_markdown_for_speech(raw_md)
    assert "###" not in cleaned
    assert "**" not in cleaned
    assert "*" not in cleaned
    assert ">" not in cleaned
    assert "---" not in cleaned
    assert "Phân Tích Thế Trận" in cleaned
    assert "thao túng thông tin" in cleaned
    assert "Đây là ranh giới bất biến cần giữ vững." in cleaned


def test_clean_markdown_abbreviations_and_probabilities() -> None:
    raw_text = "Chỉ số KPI của phòng ban đạt P > 0.85 và cần kích hoạt Plan B ngay."
    cleaned = clean_markdown_for_speech(raw_text)
    assert "KPI" not in cleaned
    assert "chỉ số hiệu suất" in cleaned
    assert "xác suất trên 85 phần trăm" in cleaned
    assert "Phương án dự phòng B" in cleaned


def test_split_into_utterance_chunks_boundary() -> None:
    long_passage = (
        "Chúng ta cần kiểm soát tình hình ngay lập tức. Đây là cơ hội vàng để xoay chuyển cục diện. "
        "Nếu đối phương tiếp tục trì hoãn, hãy kích hoạt chế độ đối đầu theo kỷ luật hệ thống. "
        "Mọi hành động đều phải có bằng chứng rõ ràng."
    )
    chunks = split_into_utterance_chunks(long_passage, max_chunk_words=15)
    assert len(chunks) >= 3
    for chunk in chunks:
        assert len(chunk.split()) <= 20
        # Verify no markdown or dangling artifacts
        assert "#" not in chunk


def test_extract_speech_modes_from_advisory_payload() -> None:
    sample_payload = {
        "position_analysis": "Thế trận đang giằng co quyết liệt giữa hai phe.",
        "step_1_anchor": {
            "title": "Bước 1: Giữ Vững Ranh Giới",
            "verbatim": '"Tôi hiểu quan điểm của anh, nhưng kỷ luật là nguyên tắc tối thượng."',
        },
        "step_2_deadline_consequence": {
            "title": "Bước 2: Ấn Định Thời Hạn",
            "verbatim": '"Hạn chót là 17 giờ chiều nay để bàn giao toàn bộ hồ sơ."',
        },
        "step_3_way_out_plan_b": {
            "title": "Bước 3: Mở Đường Rút Lui",
            "verbatim": '"Nếu hoàn thành đúng hạn, sự hợp tác vẫn tiếp tục bình thường."',
        },
        "financial_and_operational_directives": [
            "Kiểm kê tài chính độc lập trong 24 giờ.",
            "Chuẩn bị nhân sự thay thế.",
        ],
    }

    modes = extract_speech_modes(sample_payload)
    assert "full" in modes
    assert "verbatim_only" in modes
    assert "executive_summary" in modes

    # Verbatim only should have the 3 quotes and titles
    verbatim_text = modes["verbatim_only"]
    assert "Bước 1" in verbatim_text
    assert "Tôi hiểu quan điểm của anh" in verbatim_text
    assert "Hạn chót là 17 giờ" in verbatim_text
    assert "kỷ luật là nguyên tắc tối thượng" in verbatim_text

    # Summary has position analysis
    assert "Thế trận đang giằng co" in modes["executive_summary"]
    # Full has directives
    assert "Kiểm kê tài chính độc lập" in modes["full"]


def test_speech_normalizer_edge_cases() -> None:
    assert clean_markdown_for_speech("") == ""
    assert split_into_utterance_chunks("") == []
    modes_empty = extract_speech_modes({})
    assert modes_empty["full"] == ""
    assert modes_empty["verbatim_only"] == ""

