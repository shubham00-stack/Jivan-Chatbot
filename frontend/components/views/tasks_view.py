"""
JIVAN Tasks & Workflow Execution View
Features:
- Action item tracker with status (Pending / In Progress / Completed)
- Add new task with title, priority (High/Medium/Low), and notes
- Auto-extract tasks from current conversation using Groq AI
- Persistent in session state
"""

import streamlit as st
from datetime import datetime
from frontend.utils.api_client import api_client

def render_tasks_view():
    st.markdown("## ☑️ Executive Task Board & Action Items")
    st.caption("Organize action items derived from executive briefs and AI conversations.")

    if "user_tasks" not in st.session_state:
        st.session_state["user_tasks"] = [
            {"id": "t1", "title": "Analyze Q2 Sales pipeline and regional growth drivers", "priority": "High", "done": False, "date": "Today"},
            {"id": "t2", "title": "Compare infrastructure deal sizes with prior quarters", "priority": "Medium", "done": True, "date": "Yesterday"},
            {"id": "t3", "title": "Prepare executive summary slide deck for leadership", "priority": "High", "done": False, "date": "Tomorrow"}
        ]

    tasks = st.session_state["user_tasks"]

    # 1. Stats
    pending_count = sum(1 for t in tasks if not t.get("done"))
    completed_count = sum(1 for t in tasks if t.get("done"))

    c1, c2, c3 = st.columns(3)
    c1.metric("Pending Tasks", pending_count)
    c2.metric("Completed Tasks", completed_count)
    c3.metric("Completion Rate", f"{int(completed_count / (len(tasks) or 1) * 100)}%")

    st.divider()

    # 2. Add New Task / AI Extraction
    col_add, col_extract = st.columns([0.65, 0.35])
    with col_add:
        with st.expander("➕ Add New Task", expanded=False):
            new_title = st.text_input("Task Description:", placeholder="e.g. Follow up on partner contributions", key="task_new_title")
            new_priority = st.selectbox("Priority:", ["High", "Medium", "Low"], key="task_new_prio")
            if st.button("Save Task", type="primary", key="btn_save_new_task") and new_title:
                tasks.append({
                    "id": f"t_{datetime.now().timestamp()}",
                    "title": new_title.strip(),
                    "priority": new_priority,
                    "done": False,
                    "date": "Today"
                })
                st.session_state["user_tasks"] = tasks
                st.toast("Task added successfully!", icon="✅")
                st.rerun()

    with col_extract:
        if st.button("✨ Auto-Extract from Chat", use_container_width=True, help="Extract to-do items from active conversation"):
            messages = st.session_state.get("messages", [])
            if not messages:
                st.warning("Start a conversation first to extract tasks.")
            else:
                with st.spinner("Extracting action items with AI..."):
                    chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-4:]])
                    prompt = f"Extract 2 concise actionable tasks from this discussion:\n{chat_context}"
                    res = api_client.send_chat_message(message=prompt, conversation_id=None, enable_emotional_support=False)
                    extracted_text = res.get("response", "")
                    tasks.append({
                        "id": f"t_{datetime.now().timestamp()}",
                        "title": extracted_text[:120].replace("\n", " ").strip(),
                        "priority": "High",
                        "done": False,
                        "date": "Today"
                    })
                    st.session_state["user_tasks"] = tasks
                    st.success("Extracted new action item from chat!")
                    st.rerun()

    st.divider()

    # 3. Tasks List
    st.markdown("### 📋 Action Items")
    for idx, t in enumerate(tasks):
        col_check, col_title, col_prio, col_del = st.columns([0.08, 0.68, 0.14, 0.10])
        with col_check:
            is_done = st.checkbox("", value=t.get("done", False), key=f"chk_task_{t['id']}")
            if is_done != t.get("done", False):
                t["done"] = is_done
                st.session_state["user_tasks"] = tasks
                st.rerun()

        with col_title:
            if t.get("done"):
                st.markdown(f"<s>{t['title']}</s>", unsafe_allow_html=True)
            else:
                st.markdown(f"**{t['title']}**")
            st.caption(f"Created: {t.get('date', 'Today')}")

        with col_prio:
            prio = t.get("priority", "Medium")
            badge_color = "#DC2626" if prio == "High" else ("#F59E0B" if prio == "Medium" else "#10B981")
            st.markdown(f"<span style='color: {badge_color}; font-weight: 600;'>{prio}</span>", unsafe_allow_html=True)

        with col_del:
            if st.button("🗑️", key=f"del_task_{t['id']}"):
                tasks.pop(idx)
                st.session_state["user_tasks"] = tasks
                st.rerun()
        st.markdown("<hr style='margin: 6px 0; opacity: 0.15;'>", unsafe_allow_html=True)

