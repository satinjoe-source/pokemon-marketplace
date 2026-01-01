import streamlit as st
import hashlib
import base64
import time
import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from datetime import datetime as dt

# ==================== CONFIGURAZIONE DI BASE ====================
st.set_page_config(
    page_title="PokeMarket ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS: Auto Dark/Light + Velocità ====================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani&display=swap');
    
    :root {
        --primary: #FFCB05;
        --secondary: #D40000;
        --bg-dark: #111111;
        --bg-light: #FFF8E6;
        --text-dark: #111111;
        --text-light: #FFFFFF;
        --card-dark: #1E1E1E;
        --card-light: #FFFFFF;
        --border-dark: rgba(255, 255, 255, 0.1);
        --border-light: rgba(0, 0, 0, 0.1);
        --shadow: rgba(255, 203, 5, 0.2);
    }

    @media (prefers-color-scheme: dark) {
        .stApp { background-color: var(--bg-dark); color: var(--text-light); }
        .card-box { background: var(--card-dark); border-color: var(--border-dark); color: var(--text-light); }
    }
    @media (prefers-color-scheme: light) {
        .stApp { background-color: var(--bg-light); color: var(--text-dark); }
        .card-box { background: var(--card-light); border-color: var(--border-light); color: var(--text-dark); }
    }

    /* Font e stili generali */
    .stApp {
        font-family: 'Rajdhani', sans-serif;
        transition: background 0.3s, color 0.3s;
    }
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: var(--primary) !important;
        text-shadow: 0 0 10px rgba(255, 203, 5, 0.5);
    }
    .nav-logo {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .card-box {
        background: var(--card-dark);
        border: 1px solid var(--border-dark);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: 0.3s;
        height: 100%;
    }
    .card-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px var(--shadow);
    }
    .badge-price {
        font-size: 1.4rem;
        font-weight: 900;
        color: var(--primary);
        text-shadow: 0 0 10px rgba(255, 203, 5, 0.5);
    }
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        border: none;
        color: white;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
    }
    [data-testid="stHeader"], footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ==================== DATABASE SETUP ====================
DATABASE_URL = st.secrets.get("DATABASE_URL", "sqlite:///pokemon_marketplace.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    connect_args=connect_args,
    echo=False  # Non loggare query
)

@st.cache_resource
def get_engine():
    return engine

def get_conn():
    return get_engine().connect()

# ==================== UTILS: DATI SERIALIZZABILI ====================
def to_serializable(v):
    if isinstance(v, (Decimal, dt, datetime.date)):
        return float(v) if isinstance(v, Decimal) else v.isoformat()
    elif isinstance(v, bytes):
        return base64.b64encode(v).decode('utf-8')
    return v

