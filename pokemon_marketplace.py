import streamlit as st
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io
from PIL import Image
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import time
import base64

# ==================== CONFIGURAZIONE ====================
st.set_page_config(
    page_title="PokeMarket Ultra",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS NEXT-GEN (NO SIDEBAR + GLASSMORPHISM) ====================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

    /* NASCONDI SIDEBAR E HEADER STANDARD */
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* COLORI E SFONDO */
    :root {
        --primary: #6366f1;
        --secondary: #a855f7;
        --accent: #ec4899;
        --bg-dark: #0f172a;
        --glass: rgba(30, 41, 59, 0.7);
        --text: #f8fafc;
    }

    .stApp {
        background-color: var(--bg-dark);
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.15) 0px, transparent 50%);
        font-family: 'Rajdhani', sans-serif;
    }

    /* NAVBAR IN ALTO */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--glass);
        backdrop-filter: blur(12px);
        padding: 1rem 2rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 999;
    }

    .nav-logo {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(to right, #6366f1, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
    }

    /* CARDS */
    .card-box {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        height: 100%;
        position: relative;
        overflow: hidden;
    }

    .card-box:hover {
        transform: translateY(-5px);
        border-color: var(--secondary);
        box-shadow: 0 10px 30px -10px rgba(168, 85, 247, 0.3);
    }
    
    .card-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .card-box:hover::before {
        opacity: 1;
    }

    /* TEXT STYLES */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1px;
    }
    
    p, div, span {
        color: var(--text);
    }

    /* BADGES */
    .badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .badge-rare { background: rgba(168, 85, 247, 0.2); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.5); }
    .badge-price { font-size: 1.4rem; font-weight: 800; color: #4ade80; text-shadow: 0 0 10px rgba(74, 222, 128, 0.3); }

    /* INPUTS & BUTTONS */
    .stTextInput > div > div {
        background-color: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        border: none;
        color: white;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.6);
    }
    
    /* CUSTOM TABS INSTEAD OF SIDEBAR */
    .custom-tab {
        cursor: pointer;
        padding: 10px 20px;
        border-radius: 8px;
        margin-right: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .custom-tab:hover { background: rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ==================== DATABASE & UTILS ====================
DATABASE_URL = st.secrets.get('DATABASE_URL', 'sqlite:///pokemon_marketplace.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

connect_args = {"check_same_thread": False} if 'sqlite' in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    connect_args=connect_args
)

@st.cache_resource
def get_engine():
    return engine

def get_connection():
    return get_engine().connect()

# Funzione CRUCIALE per convertire i risultati DB in DIZIONARI (risolve l'errore cache)
def result_to_dict_list(result):
    return [dict(row._mapping) for row in result.fetchall()]

def init_db():
    conn = get_connection()
    try:
        conn.execute(text('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            nome TEXT, cognome TEXT, indirizzo TEXT, citta TEXT, cap TEXT, provincia TEXT, telefono TEXT,
            is_admin INTEGER DEFAULT 0, is_verified INTEGER DEFAULT 0, verification_token TEXT,
            rating REAL DEFAULT 0, total_sales INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        conn.execute(text('''CREATE TABLE IF NOT EXISTS carte (
            id SERIAL PRIMARY KEY, user_id INTEGER, nome TEXT NOT NULL, rarita TEXT, lingua TEXT,
            condizione TEXT, prezzo REAL NOT NULL, quantita INTEGER DEFAULT 1, descrizione TEXT,
            immagine BYTEA, sold INTEGER DEFAULT 0, views INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        conn.execute(text('''CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY, carta_id INTEGER, user_id INTEGER, comment TEXT, rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        conn.execute(text('''CREATE TABLE IF NOT EXISTS ordini (
            id SERIAL PRIMARY KEY, buyer_id INTEGER, seller_id INTEGER, totale REAL, commissione REAL,
            stato TEXT DEFAULT 'in attesa', metodo_pagamento TEXT, stripe_payment_intent TEXT,
            indirizzo_spedizione TEXT, tracking_number TEXT, note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        conn.execute(text('''CREATE TABLE IF NOT EXISTS ordini_dettagli (
            id SERIAL PRIMARY KEY, ordine_id INTEGER, carta_id INTEGER, quantita INTEGER, prezzo REAL
        )'''))
        
        conn.commit()
        
        # Admin check
        res = conn.execute(text("SELECT * FROM users WHERE email='admin@pokemon.com'"))
        if not res.fetchone():
            pw = hashlib.sha256('admin123'.encode()).hexdigest()
            conn.execute(text("INSERT INTO users (email, username, password, is_admin, is_verified) VALUES ('admin@pokemon.com', 'admin', :pw, 1, 1)"), {'pw': pw})
            conn.commit()
            
    except Exception as e:
        st.error(f"DB Error: {e}")
    finally:
        conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== DATA FETCHING (FIXED CACHING) ====================
@st.cache_data(ttl=10)
def get_carte_cached(search="", rarita="", lingua="", min_price=0, max_price=10000):
    conn = get_connection()
    query = "SELECT c.*, u.username as seller_name FROM carte c JOIN users u ON c.user_id = u.id WHERE c.sold = 0"
    params = {}
    
    if search:
        query += " AND LOWER(c.nome) LIKE :search"
        params['search'] = f"%{search.lower()}%"
    if rarita and rarita != "Tutte":
        query += " AND c.rarita = :rarita"
        params['rarita'] = rarita
    if lingua and lingua != "Tutte":
        query += " AND c.lingua = :lingua"
        params['lingua'] = lingua
    
    query += " AND c.prezzo BETWEEN :min AND :max ORDER BY c.created_at DESC"
    params['min'] = min_price
    params['max'] = max_price
    
    result = conn.execute(text(query), params)
    data = result_to_dict_list(result) # Conversione sicura
    conn.close()
    return data

def add_carta(user_id, nome, rarita, lingua, condizione, prezzo, quantita, descrizione, immagine):
    conn = get_connection()
    conn.execute(text("""INSERT INTO carte (user_id, nome, rarita, lingua, condizione, prezzo, quantita, descrizione, immagine)
                 VALUES (:uid, :nm, :rr, :ln, :cd, :pz, :qt, :ds, :img)"""),
              {'uid': user_id, 'nm': nome, 'rr': rarita, 'ln': lingua, 'cd': condizione,
               'pz': prezzo, 'qt': quantita, 'ds': descrizione, 'img': immagine})
    conn.commit()
    conn.close()
    get_carte_cached.clear()

def get_my_carte(user_id):
    conn = get_connection()
    result = conn.execute(text("SELECT * FROM carte WHERE user_id=:uid ORDER BY created_at DESC"), {'uid': user_id})
    data = result_to_dict_list(result)
    conn.close()
    return data

def delete_carta(cid):
    conn = get_connection()
    conn.execute(text("DELETE FROM carte WHERE id=:id"), {'id': cid})
    conn.commit()
    conn.close()
    get_carte_cached.clear()

def create_ordine(buyer_id, carrello, totale, metodo, indirizzo):
    conn = get_connection()
    try:
        seller_id = carrello[0]['seller_id'] # Semplificazione: 1 ordine per 1 venditore alla volta
        res = conn.execute(text("""INSERT INTO ordini (buyer_id, seller_id, totale, commissione, metodo_pagamento, indirizzo_spedizione)
                     VALUES (:bid, :sid, :tot, :comm, :met, :ind) RETURNING id"""),
                  {'bid': buyer_id, 'sid': seller_id, 'tot': totale, 'comm': totale*0.05, 'met': metodo, 'ind': indirizzo})
        
        # Compatibilità SQLite/Postgres per ID
        row = res.fetchone()
        oid = row[0] if row else conn.execute(text("SELECT last_insert_rowid()")).fetchone()[0]
        
        for item in carrello:
            conn.execute(text("INSERT INTO ordini_dettagli (ordine_id, carta_id, quantita, prezzo) VALUES (:oid, :cid, :qt, :pz)"),
                         {'oid': oid, 'cid': item['id'], 'qt': item['quantita'], 'pz': item['prezzo']})
            conn.execute(text("UPDATE carte SET quantita = quantita - :qt, sold = CASE WHEN quantita - :qt <= 0 THEN 1 ELSE 0 END WHERE id = :cid"),
                         {'qt': item['quantita'], 'cid': item['id']})
        
        conn.commit()
        get_carte_cached.clear()
        return oid
    except Exception as e:
        conn.rollback()
        st.error(str(e))
        return None
    finally:
        conn.close()

# ==================== STATE MANAGEMENT ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.menu = 'Market' # State per la navigazione
    st.session_state.carrello = []

init_db()

# ==================== NAVBAR (TOP MENU) ====================
def render_navbar():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="nav-logo">⚡ POKE MARKET</div>', unsafe_allow_html=True)
    
    with col2:
        # Menù orizzontale usando colonne
        if st.session_state.logged_in:
            b1, b2, b3, b4, b5 = st.columns(5)
            if b1.button("🏪 Market", use_container_width=True): st.session_state.menu = 'Market'
            if b2.button("💰 Vendi", use_container_width=True): st.session_state.menu = 'Vendi'
            if b3.button("📦 Profilo", use_container_width=True): st.session_state.menu = 'Profilo'
            
            cart_label = f"🛒 ({len(st.session_state.carrello)})"
            if b4.button(cart_label, use_container_width=True): st.session_state.menu = 'Carrello'
            
            if b5.button("🚪 Esci", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.carrello = []
                st.rerun()
        else:
            b1, b2 = st.columns(2)
            if b1.button("🔑 Accedi", use_container_width=True): st.session_state.menu = 'Login'
            if b2.button("📝 Registrati", use_container_width=True): st.session_state.menu = 'Registrati'

render_navbar()

# ==================== CONTENUTO PAGINE ====================

# --- LOGIN ---
if not st.session_state.logged_in:
    if st.session_state.menu == 'Registrati':
        st.markdown("<h2 style='text-align: center'>📝 Crea il tuo account Trainer</h2>", unsafe_allow_html=True)
        with st.form("reg"):
            c1, c2 = st.columns(2)
            email = c1.text_input("Email")
            user = c2.text_input("Username")
            pw = c1.text_input("Password", type="password")
            pw2 = c2.text_input("Conferma Password", type="password")
            
            if st.form_submit_button("Registrati", use_container_width=True):
                if pw == pw2 and len(pw) > 5:
                    try:
                        conn = get_connection()
                        conn.execute(text("INSERT INTO users (email, username, password, is_verified) VALUES (:e, :u, :p, 1)"),
                                   {'e': email, 'u': user, 'p': hash_password(pw)})
                        conn.commit()
                        conn.close()
                        st.success("Registrato! Ora accedi.")
                    except: st.error("Username o Email già usati.")
                else: st.error("Password non coincidono o troppo corte.")
                
    else: # Login Default
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center; margin-bottom: 30px;'>
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="150">
                <h2>Benvenuto nel Mercato</h2>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login"):
                uid = st.text_input("Username o Email")
                pwd = st.text_input("Password", type="password")
                if st.form_submit_button("🚀 ENTRA", use_container_width=True):
                    conn = get_connection()
                    res = conn.execute(text("SELECT * FROM users WHERE (email=:u OR username=:u) AND password=:p"),
                                     {'u': uid, 'p': hash_password(pwd)})
                    user = res.fetchone()
                    conn.close()
                    if user:
                        st.session_state.logged_in = True
                        # Converto user row in dict per sicurezza session state
                        st.session_state.user = dict(user._mapping)
                        st.session_state.menu = 'Market'
                        st.rerun()
                    else:
                        st.error("Credenziali errate")

# --- APP LOGGATA ---
elif st.session_state.logged_in:
    
    # 1. MARKETPLACE
    if st.session_state.menu == 'Market':
        # Hero Banner
        st.markdown("""
        <div style="background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%); padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 40px -10px rgba(99, 102, 241, 0.5);">
            <h1 style="color: white; margin: 0; font-size: 3rem; text-shadow: 0 2px 10px rgba(0,0,0,0.3);">TROVA LA TUA CARTA RARA</h1>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem;">Il marketplace numero 1 per collezionisti</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtri "Floating"
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            search = c1.text_input("🔍 Cerca Pokemon...", placeholder="Charizard, Pikachu...")
            rarita = c2.selectbox("💎 Rarità", ["Tutte", "Comune", "Rara", "Holo", "Ultra Rara", "Secret"])
            lingua = c3.selectbox("🌍 Lingua", ["Tutte", "Italiano", "Inglese", "Giapponese"])
            max_p = c4.number_input("💰 Max €", value=5000)
        
        st.divider()
        
        # Grid Cards
        carte = get_carte_cached(search, rarita, lingua, 0, max_p)
        
        if not carte:
            st.info("Nessuna carta trovata.")
        
        # Griglia responsive 4 colonne
        rows = [carte[i:i+4] for i in range(0, len(carte), 4)]
        
        for row in rows:
            cols = st.columns(4)
            for idx, carta in enumerate(row):
                with cols[idx]:
                    # Card HTML Structure
                    img_html = ""
                    if carta['immagine']:
                        b64 = base64.b64encode(carta['immagine']).decode()
                        img_html = f'<img src="data:image/png;base64,{b64}" style="width:100%; height:200px; object-fit:contain; margin-bottom: 10px;">'
                    
                    st.markdown(f"""
                    <div class="card-box">
                        {img_html}
                        <div class="badge badge-rare">{carta['rarita']}</div>
                        <h3 style="margin: 10px 0;">{carta['nome']}</h3>
                        <p style="font-size: 0.9rem; color: #94a3b8;">@{carta['seller_name']} | {carta['lingua']}</p>
                        <div class="badge-price">€{carta['prezzo']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Actions
                    c_btn1, c_btn2 = st.columns(2)
                    if c_btn1.button("🛒", key=f"add_{carta['id']}", use_container_width=True):
                        st.session_state.carrello.append({
                            'id': carta['id'], 'nome': carta['nome'],
                            'prezzo': carta['prezzo'], 'quantita': 1,
                            'seller_id': carta['user_id']
                        })
                        st.toast(f"Aggiunto {carta['nome']}!", icon="✅")
                    
                    if c_btn2.button("👁️", key=f"view_{carta['id']}", use_container_width=True):
                        st.toast("Dettagli coming soon", icon="ℹ️")

    # 2. VENDI
    elif st.session_state.menu == 'Vendi':
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("## ➕ Metti in vendita")
            st.info("Carica una foto chiara della carta.")
            img = st.file_uploader("Immagine", type=['png', 'jpg'])
            if img: st.image(img, width=200)
            
        with c2:
            with st.form("sell"):
                nome = st.text_input("Nome Pokemon")
                rarita = st.selectbox("Rarità", ["Comune", "Rara", "Holo", "Ultra Rara", "Secret"])
                lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Giapponese"])
                cond = st.selectbox("Condizione", ["Near Mint", "Excellent", "Played"])
                prz = st.number_input("Prezzo €", min_value=1.0)
                qty = st.number_input("Quantità", min_value=1, value=1)
                desc = st.text_area("Descrizione")
                
                if st.form_submit_button("🚀 Pubblica Annuncio", use_container_width=True):
                    if img and nome:
                        add_carta(st.session_state.user['id'], nome, rarita, lingua, cond, prz, qty, desc, img.read())
                        st.success("Pubblicato!")
                        time.sleep(1)
                        st.session_state.menu = 'Market'
                        st.rerun()
                    else:
                        st.error("Manca nome o foto")

    # 3. CARRELLO
    elif st.session_state.menu == 'Carrello':
        st.markdown("## 🛒 Il tuo Carrello")
        if not st.session_state.carrello:
            st.warning("Vuoto! Vai al Market.")
        else:
            totale = sum(x['prezzo'] for x in st.session_state.carrello)
            
            for i, item in enumerate(st.session_state.carrello):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{item['nome']}**")
                c2.write(f"€{item['prezzo']}")
                if c3.button("❌", key=f"rm_{i}"):
                    st.session_state.carrello.pop(i)
                    st.rerun()
            
            st.divider()
            st.markdown(f"<h2 style='text-align:right'>Totale: €{totale:.2f}</h2>", unsafe_allow_html=True)
            
            with st.form("checkout"):
                ind = st.text_area("Indirizzo di spedizione")
                met = st.selectbox("Pagamento", ["Carta di Credito", "PayPal"])
                if st.form_submit_button("💳 PAGA ORA", use_container_width=True):
                    if ind:
                        oid = create_ordine(st.session_state.user['id'], st.session_state.carrello, totale, met, ind)
                        if oid:
                            st.balloons()
                            st.success(f"Ordine #{oid} completato!")
                            st.session_state.carrello = []
                            time.sleep(3)
                            st.session_state.menu = 'Profilo'
                            st.rerun()
                    else: st.error("Inserisci indirizzo")

    # 4. PROFILO / MIE CARTE
    elif st.session_state.menu == 'Profilo':
        st.markdown(f"## Bentornato, @{st.session_state.user['username']}")
        
        tabs = st.tabs(["📦 Le mie Inserzioni", "🚚 I miei Ordini"])
        
        with tabs[0]:
            items = get_my_carte(st.session_state.user['id'])
            if not items: st.info("Non stai vendendo nulla.")
            
            for item in items:
                with st.container():
                    c1, c2, c3, c4 = st.columns([1, 3, 1, 1])
                    if item['immagine']:
                        c1.image(item['immagine'], width=60)
                    c2.write(f"**{item['nome']}**\n{item['rarita']}")
                    c3.write(f"€{item['prezzo']}")
                    if c4.button("🗑️", key=f"del_{item['id']}"):
                        delete_carta(item['id'])
                        st.rerun()
                    st.divider()
