---
title: "P34 — İklim verisinde eşik aşımı kararları: yenilik taraması"
date: "5 Ekim 2026"
---

# Soru

İklim ve hava verisi kayıplı sıkıştırılıyor. Ama kullanıcıların baktığı şey çoğu zaman bir eşik: "kaç gün 35 °C'yi geçti?" Hata sınırlı bir sıkıştırıcı bu sayıları ne kadar değiştirir? Bu değişim önceden kestirilebilir mi? Eşiği hiç bozmayan bir nicemleyici ne kadara mal olur?

# Bulunan yakın çalışmalar

| Çalışma | Ne yapıyor | Bizden farkı |
|---|---|---|
| Baker vd., *Evaluating lossy data compression on climate simulation data within a large ensemble*, GMD 9 (2016) | CESM büyük topluluğunda kayıplı sıkıştırmanın istatistiksel olarak ayırt edilip edilemediği. | Eşik aşım sayıları ve bunların kestirimi yok. |
| Poppick vd., *A statistical analysis of lossily compressed climate model data*, Computers & Geosciences (2020) | SZ ve ZFP'nin iklim verisinde bıraktığı izler; küçük toleranslarda bile yağışsız gün sıklığını artırdıklarını gösteriyor. | Eşikle ilgili bir yanlılık gözlemi var, ama kestiren bir yasa yok; aşırı uçlar incelenmemiş. |
| Jiao, Liang vd. (yazar sırası doğrulanacak), *Toward quantity-of-interest preserving lossy compression for scientific data* (PVLDB 16, 2023); Liang vd. QPET (PVLDB 18) | Polinom, logaritma, ağırlıklı toplam ve eş-değer yüzeyleri (isosurface) koruyan sıkıştırma. Eş-değer yüzeyde düğümlerin eşiğe göre konumu korunuyor. | **Sertifikalı tarafın yakın öncülü** (ve sizin DCC/TSP çalışmalarınız). Ama standart sıkıştırıcıların sayıları ne kadar bozduğuna dair bir yasa yok. |
| Liu, Jiang, Yang, Di, Underwood, Jin, *TOPIQ* (arXiv 2608.26912, 2026) | Sıkıştırma hatasının düzgün (türevlenebilir) QoI'lere yayılımını istatistiksel olarak kestiriyor; veri olarak CESM-ATM ve Hurricane kullanıyor. | Açıkça şunu yazıyor: "eşik tabanlı sayımlar kapsam dışında". **P34'ün dolduracağı boşluk tam bu.** |

# Değerlendirme

* Eşiği **kesin koruyan** nicemleyici yeni değil (Jiao vd.; sizin sertifikasyon makaleleriniz). P34'te bu yalnızca karşılaştırma kolu olarak yer alır.
* Yeni olabilecek olan, eşik sayımları için kestirim yasası. İki biçimi var:
  1. **Noktasal nicemleyici** (SZ'nin nicemleme adımı): Eşiğin düştüğü hücrenin tamamı tek yöne gider. Değişen gün sayısı $N p_0 d_\tau$ olur ($d_\tau$: eşiğin hücre sınırına uzaklığı) ve **hepsi aynı yönde** değişir. Bu, sayımlarda sistematik bir yanlılık demek: ızgaranın eşiğe göre nerede durduğuna bağlı olarak sıcak gün sayısı ya şişer ya azalır.
  2. **Dönüşüm kodlayıcı** (ZFP): Hataların eşik çevresindeki dağılımından, eklenti (plug-in) bir toplamla.
* TOPIQ'in kapsam dışı bıraktığı alanı doldurduğu için bir okuyucu kitlesi var. Ama katkı mütevazı. Doğru yer: **Computers & Geosciences** (Elsevier, hibrit) ya da **Environmental Modelling & Software** (hibrit). GMD açık erişimli ve APC istiyor; TÜBİTAK anlaşması kapsıyor mu, kontrol edilmeli.

**Karar:** Kapıya değer, ama beklentiyi orta tutalım: iyi bir dergi makalesi olur, büyük bir sonuç olmaz.
