import streamlit as st
import os
from config import GEMINI_API_KEYS, ANTHROPIC_API_KEY, MATCH_THRESHOLD, AUTO_DECISION_CONFIDENCE

def show_settings_ui():
    st.title("⚙️ الإعدادات والتحكم (V27 + Zero-Error)")
    
    tab1, tab2, tab3 = st.tabs(["🔑 مفاتيح AI المزدوجة", "⚖️ قواعد المطابقة", "🛠️ النظام"])
    
    with tab1:
        st.subheader("إدارة المحركات (Dual-Engine)")
        
        # Anthropic (المحرك المفضل)
        st.markdown("### 🟠 Anthropic Claude (المحرك المفضل للسيو)")
        a_key = st.text_input("Anthropic API Key", value=ANTHROPIC_API_KEY, type="password", help="يستخدم في توليد الأوصاف الاحترافية وتنسيق الأسماء.")
        if a_key:
            st.success("✅ مفتاح Anthropic نشط (الأولية له حالياً).")
        else:
            st.warning("⚠️ لم يتم ضبط مفتاح Anthropic. سيتم استخدام Gemini كبديل.")
            
        st.divider()
        
        # Gemini (المحرك الاحتياطي)
        st.markdown("### 🔵 Google Gemini (المحرك الاحتياطي)")
        for i, key in enumerate(GEMINI_API_KEYS):
            masked_key = f"{key[:8]}...{key[-4:]}"
            st.code(masked_key, language="text")
        
        st.info("💡 يتم جلب المفاتيح حالياً من ملف `config.py` أو `secrets` الحيوية.")
        
    with tab2:
        st.subheader("إعدادات محرك المطابقة والحاجز الذكي")
        new_threshold = st.slider("عتبة المطابقة الفوزي (Fuzzy Match Threshold)", 0, 100, int(MATCH_THRESHOLD))
        new_confidence = st.slider("عتبة قرار AI التلقائي (AI Confidence)", 0, 100, int(AUTO_DECISION_CONFIDENCE))
        
        st.divider()
        st.markdown("### 🛡️ سياسة صفر خطأ (Zero-Error Policy)")
        st.write("- **الحد الأدنى للحجم**: 15 مل (أقل من ذلك يعتبر عينات ويتم حجبه).")
        st.write("- **حماية التستر**: التسترات تمر دائماً كفرص ربحية.")
        st.write("- **حجب الكلمات**: سمبل، مجاني، تقسيط، تمارا (يتم حجبها آلياً).")
        
    with tab3:
        st.subheader("معلومات النظام")
        st.write(f"📁 مسار العمل: `{os.getcwd()}`")
        st.write(f"📊 قاعدة البيانات الشغالة: `mahwous_v27.db` (WAL Mode Enabled)")
        
        if st.button("🔴 مسح السجلات المؤقتة (Clear Logs)", type="secondary"):
            st.warning("تم إرسال أمر مسح السجلات...")
