import streamlit as st
import hashlib
import base64
import time
import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from datetime import datetime as dt


# ==================== Pagina unica, temi, velocità ====================
st.set_page_config(
    page_title="PokeMarket ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS: Auto Light/Dark + Veloce ====================
def load_css():
    st.markdown("""
    <style>
    :root {
        --primary: #FFCB05;
        --secondary: #D40000;
        --accent: #2C5CB8;
        --bg-dark: #111111;
        --bg-light: #FFFAE6;
        --text-dark: #111111;
        --text-light: #FFFFFF;
        --card-dark: #1E1E1E;
        --card-light: #FFFFFF;
        --shadow: rgba(255, 203, 5, 0.15);
    }

    @media (prefers-color-scheme: dark) {
        .stApp { background: var(--bg-dark); color: var(--text-light); }
        .card-box { background: var(--card-dark); color: var(--text-light); border-color: rgba(255,255,255,0.1); }
        h1, h2, h3, .badge-price { color: var(--primary); }
    }
    @media (prefers-color-scheme: light) {
        .stApp { background: var(--bg-light); color: var(--text-dark); }
        .card-box { background: var(--card-light); color: var(--text-dark); border-color: rgba(0,0,0,0.1); }
    }

    .nav-logo {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 1.8rem;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 15px rgba(255,203,5,0.3);
    }
    .card-box {
        border: 1px solid;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: 0.3s;
        background: var(--card-dark);
    }
    .card-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px var(--shadow);
    }
    .badge-price {
        font-size: 1.4rem;
        font-weight: 900;
        color: var(--primary);
        text-shadow: 0 0 10px rgba(255, 203, 5, 0.4);
    }
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        border: none;
        color: white;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
    }
    .stApp {
        font-family: 'Rajdhani', sans-serif;
        transition: background 0.3s, color 0.3s;
    }
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: var(--primary) !important;
        text-shadow: 0 0 10px rgba(255, 203, 5, 0.4);
    }
    /* Nascondi loghi */
    header, footer, .css-18ni7ap { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ==================== DATABASE LEGGERO ====================
DATABASE_URL = st.secrets["DATABASE_URL"]
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(
    DATABASE_URL,
    pool_size=3,
    max_overflow=5,
    connect_args={"connect_timeout": 10}
)

@st.cache_resource
def get_engine():
    return engine

def get_conn():
    return get_engine().connect()

def to_serializable(v):
    if isinstance(v, (Decimal)): return float(v)
    if isinstance(v, (dt, datetime.date)): return v.isoformat()
    if isinstance(v, bytes): return base64.b64encode(v).decode()
    return v

def safe_fetch(query, params={}):
    conn = get_conn()
    try:
        res = conn.execute(text(query), params)
        return [dict(row._mapping) for row in res.fetchall()]
    except:
        return []
    finally:
        conn.close()

# 🔁 Svuota solo quando necessario
st.session_state.setdefault("reload", 0)

# ==================== FRAMMENTI: Cambio pagina quasi istantaneo ====================
@st.experimental_fragment
def render_market():
    st.markdown("""
    <div style="background: linear-gradient(90deg, #FFCB05 0%, #D40000 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
        <h1>⚡ CATTURA LE TUE RARE!</h1>
        <p>Il mercato più veloce per Trainers</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    search = c1.text_input("🔍", placeholder="Cerca Charizard...")
    rarity = c2.selectbox("💎", ["Tutte", "Rara", "Holo", "Ultra Rara", "Secret"])
    lang = c3.selectbox("🌍", ["Tutte", "Italiano", "Inglese", "Giapponese"])
    max_price = c4.number_input("€", 1, 100000, 5000)

    query = """
    SELECT c.id, c.nome, c.rarita, c.lingua, c.prezzo, c.quantita,
           u.username as seller_name
    FROM carte c JOIN users u ON c.user_id = u.id
    WHERE c.sold = 0 AND c.prezzo <= :max
    """
    if search: query += " AND LOWER(c.nome) LIKE :search"
    if rarity != "Tutte": query += " AND c.rarita = :rarity"
    if lang != "Tutte": query += " AND c.lingua = :lang"

    params = {
        "max": max_price,
        "search": f"%{search.lower()}%" if search else None,
        "rarity": rarity,
        "lang": lang
    }

    cards = safe_fetch(query, {k: v for k, v in params.items() if v is not None})

    for card in cards:
        img_data = safe_fetch("SELECT immagine FROM carte WHERE id = :id", {"id": card['id']})
        img_b64 = base64.b64encode(img_data[0]["immagine"]).decode() if img_data else None
        col1, col2, col3 = st.columns([1, 3, 1])
        if img_b64:
            col1.image(f"data:image/png;base64,{img_b64}", width=80)
        col2.write(f"**{card['nome']}**")
        col2.write(f"{card['rarita']} @ {card['seller_name']}")
        col3.markdown(f"<div class='badge-price'>€{card['prezzo']:.2f}</div>", unsafe_allow_html=True)
        if st.button("🛒", key=f"add_{card['id']}"):
            st.session_state.carrello.append({
                "id": card['id'],
                "nome": card['nome'],
                "prezzo": card['prezzo'],
                "seller_id": card['user_id']
            })
            st.toast(f"✅ Aggiunto: {card['nome']}")

@st.experimental_fragment
def render_vendi():
    st.markdown("## 💥 Vendi la tua carta")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info("📸 Carica immagine")
        img = st.file_uploader("", type=["png", "jpg"], label_visibility="collapsed")
        if img: st.image(img, width=120)
    with col2:
        with st.form("vendi"):
            nome = st.text_input("Nome")
            rarita = st.selectbox("Rarità", ["Rara", "Holo", "Ultra Rara", "Secret"])
            lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Giapponese"])
            prezzo = st.number_input("Prezzo €", 0.1)
            if st.form_submit_button("🚀 Pubblica"):
                if img and nome:
                    get_conn().execute(text("""
                        INSERT INTO carte (user_id, nome, rarita, lingua, prezzo, immagine, created_at)
                        VALUES (:uid, :n, :r, :l, :p, :img, CURRENT_TIMESTAMP)
                    """), {
                        "uid": st.session_state.user['id'], "n": nome, "r": rarita,
                        "l": lingua, "p": float(prezzo), "img": img.read()
                    })
                    get_conn().commit()
                    st.success("🎉 Pubblicato!")
                    time.sleep(1)
                    st.session_state.menu = "Market"
                    st.rerun()
                else:
                    st.error("Foto o nome mancanti")

@st.experimental_fragment
def render_carrello():
    st.markdown("## 🛒 Carrello")
    if not st.session_state.carrello:
        st.warning("Vuoto 🎒")
        return

    tot = sum(x["prezzo"] for x in st.session_state.carrello)
    for i, x in enumerate(st.session_state.carrello):
        st.write(f"{x['nome']} - €{x['prezzo']:.2f}")
    st.markdown(f"### Totale: €{tot:.2f}")

    checkout = st.radio("Pagamento", ["💳 Simulato", "🔸 Stripe", "💵 PayPal"])
    if st.button("Paga Ora", use_container_width=True):
        if checkout == "🔸 Stripe":
            # Usa https://streamlit-stripe.vercel.app/ oppure fai link esterno
            st.link_button("💳 Vai a Stripe", f"https://buy.stripe.com/test_123", use_container_width=True)
        elif checkout == "💵 PayPal":
            st.link_button("💸 Vai a PayPal", "https://paypal.me/tuopoke", use_container_width=True)
        else:
            st.balloons()
            st.success("✅ Ordine confermato (simulato)")
            st.session_state.carrello.clear()

@st.experimental_fragment
def render_profilo():
    user = st.session_state.user
    st.markdown(f"## 👤 Profilo: @{user['username']}")
    created = user.get("created_at", "N/D")
    created_date = created[:10] if isinstance(created, str) and len(created) >= 10 else "N/D"
    st.markdown(f"""
    - **Iscritto il**: {created_date}
    - **Email**: {user.get("email", "N/D")}
    """)
    my = safe_fetch("SELECT * FROM carte WHERE user_id = :id", {"id": user["id"]})
    st.markdown(f"### 🔥 Hai in vendita: {len(my)} carte")
    for c in my:
        st.write(f"- {c['nome']} - €{c['prezzo']}")

# ==================== NAVBAR GESTITO CON FRAMMENTI ====================
def render_nav():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<div class="nav-logo">⚡ POKE</div>', unsafe_allow_html=True)
    with col2:
        if st.session_state.logged_in:
            a, b, c, d = st.columns(4)
            if a.button("Market", use_container_width=True): st.session_state.menu = "Market"
            if b.button("Vendi", use_container_width=True): st.session_state.menu = "Vendi"
            if c.button("Carrello", use_container_width=True): st.session_state.menu = "Carrello"
            if d.button("Profilo", use_container_width=True): st.session_state.menu = "Profilo"
        else:
            a, b = st.columns(2)
            if a.button("Login", use_container_width=True): st.session_state.menu = "Login"
            if b.button("Registrati", use_container_width=True): st.session_state.menu = "Reg"

render_nav()

# ==================== MENU PRINCIPALE ====================
if not st.session_state.logged_in:
    if st.session_state.menu == "Reg":
        st.markdown("## 📝 Registrati")
        with st.form("reg"):
            em = st.text_input("Email")
            un = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Registrati"):
                try:
                    get_conn().execute(text("""
                        INSERT INTO users (email, username, password, is_verified, created_at)
                        VALUES (:e, :u, :p, 1, CURRENT_TIMESTAMP)
                    """), {"e": em, "u": un, "p": hashlib.sha256(pw.encode()).hexdigest()})
                    get_conn().commit()
                    st.success("✅ Registrato!")
                except:
                    st.error("⚠️ Email o username già usati")
    else:
        st.markdown("## 🔑 Accedi")
        with st.form("login"):
            un = st.text_input("Email o username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("ENTRA"):
                users = safe_fetch("""
                    SELECT * FROM users
                    WHERE (email = :u OR username = :u)
                    AND password = :p
                """, {"u": un, "p": hashlib.sha256(pw.encode()).hexdigest()})
                if users:
                    st.session_state.logged_in = True
                    st.session_state.user = users[0]
                    st.session_state.menu = "Market"
                    st.rerun()
                else:
                    st.error("❌ Credenziali errate")
else:
    if st.session_state.menu == "Market": render_market()
    elif st.session_state.menu == "Vendi": render_vendi()
    elif st.session_state.menu == "Carrello": render_carrello()
    elif st.session_state.menu == "Profilo": render_profilo()
