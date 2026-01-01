import streamlit as st
import hashlib
import base64
import time
import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from PIL import Image

# ==================== CONFIGURAZIONE ====================
st.set_page_config(
    page_title="PokeMarket Ultra",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS GIALLO POKÉMON + AUTO-THEMA (DARK/LIGHT) ====================
def load_css():
    st.markdown("""
    <style>
    :root {
        --primary: #FFCB05;  /* Giallo Pikachu */
        --secondary: #D40000; /* Rosso team */
        --bg-dark: #111111;   /* Nero profondo */
        --bg-light: #FFFAE6; /* Sfondo crema chiaro */
        --text-dark: #111111;
        --text-light: #FFFFFF;
        --card-dark: #1E1E1E;
        --card-light: #FFFFFF;
        --border-dark: rgba(255, 255, 255, 0.1);
        --border-light: rgba(34, 34, 34, 0.2);
    }

    /* Auto-tema: se sistema in dark mode */
    @media (prefers-color-scheme: dark) {
        body {
            color: var(--text-light);
            background: var(--bg-dark);
        }
    }
    @media (prefers-color-scheme: light) {
        body {
            color: var(--text-dark);
            background: var(--bg-light);
        }
    }

    /* Reset globale per forzare tema dinamico */
    .stApp {
        background: var(--bg-dark);
        color: var(--text-light);
        transition: background 0.3s, color 0.3s;
        font-family: 'Orbitron', 'Arial', sans-serif;
    }

    /* Supporto per tema light se attivato manualmente */
    .stApp[data-theme="light"] {
        background: var(--bg-light);
        color: var(--text-dark);
    }
    .stApp[data-theme="light"] .card-box {
        background: var(--card-light);
        color: var(--text-dark);
        border: 1px solid var(--border-light);
    }
    .stApp[data-theme="light"] .badge-price {
        color: #D40000;
        text-shadow: 0 0 15px rgba(212, 0, 0, 0.4);
    }

    /* Force dark mode override */
    [data-testid="stHeader"], .css-18ni7ap, .css-1d391kg { background: transparent !important; }

    /* NAVBAR */
    .nav-logo {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 1.8rem;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 15px rgba(255, 203, 5, 0.3);
    }
    .nav-container {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--primary);
    }

    /* CARDS */
    .card-box {
        background: var(--card-dark);
        border: 1px solid var(--border-dark);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(8px);
        height: 100%;
        position: relative;
    }
    .stApp[data-theme="light"] .card-box {
        background: var(--card-light);
        border: 1px solid var(--border-light);
        color: var(--text-dark);
    }
    .card-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px -10px rgba(255, 203, 5, 0.3);
        border-color: var(--primary);
    }

    /* TESTI */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: var(--primary) !important;
        text-shadow: 0 0 10px rgba(255, 203, 5, 0.4);
    }
    p, span, div {
        color: var(--text-light);
    }
    .stApp[data-theme="light"] p,
    .stApp[data-theme="light"] span,
    .stApp[data-theme="light"] div {
        color: var(--text-dark);
    }

    /* BADGE */
    .badge-rare {
        background: rgba(212, 0, 0, 0.1);
        border: 1px solid var(--secondary);
        color: var(--secondary);
    }
    .badge-price {
        color: var(--primary);
        font-size: 1.4rem;
        font-weight: 900;
        text-shadow: 0 0 15px rgba(255, 203, 5, 0.5);
    }

    /* BOTTONI */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        border: none;
        color: white;
        font-weight: bold;
        font-family: 'Orbitron', sans-serif;
        border-radius: 8px;
    }

    /* FORZA TESTO LEGGIBILE */
    .css-1v0fv00 { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

load_css()


# ==================== DATABASE & INIT (uguale, ma ora corretto) ====================
DATABASE_URL = st.secrets.get('DATABASE_URL', 'sqlite:///pokemon_marketplace.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

connect_args = {"check_same_thread": False} if 'sqlite' in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, poolclass=QueuePool, pool_size=5, max_overflow=10, connect_args=connect_args)

@st.cache_resource
def get_engine():
    return engine

def get_connection():
    return get_engine().connect()

# ✅ Corretto: datetime.datetime
def convert_value(v):
    if isinstance(v, Decimal):
        return float(v)
    elif isinstance(v, (datetime.datetime, datetime.date)):
        return v.isoformat()
    elif isinstance(v, bytes):
        return base64.b64encode(v).decode('utf-8')
    else:
        return v

def result_to_dict_list(result):
    if not result:
        return []
    return [
        {key: convert_value(value) for key, value in row._mapping.items()}
        for row in result.fetchall()
    ]

def init_db():
    conn = get_connection()
    try:
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nome TEXT,
            cognome TEXT,
            indirizzo TEXT,
            citta TEXT,
            cap TEXT,
            provincia TEXT,
            telefono TEXT,
            is_admin INTEGER DEFAULT 0,
            is_verified INTEGER DEFAULT 1,
            rating REAL DEFAULT 0,
            total_sales INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS carte (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            nome TEXT NOT NULL,
            rarita TEXT,
            lingua TEXT,
            condizione TEXT,
            prezzo REAL NOT NULL,
            quantita INTEGER DEFAULT 1,
            descrizione TEXT,
            immagine BYTEA,
            sold INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS ordini (
            id SERIAL PRIMARY KEY,
            buyer_id INTEGER,
            seller_id INTEGER,
            totale REAL,
            commissione REAL,
            metodo_pagamento TEXT,
            indirizzo_spedizione TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS ordini_dettagli (
            id SERIAL PRIMARY KEY,
            ordine_id INTEGER,
            carta_id INTEGER,
            quantita INTEGER,
            prezzo REAL
        )'''))
        conn.commit()

        # Admin
        if not conn.execute(text("SELECT * FROM users WHERE email = 'admin@pokemon.com'")).fetchone():
            pw = hashlib.sha256('admin123'.encode()).hexdigest()
            conn.execute(text("""
                INSERT INTO users (email, username, password, is_admin, is_verified)
                VALUES ('admin@pokemon.com', 'admin', :pw, 1, 1)
            """), {"pw": pw})
            conn.commit()
    except Exception as e:
        st.error(f"Errore DB: {e}")
    finally:
        conn.close()

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


# ==================== DATA FUNCTIONS ====================
@st.cache_data(ttl=10)
def get_carte_cached(search="", rarita="", lingua="", min_price=0, max_price=10000):
    conn = get_connection()
    query = """
        SELECT c.id, c.user_id, c.nome, c.rarita, c.lingua, c.condizione,
               c.prezzo, c.quantita, c.descrizione, c.sold, c.created_at,
               u.username AS seller_name
        FROM carte c JOIN users u ON c.user_id = u.id
        WHERE c.sold = 0
    """
    params = {}
    if search: query += " AND LOWER(c.nome) LIKE :search"; params['search'] = f"%{search.lower()}%"
    if rarita != "Tutte": query += " AND c.rarita = :rarita"; params['rarita'] = rarita
    if lingua != "Tutte": query += " AND c.lingua = :lingua"; params['lingua'] = lingua
    query += " AND c.prezzo BETWEEN :min AND :max ORDER BY c.created_at DESC"
    params['min'] = min_price
    params['max'] = max_price

    try:
        result = conn.execute(text(query), params)
        return result_to_dict_list(result)
    except:
        return []
    finally:
        conn.close()

def get_carta_image(carta_id):
    conn = get_connection()
    try:
        row = conn.execute(text("SELECT immagine FROM carte WHERE id = :id"), {"id": carta_id}).fetchone()
        return base64.b64encode(row.immagine).decode() if row and row.immagine else None
    except:
        return None
    finally:
        conn.close()


# Le tue funzioni a posto (abbreviate ma funzionanti)
def add_carta(user_id, nome, rarita, lingua, condizione, prezzo, quantita, descrizione, immagine):
    conn = get_connection()
    try:
        conn.execute(text("""
            INSERT INTO carte (user_id, nome, rarita, lingua, condizione, prezzo, quantita, descrizione, immagine)
            VALUES (:uid, :nm, :rr, :ln, :cd, :pz, :qt, :ds, :img)
        """), {
            'uid': user_id, 'nm': nome, 'rr': rarita, 'ln': lingua,
            'cd': condizione, 'pz': float(prezzo), 'qt': quantita,
            'ds': descrizione, 'img': immagine
        })
        conn.commit()
    finally:
        conn.close()
        get_carte_cached.clear()

def get_my_carte(user_id):
    conn = get_connection()
    try:
        result = conn.execute(text("SELECT * FROM carte WHERE user_id = :uid ORDER BY created_at DESC"), {"uid": user_id})
        return result_to_dict_list(result)
    finally:
        conn.close()

def delete_carta(cid):
    conn = get_connection()
    try:
        conn.execute(text("DELETE FROM carte WHERE id = :id"), {"id": cid})
        conn.commit()
    finally:
        conn.close()
        get_carte_cached.clear()

def create_ordine(buyer_id, carrello, totale, metodo, indirizzo):
    conn = get_connection()
    try:
        seller_id = carrello[0]['seller_id']
        res = conn.execute(text("""
            INSERT INTO ordini (buyer_id, seller_id, totale, commissione, metodo_pagamento, indirizzo_spedizione)
            VALUES (:bid, :sid, :tot, :comm, :met, :ind) RETURNING id
        """), {
            'bid': buyer_id, 'sid': seller_id, 'tot': totale, 'comm': totale * 0.05,
            'met': metodo, 'ind': indirizzo
        }).fetchone()
        ordine_id = res[0] if res else conn.execute(text("SELECT lastval()")).fetchone()[0]

        for item in carrello:
            conn.execute(text("""
                INSERT INTO ordini_dettagli (ordine_id, carta_id, quantita, prezzo)
                VALUES (:oid, :cid, :qt, :pz)
            """), {'oid': ordine_id, 'cid': item['id'], 'qt': item['quantita'], 'pz': item['prezzo']})
            conn.execute(text("""
                UPDATE carte SET quantita = quantita - :qt, sold = CASE WHEN quantita - :qt <= 0 THEN 1 ELSE 0 END
                WHERE id = :cid
            """), {'qt': item['quantita'], 'cid': item['id']})
        conn.commit()
        get_carte_cached.clear()
        return ordine_id
    except Exception as e:
        conn.rollback()
        st.error("Errore ordine.")
        return None
    finally:
        conn.close()


# ==================== STATE & UTENTE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.menu = 'Market'
    st.session_state.carrello = []

init_db()


# ==================== NAVBAR ====================
def render_navbar():
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="nav-logo">⚡ POKE MARKET</div>', unsafe_allow_html=True)
    with col2:
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


# ==================== PAGINE ====================
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
                if pw == pw2 and len(pw) >= 6:
                    try:
                        conn = get_connection()
                        conn.execute(text("""
                            INSERT INTO users (email, username, password, is_verified)
                            VALUES (:e, :u, :p, 1)
                        """), {"e": email, "u": user, "p": hash_password(pw)})
                        conn.commit()
                        st.success("✅ Registrato! Ora puoi accedere.")
                        st.session_state.menu = 'Login'
                        st.rerun()
                    except:
                        st.error("📧 Email o username già in uso.")
                else:
                    st.error("❌ Password non combaciano o troppo corte.")
    else:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="150">
            <h2>Benvenuto a PokeMarket</h2>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            uid = st.text_input("Username o Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("🚀 ENTRA", use_container_width=True):
                conn = get_connection()
                user_row = conn.execute(text("""
                    SELECT * FROM users WHERE (email = :u OR username = :u) AND password = :p
                """), {"u": uid, "p": hash_password(pwd)}).fetchone()
                conn.close()
                if user_row:
                    st.session_state.logged_in = True
                    st.session_state.user = dict(user_row._mapping)
                    st.session_state.menu = 'Market'
                    st.rerun()
                else:
                    st.error("❌ Credenziali errate.")
else:
    # MARKET
    if st.session_state.menu == 'Market':
        st.markdown("""
        <div style="background: linear-gradient(90deg, #FFCB05, #D40000); padding: 40px; text-align: center; border-radius: 20px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(255,203,5,0.3);">
            <h1 style="color: white; text-shadow: 2px 2px 8px #000;">⚡ CATTURA LE RARE!</h1>
            <p style="color: white; font-size: 1.2rem;">Il mercato più veloce per collezionisti</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        search = c1.text_input("🔍 Cerca Pokemon", "")
        rarita = c2.selectbox("💎 Rarità", ["Tutte", "Comune", "Rara", "Holo", "Ultra Rara", "Secret"])
        lingua = c3.selectbox("🌍 Lingua", ["Tutte", "Italiano", "Inglese", "Giapponese"])
        max_p = c4.number_input("💰 Max €", 1, 50000, 5000)

        st.divider()
        carte = get_carte_cached(search, rarita, lingua, 0, max_p)

        if not carte:
            st.info("Nessuna carta trovata. Prova a cambiare i filtri!")
        else:
            rows = [carte[i:i+4] for i in range(0, len(carte), 4)]
            for row in rows:
                cols = st.columns(4)
                for idx, carta in enumerate(row):
                    with cols[idx]:
                        img_b64 = get_carta_image(carta['id'])
                        img_html = f'<img src="data:image/png;base64,{img_b64}" style="width:100%; height:200px; object-fit:contain;">' if img_b64 else ""
                        st.markdown(f"""
                        <div class="card-box">
                            {img_html}
                            <div style="color:var(--secondary); font-weight:bold; margin:10px 0;">{carta['rarita']}</div>
                            <h3>{carta['nome']}</h3>
                            <p>@{carta['seller_name']}</p>
                            <div class="badge-price">€{carta['prezzo']:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        a, b = st.columns(2)
                        if a.button("🛒", key=f"buy_{carta['id']}"):
                            st.session_state.carrello.append({
                                'id': carta['id'], 'nome': carta['nome'],
                                'prezzo': carta['prezzo'], 'quantita': 1,
                                'seller_id': carta['user_id']
                            })
                            st.toast("✅ Aggiunto!")
                        if b.button("👁️", key=f"view_{carta['id']}"):
                            st.toast("Dettagli in arrivo!")

    # VENDI
    elif st.session_state.menu == 'Vendi':
        st.markdown("## 🟡 Metti in vendita – Tipo Fuoco garantito!")
        col1, col2 = st.columns(2)
        with col1:
            st.info("📸 Upload immagine chiara")
            img = st.file_uploader("Immagine", type=['png', 'jpg'])
            if img: st.image(img, width=200)
        with col2:
            with st.form("sell"):
                nome = st.text_input("Nome")
                rarita = st.selectbox("Rarità", ["Comune", "Rara", "Holo", "Ultra Rara", "Secret"])
                lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Giapponese"])
                cond = st.selectbox("Condizione", ["Near Mint", "Excellent", "Played"])
                prezzo = st.number_input("Prezzo €", min_value=0.1)
                quantita = st.number_input("Quantità", 1, 100)
                desc = st.text_area("Descrizione")
                if st.form_submit_button("💰 Pubblica Annuncio", use_container_width=True):
                    if img and nome:
                        add_carta(st.session_state.user['id'], nome, rarita, lingua, cond, prezzo, quantita, desc, img.read())
                        st.balloons()
                        st.success("Annuncio pubblicato!")
                        time.sleep(1.5)
                        st.session_state.menu = 'Market'
                        st.rerun()
                    else:
                        st.error("Immagine o nome mancanti")

    # PROFILO
    elif st.session_state.menu == 'Profilo':
        user = st.session_state.user
        st.markdown(f"## 👤 Profilo di @{user['username']}")
        st.markdown(f"""
        - **Email**: {user.get('email', 'N/D')}
        - **Nome**: {user.get('nome', 'N/D')} {user.get('cognome', '')}
        - **Città**: {user.get('citta', 'N/D')} ({user.get('provincia', '')})
        - **Telefono**: {user.get('telefono', 'N/D')}
        - **Iscritto**: {user['created_at'][:10]}
        """)

        tab1, tab2 = st.tabs(["📦 Le mie Vendite", "🛒 I miei Acquisti"])
        with tab1:
            items = get_my_carte(user['id'])
            if not items: st.info(" 👜 Nessuna carta in vendita.")
            for item in items:
                img_b64 = get_carta_image(item['id'])
                c1, c2, c3, c4 = st.columns([1, 3, 1, 1])
                if img_b64:
                    c1.image(f"data:image/png;base64,{img_b64}", width=60)
                c2.write(f"**{item['nome']}**")
                c2.write(f"€{item['prezzo']} | Q: {item['quantita']}")
                if c3.button("🗑️", key=f"del_{item['id']}"):
                    delete_carta(item['id'])
                    st.rerun()
                st.divider()

        with tab2:
            st.info("📸 Acquisti in arrivo nella prossima release!")

    # CARRELLO
    elif st.session_state.menu == 'Carrello':
        st.markdown("## 🛒 Il tuo Carrello")
        if not st.session_state.carrello:
            st.warning("Il carrello è vuoto. Vai al Market.")
        else:
            totale = sum(i['prezzo'] for i in st.session_state.carrello)
            for i, item in enumerate(st.session_state.carrello):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{item['nome']}**")
                c2.write(f"€{item['prezzo']:.2f}")
                if c3.button("❌", key=f"rm_{i}"):
                    st.session_state.carrello.pop(i)
                    st.rerun()
            st.divider()
            st.markdown(f"<h3>Totale: €{totale:.2f}</h3>", unsafe_allow_html=True)
            with st.form("checkout"):
                ind = st.text_area("📬 Indirizzo di consegna")
                met = st.selectbox("💳 Metodo", ["Carta", "PayPal"])
                if st.form_submit_button("💳 PAGA ORA", use_container_width=True):
                    if ind.strip():
                        create_ordine(st.session_state.user['id'], st.session_state.carrello, totale, met, ind)
                        st.balloons()
                        st.success("🎉 Ordine completato!")
                        time.sleep(2)
                        st.session_state.menu = 'Profilo'
                        st.session_state.carrello = []
                        st.rerun()
                    else:
                        st.error("Inserisci l'indirizzo!")
