# bvt-simulate Agent

## Rol
BVT simülasyon çalıştırma, NaN/Inf kontrolü ve çıktı doğrulama.

## Ne Zaman Kullan
- Belirli bir level (1-18) çalıştırmak gerektiğinde
- Simülasyon çıktısını doğrulamak istediğinde (NaN, Inf, fiziksel sınırlar)
- Hizlı test (`--hizli`) sonuçlarını analiz etmek için

## Çalıştırma Komutu Şablonu
```bash
# Tek level (örn: 7)
python simulations/level7_tek_kisi.py --output output/level7

# main.py üzerinden
python main.py --faz 7

# Hızlı test
python main.py --hizli --phases 7 8 9
```

## Doğrulama Protokolü
1. Çıktı `output/levelN/` dizininde mi?
2. PNG dosyası oluştu mu?
3. `r_final` > 0 mu?
4. `eta` / `C` değerleri [0,1] aralığında mı?
5. NaN/Inf yok mu?

## Bilinen Sorunlar
- Level 3 (QuTiP): ~1 saat sürer, --hizli ile atla
- Level 13: η formülü düzeltildi (BVT Bölüm 13, amplitude-weighted)
