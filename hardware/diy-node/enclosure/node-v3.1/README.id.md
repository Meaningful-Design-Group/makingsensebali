[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# Node V3.1 — bodi V3 versi sekrup

***DIY Environmental Sensor Node V3.1** milik Fab Lab Bali. Folder ini bernama `bayu-v6` sampai September 2026.*

Rumah luar ruang cetak 3D untuk node kualitas udara DIY Making Sense Bali.
*Bayu* — angin. Iterasi pertama dari generasi V3: bodi ringkas, elektronik
hibrida, opsi LoRa, dirakit dengan sekrup.

> **Status: digantikan oleh [`../node-v3.2/`](../node-v3.2/) (= Node V3.2).**
> v7 adalah bodi yang sama tanpa sekrup, dengan dudukan dinding dan tiang yang menyatu di bagian belakang.
> Versi itu menghilangkan 11 sekrup dan satu bagian cetak dari proses perakitan serta tidak memerlukan braket.
> **Bangun v7.** Folder ini tetap dipertahankan karena STL di sini sudah dipakai di lapangan, dan
> pembangun yang memegang cangkang v6 tetap membutuhkan langkah perakitan untuk unit yang dimilikinya.

**Lisensi:** CERN-OHL-W-2.0 (perangkat keras) · CC-BY-SA-4.0 (dokumentasi ini)
**Sumber:** *Dokumentasi Teknis: DIY Environmental Sensor Node V3*, Fab Lab Bali, September 2026. Dokumen ini adalah versi asli berbahasa Indonesia; versi Inggris dan Spanyol diterjemahkan darinya.

![Tampilan terurai rakitan Node V3.1](img/01-exploded-v31.png)

## Daftar isi

- [Penamaan](#penamaan)
- [Mengapa generasi V3 ada](#mengapa-generasi-v3-ada)
- [Asal usul bentuknya](#asal-usul-bentuknya)
- [Arsitektur hibrida](#arsitektur-hibrida)
- [Aliran udara](#aliran-udara)
- [Varian bodi](#varian-bodi)
- [Bagian cetak](#bagian-cetak)
- [Pengaturan cetak](#pengaturan-cetak)
- [Daftar komponen](#daftar-komponen)
- [Pengkabelan](#pengkabelan)
- [Perakitan](#perakitan)
- [Pemasangan](#pemasangan)
- [Masalah yang diketahui pada berkas ini](#masalah-yang-diketahui-pada-berkas-ini)
- [Apa yang diubah v7 dan mengapa](#apa-yang-diubah-v7-dan-mengapa)
- [Yang masih kurang dari dokumentasi ini](#yang-masih-kurang-dari-dokumentasi-ini)

## Penamaan

Dua sistem penamaan bertabrakan di pohon folder ini dan keduanya masih dipakai.

| Repo ini | Fab Lab Bali | Apa itu |
|---|---|---|
| `node-v3.1/` (di sini) | **Node V3.1** | Rakitan bersekrup, braket dinding terpisah. Sudah digantikan. |
| `node-v3.2/` | **Node V3.2** | Sepenuhnya tanpa sekrup, dudukan terintegrasi. Bangun yang ini. |

Berikut adalah *enam berkas STL yang sama*, diverifikasi bita per bita terhadap rilis V3.1
Fab Lab Bali, bukan disimpulkan dari nama berkas:

| Repo ini | Rilis hulu |
|---|---|
| `stl/Main_Body.stl` | `MAIN BODY 2 ANTENNA.stl` |
| `stl/Main_Body_Cover.stl` | `TOP COVER.stl` |
| `stl/HM_Cover_and_Mainboard_Mount.stl` | `COVER HM3301 + BRACKET BOARD.stl` |
| `stl/Body_Air_Outlet.stl` | `OUTFLOW DUCT HM3301.stl` |
| `stl/BME_Cover.stl` | `COVER BME680.stl` |
| `stl/Body_Bracket.stl` | `BRACKET TO WALL.stl` |

Repo ini menerima mesh tersebut pada September 2026 tanpa dokumen yang menjelaskannya,
itulah sebabnya README ini nyaris seluruhnya berisi penanda TODO sampai sekarang. Perhatikan bahwa
salinan di repo adalah bodi **antena ganda**; pihak hulu juga merilis varian antena tunggal yang
tidak pernah dikomit di sini.

Sementara itu garis keturunan rumah sensor terhitung v1-box → v2-lantern → v3-gourd → v4-column →
v5 pine cone → v6 → v7, dan Fab Lab Bali menghitung generasi node secara utuh V1 → V2 → V3.1 →
V3.2. Kedua penghitungan itu tidak berhubungan. Ini juga *bukan*
[`../node-v2/`](../node-v2/), yang merupakan generasi
kedua dari keseluruhan node pada cangkang yang sama sekali berbeda.

## Mengapa generasi V3 ada

Stasiun berkelas regulasi harganya lebih mahal daripada yang bisa dikumpulkan sendiri oleh banjar,
sekolah atau kelompok warga mana pun di Bali —
[tabel tier](../../README.id.md) kampanye menempatkannya di
USD 5,000–25,000+. Merakit satu unit dari sensor modular murah adalah alternatif yang jelas,
dan seluruh pohon folder ini membahas bagian yang sebenarnya sulit: kotaknya.

V3 dirancang untuk menjawab empat masalah yang dihadapi node-node sebelumnya.

1. **Ketersediaan komponen.** Mengunci diri pada satu PCB atau satu modul membuat proses membangun
   terhenti ketika stok lokal habis. V3 menerima beberapa pilihan.
2. **Hisap balik udara buang.** Di dalam rumah yang ringkas, udara keluaran sensor PM sendiri tertarik
   kembali ke lubang masuknya, dan node mengukur udara yang sudah diukurnya.
3. **Perakitan dan perawatan di lapangan.** Rakitan dengan banyak sekrup kecil lambat difabrikasi
   dan lebih menyusahkan lagi untuk diservis di atap. *(V3.1 tidak menyelesaikan ini — v7 iya.)*
4. **Fleksibilitas pemasangan.** Dinding dan tiang membutuhkan pengikat berbeda tanpa harus mencetak
   bagian tambahan. *(V3.1 juga tidak menyelesaikan ini — v7 iya.)*

Tujuan: menekan biaya per unit cukup jauh sehingga seorang warga bisa memasang node di dindingnya
sendiri, dan cukup banyak node terpasang sehingga Bali punya data udara skala mikro yang tersebar
dan kredibel.

> **Tentang klaim biaya.** Dokumen sumber menyebut penghematan ~90% terhadap stasiun industri
> standar, dalam dua bentuk berbeda (biaya sasis di satu tempat, biaya total di tempat
> lain) dan tidak menyebut stasiun pembanding mana pun. Sebagaimana tertulis, klaim itu tidak dapat
> diperiksa. Terhadap rentang Tier 0 kampanye ini sendiri, penghematan sebenarnya lebih curam
> daripada 90%, jadi klaim itu kemungkinan konservatif alih-alih dibesar-besarkan — tetapi siapa pun
> yang mengutipnya ke pemberi dana harus lebih dulu menyebut stasiun tertentu beserta harganya.
> <!-- TODO: pilih stasiun pembanding bernama + harganya, nyatakan ulang klaim itu sekali saja, dalam satu bentuk. -->

## Asal usul bentuknya

Tata letak kompartemen diambil dari arsitektur rumah **stasiun Smart Citizen Kit
(SCK 2.3)** — sumber menyebut modularitas, kebersihan dan minimalisme sebagai hal yang dipinjam.
Tulang punggung kalibrasi kampanye ini sendiri adalah **SCK 2.1**
([tabel tier](../../README.id.md)), jadi ini adalah peminjaman dari lini produknya
dan bukan dari stasiun persis yang dipakai sebagai pembanding pengukuran node.

![Diagram terurai stasiun SCK](img/12-sck-station-exploded.png)

> Bagian referensi pada dokumen sumber berbunyi *"desain fisik dan penempatan kompartemen
> pada **Node V2**…"* — salinan-tempel dari dokumen V2. Bagian itu menjelaskan V3.
> <!-- TODO: salah ketik di hulu, sudah dilaporkan. -->

Referensi: [Smart Citizen Kit and Station: An open environmental monitoring system for citizen participation and scientific experimentation](https://www.sciencedirect.com/science/article/pii/S2468067219300203)

## Arsitektur hibrida

Satu cangkang, beberapa daftar komponen — sehingga proses membangun tidak terhenti ketika satu
bagian kehabisan stok secara lokal.

**Papan utama** — Seeed Grove Shield for XIAO (tanpa solder, pasang-dan-pakai) atau PCB kustom DIY
(lebih murah, perlu disolder).

**Mikrokontroler** — XIAO ESP32-C3 atau ESP32-S3; ESP32-C3 atau ESP32-S3 Supermini pada PCB
DIY; atau Seeed ESP32-S3 dengan LoRa terpasang di papan.

> **Supermini dan XIAO tidak kompatibel pin pada PCB DIY.** I²C berada di D4/D5 untuk
> XIAO dan D8/D9 untuk Supermini. Periksa [Pengkabelan](#pengkabelan) sebelum menyolder.

![Pilihan papan utama di dalam bay](img/10-mainboard-options.png)

**Sensor lingkungan** — breakout Bosch BME680 atau Seeed Grove BME680. Pada v6 keduanya memakai
`BME_Cover.stl` yang sama; v7 memisahkannya menjadi dua penutup.

| Breakout Bosch | Seeed Grove |
|---|---|
| ![Tata letak internal dengan Bosch BME680](img/08-layout-bme680-bosch.png) | ![Tata letak internal dengan Seeed BME680](img/09-layout-bme680-seeed.png) |

**Sensor PM** — hanya Seeed Studio HM3301, pada I²C. Tidak ada alternatif yang dirancang.

**Daya** — USB Type-C, 5 V DC.

## Aliran udara

Udara luar ditarik masuk melalui lubang masuk di sisi bawah menuju kipas HM3301 sendiri. Udara yang
sudah diukur keluar melalui `Body_Air_Outlet.stl`, yang membawanya ke samping, menjauh dari lubang
masuk, sehingga tidak langsung terukur ulang.

| | |
|---|---|
| ![Lubang masuk sisi bawah dan saluran keluaran](img/05-underside-intake-outflow.png) | ![Detail saluran keluaran](img/06-outflow-duct-detail.png) |

![Lubang-lubang di sisi bawah](img/07-underside-ports.png)

Ini memperbaiki hisap balik. Ini **tidak** mengatasi dua kegagalan yang ditemukan ketika node
sebelumnya dikolokasikan dengan Smart Citizen Kit — lubang masuk sisi bawah yang meratakan puncak
PM, dan pemanasan sendiri BME680 di dalam bay elektronik. Keduanya tidak berubah di v6 maupun
di v7. Lihat
[catatan jujur v7 tentang hal ini](../node-v3.2/README.id.md),
yang mencakup seluruh generasi V3.

## Varian bodi

| Radio ganda (2 antena) | Radio tunggal (1 antena) |
|---|---|
| ![Bodi antena ganda](img/03-body-dual-antenna.png) | ![Bodi antena tunggal](img/04-body-single-antenna.png) |
| 2 port pigtail SMA: Wi-Fi 2.4 GHz + LoRa sub-GHz | 1 port pigtail SMA: Wi-Fi 2.4 GHz |

Hanya bodi antena ganda yang dikomit ke repo ini, sebagai `stl/Main_Body.stl`. Varian
antena tunggal ada di
[rilis hulu V3.1](https://drive.google.com/drive/folders/1vudckcW-5sOKlDBSPK77gQ5bCxbDxIM9);
jika Anda membutuhkannya, pilih [v7](../node-v3.2/), yang menyertakan keduanya.

## Bagian cetak

Enam bagian. Ukuran dibaca langsung dari mesh, jadi nyata; semua yang ada di
[Pengaturan cetak](#pengaturan-cetak) tidak.

| Bagian | Berkas | Kotak batas (mm) | Segitiga | Fungsi |
|---|---|---|---|---|
| Bodi utama | `stl/Main_Body.stl` | 113.9 × 92.0 × 28.9 | 5,242 | Sasis, antena ganda |
| Penutup atas | `stl/Main_Body_Cover.stl` | 117.9 × 88.0 × 51.9 | 13,324 | Penutup bersekrup / pelindung |
| Penutup HM3301 + dudukan papan | `stl/HM_Cover_and_Mainboard_Mount.stl` | 83.9 × 40.1 × 8.9 | 1,522 | Penutup PM, menopang papan utama |
| Saluran keluaran | `stl/Body_Air_Outlet.stl` | 46.0 × 26.0 × 12.0 | 1,548 | Mengarahkan buangan PM menjauh dari lubang masuk |
| Penutup BME680 | `stl/BME_Cover.stl` | 44.0 × 24.0 × 2.0 | 984 | Menahan BME680 |
| Braket dinding | `stl/Body_Bracket.stl` | 76.4 × 15.0 × 28.0 | 882 | Terpisah, dibaut ke dinding |

![Bagian-bagian cetak](img/11-printed-parts-v31.png)

Bagian-bagian diekspor dalam koordinat rakitan, bukan koordinat cetak — sebagian besar memiliki
Z minimum negatif. Slicer akan menurunkannya ke bed, tetapi berkasnya tidak diorientasikan lebih
dulu untuk pencetakan.

<!-- TODO: dimensi luar dan massa setelah dirakit -->

## Pengaturan cetak

<!-- TODO: tidak satu pun dari ini diketahui. Tidak ada satu pun nilai nyata di bawah ini. -->

| | |
|---|---|
| Material | TODO — **PETG atau ASA**. PLA merayap dan melendut di bawah matahari Bali |
| Tinggi lapisan | TODO |
| Dinding / perimeter | TODO |
| Isian | TODO |
| Suhu nozzle / bed | TODO |
| Penyangga | TODO — sebutkan per bagian |
| Orientasi cetak | TODO — sebutkan per bagian; berpengaruh pada kekedapan air dan kekuatan braket |
| Perkiraan waktu cetak / filamen | TODO |

Nyatakan kebutuhan mesin dalam istilah bengkel — volume cetak minimum, diameter nozzle —
alih-alih berdasarkan merek printer.

## Daftar komponen

Lihat [`bom.csv`](bom.csv) untuk versi yang terbaca mesin.

| # | Komponen | Spesifikasi / model | Jml | Catatan |
|---|---|---|---|---|
| 1 | Prosesor utama | XIAO ESP32-C3 / ESP32-S3, Supermini, atau Seeed ESP32-S3 dengan LoRa | 1 | Master pada bus I²C |
| 2 | Papan dasar | Seeed Grove Shield **atau** PCB kustom DIY | 1 | |
| 3 | Sensor PM | Seeed Studio HM3301 | 1 | Laser PM2.5 / PM10, I²C, 0x40 |
| 4 | Sensor lingkungan | Bosch BME680 **atau** Seeed Grove BME680 | 1 | Suhu / RH / tekanan / gas, I²C, 0x76 atau 0x77 |
| 5 | Masukan daya | USB Type-C | 1 | 5 V DC |
| 6 | Pigtail | SMA female ke IPEX / U.FL | 1–2 | 1 untuk radio tunggal, 2 untuk ganda |
| 7 | Antena eksternal | 2.4 GHz (+ LoRa sub-GHz jika ganda) | 1–2 | |
| 8 | Set kabel | JST-XH dan Grove 4-pin | 1 set | |
| 9 | Sekrup mesin M3×10 | Kepala rata baja karbon | 4 | Penutup HM3301 |
| 10 | Sekrup mesin M2×5 | Kepala rata baja karbon | 2 | Braket papan, sesuai jenis papan |
| 11 | Sekrup mesin M2×10 | Kepala rata baja karbon | 3 | Penutup BME680 |
| 12 | Sekrup mesin M3×10 | Kepala rata baja karbon | 2 | Penutup atas |

11 sekrup per node, dan itulah seluruh alasan v7 ada.

> Sumber menyebut NINDEJIN sebagai merek sekrup dan hanya menyebut "kepala rata" — tanpa jenis
> alur (Phillips, hex, slot). Padanan apa pun dari toko perkakas bisa dipakai.
> <!-- TODO: jenis alur sekrup; harga; spesifikasi pengikat dinding untuk braket. -->

**Tanpa harga.** BoM V3 pada dokumen sumber tidak punya kolom harga.
[BoM Node V2](../node-v2/bom.csv) memuat harga IDR dari pembelian
sebelumnya pada papan utama yang berbeda — hanya sebagai orde besaran, bukan penawaran harga.

## Pengkabelan

Sama untuk seluruh generasi V3. Alih-alih menduplikasinya, lihat
**[v7 § Pengkabelan](../node-v3.2/README.id.md)** — tiga pilihan papan utama, lengkap dengan skematik
dan tampilan breadboard.

> Satu koreksi yang dibawa ke sana: tabel Grove Shield pada dokumen sumber memberi HM3301
> **3.3 V**, sementara skematiknya sendiri memberi **5 V**. Skematiknya yang benar — kipas dan
> laser HM3301 tidak akan berjalan pada 3.3 V.

## Perakitan

Konvensional, berbasis sekrup. Setiap bagian internal ditahan oleh pelat dan sekrup kecil.

1. **Bodi.** Pasang pigtail SMA melalui lubang antena pada `Main_Body.stl` dan
   kencangkan murnya dari luar.
2. **BME680.** Masukkan sensor ke ceruknya di lantai bodi. Pasang `BME_Cover.stl`
   dan kencangkan dengan **3 × M2×10**.
3. **HM3301 dan saluran.** Dudukkan sensor PM. Pasang `Body_Air_Outlet.stl` ke dalam saluran
   buang. Pasang `HM_Cover_and_Mainboard_Mount.stl` di atas sensor dan kencangkan dengan
   **4 × M3×10**.
4. **Papan utama.** Pasang papan pada standoff `HM_Cover_and_Mainboard_Mount.stl`
   dengan **2 × M2×5**. Sambungkan kabel I²C dari BME680 dan HM3301 serta kabel daya USB-C,
   lalu klipkan pigtail ke port U.FL.
5. **Tutup.** Pasang `Main_Body_Cover.stl` dan kencangkan dengan **2 × M3×10**, disekrup dari luar
   bodi.
6. **Braket.** Baut `Body_Bracket.stl` ke bagian belakang bodi.

> Bagian perakitan V3.1 pada dokumen sumber menyebut `V3.1_Top_Cover.stl` dan
> `V3.1_Wall_Bracket_Separate.stl`. **Berkas semacam itu tidak ada** dalam rilis — nama
> sebenarnya adalah `TOP COVER.stl` dan `BRACKET TO WALL.stl`, di sini `Main_Body_Cover.stl` dan
> `Body_Bracket.stl`. Sudah dikoreksi di atas. <!-- TODO: kesalahan di hulu, sudah dilaporkan. -->

<!-- TODO: foto rakitan yang sesungguhnya. Setiap gambar di sini adalah render CAD. -->

## Pemasangan

**Hanya dinding datar.** Pasang `Body_Bracket.stl` ke dinding dengan sekrup dan fischer, lalu
gantungkan bodi pada braket tersebut.

Tidak ada opsi tiang pada v6 — tidak ada jalur cable tie terintegrasi. Jika lokasinya berupa tiang
atau pohon, gunakan [v7](../node-v3.2/#mounting).

<!-- TODO: spesifikasi pengikat braket — ukuran sekrup, jarak, jenis fischer. Kapasitas beban. -->

## Masalah yang diketahui pada berkas ini

Ditemukan melalui inspeksi mesh pada 2026-09-01, sebelum publikasi:

- **`Main_Body.stl` tidak kedap (watertight)** — 4 tepi terbuka. Slicer biasanya memperbaikinya
  diam-diam, yang berarti hasilnya bergantung pada keputusan slicer Anda. Ekspor ulang dari sumber.
  **Sudah diperbaiki di v7**: bodinya tidak punya tepi terbuka.
- **`Body_Air_Outlet.stl` punya segitiga degenerat (berluas nol).** Tidak berbahaya dalam praktik,
  tetapi salah secara kosmetik. **Tidak diperbaiki di v7** — bagian itu dibawa tanpa perubahan.
- **Tidak ada sumber CAD yang dipublikasikan.** Lihat [`cad/README.md`](cad/README.md). Hambatan yang sama di v7.

## Apa yang diubah v7 dan mengapa

| | v6 / Node V3.1 | v7 / Node V3.2 |
|---|---|---|
| Penutup atas | Sekrup dari luar | Snap-fit detent, 3 titik |
| Penahan sensor dan papan | Sekrup M2/M3 menembus pelat | Kait snap-fit kantilever |
| Pemasangan dinding | Braket cetak terpisah, dibaut | Lubang sekrup menyatu pada bodi |
| Pemasangan tiang | Tidak didukung | Slot cable tie terintegrasi |
| Berkas braket papan | 1 | 2 — jarak kait berbeda tiap papan |
| Berkas penutup BME680 | 1 | 2 — footprint Bosch dan Seeed berbeda |
| Bagian cetak per node | 6 | 5 |
| Sekrup per node | 11 | 0 |

![Perbandingan Node V3.1 dan V3.2](img/02-v31-v32-comparison.png)

Sensor yang bisa dibuka tanpa obeng akan mendapat pembersihan sensor PM-nya. Yang membutuhkan
obeng berukuran tepat, dan empat sekrup yang tidak boleh menggelinding jatuh dari atap, tidak.

## Yang masih kurang dari dokumentasi ini

- Sumber CAD — hambatan utama untuk replikasi.
- Pengaturan cetak. Tidak ada yang diketahui.
- Biaya, dalam mata uang apa pun.
- Foto perakitan. Setiap gambar adalah render.
- Jenis alur sekrup; spesifikasi pengikat dinding dan kapasitas beban braket.
- Dimensi luar dan massa setelah dirakit; waktu pembuatan.
- Tingkat proteksi masuknya air — ketahanan cipratan diklaim, tanpa uji atau peringkat yang disebut.
- Stasiun pembanding bernama untuk klaim biaya ~90%.
- Varian bodi antena tunggal, yang ada di hulu tetapi tidak dikomit di sini.

---

*Making Sense Bali · Chapter Fab City Bali · dituanrumahi oleh Fab Lab Bali.
Perangkat keras CERN-OHL-W-2.0 · dokumentasi CC-BY-SA-4.0.*
