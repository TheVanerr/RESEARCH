# KBN Serisi — ISO 12100 Risk Değerlendirme Bilgi Formu

Bu form **BS EN ISO 12100:2010** (Madde 5.2, 5.3, 5.4) kapsamında risk değerlendirmesi için gereken bilgileri toplar.

**Nasıl kullanılır:** `[CEVAP]` satırlarına yazın. Bilmiyorsanız `BİLİNMİYOR` yazın. Bölüm atlamayın.

**Referans dosyalar:** Adım 0 verileri önceden doldurulmuş alanlarda özetlenmiştir — yanlışsa düzeltin.

---

## A. Genel tanım

| Soru | Cevap |
|------|-------|
| Değerlendirme kapsamı (hangi modeller?) | `KBN 1B 1350, KBN 1B 1500, KBN 2B 1500, KBN 1B 1650, KBN 2B 1650, KBN 1B 1850, KBN 2B 1850, KBN 1B 2050, KBN 2B 2050`|
| Risk değerlendirmesini yapan kişi / ekip | `Makine Mühendisi Fatih GÜRAL` |
| Tarih | `10.09.2026` |
| Makine tipi / ticari adı | `Kabinli Yıkama Makinesi` — örn. Kabin tipi yıkama makinesi |
| Makine direktifi / CE kapsamı | `EVET` — 2006/42/EC evet/hayır |
| Daha önce yapılmış risk değerlendirmesi var mı? | `YOK` — varsa dosya adı / tarih |

---

## B. Madde 5.3 — Makine sınırları

### B.1 Amaçlanan kullanım (intended use)

| Soru | Cevap |
|------|-------|
| Makinenin bir cümlelik amacı | `Endüstriyel Parça Yıkama` |
| Operatörün tipik görevleri (günlük) | `Makine suyunu ısıtıp, parçayı yükleyip, kapağı kapatıp start butonuna basmak. Yıkama bitince parçayı alıp yenisini koymak.` |
| Kapak açma/kapama operatör tarafından mı, otomatik mi? | `Çift el butonu olacak. Butonlara bastıktan sonra otomatik açılacak ya da kapanacak` |
| Yıkama cycle'ı kapak kapalıyken mi çalışır? | `EVET, AKSİ MÜMKÜN DEĞİLDİR` |
| Kapak açıkken cycle başlatılabilir mi? | `ASLA` |
| Bakım modu var mı? Nasıl seçilir? | `YOK. MAKİNE ENERJİSİNİ KESİP LOTO PROSEDÜRÜNÜ UYGULAYIP BAKIM YAPILACAK.` |

### B.2 Öngörülebilir amaç dışı kullanım (reasonably foreseeable misuse)

| Soru | Cevap |
|------|-------|
| Kapak altına el/baş sokma ihtimali | `EVET` |
| Throttle / flow control bypass edilebilir mi? | `HAYIR` |
| Basınç regülatörü ayarı operatör tarafından değiştirilebilir mi? | `EVET` |
| Koruyucu sensör/perde devre dışı bırakılabilir mi? (jumper, bypass) | `EL KORUMA SENSÖRÜ VARSA BIRAKILABİLİR ANCAK IŞIK PERDESİ VARSA BIRAKILAMAZ.` |
| Bilinen saha kazası / near-miss var mı? | `HAYIR` |

### B.3 Kullanıcı profili

| Soru | Cevap |
|------|-------|
| Operatör eğitim seviyesi | `AZ DENEYİMLİ` — endüstriyel / az deneyimli |
| Bakım personeli | `YETKİLİ PERSONEL` |
| Üçüncü taraf (temizlik, servis) erişimi | `MÜŞTERİYE BAĞLI` |
| Engel / kısıtlı hareket durumu düşünüldü mü? | `EVET` |

### B.4 Mekansal ve teknik sınırlar

| Soru | Cevap |
|------|-------|
| Modeller ve boy kodları | **1B/2B: 1500, 1650, 1850, 2050 + KBN 1350** — doğru mu? `EVET` |
| Toplam hareketli kütle (kg) | **1350:65 / 1500:75 / 1650:85 / 1850:95 / 2050:105** — doğru mu? `EVET` |
| Strok (mm) | **1350:950 / 1500:950 / diğerleri:1200** — doğru mu? `EVET` |
| Piston | **2×Ø50 mm, 6 bar** — doğru mu? `EVET` |
| Kapak boyutları (U×G×K mm) — her boy için | `YOK` |
| Kabin açıklık boyutu (mm) | `3000` |
| Makine kurulum yeri (iç mekân / nem / sıcaklık) | `İÇ MEKAN` |

### B.5 Enerji kaynakları

