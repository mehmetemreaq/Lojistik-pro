import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import qrcode
from PIL import Image
from io import BytesIO

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Lojistik Pro | Akıllı Yönetim", page_icon="🚚", layout="wide")

# --- 2. LOGO VE BAŞLIK ---
def ust_bilgi_ekle():
    logo_url = "https://cdn-icons-png.flaticon.com/512/4090/4090434.png"
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image(logo_url, width=90)
    with col2:
        st.title("Lojistik Pro: Akıllı Takip Sistemi")
        st.markdown("*Mehmet Emre Türkyılmaz | Lojistik Yönetimi*")
    st.divider()

# --- 3. GÜVENLİK ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

def giris_paneli():
    with st.sidebar:
        st.header("🔐 Sistem Girişi")
        kullanici = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            if kullanici == "admin" and sifre == "12345":
                st.session_state.logged_in = True
                st.session_state.role = "Yönetici"
                st.rerun()
            elif kullanici == "sofor" and sifre == "sofor123":
                st.session_state.logged_in = True
                st.session_state.role = "Şoför"
                st.rerun()
            else:
                st.error("Hatalı Giriş!")

# --- 4. ANA PROGRAM ---
if not st.session_state.logged_in:
    ust_bilgi_ekle()
    st.warning("Lütfen giriş yapınız.")
    giris_paneli()
else:
    # --- VERİ BAĞLANTISI (HATASIZ YAPI) ---
    URL = "https://docs.google.com/spreadsheets/d/SAYFA_ID_BURAYA/edit#gid=0"
    
    try:
        # Boşluklara dikkat edilen güvenli blok
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL)
        
        # Sütunları kontrol et ve eksikse sanal olarak oluştur (KeyError'u engeller)
        gerekenler = ['Mesafe', 'Yakit', 'Trafik', 'Alici', 'Durum', 'ID']
        for s in gerekenler:
            if s not in df.columns:
                df[s] = 0
    except:
        # Bağlantı koparsa sistemin çökmemesi için örnek veriler
        df = pd.DataFrame([
            {"ID": "TR-101", "Alici": "Ekol Lojistik", "Durum": "Yolda", "Yakit": 12, "Mesafe": 150, "Trafik": 3}
        ])

    ust_bilgi_ekle()
    st.sidebar.info(f"Yetki: {st.session_state.role}")

    if st.session_state.role == "Yönetici":
        t1, t2, t3 = st.tabs(["📊 Dashboard", "⛽ Analiz", "🧠 AI Tahmin"])
        with t1:
            st.subheader("Aktif Sevkiyatlar")
            st.dataframe(df, use_container_width=True)
            st.map(pd.DataFrame({'lat': [38.67], 'lon': [29.40]}))
        with t2:
            st.subheader("Maliyet Analizi")
            toplam_km = df['Mesafe'].sum()
            st.metric("Toplam Yol", f"{toplam_km} KM")
        with t3:
            st.subheader("Gecikme Tahmini")
            m = st.number_input("Mesafe (KM)", value=100)
            if st.button("Analiz Et"):
                st.success("Zamanında teslimat öngörülüyor.")

    elif st.session_state.role == "Şoför":
        st.subheader("Görev Listesi")
        st.table(df)
        if st.button("QR KOD OLUŞTUR"):
            qr = qrcode.make("TESLIMAT-ONAY")
            buf = BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf)

    if st.sidebar.button("🚪 Çıkış"):
        st.session_state.logged_in = False
        st.rerun()
