"""
JIVAN Enterprise Theme & CSS Stylesheet
Supports Bright (Light) Mode and Dark Mode:
- Left Sidebar ALWAYS visible and expanded (never collapsed off-screen)
- Zero unrendered Material ligature words ('expand_more' suppressed globally)
- Pure white (#FFFFFF) high-visibility chat input in Bright Mode with pitch dark text (#0F172A)
- Clean white (#FFFFFF) pill buttons in Bright Mode with crisp dark text
- Sticky fixed-position Right Inspector Panel (Sources & Details)
- Full isolation between chat stream and floating composer
"""

def get_jivan_css(theme_mode: str = "bright") -> str:
    is_dark = (theme_mode == "dark")

    # Color Palettes
    bg_app = "#0B0F19" if is_dark else "#F8FAFC"
    bg_card = "#111827" if is_dark else "#FFFFFF"
    border_color = "#334155" if is_dark else "#E2E8F0"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#64748B"
    bg_user_bubble = "#1E3A8A" if is_dark else "#EBF3FE"
    text_user_bubble = "#FFFFFF" if is_dark else "#0F172A"
    bg_asst_bubble = "#1F2937" if is_dark else "#FFFFFF"
    text_asst_bubble = "#E2E8F0" if is_dark else "#1E293B"
    input_bg = "#1E293B" if is_dark else "#FFFFFF"
    input_text = "#FFFFFF" if is_dark else "#0F172A"
    input_border = "#475569" if is_dark else "#CBD5E1"
    btn_bg = "#1E293B" if is_dark else "#FFFFFF"
    btn_text = "#F8FAFC" if is_dark else "#1E293B"
    btn_border = "#334155" if is_dark else "#CBD5E1"
    btn_hover_bg = "#1E3A8A" if is_dark else "#F0FDF4"

    return f"""
<style>
/* =========================================================================
   1. GLOBAL RESETS & TYPOGRAPHY
   ========================================================================= */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, p, div:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded), input, textarea {{
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}}

/* SUPPRESS ALL UNRENDERED LIGATURE TEXT (e.g. 'expand_more') ACROSS THE ENTIRE UI */
[data-testid="stIconMaterial"],
.material-symbols-rounded,
div[data-testid="stPopover"] span[data-testid="stIconMaterial"],
div[data-testid="stPopover"] .material-symbols-rounded {{
    display: none !important;
    visibility: hidden !important;
    font-size: 0px !important;
    line-height: 0 !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    text-indent: -9999px !important;
}}

/* Top Header & Toolbar Reset */
header[data-testid="stHeader"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    height: 0px !important;
    min-height: 0px !important;
    overflow: visible !important;
}}

#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{
    display: none !important;
    visibility: hidden !important;
}}

/* Main App Canvas Background */
.stApp {{
    background-color: {bg_app} !important;
    color: {text_primary} !important;
}}

.block-container {{
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}}

/* =========================================================================
   2. LEFT SIDEBAR (DEEP NAVY #0A1128) - ALWAYS VISIBLE & EXPANDED
   ========================================================================= */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"][aria-expanded="false"],
section[data-testid="stSidebar"][aria-expanded="true"] {{
    background-color: {"#070B16" if is_dark else "#0A1128"} !important;
    color: #FFFFFF !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    transform: none !important;
    margin-left: 0px !important;
    left: 0px !important;
    display: block !important;
    visibility: visible !important;
    position: relative !important;
    opacity: 1 !important;
    z-index: 100 !important;
}}

section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {{
    padding-top: 1rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    padding-bottom: 2rem !important;
}}

/* Collapse / Expand Control Button */
[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"] {{
    display: flex !important;
    visibility: visible !important;
    position: fixed !important;
    top: 12px !important;
    left: 12px !important;
    z-index: 9999999 !important;
    background: #008080 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 6px 8px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}}

[data-testid="collapsedControl"] svg,
button[data-testid="stSidebarCollapseButton"] svg {{
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
}}

/* Brand Header */
.jivan-brand-wrapper {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 4px 14px 4px;
    margin-bottom: 8px;
}}

.jivan-logo-badge {{
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #00A896 0%, #028090 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 168, 150, 0.35);
    color: white;
    font-size: 19px;
}}

.jivan-brand-title {{
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: #FFFFFF;
    text-transform: uppercase;
}}

/* + New conversation Button */
.st-key-jivan_btn_new_chat button {{
    background: linear-gradient(135deg, #008080 0%, #006666 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 0.94rem !important;
    padding: 0.6rem 1rem !important;
    box-shadow: 0 4px 14px rgba(0, 128, 128, 0.35) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    width: 100% !important;
}}

.st-key-jivan_btn_new_chat button:hover {{
    background: linear-gradient(135deg, #009999 0%, #008080 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(0, 128, 128, 0.5) !important;
}}

/* Sidebar Nav Buttons */
.st-key-nav_conversations button,
.st-key-nav_knowledge button,
.st-key-nav_tasks button,
.st-key-nav_templates button,
.st-key-nav_settings button {{
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    color: #94A3B8 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 8px 12px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}}

.st-key-nav_conversations button:hover,
.st-key-nav_knowledge button:hover,
.st-key-nav_tasks button:hover,
.st-key-nav_templates button:hover,
.st-key-nav_settings button:hover {{
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
}}

/* Sidebar Section Headers */
.jivan-section-label {{
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B;
    font-weight: 700;
    margin: 18px 0 8px 8px;
}}

/* ALL SIDEBAR BUTTONS - NEVER SOLID WHITE, ALWAYS CRISP & READABLE */
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] div[data-testid="stColumn"] .stButton > button,
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] .stButton > button {{
    background-color: rgba(255, 255, 255, 0.08) !important;
    background: rgba(255, 255, 255, 0.08) !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}}

section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] div[data-testid="stColumn"] .stButton > button:hover {{
    background-color: rgba(255, 255, 255, 0.16) !important;
    background: rgba(255, 255, 255, 0.16) !important;
    border-color: rgba(255, 255, 255, 0.28) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}

/* Appearance Theme Buttons (☀️ Bright / 🌙 Dark) */
div[class*="st-key-btn_theme_"] button,
.st-key-btn_theme_bright button,
.st-key-btn_theme_dark button {{
    background-color: rgba(255, 255, 255, 0.08) !important;
    background: rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}

div[class*="st-key-btn_theme_"] button:hover,
.st-key-btn_theme_bright button:hover,
.st-key-btn_theme_dark button:hover {{
    background-color: rgba(0, 128, 128, 0.35) !important;
    background: rgba(0, 128, 128, 0.35) !important;
    border-color: #2DD4BF !important;
    color: #2DD4BF !important;
    -webkit-text-fill-color: #2DD4BF !important;
}}

/* Recent Chats List: Transparent flat list items */
div[class*="st-key-jivan_conv_"] button,
.st-key-jivan_conv_ button {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    color: #CBD5E1 !important;
    -webkit-text-fill-color: #CBD5E1 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 6px 8px !important;
    font-size: 0.86rem !important;
}}

div[class*="st-key-jivan_conv_"] button:hover,
.st-key-jivan_conv_ button:hover {{
    background: rgba(255, 255, 255, 0.08) !important;
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}

/* Delete Conversation ✕ Buttons */
div[class*="st-key-jivan_del_"] button,
.st-key-jivan_del_ button {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
    padding: 6px 4px !important;
}}

div[class*="st-key-jivan_del_"] button:hover,
.st-key-jivan_del_ button:hover {{
    color: #EF4444 !important;
    -webkit-text-fill-color: #EF4444 !important;
    background: rgba(239, 68, 68, 0.15) !important;
    background-color: rgba(239, 68, 68, 0.15) !important;
}}

/* Profile Edit ✏️ Button */
div[class*="st-key-btn_toggle_email_edit"] button,
.st-key-btn_toggle_email_edit button {{
    background: rgba(255, 255, 255, 0.08) !important;
    background-color: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border-radius: 8px !important;
}}

div[class*="st-key-btn_toggle_email_edit"] button:hover,
.st-key-btn_toggle_email_edit button:hover {{
    background: rgba(0, 128, 128, 0.35) !important;
    background-color: rgba(0, 128, 128, 0.35) !important;
    border-color: #2DD4BF !important;
}}

/* Sidebar Profile Card */
.jivan-profile-card {{
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
}}

.jivan-profile-avatar {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #008080 0%, #005F5F 100%);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 0.86rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.jivan-profile-info {{
    flex: 1;
    overflow: hidden;
}}

.jivan-profile-name {{
    color: #FFFFFF;
    font-size: 0.84rem;
    font-weight: 600;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.jivan-profile-role {{
    color: #2DD4BF;
    font-size: 0.72rem;
    line-height: 1.2;
    margin-top: 2px;
}}

/* =========================================================================
   3. MAIN CANVAS BUTTONS - PURE BRIGHT WHITE IN BRIGHT MODE
   ========================================================================= */
div[data-testid="stMainBlockContainer"] .stButton > button {{
    background-color: {btn_bg} !important;
    background: {btn_bg} !important;
    color: {btn_text} !important;
    -webkit-text-fill-color: {btn_text} !important;
    border: 1.5px solid {btn_border} !important;
    border-radius: 20px !important;
    padding: 7px 16px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

div[data-testid="stMainBlockContainer"] .stButton > button:hover {{
    background-color: {btn_hover_bg} !important;
    background: {btn_hover_bg} !important;
    border-color: #008080 !important;
    color: #008080 !important;
    -webkit-text-fill-color: #008080 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0, 128, 128, 0.12) !important;
}}

/* Primary Buttons */
div[data-testid="stMainBlockContainer"] .stButton > button[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, #008080 0%, #006666 100%) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: none !important;
}}

div[data-testid="stMainBlockContainer"] .stButton > button[data-testid="baseButton-primary"]:hover {{
    background: linear-gradient(135deg, #009999 0%, #008080 100%) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}

/* =========================================================================
   4. CENTER CANVAS HEADER, HERO STATE & MESSAGES
   ========================================================================= */
.jivan-topbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 18px;
    border-bottom: 1px solid {border_color};
    background-color: {bg_card};
    border-radius: 14px 14px 0 0;
    margin-bottom: 12px;
}}

.jivan-topbar-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: {text_primary};
    display: flex;
    align-items: center;
    gap: 8px;
}}

.jivan-topbar-subtitle {{
    font-size: 0.8rem;
    color: {text_secondary};
    margin-top: 2px;
}}

/* Hero Empty State */
.jivan-hero-section {{
    text-align: center;
    padding: 28px 20px 14px 20px;
    animation: fadeIn 0.4s ease-out;
}}

.jivan-hero-bubble {{
    width: 58px;
    height: 58px;
    background: {"#0D3B37" if is_dark else "#E6F4F1"};
    border-radius: 50%;
    margin: 0 auto 14px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: #008080;
}}

.jivan-hero-heading {{
    font-size: 1.85rem;
    font-weight: 700;
    color: {text_primary};
    margin-bottom: 6px;
    letter-spacing: -0.01em;
}}

.jivan-hero-subheading {{
    font-size: 0.94rem;
    color: {text_secondary};
    max-width: 500px;
    margin: 0 auto 20px auto;
    line-height: 1.5;
}}

/* Date divider */
.jivan-date-divider {{
    text-align: center;
    position: relative;
    margin: 20px 0 16px 0;
}}

.jivan-date-divider::before {{
    content: '';
    position: absolute;
    left: 8%;
    right: 8%;
    top: 50%;
    height: 1px;
    background-color: {border_color};
    z-index: 1;
}}

.jivan-date-pill {{
    position: relative;
    z-index: 2;
    background-color: {bg_app};
    padding: 2px 14px;
    color: {text_secondary};
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* User Message */
.jivan-user-row {{
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
    gap: 12px;
    margin-bottom: 16px;
    animation: slideUpFadeIn 0.3s ease-out;
}}

.jivan-user-bubble {{
    background-color: {bg_user_bubble};
    color: {text_user_bubble};
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    max-width: 72%;
    font-size: 0.94rem;
    line-height: 1.55;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}}

.jivan-user-time {{
    font-size: 0.72rem;
    color: {"#93C5FD" if is_dark else "#94A3B8"};
    margin-top: 5px;
    text-align: right;
}}

.jivan-user-avatar {{
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background-color: #008080;
    color: white;
    font-size: 0.8rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

/* Assistant Message */
.jivan-ai-avatar {{
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background-color: #0A1128;
    color: #FFFFFF;
    font-size: 0.92rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
}}

/* =========================================================================
   5. ASK A QUESTION COMPOSER BOX - 100% PURE BRIGHT WHITE IN BRIGHT MODE
   ========================================================================= */
div[data-testid="stChatInput"],
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] textarea,
div[data-testid="stChatInput"] [data-baseweb="textarea"],
div[data-testid="stChatInput"] [data-baseweb="base-input"] {{
    background-color: {input_bg} !important;
    background: {input_bg} !important;
    color: {input_text} !important;
    -webkit-text-fill-color: {input_text} !important;
}}

div[data-testid="stChatInput"] {{
    border: 1.5px solid {input_border} !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 14px rgba(0, 0, 0, 0.06) !important;
    padding: 6px 10px !important;
    margin-top: 8px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}}

div[data-testid="stChatInput"]:focus-within {{
    border-color: #008080 !important;
    box-shadow: 0 4px 20px rgba(0, 128, 128, 0.2) !important;
}}

div[data-testid="stChatInput"] textarea {{
    font-family: inherit !important;
    font-size: 0.98rem !important;
    font-weight: 500 !important;
    line-height: 1.45 !important;
    caret-color: #008080 !important;
    border: none !important;
    box-shadow: none !important;
    user-select: text !important;
    -webkit-user-select: text !important;
}}

div[data-testid="stChatInput"] textarea::placeholder {{
    color: {text_secondary} !important;
    -webkit-text-fill-color: {text_secondary} !important;
    opacity: 1 !important;
}}

div[data-testid="stChatInput"] button {{
    background-color: #008080 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    border: none !important;
    transition: background 0.2s ease !important;
}}

div[data-testid="stChatInput"] button:hover {{
    background-color: #006666 !important;
}}

/* =========================================================================
   6. RIGHT PANEL (SOURCES & DETAILS) - FIXED STICKY POSITION
   ========================================================================= */
div[data-testid="column"]:nth-of-type(2) {{
    position: sticky !important;
    top: 1rem !important;
    max-height: calc(100vh - 2rem) !important;
    overflow-y: auto !important;
}}

.st-key-tab_sources button,
.st-key-tab_details button {{
    background: transparent !important;
    border: none !important;
    border-radius: 0px !important;
    box-shadow: none !important;
    border-bottom: 2px solid transparent !important;
    font-weight: 600 !important;
    font-size: 0.94rem !important;
    color: {text_secondary} !important;
    padding-bottom: 8px !important;
    transition: all 0.2s ease !important;
}}

.st-key-tab_sources button:hover,
.st-key-tab_details button:hover {{
    color: #008080 !important;
}}

/* Document cards */
.jivan-source-card {{
    background-color: {bg_card};
    border: 1px solid {border_color};
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.2s ease;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
}}

.jivan-source-card:hover {{
    border-color: #008080;
    transform: translateX(2px);
}}

.jivan-doc-badge {{
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}}

.jivan-badge-pdf {{
    background-color: #FEE2E2;
    color: #DC2626;
}}

.jivan-badge-xlsx {{
    background-color: #DCFCE7;
    color: #16A34A;
}}

.jivan-badge-docx {{
    background-color: #E0E7FF;
    color: #4F46E5;
}}

.jivan-source-meta {{
    flex: 1;
    overflow: hidden;
}}

.jivan-source-title {{
    font-size: 0.88rem;
    font-weight: 600;
    color: {text_primary};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.jivan-source-subtitle {{
    font-size: 0.74rem;
    color: {text_secondary};
    margin-top: 2px;
}}

.jivan-citation-count {{
    background-color: {border_color};
    color: {text_secondary};
    font-size: 0.72rem;
    font-weight: 600;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}}

/* Details Section */
.jivan-details-group {{
    margin-top: 20px;
    border-top: 1px solid {border_color};
    padding-top: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}}

.jivan-detail-row {{
    display: flex;
    flex-direction: column;
    gap: 2px;
}}

.jivan-detail-label {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: {text_secondary};
    font-weight: 600;
}}

.jivan-detail-val {{
    font-size: 0.88rem;
    color: {text_primary};
    font-weight: 500;
}}

/* =========================================================================
   7. KEYFRAME ANIMATIONS
   ========================================================================= */
@keyframes fadeIn {{
    from {{
        opacity: 0;
        transform: translateY(6px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@keyframes slideUpFadeIn {{
    from {{
        opacity: 0;
        transform: translateY(10px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}
</style>
"""
