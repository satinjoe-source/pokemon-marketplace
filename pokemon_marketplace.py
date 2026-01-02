import streamlit as st
import hashlib
import base64
import time
from datetime import datetime as dt, timedelta
from sqlalchemy import create_engine, text
from datetime import datetime
import statistics

st.set_page_config(
    page_title="Pokemon Portal | Marketplace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS CARDMARKET-STYLE ====================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --primary: #0066cc;
        --primary-dark: #004999;
        --success: #28a745;
        --warning: #ffc107;
        --danger: #dc3545;
        --light-bg: #f8f9fa;
        --card-bg: #ffffff;
        --border: #dee2e6;
        --text: #212529;
        --text-muted: #6c757d;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --light-bg: #1a1d23;
            --card-bg: #25282e;
            --border: #3a3d44;
            --text: #e9ecef;
            --text-muted: #adb5bd;
        }
    }

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: var(--light-bg);
        color: var(--text);
    }

    /* TOP HEADER */
    .site-header {
        background: var(--card-bg);
        border-bottom: 2px solid var(--border);
        padding: 1rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .site-logo {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--primary);
    }
    .wallet-badge {
        background: var(--success);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    /* SEARCH BAR */
    .search-container {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border);
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* CARD TABLE */
    .card-table {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .card-row {
        display: grid;
        grid-template-columns: 80px 2fr 1fr 1fr 1fr 100px;
        gap: 1rem;
        padding: 1rem;
        border-bottom: 1px solid var(--border);
        align-items: center;
        transition: background 0.2s;
    }
    .card-row:hover {
        background: var(--light-bg);
    }
    .card-img {
        width: 70px;
        height: auto;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .card-name {
        font-weight: 600;
        font-size: 1rem;
        color: var(--text);
    }
    .card-seller {
        color: var(--text-muted);
        font-size: 0.9rem;
    }
    .price-badge {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--primary);
    }
    .condition-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .nm { background: #d4edda; color: #155724; }
    .ex { background: #cce5ff; color: #004085; }
    .vg { background: #fff3cd; color: #856404; }
    .gd { background: #f8d7da; color: #721c24; }

    /* STATS BOXES */
    .stat-box {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border);
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--primary);
        margin: 0.5rem 0;
    }
    .stat-label {
        color: var(--text-muted);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* BUTTONS */
    .stButton > button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,102,204,0.3) !important;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--card-bg);
        border-bottom: 2px solid var(--border);
        padding: 0 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        padding: 1rem 1.5rem;
    }

    /* INPUTS */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 0.6rem !important;
        background: var(--card-bg) !important;
    }

    /* HIDE */
    [data-testid="stHeader"], footer, header, .viewerBadge_container__r5tak { 
        display: none !important;
    }

    /* RESPONSIVE */
    @media (max-width: 768px) {
        .card-row {
            grid-template-columns: 60px 1fr;
            gap: 0.5rem;
        }
        .card-row > *:nth-child(n+3) {
            display: none;
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

# ==================== INIT DB COMPLETO ====================
def init_db():
    conn = get_conn()
    try:
        # USERS con rating
        try:
            conn.execute(text('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                wallet_balance REAL DEFAULT 50.0,
                rating REAL DEFAULT 0.0,
                total_sales INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''))
            conn.commit()
        except:
            conn.rollback()
        
        # CARTE con condizione
        try:
            conn.execute(text('''
            CREATE TABLE IF NOT EXISTS carte (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                nome TEXT NOT NULL,
                rarita TEXT,
                condizione TEXT DEFAULT 'NM',
                prezzo REAL NOT NULL,
                descrizione TEXT,
                immagine BYTEA,
                sold INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''))
            conn.commit()
        except:
            conn.rollback()
        
        # TRANSACTIONS
        try:
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
        except:
            conn.rollback()
        
        # WISHLIST
        try:
            conn.execute(text('''
            CREATE TABLE IF NOT EXISTS wishlist (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                carta_nome TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''))
            conn.commit()
        except:
            conn.rollback()
        
        # REVIEWS
        try:
            conn.execute(text('''
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                seller_id INTEGER,
                buyer_id INTEGER,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''))
            conn.commit()
        except:
            conn.rollback()

        # ADMIN
        try:
            result = conn.execute(text("SELECT * FROM users WHERE email = 'admin@pokemon.com'"))
            if not result.fetchone():
                pw = hashlib.sha256("admin123".encode()).hexdigest()
                conn.execute(text("""
                    INSERT INTO users (email, username, password, wallet_balance, rating, created_at)
                    VALUES ('admin@pokemon.com', 'admin', :pw, 1000.0, 5.0, CURRENT_TIMESTAMP)
                """), {"pw": pw})
                conn.commit()
        except:
            conn.rollback()
            
    except Exception as e:
        conn.rollback()
        st.error(f"Errore DB: {e}")
    finally:
        conn.close()

init_db()

# ==================== WALLET ====================
def get_wallet_balance(user_id):
    conn = get_conn()
    try:
        result = conn.execute(text("SELECT wallet_balance FROM users WHERE id = :id"), {"id": user_id})
        balance = result.fetchone()
        return float(balance[0]) if balance and balance[0] is not None else 0.0
    except:
        return 0.0
    finally:
        conn.close()

def add_funds(user_id, amount):
    conn = get_conn()
    try:
        conn.execute(text("UPDATE users SET wallet_balance = COALESCE(wallet_balance, 0) + :amount WHERE id = :id"),
                     {"amount": amount, "id": user_id})
        conn.execute(text("INSERT INTO transactions (buyer_id, amount, tipo, created_at) VALUES (:id, :amount, 'ricarica', CURRENT_TIMESTAMP)"),
                     {"id": user_id, "amount": amount})
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

def process_purchase(buyer_id, seller_id, carta_id, amount):
    conn = get_conn()
    try:
        buyer_balance = get_wallet_balance(buyer_id)
        
        if buyer_balance >= amount:
            conn.execute(text("UPDATE users SET wallet_balance = wallet_balance - :amount WHERE id = :buyer"),
                         {"amount": amount, "buyer": buyer_id})
            
            seller_amount = amount * 0.95
            conn.execute(text("UPDATE users SET wallet_balance = COALESCE(wallet_balance, 0) + :amount, total_sales = total_sales + 1 WHERE id = :seller"),
                         {"amount": seller_amount, "seller": seller_id})
            
            conn.execute(text("UPDATE carte SET sold = 1 WHERE id = :id"), {"id": carta_id})
            
            conn.execute(text("INSERT INTO transactions (buyer_id, seller_id, carta_id, amount, tipo, created_at) VALUES (:buyer, :seller, :carta, :amount, 'acquisto', CURRENT_TIMESTAMP)"),
                         {"buyer": buyer_id, "seller": seller_id, "carta": carta_id, "amount": amount})
            
            conn.commit()
            return True
        return False
    except:
        conn.rollback()
        return False
    finally:
        conn.close()

# ==================== STATS ====================
@st.cache_data(ttl=60)
def get_market_stats(carta_nome=None):
    conn = get_conn()
    try:
        if carta_nome:
            result = conn.execute(text("SELECT AVG(prezzo) as avg, MIN(prezzo) as min, MAX(prezzo) as max, COUNT(*) as total FROM carte WHERE nome = :nome AND sold = 0"),
                                 {"nome": carta_nome})
        else:
            result = conn.execute(text("SELECT AVG(prezzo) as avg, MIN(prezzo) as min, MAX(prezzo) as max, COUNT(*) as total FROM carte WHERE sold = 0"))
        
        stats = result.fetchone()
        return {
            'avg': float(stats[0]) if stats[0] else 0,
            'min': float(stats[1]) if stats[1] else 0,
            'max': float(stats[2]) if stats[2] else 0,
            'total': int(stats[3]) if stats[3] else 0
        }
    finally:
        conn.close()

def increment_views(carta_id):
    conn = get_conn()
    try:
        conn.execute(text("UPDATE carte SET views = views + 1 WHERE id = :id"), {"id": carta_id})
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

# ==================== STATE ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = "marketplace"
    st.session_state.carrello = []
    st.session_state.view_mode = "table"  # table o grid

# ==================== HEADER ====================
col1, col2, col3 = st.columns([2, 3, 2])

with col1:
    st.markdown('<div class="site-logo">⚡ POKEMON PORTAL</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.logged_in:
        search_quick = st.text_input("🔍 Cerca carte...", "", key="quick_search", placeholder="Es: Pikachu VMAX")

with col3:
    if st.session_state.logged_in:
        balance = get_wallet_balance(st.session_state.user['id'])
        st.markdown(f'<div class="wallet-badge">💰 €{balance:.2f}</div>', unsafe_allow_html=True)
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

st.markdown('<hr style="margin: 1rem 0;">', unsafe_allow_html=True)

# ==================== NAVIGATION ====================
if st.session_state.logged_in:
    tabs = st.tabs(["🏪 Marketplace", "💎 Vendi", "🛒 Carrello", "⭐ Wishlist", "💳 Wallet", "👤 Profilo"])
    
    # ==================== MARKETPLACE ====================
    with tabs[0]:
        st.markdown("## 🏪 Marketplace")
        
        # FILTRI AVANZATI
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search = st.text_input("🔍 Nome", st.session_state.get("quick_search", ""))
        with col2:
            rarita = st.selectbox("⭐ Rarità", ["Tutte", "Holo", "Ultra Rara", "Secret", "Rara"])
        with col3:
            condizione = st.selectbox("💎 Condizione", ["Tutte", "NM", "EX", "VG", "GD"])
        with col4:
            sort_by = st.selectbox("📊 Ordina", ["Prezzo ↑", "Prezzo ↓", "Più recenti", "Più viste"])
        
        col1, col2 = st.columns([1, 3])
        with col1:
            max_price = st.number_input("💰 Prezzo max €", 1, 10000, 1000)
        with col2:
            view_mode = st.radio("Vista", ["📋 Tabella", "🎴 Griglia"], horizontal=True)
            st.session_state.view_mode = "table" if "Tabella" in view_mode else "grid"
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # QUERY
        query = "SELECT c.*, u.username AS seller, u.rating as seller_rating FROM carte c JOIN users u ON c.user_id = u.id WHERE c.sold = 0 AND c.user_id != :user_id AND c.prezzo <= :max"
        params = {"user_id": st.session_state.user['id'], "max": max_price}
        
        if search:
            query += " AND LOWER(c.nome) LIKE :search"
            params["search"] = f"%{search.lower()}%"
        if rarita != "Tutte":
            query += " AND c.rarita = :rarita"
            params["rarita"] = rarita
        if condizione != "Tutte":
            query += " AND c.condizione = :condizione"
            params["condizione"] = condizione
        
        if "Prezzo ↑" in sort_by:
            query += " ORDER BY c.prezzo ASC"
        elif "Prezzo ↓" in sort_by:
            query += " ORDER BY c.prezzo DESC"
        elif "viste" in sort_by:
            query += " ORDER BY c.views DESC"
        else:
            query += " ORDER BY c.created_at DESC"
        
        conn = get_conn()
        cards = to_dict_list(conn.execute(text(query), params))
        conn.close()
        
        if not cards:
            st.info("🔍 Nessuna carta trovata")
        else:
            # STATS
            stats = get_market_stats()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="stat-box"><div class="stat-label">Carte</div><div class="stat-value">{len(cards)}</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-box"><div class="stat-label">Prezzo Medio</div><div class="stat-value">€{stats["avg"]:.2f}</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat-box"><div class="stat-label">Min</div><div class="stat-value">€{stats["min"]:.2f}</div></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="stat-box"><div class="stat-label">Max</div><div class="stat-value">€{stats["max"]:.2f}</div></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # VISTA TABELLA (CARDMARKET STYLE)
            if st.session_state.view_mode == "table":
                for c in cards:
                    increment_views(c['id'])
                    
                    img_b64 = get_image_b64(c.get('immagine'))
                    img_html = f'<img src="data:image/png;base64,{img_b64}" class="card-img">' if img_b64 else ''
                    
                    cond_class = {"NM": "nm", "EX": "ex", "VG": "vg", "GD": "gd"}.get(c.get('condizione', 'NM'), 'nm')
                    
                    st.markdown('<div class="card-table">', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 1, 1, 1, 1])
                    
                    with col1:
                        st.markdown(img_html, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f'<div class="card-name">{c["nome"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-seller">@{c["seller"]} {"⭐" * int(c.get("seller_rating", 0))}</div>', unsafe_allow_html=True)
                        if c.get('descrizione'):
                            with st.expander("📝 Descrizione"):
                                st.write(c['descrizione'])
                    
                    with col3:
                        st.markdown(f'<span class="condition-badge {cond_class}">{c.get("condizione", "NM")}</span>', unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f'<div>{c.get("rarita", "N/D")}</div>', unsafe_allow_html=True)
                    
                    with col5:
                        st.markdown(f'<div class="price-badge">€{c["prezzo"]:.2f}</div>', unsafe_allow_html=True)
                        st.caption(f"👁️ {c.get('views', 0)}")
                    
                    with col6:
                        if st.button("🛒", key=f"add_{c['id']}", help="Aggiungi al carrello"):
                            st.session_state.carrello.append(c)
                            st.toast("✅ Aggiunto!")
                            time.sleep(0.3)
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # VISTA GRIGLIA
            else:
                cols = st.columns(4)
                for i, c in enumerate(cards):
                    with cols[i % 4]:
                        with st.container():
                            img_b64 = get_image_b64(c.get('immagine'))
                            if img_b64:
                                st.image(f"data:image/png;base64,{img_b64}")
                            
                            st.markdown(f"**{c['nome']}**")
                            st.caption(f"@{c['seller']}")
                            st.markdown(f"**€{c['prezzo']:.2f}** | {c.get('condizione', 'NM')}")
                            
                            if st.button("🛒 Aggiungi", key=f"grid_add_{c['id']}", use_container_width=True):
                                st.session_state.carrello.append(c)
                                st.toast("✅")
                                st.rerun()
    
    # ==================== VENDI ====================
    with tabs[1]:
        st.markdown("## 💎 Vendi le tue Carte")
        
        with st.form("vendi_form"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                img = st.file_uploader("📸 Foto*", type=["png", "jpg", "jpeg"])
                if img:
                    st.image(img)
            
            with col2:
                nome = st.text_input("🎴 Nome Carta*")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    rarita = st.selectbox("⭐ Rarità*", ["Holo", "Ultra Rara", "Secret", "Rara"])
                with col_b:
                    condizione = st.selectbox("💎 Condizione*", ["NM", "EX", "VG", "GD"])
                
                prezzo = st.number_input("💰 Prezzo €*", 0.5, 10000.0, 10.0, 0.5)
                descrizione = st.text_area("📝 Descrizione", placeholder="Condizioni, difetti, note...")
                
                st.info("💡 **Condizioni:**\n- **NM** (Near Mint): Carta perfetta\n- **EX** (Excellent): Usura minima\n- **VG** (Very Good): Usura visibile\n- **GD** (Good): Usura evidente")
            
            if st.form_submit_button("🚀 PUBBLICA", use_container_width=True):
                if not img or not nome:
                    st.error("❌ Foto e nome obbligatori")
                else:
                    conn = get_conn()
                    try:
                        conn.execute(text("""
                            INSERT INTO carte (user_id, nome, rarita, condizione, prezzo, descrizione, immagine, created_at)
                            VALUES (:u, :n, :r, :c, :p, :d, :img, CURRENT_TIMESTAMP)
                        """), {
                            "u": st.session_state.user["id"],
                            "n": nome,
                            "r": rarita,
                            "c": condizione,
                            "p": prezzo,
                            "d": descrizione,
                            "img": img.read()
                        })
                        conn.commit()
                        st.success("🎉 Carta pubblicata!")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ {e}")
                    finally:
                        conn.close()
    
    # ==================== CARRELLO ====================
    with tabs[2]:
        st.markdown("## 🛒 Carrello")
        
        if not st.session_state.carrello:
            st.info("🛒 Carrello vuoto")
        else:
            totale = sum(item["prezzo"] for item in st.session_state.carrello)
            balance = get_wallet_balance(st.session_state.user['id'])
            
            # Raggruppa per venditore
            by_seller = {}
            for item in st.session_state.carrello:
                seller = item.get('seller', 'N/D')
                if seller not in by_seller:
                    by_seller[seller] = []
                by_seller[seller].append(item)
            
            for seller, items in by_seller.items():
                st.markdown(f"### 📦 Venditore: @{seller}")
                
                for i, item in enumerate(items):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(f"**{item['nome']}** ({item.get('condizione', 'NM')})")
                    with col2:
                        st.write(f"€{item['prezzo']:.2f}")
                    with col3:
                        st.write(item.get('rarita', ''))
                    with col4:
                        if st.button("🗑️", key=f"rm_{item['id']}"):
                            st.session_state.carrello.remove(item)
                            st.rerun()
                
                st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### Totale: €{totale:.2f}")
                st.write(f"**Saldo: €{balance:.2f}**")
            
            with col2:
                if balance < totale:
                    st.error(f"❌ Saldo insufficiente (-€{totale - balance:.2f})")
                    if st.button("💳 Ricarica Wallet", use_container_width=True):
                        st.session_state.page = "wallet"
                        st.rerun()
                else:
                    if st.button("✅ CONFERMA ORDINE", use_container_width=True, type="primary"):
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
                            st.success("🎉 Ordine completato!")
                            st.session_state.carrello.clear()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Errore")
    
    # ==================== WISHLIST ====================
    with tabs[3]:
        st.markdown("## ⭐ Wishlist")
        st.info("💡 Coming soon: Aggiungi carte alla tua lista desideri e ricevi notifiche quando vengono messe in vendita!")
    
    # ==================== WALLET ====================
    with tabs[4]:
        st.markdown("## 💳 Wallet")
        
        balance = get_wallet_balance(st.session_state.user['id'])
        st.markdown(f'<div class="stat-box"><div class="stat-label">Saldo Disponibile</div><div class="stat-value">€{balance:.2f}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ➕ Ricarica")
            st.info("💡 Demo - Produzione: Stripe/PayPal")
            amount = st.number_input("€", 10.0, 1000.0, 50.0, 10.0)
            if st.button("💳 RICARICA", use_container_width=True):
                add_funds(st.session_state.user['id'], amount)
                st.success(f"✅ +€{amount:.2f}")
                time.sleep(1)
                st.rerun()
        
        with col2:
            st.markdown("### 📊 Transazioni")
            conn = get_conn()
            txs = to_dict_list(conn.execute(text("""
                SELECT * FROM transactions 
                WHERE buyer_id = :id OR seller_id = :id 
                ORDER BY created_at DESC LIMIT 5
            """), {"id": st.session_state.user['id']}))
            conn.close()
            
            for tx in txs:
                tipo_emoji = {"ricarica": "➕", "prelievo": "➖", "acquisto": "🛒"}
                st.write(f"{tipo_emoji.get(tx['tipo'], '💰')} {tx['tipo']} €{tx['amount']:.2f}")
    
    # ==================== PROFILO ====================
    with tabs[5]:
        user = st.session_state.user
        
        st.markdown(f"## 👤 @{user['username']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-box"><div class="stat-label">Rating</div><div class="stat-value">{"⭐" * int(user.get("rating", 0))}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-box"><div class="stat-label">Vendite</div><div class="stat-value">{user.get("total_sales", 0)}</div></div>', unsafe_allow_html=True)
        with col3:
            balance = get_wallet_balance(user['id'])
            st.markdown(f'<div class="stat-box"><div class="stat-label">Wallet</div><div class="stat-value">€{balance:.2f}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🎴 Le Tue Carte")
        
        conn = get_conn()
        my_cards = to_dict_list(conn.execute(text("SELECT * FROM carte WHERE user_id = :id ORDER BY created_at DESC"), {"id": user["id"]}))
        conn.close()
        
        if not my_cards:
            st.info("📷 Nessuna carta")
        else:
            for c in my_cards:
                col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                with col1:
                    img_b64 = get_image_b64(c.get('immagine'))
                    if img_b64:
                        st.image(f"data:image/png;base64,{img_b64}", width=80)
                with col2:
                    st.write(f"**{c['nome']}**")
                    st.caption(f"{c.get('rarita')} | {c.get('condizione')}")
                with col3:
                    st.markdown(f"**€{c['prezzo']:.2f}**")
                with col4:
                    if c['sold']:
                        st.success("✅ VENDUTA")
                    else:
                        st.info("In vendita")

# ==================== LOGIN/REGISTER ====================
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="150"></div>', unsafe_allow_html=True)
        st.markdown("# ⚡ Pokemon Portal")
        st.markdown("### Il marketplace professionale per collezionisti")
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Registrati"])
        
        with tab1:
            with st.form("login"):
                uid = st.text_input("Email o Username")
                pwd = st.text_input("Password", type="password")
                
                if st.form_submit_button("ACCEDI", use_container_width=True):
                    conn = get_conn()
                    try:
                        row = conn.execute(text("SELECT * FROM users WHERE (email = :u OR username = :u) AND password = :p"),
                                         {"u": uid, "p": hashlib.sha256(pwd.encode()).hexdigest()}).fetchone()
                        
                        if row:
                            user = dict(row._mapping)
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.success(f"✅ Benvenuto @{user['username']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Credenziali errate")
                    finally:
                        conn.close()
        
        with tab2:
            with st.form("register"):
                email = st.text_input("Email")
                username = st.text_input("Username")
                pw = st.text_input("Password", type="password")
                pw2 = st.text_input("Conferma Password", type="password")
                
                st.info("🎁 Bonus di benvenuto: €50!")
                
                if st.form_submit_button("REGISTRATI", use_container_width=True):
                    if not email or not username or not pw:
                        st.error("❌ Compila tutti i campi")
                    elif len(pw) < 6:
                        st.error("❌ Password min 6 caratteri")
                    elif pw != pw2:
                        st.error("❌ Password diverse")
                    else:
                        conn = get_conn()
                        try:
                            conn.execute(text("""
                                INSERT INTO users (email, username, password, wallet_balance, created_at)
                                VALUES (:e, :u, :p, 50.0, CURRENT_TIMESTAMP)
                            """), {"e": email, "u": username, "p": hashlib.sha256(pw.encode()).hexdigest()})
                            conn.commit()
                            st.success("✅ Account creato! Accedi ora.")
                            time.sleep(2)
                            st.rerun()
                        except:
                            conn.rollback()
                            st.error("❌ Email/username già in uso")
                        finally:
                            conn.close()
