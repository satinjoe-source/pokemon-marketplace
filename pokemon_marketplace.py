import streamlit as st
import hashlib
import base64
import time
from datetime import datetime as dt
from sqlalchemy import create_engine, text
from datetime import datetime

st.set_page_config(
    page_title="Pokemon Portal ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS OTTIMIZZATO ====================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

    :root {
        --cyber-pink: #FF006E;
        --cyber-purple: #8338EC;
        --cyber-blue: #3A86FF;
        --cyber-yellow: #FFBE0B;
        --cyber-green: #00FF41;
        --dark-bg: #0d1117;
        --dark-card: #161b22;
        --text-dark: #c9d1d9;
    }

    @media (prefers-color-scheme: light) {
        :root {
            --dark-bg: #f0f4ff;
            --dark-card: #ffffff;
            --text-dark: #1a202c;
            --cyber-pink: #e6005c;
            --cyber-purple: #7029d4;
            --cyber-blue: #0066ff;
        }
    }

    @keyframes float { 
        0%, 100% { transform: translateY(0); } 
        50% { transform: translateY(-15px); } 
    }

    * {
        box-sizing: border-box;
    }

    .stApp {
        background: var(--dark-bg);
        color: var(--text-dark);
        font-family: 'Poppins', sans-serif;
    }

    /* POKEMON LATERALI */
    .pokemon-side {
        position: fixed;
        pointer-events: none;
        z-index: 1;
        opacity: 0.2;
        animation: float 4s ease-in-out infinite;
    }
    .poke-left { 
        top: 15%; 
        left: 1%; 
        width: 70px; 
    }
    .poke-right { 
        top: 60%; 
        right: 1%; 
        width: 90px; 
        animation-delay: 1.5s; 
    }

    /* HEADER */
    .portal-header {
        text-align: center;
        padding: 1.5rem;
        margin: 1rem auto 2rem;
        max-width: 1200px;
    }
    .portal-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--cyber-yellow), var(--cyber-pink), var(--cyber-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: 2px;
    }

    /* NAVBAR */
    .nav-bar {
        background: var(--dark-card);
        border: 2px solid var(--cyber-purple);
        border-radius: 15px;
        padding: 1rem;
        margin: 0 auto 2rem;
        max-width: 1200px;
        box-shadow: 0 8px 32px rgba(131, 56, 236, 0.2);
    }

    /* CARDS */
    .card-item {
        background: var(--dark-card);
        border: 2px solid var(--cyber-purple);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    .card-item:hover {
        transform: translateY(-8px);
        border-color: var(--cyber-pink);
        box-shadow: 0 12px 32px rgba(255, 0, 110, 0.3);
    }
    .card-item img {
        border-radius: 8px;
        width: 100%;
        height: auto;
    }

    /* PRICE TAG */
    .price-display {
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--cyber-yellow), var(--cyber-pink));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }

    /* WALLET BOX */
    .wallet-box {
        background: linear-gradient(135deg, var(--cyber-purple), var(--cyber-blue));
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(131, 56, 236, 0.4);
    }
    .wallet-amount {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0.5rem 0;
    }

    /* BADGES */
    .badge-rarity {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0.3rem 0;
        text-transform: uppercase;
    }
    .badge-holo { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .badge-ultra { background: linear-gradient(135deg, #f093fb, #f5576c); color: white; }
    .badge-secret { background: linear-gradient(135deg, #ffd700, #ff8c00); color: #000; }
    .badge-rara { background: linear-gradient(135deg, #89f7fe, #66a6ff); color: white; }

    /* PAGE HEADER */
    .section-header {
        text-align: center;
        padding: 2rem;
        background: var(--dark-card);
        border: 2px solid var(--cyber-blue);
        border-radius: 15px;
        margin: 1rem auto 2rem;
        max-width: 1200px;
    }
    .section-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--cyber-pink), var(--cyber-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, var(--cyber-pink), var(--cyber-purple)) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.7rem 1.2rem !important;
        transition: all 0.3s !important;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 24px rgba(255, 0, 110, 0.5) !important;
    }

    /* INPUTS */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background: var(--dark-card) !important;
        border: 2px solid var(--cyber-purple) !important;
        border-radius: 8px !important;
        color: var(--text-dark) !important;
        padding: 0.6rem !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--cyber-pink) !important;
        box-shadow: 0 0 15px rgba(255, 0, 110, 0.3) !important;
    }

    /* RESPONSIVE */
    @media (max-width: 768px) {
        .portal-title { font-size: 1.8rem; }
        .section-header h1 { font-size: 1.8rem; }
        .pokemon-side { width: 50px !important; }
        .wallet-amount { font-size: 2rem; }
    }

    /* HIDE STREAMLIT */
    [data-testid="stHeader"], footer, header, .viewerBadge_container__r5tak { 
        display: none !important;
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

def to_dict_list(result):
    return [dict(row._mapping) for row in result.fetchall()]

def get_image_b64(img_data):
    if not img_data:
        return None
    try:
        if isinstance(img_data, memoryview):
            img_data = bytes(img_data)
        if isinstance(img_data, bytes):
            return base64.b64encode(img_data).decode('utf-8')
        return None
    except:
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
        "Holo": "badge-holo",
        "Ultra Rara": "badge-ultra",
        "Secret": "badge-secret",
        "Rara": "badge-rara"
    }
    return mapping.get(rarita, "badge-rara")

# ==================== INIT DB CON WALLET ====================
def init_db():
    conn = get_conn()
    try:
        # Users con WALLET
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            wallet_balance REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
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
        
        # TRANSAZIONI WALLET
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            buyer_id INTEGER,
            seller_id INTEGER,
            carta_id INTEGER,
            amount REAL NOT NULL,
            tipo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        conn.commit()

        if not conn.execute(text("SELECT * FROM users WHERE email = 'admin@pokemon.com'")).fetchone():
            pw = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute(text("""
                INSERT INTO users (email, username, password, wallet_balance, created_at)
                VALUES ('admin@pokemon.com', 'admin', :pw, 1000.0, CURRENT_TIMESTAMP)
            """), {"pw": pw})
            conn.commit()
    except Exception as e:
        st.error(f"Errore DB: {e}")
    finally:
        conn.close()

init_db()

# ==================== WALLET FUNCTIONS ====================
def get_wallet_balance(user_id):
    conn = get_conn()
    result = conn.execute(text("SELECT wallet_balance FROM users WHERE id = :id"), {"id": user_id})
    balance = result.fetchone()
    conn.close()
    return balance[0] if balance else 0.0

def add_funds(user_id, amount):
    conn = get_conn()
    conn.execute(text("UPDATE users SET wallet_balance = wallet_balance + :amount WHERE id = :id"),
                 {"amount": amount, "id": user_id})
    conn.execute(text("""INSERT INTO transactions (buyer_id, amount, tipo, created_at) 
                 VALUES (:id, :amount, 'ricarica', CURRENT_TIMESTAMP)"""),
                 {"id": user_id, "amount": amount})
    conn.commit()
    conn.close()

def withdraw_funds(user_id, amount):
    conn = get_conn()
    balance = get_wallet_balance(user_id)
    if balance >= amount:
        conn.execute(text("UPDATE users SET wallet_balance = wallet_balance - :amount WHERE id = :id"),
                     {"amount": amount, "id": user_id})
        conn.execute(text("""INSERT INTO transactions (buyer_id, amount, tipo, created_at) 
                     VALUES (:id, :amount, 'prelievo', CURRENT_TIMESTAMP)"""),
                     {"id": user_id, "amount": amount})
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def process_purchase(buyer_id, seller_id, carta_id, amount):
    conn = get_conn()
    buyer_balance = get_wallet_balance(buyer_id)
    
    if buyer_balance >= amount:
        # Sottrai da buyer
        conn.execute(text("UPDATE users SET wallet_balance = wallet_balance - :amount WHERE id = :buyer"),
                     {"amount": amount, "buyer": buyer_id})
        
        # Aggiungi a seller (95% - 5% commissione)
        seller_amount = amount * 0.95
        conn.execute(text("UPDATE users SET wallet_balance = wallet_balance + :amount WHERE id = :seller"),
                     {"amount": seller_amount, "seller": seller_id})
        
        # Marca carta come venduta
        conn.execute(text("UPDATE carte SET sold = 1 WHERE id = :id"), {"id": carta_id})
        
        # Registra transazione
        conn.execute(text("""INSERT INTO transactions 
                     (buyer_id, seller_id, carta_id, amount, tipo, created_at)
                     VALUES (:buyer, :seller, :carta, :amount, 'acquisto', CURRENT_TIMESTAMP)"""),
                     {"buyer": buyer_id, "seller": seller_id, "carta": carta_id, "amount": amount})
        
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

# ==================== STATE ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.menu = "Market"
    st.session_state.carrello = []
    st.session_state.processing = False

# ==================== POKEMON LATERALI ====================
st.markdown("""
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" class="pokemon-side poke-left">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png" class="pokemon-side poke-right">
""", unsafe_allow_html=True)

# ==================== TOP BAR ====================
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("🏠 HOME", key="top_home", use_container_width=True):
        st.session_state.menu = "Market" if st.session_state.logged_in else "Login"
        st.rerun()

with col2:
    st.markdown('<div class="portal-header"><div class="portal-title">⚡ POKEMON PORTAL</div></div>', unsafe_allow_html=True)

with col3:
    if st.session_state.logged_in:
        if st.button("🚪 LOGOUT", key="top_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.carrello = []
            st.session_state.menu = "Login"
            st.rerun()

# ==================== NAVBAR ====================
st.markdown('<div class="nav-bar">', unsafe_allow_html=True)

if st.session_state.logged_in:
    # MOSTRA WALLET
    balance = get_wallet_balance(st.session_state.user['id'])
    st.markdown(f"""
    <div class="wallet-box">
        <div style="font-size: 1rem; opacity: 0.9;">💰 Il tuo Wallet</div>
        <div class="wallet-amount">€{balance:.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    nav_cols = st.columns(5)
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
    if nav_cols[3].button("💳 Wallet", key="nav_wallet", use_container_width=True):
        st.session_state.menu = "Wallet"
        st.rerun()
    if nav_cols[4].button("👤 Profilo", key="nav_prof", use_container_width=True):
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

# ==================== PAGINE ====================
if not st.session_state.logged_in:
    if st.session_state.menu == "Registrazione":
        st.markdown("""
        <div class="section-header">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/133.png" width="100">
            <h1>✨ Diventa Trainer</h1>
            <p>Registrati e ricevi €50 di bonus!</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("reg"):
            email = st.text_input("📧 Email")
            username = st.text_input("👤 Username")
            pw = st.text_input("🔒 Password", type="password")
            pw2 = st.text_input("🔒 Conferma", type="password")
            
            if st.form_submit_button("🚀 REGISTRATI", use_container_width=True):
                if not email or not username or not pw:
                    st.error("❌ Compila tutti i campi")
                elif len(pw) < 6:
                    st.error("❌ Password minimo 6 caratteri")
                elif pw != pw2:
                    st.error("❌ Password diverse")
                else:
                    try:
                        conn = get_conn()
                        # BONUS 50€ alla registrazione
                        conn.execute(text("""
                            INSERT INTO users (email, username, password, wallet_balance, created_at)
                            VALUES (:e, :u, :p, 50.0, CURRENT_TIMESTAMP)
                        """), {"e": email, "u": username, "p": hashlib.sha256(pw.encode()).hexdigest()})
                        conn.commit()
                        conn.close()
                        st.success("✅ Account creato! Hai ricevuto €50 di bonus!")
                        time.sleep(2)
                        st.session_state.menu = "Login"
                        st.rerun()
                    except:
                        st.error("❌ Email/username già in uso")

    else:
        st.markdown("""
        <div class="section-header">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="120">
            <h1>⚡ Bentornato</h1>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            uid = st.text_input("📧 Email o Username")
            pwd = st.text_input("🔒 Password", type="password")
            
            if st.form_submit_button("🔓 ACCEDI", use_container_width=True):
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
                    st.success(f"✅ Benvenuto @{user['username']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Credenziali errate")

else:
    if st.session_state.menu == "Market":
        st.markdown("""
        <div class="section-header">
            <h1>🏪 Marketplace</h1>
            <p>Compra con il tuo Wallet</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([3, 1, 1])
        search = c1.text_input("🔍 Cerca", "")
        rarita_filter = c2.selectbox("⭐", ["Tutte", "Holo", "Ultra Rara", "Secret", "Rara"])
        max_price = c3.number_input("💰 Max €", 1, 10000, 1000)

        query = "SELECT c.*, u.username AS seller FROM carte c JOIN users u ON c.user_id = u.id WHERE c.sold = 0 AND c.prezzo <= :max AND c.user_id != :user_id"
        params = {"max": max_price, "user_id": st.session_state.user['id']}
        
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
            cols = st.columns(4)
            for i, c in enumerate(cards):
                with cols[i % 4]:
                    st.markdown('<div class="card-item">', unsafe_allow_html=True)
                    
                    img_b64 = get_image_b64(c.get('immagine'))
                    if img_b64:
                        st.image(f"data:image/png;base64,{img_b64}")
                    
                    st.markdown(f"**{c['nome']}**")
                    rarity_class = get_rarity_class(c.get('rarita', 'Rara'))
                    st.markdown(f"<span class='badge-rarity {rarity_class}'>{c.get('rarita')}</span>", unsafe_allow_html=True)
                    st.write(f"@{c['seller']}")
                    
                    if c.get('descrizione'):
                        with st.expander("📝"):
                            st.write(c['descrizione'])
                    
                    st.markdown(f"<div class='price-display'>€{c['prezzo']:.2f}</div>", unsafe_allow_html=True)
                    
                    if st.button("🛒 Aggiungi", key=f"add_{c['id']}", use_container_width=True):
                        st.session_state.carrello.append(c)
                        st.toast("✅ Aggiunto!")
                        time.sleep(0.3)
                        st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.menu == "Vendi":
        st.markdown("""
        <div class="section-header">
            <h1>💎 Vendi</h1>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("vendi"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                img = st.file_uploader("📸 Foto*", type=["png", "jpg", "jpeg"])
                if img:
                    st.image(img)
            
            with col2:
                nome = st.text_input("🎴 Nome*")
                rarita = st.selectbox("⭐", ["Holo", "Ultra Rara", "Secret", "Rara"])
                prezzo = st.number_input("💰 Prezzo €*", 0.5, 10000.0, 10.0, 0.5)
                descrizione = st.text_area("📝 Descrizione")
            
            if st.form_submit_button("🚀 PUBBLICA", use_container_width=True):
                if not img or not nome:
                    st.error("❌ Foto e nome obbligatori")
                else:
                    try:
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
                        st.success("🎉 Pubblicata!")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

    elif st.session_state.menu == "Carrello":
        st.markdown("""
        <div class="section-header">
            <h1>🛒 Carrello</h1>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.carrello:
            st.info("🛒 Carrello vuoto")
        else:
            totale = sum(item["prezzo"] for item in st.session_state.carrello)
            balance = get_wallet_balance(st.session_state.user['id'])
            
            for i, item in enumerate(st.session_state.carrello):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{item['nome']}**")
                with col2:
                    st.markdown(f"<div class='price-display'>€{item['prezzo']:.2f}</div>", unsafe_allow_html=True)
                with col3:
                    if st.button("🗑️", key=f"rm_{i}"):
                        st.session_state.carrello.pop(i)
                        st.rerun()
            
            st.divider()
            st.markdown(f"<h2>Totale: <span class='price-display'>€{totale:.2f}</span></h2>", unsafe_allow_html=True)
            st.write(f"**Saldo Wallet: €{balance:.2f}**")
            
            if balance < totale:
                st.error(f"❌ Saldo insufficiente! Ti servono €{totale - balance:.2f}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💳 Ricarica Wallet", use_container_width=True):
                        st.session_state.menu = "Wallet"
                        st.rerun()
            else:
                if st.button("✅ PAGA CON WALLET", use_container_width=True, type="primary"):
                    success_all = True
                    for item in st.session_state.carrello:
                        if not process_purchase(
                            st.session_state.user['id'],
                            item['user_id'],
                            item['id'],
                            item['prezzo']
                        ):
                            success_all = False
                            break
                    
                    if success_all:
                        st.balloons()
                        st.success("🎉 Acquisto completato!")
                        st.session_state.carrello.clear()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Errore pagamento")

    elif st.session_state.menu == "Wallet":
        st.markdown("""
        <div class="section-header">
            <h1>💳 Wallet</h1>
        </div>
        """, unsafe_allow_html=True)
        
        balance = get_wallet_balance(st.session_state.user['id'])
        st.markdown(f"""
        <div class="wallet-box">
            <div>💰 Saldo Disponibile</div>
            <div class="wallet-amount">€{balance:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ➕ Ricarica")
            st.info("💡 In produzione useresti Stripe/PayPal per ricaricare")
            amount = st.number_input("Importo €", 10.0, 1000.0, 50.0, 10.0, key="ricarica")
            if st.button("💳 RICARICA (Demo)", use_container_width=True):
                add_funds(st.session_state.user['id'], amount)
                st.success(f"✅ Ricaricati €{amount:.2f}!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            st.markdown("### ➖ Preleva")
            st.info("💡 In produzione trasferiresti su conto bancario")
            withdraw_amount = st.number_input("Importo €", 10.0, balance, 50.0, 10.0, key="preleva")
            if st.button("🏦 PRELEVA (Demo)", use_container_width=True):
                if withdraw_funds(st.session_state.user['id'], withdraw_amount):
                    st.success(f"✅ Prelevati €{withdraw_amount:.2f}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Saldo insufficiente")
        
        st.divider()
        st.markdown("### 📊 Transazioni Recenti")
        conn = get_conn()
        txs = to_dict_list(conn.execute(text("""
            SELECT * FROM transactions 
            WHERE buyer_id = :id OR seller_id = :id 
            ORDER BY created_at DESC LIMIT 10
        """), {"id": st.session_state.user['id']}))
        conn.close()
        
        for tx in txs:
            tipo_emoji = {"ricarica": "➕", "prelievo": "➖", "acquisto": "🛒"}
            st.write(f"{tipo_emoji.get(tx['tipo'], '💰')} {tx['tipo'].upper()} - €{tx['amount']:.2f} - {safe_date(tx['created_at'])}")

    elif st.session_state.menu == "Profilo":
        user = st.session_state.user
        
        st.markdown(f"""
        <div class="section-header">
            <h1>👤 @{user['username']}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        balance = get_wallet_balance(user['id'])
        st.markdown(f"""
        ### 📊 Info
        - 📧 {user['email']}
        - 💰 Wallet: €{balance:.2f}
        - 🕐 Iscritto: {safe_date(user['created_at'])}
        """)
        
        st.divider()
        st.markdown("### 🎴 Le Tue Carte")
        
        conn = get_conn()
        my_cards = to_dict_list(conn.execute(text("""
            SELECT * FROM carte WHERE user_id = :id ORDER BY created_at DESC
        """), {"id": user["id"]}))
        conn.close()
        
        if not my_cards:
            st.info("📷 Nessuna carta")
        else:
            cols = st.columns(4)
            for i, c in enumerate(my_cards):
                with cols[i % 4]:
                    st.markdown('<div class="card-item">', unsafe_allow_html=True)
                    
                    img_b64 = get_image_b64(c.get('immagine'))
                    if img_b64:
                        st.image(f"data:image/png;base64,{img_b64}")
                    
                    st.write(f"**{c['nome']}**")
                    rarity_class = get_rarity_class(c.get('rarita', 'Rara'))
                    st.markdown(f"<span class='badge-rarity {rarity_class}'>{c.get('rarita')}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='price-display'>€{c['prezzo']:.2f}</div>", unsafe_allow_html=True)
                    
                    if c['sold']:
                        st.success("✅ VENDUTA")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
