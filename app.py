import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import qrcode
from PIL import Image
from io import BytesIO

# --- 1. SAYFA YAPILANDIRMASI VE TEMA ---
st.set_page_config(
    page_title="Lojistik Pro | Akıllı Yönetim Sistemi",
    page_icon="🚚",
    layout="wide"
)

# --- 2. LOGO VE BAŞLIK FONKSİYONU ---
def ust_bilgi_ekle():
    col1, col2 = st.columns([1, 6])
    with col1:
        # Profesyonel Lojistik Logosu
        st.image("https://cdn-icons-png.flaticon.com/512/4090/4090434.png", width=90)
    with col2:
        st.title("Lojistik Pro: Uçtan Uca Takip Sistemi")
        st.markdown("*Mehmet Emre Türkyılmaz - Akıllı Lojistik Çözümleri*")
    st.divider()

# --- 3. GÜVENLİK VE OTURUM YÖNETİMİ ---
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
                st.error("Hatalı kullanıcı adı veya şifre!")

# --- 4. ANA PROGRAM AKIŞI ---
if not st.session_state.logged_in:
    ust_bilgi_ekle()
    st.warning("Lütfen devam etmek için sol taraftaki panelden giriş yapınız.")
    giris_paneli()
else:
    # --- GOOGLE SHEETS VERİ BAĞLANTISI ---
    # NOT: Kendi Google Sheets URL'nizi buraya yapıştırın
    URL = "https://docs.google.com/spreadsheets/d/17yIQDnXsoavEpYQuusPf_n-Vu5jVZycjCwk2N_qvPiE/edit?usp=sharing"
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL)
    except:
        # Veritabanı bağlı değilse gösterilecek taslak veriler
        df = pd.DataFrame([
            {"ID": "TR-101", "Alici": "Ekol Lojistik", "Durum": "Yolda", "Yakit": 12.5, "Mesafe": 150, "Trafik": 3, "Hava": "Güneşli"},
            {"ID": "TR-102", "Alici": "Libex Denizli", "Durum": "Yüklendi", "Yakit": 14.2, "Mesafe": 220, "Trafik": 4, "Hava": "Yağmurlu"}
        ])

    ust_bilgi_ekle()
    st.sidebar.success(f"Yetki: {st.session_state.role}")

    # --- ROL BAZLI EKRANLAR ---
    
    # A) YÖNETİCİ PANELİ
    if st.session_state.role == "Yönetici":
        tab1, tab2, tab3 = st.tabs(["📊 Operasyon Merkezi", "⛽ Maliyet & Verim", "🧠 AI Gecikme Tahmini"])
        
        with tab1:
            st.subheader("📍 Canlı Araç Takibi")
            # Uşak ve çevresi için örnek harita noktaları
            map_df = pd.DataFrame({'lat': [38.67, 38.61], 'lon': [29.40, 27.42]})
            st.map(map_df)
            st.subheader("📦 Aktif Sevkiyat Listesi")
            st.dataframe(df, use_container_width=True)

        with tab2:
            st.subheader("💰 Yakıt ve Performans Analizi")
            c1, c2, c3 = st.columns(3)
            toplam_km = df['Mesafe'].sum() if 'Mesafe' in df.columns else 0
            ort_yakit = df['Yakit'].mean()
            
            c1.metric("Toplam Mesafe", f"{toplam_km} KM")
            c2.metric("Ort. Yakıt (100km)", f"{ort_yakit:.2f} L")
            c3.metric("Tahmini Yakıt Gideri", f"{toplam_km * (ort_yakit/100) * 45:.2f} TL")
            
            st.bar_chart(df.set_index("ID")["Yakit"])

        with tab3:
            st.subheader("🤖 Yapay Zeka ile Teslimat Riski")
            col_ai1, col_ai2 = st.columns(2)
            mesafe_ai = col_ai1.slider("Mesafe Seçin (KM)", 50, 1000, 250)
            trafik_ai = col_ai2.slider("Trafik Yoğunluğu (1-5)", 1, 5, 2)
            hava_ai = st.selectbox("Hava Durumu", ["Güneşli", "Yağmurlu", "Karlı/Fırtınalı"])
            
            if st.button("Risk Analizi Yap"):
                hava_skor = {"Güneşli": 1, "Yağmurlu": 1.5, "Karlı/Fırtınalı": 2.5}[hava_ai]
                risk_skoru = (mesafe_ai * 0.05) + (trafik_ai * 15) * hava_skor
                
                if risk_skoru > 60:
                    st.error(f"Kritik Gecikme Riski! (Skor: {risk_skoru:.0f})")
                else:
                    st.success(f"Zamanında Teslimat Bekleniyor. (Skor: {risk_skoru:.0f})")

    # B) ŞOFÖR PANELİ
    elif st.session_state.role == "Şoför":
        st.subheader("🚛 Günlük Görev Listesi")
        st.info("Sadece size atanan görevler aşağıda listelenmiştir.")
        st.table(df[df['ID'] == "TR-101"])
        
        c_sh1, c_sh2 = st.columns(2)
        with c_sh1:
            if st.button("🚩 Yola Çıktım (GPS Başlat)"):
                st.warning("Merkeze canlı konum verisi gönderiliyor...")
        
        with c_sh2:
            if st.button("🏁 Teslimatı Onayla (QR Oluştur)"):
                qr_gen = qrcode.make(f"ONAY-{df.iloc[0]['ID']}-BAŞARILI")
                img_buf = BytesIO()
                qr_gen.save(img_buf, format="PNG")
                st.image(img_buf, caption="Müşteriye bu kodu okutun.")
                st.success("Teslimat onayı bekliyor...")

    # Çıkış Yapma
    st.sidebar.divider()
    if st.sidebar.button("🚪 Güvenli Çıkış"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

# --- 5. GEREKLİ KÜTÜPHANELER (NOT) ---
# requirements.txt dosyasına şunları yazın:
# streamlit
# pandas
# streamlit-gsheets-connection
# qrcode
# Pillow

