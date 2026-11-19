"""
JIVAN Prompt Templates Library View
Features:
- Enterprise prompt cards across Executive Analysis, Coding, Research, and Wellness
- One-click 'Use Template' action that loads prompt and switches to Conversations view
"""

import streamlit as st

TEMPLATES = [
    {
        "id": "tpl_q2",
        "category": "📊 Executive & Sales",
        "title": "Q2 Performance & Revenue Breakdown",
        "description": "Summarize top performing products, regional growth, deal sizes, and executive takeaways.",
        "prompt": "Please analyze our Q2 performance: summarize top 5 products by revenue, breakdown pipeline trends in North America and Europe, and provide 3 key strategic recommendations."
    },
    {
        "id": "tpl_code",
        "category": "💻 Engineering & Code",
        "title": "Python Architecture & Algorithm Review",
        "description": "Generate clean, production-grade Python code with type annotations, docstrings, and edge-case handling.",
        "prompt": "Write a robust, production-ready Python class implementing an asynchronous worker pool with retry logic and rate limiting."
    },
    {
        "id": "tpl_pdf",
        "category": "📑 Document Generator",
        "title": "Automated Executive Briefing PDF",
        "description": "Generate a beautifully styled multi-page PDF briefing document with headers and key findings.",
        "prompt": "/pdf Executive Strategy Briefing: Q3 Market Opportunities and Risk Mitigation"
    },
    {
        "id": "tpl_image",
        "category": "🎨 Visual Intelligence",
        "title": "High-Definition Visual Conceptualizer",
        "description": "Generate a photorealistic or artistic image using the integrated image engine.",
        "prompt": "/image A futuristic minimalist corporate glass headquarters surrounded by lush green nature, ultra realistic 4k"
    },
    {
        "id": "tpl_wellness",
        "category": "💖 Emotional Support & Wellness",
        "title": "Stress Reduction & Executive Coping Session",
        "description": "Engage in an empathetic, evidence-based cognitive reframing and breathing exercise.",
        "prompt": "/coping I am feeling overwhelmed with deadlines and workload. Please guide me through a calming exercise."
    }
]

def render_templates_view():
    st.markdown("## 📄 Enterprise Prompt Templates")
    st.caption("Jumpstart high-value workflows with pre-engineered executive and technical templates.")

    col1, col2 = st.columns(2)

    for idx, tpl in enumerate(TEMPLATES):
        col = col1 if idx % 2 == 0 else col2
        with col:
            with st.container(border=True):
                st.markdown(f"**{tpl['category']}**")
                st.markdown(f"### {tpl['title']}")
                st.write(tpl["description"])
                st.code(tpl["prompt"], language="text")
                if st.button("🚀 Use This Template", key=f"btn_use_{tpl['id']}", type="primary", use_container_width=True):
                    st.session_state["queued_prompt"] = tpl["prompt"]
                    st.session_state["active_nav"] = "Conversations"
                    st.toast(f"Loaded template: {tpl['title']}", icon="✅")
                    st.rerun()

