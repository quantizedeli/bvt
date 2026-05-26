# TRUBA HPC Entegrasyonu — BVT v9.4+

> **Status:** Sprint 07 S6 (taslak). D-009 DEFERRED kaydı — yerel
> 32×32×40 sonuçları bilim kanıtı için yeterli; TRUBA tam katalog
> (22 enstrüman) + HIGH_RES (80³) + 1080p sinematik için.

## Önkoşullar

1. **TRUBA hesap onayı:** [TÜBİTAK ULAKBIM TRUBA portal](https://yonetim.truba.gov.tr/) üzerinden başvuru → onay (~1 hafta).
2. **SSH key:** `~/.ssh/truba_rsa` ile login.
3. **Hesap kodu:** `slurm_jobs/level19_faz_g.sh` içinde `YOUR_ACCOUNT` doldurulmalı.

## İlk kez kurulum (TRUBA üzerinde)

```bash
# TRUBA login node
ssh username@orfoz.tr
git clone https://github.com/quantizedeli/bvt.git
cd bvt

# Python venv (CPU veya GPU partition'a göre)
module load python/3.11
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test
python -c "from src.models.acoustic import kos_faz_g; print('OK')"
```

## Yerel → TRUBA rsync

```bash
# Yerelden TRUBA'ya kod gönderme (output hariç)
rsync -av --exclude='output/' --exclude='__pycache__/' \
    --exclude='*.pyc' --exclude='.git/' \
    ./ truba:~/bvt/

# Geri çekme (sonuçlar)
rsync -av truba:~/bvt/output/level19/ ./output/level19/
```

## SBATCH submit

```bash
# TRUBA login node'da
cd ~/bvt
sbatch truba/slurm_jobs/level19_faz_g.sh

# Status kontrol
squeue -u $USER
sacct -j JOB_ID --format=JobID,JobName,Elapsed,State,ExitCode

# Log'lar
tail -f truba/logs/bvt_fazg_*.out
```

## Süre tahminleri

| Senaryo | CPU 32 core | GPU 1×V100 |
|---|---|---|
| top5, sure_dakika=0.1 | ~15 dk | ~3 dk |
| top5, sure_dakika=1.0 (anlamlı HRV) | ~2 saat | ~20 dk |
| Tüm 22 enstrüman, sure_dakika=1.0 | ~12 saat | ~2 saat |
| HEAD_GRID_HIGH_RES (80³), 22 enstrüman | ~22 saat | ~4 saat |

## Sprint 08 yapılacaklar (henüz hazır değil)

- [ ] `--grid high_res` CLI flag (level19) — `HEAD_GRID_HIGH_RES = (80,80,100)` aktif
- [ ] k-Wave-python GPU build deneme (D-008 geri-dönüş tetikleyicisi)
- [ ] Yerel 32³ vs TRUBA 80³ karşılaştırma figürü
- [ ] `--frekanslar tum` paralel multi-process speedup

Detay: `sprint_docs/SPRINT_07_FAZ_G_SPILLOVER.md` S6, `sprint_docs/DEFERRED_DECISIONS.md` D-009.
