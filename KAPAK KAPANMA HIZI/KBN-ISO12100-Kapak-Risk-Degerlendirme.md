# KBN Serisi — ISO 12100 Kapak Risk Değerlendirmesi

**Standart:** BS EN ISO 12100:2010 — Safety of machinery — General principles for design — Risk assessment and risk reduction  
**Kapsam:** Dikey pnömatik kapak sistemi (açma/kapama, koruma, interlock) — **tüm KBN modelleri**  
**Kaynak veri:** `KBN-Risk-Degerlendirme-Bilgi-Formu.md` (10.09.2026)  
**Hazırlayan:** Makine Mühendisi Fatih GÜRAL  
**Durum:** Kapak odaklı tam değerlendirme — makine geneli için ayrı form doldurulacak

---

## 1. Doküman bilgileri

| Alan | Değer |
|------|-------|
| Makine | Kabinli endüstriyel parça yıkama makinesi — KBN serisi |
| Modeller | KBN 1B/2B 1500, 1650, 1850, 2050 + KBN 1350 |
| CE kapsamı | 2006/42/EC — Makine Direktifi |
| Önceki risk değerlendirmesi | Yok (ilk kapak odaklı değerlendirme) |
| İlgili standartlar | ISO 14120, ISO 14119, ISO 13855, ISO 13849-1, ISO 13850, ISO 4414, IEC 60204-1 |
| Referans dosyalar | `KBN-Adim0-Veri-Tablosu.html`, `KBN-piston-pnomatik-hat.html`, pnömatik/elektrik şemaları |

---

## 2. ISO 12100 süreci (Madde 4–7)

```
[Makine sınırları] → [Tehlike tanımlama] → [Risk tahmini] → [Risk değerlendirme]
        ↓
[Yeterli değil] → [6.2 Adım 1: Tasarım] → [6.3 Adım 2: Koruma] → [6.4 Adım 3: Bilgi]
        ↓
[Artık risk kabul edilebilir mi?] → [Evet → Dokümante et (Madde 7)]
```

Bu değerlendirme **iteratif** olarak kapak tehlikeleri için uygulanmıştır. Her koruma konfigürasyonu (A / B) ayrı satırda değerlendirilmiştir.

---

## 3. Madde 5.3 — Makine sınırları (kapak alt sistemi)

### 3.1 Amaçlanan kullanım

| Parametre | Tanım |
|-----------|-------|
| Fonksiyon | Endüstriyel parça yıkama kabininin dikey kapak ile kapatılması |
| Operatör görevi | Su ısıtma → parça yükleme → **çift el butonu** ile kapak komutu → start → yıkama → parça alma |
| Kapak hareketi | Çift el butonundan sonra **otomatik** açılır veya kapanır |
| Cycle koşulu | Yalnızca kapak **kapalıyken**; kapak açıkken cycle **asla** başlamaz |
| Bakım modu | Yok — enerji kesimi + **LOTO** prosedürü zorunlu |

### 3.2 Öngörülebilir amaç dışı kullanım

| Senaryo | Değerlendirme |
|---------|---------------|
| Kapak altına el/baş sokma | **Öngörülebilir** — operatör müdahalesi |
| El koruma sensörünü bypass | **Öngörülebilir** (Konfig A) — jumper/bypass mümkün |
| Işık perdesi bypass | **Öngörülebilir değil** (Konfig B) — Safety PLC mimarisi |
| Basınç regülatörü operatör ayarı | **Öngörülebilir** — kapanma hızı/kuvveti değişebilir |
| Throttle bypass | **Öngörülebilir değil** — mekanik ayar, operatör erişimi sınırlı |
| Bilinen saha kazası | Yok |

### 3.3 Kullanıcı profili

| Kullanıcı | Profil |
|-----------|--------|
| Operatör | Az deneyimli, endüstriyel ortam |
| Bakım personeli | Yetkili personel |
| Üçüncü taraf | Müşteriye bağlı (temizlik/servis) |
| Erişilebilirlik | Engel/kısıtlı hareket durumu dikkate alınmış |