def result_to_dict_list(result):
    return [
        {k: to_serializable(v) for k, v in row._mapping.items()}
        for row in result.fetchall()
    ]

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
            nome TEXT,
            cognome TEXT,
            indirizzo TEXT,
            citta TEXT,
            cap TEXT,
            provincia TEXT,
            telefono TEXT,
            is_verified INTEGER DEFAULT 1,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS ordini (
            id SERIAL PRIMARY KEY,
            buyer_id INTEGER,
            seller_id INTEGER,
            totale REAL,
            indirizzo_spedizione TEXT,
            metodo_pagamento TEXT,
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
        res = conn.execute(text("SELECT * FROM users WHERE email = 'admin@pokemon.com'")).fetchone()
        if not res:
            pw = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute(text("""
                INSERT INTO users (email, username, password, is_verified, created_at)
                VALUES ('admin@pokemon.com', 'admin', :pw, 1, CURRENT_TIMESTAMP)
            """), {"pw": pw})
            conn.commit()

        # Patch: aggiungi created_at a utenti null
        conn.execute(text("""
            UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL
        """))
        conn.commit()

    except Exception as e:
        st.error("Errore DB init.")
    finally:
        conn.close()

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ==================== FETCH DATI (NO FRAGMENTS) ====================
@st.cache_data(ttl=30)
def get_market_cards(search="", rarita="Tutte", lingua="Tutte", max_price=5000):
    conn = get_conn()
    query = """
    SELECT c.id, c.nome, c.rarita, c.lingua, c.prezzo, c.quantita, u.username AS seller_name
    FROM carte c JOIN users u ON c.user_id = u.id
    WHERE c.sold = 0 AND c.prezzo <= :max
    """
    params = {"max": max_price}
    if search: query += " AND LOWER(c.nome) LIKE :search"; params["search"] = f"%{search.lower()}%"
    if rarita != "Tutte": query += " AND c.rarita = :rarita"; params["rarita"] = rarita
    if lingua != "Tutte": query += " AND c.lingua = :lingua"; params["lingua"] = lingua
    query += " ORDER BY c.created_at DESC"
    
    try:
        result = conn.execute(text(query), params)
        return result_to_dict_list(result)
    finally:
        conn.close()

def get_user_listings(user_id):
    conn = get_conn()
    try:
        result = conn.execute(text("""
            SELECT * FROM carte WHERE user_id = :uid ORDER BY created_at DESC
        """), {"uid": user_id})
        return result_to_dict_list(result)
    finally:
        conn.close()

def get_card_image(card_id):
    conn = get_conn()
    try:
        row = conn.execute(text("SELECT immagine FROM carte WHERE id = :id"), {"id": card_id}).fetchone()
        return base64.b64encode(row.immagine).decode() if row and row.immagine else None
    except:
        return None
    finally:
        conn.close()

# ==================== FUNZIONI CARRTINO ====================
def add_to_cart(carta_id, nome, prezzo, seller_id):
    item = {
        "id": carta_id,
        "nome": nome,
        "prezzo": prezzo,
        "quantita": 1,
        "seller_id": seller_id
    }
    st.session_state.carrello.append(item)
    st.toast(f"✅ {nome} aggiunto al carrello!")

def create_order(buyer_id, carrello, totale, metodo, indirizzo):
    conn = get_conn()
    try:
        seller_id = carrello[0]["seller_id"]
        res = conn.execute(text("""
            INSERT INTO ordini (buyer_id, seller_id, totale, metodo_pagamento, indirizzo_spedizione)
            VALUES (:b, :s, :t, :m, :i) RETURNING id
        """), {"b": buyer_id, "s": seller_id, "t": totale, "m": metodo, "i": indirizzo}).fetchone()
        order_id = res[0] if res else conn.execute(text("SELECT lastval()")).fetchone()[0]

        for item in carrello:
            conn.execute(text("""
                INSERT INTO ordini_dettagli (ordine_id, carta_id, quantita, prezzo)
                VALUES (:o, :c, :q, :p)
            """), {"o": order_id, "c": item["id"], "q": 1, "p": item["prezzo"]})
            conn.execute(text("""
                UPDATE carte SET quantita = quantita - 1, sold = CASE WHEN quantita - 1 <= 0 THEN 1 ELSE 0 END
                WHERE id = :id
            """), {"id": item["id"]})
        conn.commit()
        return order_id
    except Exception as e:
        st.error("Errore in checkout")
        return None
    finally:
        conn.close()

# ==================== INIT STATE ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.menu = "Market"
    st.session_state.carrello = []

init_db()

# ==================== NAVBAR ====================
def render_navbar():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<div class="nav-logo">⚡ POKE</div>', unsafe_allow_html=True)
    with col2:
        if st.session_state.logged_in:
            a, b, c, d = st.columns(4)
            if a.button("🏪 Market", use_container_width=True): st.session_state.menu = "Market"
            if b.button("💰 Vendi", use_container_width=True): st.session_state.menu = "Vendi"
            if c.button("🛒 Carrello", use_container_width=True): st.session_state.menu = "Carrello"
            if d.button("📦 Profilo", use_container_width=True): st.session_state.menu = "Profilo"
        else:
            a, b = st.columns(2)
            if a.button("🔑 Login", use_container_width=True): st.session_state.menu = "Login"
            if b.button("📝 Registrazione", use_container_width=True): st.session_state.menu = "Registrazione"

render_navbar()
st.markdown("<br>", unsafe_allow_html=True)

# ==================== PAGINE ====================
if not st.session_state.logged_in:
    # --- REGISTRAZIONE ---
    if st.session_state.menu == "Registrazione":
        st.markdown("## 📝 Crea il tuo account")
        with st.form("reg"):
            email = st.text_input("Email")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            password2 = st.text_input("Conferma", type="password")
            if st.form_submit_button("registrati"):
                if password != password2:
                    st.error("Password non coincidono")
                elif len(password) < 6:
                    st.error("Password troppo corta")
                else:
                    try:
                        conn = get_conn()
                        conn.execute(text("""
                            INSERT INTO users (email, username, password, created_at)
                            VALUES (:e, :u, :p, CURRENT_TIMESTAMP)
                        """), {"e": email, "u": username, "p": hash_password(password)})
                        conn.commit()
                        st.success("✅ Registrato! Ora accedi.")
                        st.session_state.menu = "Login"
                        st.rerun()
                    except:
                        st.error("⚠️ Email o username già in uso")

    # --- LOGIN ---
    else:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="120">
            <h2>Benvenuto a PokeMarket</h2>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            uid = st.text_input("Username o Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("🚀 Accedi"):
                conn = get_conn()
                user = conn.execute(text("""
                    SELECT * FROM users WHERE (email = :u OR username = :u) AND password = :p
                """), {"u": uid, "p": hash_password(pwd)}).fetchone()
                conn.close()
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = dict(user._mapping)
                    st.session_state.menu = "Market"
                    st.rerun()
                else:
                    st.error("❌ Credenziali errate")

# ———————————————————————————————————
# LOGGATO
# ———————————————————————————————————
else:
    # --- MARKET ---
    if st.session_state.menu == "Market":
        st.markdown("""
        <div style="background: linear-gradient(90deg, #FFCB05, #D40000); color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
            <h1>⚡ Trova la tua carta rara!</h1>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        search = c1.text_input("🔍 Cerca Pokemon", "")
        rarita = c2.selectbox("Rarità", ["Tutte", "Rara", "Holo", "Ultra Rara", "Secret"])
        lingua = c3.selectbox("Lingua", ["Tutte", "Italiano", "Inglese", "Giapponese"])
        max_price = c4.number_input("Prezzo max", 1, 10000, 5000)

        cards = get_market_cards(search, rarita, lingua, max_price)
        if not cards:
            st.info("Nessuna carta trovata.")
        else:
            cols = st.columns(4)
            for i, c in enumerate(cards):
                with cols[i % 4]:
                    img = get_card_image(c["id"])
                    if img:
                        st.image(f"data:image/png;base64,{img}", width=120)
                    st.markdown(f"**{c['nome']}**")
                    st.markdown(f"<span style='color:#D40000'>{c['rarita']}</span> | @{c['seller_name']}", unsafe_allow_html=True)
                    st.markdown(f"<div class='badge-price'>€{c['prezzo']:.2f}</div>", unsafe_allow_html=True)
                    if st.button("🛒", key=f"add_{c['id']}"):
                        add_to_cart(c["id"], c["nome"], c["prezzo"], c["user_id"])

    # --- VENDI ---
    elif st.session_state.menu == "Vendi":
        st.markdown("## 💥 Metti in vendita")
        with st.form("vendi"):
            nome = st.text_input("Nome Pokemon")
            rarita = st.selectbox("Rarità", ["Rara", "Holo", "Ultra Rara", "Secret"])
            lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Giapponese"])
            prezzo = st.number_input("Prezzo €", 1.0, step=0.1)
            quantita = st.number_input("Quantità", 1, 100)
            immagine = st.file_uploader("Carica immagine", type=["png", "jpg"])
            if st.form_submit_button("🚀 Pubblica"):
                if not immagine or not nome:
                    st.error("❌ Mancano nome o immagine")
                else:
                    conn = get_conn()
                    conn.execute(text("""
                        INSERT INTO carte (user_id, nome, rarita, lingua, prezzo, quantita, immagine, created_at)
                        VALUES (:u, :n, :r, :l, :p, :q, :img, CURRENT_TIMESTAMP)
                    """), {
                        "u": st.session_state.user["id"], "n": nome, "r": rarita, "l": lingua,
                        "p": prezzo, "q": quantita, "img": immagine.read()
                    })
                    conn.commit()
                    st.success("🎉 Pubblicato!")
                    st.session_state.menu = "Market"
                    st.rerun()

    # --- CARRELLO ---
    elif st.session_state.menu == "Carrello":
        st.markdown("## 🛒 Il tuo carrello")
        if not st.session_state.carrello:
            st.warning("Carrello vuoto!")
        else:
            totale = sum(item["prezzo"] for item in st.session_state.carrello)
            for i, item in enumerate(st.session_state.carrello):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{item['nome']}**")
                c2.write(f"€{item['prezzo']:.2f}")
                if c3.button("❌", key=f"rm_{i}"):
                    st.session_state.carrello.pop(i)
                    st.rerun()
            st.markdown(f"### Totale: €{totale:.2f}")
            
            with st.form("checkout"):
                indirizzo = st.text_area("Indirizzo di spedizione")
                metodo = st.radio("Pagamento", ["💳 Simulato", "🔸 Stripe", "💵 PayPal"])
                if st.form_submit_button("🔐 Paga Ora"):
                    if indirizzo.strip():
                        if metodo == "🔸 Stripe":
                            st.link_button("💳 Vai a Stripe", "https://buy.stripe.com/tuohash", use_container_width=True)
                        elif metodo == "💵 PayPal":
                            st.link_button("💸 Vai a PayPal", "https://paypal.me/tuopoke", use_container_width=True)
                        else:
                            oid = create_order(
                                st.session_state.user["id"],
                                st.session_state.carrello,
                                totale,
                                metodo,
                                indirizzo
                            )
                            if oid:
                                st.balloons()
                                st.success(f"✅ Ordine #{oid} completato!")
                                st.session_state.carrello.clear()
                                time.sleep(2)
                                st.session_state.menu = "Profilo"
                                st.rerun()
                    else:
                        st.error("Inserisci l'indirizzo")

    # --- PROFILO ---
    elif st.session_state.menu == "Profilo":
        user = st.session_state.user
        st.markdown(f"## 👤 @{user['username']}")
        created_at = user.get("created_at")
        data_iscrizione = created_at[:10] if created_at and len(created_at) >= 10 else "N/D"
        st.markdown(f"""
        - **Email**: {user.get('email', 'N/D')}
        - **Iscritto il**: {data_iscrizione}
        """)
        st.divider()

        listings = get_user_listings(user["id"])
        st.markdown(f"### 📦 Le tue vendite ({len(listings)})")
        if not listings:
            st.info("Nessuna carta in vendita")
        else:
            for item in listings:
                c1, c2, c3, c4 = st.columns([1, 3, 1, 1])
                img = get_card_image(item["id"])
                if img:
                    c1.image(f"data:image/png;base64,{img}", width=60)
                c2.write(f"**{item['nome']}**")
                c2.write(f"€{item['prezzo']} • Q:{item['quantita']}")
                c3.write(f"RAR: {item['rarita']}")
                if c4.button("🗑️", key=f"del_{item['id']}"):
                    get_conn().execute(text("DELETE FROM carte WHERE id = :id"), {"id": item["id"]})
                    get_conn().commit()
                    st.rerun()
        st.divider()
