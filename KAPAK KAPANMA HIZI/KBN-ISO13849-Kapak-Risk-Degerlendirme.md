# KBN Serisi — ISO 13849-1 Kapak Emniyet Fonksiyonları Değerlendirmesi

**Standart:** ISO 13849-1:2023 (EN ISO 13849-1) — Safety of machinery — Safety-related parts of control systems  
**Validation ref.:** ISO 13849-2  
**Kapsam:** Kapak ile ilgili tüm emniyet fonksiyonları (SRP/CS)  
**Kaynak:** `KBN-Risk-Degerlendirme-Bilgi-Formu.md` + `KBN-ISO12100-Kapak-Risk-Degerlendirme.md`  
**Hazırlayan:** Makine Mühendisi Fatih GÜRAL  
**Tarih:** 10.09.2026

---

## 1. Amaç ve kapsam

Bu doküman ISO 12100 risk değerlendirmesinin devamı olarak, kapak alt sistemindeki **emniyetle ilgili kontrol fonksiyonlarının** performans seviyesi (PL) analizini içerir.

**Değerlendirilen konfigürasyonlar:**
- **Konfig A:** Reflektörlü el koruma sensörü (Schneider XUK1 ARCNL2) — standart PLC
- **Konfig B:** Işık perdesi (OMRON F3SG-44RE0880P14-L) + Safety PLC (OMRON G9SX G9SPN20S)

---

## 2. Emniyet fonksiyonları envanteri

| ID | Fonksiyon adı | Tetikleyici | Emniyet durumu (SRP/CS çıkışı) | ISO 12100 ref. |
|----|---------------|-------------|-------------------------------|----------------|
| **SF1** | Kapak kapanırken koruma algılama → tehlikeli hareketi durdur | El sensörü (A) veya ışık perdesi (B) | Kapanma valfi OFF; mevcut: yerinde dur / hedef: geri aç | 6.3.2.5, 6.3.5.3 |
| **SF2** | Kapak kapalı değilken cycle başlatmayı engelle | Mekanik kapak kapalı sensörü | Cycle enable = 0 | ISO 14119 |
| **SF3** | Kapak açılınca cycle durdur | Mekanik kapak sensörü | Cycle stop | ISO 14119 |
| **SF4** | Acil durdurma | Acil stop butonu | Tüm valfler de-energize | ISO 13850 |
| **SF5** | Çift el butonu — kasıtlı kapak komutu | İki el butonu eşzamanlı | Kapak aç/kapa sekansı başlat | ISO 13851 |

**Bu dokümanda detaylı PL analizi:** SF1 (ana ezilme koruması), SF2, SF3, SF4. SF5 ayrı değerlendirilebilir.

---

## 3. PLr belirleme — Risk grafik (Annex A)

### 3.1 SF1 — Kapak ezilme koruması (kapanma sırasında)

| Parametre | Değer | Gerekçe |
|-----------|-------|---------|
| **S — Şiddet** | **S2** | Ezilme: ciddi kalıcı yaralanma (el, kol, parmak) |
| **F — Sıklık / maruziyet** | **F2** | Günlük kullanım, her cycle |
| **P — Kaçınma olasılığı** | **P2** | Otomatik kapanma; sınırlı reaksiyon süresi (8–12 s kapanma, algılama anında durma) |
| **PLr sonucu** | **PLr = d** | ISO 13849-1 Şekil A.1: S2 + F2 + P2 → **d** |

> **Not:** Sensör bypass senaryosunda (Konfig A) P1 kabul edilirse PLr = **e** olur. Tasarım hedefi: **PLr = d** (Konfig B ile karşılanabilir).

### 3.2 SF2 / SF3 — Kapak pozisyon interlock

| Parametre | Değer | Gerekçe |
|-----------|-------|---------|
| S | S2 | Kapak açıkken döner sepet/deterjan — ezilme |
| F | F2 | Her cycle |
| P | P1 | Kapak açık/kapalı görsel olarak belirgin |
| **PLr** | **PLr = c** | S2 + F2 + P1 → c |

