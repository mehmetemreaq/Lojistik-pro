import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import qrcode
from PIL import Image
from io import BytesIO

# --- 1. KURUMSAL TEMA VE CSS ---
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
    div[data-testid="stMetricValue"] { color: #002b5b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KULLANICI VERİTABANI VE OTURUM ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "admin": {"pw": "12345", "name": "Mehmet Emre Türkyılmaz", "role": "Yönetici"},
        "sofor": {"pw": "sofor123", "name": "Ahmet Şoför", "role": "Şoför"}
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# --- 3. GOOGLE SHEETS BAĞLANTISI (HATA KORUMALI) ---
URL = "https://docs.google.com/spreadsheets/d/SAYFA_ID_BURAYA/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=URL)
    # Hata önleyici sütun kontrolü
    for col in ['ID', 'Alici', 'Durum', 'Mesafe', 'Yakit', 'Sofor_Durumu']:
        if col not in df.columns:
            df[col] = "Belirtilmedi" if col in ['Alici', 'Durum', 'Sofor_Durumu'] else 0
except Exception as e:
    df = pd.DataFrame([{"ID": "TR-101", "Alici": "Ekol Lojistik", "Durum": "Yolda", "Mesafe": 150, "Yakit": 12, "Sofor_Durumu": "Sürüşte"}])

# --- 4. GİRİŞ VE KAYIT SİSTEMİ ---
def draw_header():
    col1, col2 = st.columns([1, 6])
    with col1: st.image("https://cdn-icons-png.flaticon.com/512/4090/4090434.png", width=90)
    with col2: 
        st.title("Lojistik Pro | Kurumsal Operasyon Portalı")
        st.caption("Uşak Lojistik Yönetimi - Profesyonel Takip Sistemi")
    st.divider()

if not st.session_state.logged_in:
    draw_header()
    t_login, t_signup = st.tabs(["🔐 Giriş Yap", "📝 Şoför Kaydı"])
    with t_login:
        u = st.text_input("Kullanıcı Adı")
        p = st.text_input("Şifre", type="password")
        if st.button("Sisteme Eriş"):
            if u in st.session_state.user_db and st.session_state.user_db[u]["pw"] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Hatalı Giriş!")
    with t_signup:
        nu = st.text_input("Yeni Kullanıcı Adı")
        np = st.text_input("Yeni Şifre", type="password")
        nn = st.text_input("Ad Soyad")
        if st.button("Şoför Olarak Kaydol"):
            st.session_state.user_db[nu] = {"pw": np, "name": nn, "role": "Şoför"}
            st.success("Kayıt başarılı! Giriş yapabilirsiniz.")

# --- 5. ANA PANEL ---
else:
    user = st.session_state.user_db[st.session_state.current_user]
    
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.write(f"💼 Yetki: {user['role']}")
        st.divider()
        with st.expander("⚙️ Profil & Belgeler"):
            st.file_uploader("Ehliyet/SRC Yükle", type=['pdf', 'jpg'])
            st.button("Şifre Değiştir")
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    draw_header()

    # --- A) YÖNETİCİ PANELİ ---
    if user['role'] == "Yönetici":
        tab1, tab2, tab3 = st.tabs(["📊 Filo Analizi", "⚙️ Kayıt Yönetimi", "🚨 Acil Durumlar"])
        
        with tab1:
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Araç", len(df))
            m2.metric("Toplam Yol", f"{df['Mesafe'].sum()} KM")
            m3.metric("Ort. Yakıt", f"{df['Yakit'].mean():.1f} L")
            st.dataframe(df, use_container_width=True)
            st.map()

        with tab2:
            islem = st.radio("İşlem Seçin:", ["Yeni Kayıt Ekle", "Kayıt Güncelle", "Kayıt Sil"])
            if islem == "Yeni Kayıt Ekle":
                with st.form("ekle"):
                    f_id = st.text_input("Sipariş ID")
                    f_alici = st.text_input("Alıcı Firma")
                    if st.form_submit_button("Excel'e Kaydet"):
                        yeni_df = pd.concat([df, pd.DataFrame([{"ID": f_id, "Alici": f_alici, "Durum": "Yüklendi", "Mesafe": 0}])], ignore_index=True)
                        conn.update(spreadsheet=URL, data=yeni_df)
                        st.success("Eklendi!")
                        st.rerun()
            elif islem == "Kayıt Sil":
                sil_id = st.selectbox("Silinecek ID", df['ID'].tolist())
                if st.button("❌ KALICI OLARAK SİL"):
                    yeni_df = df[df['ID'] != sil_id]
                    conn.update(spreadsheet=URL, data=yeni_df)
                    st.warning("Silindi!")
                    st.rerun()

        with tab3:
            st.subheader("🛡️ Acil Durum Denetimi")
            acil_vaka = df[df['Sofor_Durumu'] == 'ACİL']
            if not acil_vaka.empty: st.error(f"DİKKAT: {len(acil_vaka)} adet acil bildirim var!")
            else: st.success("Şu an aktif bir acil durum bildirimi bulunmamaktadır.")

    # --- B) ŞOFÖR PANELİ ---
    elif user['role'] == "Şoför":
        st.subheader("🚚 Sürüş Yönetim Paneli")
        st.error("🆘 ACİL DURUM: Kaza/Arıza anında butona basın!")
        if st.button("MERKEZE SİNYAL GÖNDER"): 
            st.toast("Sinyal İletildi!", icon="🚨")
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        if c1.button("🚛 Sürüş Başlat"): st.success("Sürüş başladı.")
        if c2.button("☕ Mola Ver"): st.info("Mola kaydedildi.")
        if c3.button("😴 İstirahat"): st.warning("Uyku modu aktif.")

        st.divider()
        st.subheader("📩 Gelen Görevler")
        st.info("📌 Görev: Uşak Merkez -> Uşak OSB")
        if st.button("✅ İşi Kabul Et"): st.success("Görev onaylandı.")
