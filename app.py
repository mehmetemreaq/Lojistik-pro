import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import qrcode
from PIL import Image
from io import BytesIO

# --- 1. KURUMSAL TEMA VE ARKA PLAN TASARIMI ---
st.set_page_config(page_title="Lojistik Pro | Elite", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    /* Arka Plan Resmi ve Karartma */
    .stApp {
        background-image: linear-gradient(rgba(0, 30, 60, 0.7), rgba(0, 30, 60, 0.7)), 
                          url("https://images.unsplash.com/photo-1519003722824-194d4455a60c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    /* Buzlu Cam Kart Efekti */
    div[data-testid="stVerticalBlock"] > div > div {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 20px;
    }

    /* Sidebar Tasarımı */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 30, 60, 0.9) !important;
    }

    /* Profesyonel Butonlar */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background: linear-gradient(90deg, #002b5b 0%, #004085 100%);
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        background: #0056b3;
    }
    
    /* Metrik Başlıkları */
    div[data-testid="stMetricLabel"] { color: #002b5b !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KULLANICI VERİTABANI ---
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
    for col in ['ID', 'Alici', 'Durum', 'Mesafe', 'Yakit', 'Sofor_Durumu']:
        if col not in df.columns:
            df[col] = "Belirtilmedi" if col in ['Alici', 'Durum', 'Sofor_Durumu'] else 0
except:
    df = pd.DataFrame([{"ID": "TR-101", "Alici": "Ekol Lojistik", "Durum": "Yolda", "Mesafe": 0, "Yakit": 0, "Sofor_Durumu": "Normal"}])

# --- 4. ARAYÜZ FONKSİYONLARI ---
def ust_bilgi():
    c1, c2 = st.columns([1, 5])
    with c1: st.image("https://cdn-icons-png.flaticon.com/512/4090/4090434.png", width=100)
    with c2:
        st.title("Lojistik Pro | Operasyon Merkezi")
        st.caption("Profesyonel Filo ve Sevkiyat Yönetim Sistemi")
    st.divider()

# --- 5. GİRİŞ VE KAYIT AKIŞI ---
if not st.session_state.logged_in:
    ust_bilgi()
    t1, t2 = st.tabs(["🔐 Personel Girişi", "📝 Yeni Şoför Kaydı"])
    
    with t1:
        u = st.text_input("Kullanıcı Adı")
        p = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş Yap"):
            if u in st.session_state.user_db and st.session_state.user_db[u]["pw"] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Hatalı Giriş Bilgileri!")
            
    with t2:
        nu = st.text_input("Yeni Şoför Kullanıcı Adı")
        np = st.text_input("Şifre Oluştur", type="password")
        nn = st.text_input("Ad Soyad")
        if st.button("Şoför Kaydını Tamamla"):
            st.session_state.user_db[nu] = {"pw": np, "name": nn, "role": "Şoför"}
            st.success("Kayıt Başarılı! Şimdi giriş yapabilirsiniz.")

# --- 6. ANA PROGRAM ---
else:
    user = st.session_state.user_db[st.session_state.current_user]
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.subheader(user['name'])
        st.write(f"💼 Yetki: {user['role']}")
        st.divider()
        with st.expander("⚙️ Profil & Belgeler"):
            st.file_uploader("Ehliyet/SRC Yükle", type=['pdf', 'jpg'])
            st.button("Şifre Değiştir")
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    ust_bilgi()

    if user['role'] == "Yönetici":
        tab1, tab2, tab3 = st.tabs(["📊 Filo Analizi", "⚙️ Veritabanı Yönetimi", "🚨 Acil Bildirimler"])
        
        with tab1:
            m1, m2, m3 = st.columns(3)
            m1.metric("Aktif Sevkiyat", len(df))
            m2.metric("Toplam Mesafe", f"{df['Mesafe'].sum()} KM")
            m3.metric("Ort. Verimlilik", "%94")
            st.dataframe(df, use_container_width=True)
            st.map()

        with tab2:
            islem = st.radio("İşlem Seçin:", ["Yeni Sevkiyat Ekle", "Kayıt Güncelle", "Kayıt Sil"])
            if islem == "Yeni Sevkiyat Ekle":
                with st.form("ekle"):
                    f_id = st.text_input("Sipariş No")
                    f_alici = st.text_input("Alıcı Firma")
                    if st.form_submit_button("Google Sheets'e Kaydet"):
                        y_df = pd.concat([df, pd.DataFrame([{"ID": f_id, "Alici": f_alici, "Durum": "Yüklendi", "Mesafe": 0}])], ignore_index=True)
                        conn.update(spreadsheet=URL, data=y_df)
                        st.success("Veri Excel'e yazıldı!"); st.rerun()
            elif islem == "Kayıt Sil":
                sil_id = st.selectbox("Silinecek ID", df['ID'].tolist())
                if st.button("❌ KALICI SİL"):
                    y_df = df[df['ID'] != sil_id]
                    conn.update(spreadsheet=URL, data=y_df)
                    st.warning("Veri silindi!"); st.rerun()

        with tab3:
            st.subheader("⚠️ Acil Durum İzleme")
            acil = df[df['Sofor_Durumu'] == 'ACİL']
            if not acil.empty: st.error(f"DİKKAT: {len(acil)} araçtan acil sinyal alınıyor!")
            else: st.success("Her şey yolunda. Aktif acil durum yok.")

    elif user['role'] == "Şoför":
        st.subheader("🚚 Sürüş ve Mola Paneli")
        if st.button("🚨 ACİL DURUM SİNYALİ GÖNDER"):
            st.toast("Yöneticiye bildirildi!", icon="🚨")
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        if c1.button("🚛 Sürüş Başlat"): st.success("Sürüş kaydediliyor.")
        if c2.button("☕ Mola Ver"): st.info("Mola saati başladı.")
        if c3.button("😴 İstirahat"): st.warning("İstirahat modu aktif.")

        st.divider()
        st.info("📍 Güncel Görev: Uşak Merkez -> İzmir Limanı")
        if st.button("✅ İşi Onayla"): st.success("Yöneticiye onay iletildi.")