### 3.4 Mekanik sınırlar

| Parametre | KBN 1350 | KBN 1650 | KBN 1850 | KBN 2050 |
|-----------|----------|----------|----------|----------|
| Toplam hareketli kütle (kg) | 65 | 85 | 95 | **105 ★** |
| Strok (mm) | 950 | 1200 | 1200 | 1200 |
| Piston | 2×Ø50 mm, 6 bar | aynı | aynı | aynı |
| Kabin açıklığı (mm) | — | — | — | 3000 |
| Kapak boyutları (U×G×K) | Bilinmiyor | — | — | — |

★ Worst-case enerji/hız hesapları **KBN-2050 (105 kg)** için yapılır.

### 3.5 Enerji arayüzleri

| Kaynak | Değer | Kapak etkisi |
|--------|-------|--------------|
| Pnömatik | 6 bar (regülatör; max 10 bar hat) | Kapak kuvveti ve hızı |
| Elektrik | 380 V / 50 Hz | Valf sürücü, PLC, koruma cihazları |
| Kontrol | Konfigürasyona göre standart PLC veya Safety PLC | Kapak sekansı, interlock |
| Acil stop | Valf de-energize | Kapak **yerinde kalır** (çek valf + tutma valfi) |

### 3.6 Yaşam döngüsü fazları — kapak riskleri

| Faz | Kapak ile ilgili risk |
|-----|----------------------|
| Transport / montaj | 65–105 kg kapak — ağırlık merkezi, kaldırma noktaları |
| Normal işletme | Ezilme, beklenmeyen hareket, sensör bypass |
| Ayar | Makinede ayar yok |
| Bakım / servis | LOTO uygulanmazsa makine çalıştırılabilir; kapak manuel valf tuşları ile hareket ettirilebilir |
| Arıza | Enerji kesilmeden müdahale → ani hareket |
| Hurda | Özel kapak riski yok |

---

## 4. Madde 5.4 — Tehlike tanımlama (kapak)

### 4.1 Tehlike envanteri

| # | Tehlike kategorisi | Tehlikeli durum | Tehlikeli olay | Ek B ref. |
|---|-------------------|-----------------|----------------|-----------|
| H1 | **Ezilme** | Kapak kapanırken açıklıkta el/vücut | Kapak ↔ kabin ağzı arasında sıkışma | Mekanik — crushing |
| H2 | **Kinetik enerji** | Hızlı kapanma (throttle ayarı kaybı, basınç artışı) | Yastıklama aşımı, yüksek darbe kuvveti | 6.2.3 b |
| H3 | **Beklenmeyen hareket — düşme** | Valf orta boşaltma (4V230E-E), acil stop sonrası basınç kaybı | 65–105 kg kapak aşağı kayma/düşme | 6.2.11, ISO 4414 |
| H4 | **Beklenmeyen hareket — devam** | Sensör tetiklenince kapak yerinde durur, basınç altında kalır | Ezilme devam eder (sıkışmış kişi) | 6.3.5.3 |
| H5 | **Enerji birikimi** | Bakımda basınç izole edilmeden müdahale | Ani kapak hareketi | 6.3.5.4 |
| H6 | **Koruma devre dışı** | El sensörü bypass (Konfig A) | H1 gerçekleşir | 5.5 defeat |
| H7 | **Ergonomi / elle müdahale** | Kapak söküldükten sonra manuel valf tuşları | Beklenmeyen hareket, elle sıkışma | 6.2 ergonomi |

**Kapsam dışı (bu dokümanda):** Döner sepet, elektrik, termal, kimyasal, gürültü — tam makine formunda değerlendirilecek.

### 4.2 Tehlikeli durum senaryoları

