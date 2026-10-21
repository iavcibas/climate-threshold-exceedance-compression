---
title: "P34b — Pilot notu (onay koşusundan önce yazıldı)"
date: "5 Ekim 2026 (2021–2024 verisinde P34b henüz çalıştırılmadı)"
---

# Pilot sonucu (2020, kural kararı yok)

* **B1:** 44/44, **B2:** 44/44. Paketleme, bit yuvarlama ve Lorenzo'da her değişim tek yönde ve ızgara yasasının öngördüğü işarette. En büyük sapma −%9,2 (LORENZO 1,0; 40 °C).
* **B3:** 8/15 ve 12/15, kural sağlanmıyor. Tamsayı olmayan tahminci (NIPRED), ε = 0,05 ve 0,1 °C'de eklenti toplamına uyuyor; ε ≥ 0,25 °C'de uymuyor.

# Neden: pilot verisinde yapılan tanı (`diag_nipred.py`)

Eklenti toplamı, eşiğin yakınında hatanın verinin değerinden bağımsız olduğunu varsayar. NIPRED'de büyük ε için bu varsayım bozuluyor:

* Hata yerel eğime bağlı. Örneğin ε = 0,5 °C, 30 °C'de: doğuya doğru ısınan yerlerde ortalama hata −0,23 °C, soğuyan yerlerde +0,24 °C. Yeniden kurulmuş değer, gerçek değerin gerisinden geliyor. Tahmin farkı ε'dan küçük kaldıkça değer güncellenmiyor.
* Eşiğin hemen yanındaki hata, pencerenin ortalamasından farklı:
  * ε = 1, 35 °C: ortalama hata +0,23 °C (pencerede +0,04);
  * ε = 1, 40 °C: ortalama mutlak hata 0,16 °C (pencerede 0,45).
* Sonuçta NIPRED'in sayım değişimi de **iki yönlü değil**. ε = 1 °C'de 35 °C üstü günler +215 787 değişti; bu, aşımların **+%10,2**'si. 30 °C'de +175 822 (+%3,0).

# Karar

**Kurallar değiştirilmiyor.** B3 onay yıllarında da büyük olasılıkla tutmayacak ve öyle raporlanacak. Makalede NIPRED şu şekilde anlatılacak: "rastgele görünen" ama değere bağlı hatası olan bir kodlayıcı; iki yasa da yalnız küçük ε'da geçerli; büyük ε'da sayımı yine tek yönde kaydırabiliyor.

Bu not onay koşusundan önce kayda geçirildi.
