[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# Bayu v7 — casing kanonik saat ini

*Fab Lab Bali menyebut desain ini **DIY Environmental Sensor Node V3.2**. Objek yang sama, dua
sistem penamaan — lihat [Penamaan](#penamaan-baca-ini-sebelum-menelusuri-repo).*

Casing luar ruangan cetak 3D untuk node kualitas udara DIY Making Sense Bali.
*Bayu* — angin. Seluruh generasi V3 adalah argumen tentang aliran udara, dan v7 adalah
iterasi yang berhenti memakai sekrup.

**Tahap:** siap cetak, siap lapangan sambil menunggu ko-lokasi. Belum siap replikasi — tidak ada sumber CAD.
**Menggantikan:** [`../node-v3.1/`](../node-v3.1/) (= Node V3.1) dan semua isi [`../previous-iterations/`](../previous-iterations/)
**Lisensi:** CERN-OHL-W-2.0 (perangkat keras) · CC-BY-SA-4.0 (dokumentasi ini)
**Sumber:** *Dokumentasi Teknis: DIY Environmental Sensor Node V3*, Fab Lab Bali, September 2026. Dokumen ini adalah versi asli berbahasa Indonesia; versi Inggris dan Spanyol diterjemahkan darinya.

![Tampilan terurai rakitan Node V3.2](img/01-exploded-v32.png)

## Daftar isi

- [Penamaan](#penamaan-baca-ini-sebelum-menelusuri-repo)
- [Yang berubah dari v6](#yang-berubah-dari-v6--node-v31)
- [Apa yang diperbaiki dan tidak diperbaiki desain ini](#apa-yang-diperbaiki-dan-tidak-diperbaiki-desain-ini)
- [Arsitektur hibrida](#arsitektur-hibrida--apa-yang-bisa-disubstitusi)
- [Aliran udara](#aliran-udara)
- [Bagian cetak](#bagian-cetak)
- [Pengaturan cetak](#pengaturan-cetak)
- [Daftar material](#daftar-material)
- [Pengkabelan](#pengkabelan)
- [Perakitan](#perakitan)
- [Pemasangan](#pemasangan)
- [Firmware dan alur data](#firmware-dan-alur-data)
- [Masalah yang diketahui pada berkas ini](#masalah-yang-diketahui-pada-berkas-ini)
- [Yang masih kurang dari dokumentasi ini](#yang-masih-kurang-dari-dokumentasi-ini)

## Penamaan, baca ini sebelum menelusuri repo

Dua sistem penamaan bertabrakan di pohon folder ini dan keduanya masih dipakai.

| Repo ini | Fab Lab Bali | Apa ini |
|---|---|---|
| `node-v3.1/` | **Node V3.1** | Rakitan bersekrup, braket dinding terpisah. Sudah digantikan. |
| `node-v3.2/` (di sini) | **Node V3.2** | Sepenuhnya tanpa sekrup, dudukan terintegrasi. **Bangun yang ini.** |

`node-v3.1/` dan Node V3.1 adalah *enam berkas STL yang sama* — diverifikasi bita demi bita, bukan
disimpulkan dari nama berkas. Repo menerima mesh-nya pada September 2026 tanpa dokumen yang
menjelaskannya; folder ini dan [`../node-v3.1/`](../node-v3.1/) adalah dokumen itu, yang datang
terlambat.

Garis keturunan casing dihitung v1-kotak → v2-lentera → v3-labu → v4-kolom → v5 buah pinus →
v6 → v7. Fab Lab Bali menghitung generasi node utuh: V1 → V2 → V3.1 → V3.2. Kedua penghitungan
itu tidak berkaitan dan akan terus bertabrakan; tabel di atas adalah pemetaannya.

## Yang berubah dari v6 (= Node V3.1)

| | v6 / Node V3.1 | **v7 / Node V3.2** |
|---|---|---|
| Penutup atas | Sekrup, dipasang dari luar bodi | **Snap-fit detent**, tiga titik kunci pada keliling bagian dalam |
| Penahan sensor dan papan | Sekrup M2/M3 menembus pelat penutup | **Kait snap-fit kantilever** pada setiap bagian internal |
| Pemasangan di dinding | Braket cetak terpisah, dibaut | **Lubang sekrup tercetak menyatu** di punggung bodi |
| Pemasangan di tiang | Tidak didukung | **Slot cable tie terintegrasi** di punggung bodi |
| Berkas braket papan | 1 (sekrup menyerap perbedaan suaian) | **2** — pilih sesuai mainboard, jarak kaitnya berbeda |
| Berkas penutup BME680 | 1 | **2** — breakout Bosch dan Seeed Grove punya footprint berbeda |
| Bagian cetak untuk membangun satu node | 6 | **5** (braket dinding tidak ada lagi) |

Sekrup yang dihapus dari rakitan: **11 per node** (4 × M3×10, 3 × M2×10, 2 × M2×5, 2 × M3×10).
Satu-satunya pengencang yang tersisa adalah mur antena SMA, yang merupakan komponen jadi, bukan hasil cetak.

![Perbandingan Node V3.1 dan V3.2](img/13-v31-v32-comparison.png)

Kenapa ini penting di lapangan: sensor yang bisa dibuka tanpa obeng akan dibersihkan sensor
PM-nya. Yang butuh obeng, obeng dengan ukuran yang tepat, dan empat sekrup yang tidak
menggelinding jatuh dari atap, tidak akan dibersihkan.

## Apa yang diperbaiki dan tidak diperbaiki desain ini

Node yang digantikan generasi ini pernah diko-lokasikan dengan Smart Citizen Kit dan
[gagal dua kali](../node-v2/README.id.md).
Terus terang saja soal kegagalan mana yang ditangani V3.2:

**Diperbaiki — hisap ulang gas buang.** Pada casing yang ringkas, aliran keluar sensor PM itu
sendiri tersedot kembali ke saluran masuknya, dan node berakhir mengukur udara yang sudah
diukurnya. Bagian [`OUTFLOW_DUCT_HM3301`](stl/OUTFLOW_DUCT_HM3301.stl) membawa buangan ke
samping, menjauh dari saluran masuk. Ini perbaikan nyata untuk masalah nyata.

**Tidak ditangani — dua kegagalan lapangan yang terdokumentasi.** Keduanya tidak muncul dalam
dokumen sumber, dan geometrinya menunjukkan tidak satu pun dirancang untuk mengatasinya:

1. **Saluran masuk di sisi bawah.** Evaluasi V2 menemukan saluran masuk yang menghadap ke
   bawah membatasi sirkulasi, sehingga lonjakan PM datang terlambat dan mendatar. Saluran
   masuk V3.2 masih berada di sisi bawah bodi ([`05-underside-intake-outflow.png`](../node-v3.1/img/05-underside-intake-outflow.png)).
   Syarat pertama untuk V3 dalam laporan V2 adalah *"saluran masuk dari atas atau dari sisi
   yang terbuka, bukan dari bawah."* Syarat itu tidak terpenuhi.
2. **Pemanasan sendiri BME680.** Evaluasi V2 menemukan radio Wi-Fi ESP32 memanaskan BME680
   melalui dinding pemisah, mendorong suhu di atas suhu lingkungan dan menyeret RH turun
   bersamanya. V3.2 masih mendudukkan BME680 di kantong bodi utama, dalam volume tertutup yang
   sama dengan radio, di bawah penutup cetak yang datar — tanpa pelindung radiasi, tanpa
   pemutus termal. Syarat kedua dalam laporan V2 juga tidak terpenuhi.

<!-- TODO: ini butuh keputusan dari Fab Lab Bali, bukan perbaikan dokumentasi. Entah
     (a) ko-lokasikan sebuah V3.2 dengan SCK dan publikasikan Δ°C serta jeda PM — kalau
     ternyata bodi ringkas ini tidak mengulang galat V2, hasil itu lebih berharga daripada
     asumsinya; atau (b) perlakukan kanal suhu sebagai diagnostik, bukan ambien, dan beri
     label demikian di dasbor. Jangan dibiarkan tersirat. -->

Sampai sebuah V3.2 diko-lokasikan, **perlakukan kanal suhu dan kelembapannya sebagai belum
terverifikasi**, dan harapkan puncak PM terbaca rendah. Itu bukan alasan untuk berhenti
memasang — itu alasan untuk menjalankan ko-lokasi minggu pertama yang memang sudah diwajibkan
kampanye untuk setiap node baru.

## Arsitektur hibrida — apa yang bisa disubstitusi

Inti dari bodi V3 adalah bahwa stok lokal bisa habis. Satu cangkang, beberapa daftar
material.

**Mainboard** — pilih satu:

- **Seeed Grove Shield for XIAO.** Plug-and-play, tanpa solder. Menerima XIAO ESP32-C3 atau ESP32-S3.
- **PCB custom DIY.** Lebih murah, perlu solder. Menerima XIAO ESP32-C3/S3, ESP32-C3/S3
  Supermini, atau Seeed ESP32-S3 dengan LoRa terpasang di papan.

> **Supermini dan XIAO tidak kompatibel pin di PCB DIY.** I²C jatuh di D4/D5
> untuk XIAO dan D8/D9 untuk Supermini. Periksa [Pengkabelan](#pengkabelan) sebelum memanaskan solder.

![Pilihan mainboard di dalam kompartemennya](../node-v3.1/img/10-mainboard-options.png)

**Sensor lingkungan** — breakout Bosch BME680, atau Seeed Grove BME680. Footprint-nya
berbeda, jadi cetak penutup yang sesuai:
[`COVER_BME680_BOSCH.stl`](stl/COVER_BME680_BOSCH.stl) atau
[`COVER_BME680_SEEED_STUDIO.stl`](stl/COVER_BME680_SEEED_STUDIO.stl).

**Sensor PM** — hanya Seeed Studio HM3301. Tidak ada alternatif yang dirancang untuk casing ini.

**Radio** — bodi tersedia dalam dua varian: satu port SMA (Wi-Fi) atau dua (Wi-Fi + LoRa
sub-GHz). LoRa hanya tersedia pada Seeed ESP32-S3 yang modulnya sudah terpasang di papan.

**Daya** — USB Type-C, 5 V DC.

## Aliran udara

Udara luar ditarik masuk melalui saluran masuk di sisi bawah oleh kipas HM3301 sendiri. Udara
yang sudah terukur keluar lewat saluran perpanjangan, yang mengarahkannya ke samping dan
menjauh dari saluran masuk supaya tidak langsung terukur ulang.

![Saluran masuk sisi bawah dan saluran buang](../node-v3.1/img/05-underside-intake-outflow.png)

Baca itu bersama [Apa yang diperbaiki dan tidak diperbaiki desain ini](#apa-yang-diperbaiki-dan-tidak-diperbaiki-desain-ini)
— saluran itu menyelesaikan hisap ulang, bukan pembatasan saluran masuk.

## Bagian cetak

**Lima bagian per node.** Dua dari delapan berkas itu berupa pasangan salah-satu, dan dua
varian bodi adalah pilihan, bukan satu set.

| Bagian | Berkas | Jml | Catatan |
|---|---|---|---|
| Penutup atas | [`TOP_COVER.stl`](stl/TOP_COVER.stl) | 1 | Snap-fit detent |
| Bodi utama — antena ganda | [`MAIN_BODY_2_ANTENNA.stl`](stl/MAIN_BODY_2_ANTENNA.stl) | 1 | **atau** ↓ — Wi-Fi + LoRa |
| Bodi utama — antena tunggal | [`MAIN_BODY_1_ANTENNA.stl`](stl/MAIN_BODY_1_ANTENNA.stl) | 1 | **atau** ↑ — hanya Wi-Fi |
| Penutup BME680 — Seeed | [`COVER_BME680_SEEED_STUDIO.stl`](stl/COVER_BME680_SEEED_STUDIO.stl) | 1 | **atau** ↓ |
| Penutup BME680 — Bosch | [`COVER_BME680_BOSCH.stl`](stl/COVER_BME680_BOSCH.stl) | 1 | **atau** ↑ |
| Penutup HM3301 + braket papan — Grove Shield | [`COVER_HM3301_BRACKET_BOARD_GROVE_SHIELD.stl`](stl/COVER_HM3301_BRACKET_BOARD_GROVE_SHIELD.stl) | 1 | **atau** ↓ |
| Penutup HM3301 + braket papan — PCB DIY | [`COVER_HM3301_BRACKET_BOARD_PCB_DIY.stl`](stl/COVER_HM3301_BRACKET_BOARD_PCB_DIY.stl) | 1 | **atau** ↑ |
| Saluran buang | [`OUTFLOW_DUCT_HM3301.stl`](stl/OUTFLOW_DUCT_HM3301.stl) | 1 | Tidak berubah dari v6 |

Ukuran dibaca langsung dari mesh pada 2026-09-23, jadi nyata. Semua yang ada di
[Pengaturan cetak](#pengaturan-cetak) tidak.

| Berkas | Kotak batas (mm) | Segitiga |
|---|---|---|
| `TOP_COVER.stl` | 117.9 × 88.0 × 32.0 | 14,154 |
| `MAIN_BODY_2_ANTENNA.stl` | 113.9 × 94.0 × 28.9 | 5,544 |
| `MAIN_BODY_1_ANTENNA.stl` | 113.9 × 94.0 × 28.9 | 5,422 |
| `COVER_HM3301_BRACKET_BOARD_GROVE_SHIELD.stl` | 80.2 × 43.3 × 12.4 | 5,166 |
| `COVER_HM3301_BRACKET_BOARD_PCB_DIY.stl` | 80.2 × 43.3 × 13.9 | 2,472 |
| `OUTFLOW_DUCT_HM3301.stl` | 46.0 × 26.0 × 12.0 | 1,548 |
| `COVER_BME680_BOSCH.stl` | 45.9 × 26.1 × 3.4 | 1,936 |
| `COVER_BME680_SEEED_STUDIO.stl` | 45.9 × 26.1 × 2.2 | 640 |

Bodi bertambah 2 mm pada sumbu Y dibanding v6 (92.0 → 94.0). Itu adalah fitur pemasangan
terintegrasi di muka belakang — 2 mm itu adalah braket dinding, yang diserap ke dalam bodi.

Bagian diekspor dalam koordinat rakitan, bukan koordinat cetak — sebagian besar punya Z
minimum negatif. Slicer akan menjatuhkannya ke bed, tetapi berkasnya tidak diorientasikan
lebih dulu untuk pencetakan.

![Bagian-bagian cetak](../node-v3.1/img/11-printed-parts-v31.png)

## Pengaturan cetak

<!-- TODO: tidak satu pun dari nilai ini diketahui. Tidak ada nilai nyata di tabel ini. Fab Lab
     Bali sudah mencetak bagian-bagian ini — pengaturannya ada di profil slicer seseorang. Ekspor. -->

| | |
|---|---|
| Material | TODO — **PETG atau ASA**. PLA mulur dan melendut di atap Bali; README induk sudah menyingkirkannya |
| Tinggi layer | TODO |
| Dinding / perimeter | TODO — kait snap-fit adalah jalur beban di sini, jadi yang satu ini bukan soal tampilan |
| Infill | TODO |
| Suhu nozzle / bed | TODO |
| Support | TODO — sebutkan per bagian |
| Orientasi cetak | TODO — sebutkan per bagian. Pada v7 ini penting dua kali lipat: arah layer menentukan apakah kait kantilever melentur atau patah |
| Perkiraan waktu cetak / massa filamen | TODO |

Nyatakan kebutuhan mesin dalam istilah bengkel — volume cetak minimum, diameter nozzle —
bukan dengan merek printer. Lab di kota lain punya mesin yang berbeda.

**Bagian snap-fit lebih sensitif terhadap pencetakan dibanding yang bersekrup.** Kait
kantilever yang dicetak dengan garis layer melintang di pangkalnya adalah kait yang patah pada
perakitan pertama. Sampai orientasinya terdokumentasi, cetak penutupnya rebah dan siap-siap
kehilangan satu.

## Daftar material

Lihat [`bom.csv`](bom.csv) untuk versi terbaca-mesin dalam kolom Open-Make milik repo ini.

| # | Komponen | Spesifikasi / model | Jml | Catatan |
|---|---|---|---|---|
| 1 | Prosesor utama | XIAO ESP32-C3 / ESP32-S3, ESP32-C3/S3 Supermini, atau Seeed ESP32-S3 dengan LoRa | 1 | Master pada bus I²C |
| 2 | Papan dasar | Seeed Grove Shield for XIAO **atau** PCB custom DIY | 1 | Menentukan STL braket papan mana yang Anda cetak |
| 3 | Sensor PM | Seeed Studio HM3301 | 1 | PM2.5 / PM10 laser, I²C, alamat 0x40 |
| 4 | Sensor lingkungan | Breakout Bosch BME680 **atau** Seeed Grove BME680 | 1 | T / RH / tekanan / gas, I²C, 0x76 atau 0x77 |
| 5 | Masukan daya | USB Type-C | 1 | 5 V DC |
| 6 | Pigtail | SMA female ke IPEX / U.FL | 1–2 | 1 untuk radio tunggal, 2 untuk ganda |
| 7 | Antena eksternal | 2.4 GHz (+ LoRa sub-GHz jika ganda) | 1–2 | |
| 8 | Set kabel | JST-XH dan Grove 4-pin | 1 set | Pengkabelan internal |
| 9 | Cable tie | 20–30 cm, lebar 3–4 mm | 2 | Hanya untuk pemasangan di tiang |

**Tanpa harga.** BoM V3.2 di dokumen sumber tidak punya kolom harga, dan kampanye ini tidak
punya penawaran terkini untuk rakitan ini. [BoM Node V2](../node-v2/bom.csv)
memuat harga IDR dari pembelian sebelumnya — pakai sebagai orde besaran, bukan sebagai
penawaran, dan catat bahwa V2 memakai mainboard yang berbeda.

<!-- TODO: hitung harga rakitan ini. Angka biaya adalah pertanyaan yang paling sering
     ditanyakan banjar dan satu-satunya angka yang saat ini tidak bisa dijawab dokumen ini. -->

## Pengkabelan

Semua sensor berada pada satu bus I²C, dibaca secara paralel.

> **HM3301 butuh 5 V.** Kipas dan lasernya tidak akan jalan pada 3.3 V. Tabel Grove Shield di
> dokumen sumber menyebut 3.3 V; **skema Grove Shield di dokumen sumber itu sendiri menyebut
> 5 V**, begitu juga semua tabel lain di dalamnya. Skemanya yang benar. Di bawah ini sudah
> dikoreksi. <!-- Sudah dilaporkan ke hulu — lihat "Yang masih kurang dari dokumentasi ini". -->

### Grove Shield (XIAO ESP32-C3 / S3 / S3+LoRa)

| Komponen | Pin sensor | Pin mainboard | Sinyal |
|---|---|---|---|
| USB Type-C | VBUS / 5V | 5V / VIN | Daya masuk (+5 V) |
| BME680 | VCC | 3.3V | Daya |
| | GND | GND | Ground |
| | SDA | SDA (I²C khusus) | Data I²C |
| | SCL | SCL (I²C khusus) | Clock I²C |
| HM3301 | VCC | **5V** | Daya — *bukan 3.3 V; lihat catatan di atas* |
| | GND | GND | Ground |
| | SDA | SDA (paralel dengan BME680) | Data I²C |
| | SCL | SCL (paralel dengan BME680) | Clock I²C |
| Modul LoRa | Header | Header colok langsung, ESP32-S3 | Colok langsung |

![Skema pengkabelan Grove Shield](img/07-wiring-grove-shield.png)
![Tampilan breadboard Grove Shield](img/10-breadboard-grove-shield.png)

### PCB DIY dengan XIAO ESP32-C3 / S3 / S3+LoRa

| Komponen | Pin sensor | Pin mainboard | Sinyal |
|---|---|---|---|
| Breakout USB Type-C | VBUS / 5V | 5V / VIN | Daya masuk (+5 V) |
| BME680 | VCC | 3.3V | Daya |
| | GND | GND | Ground |
| | SDA | **D4** | Data I²C |
| | SCL | **D5** | Clock I²C |
| HM3301 | VCC | 5V | Daya |
| | GND | GND | Ground |
| | SDA | D4 (paralel dengan BME680) | Data I²C |
| | SCL | D5 (paralel dengan BME680) | Clock I²C |
| Modul LoRa | Header | Header colok langsung / SPI | Langsung |

![PCB DIY dengan XIAO — skema pengkabelan](img/08-wiring-pcb-diy-xiao.png)
![PCB DIY dengan XIAO — tampilan breadboard](img/11-breadboard-pcb-diy-xiao.png)

### PCB DIY dengan ESP32-C3 / ESP32-S3 Supermini

| Komponen | Pin sensor | Pin mainboard | Sinyal |
|---|---|---|---|
| Breakout USB Type-C | VBUS / 5V | 5V / VIN | Daya masuk (+5 V) |
| BME680 | VCC | 3.3V | Daya |
| | GND | GND | Ground |
| | SDA | **D8** | Data I²C |
| | SCL | **D9** | Clock I²C |
| HM3301 | VCC | 5V | Daya |
| | GND | GND | Ground |
| | SDA | D8 (paralel dengan BME680) | Data I²C |
| | SCL | D9 (paralel dengan BME680) | Clock I²C |
| Modul LoRa | Header | Header colok langsung / SPI | Langsung |

![Skema pengkabelan Supermini](img/09-wiring-pcb-diy-supermini.png)
![Tampilan breadboard Supermini](img/12-breadboard-pcb-diy-supermini.png)

## Perakitan

Tanpa obeng. Setiap sambungan internal berupa snap fit.

1. **Bodi.** Pasang pigtail SMA melalui lubang antena di
   `MAIN_BODY_1_ANTENNA.stl` atau `MAIN_BODY_2_ANTENNA.stl` dan kencangkan murnya dari luar.
   Ini satu-satunya pengencang dalam rakitan.
2. **BME680.** Turunkan sensor ke kantongnya di lantai bodi. Tekan penutup yang sesuai —
   Bosch atau Seeed — sampai kait kantilevernya berbunyi klik.
3. **HM3301 dan saluran buang.** Dudukkan sensor PM di kompartemennya. Pasang
   `OUTFLOW_DUCT_HM3301.stl` ke kanal buang. Tekan penutup HM3301 yang sesuai —
   Grove Shield atau PCB DIY — di atas sensor sampai kaitnya mengunci.
4. **Mainboard.** Tekan papan ke bawah pada kait kantilever yang tercetak menyatu di penutup
   HM3301. Sambungkan kabel JST/Grove dari USB-C, BME680 dan HM3301, lalu jepitkan pigtail
   ke port U.FL.
5. **Tutup.** Posisikan `TOP_COVER.stl` dan tekan keempat sisinya sampai detennya berbunyi klik.

![Tata letak internal](img/02-internal-layout.png)
![Kait snap-fit kantilever](img/03-cantilever-snapfit-hooks.png)
![Penutup atas snap-fit detent](img/04-detent-snapfit-top-cover.png)

Braket papan, menurut mainboard:

| | |
|---|---|
| ![Braket Grove Shield](img/05-bracket-grove-shield.png) | ![Braket PCB DIY](img/06-bracket-pcb-diy.png) |

<!-- TODO: foto rakitan sungguhan. Setiap gambar di sini adalah render CAD. Perakit perlu
     melihat kaitnya terkunci, dan seberapa besar sebenarnya gaya "sampai berbunyi klik" itu. -->

## Pemasangan

Tanpa braket cetak. Kedua opsi tercetak menyatu di punggung bodi.

- **Dinding datar.** Pasang dua sekrup atau paku di dinding dan gantungkan bodi pada lubang
  sekrup yang tercetak menyatu.
- **Tiang atau pohon.** Selipkan dua cable tie melalui slot terintegrasi, lilitkan, tarik kencang.

<!-- TODO: jarak sekrup dan diameter lubang untuk opsi dinding; diameter tiang maksimum untuk
     slot cable tie. Keduanya bisa dibaca dari CAD, tidak satu pun ada di sumber. -->

Pemilihan lokasi lebih penting daripada braketnya. Tinggi pemasangan, arah hadap saluran
masuk, dan apa yang menaunginya ada di kartu lokasi kampanye — lihat
[dokumentasi lokakarya](../../../../docs/) sebelum memilih titik.

## Firmware dan alur data

Tidak berubah untuk seluruh generasi V3. Lihat [`../../firmware/`](../../firmware/) untuk
sketsanya, dan catatan integrasi Smart Citizen milik kampanye untuk transport MQTT — node DIY
menerbitkan ke `device/sck/<device_token>/readings` lewat TLS di port 8883, dan token
perangkat itulah seluruh identitasnya.

## Masalah yang diketahui pada berkas ini

Ditemukan lewat inspeksi mesh pada 2026-09-23, sebelum publikasi:

- **`OUTFLOW_DUCT_HM3301.stl` punya 1 tepi terbuka dan 1 segitiga degenerat (luas nol).**
  Dibawa tanpa perubahan dari v6, di mana cacat yang sama sudah ditandai dan tidak diperbaiki.
  Slicer biasanya memperbaikinya diam-diam, yang berarti hasilnya adalah apa pun yang
  diputuskan slicer Anda. Ekspor ulang dari sumbernya.
- **Tujuh bagian lainnya kedap (watertight)** tanpa segitiga degenerat. Perlu dicatat bahwa
  `Main_Body.stl` milik v6 punya 4 tepi terbuka sedangkan bodi v7 tidak punya satu pun — bodinya
  diekspor ulang dengan bersih di suatu titik di antara keduanya.
- **Tidak ada sumber CAD yang dipublikasikan.** Lihat [`cad/README.md`](cad/README.md). Ini
  penghalang untuk menyebut desain ini siap replikasi, dan penghalang yang sama juga dimiliki v6.

## Yang masih kurang dari dokumentasi ini

Sepuluh butir terbuka, bisa di-grep sebagai `TODO` di sumber berkas ini. Yang paling menghambat lebih dulu:

1. **Sumber CAD.** STL adalah hasil ekspor, bukan desain. Tidak ada orang di luar Fab Lab Bali
   yang bisa mengubah sudut kait, memindahkan port, atau memasang sensor lain.
2. **V3.2 yang sudah diko-lokasikan.** Dua dari tiga kegagalan V2 yang terdokumentasi tidak
   ditangani dalam geometrinya. Sampai satu unit berjalan seminggu berdampingan dengan SCK,
   kanal T/RH belum terverifikasi dan puncak PM patut dicurigai.
3. **Pengaturan cetak.** Tidak ada yang diketahui. Pada desain snap-fit, orientasi dan jumlah
   perimeter menentukan apakah benda ini bisa dirakit sama sekali.
4. **Biaya.** Tidak ada harga untuk rakitan ini, dalam mata uang apa pun.
5. **Foto perakitan.** Semua gambar adalah render.
6. **Jarak sekrup dan diameter lubang untuk pemasangan dinding; diameter tiang maksimum.**
7. **Dimensi luar terpasang dan massa.**
8. **Waktu perakitan**, dalam menit, untuk orang yang belum pernah merakitnya.
9. **Peringkat proteksi masuknya air dan debu.** Sumber V3 mengklaim tahan percikan untuk
   generasi ini tetapi tidak menyebut pengujian maupun peringkatnya.
10. **Pilihan antena.** Gain, dan apakah varian dua antena punya masalah isolasi terukur
    antara port 2.4 GHz dan sub-GHz.

Dua kesalahan dalam dokumen sumber dikoreksi alih-alih disalin, dan keduanya harus
dikembalikan ke Fab Lab Bali:

- Tabel pengkabelan Grove Shield memberi HM3301 3.3 V; skemanya sendiri memberi 5 V.
  Di sini dikoreksi menjadi 5 V. Mengikuti tabel itu akan membuat kipas dan lasernya mati.
- Bagian perakitan V3.1 menyebut `V3.1_Top_Cover.stl` dan `V3.1_Wall_Bracket_Separate.stl`;
  berkas semacam itu tidak ada di rilis mana pun. Nama sebenarnya adalah `TOP COVER.stl` dan
  `BRACKET TO WALL.stl`. Terdokumentasi di [`../node-v3.1/`](../node-v3.1/).

---

*Making Sense Bali · Chapter Fab City Bali · diselenggarakan oleh Fab Lab Bali.
Perangkat keras CERN-OHL-W-2.0 · dokumentasi CC-BY-SA-4.0.*
