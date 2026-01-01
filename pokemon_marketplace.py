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

# ==================== CSS MODERNO (Glassmorphism + Dark Auto) ====================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Space+Grotesk:wght@400;600&display=swap');

    /* Colori Pokémon modernizzati */
    :root {
        --bg: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.6);
        --accent: #ffcb05;
        --accent-rgb: 255, 203, 5;
        --text: #e2e8f0;
        --border: rgba(255, 203, 5, 0.2);
        --shadow: rgba(255, 203, 5, 0.1);
        --pulse: #d40000;
    }

    /* Auto tema dark/light: se il sistema è light, cambia */
    @media (prefers-color-scheme: light) {
        :root {
            --bg: #f8fafc;
            --card-bg: rgba(255, 255, 255, 0.8);
            --text: #1e293b;
            --border: rgba(255, 203, 5, 0.4);
            --shadow: rgba(255, 203, 5, 0.15);
        }
    }

    /* Reset */
    .stApp {
        background: var(--bg);
        color: var(--text);
        transition: background 0.4s ease;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Titoli */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: var(--accent) !important;
        text-shadow: 0 0 15px rgba(var(--accent-rgb), 0.4);
    }

    /* Navbar */ 
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 1rem 2rem;
        border-radius: 20px 20px 20px 20px;
        border: 1px solid var(--border);
        margin: 0.5rem auto 2rem auto;
        max-width: 90%;
        box-shadow: 0 10px 30px var(--shadow);
    }
    .nav-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        background: linear-gradient(90deg, var(--accent), var(--pulse));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .nav-item {
        background: none;
        border: none;
        color: var(--text);
        font-weight: bold;
        transition: 0.3s;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }
    .nav-item:hover {
        background: rgba(255, 203, 5, 0.1);
        box-shadow: 0 0 15px rgba(var(--accent-rgb), 0.3);
    }

    /* Card */
    .product-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.2rem;
        transition: all 0.4s ease;
        height: 100%;
        box-shadow: 0 8px 25px var(--shadow);
        backdrop-filter: blur(10px);
    }
    .product-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 40px var(--shadow);
        border-color: var(--accent);
    }

    .price-tag {
        font-size: 1.4rem;
        font-weight: 800;
        color: var(--accent);
        text-shadow: 0 0 10px rgba(var(--accent-rgb), 0.5);
    }

    /* Intestazioni pagina */
    .page-header {
        text-align: center;
        margin: 1rem 0 2rem;
    }
    .page-header h1 {
        margin: 0;
        font-size: 3rem;
        letter-spacing: 1px;
    }
    .page-header p {
        color: #94a3b8;
        font-size: 1.2rem;
    }

    [data-testid="stHeader"], footer, header { visibility: hidden; }
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

# ==================== UTILS: CONVERSIONE SICURA ====================
def to_dict_list(result):
    return [dict(row._mapping) for row in result.fetchall()]

def serializable(v):
    if isinstance(v, (datetime, dt)):
        return v.isoformat()  # ← Sempre stringa
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

# ==================== INIT DB ====================
def init_db():
    conn = get_conn()
    try:
        # Users
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        # Carte
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

        # Admin
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

# ==================== STATO APP ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.menu = "Market"
    st.session_state.carrello = []

