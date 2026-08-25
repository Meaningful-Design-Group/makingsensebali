[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# DIY Node V2 — node segitiga yang ringkas

*Making Sense Bali · Chapter Fab City Bali · dibangun dan diuji di Fab Lab Bali*

**Seeed Studio XIAO ESP32-C3 + Seeed Grove HM3301 + Bosch BME680**, ketiganya diletakkan sejajar di satu lantai sasis di dalam cangkang segitiga hasil cetak 3D. Dibangun untuk menempatkan node pemantau kualitas udara ambien pada skala banjar, sekolah, dan warung di Desa Serangan dengan biaya kira-kira seharga sebuah ponsel.

> **Status: dibangun, dipasang, dievaluasi di lapangan, dan digantikan oleh hasilnya sendiri.**
> Dua dari tiga sasaran rancangan tercapai. Yang ketiga tidak: sasis memanaskan sensor suhunya
> sendiri, dan lubang masuk udara di bagian bawah terlambat menangkap puncak polusi yang nyata.
> **Jangan cetak cangkang ini untuk penerapan di lapangan.** Baca dulu
> [Evaluasi](#evaluasi--apa-yang-ditunjukkan-uji-lapangan), lalu bangun
> [sasis pine cone](../enclosure/) sebagai gantinya. Folder ini disimpan karena rancangan yang
> gagal dengan dua alasan yang bisa disebutkan namanya lebih berharga bagi pembangun berikutnya
> daripada rancangan yang sekadar berhasil.

> **Soal penamaan, supaya tidak ada yang kehilangan sehari karenanya.** "V2" di sini adalah
> generasi kedua dari *node secara keseluruhan* menurut penomoran Fab Lab Bali. Ini **bukan**
> `enclosure/archive/v2-lantern/`, yang merupakan garis keturunan sasis yang terpisah
> (v1-box → v2-lantern → v3-gourd → v4-column → v5 pine cone). Dua jalur rancangan yang berbeda,
> dua sistem penomoran yang berbeda. Elektronik dan firmware-nya sama; cangkangnya tidak berkaitan.

![Tampilan terurai rakitan Node V2](img/01-exploded-view.png)

## Daftar isi

- [Mengapa dibangun](#mengapa-dibangun)
- [Konsep](#konsep)
- [Dari mana bentuknya berasal](#dari-mana-bentuknya-berasal)
- [Arsitektur fisik dan aliran udara](#arsitektur-fisik-dan-aliran-udara)
- [Elektronik](#elektronik)
- [Bill of materials](#bill-of-materials)
- [Custom mainboard](#custom-mainboard)
- [Tata letak internal](#tata-letak-internal)
- [Pelat bawah — daya, RF, udara](#pelat-bawah--daya-rf-udara)
- [Perakitan](#perakitan)
- [Firmware dan alur data](#firmware-dan-alur-data)
- [Evaluasi — apa yang ditunjukkan uji lapangan](#evaluasi--apa-yang-ditunjukkan-uji-lapangan)
- [Apa yang harus dilakukan V3 secara berbeda](#apa-yang-harus-dilakukan-v3-secara-berbeda)
- [Berkas](#berkas)
- [Apa yang masih kurang dari dokumentasi ini](#apa-yang-masih-kurang-dari-dokumentasi-ini)

## Mengapa dibangun

Stasiun pemantau kualitas udara kelas rujukan harganya jauh di atas kemampuan banjar, sekolah, atau kelompok warga mana pun di Bali untuk mengumpulkannya secara swadaya. Tabel tier kampanye ini sendiri menaruhnya di [USD 5.000–25.000+](../README.id.md#di-mana-ini-cocok--tier-sensor-kampanye). Merakit sendiri dari sensor modular murah adalah alternatif yang jelas, dan itulah isi seluruh pohon folder ini.

Bagian yang sulit bukan elektroniknya. Melainkan kotaknya.

Casing yang bentuknya dirancang sembarangan berubah menjadi jebakan: ia mengurung panas buangan mikroelektronika di dalam, atau ia mencekik udara luar sebelum sampai ke sensor. Apa pun yang terjadi, node melaporkan angka yang menggambarkan bagian dalam sebuah cangkang plastik, bukan udara tempat ia digantung — dan ia melaporkannya dengan presisi yang sama meyakinkannya dengan pembacaan yang benar. Justru itulah yang membuat kegagalan ini berbahaya, bukan sekadar menjengkelkan.

| | |
|---|---|
| Stasiun rujukan tetap | ![Stasiun pemantau rujukan tetap](img/02-ref-station-fixed.png) |
| Stasiun rujukan bergerak | ![Stasiun pemantau kualitas udara bergerak](img/03-ref-station-mobile.png) |

## Konsep

Sasis horizontal yang kompak. Semua komponen diletakkan mendatar di satu lantai sasis dalam **konfigurasi sejajar (side-by-side)**, dipisahkan oleh sekat pembatas di dalam, sehingga alat tetap cukup kecil untuk dibawa dengan satu tangan dan cukup rapi untuk digantung di dinding milik orang lain.

Tiga sasaran ditetapkan di awal:

1. Memotong biaya produksi hingga ~90% dibandingkan stasiun standar industri.
2. Menghasilkan cangkang yang kokoh, ringkas, mudah dicetak dengan 3D printer lokal, dan aman dari cipratan air.
3. Mendapatkan pembacaan parameter lingkungan harian yang presisi.

Sasaran 1 dan 2 tercapai. Sasaran 3 tidak — lihat evaluasi.

> **Tentang angka 90%.** Dokumen sumber menyebutkannya dengan dua cara: sekali sebagai pemotongan 90% biaya produksi *sasis*, sekali sebagai pemotongan 90% biaya produksi *total*. Kedua versi tidak menyebutkan stasiun pembanding yang menjadi acuannya, sehingga sebagaimana tertulis klaim ini tidak bisa diperiksa. Dibandingkan rentang Tier 0 milik kampanye sendiri, penghematan yang sebenarnya jauh lebih tajam dari 90%, jadi kemungkinan besar klaim ini konservatif dan bukan dilebih-lebihkan — tapi replikator yang mengutipnya kepada pendana harus lebih dulu menyebut satu stasiun tertentu beserta harganya. <!-- TODO: pilih stasiun pembanding + harganya, nyatakan klaimnya sekali saja, dalam satu bentuk. -->

| | |
|---|---|
| ![Diagram tampak bawah sasis segitiga](img/04-bottom-view-diagram.png) | ![Wireframe bagian dalam sasis](img/05-chassis-interior-wireframe.png) |

## Dari mana bentuknya berasal

Tata letak kompartemen diambil langsung dari arsitektur enclosure **stasiun Smart Citizen Kit (SCK 2.3)** — dokumen sumber menyebut modularitas, kebersihan, dan minimalisme sebagai yang diambil darinya. Perlu dicatat, tulang punggung kalibrasi kampanye sendiri adalah **SCK 2.1** ([tabel tier](../README.id.md#di-mana-ini-cocok--tier-sensor-kampanye)); 2.3 adalah kit yang lebih baru, jadi ini peminjaman dari lini produknya dan bukan dari stasiun persis yang kemudian menjadi pembanding Node V2.

| | |
|---|---|
| ![Stasiun SCK terpasang di lapangan](img/06-sck-station-deployed.png) | ![Diagram terurai stasiun SCK](img/07-sck-station-exploded.png) |

Camprodon, G., González, Ó., Barberán, V., Pérez, M., Smári, V., de Heras, M.Á., Bizzotto, A., *Smart Citizen Kit and Station: An open environmental monitoring system for citizen participation and scientific experimentation*, HardwareX 6 (Oktober 2019). <https://www.sciencedirect.com/science/article/pii/S2468067219300203>

## Arsitektur fisik dan aliran udara

Cangkangnya berbentuk segitiga tumpul dilihat dari atas, dengan ruang dalam yang dibagi sekat. Jalur aliran udara, sebagaimana dirancang:

- Komponen dipasang mendatar pada satu lantai sasis. Sekat pembatas mekanis memisahkan modul utama (XIAO ESP32-C3) dari kompartemen sensor.
- Udara luar dihisap masuk dari **BAWAH** casing melalui kisi-kisi kecil, dialirkan horizontal melintasi ruang dalam, dan dibuang ke arah **SAMPING**.
- Sensor gas dan mikro-klimatologi BME680 ditempatkan di dalam sasis utama, **menghadap ke bawah** (ke tanah), tanpa kanopi pelindung radiasi di luarnya.

Dua keputusan terakhir itulah yang dibatalkan oleh uji lapangan. Keduanya ditulis di sini sebagaimana dirancang, bukan sebagai rekomendasi.

![Tampak atas memperlihatkan tiga kompartemen](img/08-upper-view-compartments.png)

## Elektronik

Dua sensor berbagi satu jalur I²C sebagai slave terhadap master XIAO ESP32-C3.

| Dari mikrokontroler (XIAO) | Ke perangkat sensor | Fungsi jalur pin | Warna kabel |
|---|---|---|---|
| GND (pin 13) | BME680 + HM3301 | Ground bersama | Hitam |
| 5V (pin 14) | Sensor debu HM3301 | Daya utama 5 V | Merah |
| 3V3 (pin 12) | Sensor gas BME680 | Daya logika 3,3 V | Kuning |
| D4 (pin 5) | BME680 + HM3301 | Serial data (bus SDA) | Ungu |
| D5 (pin 6) | BME680 + HM3301 | Serial clock (bus SCL) | Biru |

Alamat I²C, dari firmware bersama: **HM3301 di `0x40`**, **BME680 di `0x76`** (turun ke `0x77` bila SDO ditarik ke 3V3).

**Pin 14 tertulis `5V`** pada sablon papan; dokumen sumber menyebutnya VUSB. Pada XIAO ia biasanya adalah rel VBUS dari USB, tapi Node V2 mengaliri pin itu dari arah sebaliknya — dari DC jack di pelat bawah, lewat terminal blok mainboard. Bagaimanapun, hanya kipas dan laser HM3301 yang ada di jalur 5 V, jadi XIAO yang berjalan hanya dari pad BAT akan membuat sensor debu mati. Bill of materials tidak memuat sel baterai, jadi rakitan ini tidak pernah sampai ke kasus itu; ini baru relevan kalau ada yang mengadaptasinya. <!-- TODO: pastikan pada unit fisik apakah DC jack mengaliri pad 5V atau langsung ke soket sensor. -->

| | |
|---|---|
| ![Diagram pengkabelan](img/10-wiring-diagram.png) | ![Skematik](img/11-schematic.png) |

## Bill of materials

Versi yang bisa dibaca mesin, lengkap dengan kolom sourcing: **[`bom.csv`](bom.csv)**.

| No. | Komponen | Spesifikasi | Jml | Satuan (IDR) | Total (IDR) |
|---|---|---|---|---|---|
| 1 | Seeed Studio XIAO ESP32-C3 | Mikrokontroler RISC-V, Wi-Fi/BLE, USB-C | 1 | 165.000 | 165.000 |
| 2 | Seeed Grove HM3301 | Sensor partikulat laser scattering | 1 | 700.000 | 700.000 |
| 3 | CJMCU-680 (BME680) | Breakout sensor lingkungan gas 4-in-1 | 1 | 282.000 | 282.000 |
| 4 | Cangkang cetak 3D Node V2 | Casing segitiga kustom, bahan PETG | 1 | 65.000 | 65.000 |
| 5 | Aksesori wiring harness | Jumper Dupont female + kabel Grove 4-pin | 1 lot | 35.000 | 35.000 |
| 6 | Baut mesin M2 × 6 mm | Flat head, carbon steel (NINDEJIN) | 15 | 200 | 3.000 |
| 7 | Baut mesin M3 × 6 mm | Flat head, carbon steel (NINDEJIN) | 4 | 300 | 1.200 |
| 8 | Baut mesin M3 × 10 mm | Flat head, carbon steel (NINDEJIN) | 4 | 400 | 1.600 |
| 9 | Baut mesin M3 × 14 mm | Flat head, carbon steel (NINDEJIN) | 2 | 500 | 1.000 |
| | | | | **Total** | **Rp 1.253.800** |

Dokumen sumber memberikan angka-angka ini tanpa menyebutkan di mana dan kapan komponennya dibeli, jadi perlakukan sebagai biaya satu rakitan di Indonesia, bukan sebagai daftar harga. [Catatan sourcing di README induk](../README.id.md) adalah panduan yang lebih baik bagi siapa pun yang memesan: HM3301 adalah penentu biaya, dan memesan langsung dari Seeed biasanya lebih murah daripada eceran lokal untuk pembelian batch. Baut mesin flat head setara apa pun bisa menggantikan yang bermerek.

<!-- TODO: di mana dan kapan komponennya dibeli, dan apakah ini harga eceran atau distributor. -->
<!-- TODO: setara USD + kurs IDR/USD pada tanggal pembelian, supaya angkanya bisa dibandingkan dengan biaya USD yang dikutip di ../README.id.md. -->
<!-- TODO: apa saja yang tercakup dalam Rp 65.000 untuk cangkang (filamen saja, atau filamen plus waktu mesin) dan massa PETG dalam gram, supaya bisa dihitung ulang di mana saja. -->

## Custom mainboard

Kabel Dupont yang longgar di sasis sesempit ini berubah menjadi masalah perawatan dalam satu kali kunjungan servis, jadi XIAO tidak dikabeli langsung. Ia disolder ke **perfboard 3 × 7 cm** yang berfungsi sebagai papan pembawa kecil.

**Sisi atas.** XIAO dipasang di bagian tengah. Satu soket JST/Grove 4-pin di sisi kanan dan kiri memberi sensor sambungan plug-and-play. Satu terminal blok ulir hijau menerima input daya utama.

**Sisi bawah (jalur solder).** Teknik point-to-point dengan solid jumper wire. Kabel merah (5 V / 3,3 V) dan hitam (GND) dipasang paralel sebagai bus daya; kabel hijau dan biru mendistribusikan bus I²C (SDA dan SCL) secara paralel ke kedua soket sensor.

| | |
|---|---|
| ![Mainboard, sisi atas](img/13-mainboard-top.jpg) | ![Mainboard, sisi bawah](img/14-mainboard-bottom.jpg) |

> **Konflik kode warna, belum terselesaikan.** Tabel pengkabelan di atas menyebut **ungu = SDA, biru = SCL**. Jumper pada perfboard sendiri memakai **hijau dan biru** untuk dua sinyal yang sama. Kedua pernyataan berasal dari dokumen sumber. Mana pun yang benar, kedua kode warna ini bertentangan, dan replikator yang mengikuti salah satunya sambil melihat foto dari yang lain akan menukar SDA dan SCL — yang muncul sebagai "sensor tidak ditemukan" dan membuat Anda memburu masalah daya yang tidak ada. <!-- TODO: periksa unit fisik, pilih satu kode warna, perbaiki yang lain. -->

## Tata letak internal

Cangkang cetak membagi lantai secara horizontal, dengan dudukan sekrup bawaan yang mengunci setiap bagian pada posisinya.

**Bilik kiri — debu.** Modul laser HM3301, dikunci dengan empat baut M2 langsung ke sasis bawah.

**Bilik tengah — otak sistem.** Mainboard perfboard XIAO, terpasang pas di jalurnya dengan jarak aman yang disengaja dari sensor debu agar tidak terjadi korsleting.

**Ujung segitiga — mikro-klimatologi.** BME680 (PCB ungu) di sudut paling lancip cangkang, digeser mundur mendekati celah sasis agar lebih responsif menangkap perubahan suhu dan kelembapan luar.

![Tata letak internal unit yang sudah dirakit](img/15-internal-layout-built.jpg)

## Pelat bawah — daya, RF, udara

Seluruh antarmuka luar dikonsentrasikan pada pelat putih bagian bawah, yang menjaga sisi-sisinya tetap bersih dan konektornya terhindar dari hujan.

- **Input daya.** DC female jack, disolder dan dilindungi heat-shrink tubing kuning, menyalurkan 5 V DC ke terminal blok mainboard.
- **RF.** Konektor pigtail SMA menembus pelat, dengan antena omni 2,4 GHz eksternal diarahkan ke bawah-samping agar sambungan Wi-Fi tetap hidup menembus dinding bangunan banjar.
- **Udara.** Kisi-kisi lingkaran tepat di bawah kipas hisap HM3301, yang menjadi pintu masuk utama udara ambien.

| | |
|---|---|
| ![Render tampak bawah dengan keterangan](img/09-bottom-view-render.png) | ![Pelat bawah unit yang sudah dirakit](img/16-base-plate-io.jpg) |

## Perakitan

Alat: solder, obeng yang sesuai dengan baut Anda, tang potong dan pengupas kabel, heat gun atau korek untuk heat-shrink. <!-- TODO: waktu perakitan. Dokumen sumber tidak mencatatnya; angka ~3 jam di README induk adalah untuk rakitan yang berbeda. -->

1. **Cetak cangkang** dengan PETG, bukan PLA — [PLA melunak pada suhu atap rumah Bali](../README.id.md). <!-- TODO: layer height, jumlah dinding, infill, suhu nozzle/bed, orientasi cetak, kebutuhan support, waktu cetak. Tidak satu pun ada di dokumen sumber, dan semuanya dibutuhkan untuk mencetak ulang bagian ini. -->
2. **Bangun mainboard.** Solder XIAO di tengah perfboard 3 × 7 cm, dua soket Grove/JST di kedua sisi, dan terminal blok ulir. Lalu jalankan bus di sisi bawah secara point-to-point: merah dan hitam paralel untuk daya, dua jalur I²C paralel ke kedua soket.
3. **Pasang perangkat keras pelat bawah.** Solder kabel DC jack, lindungi sambungannya dengan heat-shrink, dan pasang pigtail SMA. Kerjakan ini sebelum apa pun masuk ke cangkang — pelatnya jauh lebih mudah dikerjakan saat kosong.
4. **Pasang sensor debu.** HM3301 ke bilik kiri, empat baut M2 × 6 ke dudukan sasis, kipas hisap menghadap kisi-kisi lingkaran.
5. **Pasang mainboard.** Perfboard ke jalur tengah, dikencangkan, periksa jaraknya ke sensor debu.
6. **Pasang BME680** di ujung segitiga, digeser mundur mendekati celah sasis.
7. **Sambungkan.** Kabel Grove dari soket mainboard ke HM3301; empat kabel BME680 ke soket satunya. Antena ke XIAO. Kabel DC jack ke terminal blok.
8. **Flash dan periksa** sebelum cangkang ditutup — lihat bagian berikutnya. Ubah `SC_DEVICE_TOKEN` di sketch menjadi token Smart Citizen milik node ini sebelum di-flash, lalu sediakan Wi-Fi pada boot pertama lewat captive portal `MakingSenseBali-XXXX`. Pada keluaran serial, `[hm3301] online at 0x40` menyebutkan alamatnya; baris BME680 hanya melaporkan bahwa sensornya menjawab, bukan di `0x76` atau `0x77` mana ia menjawab.
9. **Tutup** dengan baut M3 (6, 10, dan 14 mm; dudukan pada cangkang menentukan mana yang ke mana).

> Langkah 2, 5, dan 7 adalah tiga langkah yang paling membutuhkan foto dari atas dengan bagian-bagiannya diberi label. Dua foto mainboard di atas sudah cukup menutupi langkah 2; langkah 5 dan 7 saat ini hanya mengandalkan satu foto interior yang umum. <!-- TODO: foto langkah 5 dan 7. -->

**Sebelum dipasang di lapangan**, lapisi sisi solder perfboard dengan silicone conformal coating, tutupi dulu lubang sensor dan konektor USB-C. Kelembapan relatif Bali di atas 80% hampir sepanjang tahun dan papan tanpa lapisan berkarat dalam 6–12 bulan; alasan dan produknya ada di [README induk](../README.id.md).

## Firmware dan alur data

Node V2 menjalankan sketch DIY node bersama milik kampanye tanpa perubahan kode selain token Smart Citizen per perangkat: **[`../firmware/diy_node/`](../firmware/diy_node/)**. Berkas yang sama menyasar XIAO ESP32-S3 maupun ESP32-C3 — pemetaan pin D4/D5 diselesaikan per varian board, jadi tidak ada di dalamnya yang khusus untuk satu chip.

Setiap 60 detik XIAO mengalamati tiap sensor bergantian lewat I²C, mengemas pembacaannya sebagai JSON, dan mengirimkannya lewat Wi-Fi via MQTT di port 8883 ke `mqtt.smartcitizen.me`, tempat dasbor kampanye membacanya. Koneksinya memakai TLS tetapi **validasi sertifikat dimatikan** di versi firmware ini (`net.setInsecure()`) — cukup untuk kit lokakarya, tidak cukup untuk node yang datanya masuk ke argumen kebijakan. Sketch-nya sendiri menyatakan hal itu di tempat kejadiannya.

ID kanal katalog global Smart Citizen yang dipakai node ini:

| ID | Kanal | Satuan |
|---|---|---|
| 233 / 234 / 235 | HM3301 PM1.0 / PM2.5 / PM10.0 | µg/m³ |
| 237 / 238 | BME68X suhu / kelembapan (lihat catatan) | °C, %RH |
| 239 | BME68X tekanan | kPa |
| 240 | BME68X gas resistance | Ω (mentah) |
| 241 | BME68X IAQ | indeks, aproksimasi terbuka |

> **Kanal 237 / 238 diberi nama "heat-compensated" di katalog Smart Citizen.** Firmware mengirim nilai BME680 apa adanya, tanpa kompensasi sasis apa pun. Khusus pada node ini, nama kanal menjanjikan sesuatu yang tidak dibawa datanya — persis error yang kemudian diukur oleh evaluasi.

![Diagram integrasi sistem](img/12-system-integration-diagram.png)

> **Dokumentasi vs kode, ditandai.** Dokumen sumber menyebutkan data mentah "disaring menggunakan fungsi kalkulasi kalibrasi lokal untuk mengeliminasi error sasis" sebelum dikirim. **Fungsi seperti itu tidak ada di firmware yang ditautkan.** Firmware mengirim suhu dan kelembapan apa adanya, ditambah aproksimasi IAQ on-device yang secara eksplisit tidak terkalibrasi. Dua alasan mengapa ini penting: fungsi yang dijelaskan itu tidak ada, dan kalau ada yang menambahkannya, itu bertentangan dengan kebijakan kampanye bahwa [koreksi hidup di lapisan pemrosesan dasbor, bukan di firmware](../README.id.md) — koreksi di firmware tidak bisa diaudit, koreksi di dasbor terversi. Panas sendiri yang ditemukan evaluasi adalah error nyata yang memang butuh koreksi nyata; tempatnya di pipeline data. <!-- TODO: hapus klaim ini dari peredaran, atau tunjuk kode yang benar-benar mengimplementasikannya. -->

## Evaluasi — apa yang ditunjukkan uji lapangan

Node V2 dijalankan berdampingan dengan stasiun acuan Smart Citizen Kit. Dua hasil, mengarah ke dua arah yang berlawanan.

**Suhu terbaca terlalu tinggi.** Modul Wi-Fi pada XIAO ESP32-C3 memancarkan panas terus-menerus. Karena diletakkan berdampingan dengan BME680 dalam satu ruang tertutup, panas itu merambat lewat dinding plastik dan masuk ke sensor. Pembacaan suhu Node V2 jauh di atas cuaca sebenarnya di luar cangkang. Kelembapan relatif ikut salah bersamanya: sensor yang berada di udara lebih hangat daripada udara sekitar akan membaca udara itu lebih kering daripada udara luar yang sebenarnya. Dokumen sumber hanya melaporkan error suhunya, jadi perlakukan konsekuensi pada kelembapan ini sebagai kesimpulan turunan, bukan hasil pengukuran.

**Partikulat terlambat.** Menempatkan lubang masuk udara di kolong bawah menghambat sirkulasi partikel. Ketika debu di lingkungan sekitar melonjak mendadak, Node V2 merespons terlambat: udara baru lambat menembus kisi-kisi bawah yang sempit, grafik tren mendatar, dan puncak polusi yang sebenarnya tidak pernah masuk ke rekaman. Untuk kampanye yang seluruh argumennya bersandar pada penangkapan peristiwa pembakaran terbuka, node yang menghaluskan puncak lebih buruk daripada node yang sekadar berisik.

Kedua kegagalan ini tidak mengumumkan dirinya. Keduanya menghasilkan data yang tampak masuk akal. Justru itulah alasan keduanya ditulis di sini.

## Apa yang harus dilakukan V3 secara berbeda

1. **Masukan udara dari atas atau samping terbuka, bukan dari bawah.** Lubang masuk menghadap ke bawah terbukti gagal. V3 kembali ke jalur aliran udara vertikal.
2. **Keluarkan BME680 dari kompartemen utama.** Sensor itu harus berada di luar bilik elektronik, di bawah struktur kubah perisai radiasi matahari (multi-louvered solar radiation shield), agar membaca udara alam dan bukan buangan panas mikrokontroler.

Keduanya sudah terpecahkan di [sasis pine cone v5 yang berlaku sekarang](../enclosure/), yang menaruh setiap celah napas di bayangan hujan sebuah sisik dan menjalankan cerobong dari lubang masuk rendah setinggi BME680 ke pembuangan tinggi di bawah tudung. Kalau V3 memang rancangan baru dan bukan adopsi v5, folder itu yang pertama harus dibaca.

Ada pelajaran ketiga yang disiratkan evaluasi tanpa dinyatakan: **keringkasan dan isolasi termal saling bertentangan langsung**, dan V2 memilih keringkasan tanpa menghitung harganya. Cangkang yang menampung radio dan sensor suhu dalam satu ruang tertutup akan melaporkan suhu radionya. Pisahkan keduanya secara fisik, atau terima bahwa kanal suhunya bersifat diagnostik dan bukan ambien — lalu nyatakan itu di dasbor.

## Berkas

| Apa | Di mana |
|---|---|
| Firmware (dipakai bersama seluruh keluarga DIY node) | [`../firmware/diy_node/`](../firmware/diy_node/) |
| Bill of materials, terbaca mesin | [`bom.csv`](bom.csv) |
| Foto, render, dan diagram | [`img/`](img/) |
| Berkas enclosure Node V2 | [Folder Google Drive](https://drive.google.com/file/d/1OdK7mdnLc2XkGRntHOQXK7PGmcP8E4bJ/view?usp=sharing) — **belum ada di repo ini** |
| Makalah acuan stasiun SCK | [HardwareX 6 (2019)](https://www.sciencedirect.com/science/article/pii/S2468067219300203) |
| Sasis yang direkomendasikan saat ini | [`../enclosure/`](../enclosure/) |

## Apa yang masih kurang dari dokumentasi ini

Ditulis terus terang, karena pembaca berhak tahu mana yang memang lubang, bukan menemukannya sendiri di depan printer.

- **Sumber CAD-nya tidak ada di sini, begitu pula STL-nya.** Enclosure-nya berada di folder Google Drive di luar repo. Saat ini tidak ada yang bisa mencetak ulang cangkang ini dari repositori, dan kalau tautan Drive itu mati, rancangannya hilang. Ini satu-satunya lubang yang benar-benar memblokir: [open hardware butuh sumber yang bisa diedit sekaligus ekspor siap-bangun](https://open-make.github.io/Hardware-template-guide/), dan folder ini sekarang tidak punya keduanya.
- **Tidak ada parameter cetak.** Layer height, dinding, infill, suhu, orientasi, support, waktu cetak. Bagian ini tidak bisa direproduksi secara konsisten tanpa itu semua.
- **Tidak ada dimensi cangkang atau ketebalan dinding**, jadi rancangannya tidak bisa diadaptasi atau diperiksa kewajarannya.
- **Kode warna SDA/SCL bertentangan dengan dirinya sendiri** antara tabel pengkabelan dan perfboard.
- **Klaim "kalibrasi lokal"** tidak punya kode yang bersesuaian.
- **Tidak ada angka terukur untuk kegagalannya.** "Terbaca lebih panas" dan "terlambat" adalah temuan yang tepat, tapi Δ°C terhadap SCK dan keterlambatan dalam menit akan membuat rancangan berikutnya punya target, bukan sekadar arah. Kalau data ko-lokasi itu masih ada, tempatnya di sini.
- **Sebelas baut tanpa tujuan.** BoM membeli 15 baut M2 × 6; empat mengunci HM3301, sisanya tidak muncul di langkah perakitan mana pun.
- **Tidak ada catatan perbaikan atau pembuangan.** Wajar pada tahap ini; wajib sebelum ada yang menyebut rancangan ini siap direplikasi.

Didokumentasikan mengikuti [Open-Make Hardware Template Guide](https://open-make.github.io/Hardware-template-guide/) — Colomb, J. (2025), *Guide and template for hardware project documentation*, Zenodo, [doi:10.5281/zenodo.14725490](https://doi.org/10.5281/zenodo.14725490). Tahap pengembangan: **prototyping**, sudah dievaluasi dan digantikan.

## Lisensi

MIT, sama dengan repositori induk. Acuan stasiun SCK adalah karya para penulisnya sendiri, dikutip di atas. Fork untuk Making Sense [tempat Anda] — dan kalau Anda membangun V3 yang dituntut rancangan ini, kembalikan ke folder di sebelah folder ini.
