import re
from typing import Tuple, Optional
from backend.core.security import detect_prompt_injection, sanitize_input
from backend.core.logging import logger

CRISIS_PATTERNS = [
    r"\b(suicid(e|al)|kill\s+(my|one)?self|end(ing)?\s+my\s+life|want\s+to\s+die|hang(ing)?\s+myself)\b",
    r"\b(self[\s-]?harm|cut(ting)?\s+myself|slit(ting)?\s+my\s+wrist|overdos(e|ing)|take\s+all\s+my\s+pills)\b",
    r"\b(hate\s+living|no\s+reason\s+to\s+live|better\s+off\s+dead|can'?t\s+go\s+on\s+anymore|hurt(ing)?\s+myself)\b",
    r"\b(abused?|being\s+hit|domestic\s+violence|someone\s+hurting\s+me)\b",
]

COMPILED_CRISIS_RE = [re.compile(p, re.IGNORECASE) for p in CRISIS_PATTERNS]

CRISIS_RESPONSE_TEMPLATE = """I hear how much pain you are experiencing right now, and I want you to know that you do not have to carry this alone. Your life and well-being matter deeply.

I am an AI assistant, not a doctor or licensed therapist, and I cannot provide therapy or medical crisis care. Please reach out right now to someone who can help support you:

- **United States & Canada**: Call or text **988** to reach the Suicide & Crisis Lifeline (Free, confidential, available 24/7).
- **Crisis Text Line**: Text **HOME** to **741741** to connect with a crisis counselor.
- **United Kingdom**: Call **111** (NHS) or call Samaritans at **116 123**.
- **International Resources**: Visit **[findahelpline.com](https://findahelpline.com/)** to find free, confidential support in your country.
- **Emergency Services**: If you are in immediate danger of hurting yourself or others, please call your local emergency services (such as 911, 999, or 112) or go to the nearest emergency room.

Please reach out to a trusted family member, friend, or healthcare provider. People who care want to be there for you."""

MEDICAL_DISCLAIMER_SUFFIX = "\n\n*(Note: I am an AI companion, not a licensed therapist or healthcare provider. For medical or mental health diagnoses and treatments, please consult a qualified professional.)*"

class SafetyService:
    def check_safety(self, text: str) -> Tuple[bool, bool, Optional[str]]:
        """
        Evaluates user text.
        Returns:
            (is_safe: bool, is_crisis: bool, response_or_reason: Optional[str])
        """
        cleaned = sanitize_input(text)

        # 1. Check for immediate crisis or self-harm keywords
        for regex in COMPILED_CRISIS_RE:
            if regex.search(cleaned):
                logger.warning("Crisis intervention sentinel triggered.")
                return False, True, CRISIS_RESPONSE_TEMPLATE

        # 2. Check for Prompt Injection / Jailbreaks
        is_injection, reason = detect_prompt_injection(cleaned)
        if is_injection:
            return False, False, (
                "I detected instructions that attempt to alter or bypass system security guidelines. "
                "I cannot process this request as phrased. Please rephrase your question naturally."
            )

        return True, False, None

    def append_disclaimer_if_needed(self, text: str, is_emotional: bool = False) -> str:
        """Appends a gentle disclaimer if health or therapeutic topics were discussed."""
        if is_emotional and "licensed therapist" not in text:
            return text + MEDICAL_DISCLAIMER_SUFFIX
        return text

safety_service = SafetyService()
