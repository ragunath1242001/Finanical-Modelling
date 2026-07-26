from src.reporting.downloads import pdf_report_bytes
from src.ui.banking_101 import BANKING_101_TOPICS, _topic_report_sections, banking_101_summary


def test_banking_101_has_beginner_core_topics():
    topics = {topic["topic"] for topic in BANKING_101_TOPICS}
    assert "What a Bank Does" in topics
    assert "Basic Loan Concepts" in topics
    assert "PD, LGD, EAD and Expected Loss" in topics
    assert "Capital, RWA and CET1" in topics
    assert "End-to-End Banking Risk Story" in topics


def test_banking_101_topics_have_required_sections():
    for topic in BANKING_101_TOPICS:
        assert topic["area"]
        assert topic["beginner_meaning"], topic["topic"]
        assert topic["why_it_matters"], topic["topic"]
        assert topic["project_use"], topic["topic"]
        assert topic["simple_example"], topic["topic"]
        assert topic["memory_hook"], topic["topic"]
        assert topic["self_checks"], topic["topic"]


def test_banking_101_summary_has_one_row_per_topic():
    summary = banking_101_summary()
    assert len(summary) == len(BANKING_101_TOPICS)
    assert set(summary.columns) == {"area", "topic", "why_it_matters"}


def test_banking_101_topic_pdf_sections_generate_pdf():
    topic = BANKING_101_TOPICS[0]
    sections = _topic_report_sections(topic)
    data = pdf_report_bytes(f"Banking 101 - {topic['topic']}", sections)
    assert data.startswith(b"%PDF")