### 3.3 SF4 — Acil durdurma

| Parametre | Değer | Gerekçe |
|-----------|-------|---------|
| S | S2–S3 | Geniş tehlike durdurma |
| F | F2 | Her zaman erişilebilir |
| P | — | Acil stop için PLr genelde **PLr = c** (ISO 13850) |
| **PLr** | **PLr = c** | Standart endüstriyel uygulama |

---

## 4. SF1 detaylı analiz — Konfigürasyon A (El sensörü)

### 4.1 Fonksiyon tanımı (mevcut)

```
[Çift el] → Kapak kapanma komutu → [YV-K ON]
    ↓
[XUK1 el sensörü — alt bölge] — algılama?
    ↓ EVET                          ↓ HAYIR
[Standart PLC DI]              [Kapanma devam]
    ↓
[YV-K OFF veya nötr] → Kapak YERİNDE DURUR
```

### 4.2 SRP/CS mimarisi

| Blok | Bileşen | Emniyet rolü | MTTFd / B10d |
|------|---------|--------------|--------------|
| Giriş | XUK1 ARCNL2 | Algılama (reflektörlü) | **Bilinmiyor** — üretici verisi gerekli |
| Mantık | Standart PLC (konfigürasyona göre) | Sinyal işleme | **Standart PLC — emniyet için uygun değil** |
| Çıkış | YV-K (AIRTAC 4V230E-08) | Kapanmayı durdur | Kanıtlanmış emniyet prensibi değil |
| Geri besleme | Yok | — | — |

### 4.3 Kategori değerlendirmesi (mevcut)

| Kriter | Değerlendirme |
|--------|---------------|
| Tek kanal, standart PLC | **Kategori B veya en fazla 1** |
| Test (diagnostic) | Yok / bilinmiyor |
| Tek hata toleransı | Yok |
| Emniyet rölesi | **Yok** |
| **Tahmini PL** | **PL a veya PL b** (PLc altı) |

### 4.4 PLr vs PL karşılaştırma

| | Değer |
|---|-------|
| Gerekli | **PLr = d** |
| Mevcut (tahmini) | **PL a–b** |
| **Sonuç** | **✗ UYGUN DEĞİL** |

### 4.5 Konfig A — Gerekli iyileştirmeler (PLr = d hedefi)

| # | İyileştirme | Etki |
|---|-------------|------|
| 1 | Emniyet rölesi (ör. Pilz PNOZ) veya Safety PLC | Kategori 3/4 mimarisi |
| 2 | Çift kanal sensör veya test edilebilir emniyet sensörü | DC artışı |
| 3 | Emniyet çıkış + geri okuma (valf pozisyon) | Hata tespiti |
| 4 | Algılama → **geri açılma** (YV-A ON) | 6.3.5.3 uyumu + 10 J opsiyonu |
| 5 | Bypass tespiti / mühürlü bağlantı | Defeat önleme |

**Önerilen mimari (A+):**

```
[XUK1 sensör] → [Emniyet rölesi 2 kanal] → [Emniyet kontaktör + valf]
                      ↓ algılama
              [YV-K OFF + YV-A ON] → Geri açılma
```

---

## 5. SF1 detaylı analiz — Konfigürasyon B (Işık perdesi + Safety PLC)

### 5.1 Fonksiyon tanımı (mevcut)

```
[Çift el] → Kapak kapanma komutu → [YV-K ON]
    ↓
[F3SG ışık perdesi — 400 mm, Type 4] — ışın kesildi?
    ↓ EVET                          ↓ HAYIR
[G9SX Safety PLC OSSD]           [Kapanma devam]
    ↓
[Emniyet çıkış] → Kapanma durur (YV-K OFF / yerinde)
```

### 5.2 SRP/CS mimarisi

