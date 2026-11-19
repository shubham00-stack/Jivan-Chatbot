import re
from typing import Dict, Any, Tuple

EMOTION_KEYWORDS = {
    "anxiety": [r"\b(anxious|anxiety|panic|panicking|nervous|dread|worried|scared|terrified)\b"],
    "sadness": [r"\b(sad|depressed|unhappy|crying|heartbroken|hopeless|down|miserable)\b"],
    "overwhelm": [r"\b(overwhelmed|too\s+much|burnout|burned\s+out|exhausted|stressed|can'?t\s+cope)\b"],
    "loneliness": [r"\b(lonely|alone|isolated|nobody\s+cares|no\s+friends|abandoned)\b"],
    "anger": [r"\b(angry|furious|mad|irritated|frustrated|pissed|resentful)\b"],
    "grief": [r"\b(loss|grieving|grief|passed\s+away|died|mourning)\b"],
}

COPING_TECHNIQUES = {
    "grounding": (
        "**The 5-4-3-2-1 Grounding Technique**:\n"
        "• Acknowledge **5** things you can see around you.\n"
        "• Acknowledge **4** things you can touch or feel.\n"
        "• Acknowledge **3** things you can hear right now.\n"
        "• Acknowledge **2** things you can smell.\n"
        "• Acknowledge **1** thing you can taste or are grateful for."
    ),
    "box_breathing": (
        "**Box Breathing Exercise**:\n"
        "• Inhale slowly through your nose for **4 seconds**.\n"
        "• Gently hold your breath for **4 seconds**.\n"
        "• Exhale smoothly through your mouth for **4 seconds**.\n"
        "• Rest and pause for **4 seconds**.\n"
        "*(Repeat 3 to 4 times to help calm your nervous system.)*"
    ),
    "journaling": (
        "**Gentle Reflection Prompt**:\n"
        "• Take a moment to write down what feels heaviest right now without filtering your thoughts.\n"
        "• Remind yourself: *What is one small thing within my control today?*"
    )
}

class EmotionalSupportService:
    def __init__(self):
        self.compiled_emotions = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in EMOTION_KEYWORDS.items()
        }

    def detect_emotional_state(self, text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Analyzes message text to detect if the user is expressing emotional distress or vulnerability.
        Returns (is_emotional, detected_category, context_dict)
        """
        detected_categories = []
        for category, regex_list in self.compiled_emotions.items():
            for regex in regex_list:
                if regex.search(text):
                    detected_categories.append(category)
                    break

        if detected_categories:
            primary_category = detected_categories[0]
            coping = self.get_coping_suggestion(primary_category)
            return True, primary_category, {
                "categories": detected_categories,
                "suggested_technique": coping
            }
        return False, "neutral", {}

    def get_coping_suggestion(self, category: str) -> str:
        if category in ("anxiety", "overwhelm"):
            return COPING_TECHNIQUES["box_breathing"]
        elif category in ("loneliness", "sadness", "grief"):
            return COPING_TECHNIQUES["grounding"]
        else:
            return COPING_TECHNIQUES["journaling"]

    def build_emotional_system_prompt(self, category: str) -> str:
        return (
            "You are a compassionate, warm, patient, and deeply empathetic conversational assistant. "
            f"The user appears to be feeling {category}. "
            "Guidelines:\n"
            "1. Validate their feelings with genuine kindness, active listening, and calm reassurance.\n"
            "2. Never judge, dismiss, or tell them to 'just cheer up' or 'calm down'.\n"
            "3. Offer gentle, non-prescriptive coping exercises or comforting perspectives when appropriate.\n"
            "4. Maintain boundaries: Do NOT diagnose mental health conditions, prescribe clinical treatments, or encourage emotional dependency.\n"
            "5. Encourage autonomy, self-compassion, and connecting with trusted support networks."
        )

emotional_support_service = EmotionalSupportService()