| Soru | Cevap |
|------|-------|
| Pnömatik basınç (bar) | **6 bar** — doğru mu? `EVET` |
| Kompresör kapasitesi (tipik / min müşteri) | `BİLMİYORUM STANDARTA GÖRE HESAPLANACAK` NL/dk veya m³/dk |
| Elektrik besleme (V, faz) | `380V / 50HZ` |
| Kontrol: standart PLC / Safety PLC / röle | `KONFİGÜRASYONA GÖRE` — konfigürasyona göre |
| Acil stop tipi ve etkisi | `VALFLERDEKİ ENERJİNİN KESİLMESİ GEREKİYOR` — valfler de-energize oluyor mu? |

### B.6 Yaşam döngüsü fazları

| Faz | Özel risk / not |
|-----|-----------------|
| Transport / montaj | `AĞIRLIK MERKEZİ ORTADA TAŞINIRKEN BUNA DİKKAT EDİLMELİ.` |
| Normal işletme | `KULLANIM AMACINA VE GÜVENLİK KURALLARINA UYARSA YOK` |
| Ayar / teaching | `MAKİNEDE GEREKEN HERHANGİ BİR AYAR BULUNMAMAKTADIR` |
| Bakım / servis | `OPERATÖR MAKİNE İÇİNE GİRERSE VE LOTO PROSEDÜRÜ UYGULANMAMIŞSA MAKİNE ÇALIŞTIRILABİLİR.` |
| Arıza / müdahale | `ENERJİ KESİLİP LOTO PROSEDÜRÜ UYGULANMADIYSA MAKİNE ÇALŞTIRILABİLİR.` |
| Hurda / söküm | `YOK` |

---

## C. Madde 5.4 — Tehlike envanteri (KBN'ye özel)

Her satır için: **Var / Yok / BİLİNMİYOR** ve kısa açıklama.

### C.1 Mekanik tehlikeler

| Tehlike | Var mı? | Tehlikeli durum / olay | Not |
|---------|---------|------------------------|-----|
| Ezilme (kapak ↔ kabin ağzı) | `[YOK]` | `[KAPAK KAPANIRKEN ELİNİ KOYARSA SENSÖR GÖRECEİ İÇİN KAPAK DURUR. TEK TEHLİKELİ DURUM EL KORUMA SENSÖRÜNÜ BYPASS EDERSE BU TEHLİKEYİ YAŞAR]` | |
| Kesme / sıkışma (piston-yan guide) | `[YOK]` | ` ` | |
| Düşen kapak (valf boşaltma / acil stop) | `[YOK]` | `[KAPAKLARDA PNOMATİK ÇEKVALF VAR. KAPAK DÜŞME TEHLİKESİNİ DURDURUYOR.]` | |
| Kinetik enerji (hızlı kapanma) | `[YOK]` | `[KISMA VANASI İLE KAPAK HIZI AYARLANIYOR]` | |
| Erişilebilir hareketli parçalar (döner tabla) | `[VAR]` | `DÖNER SEPET VAR. KAPAK AÇIKKEN OTOMATİK DÖNMÜYOR SEPET TEST BUTONUNA BASILDIĞI SÜRECE DÖNÜYOR.` | |
| Yüksek basınçlı hortum patlaması | `[YOK]` | `[HORTUMLARDA MAKS 6 BAR BASINÇ VAR. BU DA BÜYÜK BİR PATLAMADAN ZİYADE HAVA KAÇAĞINA SEBEP OLUR]` | |

### C.2 Diğer tehlike kategorileri (varsa işaretleyin)

| Kategori | İlgili mi? | Açıklama |
|----------|------------|----------|
| Elektrik (IEC 60204-1) | `[VAR]` | `[CEVAP]` |
| Termal (sıcak yüzey, buhar) | `[VAR]` | `[MAKİNE DIŞ YÜZEYİNDEKİ BELİRLİ NOKTALAR 40 DERECEYE ULAŞABİLİYOR. AYRICA KAPAK AÇILDIĞINDA SICAK BUHAR ATIYOR. BUNUN İÇİN EGZOS FANI KOYULUYOR.]` |
| Kimyasal (deterjan, buhar) | `[VAR]` | `[ALKALİ BAZLI DETERJANLAR KULLANILIYOR.]` |
| Gürültü / titreşim | `[VAR]` | `[MAKS 65 DB]` |
| Kaygan zemin / su sıçraması | `[VAR]` | `[ÇOK DÜŞÜK İHTİMALLE MAKİNEDEN 1 2 DAMLA SU ÇEVREYE GİDEBİLİR. BU DA KAYMAYA SEBEP OLABİLİR AMA ÇOK DÜŞÜK İHTİMAL.]` |
| Ergonomi (kapak manuel müdahale) | `[VAR]` | `[KAPALI MUHAFAZA İÇERİSİNDE VALFLER VAR. KAPAK SÖKÜLDÜKTEN SONRA BU VALFLERİN MANUEL TUŞLARINA BASILARAK MÜDAHALE EDİLEBİLİR.]` |

