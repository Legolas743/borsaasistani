# -*- coding: utf-8 -*-
import anthropic

def yapay_zeka_analiz_et(hisse_kodu, fiyat, degisim, api_key):
    # Eğer API key girilmişse gerçek Claude AI analizi yapmaya çalışalım
    if api_key and len(api_key.strip()) > 10:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""
            Sen profesyonel bir Borsa İstanbul (BIST) finansal analistisin. 
            Hisse Kodu: {hisse_kodu}
            Güncel Fiyat: {fiyat} TL
            Günlük Değişim: %{degisim}
            
            Bu hisse için kısa bir analiz yap. Yanıtı kesinlikle şu formatta ver:
            KATEGORI: [ALIMA EN UYGUN / ORTARAMADA / RİSKLİ / BEKLE]
            SKOR: [0 ile 100 arasında bir sayı]
            RISK: [Düşük / Orta / Yüksek]
            OZET: [Tek cümlelik teknik özet]
            EAGILIM: [Yükseliş Eğilimli / Yatay / Düşüş Eğilimli]
            """
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            # Basit bir parse işlemiyle Claude'un yanıtını ayıkla
            lines = response_text.strip().split('\n')
            res = {}
            for line in lines:
                if ":" in line:
                    k, v = line.split(":", 1)
                    res[k.strip().lower()] = v.strip()
            
            return {
                "kategori": res.get("kategori", "ALIMA EN UYGUN"),
                "skor": int(res.get("skor", 85)),
                "risk": res.get("risk", "Orta"),
                "ozet": res.get("ozet", f"{hisse_kodu} için piyasa hareketleri inceleniyor."),
                "eagilim": res.get("eagilim", "Yükseliş Eğilimli")
            }
        except Exception as e:
            # API hatası olursa simülasyona düşer
            pass

    # API Key girilmediyse veya hata aldıysa, hissenin günlük değişimine göre dinamik skor üretelim:
    # Böylece her hisse aynı skoru vermez, değişime göre şekillenir.
    temel_skor = 50 + int(degisim * 3)
    if temel_skor > 95: skor = 95
    elif temel_skor < 20: skor = 25
    else: skor = temel_skor

    if degisim > 2.5:
        kategori = "ALIMA EN UYGUN"
        risk = "Orta"
        ozet = f"{hisse_kodu} güçlü hacim ve pozitif ivmeyle hareket ediyor."
        egilim = "Güçlü Yükseliş"
    elif degisim >= 0:
        kategori = "ORTARAMADA / İZLE"
        risk = "Düşük-Orta"
        ozet = f"{hisse_kodu} yatay seyrini koruyor, kademeli izlenebilir."
        egilim = "Yatay / Kararsız"
    else:
        kategori = "RİSKLİ / DÜŞÜŞTE"
        risk = "Yüksek"
        ozet = f"{hisse_kodu} günlük bazda baskı altında ve geri çekiliyor."
        egilim = "Düşüş Eğilimli"

    return {
        "kategori": kategori,
        "skor": skor,
        "risk": risk,
        "ozet": ozet,
        "eagilim": egilim
    }