---
title: "P34 — Ön kayıt"
date: "5 Ekim 2026 (gerçek veri görülmeden)"
---

# Veri

NOAA CPC Global Daily Maximum Temperature, 0,5°, yalnız kara hücreleri. Dosyalar `tmax.YYYY.nc`, yıl başına yaklaşık 81 MB.

* **Pilot:** 2020. Yalnızca veriyi ve kodu kontrol etmek için; hiçbir kural bu yıla bakılarak karara bağlanmaz.
* **Onay:** 2021–2024. Kurallar yalnızca bu yıllarda değerlendirilir.

# Kodlayıcılar ve eşikler

* **UQ(ε):** Noktasal düzgün nicemleyici, adım 2ε. Izgara fazı ε başına bir kez, sabit tohumla rastgele seçilir. SZ türü sıkıştırıcıların nicemleme adımıyla aynıdır.
* **CERT(ε):** Aynı adım, ama eşik bir hücre sınırına oturtulmuş, hücreler sağdan kapalı. Bu, sertifikalı karşılaştırma kolu.
* **ZFP(ε):** zfp sabit doğruluk kipi, tolerans ε; her günlük alan ayrı sıkıştırılır, okyanus 0 ile doldurulur. zfpy kurulamazsa bu kol düşer ve K2 değerlendirilmez.
* ε ∈ {0,05; 0,1; 0,25; 0,5; 1,0} °C; eşik τ ∈ {30, 35, 40} °C; "aşım" = değer > τ.

# Tahminler (yalnız özgün veri ve kodlayıcının hata istatistiğinden)

* **UQ:** $F=N\,p_0\,d_\tau$. Burada $d_\tau$, eşik ile yeniden kurma noktasının karşı tarafındaki hücre sınırı arasındaki uzaklık. Sayım değişimi $\pm F$; işaret, yeniden kurma noktasının eşiğin üstünde ya da altında olmasına göre belirlenir. $p_0$, özgün verinin τ'daki yoğunluğu (±0,25 °C pencere).
* **ZFP:** τ'ya yakın her özgün değerin eşiği geçme olasılığı, kodlayıcının τ çevresindeki hata dağılımından alınır. Hatanın değerden bağımsız olduğu varsayılır. Bu olasılıkların toplamı değişen gün sayısını, işaretli toplamı da net sayım değişimini verir.
* **CERT:** Sıfır değişim (kesin).

# Kurallar (yalnız onay yılları)

* **K1 (UQ yasası):** En az 30 değişimli UQ hücrelerinin en az %80'inde |ölçülen − tahmin| ≤ max(%15, 2√tahmin) olmalı.
* **K2 (ZFP yasası):** Aynı ölçüt ZFP hücreleri için.
* **K3 (yön ve kesinlik):** Her UQ hücresinde (≥30 değişim) bütün değişimler tek yönde ve tahmin edilen işarette olmalı. Her CERT hücresinde değişim 0 olmalı.

**Okuma:**

* K1, K2 ve K3 geçerse makale yazılır.
* K1 ile K2'nin ikisi de kalırsa kapı kapanır.
* Diğer durumlarda sonuç kural kural raporlanır.

# Sentetik ön deneme ve düzeltme (dürüstlük notu)

`--selftest` sentetik alanlarla yapıldı (0,01 °C ızgarasında saklanmış değerler).

İlk kuramda UQ için de $F=N p_0 E|e|$ yazmıştım. Deneme bunun yanlış olduğunu gösterdi: noktasal bir nicemleyici eşiğin düştüğü hücreyi bütünüyle tek bir tarafa taşır. Değişimlerin hepsi aynı yönde olur ve sayısı $N p_0 d_\tau$'dur. Ortalama $E|e|=\varepsilon/2$ formülü yalnızca ızgara fazı üzerinden ortalamada doğrudur.

Aynı denemede ZFP için de iki şey ortaya çıktı:

* Veri sonlu bir ızgarada saklandığında, tam τ'ya eşit değerler (bağlar) önemli bir katkı yapıyor.
* Yoğunluğa dayalı kapalı form bu katkıyı kaçırıyor.

Bu yüzden ZFP için eklenti toplamına geçildi. Düzeltilmiş kodla sentetik veride K1 13/15, K2 15/15, K3 15/15 sağlandı.

Kurallar bu düzeltmeden sonra yazıldı. Gerçek veri henüz görülmedi.
