import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import qrcode
from PIL import Image
from io import BytesIO

# --- 1. KURUMSAL TEMA VE GÜVENLİK ---
st.set_page_config(page_title="Lojistik Pro Enterprise", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f2f6 0%, #dfe4ea 100%); }
    [data-testid="stSidebar"] { background-color: #001e3c !important; color: white; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(90deg, #002b5b 0%, #004085 100%); 
        color: white; font-weight: 600; border: none; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); background: #0056b3; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KULLANICI YÖNETİMİ ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "admin": {"pw": "12345", "name": "Mehmet Emre Türkyılmaz", "role": "Yönetici"},
        "sofor": {"pw": "sofor123", "name": "Ahmet Şoför", "role": "Şoför"}
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# --- 3. VERİ BAĞLANTISI (HATA KORUMALI) ---
URL = "https://docs.google.com/spreadsheets/d/SAYFA_ID_BURAYA/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=URL)
    # Eksik sütunları otomatik oluşturarak KeyError'ı engelle
    for col in ['ID', 'Alici', 'Durum', 'Mesafe', 'Yakit', 'Sofor_Durumu']:
        if col not in df.columns:
            df[col] = "Veri Yok" if col in ['Alici', 'Durum', 'Sofor_Durumu'] else 0
except Exception as e:
    # Bağlantı yoksa veya hata varsa örnek veri göster (Uygulama kapanmaz)
    df = pd.DataFrame([{"ID": "TR-101", "Alici": "Ekol Lojistik", "Durum": "Yolda", "Mesafe": 150, "Yakit": 12, "Sofor_Durumu": "Sürüşte"}])

# --- 4. GİRİŞ VE ANA PANEL ---
def draw_header():
    col1, col2 = st.columns([1, 6])
    with col1: st.image("https://cdn-icons-png.flaticon.com/512/4090/4090434.png", width=90)
    with col2: 
        st.title("Lojistik Pro | Yönetim Portalı")
        st.caption("Uşak Lojistik Operasyon Merkezi")
    st.divider()

if not st.session_state.logged_in:
    draw_header()
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if u in st.session_state.user_db and st.session_state.user_db[u]["pw"] == p:
            st.session_state.logged_in = True
            st.session_state.current_user = u
            st.rerun()
        else: st.error("Hatalı Giriş!")
else:
    user = st.session_state.user_db[st.session_state.current_user]
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        if st.button("🚪 Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    draw_header()

    if user['role'] == "Yönetici":
        t1, t2 = st.tabs(["📊 Filo Takibi", "⚙️ Kayıt Yönetimi"])
        with t1:
            st.dataframe(df, use_container_width=True)
            st.map()
        with t2:
            st.subheader("İşlem Seçin")
            islem = st.radio("", ["Yeni Ekle", "Güncelle", "Sil"])
            
            # --- EKLEME VE SİLME FONKSİYONLARI ---
            if islem == "Yeni Ekle":
                with st.form("ekle"):
                    f_id = st.text_input("ID")
                    f_alici = st.text_input("Firma")
                    if st.form_submit_button("Excel'e Yaz"):
                        yeni_df = pd.concat([df, pd.DataFrame([{"ID": f_id, "Alici": f_alici, "Durum": "Yüklendi", "Mesafe": 0}])], ignore_index=True)
                        conn.update(spreadsheet=URL, data=yeni_df)
                        st.success("Eklendi!")
                        st.rerun()
            elif islem == "Sil":
                sil_id = st.selectbox("ID Seç", df['ID'].tolist())
                if st.button("❌ KALICI OLARAK SİL"):
                    yeni_df = df[df['ID'] != sil_id]
                    conn.update(spreadsheet=URL, data=yeni_df)
                    st.warning("Silindi!")
                    st.rerun()
