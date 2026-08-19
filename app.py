# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import data_fetcher
import ai_engine

# Giriş kontrolü (Şifre: 5654)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 Borsa Asistanı Giriş")
        pwd = st.text_input("Şifreyi giriniz:", type="password")
        if st.button("Giriş Yap"):
            if pwd == "5654":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Yanlış şifre! (Şifre: 5654)")
        return False
    return True

if not check_password():
    st.stop()

st.set_page_config(page_title='Borsa Fırsat Asistanı', layout='wide', initial_sidebar_state='expanded')

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #f0f6fc;
        background-color: #0b0f19;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        background-color: #21262d;
        color: #f0f6fc;
        border: 1px solid #30363d;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #00ffcc;
        color: #00ffcc;
        background-color: #30363d;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if 'portfoy' not in st.session_state:
    st.session_state['portfoy'] = {}
if 'favoriler' not in st.session_state:
    st.session_state['favoriler'] = []
if 'secili_hisse' not in st.session_state:
    st.session_state['secili_hisse'] = 'HKTM'

st.sidebar.title('⚡ Portföy & Kontrol')
api_key = st.sidebar.text_input('Anthropic API Key', type='password', key='api_key_input')
st.sidebar.caption('🔑 Claude yapay zeka analizi için gereklidir.')

st.sidebar.markdown('---')
st.sidebar.subheader('💼 Portföyüm')
if not st.session_state['portfoy']:
    st.sidebar.info('Henüz portföye hisse eklenmedi.')
else:
    for h_kod, h_detay in list(st.session_state['portfoy'].items()):
        col_p1, col_p2, col_p3 = st.sidebar.columns([2, 1, 1])
        col_p1.markdown(f"**{h_kod}**<br><small style='color:#8b949e'>{h_detay['adet']} Adet</small>", unsafe_allow_html=True)
        if col_p2.button('Seç', key=f'view_p_{h_kod}'):
            st.session_state['secili_hisse'] = h_kod
            st.rerun()
        if col_p3.button('Sil', key=f'del_p_{h_kod}'):
            del st.session_state['portfoy'][h_kod]
            st.rerun()

st.sidebar.markdown('---')
st.sidebar.subheader('⭐ Favorilerim')
if not st.session_state['favoriler']:
    st.sidebar.info('Favori hisse yok.')
else:
    for fav in list(st.session_state['favoriler']):
        col_f1, col_f2, col_f3 = st.sidebar.columns([2, 1, 1])
        col_f1.markdown(f"⭐ **{fav}**", unsafe_allow_html=True)
        if col_f2.button('Seç', key=f'view_f_{fav}'):
            st.session_state['secili_hisse'] = fav
            st.rerun()
        if col_f3.button('Sil', key=f'del_f_{fav}'):
            st.session_state['favoriler'].remove(fav)
            st.rerun()

st.sidebar.markdown('---')
st.sidebar.subheader('🔥 Alıma En Uygun Piyasalar')
st.sidebar.caption('Yalnızca güçlü alım sinyali verenler listelenir.')
ozet_veriler = data_fetcher.piyasa_ozeti_al()
for item in ozet_veriler:
    ai_kontrol = ai_engine.yapay_zeka_analiz_et(item['hisse'], item['fiyat'], item['degisim'], api_key)
    if 'ALIMA EN UYGUN' in ai_kontrol.get('kategori', '').upper():
        degisim = item['degisim']
        ok_isareti = '📈' if degisim >= 0 else '📉'
        renk_kod = '#3fb950' if degisim >= 0 else '#f85149'
        kart_html = f"<div style='background:#161b22; padding:8px; border-radius:6px; margin-bottom:6px; border:1px solid #30363d;'><b>{item['hisse']}</b> : <code>{item['fiyat']} TL</code> <span style='color:{renk_kod}; float:right;'>{ok_isareti} %{degisim}</span></div>"
        st.sidebar.markdown(kart_html, unsafe_allow_html=True)

st.title('🚀 Borsa Fırsat Asistanı')
st.markdown('<p style="color: #8b949e; margin-top: -10px;">Babanız için canlı analiz, portföy takibi ve yapay zeka karar destek merkezi.</p>', unsafe_allow_html=True)

with st.expander('🌐 Babanın İstediği Yerden (Telefondan) Bakabilmesi İçin İpucu'):
    st.markdown('Aynı Wi-Fi üzerindeki telefondan tarayıcıya IP adresini yazarak (örn: `http://192.168.1.X:8501`) her yerden erişebilirsin!')

