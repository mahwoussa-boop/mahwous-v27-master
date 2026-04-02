def get_styles():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Noto+Sans+Arabic:wght@300;400;700&display=swap');
    
    :root {
        --primary: #5C6BC0;
        --secondary: #1A237E;
        --accent: #FFD600;
        --bg-dark: #0E1117;
        --card-bg: #1A1C23;
        --text-main: #E0E0E0;
    }
    
    * { font-family: 'Outfit', 'Noto Sans Arabic', sans-serif; }
    
    .stApp { background-color: var(--bg-dark); color: var(--text-main); }
    
    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, #1e1e2d 0%, #161622 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: transform 0.3s ease;
    }
    .stat-card:hover { transform: translateY(-5px); border-color: var(--primary); }
    
    .stat-val { font-size: 2.2rem; font-weight: 800; color: var(--accent); margin: 0; }
    .stat-label { font-size: 0.9rem; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0B0E14;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, var(--secondary), var(--primary));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 700;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(92,107,192,0.4); }
    </style>
    """

def stat_card(label, value, icon="📈"):
    return f"""
    <div class="stat-card">
        <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
        <div class="stat-label">{label}</div>
        <div class="stat-val">{value}</div>
    </div>
    """
