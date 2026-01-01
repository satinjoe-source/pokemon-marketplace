import streamlit as st
import hashlib
import base64
import time
from datetime import datetime as dt
from sqlalchemy import create_engine, text
from datetime import datetime

# ==================== CONFIG ====================
st.set_page_config(
    page_title="Pokemon Portal ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS GIOVANI GEN Z ====================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&family=Press+Start+2P&display=swap');

    /* PALETTE CYBER GEN Z */
    :root {
        --cyber-green: #00FF41;
        --cyber-pink: #FF006E;
        --cyber-purple: #8338EC;
        --cyber-blue: #3A86FF;
        --cyber-yellow: #FFBE0B;
        --dark-bg: #0d1117;
        --dark-card: #161b22;
        --light-bg: #ffffff;
        --light-card: #f6f8fa;
        --text-dark: #c9d1d9;
        --text-light: #24292f;
    }

    /* TEMA SCURO (default) */
    :root {
        --bg: var(--dark-bg);
        --card: var(--dark-card);
        --text: var(--text-dark);
    }

    /* TEMA CHIARO LEGGIBILE */
    @media (prefers-color-scheme: light) {
        :root {
            --bg: #f0f4ff;
            --card: var(--light-card);
            --text: var(--text-light);
            --cyber-green: #00cc33;
            --cyber-pink: #e6005c;
            --cyber-purple: #7029d4;
            --cyber-blue: #0066ff;
            --cyber-yellow: #ff9900;
        }
    }

    /* ANIMAZIONI */
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
    @keyframes slideIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes neon { 0%, 100% { text-shadow: 0 0 10px currentColor, 0 0 20px currentColor; } 50% { text-shadow: 0 0 20px currentColor, 0 0 40px currentColor; } }

    /* BACKGROUND CON PATTERN POKEMON */
    .stApp {
        background: var(--bg);
        color: var(--text);
        font-family: 'Poppins', sans-serif;
        position: relative;
    }
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(0, 255, 65, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(255, 0, 110, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(131, 56, 236, 0.05) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* POKEMON DECORATIVI FISSI */
    .pokemon-deco {
        position: fixed;
        pointer-events: none;
        z-index: 1;
        opacity: 0.3;
        animation: float 4s ease-in-out infinite;
    }
    .poke-1 { top: 10%; left: 5%; width: 80px; }
    .poke-2 { top: 60%; right: 5%; width: 100px; animation-delay: 1s; }
    .poke-3 { bottom: 10%; left: 10%; width: 70px; animation-delay: 2s; }

    /* TITOLI NEON */
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--cyber-pink), var(--cyber-purple), var(--cyber-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: neon 3s ease-in-out infinite;
        letter-spacing: 1px;
    }

    /* TOP BAR CON HOME/LOGOUT */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: rgba(13, 17, 23, 0.95);
        backdrop-filter: blur(20px);
        padding: 0.8rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        border-bottom: 2px solid var(--cyber-pink);
        box-shadow: 0 4px 20px rgba(255, 0, 110, 0.3);
    }
    .top-bar-title {
        font-family: 'Press Start 2P', cursive;
        font-size: 1.2rem;
        background: linear-gradient(90deg, var(--cyber-yellow), var(--cyber-pink));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-content {
        margin-top: 80px;
        position: relative;
        z-index: 2;
    }

    /* NAVBAR */
    .nav-container {
        background: rgba(22, 27, 34, 0.9);
        backdrop-filter: blur(15px);
        border: 3px solid transparent;
        border-image: linear-gradient(90deg, var(--cyber-pink), var(--cyber-purple), var(--cyber-blue)) 1;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 2rem auto;
        max-width: 95%;
        box-shadow: 0 10px 40px rgba(255, 0, 110, 0.2);
        animation: slideIn 0.6s ease-out;
    }

    /* CARD 3D */
    .product-card {
        background: var(--card);
        border: 3px solid transparent;
        border-image: linear-gradient(135deg, var(--cyber-pink), var(--cyber-blue)) 1;
        border-radius: 15px;
        padding: 1.2rem;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }
    .product-card::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 0, 110, 0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.5s;
    }
    .product-card:hover::before {
        left: 100%;
    }
    .product-card:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 20px 50px rgba(255, 0, 110, 0.4);
        border-image: linear-gradient(135deg, var(--cyber-yellow), var(--cyber-pink)) 1;
    }
    .product-card img {
        border-radius: 10px;
        transition: transform 0.4s;
        filter: drop-shadow(0 0 15px rgba(131, 56, 236, 0.4));
    }
    .product-card:hover img {
        transform: scale(1.1) rotate(-5deg);
    }

    /* PRICE TAG ENERGETICO */
    .price-tag {
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--cyber-yellow), var(--cyber-pink));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(255, 190, 11, 0.6);
        margin: 1rem 0;
        animation: pulse 2s ease-in-out infinite;
    }

    /* BADGE RARITÀ VIVACI */
    .rarity-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        box-shadow: 0 0 20px currentColor;
    }
    .rarity-holo { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .rarity-ultra { background: linear-gradient(135deg, var(--cyber-pink), var(--cyber-purple)); color: white; }
    .rarity-secret { background: linear-gradient(135deg, var(--cyber-yellow), #ff6b00); color: black; }
    .rarity-rara { background: linear-gradient(135deg, var(--cyber-blue), var(--cyber-green)); color: white; }

    /* HEADER PAGINA */
    .page-header {
        text-align: center;
        padding: 2rem;
        background: rgba(22, 27, 34, 0.8);
        backdrop-filter: blur(10px);
        border: 3px solid transparent;
        border-image: linear-gradient(90deg, var(--cyber-pink), var(--cyber-blue)) 1;
        border-radius: 20px;
        margin: 2rem auto;
        animation: slideIn 0.6s ease-out;
    }
    .page-header h1 { font-size: 3rem; margin: 0; }
    .page-header p { color: var(--text); font-size: 1.2rem; margin-top: 1rem; opacity: 0.8; }
    .page-header img { animation: float 3s ease-in-out infinite; }

    /* BUTTONS ENERGETICI */
    .stButton > button {
        background: linear-gradient(135deg, var(--cyber-pink), var(--cyber-purple)) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.8rem 1.5rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s !important;
        box-shadow: 0 5px 20px rgba(255, 0, 110, 0.4) !important;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 10px 40px rgba(255, 0, 110, 0.6) !important;
    }
    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }

    /* INPUTS MODERNI */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background: var(--card) !important;
        border: 2px solid var(--cyber-purple) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
        padding: 0.8rem !important;
        font-family: 'Poppins', sans-serif !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: var(--cyber-pink) !important;
        box-shadow: 0 0 20px rgba(255, 0, 110, 0.3) !important;
    }

    /* FILE UPLOADER CON CAMERA */
    .stFileUploader {
        background: var(--card);
        border: 2px dashed var(--cyber-blue);
        border-radius: 15px;
        padding: 1.5rem;
    }

    /* RESPONSIVE */
    @media (max-width: 768px) {
        .top-bar-title { font-size: 0.8rem; }
        .page-header h1 { font-size: 2rem; }
        .product-card { padding: 1rem; }
        .price-tag { font-size: 1.5rem; }
        .pokemon-deco { display: none; }
    }

    /* NASCONDI ELEMENTI STREAMLIT */
    [data-testid="stHeader"], footer, header, .viewerBadge_container__r5tak { 
        visibility: hidden !important; 
        height: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ==================== DATABASE ====================
DATABASE_URL = st.secrets.get("DATABASE_URL", "sqlite:///pokemon_marketplace.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

@st.cache_resource
def get_engine():
    return engine

def get_conn():
    return get_engine().connect()

# ==================== UTILS ====================
def to_dict_list(result):
    return [dict(row._mapping) for row in result.fetchall()]

def get_image_b64(img_data):
    """Fix immagini - gestisce bytes, memoryview, ecc."""
    if not img_data:
        return None
    try:
        if isinstance(img_data, memoryview):
            img_data = bytes(img_data)
        if isinstance(img_data, bytes):
            return base64.b64encode(img_data).decode('utf-8')
        return None
    except Exception as e:
        st.error(f"Errore immagine: {e}")
        return None

def safe_date(d):
    try:
        if not d: return "N/D"
        if isinstance(d, (datetime, dt)):
            return d.date().isoformat()
        return str(d)[:10]
    except:
        return "N/D"

def get_rarity_class(rarita):
    mapping = {
        "Holo": "rarity-holo",
        "Ultra Rara": "rarity-ultra",
        "Secret": "rarity-secret",
        "Rara": "rarity-rara"
    }
    return mapping.get(rarita, "rarity-rara")

# ==================== INIT DB ====================
def init_db():
    conn = get_conn()
    try:
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        # AGGIUNTO CAMPO DESCRIZIONE
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS carte (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            nome TEXT NOT NULL,
            rarita TEXT,
            prezzo REAL NOT NULL,
            descrizione TEXT,
            immagine BYTEA,
            sold INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        conn.commit()

        if not conn.execute(text("SELECT * FROM users WHERE email = 'admin@pokemon.com'")).fetchone():
            pw = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute(text("""
                INSERT INTO users (email, username, password, created_at)
                VALUES ('admin@pokemon.com', 'admin', :pw, CURRENT_TIMESTAMP)
            """), {"pw": pw})
            conn.commit()
    except Exception as e:
        st.error(f"Errore DB: {e}")
    finally:
        conn.close()

init_db()

# ==================== STATE ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.menu = "Market"
    st.session_state.carrello = []
    st.session_state.processing = False

# ==================== POKEMON DECORATIVI ====================
st.markdown("""
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" class="pokemon-deco poke-1">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png" class="pokemon-deco poke-2">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/150.png" class="pokemon-deco poke-3">
""", unsafe_allow_html=True)

# ==================== TOP BAR CON HOME/LOGOUT ====================
def render_topbar():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🏠 HOME", key="top_home", use_container_width=True):
            st.session_state.menu = "Market" if st.session_state.logged_in else "Login"
            st.rerun()
    
    with col2:
        st.markdown('<div class="top-bar-title">⚡ POKEMON PORTAL</div>', unsafe_allow_html=True)
    
    with col3:
        if st.session_state.logged_in:
            if st.button("🚪 LOGOUT", key="top_logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.carrello = []
                st.session_state.menu = "Login"
                st.rerun()

render_topbar()

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==================== NAVBAR ====================
def render_nav():
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        nav_cols = st.columns(4)
        if nav_cols[0].button("🏪 Marketplace", key="nav_mkt", use_container_width=True):
            st.session_state.menu = "Market"
            st.rerun()
        if nav_cols[1].button("💎 Vendi", key="nav_vendi", use_container_width=True):
            st.session_state.menu = "Vendi"
            st.rerun()
        cart_count = len(st.session_state.carrello)
        if nav_cols[2].button(f"🛒 Carrello ({cart_count})", key="nav_cart", use_container_width=True):
            st.session_state.menu = "Carrello"
            st.rerun()
        if nav_cols[3].button("👤 Profilo", key="nav_prof", use_container_width=True):
            st.session_state.menu = "Profilo"
            st.rerun()
    else:
        nav_cols = st.columns(2)
        if nav_cols[0].button("🔑 Login", key="nav_login", use_container_width=True):
            st.session_state.menu = "Login"
            st.rerun()
        if nav_cols[1].button("📝 Registrati", key="nav_reg", use_container_width=True):
            st.session_state.menu = "Registrazione"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

render_nav()

# ==================== PAGINE ====================
if not st.session_state.logged_in:
    # --- REGISTRAZIONE ---
    if st.session_state.menu == "Registrazione":
        st.markdown("""
        <div class="page-header">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/133.png" width="120">
            <h1>✨ Diventa un Trainer</h1>
            <p>Unisciti alla community!</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("reg", clear_on_submit=False):
            email = st.text_input("📧 Email", placeholder="trainer@pokemon.com")
            username = st.text_input("👤 Username", placeholder="ash_ketchum")
            pw = st.text_input("🔒 Password", type="password", placeholder="Min 6 caratteri")
            pw2 = st.text_input("🔒 Conferma Password", type="password")
            
            submitted = st.form_submit_button("🚀 REGISTRATI", use_container_width=True, disabled=st.session_state.processing)
            
            if submitted:
                st.session_state.processing = True
                if not email or not username or not pw:
                    st.error("❌ Compila tutti i campi")
                    st.session_state.processing = False
                elif len(pw) < 6:
                    st.error("❌ Password troppo corta")
                    st.session_state.processing = False
                elif pw != pw2:
                    st.error("❌ Password diverse")
                    st.session_state.processing = False
                else:
                    try:
                        with st.spinner("Creazione account..."):
                            conn = get_conn()
                            conn.execute(text("""
                                INSERT INTO users (email, username, password, created_at)
                                VALUES (:e, :u, :p, CURRENT_TIMESTAMP)
                            """), {"e": email, "u": username, "p": hashlib.sha256(pw.encode()).hexdigest()})
                            conn.commit()
                            conn.close()
                            st.session_state.processing = False
                            st.success("✅ Account creato!")
                            time.sleep(1.5)
                            st.session_state.menu = "Login"
                            st.rerun()
                    except:
                        st.session_state.processing = False
                        st.error("❌ Email/username già in uso")

    # --- LOGIN ---
    else:
        st.markdown("""
        <div class="page-header">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="140">
            <h1>⚡ Bentornato Trainer</h1>
            <p>Accedi al Pokemon Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login", clear_on_submit=True):
            uid = st.text_input("📧 Email o Username")
            pwd = st.text_input("🔒 Password", type="password")
            
            submitted = st.form_submit_button("🔓 ACCEDI", use_container_width=True, disabled=st.session_state.processing)
            
            if submitted:
                st.session_state.processing = True
                with st.spinner("Verifica..."):
                    conn = get_conn()
                    row = conn.execute(text("""
                        SELECT * FROM users WHERE (email = :u OR username = :u) AND password = :p
                    """), {"u": uid, "p": hashlib.sha256(pwd.encode()).hexdigest()}).fetchone()
                    conn.close()
                    
                    if row:
                        user = dict(row._mapping)
                        user['created_at'] = safe_date(user['created_at'])
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.menu = "Market"
                        st.session_state.processing = False
                        st.success(f"✅ Benvenuto @{user['username']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.processing = False
                        st.error("❌ Credenziali errate")

# ==================== LOGGATO ====================
else:
    # --- MARKET ---
    if st.session_state.menu == "Market":
        st.markdown("""
        <div class="page-header">
            <h1>🏪 Marketplace</h1>
            <p>Trova le carte più rare</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        search = c1.text_input("🔍 Cerca", "")
        rarita_filter = c2.selectbox("⭐", ["Tutte", "Holo", "Ultra Rara", "Secret", "Rara"])
        max_price = c3.number_input("💰 Max €", 1, 100000, 5000)
        if c4.button("Cerca", use_container_width=True):
            pass

        query = "SELECT c.*, u.username AS seller FROM carte c JOIN users u ON c.user_id = u.id WHERE c.sold = 0 AND c.prezzo <= :max"
        params = {"max": max_price}
        
        if search:
            query += " AND LOWER(c.nome) LIKE :search"
            params["search"] = f"%{search.lower()}%"
        if rarita_filter != "Tutte":
            query += " AND c.rarita = :rarita"
            params["rarita"] = rarita_filter
        query += " ORDER BY c.created_at DESC"

        conn = get_conn()
        cards = to_dict_list(conn.execute(text(query), params))
        conn.close()

        if not cards:
            st.info("🔍 Nessuna carta trovata")
        else:
            st.write(f"**{len(cards)} carte**")
            
            cols = st.columns(4)
            for i, c in enumerate(cards):
                with cols[i % 4]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    img_b64 = get_image_b64(c.get('immagine'))
                    if img_b64:
                        st.image(f"data:image/png;base64,{img_b64}", use_container_width=True)
                    else:
                        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png", use_container_width=True)
                    
                    st.markdown(f"### {c['nome']}")
                    
                    rarity_class = get_rarity_class(c.get('rarita', 'Rara'))
                    st.markdown(f"<span class='rarity-badge {rarity_class}'>{c.get('rarita', 'N/D')}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"<div style='margin: 0.5rem 0; opacity: 0.8;'>@{c.get('seller', 'N/D')}</div>", unsafe_allow_html=True)
                    
                    if c.get('descrizione'):
                        with st.expander("📝 Descrizione"):
                            st.write(c['descrizione'])
                    
                    st.markdown(f"<div class='price-tag'>€{c['prezzo']:.2f}</div>", unsafe_allow_html=True)
                    
                    if st.button("🛒 Aggiungi", key=f"add_{c['id']}", use_container_width=True):
                        st.session_state.carrello.append({
                            "id": c["id"],
                            "nome": c["nome"],
                            "prezzo": c["prezzo"],
                            "seller_id": c["user_id"]
                        })
                        st.toast("✅ Aggiunto!", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    # --- VENDI ---
    elif st.session_state.menu == "Vendi":
        st.markdown("""
        <div class="page-header">
            <h1>💎 Vendi le tue Carte</h1>
            <p>Condividi con la community</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("vendi", clear_on_submit=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # CAMERA MOBILE FIX
                img = st.file_uploader(
                    "📸 Foto Carta*",
                    type=["png", "jpg", "jpeg"],
                    help="Su smartphone: tocca per scattare foto"
                )
                if img:
                    st.image(img, use_container_width=True)
            
            with col2:
                nome = st.text_input("🎴 Nome Carta*", placeholder="Pikachu VMAX")
                rarita = st.selectbox("⭐ Rarità*", ["Holo", "Ultra Rara", "Secret", "Rara"])
                prezzo = st.number_input("💰 Prezzo €*", min_value=0.5, step=0.5, value=10.0)
                descrizione = st.text_area("📝 Descrizione / Difetti", placeholder="Es: Carta in condizioni NM, piccola piega angolo...")
                
                st.markdown("""
                <div style='background: rgba(131, 56, 236, 0.15); padding: 1rem; border-radius: 10px; margin-top: 1rem; border-left: 3px solid var(--cyber-purple);'>
                    <strong>💡 Consigli:</strong><br>
                    • Scatta foto nitide e ben illuminate<br>
                    • Controlla i prezzi di mercato<br>
                    • Descrivi accuratamente le condizioni
                </div>
                """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🚀 PUBBLICA", use_container_width=True, disabled=st.session_state.processing)
            
            if submitted:
                st.session_state.processing = True
                if not img or not nome:
                    st.error("❌ Foto e nome obbligatori")
                    st.session_state.processing = False
                else:
                    try:
                        with st.spinner("Pubblicazione..."):
                            conn = get_conn()
                            conn.execute(text("""
                                INSERT INTO carte (user_id, nome, rarita, prezzo, descrizione, immagine, created_at)
                                VALUES (:u, :n, :r, :p, :d, :img, CURRENT_TIMESTAMP)
                            """), {
                                "u": st.session_state.user["id"],
                                "n": nome,
                                "r": rarita,
                                "p": prezzo,
                                "d": descrizione,
                                "img": img.read()
                            })
                            conn.commit()
                            conn.close()
                            st.session_state.processing = False
                            st.success("🎉 Carta pubblicata!")
                            time.sleep(1.5)
                            st.rerun()
                    except Exception as e:
                        st.session_state.processing = False
                        st.error(f"❌ Errore: {e}")

    # --- CARRELLO ---
    elif st.session_state.menu == "Carrello":
        st.markdown("""
        <div class="page-header">
            <h1>🛒 Carrello</h1>
            <p>Completa il tuo ordine</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.carrello:
            st.markdown("""
            <div style='text-align: center; padding: 4rem; background: rgba(22, 27, 34, 0.8); border-radius: 20px; border: 2px dashed var(--cyber-blue);'>
                <h2 style='opacity: 0.6;'>🛒 Carrello vuoto</h2>
                <p style='opacity: 0.6;'>Vai al marketplace!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            totale = sum(item["prezzo"] for item in st.session_state.carrello)
            
            st.markdown("### 📦 Articoli")
            for i, item in enumerate(st.session_state.carrello):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{item['nome']}**")
                with col2:
                    st.markdown(f"<span class='price-tag'>€{item['prezzo']:.2f}</span>", unsafe_allow_html=True)
                with col3:
                    if st.button("🗑️", key=f"rm_{i}"):
                        st.session_state.carrello.pop(i)
                        st.rerun()
            
            st.divider()
            st.markdown(f"<h2 style='text-align: right;'>Totale: <span class='price-tag'>€{totale:.2f}</span></h2>", unsafe_allow_html=True)
            
            st.markdown("### 💳 Checkout")
            if st.button("✅ CONFERMA ORDINE", use_container_width=True, type="primary", disabled=st.session_state.processing):
                st.session_state.processing = True
                with st.spinner("Elaborazione..."):
                    time.sleep(1.5)
                    st.balloons()
                    st.success("🎉 Ordine confermato!")
                    st.session_state.carrello.clear()
                    st.session_state.processing = False
                    time.sleep(2)
                    st.rerun()

    # --- PROFILO ---
    elif st.session_state.menu == "Profilo":
        user = st.session_state.user
        
        st.markdown(f"""
        <div class="page-header">
            <h1>👤 @{user['username']}</h1>
            <p>Il tuo profilo Trainer</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        ### 📊 Info
        - 📧 **Email**: {user.get('email', 'N/D')}
        - 🕐 **Iscritto**: {safe_date(user.get('created_at'))}
        """)
        
        st.divider()
        st.markdown("### 🎴 Tue Carte")
        
        conn = get_conn()
        my_cards = to_dict_list(conn.execute(text("SELECT * FROM carte WHERE user_id = :id AND sold = 0 ORDER BY created_at DESC"), {"id": user["id"]}))
        conn.close()
        
        if not my_cards:
            st.info("📷 Nessuna carta. Vai su 'Vendi'!")
        else:
            cols = st.columns(4)
            for i, c in enumerate(my_cards):
                with cols[i % 4]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    img_b64 = get_image_b64(c.get('immagine'))
                    if img_b64:
                        st.image(f"data:image/png;base64,{img_b64}", use_container_width=True)
                    
                    st.markdown(f"**{c['nome']}**")
                    rarity_class = get_rarity_class(c.get('rarita', 'Rara'))
                    st.markdown(f"<span class='rarity-badge {rarity_class}'>{c.get('rarita', 'N/D')}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='price-tag'>€{c['prezzo']:.2f}</div>", unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
