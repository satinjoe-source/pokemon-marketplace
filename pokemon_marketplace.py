import streamlit as st
import hashlib
import base64
import time
from datetime import datetime as dt
from sqlalchemy import create_engine, text
from datetime import datetime

# ==================== CONFIGURAZIONE APP ====================
st.set_page_config(
    page_title="PokeMarket Nova ✨",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS ULTRA MODERNO ====================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Space+Grotesk:wght@400;600;700&display=swap');

    /* Variabili tema Pokemon */
    :root {
        --bg-primary: #0a0e27;
        --bg-secondary: #1a1f3a;
        --card-bg: rgba(26, 31, 58, 0.8);
        --accent-yellow: #ffcb05;
        --accent-blue: #3b4cca;
        --accent-red: #d40000;
        --text-primary: #ffffff;
        --text-secondary: #94a3b8;
        --border: rgba(255, 203, 5, 0.3);
        --glow: rgba(255, 203, 5, 0.4);
    }

    @media (prefers-color-scheme: light) {
        :root {
            --bg-primary: #f0f4f8;
            --bg-secondary: #ffffff;
            --card-bg: rgba(255, 255, 255, 0.95);
            --text-primary: #0a0e27;
            --text-secondary: #64748b;
            --border: rgba(59, 76, 202, 0.3);
        }
    }

    /* Animazioni */
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 203, 5, 0.3); }
        50% { box-shadow: 0 0 40px rgba(255, 203, 5, 0.6); }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Background animato */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        background-attachment: fixed;
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
    }
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 50%, rgba(255, 203, 5, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(212, 0, 0, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(59, 76, 202, 0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* Titoli con effetto neon */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        background: linear-gradient(90deg, var(--accent-yellow), var(--accent-red));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(255, 203, 5, 0.5);
        animation: glow 3s ease-in-out infinite;
    }

    /* Navbar glassmorphism */
    .nav-container {
        background: rgba(10, 14, 39, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 2px solid var(--border);
        border-radius: 25px;
        padding: 1.5rem 2.5rem;
        margin: 1rem auto 3rem;
        max-width: 95%;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3), 0 0 30px var(--glow);
        animation: slideIn 0.6s ease-out;
    }
    .nav-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, var(--accent-yellow), var(--accent-red));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Card con effetto 3D */
    .product-card {
        background: var(--card-bg);
        backdrop-filter: blur(15px);
        border: 2px solid var(--border);
        border-radius: 20px;
        padding: 1.5rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 100%;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
        animation: slideIn 0.5s ease-out;
    }
    .product-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 203, 5, 0.1), transparent);
        transition: left 0.5s;
    }
    .product-card:hover::before {
        left: 100%;
    }
    .product-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4), 0 0 40px var(--glow);
        border-color: var(--accent-yellow);
    }
    .product-card img {
        transition: transform 0.4s;
        filter: drop-shadow(0 0 10px rgba(255, 203, 5, 0.3));
    }
    .product-card:hover img {
        transform: scale(1.1) rotate(5deg);
    }

    /* Prezzo con effetto brillante */
    .price-tag {
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--accent-yellow), var(--accent-red));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 15px rgba(255, 203, 5, 0.6);
        margin: 0.75rem 0;
        animation: glow 2s ease-in-out infinite;
    }

    /* Header pagina */
    .page-header {
        text-align: center;
        margin: 2rem 0 3rem;
        padding: 2rem;
        background: rgba(26, 31, 58, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 2px solid var(--border);
        animation: slideIn 0.6s ease-out;
    }
    .page-header h1 {
        margin: 0;
        font-size: 3.5rem;
        letter-spacing: 2px;
    }
    .page-header p {
        color: var(--text-secondary);
        font-size: 1.3rem;
        margin-top: 1rem;
    }
    .page-header img {
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 10px 20px rgba(255, 203, 5, 0.4));
    }

    /* Badge rarità */
    .rarity-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .rarity-holo {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.5);
    }
    .rarity-ultra {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        box-shadow: 0 0 15px rgba(240, 147, 251, 0.5);
    }
    .rarity-secret {
        background: linear-gradient(135deg, #ffd700, #ff8c00);
        color: white;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
    }
    .rarity-rara {
        background: linear-gradient(135deg, #89f7fe, #66a6ff);
        color: white;
        box-shadow: 0 0 15px rgba(137, 247, 254, 0.5);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-yellow), var(--accent-red)) !important;
        color: var(--bg-primary) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s !important;
        box-shadow: 0 5px 15px rgba(255, 203, 5, 0.3) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 10px 30px rgba(255, 203, 5, 0.5) !important;
    }
    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background: rgba(26, 31, 58, 0.8) !important;
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        padding: 0.75rem !important;
        transition: all 0.3s !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--accent-yellow) !important;
        box-shadow: 0 0 20px var(--glow) !important;
    }

    /* Nasconde elementi Streamlit */
    [data-testid="stHeader"], footer, header, .viewerBadge_container__r5tak { 
        visibility: hidden !important; 
        height: 0 !important;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .nav-title {
            font-size: 1.5rem;
        }
        .page-header h1 {
            font-size: 2rem;
        }
        .product-card {
            padding: 1rem;
        }
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

def serializable(v):
    if isinstance(v, (datetime, dt)):
        return v.isoformat()
    elif isinstance(v, bytes):
        return base64.b64encode(v).decode()
    return v

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
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS carte (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            nome TEXT NOT NULL,
            rarita TEXT,
            prezzo REAL NOT NULL,
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

# ==================== STATO ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.menu = "Market"
    st.session_state.carrello = []
    st.session_state.processing = False

# ==================== NAVBAR ====================
def render_nav():
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        st.markdown('<div class="nav-title">⚡ POKE<span style="color:#D40000">MARKET</span> NOVA</div>', unsafe_allow_html=True)
        
        if st.session_state.logged_in:
            nav_cols = st.columns(4)
            if nav_cols[0].button("🏪 Market", key="nav_mkt", use_container_width=True):
                st.session_state.menu = "Market"
                st.rerun()
            if nav_cols[1].button("💰 Vendi", key="nav_vendi", use_container_width=True):
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
            <h1>✨ Unisciti alla Lega</h1>
            <p>Diventa un Trainer leggendario</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("reg", clear_on_submit=False):
            email = st.text_input("📧 Email", placeholder="trainer@pokemon.com")
            username = st.text_input("👤 Username", placeholder="ash_ketchum")
            pw = st.text_input("🔒 Password", type="password", placeholder="Min 6 caratteri")
            pw2 = st.text_input("🔒 Conferma Password", type="password")
            
            submitted = st.form_submit_button(
                "🚀 REGISTRATI ORA",
                use_container_width=True,
                disabled=st.session_state.processing
            )
            
            if submitted:
                st.session_state.processing = True
                if not email or not username or not pw:
                    st.error("❌ Compila tutti i campi")
                    st.session_state.processing = False
                elif len(pw) < 6:
                    st.error("❌ Password troppo corta (min 6)")
                    st.session_state.processing = False
                elif pw != pw2:
                    st.error("❌ Password non coincidono")
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
                            st.success("✅ Registrato! Ora accedi.")
                            time.sleep(1.5)
                            st.session_state.menu = "Login"
                            st.rerun()
                    except Exception as e:
                        st.session_state.processing = False
                        if "unique" in str(e).lower():
                            st.error("❌ Email o username già in uso")
                        else:
                            st.error(f"❌ Errore: {e}")

    # --- LOGIN ---
    else:
        st.markdown("""
        <div class="page-header">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="140">
            <h1>⚡ Bentornato Trainer</h1>
            <p>Accedi e inizia la tua avventura</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login", clear_on_submit=True):
            uid = st.text_input("📧 Email o Username")
            pwd = st.text_input("🔒 Password", type="password")
            
            submitted = st.form_submit_button(
                "🔓 ACCEDI",
                use_container_width=True,
                disabled=st.session_state.processing
            )
            
            if submitted:
                st.session_state.processing = True
                with st.spinner("Verifica credenziali..."):
                    conn = get_conn()
                    row = conn.execute(text("""
                        SELECT * FROM users WHERE (email = :u OR username = :u) AND password = :p
                    """), {"u": uid, "p": hashlib.sha256(pwd.encode()).hexdigest()}).fetchone()
                    conn.close()
                    
                    if row:
                        st.session_state.logged_in = True
                        user = dict(row._mapping)
                        user['created_at'] = safe_date(user['created_at'])
                        st.session_state.user = user
                        st.session_state.menu = "Market"
                        st.session_state.processing = False
                        st.success(f"✅ Benvenuto @{user['username']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.processing = False
                        st.error("❌ Credenziali errate")

# ——————————————————— LOGGATO ———————————————————
else:
    # --- MARKET ---
    if st.session_state.menu == "Market":
        st.markdown("""
        <div class="page-header">
            <h1>🏪 Marketplace Globale</h1>
            <p>Scopri le carte più rare del mondo</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        search = c1.text_input("🔍 Cerca carta", "")
        rarita_filter = c2.selectbox("⭐ Rarità", ["Tutte", "Holo", "Ultra Rara", "Secret", "Rara"])
        max_price = c3.number_input("💰 Max €", 1, 100000, 5000)
        if c4.button("🔍 Cerca", use_container_width=True):
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

        with st.spinner("Caricamento carte..."):
            conn = get_conn()
            cards = to_dict_list(conn.execute(text(query), params))
            conn.close()

        if not cards:
            st.info("🔍 Nessuna carta trovata. Prova con filtri diversi!")
        else:
            st.write(f"**{len(cards)} carte trovate**")
            
            cols = st.columns(4)
            for i, c in enumerate(cards):
                with cols[i % 4]:
                    img = serializable(c['immagine']) if c['immagine'] else None
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    if img:
                        st.image(f"data:image/png;base64,{img}", use_container_width=True)
                    else:
                        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/0.png", use_container_width=True)
                    
                    st.markdown(f"### {c['nome']}")
                    
                    rarity_class = get_rarity_class(c['rarita'])
                    st.markdown(f"<span class='rarity-badge {rarity_class}'>{c['rarita']}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"<div style='color: var(--text-secondary); margin: 0.5rem 0;'>Venditore: <strong>@{c['seller']}</strong></div>", unsafe_allow_html=True)
                    
                    st.markdown(f"<div class='price-tag'>€{c['prezzo']:.2f}</div>", unsafe_allow_html=True)
                    
                    if st.button("🛒 Aggiungi al carrello", key=f"add_{c['id']}", use_container_width=True):
                        st.session_state.carrello.append({
                            "id": c["id"],
                            "nome": c["nome"],
                            "prezzo": c["prezzo"],
                            "seller_id": c["user_id"]
                        })
                        st.toast("✅ Carta aggiunta!", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    # --- VENDI ---
    elif st.session_state.menu == "Vendi":
        st.markdown("""
        <div class="page-header">
            <h1>💎 Vendi le tue Carte</h1>
            <p>Condividi i tuoi tesori con il mondo</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("vendi", clear_on_submit=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                img = st.file_uploader("🖼️ Foto Carta*", type=["png", "jpg", "jpeg"])
                if img:
                    st.image(img, caption="Anteprima", use_container_width=True)
            
            with col2:
                nome = st.text_input("🎴 Nome Carta*", placeholder="Pikachu VMAX")
                rarita = st.selectbox("⭐ Rarità*", ["Holo", "Ultra Rara", "Secret", "Rara"])
                prezzo = st.number_input("💰 Prezzo €*", min_value=0.5, step=0.5, value=10.0)
                
                st.markdown("""
                <div style='background: rgba(255, 203, 5, 0.1); padding: 1rem; border-radius: 10px; margin-top: 1rem;'>
                    <strong>💡 Suggerimenti:</strong><br>
                    • Usa foto nitide e ben illuminate<br>
                    • Controlla i prezzi di mercato<br>
                    • Descrivi eventuali difetti
                </div>
                """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button(
                "🚀 PUBBLICA CARTA",
                use_container_width=True,
                disabled=st.session_state.processing
            )
            
            if submitted:
                st.session_state.processing = True
                if not img or not nome:
                    st.error("❌ Foto e nome sono obbligatori!")
                    st.session_state.processing = False
                elif prezzo < 0.5:
                    st.error("❌ Prezzo minimo €0.50")
                    st.session_state.processing = False
                else:
                    try:
                        with st.spinner("Pubblicazione in corso..."):
                            conn = get_conn()
                            conn.execute(text("""
                                INSERT INTO carte (user_id, nome, rarita, prezzo, immagine, created_at)
                                VALUES (:u, :n, :r, :p, :img, CURRENT_TIMESTAMP)
                            """), {
                                "u": st.session_state.user["id"],
                                "n": nome,
                                "r": rarita,
                                "p": prezzo,
                                "img": img.read()
                            })
                            conn.commit()
                            conn.close()
                            st.session_state.processing = False
                            st.success("🎉 Carta pubblicata con successo!")
                            time.sleep(1.5)
                            st.rerun()
                    except Exception as e:
                        st.session_state.processing = False
                        st.error(f"❌ Errore: {e}")

    # --- CARRELLO ---
    elif st.session_state.menu == "Carrello":
        st.markdown("""
        <div class="page-header">
            <h1>🛒 Il tuo Carrello</h1>
            <p>Completa il tuo ordine</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.carrello:
            st.markdown("""
            <div style='text-align: center; padding: 4rem; background: rgba(26, 31, 58, 0.5); border-radius: 20px;'>
                <h2 style='color: var(--text-secondary);'>🛒 Carrello vuoto</h2>
                <p style='color: var(--text-secondary);'>Vai al marketplace e trova le tue carte preferite!</p>
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
            
            st.markdown("### 💳 Metodo di Pagamento")
            metodo = st.radio("Scegli metodo", ["🎯 Simulazione", "💳 Stripe", "💙 PayPal"], horizontal=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if metodo == "💳 Stripe":
                    st.link_button("💳 Paga con Stripe", "https://buy.stripe.com/test", use_container_width=True, type="primary")
            with col2:
                if metodo == "💙 PayPal":
                    st.link_button("💙 Paga con PayPal", "https://paypal.me/test", use_container_width=True)
            
            if metodo == "🎯 Simulazione":
                if st.button("✅ CONFERMA ORDINE", use_container_width=True, type="primary", disabled=st.session_state.processing):
                    st.session_state.processing = True
                    with st.spinner("Elaborazione ordine..."):
                        time.sleep(1.5)
                        st.balloons()
                        st.success("🎉 Ordine confermato! Grazie per l'acquisto!")
                        st.session_state.carrello.clear()
                        st.session_state.processing = False
                        time.sleep(2)
                        st.rerun()

    # --- PROFILO ---
    elif st.session_state.menu == "Profilo":
        user = st.session_state.user
        created = safe_date(user.get("created_at"))
        
        st.markdown(f"""
        <div class="page-header">
            <h1>👤 Profilo Trainer</h1>
            <p>@{user['username']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            ### 📊 Informazioni
            - 📧 **Email**: {user.get('email', 'N/D')}
            - 🕐 **Iscritto il**: {created}
            - 🎴 **Carte in vendita**: {len(to_dict_list(get_conn().execute(text("SELECT * FROM carte WHERE user_id = :id AND sold = 0"), {"id": user["id"]})))}
            """)
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.carrello = []
                st.rerun()
        
        st.divider()
        st.markdown("### 🎴 Le Tue Carte in Vendita")
        
        conn = get_conn()
        my_cards = to_dict_list(conn.execute(text("SELECT * FROM carte WHERE user_id = :id AND sold = 0"), {"id": user["id"]}))
        conn.close()
        
        if not my_cards:
            st.info("📷 Nessuna carta in vendita. Vai su 'Vendi' per pubblicarne una!")
        else:
            cols = st.columns(4)
            for i, c in enumerate(my_cards):
                with cols[i % 4]:
                    img = serializable(c['immagine']) if c['immagine'] else None
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    if img:
                        st.image(f"data:image/png;base64,{img}", use_container_width=True)
                    
                    st.markdown(f"**{c['nome']}**")
                    rarity_class = get_rarity_class(c['rarita'])
                    st.markdown(f"<span class='rarity-badge {rarity_class}'>{c['rarita']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='price-tag'>€{c['prezzo']:.2f}</div>", unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