| Senaryo | Tetikleyici | Sonuç |
|---------|-------------|-------|
| S1 | Operatör parça yerleştirirken kapak kapanır | H1 — ezilme |
| S2 | Kapanma sırasında el koruma sensörü algılar | Kapak durur (Konfig A/B) — H4 riski (geri açılmıyor) |
| S3 | Işık perdesi algılar (Konfig B) | Kapak durur — H4 riski |
| S4 | Sensör bypass edilmiş (Konfig A) | H1 — tam ezilme riski |
| S5 | Acil stop | Valf de-energize, kapak kalır — H3 düşük (çek valf mevcut) |
| S6 | 4V230E orta konuma alınır (E boşaltma) | H3 — basınç kaybı, düşme riski |
| S7 | Bakımda LOTO yok | H5 — ani hareket |

---

## 5. Madde 5.5 — Risk tahmini

### 5.1 Değerlendirme yöntemi

ISO 12100 risk parametreleri: **Şiddet (S)**, **Maruziyet/Sıklık (F)**, **Kaçınma olasılığı (P)**.

| Parametre | Skala | Kapak ezilme (H1) açıklaması |
|-----------|-------|------------------------------|
| S — Şiddet | S1: hafif / S2: ciddi kalıcı / S3: ölüm | **S2** — 65–105 kg kapak, el/kol ezilmesi ciddi kalıcı yaralanma |
| F — Sıklık | F1: seyrek / F2: sık-günlük | **F2** — her cycle'da kapak kapanır |
| P — Kaçınma | P1: mümkün / P2: neredeyse imkânsız | **P2** — otomatik kapanma 8–12 s; algılama varsa P1'e yaklaşır |

### 5.2 Risk matrisi — başlangıç (koruma öncesi)

| Tehlike | S | F | P | Başlangıç riski | Not |
|---------|---|---|---|-----------------|-----|
| H1 Ezilme | S2 | F2 | P2 | **Yüksek** | Koruma olmadan kabul edilemez |
| H2 Kinetik enerji | S2 | F2 | P2 | **Orta-Yüksek** | Throttle + yavaş kapanma ile azaltılmış |
| H3 Düşme | S2 | F1 | P2 | **Orta** | Çek valf mevcut |
| H4 Sıkışma devamı | S2 | F2 | P2 | **Yüksek** | Geri açılma yok |
| H5 Bakım enerjisi | S2 | F1 | P1 | **Orta** | LOTO prosedürüne bağlı |
| H6 Bypass | S2 | F1 | P2 | **Yüksek** | Yalnızca Konfig A |
| H7 Manuel valf | S1 | F1 | P1 | **Düşük-Orta** | Bakım senaryosu |

---

## 6. Madde 5.6 — Risk değerlendirme (mevcut durum)

### 6.1 Konfigürasyon A — Reflektörlü el koruma sensörü (XUK1 ARCNL2)

| Tehlike | Mevcut önlemler | Değerlendirme | Azaltma gerekli? |
|---------|-----------------|---------------|------------------|
| H1 | Alt bölge sensör + kapanma throttle + çek valf | **Kabul edilebilir değil** — sensör bypass edilebilir; emniyet katmanı yok | **EVET** |
| H2 | Kısma vanası, 8–12 s kapanma, 6 bar limit | **Kısmen kabul** — 4 J hedefi doğrulanmalı | **EVET** (Adım 1 hesap) |
| H3 | PCV08G çek valf + tutma valfi | **Kabul edilebilir** — acil stop sonrası kapak kalır | Hayır |
| H4 | Sensör → yerinde dur | **Kabul edilebilir değil** — ISO 12100 6.3.5.3 geri hareket önerir | **EVET** |
| H6 | Sensör bypass mümkün | **Kabul edilebilir değil** | **EVET** |

**Konfig A genel sonuç:** Başlangıç riski **yeterince azaltılmamış**. Emniyet rölesi/Safety PLC olmadan PL hedefi karşılanamaz.

### 6.2 Konfigürasyon B — Işık perdesi (OMRON F3SG-44RE0880P14-L + G9SX G9SPN20S)

