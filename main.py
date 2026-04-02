import streamlit as st
import os
from src.ui.styles import get_styles
from src.utils.mahwous_logging import configure_logging
from src.utils.db_manager import db
from config import APP_TITLE, APP_ICON, VERSION

# 1. إعدادات الصفحة والتسجيل
st.set_page_config(
    page_title=f"{APP_TITLE} {VERSION}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)
configure_logging()

# 2. حقن الاستايلات (CSS)
st.markdown(get_styles(), unsafe_allow_html=True)

# 3. إعداد حالة الجلسة (Session State)
if "current_page" not in st.session_state:
    st.session_state.current_page = "📊 لوحة التحكم"

# 4. شريط التنقل الجانبي (Sidebar Navigation)
with st.sidebar:
    st.markdown(f"<h1 style='text-align: center;'>{APP_ICON} {APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #888;'>النسخة {VERSION}</p>", unsafe_allow_html=True)
    st.divider()
    
    pages = {
        "📊 لوحة التحكم": "dashboard",
        "🔍 تحليل المنافسين": "competitors",
        "🕸️ الكشط الذكي": "scraper",
        "📦 المفقودات": "missing",
        "🪄 أدوات الذكاء الاصطناعي": "ai_tools",
        "🛠️ التدقيق والتحسين": "audit",
        "🤖 المحادثة الذكية": "chat",
        "⚙️ الإعدادات": "settings"
    }
    
    selection = st.radio("القائمة الرئيسية", list(pages.keys()))
    st.session_state.current_page = selection
    
    st.divider()
    if st.button("🔄 تصفير الجلسة (Reset)"):
        st.session_state.clear()
        st.rerun()
    
    st.info("نظام V27 المطور (Zero-Error Mode).")

# 5. التوجيه (Routing)
def main():
    page = st.session_state.current_page
    
    if page == "📊 لوحة التحكم":
        from src.ui.dashboard import show_dashboard
        show_dashboard()
    elif page == "🔍 تحليل المنافسين":
        from src.ui.competitors import show_competitors_analysis
        show_competitors_analysis()
    elif page == "🕸️ الكشط الذكي":
        from src.ui.scraper_ui import show_scraper_ui
        show_scraper_ui()
    elif page == "📦 المفقودات":
        from src.ui.missing import show_missing_products
        show_missing_products()
    elif page == "🤖 المحادثة الذكية":
        from src.ui.chat import show_chat_ui
        show_chat_ui()
    elif page == "🪄 أدوات الذكاء الاصطناعي":
        from src.ui.ai_tools import show_ai_tools_ui
        show_ai_tools_ui()
    elif page == "🛠️ التدقيق والتحسين":
        from src.ui.audit import show_audit_ui
        show_audit_ui()
    elif page == "⚙️ الإعدادات":
        from src.ui.settings import show_settings_ui
        show_settings_ui()
    else:
        st.title(page)
        st.warning("هذا القسم قيد التحديث.")

if __name__ == "__main__":
    try:
        db.log_event("main", "app_start")
    except:
        pass
    main()
