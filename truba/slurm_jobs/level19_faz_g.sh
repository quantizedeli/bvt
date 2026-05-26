#!/bin/bash
#SBATCH --job-name=bvt_fazg
#SBATCH --account=YOUR_ACCOUNT          # TRUBA hesap kodu (ULAKBIM)
#SBATCH --partition=akya-cuda           # GPU partition; CPU için: orfoz / barbun
#SBATCH --gres=gpu:1                    # GPU node — CPU-only kullanım için kaldır
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=24:00:00                 # 22 enstrüman × ~1 sa CPU (GPU ile ~2-4 sa)
#SBATCH --output=truba/logs/bvt_fazg_%j.out
#SBATCH --error=truba/logs/bvt_fazg_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=ahmetkemalacar@gmail.com

# =============================================================
# BVT Sprint 07 S6 — FAZ G TRUBA Batch (D-009)
# =============================================================
# Tetikleyici: makale revizyonu "tam çözünürlük" hakem talebi veya
# 1080p sinematik hero animations için yüksek-res voxel ihtiyacı.
#
# Yerel 32×32×40 sonuçları bilim kanıtı için yeterli — bu batch sadece
# tam katalog (22 enstrüman) + HEAD_GRID_HIGH_RES (80×80×100) için.
#
# Önkoşul:
#   - TRUBA hesap onayı + YOUR_ACCOUNT yukarıda doldurulmalı
#   - Repo TRUBA'ya rsync edilmiş: rsync -av --exclude='output/' . truba:~/bvt/
#   - Conda/venv hazır: module load python/3.11; pip install -r requirements.txt
#
# Çalıştırma:
#   sbatch truba/slurm_jobs/level19_faz_g.sh
# =============================================================

set -e
echo "[$(date)] Job start (Job ID: $SLURM_JOB_ID)"
echo "Node: $SLURMD_NODENAME, GPU: $CUDA_VISIBLE_DEVICES"

cd $SLURM_SUBMIT_DIR || cd ~/bvt
mkdir -p truba/logs output/level19/cache

# Ortam yükleme (TRUBA modül sistemi)
module purge
module load python/3.11
module load gcc/11.3.0
# GPU varsa: module load cuda/12.1

# Python venv aktif (yerel veya conda)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Kontrol
python -c "import numpy, scipy, mne; print(f'np={numpy.__version__} sp={scipy.__version__} mne={mne.__version__}')"
python -c "from src.models.acoustic import kos_faz_g; print('FAZ G import OK')"

# Ana koşum — 22 enstrüman + HIGH_RES (80×80×100) + sure_dakika=1.0 (60 sn fiziksel)
# NOT: --grid high_res flag Sprint 08'de eklenecek; şu an manuel constants.py overrride
echo "[$(date)] FAZ G top5 (test) başlıyor..."
python simulations/level19_volumetric_acoustic.py \
    --frekanslar top5 \
    --sure-dakika 1.0 \
    --spl-db 70.0 \
    --anim

echo "[$(date)] FAZ G tam katalog (22 enstrüman) başlıyor..."
python simulations/level19_volumetric_acoustic.py \
    --frekanslar tum \
    --sure-dakika 1.0 \
    --spl-db 70.0 \
    --anim \
    --anim-aspect both

# Sonuçları yerele rsync için tar
echo "[$(date)] Çıktıları arşivle..."
tar czf output/level19_truba_$(date +%Y%m%d_%H%M).tar.gz \
    output/level19/*.png output/level19/*.mp4 output/level19/cache/

echo "[$(date)] Job complete"

# Yerele indirme (yerelden çalıştır):
#   rsync -av truba:~/bvt/output/level19_truba_*.tar.gz output/
#   tar xzf output/level19_truba_*.tar.gz