| Tehlike | Mevcut önlemler | Değerlendirme | Azaltma gerekli? |
|---------|-----------------|---------------|------------------|
| H1 | Tam boy perde (400 mm, mesafe 50 mm) + Safety PLC | **Kısmen kabul** — bypass zor; geri açılma yok | **EVET** (geri açılma + PL doğrulama) |
| H2 | Throttle + yavaş kapanma | **Kısmen kabul** — enerji limiti hesabı gerekli | **EVET** |
| H3 | Çek valf | **Kabul edilebilir** | Hayır |
| H4 | Perde → yerinde dur | **Kabul edilebilir değil** | **EVET** |
| H6 | Bypass zor (Safety PLC) | **Kabul edilebilir** (mimari uygun) | Hayır |

**Konfig B genel sonuç:** Koruma mimarisi Konfig A'ya göre **belirgin üstün**; ancak **geri açılma eksikliği** ve **PL validation** tamamlanmadan nihai kabul verilemez.

---

## 7. Madde 6 — Risk azaltma (üç adımlı yöntem)

### 7.1 Adım 1 — Doğası gereği güvenli tasarım (6.2)

| # | Önlem | ISO ref. | Mevcut durum | Etki | Aksiyon |
|---|-------|----------|--------------|------|---------|
| 1.1 | Kapanma hızı sınırlama (kısma vanası, D4 pilot) | 6.2.3 b | **Uygulanıyor** | H2 ↓ | 4 J hesabı ile doğrula (KBN-2050 worst-case) |
| 1.2 | Yastıklı piston, strok sonu emilim | 6.2.3 | **Uygulanıyor** | H2 ↓ | Yastıklama ayarı dokümante et |
| 1.3 | Basınç üst limiti (6 bar regülatör) | 6.2.11 | **Uygulanıyor** | H2 ↓ | Operatör ayarını kılavuzda yasakla/kilitle |
| 1.4 | Beklenmeyen düşüş önleme (çek valf PCV08G) | 6.2.11 | **Uygulanıyor** | H3 ↓ | — |
| 1.5 | Enerji limiti tasarım hedefi E_k ≤ 4 J | ISO 14120 §5.2.5.4 | **Hedef** | H1 ↓ | Adım 1 hesap: t_min = f(m, 4J) |
| 1.6 | E valf orta konum kullanımından kaçınma | 6.2.11 | **Kısmen** | H3 ↓ | Güvenlik fonksiyonunda E merkeze **gitme** |

**Adım 1 hedef kapanma süresi (4 J, teorik):**

| Model | m (kg) | v_max = √(8/m) (m/s) | Strok (mm) | t_ISO (s) |
|-------|--------|----------------------|------------|-----------|
| KBN-1350 | 65 | 0,35 | 950 | 2,7 |
| KBN-1650 | 85 | 0,31 | 1200 | 3,9 |
| KBN-1850 | 95 | 0,29 | 1200 | 4,1 |
| KBN-2050 | 105 | 0,28 | 1200 | **4,3** |

Mevcut 8–12 s >> t_ISO → **Adım 1 enerji limiti karşılanıyor** (doğrulama ölçümü önerilir).

### 7.2 Adım 2 — Koruyucu tedbirler (6.3)

