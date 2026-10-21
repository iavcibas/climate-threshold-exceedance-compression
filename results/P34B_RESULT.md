---
title: "P34b — Arşiv kodlayıcıları: kapı sonucu"
date: "5 Ekim 2026"
---

# Karar

Onay yılları 2021–2024, toplam 91 864 030 geçerli gün-hücre.

* **B1 GEÇTİ (44/44).** Paketleme, bit yuvarlama ve Lorenzo'da değişen gün sayısı ızgara yasasına uydu. Ölçülen/tahmin oranı 0,909–1,049.
* **B2 GEÇTİ (44/44).** Bu üç kodlayıcıda her değişim tek yönde. Yön de her hücrede tahmin edilen yön: aşağı, yani sıcak gün kaybı.
* **B3 KALDI.** Tamsayı olmayan tahminci (NIPRED) için iki koşul vardı:
  * değişim sayısı eklenti toplamına uymalıydı: 8/15 (kural en az 12/15);
  * net değişim küçük kalmalıydı: 12/15, bu koşul sağlandı.

  Kapı, ilk koşul yüzünden kaldı.

Pilot yılı (2020) aynı tabloyu verdi: 44/44, 44/44, 8/15 ve 12/15. Pilottaki tanı `P34B_PILOT_NOTE` dosyasında.

# Öne çıkan sayılar (aşımlara oranla net değişim)

| Kodlayıcı | Ayar | Azami hata (°C) | 30 °C | 35 °C | 40 °C |
|---|---|---|---|---|---|
| Paketleme | s = 0,01 | 0,005 | −%0,06 | −%0,12 | −%0,15 |
| Paketleme | s = 0,1 | 0,05 | −%0,64 | −%1,18 | −%1,45 |
| Paketleme | s = 0,5 | 0,25 | −%3,20 | −%5,76 | −%7,12 |
| Bit yuvarlama | 9 bit | 0,031 | −%0,20 | −%0,74 | −%0,91 |
| Bit yuvarlama | 7 bit | 0,125 | −%0,80 | −%2,92 | −%3,61 |
| Bit yuvarlama | 5 bit | 0,5 | −%3,20 | −%11,19 | −%13,89 |
| Lorenzo | ε = 0,1 | 0,1 | −%1,27 | −%2,35 | −%2,89 |
| Lorenzo | ε = 0,5 | 0,5 | −%6,48 | −%11,19 | −%13,89 |
| Lorenzo | ε = 1 | 1,0 | −%13,26 | 0 (eşik hücre sınırında) | −%26,45 |
| NIPRED | ε = 0,1 | 0,1 | −%0,01 | +%0,04 | −%0,02 |
| NIPRED | ε = 0,5 | 0,5 | 0,00 | +%2,52 | −%0,08 |
| NIPRED | ε = 1 | 1,0 | +%2,91 | **+%9,79** | −%0,99 |

# Sade dille

1. **Arşivlerin gerçekten kullandığı üç yöntem, yuvarlak eşiklerin üstündeki sıcak günleri sistematik olarak siliyor.** Paketleme, bit yuvarlama ve SZ'nin Lorenzo tahmincisi bu üçü.
   * Neden: 30, 35 ve 40 °C bu ızgaraların üzerinde birer nokta. Eşiğin hemen üstündeki yarım hücre eşiğin kendisine yuvarlanıyor; "eşikten büyük" sorusuna verilen yanıt da "hayır"a dönüyor.
   * Büyüklük, sıkıştırma hiç çalıştırılmadan $N p_0 h/2$ ile hesaplandı. 44 hücrenin hepsinde tutarlı çıktı.
   * Kayıp, ±0,25 °C'lik makul bir hata sınırında bile 40 °C üstü günlerin %7'si.
2. **Lorenzo'nun ızgara üzerinde kalması yalnızca bir kuram değil.** Lorenzo ile aynı adımdaki paketleme birebir aynı sayıları verdi; ε = 0,25 ile s = 0,5 neredeyse aynı (794 051 ve 794 054).
3. **Tamsayı olmayan tahmincide iki yasa da büyük ε'da tutmuyor.** Bu bir başarısızlık ve öyle raporlanıyor.
   * ε ≤ 0,1 °C'de değişim sayısını eklenti toplamı doğru verdi ve net değişim sıfıra yakın kaldı.
   * ε ≥ 0,25 °C'de hata, değerin kendisine ve yerel eğime bağlı hale geliyor. Bu yüzden "rastgele hata" varsayımı bozuluyor.
   * ε = 1 °C'de 35 °C üstü günler **%9,8 arttı**. "Rastgele görünen" bir kodlayıcı bile sayımı tek yönde kaydırabiliyor.
4. **Uygulamadaki sonuç.** Sayım yapılacaksa ya eşiği hücre sınırına koymak gerekiyor (CERT; P34'te sıfır değişim), ya da sapmayı $N p_0 h/2$ ile önceden bildirmek.

# Makaleye etkisi

* Ana mesaj güçlendi: tek yönlü yanlılık artık arşivlerin gerçekten kullandığı üç kodlayıcıda gösterilmiş durumda.
* "Rastgele hatalı kodlayıcılar dengelidir" cümlesi yalnızca ZFP ve küçük ε için kurulabilir. NIPRED sonucu makalede açıkça başarısız ön kayıtlı tahmin olarak yer alacak.

Dosyalar: `p34b_pilot.txt/json`, `p34b_confirm.txt/json`, `P34B_PILOT_NOTE`, `diag_nipred.py`.
