---
title: "P34 — Çalıştırma talimatı"
date: "5 Ekim 2026"
---

WSL Ubuntu'da (internet gerekli). GPU kullanılmaz.

**1. Paketler (bir kez):**

```
conda activate selfmad
pip install netCDF4 zfpy
```

zfpy kurulamazsa sorun değil: kod yalnız UQ ve CERT kollarıyla çalışır.

**2. Pilot verisi (yaklaşık 81 MB):**

```
cd "/mnt/c/srlc/CALISMALAR/GELECEK YONLER/P34 climate threshold exceedance gate test"
mkdir -p data && cd data
wget https://psl.noaa.gov/thredds/fileServer/Datasets/cpc_global_temp/tmax.2020.nc
cd ..
python p34_run.py --pilot
```

Bağlantı çalışmazsa bana yazın; THREDDS sayfasından doğru adresi birlikte buluruz.

Pilot bittiğinde ekrandaki ilk satırları (N, granularity, her eşik için p0) ve kural bölümünü bana yapıştırın. Pilotun sonucu bağlayıcı değildir; yalnızca verinin beklediğimiz gibi olup olmadığını görmek içindir.

**3. Onay verisi (yaklaşık 320 MB) ve asıl koşu.** Pilot sorunsuzsa:

```
cd data
for y in 2021 2022 2023 2024; do wget https://psl.noaa.gov/thredds/fileServer/Datasets/cpc_global_temp/tmax.$y.nc; done
cd ..
python p34_run.py --confirm
```

Asıl koşu birkaç dakika sürer (ZFP ile biraz daha uzun). Kural bölümünü ve "Verdict" satırını yapıştırmanız yeterli.