| # | Önlem | ISO ref. | Konfig A | Konfig B | Durum |
|---|-------|----------|----------|----------|-------|
| 2.1 | Power-operated guard (pnömatik kapak) | ISO 14120 | ✓ | ✓ | Mevcut |
| 2.2 | Hassas koruyucu ekipman (SPOC) | 6.3.2.5 | El sensörü (kısmi alan) | Işık perdesi (tam alan) | Mevcut |
| 2.3 | Kapak kapalı sensörü (mekanik) | ISO 14119 | ✓ | ✓ | Mevcut — interlock değil |
| 2.4 | Guard locking | ISO 14119 | ✗ | ✗ | Yok — cycle kapalı sensör ile |
| 2.5 | Çift el kontrol (kapak komutu) | ISO 13851 | ✓ (planlı/mevcut) | ✓ | Operatör kasıtlı komut |
| 2.6 | Emniyet-related kontrol sistemi | ISO 13849-1 | **Yok** (standart PLC) | **Safety PLC** | B üstün |
| 2.7 | Algılama → geri açılma | 6.3.5.3 | ✗ (yerinde dur) | ✗ (yerinde dur) | **Eksik — öncelikli** |
| 2.8 | Otomatik yeniden kapanma yasağı | ISO 14119 | ✓ | ✓ | Reset gerekli |
| 2.9 | ISO 13855 mesafe (perde) | ISO 13855 | n/a | 50 mm — **doğrulanmalı** | Hesap gerekli |

### 7.3 Adım 3 — Bilgilendirme (6.4)

| # | Gereksinim | Durum | Aksiyon |
|---|------------|-------|---------|
| 3.1 | Kullanım kılavuzunda kapak güvenliği | **Mevcut** | — |
| 3.2 | Basınç/kapanma süresi fabrika ayarı | **Mevcut** | Müşteri değiştirmemeli |
| 3.3 | Bakımda pnömatik izolasyon talimatı | **Eksik** | LOTO prosedürü ekle |
| 3.4 | Artık riskler listesi | **Mevcut** | Kapak bölümünü güncelle |
| 3.5 | Uyarı işaretleri / ikaz lambası | **Mevcut** | Kırmızı/yeşil/sarı tepe lambası |
| 3.6 | Kaldırma noktaları (65–105 kg) | **Mevcut** | Kapak her iki yanı |

### 7.4 Tamamlayıcı koruma (6.3.5)

| Madde | Gereksinim | KBN durumu | Değerlendirme |
|-------|------------|------------|---------------|
| 6.3.5.2 | Acil durdurma (ISO 13850) | Pano üzerinde, reset prosedürlü | ✓ Uygun |
| 6.3.5.3 | Sıkışma → geri hareket | **Yok** — yerinde dur | ✗ **Uygun değil** |
| 6.3.5.4 | Enerji izolasyon + boşaltma | LOTO; otomatik boşaltma yok | Kısmen — talimat eksik |
| 6.3.5.5 | Ağır parça taşıma | Kaldırma noktaları mevcut | ✓ |

---

## 8. Risk azaltma sonrası değerlendirme

### 8.1 Hedef durum (önerilen)

| Tehlike | Hedef önlem | Hedef risk |
|---------|-------------|------------|
| H1 | Perde/sensör + geri açılma + PL≥d + E_k≤4J | **Düşük — kabul edilebilir** |
| H2 | Throttle + 8–12 s + yastıklama + ölçüm | **Düşük** |
| H3 | Çek valf + güvenlik fonksiyonunda E kullanmama | **Düşük** |
| H4 | Algılama → **açma valfi ON** (geri açılma) | **Düşük** |
| H6 | Safety PLC + tam alan perde (Konfig B) | **Düşük** |

### 8.2 Artık riskler (residual risks)

| # | Artık risk | Maruziyet | Azaltma / bilgilendirme |
|---|------------|-----------|-------------------------|
| R1 | Konfig A'da sensör bypass | Bakım/kötü niyet | Konfig B'ye geçiş veya emniyet rölesi zorunlu |
| R2 | Regülatör operatör ayarı | Basınç artışı → hızlanma | Mühürleme / kılavuz uyarısı |
| R3 | Bakımda LOTO ihmal | Ani hareket | Talimat + eğitim |
| R4 | Sıcak buhar (kapak açılınca) | Operatör | Egzoz fanı — tam makine değerlendirmesinde |
| R5 | Kapak sökümünde manuel valf | Bakım personeli | LOTO + prosedür |
| R6 | 4 J ölçümü yapılmadı | Teorik uygunluk | Saha test raporu |

---

