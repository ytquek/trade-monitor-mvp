from app.services.scoring import topic_scores, detect_event_type


def test_topic_scoring_finds_trade_connectivity():
    text = "The customs single window will streamline border procedures and digital trade facilitation."
    topics, keyword_score, semantic_score = topic_scores(text)
    assert "trade_connectivity" in topics
    assert keyword_score > 0
    assert semantic_score >= 0


def test_event_detection_launch():
    event_type, score = detect_event_type("The government launched a port community system rollout.")
    assert event_type in {"launch", "regulation", "expansion", "concession", "investment", "tender", "disruption"}
    assert score > 0