---

## D. Kapak & pnömatik sistem (detay)

### D.1 Hareket

| Soru | Cevap |
|------|-------|
| Kapanmada beslenen port | **Alt port** — doğru mu? `EVET` |
| Açılmada beslenen port | **Üst port** — doğru mu? `EVET` |
| Mevcut kapanma süresi (s) | **8–12** — tipik ayar? `EVET` |
| Mevcut açılma süresi (s) | `8-12` |
| Hat üzerinde throttle / flow control var mı? | `KAPANMA HATTINDA VAR` — konum, ayar aralığı |
| Çek valf marka/model | `AIRTAC PCV08G 06-K-Z` |
| Çek valf iğne ayarı (açıklama / foto) | `BİLİNMİYOR` |
| Silindir yastıklama ayarı | `YARIM TUR AÇILIYOR TAM SIKILIP` |

### D.2 Hortum & valf

| Soru | Cevap |
|------|-------|
| Esas hat | **D8 × 4 m × 2 piston** — doğru mu? `EVET` |
| Pilot/plot hat | **D4 dirsek** — doğru mu? `EVET` |
| Kapama valfi | **AIRTAC 4V230E-08** — doğru mu? `EVET` |
| Açma valfi | `AIRTAC 4V230E-08` |
| Valf orta konum | **Boşaltma (E)** — doğru mu? `EVET` |
| Hat-PID veya pnömatik şema dosyası var mı? | `VAR` — varsa dosya adı |

*(Pnömatik hat şeması: `KBN-piston-pnomatik-hat.html`)*

---

## E. Koruyucu önlemler — iki konfigürasyon

### E.1 Konfigürasyon A — Reflektörlü el koruma sensörü

| Soru | Cevap |
|------|-------|
| Sensör marka / model | `SENSÖR XUK1 ARCNL2` |
| Korunan alan (mm veya foto) | `alt dar bölge` — alt dar bölge |
| Emniyet rölesi / Safety PLC | **Yok (mevcut)** — doğru mu? `YOK` |
| Normal PLC giriş tipi (PNP/NPN, 24V) | `24V` |
| Sensör tetiklenince kapak davranışı | `bilinmiyor` — dur / geri aç / bilinmiyor |
| Cycle reset prosedürü | `yok` |
| Kapak tam kapanmadan interlock ON olur mu? | `HAYIR` |

### E.2 Konfigürasyon B — Işık perdesi

| Soru | Cevap |
|------|-------|
| Perde marka / model / tip (Type 2/4?) | `OMRON F3SG-44RE0880P14-L` |
| Safety PLC marka / model | `OMRON G9SX G9SPN20S` |
| PL hedefi veya mevcut PL (biliyorsanız) | `BİLİNMİYOR` |
| Perde ile tehlike bölgesi arası mesafe (mm) | `50` |
| Perde yüksekliği / koruma alanı | `400mm` |
| Sensör tetiklenince kapak davranışı | **Geri açılma yok (mevcut)** — doğru mu? `EVET, YERİNDE DURUYOR` |
| Otomatik yeniden kapanma var mı? | `YOK` |
| Muting / blanking kullanılıyor mu? | `BİLİNMİYOR` |

### E.3 Ortak interlock

| Soru | Cevap |
|------|-------|
| Kapak kapalı sensörü (mekanik / manyetik / proximity) | `MEKANİK` |
| Guard locking (kilitli kapak) var mı? | `YOK` |
| Kapak kapalı + kilitli olmadan cycle başlar mı? | `HAYIR` |
| Kapak açılınca cycle durur mu? (stop time ms) | `EVET` |

---

## F. Madde 6 — Mevcut koruyucu önlemler

### F.1 Adım 1 — Doğası gereği güvenli tasarım (6.2)

| Önlem | Uygulanıyor mu? | Detay |
|-------|-----------------|-------|
| Kapanma hızı sınırlama (throttle / çek valf) | `[EVET]` | `KISMA VANASI VAR` |
| Yastıklama / strok sonu emilim | `[EVET]` | `YASTIKLI PİSTON TERCİH EDİLİYOR` |
| Basınç üst limiti (regülatör) | `[EVET]` | `[6 BAR AYARLANIYOR AMA MAKS 10 BAR]` |
| Beklenmeyen düşüş önleme (E valf riski) | `[EVET]` | `[PNOMATİK ÇEKVALF VAR + PİSTON GİRİŞİNDE PLOT HATTI VAR + VALFLER ELEKTRİK KESİLDİĞİNDE İÇERİDEKİ HAVAYI TUTAN EGZOS TİPİ VALF]` |

