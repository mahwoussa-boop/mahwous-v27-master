def product_result_card(row):
    """بطاقة عرض نتيجة المطابقة بشكل احترافي"""
    status_colors = {
        "lower": ("#4CAF50", "سعر أقل 🟢", "border-left: 5px solid #4CAF50;"),
        "higher": ("#F44336", "سعر أعلى 🔴", "border-left: 5px solid #F44336;"),
        "approved": ("#2196F3", "مطابق ✅", "border-left: 5px solid #2196F3;"),
        "missing": ("#9E9E9E", "مفقود ⚪", "border-left: 5px solid #9E9E9E;"),
        "review": ("#FF9800", "للمراجعة ⚠️", "border-left: 5px solid #FF9800;")
    }
    
    color, label, border = status_colors.get(row['status'], ("#fff", "غير معروف", ""))
    ai_badge = f"<span style='background:#E91E63; color:white; padding:2px 8px; border-radius:10px; font-size:0.7rem;'>AI Verified</span>" if row.get('ai_verified') else ""
    
    return f"""
    <div style="background: #1A1C23; padding: 20px; border-radius: 12px; margin-bottom: 12px; {border}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h4 style="margin: 0; color: #E0E0E0;">{row['our_name']}</h4>
                <p style="color: #888; font-size: 0.85rem; margin-top: 4px;">ID: {row['our_id']} | {ai_badge}</p>
            </div>
            <div style="text-align: right;">
                <div style="color: {color}; font-weight: 800; font-size: 1.1rem;">{label}</div>
                <div style="color: #FFD600; font-size: 1.2rem; font-weight: 700;">{row['our_price']} ريال</div>
            </div>
        </div>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin: 15px 0;">
        <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
            <div style="color: #aaa;">المنافس: <span style="color: #fff;">{row['match_name']}</span></div>
            <div style="color: #aaa;">سعر المنافس: <span style="color: #FFD600; font-weight: 700;">{row['comp_price']} ريال</span></div>
        </div>
        <div style="margin-top: 15px; display: flex; gap: 10px;">
            <button style="background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; color: #4CAF50; padding: 5px 15px; border-radius: 8px; font-size: 0.8rem; cursor: pointer;">موافقة</button>
            <button style="background: rgba(244, 67, 54, 0.1); border: 1px solid #F44336; color: #F44336; padding: 5px 15px; border-radius: 8px; font-size: 0.8rem; cursor: pointer;">رفض</button>
        </div>
    </div>
    """

def upload_placeholder():
    return """
    <div style="border: 2px dashed #3F51B5; border-radius: 12px; padding: 40px; text-align: center; color: #888;">
        <div style="font-size: 3rem; margin-bottom: 10px;">📄</div>
        <h4>ارفع ملف المنافس للبدء</h4>
        <p>يدعم ملفات Excel و CSV المستخرجة من أنظمة الكشط</p>
    </div>
    """