| Blok | Bileşen | Emniyet rolü | Veri |
|------|---------|--------------|------|
| Giriş | OMRON F3SG-44RE0880P14-L | Type 4 ışık perdesi | IEC 61496-3 |
| Mantık | OMRON G9SX G9SPN20S | Safety PLC | PL e/d tipik (üretici) |
| Çıkış | Emniyet rölesi / emniyet valf sürücü | Kapanma durdurma | Doğrulanacak |
| Mesafe | 50 mm (perde ↔ tehlike) | ISO 13855 | **Hesap gerekli** |

### 5.3 Kategori değerlendirmesi (tahmini)

| Kriter | Değerlendirme |
|--------|---------------|
| Type 4 perde + Safety PLC | **Kategori 4 mimarisi mümkün** |
| Tek hata toleransı | Safety PLC ile sağlanabilir |
| Diagnostic coverage (DC) | Yüksek (perde + PLC self-test) |
| **Tahmini PL (üretici verisi ile)** | **PL d — PL e** (G9SX tipik PL e/d) |

### 5.4 PLr vs PL karşılaştırma

| | Değer |
|---|-------|
| Gerekli | **PLr = d** |
| Mevcut (tahmini, validation öncesi) | **PL d** (üretici PL hesap dosyası ile doğrulanacak) |
| **Sonuç** | **△ KOŞULLU UYGUN** — validation + geri açılma eksik |

### 5.5 Konfig B — Açık noktalar

| # | Konu | Durum | Aksiyon |
|---|------|-------|---------|
| 1 | Stop time (F3SG → kapak durma) | Bilinmiyor | Saha ölçümü — ISO 13855 için kritik |
| 2 | ISO 13855 mesafe (50 mm) | Bildirilmiş | Resmi hesap: S = K×T + C |
| 3 | Geri açılma (6.3.5.3) | **Yok** | Safety PLC'de YV-A çıkışı tanımla |
| 4 | Muting / blanking | Bilinmiyor | Dokümante et |
| 5 | Validation (13849-2) | **Hayır** | Yazılım + donanım validation raporu |
| 6 | PFHd toplam | Bilinmiyor | G9SX + F3SG birleşik hesap |

### 5.6 ISO 13855 mesafe kontrolü (ön hesap)

**Formül:** S = (K × T) + C

| Parametre | Değer | Not |
|-----------|-------|-----|
| K (yaklaşma hızı) | 1600 mm/s | El/kol — varsayılan |
| T (toplam tepki süresi) | t_reaction + t_stop | **Ölçülecek** |
| C (penetrasyon) | 850 mm (Type 4, dikey) | IEC 61496 |
| S (min mesafe) | **Hesaplanacak** | Form: 50 mm — **doğrulanmalı** |

**Örnek (T = 0,3 s varsayım):** S = 1600×0,3 + 850 = **1330 mm** → Bildirilen 50 mm **yetersiz olabilir** — acil doğrulama gerekir.

> ⚠️ **Kritik:** 50 mm mesafe muhtemelen farklı bir referans noktasına aittir (perde alt kenarı ↔ kapak altı). ISO 13855 hesabı resmi yapılmalı.

---

## 6. SF2 / SF3 — Kapak kapalı sensörü (mekanik)

### 6.1 Fonksiyon tanımı

| Fonksiyon | Koşul | Çıkış |
|-----------|-------|-------|
| SF2 | Kapak kapalı ≠ ON | Cycle start engelle |
| SF3 | Kapak açıldı | Cycle stop |

### 6.2 Mevcut mimari

| Bileşen | Tip | Emniyet sınıfı |
|---------|-----|----------------|
| Kapak sensörü | Mekanik (limitswitch benzeri) | Standart |
| PLC girişi | Standart DI | Emniyet kanıtı yok |
| Guard locking | **Yok** | — |

### 6.3 PL değerlendirmesi

