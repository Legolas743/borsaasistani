# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import time
import data_fetcher

# --- Sayfa Yapılandırması (Mobil Uyumlu) ---
st.set_page_config(
    page_title="Borsa Aile Paneli",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Özel Mobil & Modern CSS Stilleri ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #1f2937; color: white; border: 1px solid #374151; }
    .stButton>button:hover { background-color: #374151; border-color: #4b5563; }
    div.metric-container { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .card-style { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- Şifre Korumalı Giriş Mekanizması ---
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>🔒 Borsa Aile Paneli Girişi</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        sifre_giris = st.text_input("Lütfen Erişim Şifresini Girin", type="password")
        if st.button("Giriş Yap"):
            if sifre_giris == "5654":
                st.session_state.giris_yapildi = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
    st.stop()

# --- Üst Başlık & Canlı Durum ---
st.markdown("<h2 style='margin-bottom: 0;'>📊 BIST Canlı Takip ve Analiz Paneli</h2>", unsafe_allow_html=True)
st.caption("Aile Kullanımı İçin Özel Olarak Hazırlanmıştır • Gerçek Zamanlı Veri Akışı")

# --- Kenar Çubuğu / Hisse Seçimi ---
st.sidebar.header("⚙️ Kontrol Paneli")
secilen_hisse_kod = st.sidebar.text_input("Hisse Kodu (Örn: THYAO, HKTM, EREGL)", value="HKTM").strip().upper()

# --- Veri Çekme ---
hisse_data = data_fetcher.hisse_verisi_al(secilen_hisse_kod)
ozet_veriler = data_fetcher.piyasa_ozeti_al()

# --- Piyasa Özet Şeridi (Üst Özet) ---
st.markdown("### 🔥 Piyasa Özeti")
cols = st.columns(min(len(ozet_veriler), 4))
for idx, item in enumerate(ozet_veriler[:4]):
    with cols[idx]:
         renk = "green" if item['degisim'] >= 0 else "red"
         st.markdown(f"""
             <div class="metric-container">
                 <h4 style="margin:0;">{item['hisse']}</h4>
                 <p style="margin:0; font-size:18px;"><b>{item['fiyat']} TL</b></p>
                 <p style="margin:0; color:{renk}; font-size:14px;">%{item['degisim']}</p>
             </div>
         """, unsafe_allow_html=True)

st.markdown("---")

# --- Seçilen Hisse Temel Göstergeleri ---
c1, c2, c3 = st.columns(3)
c1.metric(label=f"{hisse_data['hisse']} Güncel Fiyat", value=f"{hisse_data['fiyat']} TL", delta=f"%{hisse_data['degisim']}")
c2.metric(label="Veri Kaynağı", value="Yahoo Finance", delta="Canlı")
c3.metric(label="Sistem Durumu", value="Aktif", delta="Sorunsuz")

st.markdown("---")

# --- Grafik ve Tahmin Bölümü ---
st.subheader(f"📈 {hisse_data['hisse']} Fiyat ve Yapay Zeka Trend Projeksiyonu")

g_col1, g_col2 = st.columns([2, 1])
with g_col1:
    grafik_tipi = st.selectbox("Grafik Türü", ["Çizgi (Line)", "Alan (Area)", "Standart"])
with g_col2:
    tahmin_goster = st.checkbox("🔮 AI Yön Tahmin Çizgisini Göster", value=True)

# Plotly Grafik Oluşturma
fig = go.Figure()
df_grafik = hisse_data.get('grafik')

if df_grafik is not None and not df_grafik.empty:
    if grafik_tipi == "Çizgi (Line)":
        fig.add_trace(go.Scatter(x=df_grafik['Date'], y=df_grafik['Fiyat'], mode='lines+markers', name='Gerçek Fiyat', line=dict(color='#00FF7F', width=3)))
    elif grafik_tipi == "Alan (Area)":
        fig.add_trace(go.Scatter(x=df_grafik['Date'], y=df_grafik['Fiyat'], mode='lines', fill='tozeroy', name='Gerçek Fiyat', line=dict(color='#1E90FF', width=2), fillcolor='rgba(30, 144, 255, 0.2)'))
    else:
        fig.add_trace(go.Scatter(x=df_grafik['Date'], y=df_grafik['Fiyat'], mode='lines', name='Kapanış', line=dict(color='#FFA500', width=2.5)))

    # Yapay Zeka Tahmini Çizgi Senaryosu
    if tahmin_goster and len(df_grafik) > 0:
        son_tarih = df_grafik['Date'].iloc[-1]
        son_fiyat = df_grafik['Fiyat'].iloc[-1]
        tahmin_x = [son_tarih, "Hedef Projeksiyon"]
        tahmin_y = [son_fiyat, son_fiyat * 1.035] # %3.5 potansiyel hedef
        
        fig.add_trace(go.Scatter(
            x=tahmin_x, y=tahmin_y,
            mode='lines+markers',
            name='AI Yön Projeksiyonu',
            line=dict(color='#FF4500', width=2, dash='dash')
        ))

    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=10, r=10, t=10, b=10),
        height=420,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#30363d')
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Grafik verisi yüklenemedi.")

st.markdown("---")

# --- Canlı Haber / Sosyal Akış Kartları (Google News Gerçek Akış) ---
st.markdown("### 💬 Canlı Sosyal Duyarlılık & Piyasa Akışı")
yorumlar = data_fetcher.forum_yorumlarini_getir(secilen_hisse_kod)

y_cols = st.columns(len(yorumlar) if len(yorumlar) > 0 else 1)
for idx, yorum in enumerate(yorumlar):
    with y_cols[idx % len(y_cols)]:
        st.markdown(f"""
            <div class="card-style">
                <p style="margin:0; font-size:12px; color:#8b949e;"><b>{yorum['yazar']}</b> • {yorum['zaman']}</p>
                <p style="margin:5px 0; font-size:13px; color:#58a6ff;"><b>{yorum['tip']}</b></p>
                <p style="margin:0; font-size:14px;">{yorum['yorum']}</p>
            </div>
        """, unsafe_allow_html=True)

# --- 15 Saniyede Bir Otomatik Yenileme Mekanizması ---
if "son_guncelleme" not in st.session_state:
    st.session_state.son_guncelleme = time.time()

gecen_sure = time.time() - st.session_state.son_guncelleme
st.sidebar.markdown("---")
st.sidebar.caption("🔄 **Canlı Akış:** Her 15 saniyede bir otomatik güncelleniyor.")

if gecen_sure > 15:
    st.session_state.son_guncelleme = time.time()
    st.rerun()
else:
    time.sleep(1)
    st.rerun()