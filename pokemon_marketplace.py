# pokemon_marketplace.py - VERSIONE CORRETTA E COMPLETA
import streamlit as st
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
from PIL import Image
import io
import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# ==================== CONFIGURAZIONE DATABASE ====================
DATABASE_URL = st.secrets.get('DATABASE_URL', 'sqlite:///pokemon_marketplace.db')

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

engine = create_engine(DATABASE_URL, poolclass=NullPool)

# ==================== CONFIGURAZIONE EMAIL ====================
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': st.secrets.get('EMAIL_USER', ''),
    'password': st.secrets.get('EMAIL_PASSWORD', '')
}

# ==================== DATABASE FUNCTIONS ====================
def get_connection():
    return engine.connect()

def init_db():
    conn = get_connection()
    
    try:
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
        
        conn.execute(text('''CREATE TABLE IF NOT EXISTS carte (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            nome TEXT NOT NULL,
            serie TEXT,
            numero TEXT,
            rarita TEXT,
            lingua TEXT,
            condizione TEXT,
            prezzo REAL NOT NULL,
            quantita INTEGER DEFAULT 1,
            descrizione TEXT,
            immagine BYTEA,
            stato TEXT DEFAULT 'disponibile',
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''))
        
        conn.execute(text('''CREATE TABLE IF NOT EXISTS ordini (
            id SERIAL PRIMARY KEY,
            buyer_id INTEGER REFERENCES users(id),
            seller_id INTEGER REFERENCES users(id),
            totale REAL,
            commissione REAL,
            stato TEXT DEFAULT 'in attesa',
            metodo_pagamento TEXT,
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

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_verification_email(to_email, token, username):
    from_email = st.secrets["EMAIL_USER"]
    password = st.secrets["EMAIL_PASSWORD"]
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Conferma il tuo account - Pokemon Card Marketplace'
    msg['From'] = f'Pokemon Marketplace <{from_email}>'
    msg['To'] = to_email
    
    verification_link = f"https://pokemonpy.streamlit.app/?verify={token}"
    
    # Plain text
    text = f"""
Ciao {username}!

Grazie per esserti registrato a Pokemon Card Marketplace.

Per completare la registrazione, clicca sul link qui sotto:

{verification_link}

Se non hai richiesto questa registrazione, ignora questa email.

Il link scade tra 24 ore.

---
Pokemon Card Marketplace
Il tuo marketplace di carte Pokemon
"""
    
    # HTML
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
        
        <p>Per completare la registrazione e iniziare a comprare e vendere carte Pokemon, clicca sul pulsante qui sotto:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_link}" 
               style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                Conferma il tuo account
            </a>
        </div>
        
        <p style="color: #666; font-size: 14px;">Se il pulsante non funziona, copia e incolla questo link nel tuo browser:</p>
        <p style="background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 5px; word-wrap: break-word; font-size: 12px;">
            {verification_link}
        </p>
        
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        
        <p style="color: #999; font-size: 12px;">
            Se non hai richiesto questa registrazione, ignora questa email.<br>
            Il link di verifica scadr&agrave; tra 24 ore.
        </p>
        
        <p style="color: #999; font-size: 12px; margin-top: 20px;">
            &copy; 2026 Pokemon Card Marketplace. Tutti i diritti riservati.
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
        return True
    except Exception as e:
        st.error(f"Errore invio email: {e}")
        return False

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
            return True, "✅ Registrazione completata! Controlla la tua email per verificare l'account."
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

def add_carta(user_id, nome, serie, numero, rarita, lingua, condizione, prezzo, quantita, descrizione, immagine):
    conn = get_connection()
    conn.execute(text("""INSERT INTO carte 
                 (user_id, nome, serie, numero, rarita, lingua, condizione, prezzo, quantita, descrizione, immagine)
                 VALUES (:user_id, :nome, :serie, :numero, :rarita, :lingua, :condizione, :prezzo, :quantita, :descrizione, :immagine)"""),
              {
                  'user_id': user_id,
                  'nome': nome,
                  'serie': serie,
                  'numero': numero,
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

def get_my_carte(user_id):
    conn = get_connection()
    result = conn.execute(text("SELECT * FROM carte WHERE user_id=:user_id ORDER BY created_at DESC"),
                         {'user_id': user_id})
    carte = result.fetchall()
    conn.close()
    return carte

def get_carte(search="", rarita="", serie="", lingua="", min_price=0, max_price=10000):
    conn = get_connection()
    query = """SELECT c.*, u.username, u.rating FROM carte c 
               JOIN users u ON c.user_id = u.id 
               WHERE c.quantita > 0 AND c.stato='disponibile'"""
    params = {}
    
    if search:
        query += " AND (c.nome ILIKE :search OR c.descrizione ILIKE :search)"
        params['search'] = f"%{search}%"
    if rarita:
        query += " AND c.rarita = :rarita"
        params['rarita'] = rarita
    if serie:
        query += " AND c.serie ILIKE :serie"
        params['serie'] = f"%{serie}%"
    if lingua:
        query += " AND c.lingua = :lingua"
        params['lingua'] = lingua
    
    query += " AND c.prezzo BETWEEN :min_price AND :max_price"
    params['min_price'] = min_price
    params['max_price'] = max_price
    
    result = conn.execute(text(query), params)
    carte = result.fetchall()
    conn.close()
    return carte

def delete_carta(carta_id):
    conn = get_connection()
    conn.execute(text("DELETE FROM carte WHERE id=:id"), {'id': carta_id})
    conn.commit()
    conn.close()

def increment_views(carta_id):
    conn = get_connection()
    conn.execute(text("UPDATE carte SET views = views + 1 WHERE id=:id"), {'id': carta_id})
    conn.commit()
    conn.close()

def create_ordine(buyer_id, seller_id, carrello, totale, metodo_pagamento, indirizzo):
    conn = get_connection()
    
    commissione = totale * 0.05
    result = conn.execute(text("""INSERT INTO ordini (buyer_id, seller_id, totale, commissione, metodo_pagamento, indirizzo_spedizione)
                 VALUES (:buyer_id, :seller_id, :totale, :commissione, :metodo, :indirizzo)
                 RETURNING id"""),
              {
                  'buyer_id': buyer_id,
                  'seller_id': seller_id,
                  'totale': totale,
                  'commissione': commissione,
                  'metodo': metodo_pagamento,
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
        conn.execute(text("UPDATE carte SET quantita = quantita - :qta WHERE id = :id"),
                  {'qta': item['quantita'], 'id': item['id']})
    
    conn.commit()
    conn.close()
    return ordine_id

def get_all_users():
    conn = get_connection()
    result = conn.execute(text("SELECT * FROM users ORDER BY created_at DESC"))
    users = result.fetchall()
    conn.close()
    return users

def get_all_carte_admin():
    conn = get_connection()
    result = conn.execute(text("""SELECT c.*, u.username FROM carte c 
                 JOIN users u ON c.user_id = u.id 
                 ORDER BY c.created_at DESC"""))
    carte = result.fetchall()
    conn.close()
    return carte

def get_stats():
    conn = get_connection()
    
    result = conn.execute(text("SELECT COUNT(*) FROM users WHERE is_admin=0"))
    total_users = result.fetchone()[0]
    
    result = conn.execute(text("SELECT COUNT(*) FROM carte"))
    total_carte = result.fetchone()[0]
    
    result = conn.execute(text("SELECT COUNT(*) FROM ordini"))
    total_ordini = result.fetchone()[0]
    
    result = conn.execute(text("SELECT COALESCE(SUM(totale), 0) FROM ordini WHERE stato='completato'"))
    total_revenue = result.fetchone()[0]
    
    result = conn.execute(text("SELECT COALESCE(SUM(commissione), 0) FROM ordini WHERE stato='completato'"))
    total_commission = result.fetchone()[0]
    
    conn.close()
    return total_users, total_carte, total_ordini, total_revenue, total_commission

def toggle_user_status(user_id, field):
    conn = get_connection()
    if field == 'admin':
        conn.execute(text("UPDATE users SET is_admin = CASE WHEN is_admin = 1 THEN 0 ELSE 1 END WHERE id=:id"), {'id': user_id})
    elif field == 'verified':
        conn.execute(text("UPDATE users SET is_verified = CASE WHEN is_verified = 1 THEN 0 ELSE 1 END WHERE id=:id"), {'id': user_id})
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = get_connection()
    conn.execute(text("DELETE FROM carte WHERE user_id=:id"), {'id': user_id})
    conn.execute(text("DELETE FROM users WHERE id=:id"), {'id': user_id})
    conn.commit()
    conn.close()

# ==================== CSS ====================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
    }
    
    .pokemon-title {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #FFCB05, #FF0000, #3B4CCA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .card-container {
        background: white;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        transition: transform 0.3s, box-shadow 0.3s;
        border: 3px solid #FFCB05;
        margin: 10px 0;
    }
    
    .card-container:hover {
        transform: translateY(-10px) rotate(1deg);
        box-shadow: 0 12px 24px rgba(255,203,5,0.4);
    }
    
    .price-tag {
        background: linear-gradient(135deg, #FF0000, #CC0000);
        color: white;
        padding: 8px 16px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.3rem;
        display: inline-block;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .rarity-badge {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #000;
        padding: 5px 12px;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin: 5px 0;
    }
    
    .ultra-rare {
        background: linear-gradient(135deg, #9333EA, #EC4899);
        color: white;
    }
    
    .secret-rare {
        background: linear-gradient(135deg, #000000, #434343);
        color: #FFD700;
        animation: glow 2s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 10px #FFD700; }
        50% { box-shadow: 0 0 20px #FFD700, 0 0 30px #FFD700; }
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #FF0000, #CC0000);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: 600;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #CC0000, #990000);
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    .cart-total {
        background: linear-gradient(135deg, #3B4CCA, #2D3A8C);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 20px 0;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    .pokemon-header {
        background: linear-gradient(135deg, #FFCB05, #FFA500);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 10px;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF0000;
    }
    
    .stock-low {
        color: #FF0000;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pikachu-corner {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 100px;
        animation: bounce 2s infinite;
        z-index: 1000;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    
    .seller-badge {
        background: linear-gradient(135deg, #3B4CCA, #2D3A8C);
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .verified-badge {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'carrello' not in st.session_state:
    st.session_state.carrello = []
if 'page' not in st.session_state:
    st.session_state.page = 'marketplace'

init_db()

st.set_page_config(page_title="⚡ Pokemon Marketplace", page_icon="⚡", layout="wide")
load_css()

# Pikachu animato
st.markdown("""
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" 
     class="pikachu-corner">
""", unsafe_allow_html=True)

# Check email verification
query_params = st.query_params
if 'verify' in query_params:
    if verify_user(query_params['verify']):
        st.success("✅ Email verificata con successo! Ora puoi effettuare il login.")
        st.balloons()
    else:
        st.error("❌ Token di verifica non valido")

# ==================== NAVBAR ====================
st.markdown('<h1 class="pokemon-title">⚡ POKEMON MARKETPLACE</h1>', unsafe_allow_html=True)

if st.session_state.logged_in:
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
    
    with col1:
        if st.button("🏪 Marketplace", use_container_width=True):
            st.session_state.page = 'marketplace'
            st.rerun()
    
    with col2:
        if st.button("➕ Vendi", use_container_width=True):
            st.session_state.page = 'sell'
            st.rerun()
    
    with col3:
        if st.button("📦 Mie Carte", use_container_width=True):
            st.session_state.page = 'my_cards'
            st.rerun()
    
    with col4:
        cart_label = f"🛒 Carrello ({len(st.session_state.carrello)})"
        if st.button(cart_label, use_container_width=True):
            st.session_state.page = 'cart'
            st.rerun()
    
    with col5:
        if st.session_state.user[11]:  # is_admin
            if st.button("👑 Admin", use_container_width=True):
                st.session_state.page = 'admin'
                st.rerun()
        else:
            st.write(f"👤 @{st.session_state.user[2]}")
    
    with col6:
        st.write(f"⭐ {st.session_state.user[14]:.1f}")
    
    with col7:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.carrello = []
            st.session_state.page = 'marketplace'
            st.rerun()

st.divider()

# ==================== MAIN CONTENT ====================

# Pagina Login/Registrazione
if not st.session_state.logged_in and st.session_state.page == 'marketplace':
    
    # Header Pokemon
    st.markdown("""
    <div class="pokemon-header">
        <div style="display: flex; justify-content: space-around; align-items: center;">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png" width="80">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png" width="80">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png" width="80">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="80">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/133.png" width="80">
            <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/143.png" width="80">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 ACCEDI", "📝 REGISTRATI"])
    
    with tab1:
        with st.form("login_form", clear_on_submit=True):
            st.markdown("### 🔑 Accedi al tuo account")
            
            login_id = st.text_input("📧 Email o Username", placeholder="mario.rossi@email.com")
            login_pass = st.text_input("🔒 Password", type="password")
            
            submitted = st.form_submit_button("🚀 ACCEDI", use_container_width=True, type="primary")
            
            if submitted:
                user = login_user(login_id, login_pass)
                if user:
                    if user[12]:  # is_verified
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success(f"✅ Benvenuto @{user[2]}!")
                        st.rerun()
                    else:
                        st.error("❌ Devi verificare la tua email prima di accedere!")
                        st.info("📧 Controlla la tua casella email oppure usa il form qui sotto per ricevere un nuovo link.")
                else:
                    st.error("❌ Credenziali non valide")
        
        # ✅ NUOVO: Form per reinviare email di verifica
        st.divider()
        st.markdown("#### 📧 Non hai ricevuto l'email di verifica?")
        
        with st.form("resend_form"):
            resend_email = st.text_input("Inserisci la tua email", key="resend_email_input")
            resend_submitted = st.form_submit_button("📨 Reinvia Email di Verifica")
            
            if resend_submitted and resend_email:
                conn = get_connection()
                result = conn.execute(text("SELECT * FROM users WHERE email=:email AND is_verified=0"),
                                     {'email': resend_email})
                user_to_verify = result.fetchone()
                conn.close()
                
                if user_to_verify:
                    send_verification_email(user_to_verify[1], user_to_verify[13], user_to_verify[2])
                    st.success("✅ Email di verifica reinviata! Controlla la tua casella.")
                else:
                    st.error("❌ Email non trovata o account già verificato")
    
    with tab2:
        # ✅ CORRETTO: clear_on_submit=False per non cancellare il form in caso di errore
        with st.form("register_form", clear_on_submit=False):
            st.markdown("### 📝 Crea il tuo account")
            
            reg_email = st.text_input("📧 Email*", placeholder="mario.rossi@email.com", key="reg_email")
            reg_username = st.text_input("👤 Username*", placeholder="mario_rossi", key="reg_username")
            
            col1, col2 = st.columns(2)
            with col1:
                reg_pass = st.text_input("🔒 Password*", type="password", placeholder="Min 6 caratteri", key="reg_pass")
            with col2:
                reg_pass_confirm = st.text_input("🔒 Conferma Password*", type="password", key="reg_pass_confirm")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                reg_nome = st.text_input("Nome*", key="reg_nome")
            with col2:
                reg_cognome = st.text_input("Cognome*", key="reg_cognome")
            
            reg_indirizzo = st.text_input("📍 Indirizzo", placeholder="Via Roma 123", key="reg_indirizzo")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                reg_citta = st.text_input("Città", placeholder="Milano", key="reg_citta")
            with col2:
                reg_cap = st.text_input("CAP", placeholder="20100", key="reg_cap")
            with col3:
                reg_provincia = st.text_input("Provincia", placeholder="MI", key="reg_provincia")
            
            reg_telefono = st.text_input("📱 Telefono", placeholder="+39 333 1234567", key="reg_telefono")
            
            reg_privacy = st.checkbox("✅ Accetto termini e condizioni*", key="reg_privacy")
            
            submitted = st.form_submit_button("✅ REGISTRATI ORA", use_container_width=True, type="primary")
            
            if submitted:
                if not reg_privacy:
                    st.error("❌ Devi accettare i termini e condizioni")
                elif reg_pass != reg_pass_confirm:
                    st.error("❌ Le password non corrispondono")
                elif len(reg_pass) < 6:
                    st.error("❌ Password troppo corta (minimo 6 caratteri)")
                elif not reg_email or not reg_username or not reg_nome or not reg_cognome:
                    st.error("❌ Compila tutti i campi obbligatori (*)")
                else:
                    success, message = register_user(
                        reg_email, reg_username, reg_pass, reg_nome, reg_cognome,
                        reg_indirizzo, reg_citta, reg_cap, reg_provincia, reg_telefono
                    )
                    if success:
                        st.success(message)
                        st.balloons()
                        st.info("📧 Controlla la tua casella email e clicca sul link di verifica!")
                        
                        # ✅ NUOVO: Reset form solo dopo successo
                        for key in list(st.session_state.keys()):
                            if key.startswith('reg_'):
                                del st.session_state[key]
                        st.rerun()
                    else:
                        st.error(message)

# Resto delle pagine (solo se loggato)
elif st.session_state.logged_in:
    
    if st.session_state.page == 'admin' and st.session_state.user[11]:
        st.markdown('<h2 class="pokemon-title">👑 PANNELLO ADMIN</h2>', unsafe_allow_html=True)
        
        admin_menu = st.radio("", ["📊 Dashboard", "👥 Utenti", "🎴 Carte"], horizontal=True)
        
        if admin_menu == "📊 Dashboard":
            total_users, total_carte, total_ordini, total_revenue, total_commission = get_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'''<div class="stat-card">
                    <div class="stat-number">{total_users}</div>
                    <div>👥 Utenti</div>
                </div>''', unsafe_allow_html=True)
            with col2:
                st.markdown(f'''<div class="stat-card">
                    <div class="stat-number">{total_carte}</div>
                    <div>🎴 Carte</div>
                </div>''', unsafe_allow_html=True)
            with col3:
                st.markdown(f'''<div class="stat-card">
                    <div class="stat-number">{total_ordini}</div>
                    <div>📦 Ordini</div>
                </div>''', unsafe_allow_html=True)
            with col4:
                st.markdown(f'''<div class="stat-card">
                    <div class="stat-number">€{total_commission:.0f}</div>
                    <div>💰 Commissioni</div>
                </div>''', unsafe_allow_html=True)
        
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
                    if carta[11]:
                        img = Image.open(io.BytesIO(carta[11]))
                        st.image(img, width=80)
                with col2:
                    st.write(f"**{carta[2]}**")
                    st.caption(f"@{carta[17]}")
                with col3:
                    st.write(f"€{carta[8]:.2f} | {carta[9]} pz")
                with col4:
                    if st.button("🗑️", key=f"del_c_{carta[0]}"):
                        delete_carta(carta[0])
                        st.rerun()
    
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
                    serie = st.text_input("📚 Serie*")
                with col_b:
                    numero = st.text_input("#️⃣ Numero*")
                
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
            
            submitted = st.form_submit_button("✅ Pubblica", use_container_width=True, type="primary")
            
            if submitted:
                if not immagine_file or not nome or not serie or not numero:
                    st.error("❌ Compila tutti i campi *")
                else:
                    img_bytes = immagine_file.read()
                    add_carta(st.session_state.user[0], nome, serie, numero, rarita, lingua, 
                             condizione, prezzo, quantita, descrizione, img_bytes)
                    st.success("🎉 Carta pubblicata!")
                    st.balloons()
    
    elif st.session_state.page == 'my_cards':
        st.markdown("## 📦 Le Mie Carte")
        
        my_carte = get_my_carte(st.session_state.user[0])
        
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
                            
                            if carta[11]:
                                img = Image.open(io.BytesIO(carta[11]))
                                st.image(img, use_container_width=True)
                            
                            st.markdown(f"### {carta[2]}")
                            st.caption(f"{carta[3]} - #{carta[4]}")
                            
                            rarity_class = ""
                            if carta[5] in ["Ultra Rara", "Full Art", "Rainbow Rare"]:
                                rarity_class = "ultra-rare"
                            elif "Secret" in carta[5]:
                                rarity_class = "secret-rare"
                            
                            st.markdown(f'<span class="rarity-badge {rarity_class}">{carta[5]}</span>', 
                                       unsafe_allow_html=True)
                            
                            st.markdown(f'<div class="price-tag">€{carta[8]:.2f}</div>', unsafe_allow_html=True)
                            st.write(f"📦 {carta[9]} | 👁️ {carta[13]}")
                            
                            if st.button("🗑️ Elimina", key=f"del_{carta[0]}", use_container_width=True):
                                delete_carta(carta[0])
                                st.rerun()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
    
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
            st.markdown(f'<div class="cart-total">💰 TOTALE: €{totale:.2f}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                metodo = st.selectbox("💳 Pagamento", ["PayPal", "Satispay", "Carta"])
            with col2:
                user = st.session_state.user
                indirizzo_default = f"{user[6]}, {user[7]} {user[8]}" if user[6] else ""
                indirizzo = st.text_area("📍 Indirizzo", value=indirizzo_default)
            
            if st.button("💳 PAGA ORA", type="primary", use_container_width=True):
                seller_id = st.session_state.carrello[0]['seller_id']
                ordine_id = create_ordine(st.session_state.user[0], seller_id, 
                                         st.session_state.carrello, totale, metodo, indirizzo)
                st.success(f"🎉 Ordine #{ordine_id} creato!")
                st.balloons()
                st.session_state.carrello = []
                st.rerun()
    
    else:  # Marketplace
        st.markdown("""
        <div class="pokemon-header">
            <div style="display: flex; justify-content: space-around; align-items: center;">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png" width="80">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png" width="80">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png" width="80">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png" width="80">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/133.png" width="80">
                <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/143.png" width="80">
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
            serie_filter = st.text_input("📚 Serie")
        
        rarita = rarita_filter if rarita_filter != "Tutte" else ""
        lingua = lingua_filter if lingua_filter != "Tutte" else ""
        
        carte = get_carte(search, rarita, serie_filter, lingua)
        
        if not carte:
            st.info("🔍 Nessuna carta trovata")
        else:
            cols_per_row = 4
            for i in range(0, len(carte), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(carte):
                        carta = carte[i + j]
                        with col:
                            st.markdown('<div class="card-container">', unsafe_allow_html=True)
                            
                            if carta[11]:
                                img = Image.open(io.BytesIO(carta[11]))
                                st.image(img, use_container_width=True)
                                increment_views(carta[0])
                            
                            st.markdown(f"### {carta[2]}")
                            st.caption(f"{carta[3]} - #{carta[4]}")
                            
                            st.markdown(f'<span class="seller-badge">@{carta[16]}</span>', unsafe_allow_html=True)
                            
                            rarity_class = ""
                            if carta[5] in ["Ultra Rara", "Full Art", "Rainbow Rare"]:
                                rarity_class = "ultra-rare"
                            elif "Secret" in carta[5]:
                                rarity_class = "secret-rare"
                            
                            st.markdown(f'<span class="rarity-badge {rarity_class}">{carta[5]}</span>', 
                                       unsafe_allow_html=True)
                            
                            st.write(f"💎 {carta[7]}")
                            st.markdown(f'<div class="price-tag">€{carta[8]:.2f}</div>', unsafe_allow_html=True)
                            
                            if carta[9] < 5:
                                st.markdown(f'<span class="stock-low">⚠️ {carta[9]} pz!</span>', unsafe_allow_html=True)
                            else:
                                st.write(f"📦 {carta[9]} disponibili")
                            
                            qta = st.number_input("Qta", min_value=1, max_value=carta[9], 
                                                 value=1, key=f"qta_{carta[0]}")
                            if st.button("🛒 Aggiungi", key=f"add_{carta[0]}", use_container_width=True):
                                item = {
                                    'id': carta[0],
                                    'nome': carta[2],
                                    'prezzo': carta[8],
                                    'quantita': qta,
                                    'seller_id': carta[1]
                                }
                                st.session_state.carrello.append(item)
                                st.success("✅ Aggiunto!")
                                st.rerun()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