# ==================== NAVBAR MODERNO ====================
def render_nav():
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    st.markdown('<div class="nav-title">⚡ POKE<span style="color:#D40000">MARKET</span></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        nav_cols = st.columns(4 if st.session_state.logged_in else 2)
        if st.session_state.logged_in:
            if nav_cols[0].button("🏪 Market", key="nav_mkt"):
                st.session_state.menu = "Market"
                st.rerun()
            if nav_cols[1].button("💰 Vendi", key="nav_vendi"):
                st.session_state.menu = "Vendi"
                st.rerun()
            if nav_cols[2].button("🛒 Carrello", key="nav_cart"):
                st.session_state.menu = "Carrello"
                st.rerun()
            if nav_cols[3].button("📦 Profilo", key="nav_prof"):
                st.session_state.menu = "Profilo"
                st.rerun()
        else:
            if nav_cols[0].button("🔑 Login", key="nav_login"):
                st.session_state.menu = "Login"
                st.rerun()
            if nav_cols[1].button("📝 Registrazione", key="nav_reg"):
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
            <h1>📬 Crea il tuo account</h1>
            <p>Unisciti ai migliori Trainer</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("reg"):
            email = st.text_input("Email")
            username = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            pw2 = st.text_input("Conferma Password", type="password")
            if st.form_submit_button("Registrati"):
                if pw != pw2:
                    st.error("Password non coincidono")
                else:
                    try:
                        conn = get_conn()
                        conn.execute(text("""
                            INSERT INTO users (email, username, password, created_at)
                            VALUES (:e, :u, :p, CURRENT_TIMESTAMP)
                        """), {"e": email, "u": username, "p": hashlib.sha256(pw.encode()).hexdigest()})
                        conn.commit()
                        st.success("✅ Registrato! Ora accedi.")
                        time.sleep(1)
                        st.session_state.menu = "Login"
                        st.rerun()
                    except:
                        st.error("🎯 Email o username già in uso")

    # --- LOGIN ---
    else:
        st.markdown("""
        <div class="page-header">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/385.png" width="130" style="margin: 0 auto;">
            <h1>Benvenuto sul Ring</h1>
            <p>Accedi e cattura i tuoi Pokémon rari</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            uid = st.text_input("Email o Username")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("🔓 ENTRA"):
                row = get_conn().execute(text("""
                    SELECT * FROM users WHERE (email = :u OR username = :u) AND password = :p
                """), {"u": uid, "p": hashlib.sha256(pwd.encode()).hexdigest()}).fetchone()
                if row:
                    st.session_state.logged_in = True
                    user = dict(row._mapping)
                    user['created_at'] = safe_date(user['created_at'])
                    st.session_state.user = user
                    st.session_state.menu = "Market"
                    st.rerun()
                else:
                    st.error("❌ Credenziali errate")

# ——————————————————— LOGGATO ———————————————————
else:
    # --- MARKET ---
    if st.session_state.menu == "Market":
        st.markdown("""
        <div class="page-header">
            <h1>✨ Trova la tua carta perfetta</h1>
            <p>Colleziona, negozia, domina</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2, 1, 1])
        search = c1.text_input("🔍 Cerca", "")
        max_price = c2.number_input("Prezzo max", 1, 100000, 5000)
        if c3.button("🔍 Filtra", use_container_width=True):
            pass  # I dati si aggiorneranno sotto

        query = "SELECT c.*, u.username AS seller FROM carte c JOIN users u ON c.user_id = u.id WHERE c.sold = 0 AND c.prezzo <= :max"
        if search:
            query += " AND LOWER(c.nome) LIKE :search"
        query += " ORDER BY c.created_at DESC"
        params = {"max": max_price, "search": f"%{search.lower()}%" if search else None}
        params = {k: v for k, v in params.items() if v is not None}

        cards = to_dict_list(get_conn().execute(text(query), params))

        cols = st.columns(4)
        for i, c in enumerate(cards):
            with cols[i % 4]:
                img = serializable(c['immagine']) if c['immagine'] else None
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if img:
                    st.image(f"data:image/png;base64,{img}", width=120)
                st.markdown(f"**{c['nome']}**")
                st.markdown(f"<span style='color:#94a3b8'>{c['rarita']} • @{c['seller']}</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='price-tag'>€{c['prezzo']:.2f}</div>", unsafe_allow_html=True)
                if st.button("🛒 Aggiungi", key=f"add_{c['id']}"):
                    st.session_state.carrello.append({
                        "id": c["id"],
                        "nome": c["nome"],
                        "prezzo": c["prezzo"],
                        "seller_id": c["user_id"]
                    })
                    st.toast("✅ Aggiunto!", icon="🛒")
                st.markdown('</div>', unsafe_allow_html=True)

    # --- VENDI ---
    elif st.session_state.menu == "Vendi":
        st.header("🔥 Pubblica la tua carta")
        with st.form("vendi"):
            nome = st.text_input("Nome")
            rarita = st.selectbox("Rarità", ["Holo", "Ultra Rara", "Secret", "Rara"])
            prezzo = st.number_input("Prezzo €", 1.0)
            img = st.file_uploader("Immagine", type=["png", "jpg"])
            if st.form_submit_button("🚀 Pubblica"):
                if not img or not nome:
                    st.error("📸 Foto e nome obbligatori")
                else:
                    get_conn().execute(text("""
                        INSERT INTO carte (user_id, nome, rarita, prezzo, immagine, created_at)
                        VALUES (:u, :n, :r, :p, :img, CURRENT_TIMESTAMP)
                    """), {
                        "u": st.session_state.user["id"], "n": nome, "r": rarita,
                        "p": prezzo, "img": img.read()
                    })
                    get_conn().commit()
                    st.success("🎉 Pubblicato!")
                    time.sleep(1)
                    st.rerun()

    # --- CARRELLO ---
    elif st.session_state.menu == "Carrello":
        st.header("🛒 Il tuo Carrello")
        if not st.session_state.carrello:
            st.info("Vuoto. Vai a caccia di carte!")
        else:
            totale = sum(item["prezzo"] for item in st.session_state.carrello)
            for item in st.session_state.carrello:
                st.markdown(f"- {item['nome']} → €{item['prezzo']:.2f}")

            st.markdown(f"#### Totale: €{totale:.2f}")
            metodo = st.radio("Metodo", ["🔹 Simulato", "🔸 Stripe", "💙 PayPal"])
            if st.button("💳 PAGA ORA"):
                if metodo == "🔸 Stripe":
                    st.link_button("Vai a Stripe", "https://buy.stripe.com/tuohash", type="primary")
                elif metodo == "💙 PayPal":
                    st.link_button("Vai a PayPal", "https://paypal.me/tuopoke", type="secondary")
                else:
                    st.balloons()
                    st.success("🎉 Ordine confermato!")
                    st.session_state.carrello.clear()
                    time.sleep(2)
                    st.rerun()

    # --- PROFILO ---
    elif st.session_state.menu == "Profilo":
        user = st.session_state.user
        created = safe_date(user.get("created_at"))
        st.markdown(f"## 👤 Profilo: @{user['username']}")
        st.markdown(f"""
        - 📧 **Email**: {user.get('email', 'N/D')}
        - 🕐 **Iscritto il**: {created}
        """)
        st.divider()
        st.markdown("### TUE CARTE IN VENDITA")
        query = "SELECT * FROM carte WHERE user_id = :id AND sold = 0"
        results = to_dict_list(get_conn().execute(text(query), {"id": user["id"]}))
        for r in results:
            st.markdown(f"- **{r['nome']}** | €{r['prezzo']} | {r['rarita']}")
        if not results:
            st.info("📷 Nessuna carta in vendita")

