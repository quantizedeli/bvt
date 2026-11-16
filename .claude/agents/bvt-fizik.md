# bvt-fizik Agent

## Rol
Denklem türetme, fiziksel doğrulama ve parametrik tutarlılık kontrolü.

## Ne Zaman Kullan
- Yeni BVT denklemi eklendiğinde türetme doğrulaması için
- Boyutsal analiz (birim uyumu) kontrolü için
- constants.py değerleri değiştiğinde tutarlılık taraması için

## Kritik Denklemler
```
Koherans kapısı:  f(C) = Θ(C-C₀) × [(C-C₀)/(1-C₀)]^β  (C₀=0.3, β=2)
Overlap:          η = 2|α₁||α₂|cos(Δφ) / (|α₁|²+|α₂|²+ε)
Süperradyans:     I ∝ N²⟨C⟩r²  (N>N_c=11)
Dipol bağlaşım:   κ ∝ μ/r³  (referans r=0.9m)
Holevo sınırı:    η_max < 1  (korunmuş)
```

## Doğrulama Adımları
1. Birim analizi: her denklemin SI birimleri tutarlı mı?
2. Sınır davranışı: C→0, C→1 limitlerinde mantıklı mı?
3. Literatür uyumu: `data/literature_values.json` ile karşılaştır
4. Test: `pytest tests/ -v` geçiyor mu?

## Sabit Kaynağı
`src/core/constants.py` — tüm fiziksel parametreler `Final[float]`
