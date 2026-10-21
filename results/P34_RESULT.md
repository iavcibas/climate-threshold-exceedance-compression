---
title: "P34 — İklim verisinde eşik aşımı sayımları: kapı sonucu"
date: "5 Ekim 2026"
---

# Karar

**Kapı geçti.** Onay yılları 2021–2024, toplam 91 864 030 geçerli gün-hücre. K1 15/15, K2 15/15, K3 15/15.

# Öne çıkan sayılar (35 °C eşiği, 9 134 605 aşım)

| Kodlayıcı | ε (°C) | Değişen gün | Tahmin | Net sayım değişimi | Aşımlara oranı |
|---|---|---|---|---|---|
| UQ (SZ türü noktasal) | 0,05 | 84 885 | 84 389 | +84 885 | +%0,93 |
| UQ | 0,1 | 177 221 | 178 790 | −177 221 | −%1,94 |
| UQ | 0,5 | 785 556 | 753 927 | +785 556 | **+%8,6** |
| UQ | 1,0 | 469 709 | 482 722 | −469 709 | −%5,1 |
| ZFP | 0,5 | 73 159 | 73 332 | −13 199 | −%0,14 |
| ZFP | 1,0 | 144 835 | 145 541 | +18 355 | +%0,20 |
| CERT (eşiğe hizalı) | hepsi | 0 | 0 | 0 | 0 |

# Sade dille

1. **SZ türü bir nicemleme sıcak gün sayısını sistematik olarak kaydırıyor.** Eşiğin düştüğü hücredeki bütün değerler aynı tarafa gidiyor. Değişimlerin hepsi tek yönde ve sayısı tam olarak $N p_0 d_\tau$. Bu formülün tek girdisi ızgaranın eşiğe göre nerede durduğu. ±0,5 °C hata sınırında 35 °C üstü günler %8,6 şişti. Aynı hata sınırı, ızgara başka bir yerde dursaydı sayıyı azaltabilirdi; nitekim ±0,1 ve ±1 °C'de azalttı. İklim çalışmalarında "sıcak gün sayısı arttı mı" sorusunu doğrudan etkileyen bir yanlılık bu.
2. **ZFP de karar değiştiriyor, ama dengeli biçimde.** Değişen gün sayısını eklenti toplamı neredeyse birebir tahmin etti (15/15). Net sayım değişimi küçük (%0,2'nin altında), çünkü değişimler iki yöne dağılıyor.
3. **Eşiğe hizalı nicemleyici bütün değişimleri siliyor.** Bu, sizin sertifikasyon çizginizin iklim verisindeki karşılığı ve aynı bit maliyetinde geliyor.
4. **Kestirim için yalnızca iki şey gerekiyor:** verinin eşikteki yoğunluğu ($p_0$) ve kodlayıcının ızgarası ya da hata dağılımı. Sıkıştırmayı çalıştırmadan, önceden hesaplanabiliyor.

# Notlar

* Net sayım değişimi ZFP için kural değildi. İşaret çoğu hücrede doğru, ama büyüklük kaba tahmin ediliyor (ör. ε = 1, 30 °C'de ölçülen −19 487, tahmin −5 195). Makalede yalnızca betimleyici olarak verilir.
* Pilot yılı (2020) aynı sonucu verdi ve karar için kullanılmadı.
* **Dergi:** Computers & Geosciences ya da Environmental Modelling & Software (ikisi de hibrit). GMD için önce APC kapsamı kontrol edilmeli.

Dosyalar: `p34_pilot.txt/json`, `p34_confirm.txt/json`.
