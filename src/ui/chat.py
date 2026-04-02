import streamlit as st
from ..engines.ai_core import ai

def show_chat_ui():
    st.title("🤖 خبير مبيعات مهووس (Smart Expert)")
    st.markdown("تحاور مع الذكاء الاصطناعي لتحليل استراتيجياتك ورفع مبيعاتك.")

    # 1. جلب سياق البيانات (إذا وجد)
    context_info = ""
    if "analysis_results" in st.session_state:
        df = st.session_state.analysis_results
        total = len(df)
        lower = len(df[df['status'] == 'lower'])
        higher = len(df[df['status'] == 'higher'])
        context_info = f"\nسياق البيانات الحالي: لديك {total} منتج محلل. {lower} منتج سعرنا أقل، {higher} منتج سعرنا أعلى."

    # عرض التاريخ بتنسيق جميل (بحد أقصى 15 رسالة للحفاظ على السياق)
    if len(st.session_state.chat_history) > 16:
        st.session_state.chat_history = st.session_state.chat_history[-16:]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 3. الأزرار السريعة (V26 Style)
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    quick_prompt = None
    if c1.button("📑 ملخص الوضع", use_container_width=True): quick_prompt = "أعطني ملخصاً بيانياً واحترافياً لوضعي التنافسي الحالي."
    if c2.button("🎯 أكبر الفرص", use_container_width=True): quick_prompt = "ما هي أكبر 5 فرص لزيادة المبيعات الآن؟"
    if c3.button("📦 سد الفجوات", use_container_width=True): quick_prompt = "حلل المنتجات المفقودة واقترح خطة لطلبها."
    if c4.button("🧠 منطق التسعير", use_container_width=True): quick_prompt = "اشرح لي المنطق النفسي المتبع في تسعير العطور الفاخرة."

    # المدخلات
    prompt = st.chat_input("اسأل خبير مهووس...")
    if quick_prompt: prompt = quick_prompt

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # بناء البرومبت مع السياق
        full_prompt = f"{prompt}\n{context_info}"
        
        # استدعاء Gemini
        with st.chat_message("assistant"):
            with st.spinner("جاري استحضار الحكمة البيعية..."):
                system_instr = (
                    "أنت خبير مبيعات وتسعير عطور محترف في متجر مهووس بالسعودية. "
                    "تحدث بلهجة احترافية حماسية. ركز على زيادة الربحية والتنافسية. "
                    "إذا كان هناك سياق بيانات، استخدمه في إجابتك."
                )
                response = ai.call_gemini(full_prompt, system_instruction=system_instr, response_type="text")
                if response:
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                else:
                    st.error("عذراً، المحرك مشغول حالياً. حاول مراسلتي لاحقاً.")
