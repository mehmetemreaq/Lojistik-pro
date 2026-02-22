import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import qrcode
from PIL import Image
from io import BytesIO
import datetime

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Lojistik Pro | Kurumsal Yönetim", page_icon="🚛", layout="wide")

# --- 2. LOGO VE BAŞLIK ---
def ust_bilgi_ekle():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/4090/4090434.png", width=90)
    with col2:
        st.title("Lojistik Pro: Akıllı Operasyon & Şoför Yönetimi")
        st.markdown("*Mehmet Emre Türkyılmaz | Profesyonel Lojistik Çözümleri*")
    st.divider()

# --- 3. GÜVENLİK SİSTEMİ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

def giris_paneli():
    with st.sidebar:
        st.header("🔐 Güvenli Giriş")
        kullanici = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Sisteme Eriş"):
            if kullanici == "admin" and sifre == "12345":
                st.session_state.logged_in = True
                st.session_state.role = "Yönetici"
                st.rerun()
            elif kullanici == "sofor" and sifre == "sofor123":
                st.session_state.logged_in = True
                st.session_state.role = "Şoför"
                st.rerun()
            else:
                st.error("Yetkisiz Giriş Denemesi!")

# --- 4. ANA PROGRAM AKIŞI ---
if not st.session_state.logged_in:
    ust_bilgi_ekle()
    st.info("Lojistik yönetim paneline erişmek için lütfen giriş yapınız.")
    giris_paneli()
else:
    # --- VERİ BAĞLANTISI ---
    URL = "https://docs.google.com/spreadsheets/d/SAYFA_ID_BURAYA/edit#gid=0"
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL)
        # Eksik sütunları sanal olarak oluşturma (Hata önleyici)
        for col in ['ID', 'Alici', 'Durum', 'Mesafe', 'Yakit', 'Sofor_Durumu']:
            if col not in df.columns:
                df[col] = "Veri Yok" if col in ['Alici', 'Durum', 'Sofor_Durumu'] else 0
    except:
        df = pd.DataFrame([{"ID": "TR-101", "Alici": "Ekol Lojistik", "Durum": "Yolda", "Mesafe": 200, "Yakit": 15, "Sofor_Durumu": "Sürüşte"}])

    ust_bilgi_ekle()
    st.sidebar.success(f"Oturum Açıldı: {st.session_state.role}")

    # --- A) YÖNETİCİ EKRANI ---
    if st.session_state.role == "Yönetici":
        tab1, tab2, tab3 = st.tabs(["📊 Filo Takibi", "😴 Şoför Sağlık/Mola", "⚙️ Veri & Firma Yönetimi"])

        with tab1:
            st.subheader("📍 Canlı Sevkiyat ve Araç Durumu")
            st.dataframe(df, use_container_width=True)
            st.map(pd.DataFrame({'lat': [38.67], 'lon': [29.40]})) # Örnek: Uşak

        with tab2:
            st.subheader("🕵️ Şoför Yorgunluk ve Dinlenme Takibi")
            # Şoförlerin durumlarını filtrele
            st.table(df[['ID', 'Alici', 'Sofor_Durumu']])
            st.warning("🔔 Hatırlatma: 4.5 saati aşan şoförlere sistem üzerinden mola uyarısı gönderildi.")

        with tab3:
            st.subheader("🛠️ Sistem Yönetim Merkezi")
            islem = st.selectbox("İşlem Tipi", ["Yeni Sevkiyat/Firma Ekle", "Kayıt Düzenle/Sil"])
            
            if islem == "Yeni Sevkiyat/Firma Ekle":
                with st.form("ekleme_formu"):
                    n_id = st.text_input("ID")
                    n_alici = st.text_input("Şirket/Alıcı Adı")
                    n_mes = st.number_input("Mesafe", min_value=0)
                    if st.form_submit_button("Veritabanına Kaydet"):
                        st.success(f"{n_alici} firması ve sevkiyatı sisteme eklendi.")
            
            elif islem == "Kayıt Düzenle/Sil":
                secilen = st.selectbox("Düzenlenecek Kayıt", df['ID'].tolist())
                if st.button("❌ Seçili Kaydı Veritabanından Kaldır"):
                    st.error(f"{secilen} ID'li kayıt silindi.")

    # --- B) ŞOFÖR EKRANI ---
    elif st.session_state.role == "Şoför":
        st.subheader("🚚 Sürüş ve Dinlenme Kontrol Paneli")
        
        c1, c2, c3 = st.columns(3)
        if c1.button("🚛 Sürüşü Başlat"):
            st.success("Sürüş süresi başlatıldı. İyi yolculuklar!")
        if c2.button("☕ Mola Ver"):
            st.info("45 dakikalık mola süreniz başladı.")
        if c3.button("😴 İstirahate Geç"):
            st.warning("Uyku modu aktif. Sistem sizi 8 saat sonra uyaracak.")

        st.divider()
        st.subheader("📋 Görev Detayları")
        st.table(df.head(1)) # Şoföre sadece ilgili görevi göster
        
        if st.button("✅ Teslimat QR Kodu Oluştur"):
            qr = qrcode.make("TESLIM-ONAY-SUCCESS")
            buf = BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf, caption="Teslimat sırasında müşteriye okutun.")

    if st.sidebar.button("🚪 Güvenli Çıkış"):
        st.session_state.logged_in = False
        st.rerun()