| | Değer |
|---|-------|
| PLr | **c** |
| Mevcut (tahmini) | **PL a–b** (standart PLC, tek kanal mekanik) |
| **Sonuç** | **✗ UYGUN DEĞİL** (PLr c için) |

### 6.4 Öneri

- Emniyet kapı switch (ISO 14119, en az 2 kodlu veya emniyet switch + Safety PLC)
- Veya: SF2/SF3'ü Safety PLC'ye taşı (Konfig B altyapısı ile)
- Guard locking gerekli değil (cycle kapalı sensör yeterli) — ancak **emniyet switch** PL c için şart

---

## 7. SF4 — Acil durdurma

| Parametre | Değer |
|-----------|-------|
| Konum | Elektrik panosu üzerinde |
| Etki | Valf de-energize |
| Reset | Prosedürlü |
| Kapak davranışı | **Yerinde kalır** (çek valf) |
| PLr | c |
| Mevcut (tahmini) | b–c (tek kanal kategori 0/1) |
| **Sonuç** | **△ Doğrulanmalı** — emniyet rölesi ile PL c sağlanabilir |

---

## 8. Emniyet fonksiyonları özet tablosu

| SF | Fonksiyon | PLr | Konfig A PL | Konfig B PL | Uygun? |
|----|-----------|-----|-------------|-------------|--------|
| SF1 | Kapanma algılama → dur/geri aç | **d** | a–b ✗ | d △ | B: koşullu |
| SF2 | Kapak kapalı → cycle lock | **c** | a–b ✗ | a–b ✗ | ✗ (her iki) |
| SF3 | Kapak açık → cycle stop | **c** | a–b ✗ | a–b ✗ | ✗ (her iki) |
| SF4 | Acil stop | **c** | b △ | b–c △ | △ |
| SF5 | Çift el kapak komutu | b | ? | ? | Ayrı analiz |

---

## 9. Güvenlik fonksiyonu spesifikasyonu (hedef — onay için)

### 9.1 SF1-HEDEF — Önerilen nihai fonksiyon

| Alan | Spesifikasyon |
|------|---------------|
| **Ad** | Kapak ezilme koruması — algılama ve geri açılma |
| **Giriş** | Type 4 ışık perdesi (F3SG) OSSD → G9SX |
| **Tetikleme** | Kapanma sekansı aktif AND perde ışını kesildi |
| **Emniyet durumu** | YV-K de-energize + **YV-A energize** → kapak yukarı |
| **Reset** | Manuel reset butonu; otomatik yeniden kapanma **YOK** |
| **Stop time** | ≤ [ölçülecek] ms (ISO 13855 hesabına girdi) |
| **PLr** | d |
| **Hedef PL** | d (minimum), e tercih |
| **Kategori** | 3 veya 4 |
| **Enerji limiti** | E_k ≤ 4 J (mevcut) veya ≤ 10 J (geri açılma ile) |

### 9.2 SF1-HEDEF — Pnömatik mantık (kritik)

```
ALGILAMA:
  YV-K = OFF (kapanma dur)
  YV-A = ON  (açma aktif — geri açılma)
  YV orta konum (E boşaltma) = KULLANMA ← 105 kg düşme riski

NORMAL KAPANMA:
  YV-K = ON, YV-A = OFF

ACİL STOP:
  YV-K = OFF, YV-A = OFF
  Çek valf → kapak yerinde
```

---

## 10. Validation planı (ISO 13849-2)

| # | Validation aktivitesi | Sorumlu | Durum |
|---|----------------------|---------|-------|
| V1 | Emniyet fonksiyon spesifikasyonu onayı | Mühendislik | Bu doküman |
| V2 | G9SX uygulama projesi (SOFTWARE validation) | Otomasyon | Bekliyor |
| V3 | F3SG montaj + mesafe (ISO 13855) | Montaj + Emniyet | Bekliyor |
| V4 | Stop time ölçümü | Test | Bekliyor |
| V5 | Fonksiyon testi (10 senaryo) | Test | Bekliyor |
| V6 | PFHd / PL hesap (üretici araçları) | Emniyet | Bekliyor |
| V7 | Validation raporu | QA | Bekliyor |

