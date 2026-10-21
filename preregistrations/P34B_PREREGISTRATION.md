---
title: "P34b — Arşivlerin gerçekte kullandığı kodlayıcılar: ön kayıt"
date: "5 Ekim 2026 (P34b kodlayıcıları gerçek veride hiç çalıştırılmadan)"
---

# Neden

P34'teki "UQ" kolu, ızgara fazı rastgele seçilmiş sabit bir ızgaraydı. Ben bunu "SZ türü" diye adlandırmıştım; bu ad tam doğru değil. SZ, değeri doğrudan nicemlemez: önce bir tahmin yapar ve yalnızca tahmin farkını nicemler. Bu yüzden P34'ün yalnızca UQ'yla verdiği sonucu, arşivlerin gerçekten kullandığı kodlayıcılarda sınamak gerekiyor:

* **PACK(s):** netCDF/GRIB tarzı paketleme (`scale_factor`, `add_offset = 0`): $\hat x=s\cdot\mathrm{round}(x/s)$, s ∈ {0,01; 0,05; 0,1; 0,25; 0,5} °C.
* **BITROUND(k):** Mantisi k bite en yakına yuvarlama (eşitlikte çifte), numcodecs BitRound'un yaptığı işlem. k ∈ {5, …, 9}. 35 °C'de adım $2^{5-k}$: 1; 0,5; 0,25; 0,125; 0,0625 °C.
* **LORENZO(ε):** SZ-1 tarzı tahminli nicemleme, boylam boyunca; tahmin bir önceki yeniden kurulmuş değer.
* **NIPRED(ε):** Aynısı, ama tamsayı olmayan tahminle ($0{,}75\,r_{j-1}+0{,}25\,r_{j-2}$).
* Bütün çıktılar arşivdeki gibi float32 olarak saklanır.

# Sentetik denemede bulunan ve kurama eklenen bir gözlem

Tamsayı ağırlıklı bir tahminci (Lorenzo) yeniden kurulmuş değerleri $2\varepsilon\mathbb Z$ ızgarasının üzerinde tutar. Çünkü ızgara noktalarının tamsayı katsayılı toplamı yine ızgara noktasıdır. Sonuç olarak Lorenzo, sabit ızgaralı bir nicemleyici gibi davranır.

Eşikler (30, 35, 40 °C) bu ızgaraların çoğunda tam bir ızgara noktasıdır. O zaman eşiğin hücresi $[\tau-h/2,\,\tau+h/2]$ olur ve $(\tau,\tau+h/2]$ aralığındaki her değer aşımını kaybeder:
$$F=N\,p_0\,h/2,\qquad \Delta C=-F.$$
Kısacası: **yuvarlama, "yuvarlak" bir eşiğin üstündeki sıcak günleri sistematik olarak siler.**

Eşik bir ızgara noktası değilse, yön ve büyüklük P34'teki uzaklık kuralıyla belirlenir. Örneğin Lorenzo ε = 1'de 35 °C hücre sınırına düşer ve hiç değişim olmaz.

Tamsayı olmayan tahminci ise her adımda ızgarayı inceltir. Hatalar rastgele davranır, değişimler iki yöne dağılır.

# Kurallar (yalnız onay yılları 2021–2024; pilot 2020 bağlayıcı değil)

* **B1:** PACK, BITROUND ve LORENZO hücrelerinde (≥30 değişim) ölçülen değişim, ızgara yasasının max(%15, 2√) toleransı içinde olmalı; hücrelerin en az %80'inde.
* **B2:** Aynı hücrelerin **hepsinde** değişimler tek yönde ve tahmin edilen işarette olmalı.
* **B3:** NIPRED hücrelerinde (≥30 değişim) iki koşul birlikte aranır:
  * değişim sayısı P34'teki eklenti toplamının toleransı içinde olmalı (en az %80);
  * net değişim küçük olmalı: |ΔC| ≤ 0,2 F (en az %80).

Sentetik denemede (yalnızca kod kontrolü): B1 43/44, B2 44/44, B3 15/15 ve 15/15.

# Komutlar

P34 klasöründe; veri zaten indirilmiş durumda:

```
python p34b_run.py --pilot
python p34b_run.py --confirm
```
