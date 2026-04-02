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

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "أهلاً بك يا بطل! أنا خبير مبيعات مهووس. لقد فحصت بياناتك وأنا مستعد لمساعدتك في اكتساح السوق. ماذا تريد أن نحلل اليوم؟"}
        ]

    # عرض التاريخ بتنسيق جميل
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # المدخلات
    if prompt := st.chat_input("اسأل خبير مهووس..."):
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