### 10.1 Fonksiyon test senaryoları (SF1)

| # | Senaryo | Beklenen sonuç |
|---|---------|----------------|
| T1 | Kapanma sırasında perde/sensör tetikle | Kapak durur + geri açar |
| T2 | Reset olmadan tekrar kapanma komutu | Kapanmaz |
| T3 | Reset sonrası çift el + kapanma | Normal kapanır |
| T4 | Perde arızası simülasyonu | Emniyet durumu |
| T5 | Acil stop kapanma sırasında | Valf de-energize, kapak kalır |
| T6 | Kapak tam kapanmadan cycle start | Cycle başlamaz (SF2) |
| T7 | Cycle sırasında kapak aç | Cycle durur (SF3) |
| T8 | Tek el butonu | Kapak hareket etmez |
| T9 | YV orta konum simülasyonu | Kapak düşmemeli |
| T10 | Bypass denemesi (A) | Tespit / engelleme |

---

## 11. Sonuç ve karar

### 11.1 Konfigürasyon A

| Kriter | Sonuç |
|--------|-------|
| SF1 PL ≥ PLr (d) | **✗ Hayır** |
| Validation | **✗ Yapılmadı** |
| **Karar** | **Red — seri üretim için uygun değil** |
| **Minimum iyileştirme** | Emniyet rölesi/PLC + geri açılma + validation |

### 11.2 Konfigürasyon B

| Kriter | Sonuç |
|--------|-------|
| SF1 PL ≥ PLr (d) | **△ Muhtemel** — üretici PL dosyası ile doğrula |
| SF2/SF3 PL ≥ PLr (c) | **✗ Hayır** — mekanik switch + standart PLC |
| ISO 13855 mesafe | **△ Doğrulanmalı** |
| Geri açılma | **✗ Eksik** |
| Validation | **✗ Yapılmadı** |
| **Karar** | **Koşullu — 4 aksiyon tamamlanınca kabul** |

### 11.3 Zorunlu aksiyonlar (Konfig B — seri üretim yolu)

1. **SF1 geri açılma** — Safety PLC programına YV-A çıkışı
2. **SF2/SF3 emniyet switch** — PL c mimarisi (G9SX girişi)
3. **ISO 13855 mesafe hesabı** — resmi rapor
4. **ISO 13849-2 validation** — yazılım + donanım
5. **Stop time ölçümü** — test raporu

---

## 12. PL karşılaştırma özeti (görsel)

```
PLr skalası:  a ─── b ─── c ─── d ─── e
                              ↑
                         SF1 hedef (d)

Konfig A SF1:  [a/b] ✗
Konfig B SF1:  [d/e] △ (validation bekliyor)
SF2/SF3:       [a/b] ✗ (her iki konfig)
SF4:           [b/c] △
```

---

## 13. Onay

| Rol | Ad Soyad | Tarih | İmza |
|-----|----------|-------|------|
| Hazırlayan | Fatih GÜRAL | 10.09.2026 | |
| Emniyet sorumlusu | | | |
| Onaylayan | | | |

---

*HTML rapor: [`KBN-ISO13849-Kapak-Risk-Degerlendirme.html`](KBN-ISO13849-Kapak-Risk-Degerlendirme.html) · ISO 12100: [`KBN-ISO12100-Kapak-Risk-Degerlendirme.html`](KBN-ISO12100-Kapak-Risk-Degerlendirme.html)*

*Referanslar: ISO 13849-1 Annex A (risk graph), ISO 13849-2 (validation), ISO 13855 (positioning), ISO 14119 (interlocking), IEC 61496-3 (Type 4 light curtain)*