## 9. Sonuç ve karar

### 9.1 Konfigürasyon A — El sensörü

| Kriter | Sonuç |
|--------|-------|
| Adım 1 (tasarım) | **Uygun** (teorik 4 J; ölçüm önerilir) |
| Adım 2 (koruma) | **Yetersiz** — emniyet katmanı yok, bypass mümkün, geri açılma yok |
| Adım 3 (bilgi) | **Kısmen uygun** — bakım talimatı eksik |
| **Genel karar** | **Risk yeterince azaltılmamış** — seri üretim için **önerilmez** (iyileştirme zorunlu) |

**Zorunlu aksiyonlar (A):**
1. Emniyet rölesi veya Safety PLC ekle
2. Algılama → geri açılma fonksiyonu uygula
3. ISO 13849 PL validation yap
4. 4 J kapanma enerjisi saha ölçümü

### 9.2 Konfigürasyon B — Işık perdesi + Safety PLC

| Kriter | Sonuç |
|--------|-------|
| Adım 1 (tasarım) | **Uygun** (teorik) |
| Adım 2 (koruma) | **Kısmen uygun** — mimari doğru; geri açılma ve ISO 13855 mesafe eksik |
| Adım 3 (bilgi) | **Kısmen uygun** |
| **Genel karar** | **Koşullu kabul** — geri açılma eklenip PL validation tamamlandığında kabul edilebilir |

**Zorunlu aksiyonlar (B):**
1. Algılama → açma valfi ON (geri açılma) — **öncelik 1**
2. ISO 13855 mesafe hesabı (50 mm doğrula)
3. ISO 13849-2 validation
4. Stop time ölçümü (perde → kapak durma)

### 9.3 Öncelik sıralaması

| Öncelik | Aksiyon | Standart |
|---------|---------|----------|
| P1 | Geri açılma güvenlik fonksiyonu | ISO 12100 6.3.5.3, ISO 14120 |
| P2 | PL validation (Konfig B) | ISO 13849-1/2 |
| P3 | 4 J enerji ölçümü | ISO 14120 |
| P4 | Konfig A emniyet mimarisi | ISO 13849-1 |
| P5 | Bakım LOTO talimatı | ISO 12100 6.4, ISO 14118 |

---

## 10. Madde 7 — Dokümantasyon checklist

| # | Gereksinim (12100 §7) | Dosya | Durum |
|---|----------------------|-------|-------|
| a | Makine tanımı, limitler | Bu doküman §3, Adım 0 tablosu | ✓ |
| b | Varsayımlar (kütle, basınç) | Adım 0 + form | ✓ |
| c | Tehlikeler, tehlikeli durumlar | §4 | ✓ |
| d | Risk veri kaynağı | Form + saha (kaza yok) | ✓ |
| e | Koruyucu önlem hedefleri (PLr) | `KBN-ISO13849-Kapak-Risk-Degerlendirme.md` | ✓ |
| f | Uygulanan önlemler | Pnömatik/elektrik şema | ✓ |
| g | Artık riskler | §8.2 | ✓ |
| h | Sonuç | §9 | ✓ |

---

## 11. Onay

| Rol | Ad Soyad | Tarih | İmza |
|-----|----------|-------|------|
| Hazırlayan | Fatih GÜRAL | 10.09.2026 | |
| Onaylayan | | | |
| Gözden geçiren (Emniyet) | | | |

---

*HTML rapor: [`KBN-ISO12100-Kapak-Risk-Degerlendirme.html`](KBN-ISO12100-Kapak-Risk-Degerlendirme.html) · Sonraki: [`KBN-ISO13849-Kapak-Risk-Degerlendirme.md`](KBN-ISO13849-Kapak-Risk-Degerlendirme.md) · Tam makine formu: [`KBN-Tam-Makine-Risk-Degerlendirme-Bilgi-Formu.md`](KBN-Tam-Makine-Risk-Degerlendirme-Bilgi-Formu.md)*
