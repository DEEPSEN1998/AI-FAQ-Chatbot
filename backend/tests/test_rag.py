"""Unit tests for deterministic RAG helpers; remote NVIDIA APIs are not called."""

from backend.app.rag import chunk_text, is_portfolio_question, split_by_portfolio_state


def test_chunk_text_keeps_all_content_in_order():
    """Overlapping chunks retain the start and end of a long normalized document."""
    text = " ".join(f"word{i}" for i in range(100))
    chunks = chunk_text(text, chunk_size=80, overlap=20)

    assert len(chunks) > 1
    assert chunks[0].startswith("word0")
    assert chunks[-1].endswith("word99")
    assert all(len(chunk) <= 80 for chunk in chunks)


def test_portfolio_section_is_tagged_without_tagging_the_next_section():
    """Only project text is selected when a knowledge file contains many sections."""
    text = "SECTION: PORTFOLIO\nProject Name: Example\nSECTION: COMPANY STRENGTHS\nFast support"
    segments, active = split_by_portfolio_state(text, portfolio_active=False)

    assert any("Project Name: Example" in segment and portfolio for segment, portfolio in segments)
    assert any("Fast support" in segment and not portfolio for segment, portfolio in segments)
    assert active is False
    assert is_portfolio_question("Please show all portfolios")