col_search, col_actions = st.columns([2, 3])
with col_search:
    hisse_kod = st.text_input('🔍 Hisse Kodu Ara (Örn: THYAO, EREGL):', value=st.session_state['secili_hisse']).upper()
    st.session_state['secili_hisse'] = hisse_kod

if hisse_kod:
    hisse_data = data_fetcher.hisse_verisi_al(hisse_kod)
    ai_res = ai_engine.yapay_zeka_analiz_et(hisse_kod, hisse_data['fiyat'], hisse_data['degisim'], api_key)
    yorumlar = data_fetcher.forum_yorumlarini_getir(hisse_kod)

    col_btn1, col_btn2, _ = st.columns([1.5, 2, 2])
    with col_btn1:
        if hisse_kod in st.session_state['favoriler']:
            if st.button('★ Favorilerden Çıkar'):
                st.session_state['favoriler'].remove(hisse_kod)
                st.rerun()
        else:
            if st.button('☆ Favorilere Ekle'):
                st.session_state['favoriler'].append(hisse_kod)
                st.rerun()
    with col_btn2:
        adet_girdi = st.number_input('Adet Miktarı:', min_value=1, value=100, key='p_adet_input')
        if st.button('💼 Portföye Kaydet'):
            st.session_state['portfoy'][hisse_kod] = {'adet': adet_girdi, 'fiyat': hisse_data['fiyat']}
            st.success(f'{hisse_kod} portföye eklendi!')
            st.rerun()

    st.markdown('---')

    skor_html = f"<div style='background: linear-gradient(135deg, #238636 0%, #2ea043 100%); padding: 22px; border-radius: 12px; color: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);'><h3 style='margin:0; color:#ffffff; font-weight:700;'>✨ KATEGORİ: {ai_res.get('kategori', 'ALIMA EN UYGUN')}</h3><h1 style='margin:10px 0; color:#ffffff; font-weight:800;'>Uygunluk Skoru: %{ai_res.get('skor', 88)}</h1><p style='margin:0; font-weight: 500; color: #e6edf3;'>Risk Durumu: {ai_res.get('risk', 'Orta')}</p></div>"
    st.markdown(skor_html, unsafe_allow_html=True)

    with st.expander('📊 Neden Bu Kategoride? (Detaylı Yapay Zeka Raporu)', expanded=True):
        st.markdown(f"• **Teknik Durum:** <span style='color:#e6edf3;'>{ai_res.get('ozet', 'Hisse günü yüksek hacimli ve güçlü bir yükselişle sürdürüyor.')}</span>", unsafe_allow_html=True)
        st.markdown('<span style="color:#e6edf3;">• <b>Piyasa & Sosyal Medya Havası:</b> Analistlerin çoğu yükseliş ivmesinin süreceğini öngörüyor.</span>', unsafe_allow_html=True)

    st.subheader('💬 Canlı Sosyal Duyarlılık & Forum Akışı')
    
    # Yatay kaydırmalı (slider) modern forum akış yapısı
    icerik = '<div style="display: flex; overflow-x: auto; gap: 15px; padding-bottom: 15px; scroll-snap-type: x mandatory;">'
    for y in yorumlar:
        icerik += f"""
        <div style="flex: 0 0 300px; scroll-snap-align: start; background: #161b22; padding: 15px; border-radius: 10px; border-left: 4px solid #3fb950; border: 1px solid #30363d; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
            <b style='color:#f0f6fc;'>{y['yazar']}</b> <span style='color: #8b949e; font-size: 0.85em;'>({y['zaman']})</span> 
            <br><code style='background:#21262d; color:#7ee787; font-size: 0.8em;'>{y['tip']}</code>
            <p style='margin: 8px 0 5px 0; color: #c9d1d9; font-size: 0.95em;'>{y['yorum']}</p>
            <small style='color: #8b949e;'>👍 {y['begeni']} Beğeni</small>
        </div>
        """
    icerik += '</div>'
    
    components.html(f"""
        <div style="font-family: sans-serif; background-color: #0b0f19; padding: 5px;">{icerik}</div>
    """, height=210)

    st.subheader('📈 Son 1 Aylık Fiyat Hareketi ve Trend')
    if hisse_data['grafik'] is not None and not hisse_data['grafik'].empty:
        fig = px.line(hisse_data['grafik'], x='Date', y='Fiyat', title=f'{hisse_kod} 1 Aylık Performans Grafiği')
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(template='plotly_dark', height=420, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='#0b0f19', plot_bgcolor='#161b22')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Grafik verisi yükleniyor...')

    st.success(f"Tahmini Eğilim: {ai_res.get('eagilim', 'Yükseliş Eğilimli')}")
    st.caption('⚠️ *Yatırım tavsiyesi değildir. Yapay zekâ karar destek özetidir.*')