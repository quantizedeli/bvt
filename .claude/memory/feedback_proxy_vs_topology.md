---
name: feedback-proxy-vs-topology
description: "Bir proxy/heuristik spec'i geçiyor diye doğru fiziği temsil etmez — kök neden çoğu kez kalibrasyon değil yanlış model topolojisi"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 37ac1a5e-7a49-4ce0-bf40-05b59cc0ab8c
---

BVT Sprint 11'de iki "kalibrasyon problemi" sanılan DEFERRED'in (D-016 JR Hopf,
D-017 HEP topografi) gerçek kök nedeni **yanlış model topolojisi**ydi:

- **D-016:** JR'de dış input p(t) sigmoid'den geçiyordu (`S(I_p+...)`); p∈[100,300]'de
  sigmoid satüre → sabit-nokta, limit-cycle yok. Sprint 09 "A_e/A_i gain + I_p_std
  broadband proxy"si 192× ratio ile spec'i geçti ama gerçek 10 Hz osilasyon değildi.
  Çözüm: kanonik Jansen-Rit topolojisi (p doğrudan eksitatör interneuron'a) →
  Hopf rejimi kendiliğinden açıldı, kabul kriteri daha güçlü sağlandı.
- **D-017:** tek z-eksenli kalp dipolü → tüm elektrodlar aynı sinyalin skaler katı →
  t-testi ölçek-değişmez → topografi ayırt edilemez. Çözüm: santral kortikal kaynak
  (geometri) + sensör gürültü tabanı (ölçek-değişmezliği kırar).

**Why:** Bir proxy spec'in sayısal eşiğini geçtiğinde "tamam" demek cazip; ama
eşiği geçmek ≠ doğru mekanizma. Yanlış topoloji sonsuza kadar kalibre edilemez.

**How to apply:** Bir metrik "beklenenin tersi" veya "makine sıfırına çöküyor" ya da
"tüm kanallar aynı çıkıyor" diyorsa → parametre tweak'inden ÖNCE model denklemlerinin
topolojisini sorgula (girdi nereye giriyor? jump operatörü yapıyı görüyor mu? metrik
ölçek-değişmez mi?). Önce kanonik/literatür topolojisini empirik test et
(`python -c`), sonra kalibre et. Bkz [[feedback-deferred-decisions-log]].