### F.2 Adım 2 — Koruyucu tedbirler (6.3)

| Önlem | Uygulanıyor mu? | Detay |
|-------|-----------------|-------|
| Hareketli kapak (power-operated guard) | `[ ]` | `[CEVAP]` |
| Hassas koruyucu ekipman (A veya B) | `[ ]` | `[CEVAP]` |
| Interlock (ISO 14119) | `[HAYIR]` | `[KAPAKTA İNTERLOCK SİSTEMİ BULUNMAMAKTADIR.]` |
| ISO 14120 enerji limiti (4 J hedef) | `[BİLİNMİYOR]` | `[CEVAP]` — ölçüldü mü? |

### F.3 Tamamlayıcı önlemler (6.3.5)

| Önlem | Uygulanıyor mu? | Detay |
|-------|-----------------|-------|
| Acil stop (ISO 13850) | `[EVET]` | `[ELEKTRİK PANOSU ÜZERİNDE, RESET PROSEDÜRÜ DE İÇERİYOR]` — konum, reset |
| Sıkışma → geri hareket (6.3.5.3) | `[ ]` | `[CEVAP]` |
| Bakımda basınç boşaltma (6.3.5.4) | `[HAYIR]` | `[OLMAMASI DAHA İYİ OLABİLİR]` |
| Uyarı işaretleri / ikaz lambası | `[EVET]` | `[MAKİNEDE ARIZA OLDUĞUNDA TEPE LAMBASI KIRMIZI YANAR, ÇALIŞIRKEN YEŞİL YANAR, HAZIRLIK TAMAMLANDIĞINDA SARI YANAR]` |
| Kaldırma noktaları (kapak 65–105 kg) | `[EVET ]` | `[KAPAĞIN HER İKİ YANI]` |

### F.4 Kullanım bilgisi (6.4)

| Soru | Cevap |
|------|-------|
| Kullanım kılavuzunda kapak güvenliği anlatılıyor mu? | `EVET` |
| Kapanma süresi / basınç ayarı kılavuzda var mı? | `BASINÇ AYARI VE KAPANMA SÜRESİ FABRİKADA BİR KEZ YAPILIP GÖNDERİLİYOR. TEKRAR AYARA GEREK YOK.` |
| Bakım talimatında pnömatik izolasyon adımları | `YOK` |
| Artık riskler (residual risks) listelenmiş mi? | `EVET` |

---

## G. Performans seviyesi (ISO 13849-1) — 12100 sonrası

| Soru | Cevap |
|------|-------|
| Kapak ezilme için hedef PLr (d/e?) | `BİLİNMİYOR` — bilmiyorsanız BİLİNMİYOR |
| Güvenlik fonksiyonları listesi | `ACİL STOP, KAPAK KAPALI SENSÖRÜ, IŞIK PERDESİ VE YA EL KORUMA SENSÖRÜ` — örn. S1: kapak kapanırken perde → stop |
| Her fonksiyon için mevcut PL / SIL | `BİLİNMİYOR` |
| Validation yapıldı mı? (13849-2) | `HAYIR` |

---

## H. Ekler (varsa dosya adını yazın)

| Ek | Dosya / açıklama |
|----|------------------|
| Pnömatik şema | `EVET` |
| Elektrik şema (kapak devresi) | `EVET` |
| PLC program özeti (kapak + güvenlik) | `EVET` |
| Saha fotoğrafları | `EVET` |
| Önceki risk değerlendirme raporu | `EVET` |
| Test raporu (kapanma süresi ölçümü) | `EVET` |

---

## I. Öncelikli cevaplar (minimum set)

Risk değerlendirmesine başlamak için **en az** şunlar gerekli:

1. `[HAYIR]` Kapak tam kapanmadan cycle başlıyor mu?
2. `[YERİNDE DURUYOR]` Her iki koruma konfigürasyonunda (A/B) sensör tetiklenince kapak ne yapıyor?
3. `[YOK]` Interlock sensör tipi ve konumu
4. `[VAR, PİSTON ALTINDA KAPANMAYI SAĞLAYAN KISMIN ÇEKVALFİNDE]` Throttle / flow control var mı, nerede?
5. `[KALIR]` Acil stop sonrası kapak davranışı (düşer / kalır / yavaş iner)
6. `[BOŞALTILMIYOR]` Bakımda basınç nasıl boşaltılıyor?
7. `[YOK]` Bilinen kaza / şikayet / servis notu
8. `[BİLİNMİYOR]` Hedef veya mevcut PL (biliyorsanız)

---

*Form doldurulduktan sonra: `KBN-ISO12100-Risk-Degerlendirme.html` tam risk değerlendirme raporuna dönüştürülecek.*
