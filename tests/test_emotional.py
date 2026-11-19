from backend.services.emotional_support_service import emotional_support_service
from backend.services.safety_service import safety_service

def test_emotional_state_detection():
    anxious_text = "I feel so anxious and overwhelmed by all my deadlines, I can't sleep."
    is_emotional, category, ctx = emotional_support_service.detect_emotional_state(anxious_text)
    assert is_emotional is True
    assert category in ("anxiety", "overwhelm")
    assert "suggested_technique" in ctx

def test_neutral_text_not_flagged_emotional():
    neutral_text = "What is the speed of light in a vacuum?"
    is_emotional, category, ctx = emotional_support_service.detect_emotional_state(neutral_text)
    assert is_emotional is False
    assert category == "neutral"

def test_medical_disclaimer_appended():
    response = "Take a few deep breaths and give yourself some grace."
    with_disclaimer = safety_service.append_disclaimer_if_needed(response, is_emotional=True)
    assert "licensed therapist" in with_disclaimer

