# pokemon_marketplace.py - VERSIONE OTTIMIZZATA
import streamlit as st
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
from PIL import Image
import io
import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import time

# ==================== CONFIGURAZIONE ====================
st.set_page_config(
    page_title="Pokemon Card Marketplace",
    page_icon="🎴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS OTTIMIZZATO + DARK MODE ====================
def load_css():
    st.markdown("""
    <style>
    /* VARIABILI DARK/LIGHT */
    :root {
        --bg-primary: #0f0f23;
        --bg-secondary: #1a1a2e;
        --bg-card: #16213e;
        --text-primary: #e4e4e7;
        --text-secondary: #a1a1aa;
        --accent-primary: #7c3aed;
        --accent-secondary: #c026d3;
        --border-color: #27272a;
        --success: #22c55e;
        --warning: #f59e0b;
        --error: #ef4444;
    }
    
    @media (prefers-color-scheme: light) {
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f4f4f5;
            --bg-card: #ffffff;
            --text-primary: #18181b;
            --text-secondary: #71717a;
            --border-color: #e4e4e7;
        }
    }
    
    /* RESET STREAMLIT */
    .main {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        padding: 1rem;
    }
    
    .stApp {
        background: var(--bg-primary);
    }
    
    /* CARDS */
    .card-container {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.2s;
        height: 100%;
    }
    
    .card-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.3);
        border-color: var(--accent-primary);
    }
    
    /* BADGES */
    .rarity-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        color: white;
        margin: 0.5rem 0;
    }
    
    .sold-badge {
        background: var(--error) !important;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .price-tag {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent-primary);
        margin: 0.5rem 0;
    }
    
    /* HEADER */
    .pokemon-title {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 0 0 30px rgba(124, 58, 237, 0.5);
    }
    
    /* COMMENTI */
    .comment-box {
        background: var(--bg-card);
        border-left: 3px solid var(--accent-primary);
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    .comment-author {
        font-weight: 600;
        color: var(--accent-primary);
        margin-bottom: 0.5rem;
    }
    
    /* LOADING */
    .stSpinner > div {
        border-color: var(--accent-primary) !important;
    }
    
    /* RESPONSIVE */
    @media (max-width: 768px) {
        .pokemon-title {
            font-size: 2rem;
        }
        .card-container {
            padding: 0.75rem;
        }
        .price-tag {
            font-size: 1.25rem;
        }
    }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
    }
    
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ==================== DATABASE ====================
DATABASE_URL = st.secrets.get('DATABASE_URL', 'sqlite:///pokemon_marketplace.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

# Connection pooling per performance
engine = create_engine(
    DATABASE_URL, 
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': st.secrets.get('EMAIL_USER', ''),
    'password': st.secrets.get('EMAIL_PASSWORD', '')
}

# ==================== DATABASE FUNCTIONS CON CACHING ====================
@st.cache_resource
def get_engine():
    return engine

def get_connection():
    return get_engine().connect()

def init_db():
    conn = get_connection()
    try:
        # Users
        conn.execute(text('''CREATE TABLE IF NOT EXISTS users (
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
            is_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            rating REAL DEFAULT 0,
            total_sales INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        # Carte - RIMOSSI numero e serie, AGGIUNTO sold
        conn.execute(text('''CREATE TABLE IF NOT EXISTS carte (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
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
        
        # Commenti - NUOVA TABELLA
        conn.execute(text('''CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            carta_id INTEGER REFERENCES carte(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id),
            comment TEXT NOT NULL,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        # Ordini
        conn.execute(text('''CREATE TABLE IF NOT EXISTS ordini (
            id SERIAL PRIMARY KEY,
            buyer_id INTEGER REFERENCES users(id),
            seller_id INTEGER REFERENCES users(id),
            totale REAL,
            commissione REAL,
            stato TEXT DEFAULT 'in attesa',
            metodo_pagamento TEXT,
            stripe_payment_intent TEXT,
            indirizzo_spedizione TEXT,
            tracking_number TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        conn.execute(text('''CREATE TABLE IF NOT EXISTS ordini_dettagli (
            id SERIAL PRIMARY KEY,
            ordine_id INTEGER REFERENCES ordini(id),
            carta_id INTEGER REFERENCES carte(id),
            quantita INTEGER,
            prezzo REAL
        )'''))
        
        conn.commit()
        
        # Admin di default
        result = conn.execute(text("SELECT * FROM users WHERE email='admin@pokemon.com'"))
        if not result.fetchone():
            admin_pass = hash_password('admin123')
            conn.execute(text("""INSERT INTO users (email, username, password, nome, cognome, is_admin, is_verified) 
                         VALUES ('admin@pokemon.com', 'admin', :password, 'Admin', 'System', 1, 1)"""),
                         {'password': admin_pass})
            conn.commit()
    
    except Exception as e:
        st.error(f"Errore DB: {e}")
    finally:
        conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== EMAIL ====================
def send_verification_email(to_email, token, username):
    from_email = st.secrets["EMAIL_USER"]
    password = st.secrets["EMAIL_PASSWORD"]
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Conferma il tuo account - Pokemon Card Marketplace'
    msg['From'] = f'Pokemon Marketplace <{from_email}>'
    msg['To'] = to_email
    
    verification_link = f"https://pokemonpy.streamlit.app/?verify={token}"
    
    text = f"""
Ciao {username}!

Grazie per esserti registrato a Pokemon Card Marketplace.
Per completare la registrazione, clicca sul link qui sotto:

{verification_link}

Il link scade tra 24 ore.

---
Pokemon Card Marketplace
"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0;">Pokemon Card Marketplace</h1>
    </div>
    
    <div style="background: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">
        <h2 style="color: #667eea; margin-top: 0;">Benvenuto {username}!</h2>
        
        <p>Grazie per esserti registrato su Pokemon Card Marketplace.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_link}" 
               style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Conferma il tuo account
            </a>
        </div>
        
        <p style="color: #666; font-size: 14px;">Se il pulsante non funziona, copia e incolla questo link:</p>
        <p style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 5px; word-wrap: break-word; font-size: 12px;">
            {verification_link}
        </p>
        
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        
        <p style="color: #999; font-size: 12px;">
            Il link di verifica scadr&agrave; tra 24 ore.<br>
            &copy; 2026 Pokemon Card Marketplace
        </p>
    </div>
</body>
</html>
"""
    
    part1 = MIMEText(text, 'plain', 'utf-8')
    part2 = MIMEText(html, 'html', 'utf-8')
    
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return True, "Email inviata"
    except Exception as e:
        return False, str(e)

# ==================== USER FUNCTIONS ====================
def register_user(email, username, password, nome, cognome, indirizzo, citta, cap, provincia, telefono):
    conn = get_connection()
    try:
        token = secrets.token_urlsafe(32)
        conn.execute(text("""INSERT INTO users 
                     (email, username, password, nome, cognome, indirizzo, citta, cap, provincia, telefono, verification_token) 
                     VALUES (:email, :username, :password, :nome, :cognome, :indirizzo, :citta, :cap, :provincia, :telefono, :token)"""),
                  {
                      'email': email,
                      'username': username,
                      'password': hash_password(password),
                      'nome': nome,
                      'cognome': cognome,
                      'indirizzo': indirizzo,
                      'citta': citta,
                      'cap': cap,
                      'provincia': provincia,
                      'telefono': telefono,
                      'token': token
                  })
        conn.commit()
        conn.close()
        
        success, message = send_verification_email(email, token, username)
        if success:
            return True, "✅ Registrazione completata! Controlla la tua email."
        else:
            return True, f"⚠️ Account creato ma errore invio email: {message}"
    except Exception as e:
        conn.close()
        if 'email' in str(e).lower():
            return False, "❌ Email già registrata"
        elif 'username' in str(e).lower():
            return False, "❌ Username già in uso"
        return False, f"❌ Errore: {str(e)}"

def verify_user(token):
    conn = get_connection()
    result = conn.execute(text("UPDATE users SET is_verified=1 WHERE verification_token=:token"),
                         {'token': token})
    affected = result.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def login_user(email_or_username, password):
    conn = get_connection()
    result = conn.execute(text("""SELECT * FROM users 
                 WHERE (email=:id OR username=:id) AND password=:password"""),
              {'id': email_or_username, 'password': hash_password(password)})
    user = result.fetchone()
    conn.close()
    return user

# ==================== CARTE FUNCTIONS CON CACHING ====================
@st.cache_data(ttl=30)  # Cache 30 secondi
def get_carte_cached(search="", rarita="", lingua="", min_price=0, max_price=10000):
    conn = get_connection()
    query = """SELECT c.*, u.username 
               FROM carte c 
               JOIN users u ON c.user_id = u.id 
               WHERE c.sold = 0"""
    params = {}
    
    if search:
        query += " AND LOWER(c.nome) LIKE :search"
        params['search'] = f"%{search.lower()}%"
    if rarita:
        query += " AND c.rarita = :rarita"
        params['rarita'] = rarita
    if lingua:
        query += " AND c.lingua = :lingua"
        params['lingua'] = lingua
    
    query += " AND c.prezzo BETWEEN :min_price AND :max_price"
    params['min_price'] = min_price
    params['max_price'] = max_price
    
    query += " ORDER BY c.created_at DESC"
    
    result = conn.execute(text(query), params)
    carte = result.fetchall()
    conn.close()
    return carte

def add_carta(user_id, nome, rarita, lingua, condizione, prezzo, quantita, descrizione, immagine):
    conn = get_connection()
    conn.execute(text("""INSERT INTO carte 
                 (user_id, nome, rarita, lingua, condizione, prezzo, quantita, descrizione, immagine)
                 VALUES (:user_id, :nome, :rarita, :lingua, :condizione, :prezzo, :quantita, :descrizione, :immagine)"""),
              {
                  'user_id': user_id,
                  'nome': nome,
                  'rarita': rarita,
                  'lingua': lingua,
                  'condizione': condizione,
                  'prezzo': prezzo,
                  'quantita': quantita,
                  'descrizione': descrizione,
                  'immagine': immagine
              })
    conn.commit()
    conn.close()
    get_carte_cached.clear()  # Invalida cache

@st.cache_data(ttl=60)
def get_my_carte_cached(user_id):
    conn = get_connection()
    result = conn.execute(text("SELECT * FROM carte WHERE user_id=:user_id ORDER BY created_at DESC"),
                         {'user_id': user_id})
    carte = result.fetchall()
    conn.close()
    return carte

def mark_as_sold(carta_id):
    conn = get_connection()
    conn.execute(text("UPDATE carte SET sold=1 WHERE id=:id"), {'id': carta_id})
    conn.commit()
    conn.close()
    get_carte_cached.clear()
    get_my_carte_cached.clear()

def delete_carta(carta_id):
    conn = get_connection()
    conn.execute(text("DELETE FROM carte WHERE id=:id"), {'id': carta_id})
    conn.commit()
    conn.close()
    get_carte_cached.clear()
    get_my_carte_cached.clear()

# ==================== COMMENTI ====================
def add_comment(carta_id, user_id, comment, rating):
    conn = get_connection()
    conn.execute(text("""INSERT INTO comments (carta_id, user_id, comment, rating)
                 VALUES (:carta_id, :user_id, :comment, :rating)"""),
              {'carta_id': carta_id, 'user_id': user_id, 'comment': comment, 'rating': rating})
    conn.commit()
    conn.close()
    get_comments.clear()

@st.cache_data(ttl=30)
def get_comments(carta_id):
    conn = get_connection()
    result = conn.execute(text("""SELECT c.*, u.username 
                         FROM comments c 
                         JOIN users u ON c.user_id = u.id 
                         WHERE c.carta_id = :carta_id 
                         ORDER BY c.created_at DESC"""),
                         {'carta_id': carta_id})
    comments = result.fetchall()
    conn.close()
    return comments

# ==================== ORDINI ====================
def create_ordine(buyer_id, seller_id, carrello, totale, metodo, indirizzo, stripe_intent=None):
    conn = get_connection()
    commissione = totale * 0.05
    
    result = conn.execute(text("""INSERT INTO ordini 
                 (buyer_id, seller_id, totale, commissione, metodo_pagamento, stripe_payment_intent, indirizzo_spedizione)
                 VALUES (:buyer_id, :seller_id, :totale, :commissione, :metodo, :stripe_intent, :indirizzo)
                 RETURNING id"""),
              {
                  'buyer_id': buyer_id,
                  'seller_id': seller_id,
                  'totale': totale,
                  'commissione': commissione,
                  'metodo': metodo,
                  'stripe_intent': stripe_intent,
                  'indirizzo': indirizzo
              })
    ordine_id = result.fetchone()[0]
    
    for item in carrello:
        conn.execute(text("""INSERT INTO ordini_dettagli (ordine_id, carta_id, quantita, prezzo)
                     VALUES (:ordine_id, :carta_id, :quantita, :prezzo)"""),
                  {
                      'ordine_id': ordine_id,
                      'carta_id': item['id'],
                      'quantita': item['quantita'],
                      'prezzo': item['prezzo']
                  })
        
        # Marca come venduta se quantità = 0
        conn.execute(text("""UPDATE carte 
                     SET quantita = quantita - :qta,
                         sold = CASE WHEN quantita - :qta <= 0 THEN 1 ELSE 0 END
                     WHERE id = :id"""),
                  {'qta': item['quantita'], 'id': item['id']})
    
    conn.commit()
    conn.close()
    get_carte_cached.clear()
    return ordine_id

# ==================== ADMIN ====================
@st.cache_data(ttl=60)
def get_stats():
    conn = get_connection()
    
    r1 = conn.execute(text("SELECT COUNT(*) FROM users"))
    total_users = r1.fetchone()[0]
    
    r2 = conn.execute(text("SELECT COUNT(*) FROM carte"))
    total_carte = r2.fetchone()[0]
    
    r3 = conn.execute(text("SELECT COUNT(*) FROM ordini"))
    total_ordini = r3.fetchone()[0]
    
    r4 = conn.execute(text("SELECT SUM(totale) FROM ordini"))
    total_revenue = r4.fetchone()[0] or 0
    
    r5 = conn.execute(text("SELECT SUM(commissione) FROM ordini"))
    total_commission = r5.fetchone()[0] or 0
    
    conn.close()
    return total_users, total_carte, total_ordini, total_revenue, total_commission

@st.cache_data(ttl=60)
def get_all_users():
    conn = get_connection()
    result = conn.execute(text("SELECT * FROM users ORDER BY created_at DESC"))
    users = result.fetchall()
    conn.close()
    return users

def delete_user(user_id):
    conn = get_connection()
    conn.execute(text("DELETE FROM users WHERE id=:id"), {'id': user_id})
    conn.commit()
    conn.close()
    get_all_users.clear()

def toggle_user_status(user_id, status_type):
    conn = get_connection()
    if status_type == 'admin':
        conn.execute(text("UPDATE users SET is_admin = 1 - is_admin WHERE id=:id"), {'id': user_id})
    else:
        conn.execute(text("UPDATE users SET is_verified = 1 - is_verified WHERE id=:id"), {'id': user_id})
    conn.commit()
    conn.close()
    get_all_users.clear()

@st.cache_data(ttl=60)
def get_all_carte_admin():
    conn = get_connection()
    result = conn.execute(text("""SELECT c.*, u.username 
                         FROM carte c 
                         JOIN users u ON c.user_id = u.id 
                         ORDER BY c.created_at DESC"""))
    carte = result.fetchall()
    conn.close()
    return carte

# ==================== PAGAMENTI STRIPE ====================
def create_stripe_payment(amount):
    """
    Integrazione Stripe per pagamenti
    Richiede: pip install stripe
    """
    try:
        import stripe
        stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", "sk_test_...")
        
        # Crea payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Centesimi
            currency="eur",
            metadata={'integration_check': 'accept_a_payment'}
        )
        
        return intent.id, intent.client_secret
    except Exception as e:
        st.error(f"Errore Stripe: {e}")
        return None, None

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = 'marketplace'
    st.session_state.carrello = []
    st.session_state.processing = False  # Per evitare doppi submit

# ==================== INIT DB ====================
init_db()

# ==================== VERIFICA EMAIL TOKEN ====================
query_params = st.query_params
if 'verify' in query_params:
    token = query_params['verify']
    if verify_user(token):
        st.success("✅ Account verificato! Ora puoi accedere.")
        time.sleep(2)
        st.query_params.clear()
        st.rerun()
    else:
        st.error("❌ Token non valido o scaduto")

# ==================== SIDEBAR MENU ====================
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown(f"### 👤 @{st.session_state.user[2]}")
        st.caption(f"⭐ {st.session_state.user[14]:.1f}")
        
        if st.button("🏪 Marketplace", use_container_width=True):
            st.session_state.page = 'marketplace'
            st.rerun()
        
        if st.button("💰 Vendi", use_container_width=True):
            st.session_state.page = 'sell'
            st.rerun()
        
        if st.button("📦 Le Mie Carte", use_container_width=True):
            st.session_state.page = 'my_cards'
            st.rerun()
        
        cart_count = len(st.session_state.carrello)
        if st.button(f"🛒 Carrello ({cart_count})", use_container_width=True):
            st.session_state.page = 'cart'
            st.rerun()
        
        if st.session_state.user[11]:  # is_admin
            if st.button("👑 Admin", use_container_width=True):
                st.session_state.page = 'admin'
                st.rerun()
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.carrello = []
            st.rerun()

# ==================== PAGINE ====================
if not st.session_state.logged_in:
    st.markdown('<h1 class="pokemon-title">🎴 POKEMON CARD MARKETPLACE</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png" width="80">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png" width="80">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png" width="80">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="80">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 ACCEDI", "📝 REGISTRATI"])
    
    with tab1:
        with st.form("login_form", clear_on_submit=True):
            st.markdown("### 🔑 Accedi al tuo account")
            
            login_id = st.text_input("📧 Email o Username")
            login_pass = st.text_input("🔒 Password", type="password")
            
            submitted = st.form_submit_button(
                "🚀 ACCEDI", 
                use_container_width=True, 
                type="primary",
                disabled=st.session_state.processing
            )
            
            if submitted:
                st.session_state.processing = True
                with st.spinner("Verifica credenziali..."):
                    user = login_user(login_id, login_pass)
                    if user:
                        if user[12]:  # is_verified
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.session_state.processing = False
                            st.success(f"✅ Benvenuto @{user[2]}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.session_state.processing = False
                            st.error("❌ Devi verificare la tua email!")
                    else:
                        st.session_state.processing = False
                        st.error("❌ Credenziali non valide")
        
        st.divider()
        st.markdown("#### 📧 Non hai ricevuto l'email?")
        
        with st.form("resend_form"):
            resend_email = st.text_input("Email")
            resend_submitted = st.form_submit_button("📨 Reinvia")
            
            if resend_submitted and resend_email:
                with st.spinner("Invio email..."):
                    conn = get_connection()
                    result = conn.execute(text("SELECT * FROM users WHERE email=:email AND is_verified=0"),
                                         {'email': resend_email})
                    user_to_verify = result.fetchone()
                    conn.close()
                    
                    if user_to_verify:
                        send_verification_email(user_to_verify[1], user_to_verify[13], user_to_verify[2])
                        st.success("✅ Email reinviata!")
                    else:
                        st.error("❌ Email non trovata")
    
    with tab2:
        with st.form("register_form", clear_on_submit=False):
            st.markdown("### 📝 Crea il tuo account")
            
            reg_email = st.text_input("📧 Email*", key="reg_email")
            reg_username = st.text_input("👤 Username*", key="reg_username")
            
            col1, col2 = st.columns(2)
            with col1:
                reg_pass = st.text_input("🔒 Password*", type="password", key="reg_pass")
            with col2:
                reg_pass_confirm = st.text_input("🔒 Conferma*", type="password", key="reg_pass_confirm")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                reg_nome = st.text_input("Nome*", key="reg_nome")
            with col2:
                reg_cognome = st.text_input("Cognome*", key="reg_cognome")
            
            reg_indirizzo = st.text_input("📍 Indirizzo", key="reg_indirizzo")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                reg_citta = st.text_input("Città", key="reg_citta")
            with col2:
                reg_cap = st.text_input("CAP", key="reg_cap")
            with col3:
                reg_provincia = st.text_input("Provincia", key="reg_provincia")
            
            reg_telefono = st.text_input("📱 Telefono", key="reg_telefono")
            reg_privacy = st.checkbox("✅ Accetto termini*", key="reg_privacy")
            
            submitted = st.form_submit_button(
                "✅ REGISTRATI", 
                use_container_width=True, 
                type="primary",
                disabled=st.session_state.processing
            )
            
            if submitted:
                st.session_state.processing = True
                if not reg_privacy:
                    st.session_state.processing = False
                    st.error("❌ Accetta termini")
                elif reg_pass != reg_pass_confirm:
                    st.session_state.processing = False
                    st.error("❌ Password diverse")
                elif len(reg_pass) < 6:
                    st.session_state.processing = False
                    st.error("❌ Password corta")
                elif not reg_email or not reg_username or not reg_nome or not reg_cognome:
                    st.session_state.processing = False
                    st.error("❌ Compila campi obbligatori")
                else:
                    with st.spinner("Creazione account..."):
                        success, message = register_user(
                            reg_email, reg_username, reg_pass, reg_nome, reg_cognome,
                            reg_indirizzo, reg_citta, reg_cap, reg_provincia, reg_telefono
                        )
                        st.session_state.processing = False
                        if success:
                            st.success(message)
                            for key in list(st.session_state.keys()):
                                if key.startswith('reg_'):
                                    del st.session_state[key]
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(message)

elif st.session_state.logged_in:
    
    # ==================== ADMIN ====================
    if st.session_state.page == 'admin' and st.session_state.user[11]:
        st.markdown('<h2 class="pokemon-title">👑 ADMIN</h2>', unsafe_allow_html=True)
        
        admin_menu = st.radio("", ["📊 Dashboard", "👥 Utenti", "🎴 Carte"], horizontal=True)
        
        if admin_menu == "📊 Dashboard":
            total_users, total_carte, total_ordini, total_revenue, total_commission = get_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Utenti", total_users)
            with col2:
                st.metric("🎴 Carte", total_carte)
            with col3:
                st.metric("📦 Ordini", total_ordini)
            with col4:
                st.metric("💰 Commissioni", f"€{total_commission:.0f}")
        
        elif admin_menu == "👥 Utenti":
            users = get_all_users()
            
            for user_item in users:
                with st.expander(f"@{user_item[2]} - {user_item[1]}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**{user_item[4]} {user_item[5]}**")
                        st.write(f"📧 {user_item[1]}")
                    with col2:
                        st.write(f"⭐ {user_item[14]:.1f}")
                        admin_txt = "✅ Admin" if user_item[11] else "❌"
                        verified_txt = "✅ Verificato" if user_item[12] else "❌"
                        st.write(f"{admin_txt} | {verified_txt}")
                    with col3:
                        if st.button("👑", key=f"adm_{user_item[0]}"):
                            toggle_user_status(user_item[0], 'admin')
                            st.rerun()
                        if st.button("✓", key=f"ver_{user_item[0]}"):
                            toggle_user_status(user_item[0], 'verified')
                            st.rerun()
                        if st.button("🗑️", key=f"del_{user_item[0]}"):
                            delete_user(user_item[0])
                            st.rerun()
        
        else:  # Carte
            carte = get_all_carte_admin()
            
            for carta in carte:
                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                with col1:
                    if carta[9]:
                        img = Image.open(io.BytesIO(carta[9]))
                        st.image(img, width=80)
                with col2:
                    st.write(f"**{carta[2]}**")
                    st.caption(f"@{carta[13]}")
                    if carta[10]:  # sold
                        st.markdown('<span class="sold-badge">VENDUTA</span>', unsafe_allow_html=True)
                with col3:
                    st.write(f"€{carta[6]:.2f} | {carta[7]} pz")
                with col4:
                    if st.button("🗑️", key=f"del_c_{carta[0]}"):
                        delete_carta(carta[0])
                        st.rerun()
    
    # ==================== VENDI ====================
    elif st.session_state.page == 'sell':
        st.markdown("## ➕ Vendi le tue Carte")
        
        with st.form("sell_form", clear_on_submit=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                immagine_file = st.file_uploader("🖼️ Foto*", type=['png', 'jpg', 'jpeg'])
                if immagine_file:
                    st.image(immagine_file, use_container_width=True)
            
            with col2:
                nome = st.text_input("🎴 Nome Carta*")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    rarita = st.selectbox("⭐ Rarità*", 
                        ["Comune", "Non Comune", "Rara", "Holo Rara", "Ultra Rara", 
                         "Full Art", "Rainbow Rare", "Secret Rare"])
                with col_b:
                    lingua = st.selectbox("🌍 Lingua*", 
                        ["Italiano", "Inglese", "Giapponese", "Francese"])
                
                condizione = st.selectbox("💎 Condizione*", 
                    ["Near Mint (NM)", "Excellent (EX)", "Very Good (VG)"])
                
                col_a, col_b = st.columns(2)
                with col_a:
                    prezzo = st.number_input("💰 Prezzo €*", min_value=0.10, step=0.50, value=1.00)
                with col_b:
                    quantita = st.number_input("📦 Quantità*", min_value=1, value=1)
                
                descrizione = st.text_area("📝 Descrizione")
            
            submitted = st.form_submit_button(
                "✅ Pubblica", 
                use_container_width=True, 
                type="primary",
                disabled=st.session_state.processing
            )
            
            if submitted:
                st.session_state.processing = True
                if not immagine_file or not nome:
                    st.session_state.processing = False
                    st.error("❌ Compila tutti i campi *")
                else:
                    with st.spinner("Pubblicazione carta..."):
                        img_bytes = immagine_file.read()
                        add_carta(st.session_state.user[0], nome, rarita, lingua, 
                                 condizione, prezzo, quantita, descrizione, img_bytes)
                        st.session_state.processing = False
                        st.success("🎉 Carta pubblicata!")
                        time.sleep(1)
                        st.rerun()
    
    # ==================== LE MIE CARTE ====================
    elif st.session_state.page == 'my_cards':
        st.markdown("## 📦 Le Mie Carte")
        
        my_carte = get_my_carte_cached(st.session_state.user[0])
        
        if not my_carte:
            st.info("📭 Nessuna carta pubblicata")
        else:
            cols_per_row = 3
            for i in range(0, len(my_carte), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(my_carte):
                        carta = my_carte[i + j]
                        with col:
                            st.markdown('<div class="card-container">', unsafe_allow_html=True)
                            
                            if carta[9]:
                                img = Image.open(io.BytesIO(carta[9]))
                                st.image(img, use_container_width=True)
                            
                            st.markdown(f"### {carta[2]}")
                            
                            # Badge venduta
                            if carta[10]:  # sold
                                st.markdown('<span class="sold-badge">VENDUTA</span>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<span class="rarity-badge">{carta[3]}</span>', 
                                           unsafe_allow_html=True)
                            
                            st.markdown(f'<div class="price-tag">€{carta[6]:.2f}</div>', unsafe_allow_html=True)
                            st.write(f"📦 {carta[7]} | 👁️ {carta[11]}")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if not carta[10] and st.button("✅ Venduta", key=f"sold_{carta[0]}", use_container_width=True):
                                    mark_as_sold(carta[0])
                                    st.rerun()
                            with col_b:
                                if st.button("🗑️ Elimina", key=f"del_{carta[0]}", use_container_width=True):
                                    delete_carta(carta[0])
                                    st.rerun()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== CARRELLO ====================
    elif st.session_state.page == 'cart':
        st.markdown("## 🛒 Il Tuo Carrello")
        
        if not st.session_state.carrello:
            st.info("🛒 Carrello vuoto")
        else:
            for i, item in enumerate(st.session_state.carrello):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**{item['nome']}**")
                with col2:
                    st.markdown(f'<span class="price-tag">€{item["prezzo"]:.2f}</span>', unsafe_allow_html=True)
                with col3:
                    st.write(f"✖️ {item['quantita']}")
                with col4:
                    if st.button("🗑️", key=f"rm_{i}"):
                        st.session_state.carrello.pop(i)
                        st.rerun()
            
            totale = sum(item['prezzo'] * item['quantita'] for item in st.session_state.carrello)
            st.markdown(f'<div style="font-size: 2rem; font-weight: bold; color: var(--accent-primary); margin: 2rem 0;">💰 TOTALE: €{totale:.2f}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                metodo = st.selectbox("💳 Pagamento", ["Stripe", "PayPal", "Bonifico"])
            with col2:
                user = st.session_state.user
                indirizzo_default = f"{user[6]}, {user[7]} {user[8]}" if user[6] else ""
                indirizzo = st.text_area("📍 Indirizzo", value=indirizzo_default)
            
            if st.button(
                "💳 PAGA ORA", 
                type="primary", 
                use_container_width=True,
                disabled=st.session_state.processing
            ):
                st.session_state.processing = True
                
                with st.spinner("Elaborazione pagamento..."):
                    if metodo == "Stripe":
                        # Integrazione Stripe
                        intent_id, client_secret = create_stripe_payment(totale)
                        if intent_id:
                            seller_id = st.session_state.carrello[0]['seller_id']
                            ordine_id = create_ordine(
                                st.session_state.user[0], 
                                seller_id,
                                st.session_state.carrello, 
                                totale, 
                                metodo, 
                                indirizzo,
                                intent_id
                            )
                            st.session_state.processing = False
                            st.success(f"🎉 Ordine #{ordine_id} creato!")
                            st.session_state.carrello = []
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.session_state.processing = False
                            st.error("Errore pagamento Stripe")
                    else:
                        # Altri metodi
                        seller_id = st.session_state.carrello[0]['seller_id']
                        ordine_id = create_ordine(
                            st.session_state.user[0], 
                            seller_id,
                            st.session_state.carrello, 
                            totale, 
                            metodo, 
                            indirizzo
                        )
                        st.session_state.processing = False
                        st.success(f"🎉 Ordine #{ordine_id} creato!")
                        st.session_state.carrello = []
                        time.sleep(2)
                        st.rerun()
    
    # ==================== MARKETPLACE ====================
    else:
        st.markdown('<h1 class="pokemon-title">🏪 MARKETPLACE</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="60">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png" width="60">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/9.png" width="60">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/150.png" width="60">
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search = st.text_input("🔍 Cerca")
        with col2:
            rarita_filter = st.selectbox("⭐ Rarità", 
                ["Tutte", "Comune", "Non Comune", "Rara", "Holo Rara", "Ultra Rara", "Secret Rare"])
        with col3:
            lingua_filter = st.selectbox("🌍 Lingua", 
                ["Tutte", "Italiano", "Inglese", "Giapponese"])
        with col4:
            max_price = st.number_input("💰 Max €", min_value=0, value=1000, step=50)
        
        rarita = rarita_filter if rarita_filter != "Tutte" else ""
        lingua = lingua_filter if lingua_filter != "Tutte" else ""
        
        with st.spinner("Caricamento carte..."):
            carte = get_carte_cached(search, rarita, lingua, 0, max_price)
        
        if not carte:
            st.info("🔍 Nessuna carta trovata")
        else:
            st.write(f"**{len(carte)} carte trovate**")
            
            cols_per_row = 4
            for i in range(0, len(carte), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(carte):
                        carta = carte[i + j]
                        with col:
                            st.markdown('<div class="card-container">', unsafe_allow_html=True)
                            
                            if carta[9]:
                                img = Image.open(io.BytesIO(carta[9]))
                                st.image(img, use_container_width=True)
                            
                            st.markdown(f"### {carta[2]}")
                            st.markdown(f'<span class="seller-badge">@{carta[12]}</span>', unsafe_allow_html=True)
                            
                            st.markdown(f'<span class="rarity-badge">{carta[3]}</span>', 
                                       unsafe_allow_html=True)
                            
                            st.write(f"💎 {carta[5]}")
                            st.markdown(f'<div class="price-tag">€{carta[6]:.2f}</div>', unsafe_allow_html=True)
                            
                            if carta[7] < 5:
                                st.warning(f"⚠️ Solo {carta[7]} pz!")
                            else:
                                st.write(f"📦 {carta[7]} disponibili")
                            
                            # Sistema commenti
                            with st.expander("💬 Commenti"):
                                comments = get_comments(carta[0])
                                
                                if comments:
                                    for comment in comments:
                                        st.markdown(f"""
                                        <div class="comment-box">
                                            <div class="comment-author">@{comment[5]} {'⭐' * comment[4]}</div>
                                            <div>{comment[3]}</div>
                                            <small style="color: var(--text-secondary);">{comment[6]}</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info("Nessun commento")
                                
                                with st.form(f"comment_{carta[0]}"):
                                    new_comment = st.text_area("Scrivi un commento", key=f"cmt_{carta[0]}")
                                    rating = st.select_slider("Valutazione", options=[1,2,3,4,5], value=5, key=f"rat_{carta[0]}")
                                    
                                    if st.form_submit_button("Invia"):
                                        if new_comment:
                                            add_comment(carta[0], st.session_state.user[0], new_comment, rating)
                                            st.success("Commento aggiunto!")
                                            st.rerun()
                            
                            qta = st.number_input("Qta", min_value=1, max_value=carta[7], 
                                                 value=1, key=f"qta_{carta[0]}")
                            
                            if st.button("🛒 Aggiungi", key=f"add_{carta[0]}", use_container_width=True):
                                item = {
                                    'id': carta[0],
                                    'nome': carta[2],
                                    'prezzo': carta[6],
                                    'quantita': qta,
                                    'seller_id': carta[1]
                                }
                                st.session_state.carrello.append(item)
                                st.success("✅ Aggiunto!")
                                time.sleep(0.5)
                                st.rerun()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
