from src.ui.study_guide import QUIZ_BANK, STUDY_GUIDE, all_topics, study_guide_summary


def test_study_guide_has_core_topics():
    topics = all_topics()
    assert "PD, LGD, EAD and Expected Loss" in topics
    assert "IFRS 9 ECL and Staging" in topics
    assert "XVA Counterparty Risk" in topics


def test_study_guide_topics_have_required_sections():
    for category, topics in STUDY_GUIDE.items():
        assert topics, f"{category} should contain topics"
        for topic in topics:
            assert topic["definition"], topic["topic"]
            assert topic["project_use"], topic["topic"]
            assert topic["formulas"], topic["topic"]
            assert topic["memory"], topic["topic"]
            assert topic["questions"], topic["topic"]


def test_study_guide_summary_has_one_row_per_topic():
    summary = study_guide_summary()
    assert len(summary) == len(all_topics())
    assert set(summary.columns) == {"category", "topic"}


def test_quiz_bank_has_answers_and_explanations():
    assert QUIZ_BANK
    for item in QUIZ_BANK:
        assert item["answer"] in item["options"]
        assert item["explanation"]
