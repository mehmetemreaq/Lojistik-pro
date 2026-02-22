import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import qrcode
from PIL import Image
from io import BytesIO
import datetime

# --- 1. KURUMSAL TEMA VE SAYFA AYARLARI ---
st.set_page_config(page_title="Lojistik Pro Enterprise", page_icon="🏢", layout="wide")

# Kurumsal Stil Tanımlamaları (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #002b5b; color: white; transition: 0.3s; }
    .stButton>button:hover { background-color: #004085; border-color: #004085; }
    .stAlert { border-radius: 10px; }
    div[data-testid="stMetricValue"] { color: #002b5b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KULLANICI VE OTURUM YÖNETİMİ ---
if 'user_db' not in st.session_state:
    # Başlangıç kullanıcıları
    st.session_state.user_db = {
        "admin": {"pw": "12345", "name": "Mehmet Emre Türkyılmaz", "role": "Yönetici"},
        "sofor": {"pw": "sofor123", "name": "Ahmet Şoför", "role": "Şoför"}
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# --- 3. YARDIMCI FONKSİYONLAR ---
def draw_header():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/4090/4090434.png", width=100)
    with col2:
        st.title("Lojistik Pro | Kurumsal Operasyon Portalı")
        st.caption("Uşak Lojistik Yönetim ve Takip Sistemi")
    st.divider()

# --- 4. GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.logged_in:
    draw_header()
    tab_log, tab_reg = st.tabs(["🔐 Giriş Yap", "📝 Yeni Kayıt"])
    
    with tab_log:
        u = st.text_input("Kullanıcı Adı")
        p = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş"):
            if u in st.session_state.user_db and st.session_state.user_db[u]["pw"] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else:
                st.error("Hatalı kimlik bilgileri.")

    with tab_reg:
        st.subheader("🚚 Yeni Şoför Kaydı")
        st.info("Bu panel sadece şoför personeli içindir. Yönetici yetkileri sistem yöneticisi tarafından atanır.")
        
        nu = st.text_input("Yeni Kullanıcı Adı")
        np = st.text_input("Yeni Şifre", type="password")
        nn = st.text_input("Ad Soyad")
        
        # Seçim kutusu kaldırıldı, rol otomatik olarak 'Şoför' atandı
        if st.button("Şoför Kaydını Tamamla"):
            if nu and np:
                # Yeni kayıt otomatik olarak 'Şoför' rolüyle veritabanına eklenir
                st.session_state.user_db[nu] = {"pw": np, "name": nn, "role": "Şoför"}
                st.success(f"Sayın {nn}, kaydınız başarıyla oluşturuldu. Giriş yapabilirsiniz.")
            else:
                st.error("Lütfen tüm alanları doldurunuz.")
# --- 5. ANA PANEL ---
else:
    user = st.session_state.user_db[st.session_state.current_user]
    
    # Sidebar: Profil ve Acil Durum
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.write(f"🏷️ Rol: {user['role']}")
        st.divider()
        
        with st.expander("⚙️ Profil Ayarları"):
            new_name = st.text_input("İsim Güncelle", value=user['name'])
            new_pass = st.text_input("Yeni Şifre", type="password")
            if st.button("Kaydet"):
                st.session_state.user_db[st.session_state.current_user]['name'] = new_name
                if new_pass: st.session_state.user_db[st.session_state.current_user]['pw'] = new_pass
                st.success("Güncellendi!")
        
        with st.expander("📂 Özlük Dosyası (SRC/Ehliyet)"):
            st.file_uploader("Belge Yükle", type=['pdf', 'jpg'])
            st.date_input("Geçerlilik Tarihi")
            st.button("Belgeyi Gönder")
            
        if st.sidebar.button("🚪 Güvenli Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    draw_header()

    # --- GOOGLE SHEETS VERİ ÇEKME ---
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet="SAYFA_URL_BURAYA") # Kendi linkinizi buraya koyun
    except:
        # Hata durumunda örnek veriler
        df = pd.DataFrame([{"ID": "TR-101", "Alici": "Ekol Lojistik", "Durum": "Yolda", "Mesafe": 150, "Sofor_Durumu": "Sürüşte"}])

    # --- YÖNETİCİ PANELİ ---
    if user['role'] == "Yönetici":
        t1, t2, t3, t4 = st.tabs(["📊 Filo Takibi", "📨 İş Atama", "🛡️ Denetim", "🛠️ Yönetim"])
        
        with t1:
            st.subheader("📍 Canlı Operasyon Merkezi")
            m1, m2, m3 = st.columns(3)
            m1.metric("Aktif Araç", len(df))
            m2.metric("Mesafe Toplamı", f"{df['Mesafe'].sum()} KM")
            m3.metric("Filo Verimi", "%92")
            st.map()
            st.dataframe(df, use_container_width=True)

        with t2:
            st.subheader("📝 Yeni İş Emri Gönder")
            with st.form("is_emri"):
                st.selectbox("Şoför Seç", ["Ahmet Şoför", "Can Lojistik"])
                st.text_area("Yük Detayı")
                if st.form_submit_button("İş Emrini Yayınla"): st.success("Görev iletildi.")

        with t3:
            st.subheader("🚨 Acil Durum & Mesaj Merkezi")
            st.error("⚠️ Aktif Acil Durum Bildirimi Yok.")
            st.info("Mesajlar: Şoför Ahmet mola bitişini bildirdi.")

        with t4:
            st.subheader("⚙️ Veritabanı Yönetimi")
            secilen = st.selectbox("Kayıt Seç", df['ID'].tolist())
            if st.button("❌ Seçili Kaydı Sil"): st.warning("Kayıt silindi (Test Modu)")

    # --- ŞOFÖR PANELİ ---
    elif user['role'] == "Şoför":
        st.subheader("🚚 Sürüş Kontrol Paneli")
        
        # ACİL DURUM BUTONU (Kırmızı)
        st.error("🚨 ACİL DURUM: Kaza veya Arıza anında hemen basın!")
        if st.button("🆘 MERKEZE ACİL DURUM SİNYALİ GÖNDER"):
            st.toast("ACİL DURUM SİNYALİ İLETİLDİ!", icon="🚨")

        st.divider()
        c1, c2, c3 = st.columns(3)
        if c1.button("🚛 Sürüş Başlat"): st.success("Sürüş kaydediliyor.")
        if c2.button("☕ Mola"): st.info("Mola kaydedildi.")
        if c3.button("😴 Uyku"): st.warning("İstirahate geçildi.")

        st.divider()
        st.subheader("📩 Gelen Görevler")
        st.info("📍 Mevcut Görev: Uşak OSB -> İzmir Limanı")
        if st.button("✅ İşi Onayla"): st.success("İş kabul edildi.")

