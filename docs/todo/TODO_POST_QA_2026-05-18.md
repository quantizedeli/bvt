# BVT Post-QA TODO — 2026-05-18

## P0 — güven / doğruluk

- [ ] `main.py` için iki ayrı mod tasarla:
  - `--smoke` = dakikalar değil saniyeler içinde sistem kontrolü
  - `--hizli` = bilimsel olarak hâlâ anlamlı ama kısaltılmış çalışma
- [ ] `docs/TODO.md` dosyasını “historical backlog” olarak işaretle veya güncel backlog’a böl
- [ ] Dashboard asset sync’i render pipeline sonuna otomatik bağla

## P1 — cinematic olgunlaştırma

- [ ] Hero01: 3D field shells
- [ ] Hero01: coherent vs incoherent split scene
- [ ] Hero01: 16:9 final + 9:16 final
- [ ] Hero02: PyVista 3D field merge + distance-driven camera
- [ ] Hero03: topology compare cinematic montage
- [ ] Hero04: topology morph 3D remake

## P1 — dokümantasyon hijyeni

- [ ] `README.md` içinde klasik animasyon sayısını script tabanlı dinamik ölçüme bağla veya sayı vermeyi bırak
- [ ] `docs/simulation_levels.md` süre tahminlerini gerçek benchmark çıktılarıyla güncelle
- [ ] `CHANGELOG.md` sürüm sıralamasını normalize et (`v9.9.0`, `v9.5.0-dev`, `v9.3.1` kronolojisi karışık)

## P2 — repo temizliği

- [ ] Vendored `marimo-0.23.2/` için ayrı envanter notu veya submodule stratejisi düşün
- [ ] `output/` artefaktlarının hangilerinin kaynak, hangilerinin türetilmiş olduğunu manifest düzeyinde ayır
- [ ] `git status` erişim uyarısı (`~/.config/git/ignore` permission denied) için yerel ortam notu ekle
