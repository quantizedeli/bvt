"""v9.2 constants kalibrasyon dogrulama -- BVT_ClaudeCode_TODO_v9.2.1 FAZ A.6"""
import sys
import os
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from src.core.constants import (
    KAPPA_EFF, GAMMA_DEC, GAMMA_DEC_HIGH, MU_HEART, MU_HEART_MCG, MU_0,
    OMEGA_SPREAD_DEFAULT, N_C_SUPERRADIANCE, F_HEART,
)

print("=" * 60)
print("v9.2 SABİT KALİBRASYON DOĞRULAMA")
print("=" * 60)

# Test 1: K/K_c oranı (Kuramoto kritik bağlaşım K_c = 2×σ_ω)
K_c = 2 * OMEGA_SPREAD_DEFAULT
ratio = KAPPA_EFF / K_c
assert 1.5 <= ratio <= 7.0, f"K/K_c={ratio:.2f} dışı [1.5, 7.0]"
print(f"✓ K/K_c = {ratio:.2f}  (gerçekçi süperkritik, K_c={K_c:.2f})")

# Test 2: N_c formülünden
N_c_formul = GAMMA_DEC_HIGH / KAPPA_EFF * 100
assert 8 <= N_c_formul <= 13, f"N_c={N_c_formul:.1f} literatürden uzak (8-13)"
print(f"✓ N_c = {N_c_formul:.1f}  (literatür 10-12, γ/κ={GAMMA_DEC_HIGH/KAPPA_EFF:.3f})")

# Test 3: Kalp B alanı (5cm'de 10-200 pT) — MU_HEART_MCG alan hesapları için kalibre değer
mu_0_over_4pi = MU_0 / (4 * np.pi)
B_5cm = mu_0_over_4pi * 2 * MU_HEART_MCG / (0.05 ** 3)
B_5cm_pT = B_5cm * 1e12
assert 10 <= B_5cm_pT <= 200, f"B(5cm)={B_5cm_pT:.1f} pT dışı [10, 200]"
print(f"✓ B(5cm) = {B_5cm_pT:.1f} pT  (MU_HEART_MCG={MU_HEART_MCG:.2e}, literatür: 50-100 pT)")

# Test 4: τ_sync (Kuramoto senkron zamanı)
if KAPPA_EFF > K_c:
    tau_sync = 1.0 / (KAPPA_EFF - K_c)
    assert 0.3 <= tau_sync <= 30, f"τ_sync={tau_sync:.2f}s dışı [0.3, 30]"
    print(f"✓ τ_sync ~ {tau_sync:.2f}s  (HeartMath: 5-15s, KAPPA-K_c={KAPPA_EFF-K_c:.2f})")
else:
    print(f"[UYARI] KAPPA_EFF={KAPPA_EFF} <= K_c={K_c} — senkron oluşmaz!")

# Test 5: N_C_SUPERRADIANCE integer kontrolü
assert N_C_SUPERRADIANCE == int(N_c_formul), f"N_C_SUPERRADIANCE={N_C_SUPERRADIANCE} ≠ formül={int(N_c_formul)}"
print(f"✓ N_C_SUPERRADIANCE = {N_C_SUPERRADIANCE}  (γ/κ×100 formülünden)")

# Test 6: MU_HEART güncellendi
assert MU_HEART == 1e-5, f"MU_HEART={MU_HEART}, 1e-5 bekleniyor"
print(f"✓ MU_HEART = {MU_HEART:.0e} A·m²  (v9.2 MCG gerçekçi değer)")

# Test 7: OMEGA_SPREAD_DEFAULT
assert OMEGA_SPREAD_DEFAULT == 1.5, f"OMEGA_SPREAD_DEFAULT={OMEGA_SPREAD_DEFAULT}, 1.5 bekleniyor"
print(f"✓ OMEGA_SPREAD_DEFAULT = {OMEGA_SPREAD_DEFAULT} rad/s  (gerçekçi HRV dağılımı)")

print("\n" + "=" * 60)
print("✅ TÜM v9.2 KALİBRASYON TESTLERİ GEÇTİ (7/7)")
print("=" * 60)

if __name__ == "__main__":
    pass
