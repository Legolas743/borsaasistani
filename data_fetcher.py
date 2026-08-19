# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import feedparser

def hisse_verisi_al(hisse_kodu):
    # (Önceki fonksiyonun aynı kalabilir, değişmedi)
    kod_clean = str(hisse_kodu).strip().upper()
    ticker_kod = kod_clean if kod_clean.endswith('.IS') else kod_clean + '.IS'
    ticker = yf.Ticker(ticker_kod)
    df = ticker.history(period='1mo', interval='1d')
    if df.empty:
        return {'hisse': kod_clean, 'fiyat': 0.0, 'degisim': 0.0, 'grafik': None}
    guncel_fiyat = round(float(df['Close'].iloc[-1]), 2)
    onceki_fiyat = float(df['Close'].iloc[-2]) if len(df) > 1 else guncel_fiyat
    gunluk_degisim = round(((guncel_fiyat - onceki_fiyat) / onceki_fiyat) * 100, 2)
    return {'hisse': kod_clean, 'fiyat': guncel_fiyat, 'degisim': gunluk_degisim}

def forum_yorumlarini_getir(hisse_kodu):
    """Google News üzerinden gerçek zamanlı finansal akışı çeker."""
    hisse_kodu = str(hisse_kodu).upper()
    # Google News RSS ile hisse hakkında güncel haber/sosyal başlıkları çekiyoruz
    url = f"https://news.google.com/rss/search?q={hisse_kodu}+hisse+BIST&hl=tr&gl=TR&ceid=TR:tr"
    feed = feedparser.parse(url)
    
    yorumlar = []
    for entry in feed.entries[:3]: # En güncel 3 başlığı al
        yorumlar.append({
            'yazar': entry.source.title if 'source' in entry else 'Piyasa Haber',
            'zaman': 'Güncel',
            'yorum': entry.title,
            'tip': 'HABER',
            'begeni': 'Gerçek Zamanlı'
        })
    
    # Eğer sonuç gelmezse boş döndürmek yerine bir adet sistem bilgisi bırakıyoruz
    if not yorumlar:
        return [{'yazar': 'Sistem', 'zaman': 'Şu an', 'yorum': f'{hisse_kodu} için anlık veri akışı güncelleniyor...', 'tip': 'BİLGİ', 'begeni': 0}]
    
    return yorumlar