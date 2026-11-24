"""
JIVAN AI - Centralized Light & Dark Mode Stylesheet
Features:
- Centralized CSS Variables:
  * Light Mode: #FFFFFF main, #F5F7FA secondary, #F0F3F8 cards, #202124 text, #737780 secondary text, #E1E5EB borders
  * Dark Mode: #121212 main, #181818 secondary, #202124 cards, #F5F5F5 text, #A1A1AA secondary text, #303030 borders
  * Accent: JIVAN Blue (#1D61D2) preserved across both themes
  * Message Composer: #212121 charcoal preserved in both themes
- 250ms smooth transition across background-color, color, border-color, and box-shadow
- Theme persistence via localStorage and prefers-color-scheme detection
- Custom styling for all app components: Top bar, Cards, Sidebar, Chat feed, Popovers, Scrollbars, Inputs
"""

def get_jivan_css(theme_mode: str = "light") -> str:
    is_dark = (str(theme_mode).lower() in ("dark", "obsidian", "night"))
    active_theme = "dark" if is_dark else "light"

    return f"""
<script>
(function() {{
  const THEME_KEY = 'jivan_theme';
  
  function getSystemTheme() {{
    return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  }}
  
  function getEffectiveTheme() {{
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === 'dark' || saved === 'light') return saved;
    return getSystemTheme();
  }}

  const effectiveTheme = getEffectiveTheme();
  
  // Apply data-theme immediately to root and body to eliminate flash
  document.documentElement.setAttribute('data-theme', effectiveTheme);
  if (document.body) {{
    document.body.setAttribute('data-theme', effectiveTheme);
    document.body.classList.remove('theme-light', 'theme-dark');
    document.body.classList.add('theme-' + effectiveTheme);
  }}

  // Keep query param in sync with active theme
  const url = new URL(window.location.href);
  const currentParam = url.searchParams.get('theme');
  if (currentParam && currentParam !== effectiveTheme && (currentParam === 'dark' || currentParam === 'light')) {{
    localStorage.setItem(THEME_KEY, currentParam);
    document.documentElement.setAttribute('data-theme', currentParam);
    if (document.body) {{
      document.body.setAttribute('data-theme', currentParam);
      document.body.classList.remove('theme-light', 'theme-dark');
      document.body.classList.add('theme-' + currentParam);
    }}
  }} else if (!currentParam) {{
    url.searchParams.set('theme', effectiveTheme);
    window.history.replaceState(null, '', url.toString());
  }}

  // Listen to OS prefers-color-scheme change if user hasn't explicitly chosen
  if (window.matchMedia) {{
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {{
      if (!localStorage.getItem(THEME_KEY)) {{
        const newSys = e.matches ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newSys);
        const u = new URL(window.location.href);
        u.searchParams.set('theme', newSys);
        window.location.href = u.toString();
      }}
    }});
  }}
}})();
</script>

<style>
/* =========================================================================
   1. CENTRALIZED THEME CSS VARIABLES
   ========================================================================= */
:root {{
    /* Default fallback variables based on active server evaluation */
    --bg-primary: {"#121212" if is_dark else "#FFFFFF"};
    --bg-secondary: {"#181818" if is_dark else "#F5F7FA"};
    --bg-card: {"#202124" if is_dark else "#F0F3F8"};
    --bg-card-hover: {"#2A2B2E" if is_dark else "#E8EEF5"};
    --text-primary: {"#F5F5F5" if is_dark else "#202124"};
    --text-secondary: {"#A1A1AA" if is_dark else "#737780"};
    --text-muted: {"#71717A" if is_dark else "#8E918F"};
    --border-color: {"#303030" if is_dark else "#E1E5EB"};
    --border-subtle: {"rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)"};
    --accent-color: #1D61D2;
    --accent-hover: #1852B5;
    --composer-bg: #212121;
    --user-bubble-bg: {"#202124" if is_dark else "#F0F3F8"};
    --user-bubble-text: {"#F5F5F5" if is_dark else "#202124"};
    --scrollbar-thumb: {"#3F3F46" if is_dark else "#D1D5DB"};
    --scrollbar-track: {"#121212" if is_dark else "#FFFFFF"};
    --input-bg: {"#181818" if is_dark else "#FFFFFF"};
    --input-border: {"#303030" if is_dark else "#E1E5EB"};
    --gemini-gradient: {"linear-gradient(90deg, #8AB4F8 0%, #C58AF9 50%, #F28B82 100%)" if is_dark else "linear-gradient(74deg, #4285F4 0%, #9B72CF 35%, #D96570 70%, #1A73E8 100%)"};
    --gemini-sparkle-gradient: {"linear-gradient(135deg, #8AB4F8 0%, #C58AF9 50%, #F28B82 100%)" if is_dark else "linear-gradient(135deg, #4285F4 0%, #9B72CF 50%, #D96570 100%)"};
    --btn-new-chat-bg: {"#202124" if is_dark else "#E1EAF8"};
    --btn-new-chat-text: {"#F5F5F5" if is_dark else "#041E49"};
    --btn-new-chat-hover: {"#2C2D30" if is_dark else "#D0E0F7"};
}}

/* Light Theme Variables */
[data-theme="light"], .stApp[data-theme="light"], body.theme-light {{
    --bg-primary: #FFFFFF;
    --bg-secondary: #F5F7FA;
    --bg-card: #F0F3F8;
    --bg-card-hover: #E8EEF5;
    --text-primary: #202124;
    --text-secondary: #737780;
    --text-muted: #8E918F;
    --border-color: #E1E5EB;
    --border-subtle: rgba(0, 0, 0, 0.08);
    --accent-color: #1D61D2;
    --accent-hover: #1852B5;
    --composer-bg: #212121;
    --user-bubble-bg: #F0F3F8;
    --user-bubble-text: #202124;
    --scrollbar-thumb: #D1D5DB;
    --scrollbar-track: #FFFFFF;
    --input-bg: #FFFFFF;
    --input-border: #E1E5EB;
    --gemini-gradient: linear-gradient(74deg, #4285F4 0%, #9B72CF 35%, #D96570 70%, #1A73E8 100%);
    --gemini-sparkle-gradient: linear-gradient(135deg, #4285F4 0%, #9B72CF 50%, #D96570 100%);
    --btn-new-chat-bg: #E1EAF8;
    --btn-new-chat-text: #041E49;
    --btn-new-chat-hover: #D0E0F7;
}}

/* Dark Theme Variables */
[data-theme="dark"], .stApp[data-theme="dark"], body.theme-dark {{
    --bg-primary: #121212;
    --bg-secondary: #181818;
    --bg-card: #202124;
    --bg-card-hover: #2A2B2E;
    --text-primary: #F5F5F5;
    --text-secondary: #A1A1AA;
    --text-muted: #71717A;
    --border-color: #303030;
    --border-subtle: rgba(255, 255, 255, 0.08);
    --accent-color: #1D61D2;
    --accent-hover: #1852B5;
    --composer-bg: #212121;
    --user-bubble-bg: #202124;
    --user-bubble-text: #F5F5F5;
    --scrollbar-thumb: #3F3F46;
    --scrollbar-track: #121212;
    --input-bg: #181818;
    --input-border: #303030;
    --gemini-gradient: linear-gradient(90deg, #8AB4F8 0%, #C58AF9 50%, #F28B82 100%);
    --gemini-sparkle-gradient: linear-gradient(135deg, #8AB4F8 0%, #C58AF9 50%, #F28B82 100%);
    --btn-new-chat-bg: #202124;
    --btn-new-chat-text: #F5F5F5;
    --btn-new-chat-hover: #2C2D30;
}}

/* =========================================================================
   2. SMOOTH GLOBAL THEME TRANSITIONS (250ms)
   ========================================================================= */
.stApp,
section[data-testid="stSidebar"],
.gemini-model-badge,
.gemini-user-bubble,
.gemini-profile-pill,
div[data-testid="stExpander"],
div[data-testid="stMetricValue"],
div[data-testid="stMetricLabel"],
div[data-testid="stPopoverBody"],
.st-key-btn_topbar_theme_toggle button,
.st-key-btn_topbar_pin button,
.st-key-btn_topbar_share button,
.st-key-btn_topbar_inspector button,
.st-key-btn_topbar_clear button,
.st-key-gemini_card_code button,
.st-key-gemini_card_slides button,
.st-key-gemini_card_art button,
.st-key-gemini_card_doc button,
div[class*="st-key-jivan_conv_"] button,
.st-key-jivan_btn_new_chat button,
.st-key-nav_conversations button,
.st-key-nav_knowledge button,
.st-key-nav_tasks button,
.st-key-nav_templates button,
.st-key-nav_settings button {{
    transition: background-color 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                border-color 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                color 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}

/* =========================================================================
   3. GLOBAL RESETS & FONTS
   ========================================================================= */
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&family=Roboto:wght@300;400;500;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, p, div:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded), input, textarea {{
    font-family: 'Google Sans', 'Roboto', 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}}

/* Suppress unrendered icon font ligatures */
[data-testid="stIconMaterial"],
.material-symbols-rounded,
div[data-testid="stPopover"] span[data-testid="stIconMaterial"],
div[data-testid="stPopover"] .material-symbols-rounded {{
    display: none !important;
    visibility: hidden !important;
    font-size: 0px !important;
    width: 0 !important;
    height: 0 !important;
}}

/* Streamlit Header & Toolbar Reset */
header[data-testid="stHeader"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    height: 0px !important;
    min-height: 0px !important;
}}

#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{
    display: none !important;
    visibility: hidden !important;
}}

/* App Canvas */
.stApp {{
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}}

.block-container {{
    padding-top: 1rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}}

/* =========================================================================
   4. SIDEBAR STYLING
   ========================================================================= */
section[data-testid="stSidebar"] {{
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-right: 1px solid var(--border-color) !important;
}}

section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {{
    padding: 1.2rem 0.9rem !important;
}}

/* Collapse Hamburger Button */
[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"] {{
    display: flex !important;
    visibility: visible !important;
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    z-index: 999999 !important;
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-radius: 50% !important;
    width: 40px !important;
    height: 40px !important;
    border: 1px solid var(--border-color) !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
    transition: background 0.2s ease !important;
}}

[data-testid="collapsedControl"]:hover,
button[data-testid="stSidebarCollapseButton"]:hover {{
    background: var(--bg-card-hover) !important;
}}

[data-testid="collapsedControl"] svg,
button[data-testid="stSidebarCollapseButton"] svg {{
    fill: var(--text-primary) !important;
    stroke: var(--text-primary) !important;
}}

/* Brand Header */
.gemini-brand-wrapper {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 6px 14px 6px;
    margin-bottom: 10px;
    border-bottom: 1px solid var(--border-subtle);
}}

.gemini-sparkle-logo {{
    width: 32px;
    height: 32px;
    border-radius: 10px;
    background: var(--gemini-sparkle-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 700;
    box-shadow: 0 2px 10px rgba(66, 133, 244, 0.35);
}}

.gemini-brand-title {{
    font-size: 1.35rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 6px;
}}

.gemini-brand-badge {{
    font-size: 0.68rem;
    font-weight: 600;
    background: var(--gemini-sparkle-gradient);
    color: #FFFFFF;
    padding: 2px 7px;
    border-radius: 12px;
    letter-spacing: 0.02em;
}}

/* '+ New chat' Capsule Pill */
.st-key-jivan_btn_new_chat button {{
    background: var(--btn-new-chat-bg) !important;
    color: var(--btn-new-chat-text) !important;
    -webkit-text-fill-color: var(--btn-new-chat-text) !important;
    border: none !important;
    border-radius: 28px !important;
    font-weight: 500 !important;
    font-size: 0.94rem !important;
    padding: 0.65rem 1.2rem !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
    transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}}

.st-key-jivan_btn_new_chat button:hover {{
    background: var(--btn-new-chat-hover) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12) !important;
    transform: translateY(-1px) !important;
}}

/* Navigation Links */
.st-key-nav_conversations button,
.st-key-nav_knowledge button,
.st-key-nav_tasks button,
.st-key-nav_templates button,
.st-key-nav_settings button {{
    background: transparent !important;
    border: none !important;
    border-radius: 24px !important;
    color: var(--text-secondary) !important;
    -webkit-text-fill-color: var(--text-secondary) !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 9px 14px !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}}

.st-key-nav_conversations button:hover,
.st-key-nav_knowledge button:hover,
.st-key-nav_tasks button:hover,
.st-key-nav_templates button:hover,
.st-key-nav_settings button:hover {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
}}

.gemini-sidebar-heading {{
    font-size: 0.76rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin: 18px 0 8px 10px;
}}

/* Recent Chats Items */
div[class*="st-key-jivan_conv_"] button {{
    background: transparent !important;
    border: none !important;
    border-radius: 20px !important;
    color: var(--text-secondary) !important;
    -webkit-text-fill-color: var(--text-secondary) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 8px 12px !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    transition: all 0.15s ease !important;
}}

div[class*="st-key-jivan_conv_"] button:hover {{
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
}}

div[class*="st-key-jivan_del_"] button {{
    background: transparent !important;
    border: none !important;
    border-radius: 50% !important;
    color: var(--text-muted) !important;
    -webkit-text-fill-color: var(--text-muted) !important;
    padding: 6px !important;
}}

div[class*="st-key-jivan_del_"] button:hover {{
    color: #DC2626 !important;
    -webkit-text-fill-color: #DC2626 !important;
    background: rgba(220, 38, 38, 0.1) !important;
}}

/* Theme Toggle Segmented Control in Sidebar */
.st-key-btn_theme_bright button,
.st-key-btn_theme_dark button {{
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 20px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
}}

.st-key-btn_theme_bright button:hover,
.st-key-btn_theme_dark button:hover {{
    background: var(--bg-card-hover) !important;
    border-color: var(--accent-color) !important;
}}

/* User Profile Pill */
.gemini-profile-pill {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 24px;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    margin-top: 10px;
    transition: all 0.2s ease;
}}

.gemini-profile-pill:hover {{
    background: var(--bg-card-hover);
}}

.gemini-avatar-circle {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--gemini-sparkle-gradient);
    color: #FFFFFF;
    font-weight: 600;
    font-size: 0.82rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.gemini-profile-email {{
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.gemini-profile-status {{
    font-size: 0.70rem;
    color: var(--text-muted);
}}

/* =========================================================================
   5. TOP NAVIGATION BAR & THEME TOGGLE BUTTON
   ========================================================================= */
.gemini-top-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 18px;
}}

.gemini-model-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 20px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    font-size: 0.95rem;
    font-weight: 500;
    cursor: default;
}}

.gemini-model-sparkle {{
    font-size: 1.05rem;
    background: var(--gemini-sparkle-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

/* Top-Right Action Buttons */
.st-key-btn_topbar_pin button,
.st-key-btn_topbar_share button,
.st-key-btn_topbar_inspector button,
.st-key-btn_topbar_clear button,
.st-key-btn_topbar_theme_toggle button {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 20px !important;
    color: var(--text-secondary) !important;
    -webkit-text-fill-color: var(--text-secondary) !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 6px 12px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
}}

.st-key-btn_topbar_pin button:hover,
.st-key-btn_topbar_share button:hover,
.st-key-btn_topbar_inspector button:hover,
.st-key-btn_topbar_clear button:hover,
.st-key-btn_topbar_theme_toggle button:hover {{
    background: var(--bg-card-hover) !important;
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
    border-color: var(--accent-color) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.10) !important;
}}

/* Special Theme Toggle Styling */
.st-key-btn_topbar_theme_toggle button {{
    font-weight: 600 !important;
    border-color: var(--accent-color) !important;
}}

/* =========================================================================
   6. HERO WELCOME SCREEN & SUGGESTION CARDS
   ========================================================================= */
.gemini-hero-container {{
    text-align: left;
    max-width: 860px;
    margin: 40px auto 30px auto;
    padding: 0 16px;
}}

.gemini-hero-greeting {{
    font-size: 3.2rem;
    font-weight: 500;
    line-height: 1.18;
    letter-spacing: -0.02em;
    margin-bottom: 6px;
}}

.gemini-gradient-text {{
    background: var(--gemini-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
}}

.gemini-hero-subgreeting {{
    font-size: 3.2rem;
    font-weight: 500;
    line-height: 1.18;
    letter-spacing: -0.02em;
    color: var(--text-muted);
    margin-bottom: 34px;
}}

/* 4 Suggestion Cards */
.gemini-cards-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-top: 24px;
    max-width: 860px;
    margin-left: auto;
    margin-right: auto;
}}

.st-key-gemini_card_code button,
.st-key-gemini_card_slides button,
.st-key-gemini_card_art button,
.st-key-gemini_card_doc button {{
    background-color: var(--bg-card) !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 16px 14px !important;
    min-height: 120px !important;
    text-align: left !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
    width: 100% !important;
}}

.st-key-gemini_card_code button:hover,
.st-key-gemini_card_slides button:hover,
.st-key-gemini_card_art button:hover,
.st-key-gemini_card_doc button:hover {{
    background: var(--bg-card-hover) !important;
    border-color: var(--accent-color) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
}}

/* =========================================================================
   7. CHAT MESSAGES STREAM
   ========================================================================= */
.gemini-chat-container {{
    max-width: 860px;
    margin: 0 auto;
}}

.gemini-user-row {{
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
    gap: 12px;
    margin-bottom: 22px;
    margin-top: 10px;
}}

.gemini-user-bubble {{
    background-color: var(--user-bubble-bg);
    color: var(--user-bubble-text);
    border: 1px solid var(--border-color);
    border-radius: 24px 24px 6px 24px;
    padding: 14px 20px;
    max-width: 80%;
    font-size: 0.98rem;
    line-height: 1.55;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}

.gemini-user-avatar {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--accent-color);
    color: #FFFFFF;
    font-size: 0.8rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.gemini-asst-row {{
    display: flex;
    gap: 14px;
    margin-bottom: 24px;
    align-items: flex-start;
}}

.gemini-asst-sparkle {{
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: var(--gemini-sparkle-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-size: 15px;
    flex-shrink: 0;
    margin-top: 2px;
    box-shadow: 0 2px 8px rgba(66, 133, 244, 0.3);
}}

.gemini-asst-content {{
    flex: 1;
    overflow: hidden;
    font-size: 1rem;
    line-height: 1.65;
    color: var(--text-primary);
}}

.gemini-specialist-tag {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--accent-color);
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    padding: 3px 9px;
    border-radius: 12px;
    margin-bottom: 8px;
}}

/* Message Action Buttons */
.st-key-btn_copy_msg button,
.st-key-btn_like_msg button,
.st-key-btn_dislike_msg button,
div[class*="st-key-copy_"] button,
div[class*="st-key-like_"] button,
div[class*="st-key-dislike_"] button {{
    background: transparent !important;
    border: none !important;
    color: var(--text-muted) !important;
    -webkit-text-fill-color: var(--text-muted) !important;
    border-radius: 50% !important;
    width: 34px !important;
    height: 34px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0.92rem !important;
    transition: all 0.15s ease !important;
}}

div[class*="st-key-copy_"] button:hover,
div[class*="st-key-like_"] button:hover,
div[class*="st-key-dislike_"] button:hover {{
    background: var(--bg-card) !important;
    color: var(--accent-color) !important;
    -webkit-text-fill-color: var(--accent-color) !important;
}}

.gemini-grounding-chip {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 4px 12px;
    font-size: 0.80rem;
    color: var(--text-secondary);
    margin: 4px 6px 4px 0;
}}

/* =========================================================================
   8. COMPOSER IFRAME INTEGRATION (Preserved #212121 Charcoal Dock)
   ========================================================================= */
.gemini-composer-wrapper {{
    max-width: 860px;
    margin: 0 auto;
    position: relative;
    padding: 0 4px;
}}

iframe[title*="jivan_chatgpt_composer"],
iframe[src*="jivan_chatgpt_composer"],
div[data-testid="stCustomComponentV1"] {{
    width: 100% !important;
    max-width: 860px !important;
    margin: 0 auto !important;
    border: none !important;
    display: block !important;
}}

/* Popover surfaces in theme */
div[data-testid="stPopoverBody"] {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25) !important;
    padding: 14px 16px !important;
}}

/* Thinking Box */
.jivan-thinking-box {{
    background: rgba(29, 97, 210, 0.08);
    border-left: 3px solid var(--accent-color);
    border-radius: 8px;
    padding: 8px 14px;
    margin-bottom: 12px;
    font-size: 0.86rem;
    color: var(--accent-color);
}}

/* Disclaimer */
.gemini-disclaimer {{
    font-size: 0.72rem;
    color: var(--text-muted);
    text-align: center;
    margin-top: 10px;
    letter-spacing: 0.01em;
}}

/* =========================================================================
   9. STREAMLIT EXPANDERS, METRICS, AND INPUTS
   ========================================================================= */
div[data-testid="stExpander"] {{
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 14px !important;
    color: var(--text-primary) !important;
}}

div[data-testid="stExpander"] summary {{
    color: var(--text-primary) !important;
}}

div[data-testid="stMetricValue"] {{
    color: var(--text-primary) !important;
}}

div[data-testid="stMetricLabel"] {{
    color: var(--text-secondary) !important;
}}

input, textarea, div[data-baseweb="select"] > div {{
    background-color: var(--input-bg) !important;
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
    border-color: var(--input-border) !important;
}}

hr {{
    border-color: var(--border-color) !important;
}}

/* =========================================================================
   10. SCROLLBARS
   ========================================================================= */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--scrollbar-track) !important;
}}

::-webkit-scrollbar-thumb {{
    background: var(--scrollbar-thumb) !important;
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--text-muted) !important;
}}

/* =========================================================================
   11. RESPONSIVE MEDIA QUERIES
   ========================================================================= */
@media (max-width: 992px) {{
    .gemini-cards-grid {{
        grid-template-columns: repeat(2, 1fr) !important;
    }}
    .gemini-hero-greeting,
    .gemini-hero-subgreeting {{
        font-size: 2.4rem !important;
    }}
}}

@media (max-width: 768px) {{
    .block-container {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 3.5rem !important;
    }}
    .gemini-cards-grid {{
        grid-template-columns: 1fr !important;
    }}
    .gemini-hero-greeting,
    .gemini-hero-subgreeting {{
        font-size: 1.85rem !important;
    }}
    .gemini-user-bubble {{
        max-width: 90% !important;
    }}
}}
</style>
"""
