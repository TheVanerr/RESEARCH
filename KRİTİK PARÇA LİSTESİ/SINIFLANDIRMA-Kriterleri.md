# Kritik parça sınıflandırması — çalışma mantığı

Bu proje **IEC/IEEE 82079-1** anlamında *hangi parçaların dokümante edileceği* (yedek/sarf listesi) ile **işletmenin depoda ne tutacağı** (stok politikası) ayrımına dayanır. Liste geniş; stok dar tutulur.

## Boyut 1 — Önem derecesi (A / B / C)

| Kod | Anlam | Örnek |
|-----|--------|--------|
| **C** | Arızada makine **çalışmaz** veya **emniyet onayı yok** (tek nokta arıza) | Safety PLC, ana pompa, seviye emniyeti, kapak zinciri |
| **B** | Makine **kısıtlı** çalışır; kısa sürede duruş veya ciddi kalite/kapasite kaybı | Tek invertör (yedek devre yok), kurutma fanı |
| **A** | Makine **çalışmaya devam eder**; konfor, hız, ikincil fonksiyon | Sinyal lambası, ikinci pompa devredeyken alternatif |

**Not:** C = “kritik parça listesinde mutlaka satır” eşiği değil; listede A da olabilir. C, **öncelik ve aciliyet** içindir.

## Boyut 2 — Bozulma / aşınma (1 / 2 / 3)

| Kod | Anlam | Örnek |
|-----|--------|--------|
| **1** | **Sık** tüketim/aşınma (bakım periyodunda, aylık–yıllık) | Kontaktör, filtre, nozzle, sepet tekeri, keçe |
| **2** | **Orta** (birkaç yıl, planlı ömür) | Redüktör, bazı sensörler, rezistans |
| **3** | **Seyrek** (normal ömürde beklenmez; olay bazlı) | Safety PLC, pano gövdesi, darbe/kaza hasarı |

**1** stok kararını güçlendirir; **3** stok zorunluluğunu zayıflatır (C olsa bile).

## Boyut 3 — Ulaşılabilirlik (K / O / Z) — önerilir

| Kod | Anlam | Örnek |
|-----|--------|--------|
| **K** | **Kolay** — piyasa, hızlı tedarik (günler) | Kontaktör, termik, kablo rakoru |
| **O** | **Orta** — bayi/ithalat, tipik termin (1–3 hafta) | Özel pompa, marka sensör |
| **Z** | **Zor** — CNK imalat, uzun termin, tek kaynak | Özel sac komple, özel sepet |

**Evet, dahil edilmeli.** Aynı C+3 parçada bile: K ise “siparişle 2 günde gelir”, Z ise “listedeki kod ve teknik resim şart” farkı oluşur.

## Stok önerisi (liste ile karıştırma)

Üç sezgisel grup tek tabloda **matris** ile ifade edilir:

| Tip | Tipik profil | Stok |
|-----|----------------|------|
| **Depo stoku (tüketim)** | Aşınma **1**, genelde **K**, düşük birim fiyat | Evet (adet politikası sizde) |
| **Planlı aşınma** | Aşınma **1–2**, **B/C** olabilir | Evet / minimum |
| **Liste-only (kritik sipariş)** | Önem **C**, aşınma **3** | Hayır (0); arızada sipariş |

Örnekleriniz:
- **Kontaktör:** önem B/C (devreye göre), aşınma 1, ulaşılabilirlik K → **stokta tut**.
- **Sepet tekeri:** önem B, aşınma 1, ulaşılabilirlik O/Z → **stokta tut**.
- **Safety PLC:** önem **C**, aşınma **3**, ulaşılabilirlik O → **listede satır, stok 0** (darbe/kaza istisnası; MTBF yüksek).

## Excel / HTML sütunları

1. Sipariş kodu · Parça adı · **Fotoğraf** (dosya yolu) · Varyant  
2. **Önem (A/B/C)**  
3. **Aşınma (1/2/3)**  
4. **Ulaşılabilirlik (K/O/Z)**  
5. **Önerilen stok (adet)** — elle veya politika tablosuna göre  
6. **Not / gerekçe**

Komple–alt parça ayrımı veri doldurulunca eklenebilir; şablon düz tablodur.

## Uygulanan stok formülü

`build_kritik_sablon.py` → `STOK_KURALLARI`. Önerilen miktar **yalnızca** Önem + Aşınma + Ulaşılabilirlik'ten hesaplanır; aynı sınıftaki iki parça her zaman aynı miktarı alır. Elle girilen miktar ve gerekçe her üretimde formülle üzerine yazılır. Sınıf eksikse miktar 0 olur.

**Aşınma belirleyicidir:** sık (1) ≥ 2 > orta (2) = 1 ≥ seyrek (3) ≤ 1. Nadir bozulan bir parça (ör. faz koruma rölesi) hiçbir zaman sık bozulan bir parçadan (ör. rezistans) fazla stok almaz. Ulaşılabilirlik yalnızca seyrek + kritik parçada "1 emniyet yedeği mi, sadece liste mi" kararını verir.

| Kural (ilk eşleşen) | Miktar | Gerekçe |
|---|---|---|
| C + 1 | 3 | sık aşınma, kritik — depo seti |
| A/B + 1 | 2 | sık aşınma — depo seti |
| 2 (her önem/ulaş.) | 1 | orta aşınma — 1 yedek |
| C + 3 + K/O | 1 | kritik ama seyrek — 1 emniyet yedeği |
| C + 3 + Z | 0 | kritik, seyrek, imalat / uzun termin — listede tut, siparişle |
| A/B + 3 | 0 | seyrek arıza — listede tut, siparişle |

**Set birimli parçalar (nozzle):** adet yerine **set** önerilir; formül stok veriyorsa **1 set** = makinedeki nozzle takımı. `SET_BIRIMLI` deseniyle başka parça aileleri de eklenebilir.
