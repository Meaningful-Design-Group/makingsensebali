[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# Casing

Rumah luar ruang untuk node kualitas udara DIY Making Sense Bali. Semua yang ada di
folder ini sudah dicetak dan dipasang di lapangan.

> ## Bangun [`node-v3.2/`](node-v3.2/).
> Perakitan tanpa sekrup, dudukan pemasangan menyatu dengan badan, lima bagian cetak.
> Fab Lab Bali, September 2026.

| | |
|---|---|
| [`node-v3.2/`](node-v3.2/) | **Kanonik.** Snap-fit penuh tanpa sekrup, dudukan dinding dan tiang terintegrasi. Delapan STL diterbitkan, sumber CAD masih belum ada. |
| [`node-v3.1/`](node-v3.1/) | Digantikan oleh v3.2. Badan yang sama, dirakit dengan 11 sekrup ditambah braket dinding terpisah. Dipertahankan karena unitnya masih terpasang di lapangan. |
| [`node-v2/`](node-v2/) | Pensiun. Dibangun, dipasang, dikolokasi dengan Smart Citizen Kit, dan **gagal dua kali**. Dipertahankan demi catatan kegagalannya, yang merupakan hal paling bisa dipakai ulang di sini. |
| [`previous-iterations/`](previous-iterations/) | Silsilah casing sebelum V3: v1-box → v2-lantern → v3-gourd → v4-column → v5 pine cone. Pensiun, terdokumentasi. |
| [`LICENSES/`](LICENSES/) | Perangkat keras CERN-OHL-W-2.0 · Dokumentasi CC-BY-SA-4.0 · Perangkat lunak MIT |

**Mencari pekerjaan meru-tower parametrik?** Itu adalah studi desain terpisah yang belum
pernah dicetak dan tersimpan di [`../enclosure-research/`](../enclosure-research/). Lihat
[Dua jalur](#dua-jalur-dan-mengapa-keduanya-terpisah) di bawah.

## Penamaan

Fab Lab Bali memberi nomor pada generasi node secara utuh. Repo ini dulu memberi nomor
iterasi casing secara terpisah sebagai `bayu-vN`, yang menghasilkan dua nama untuk satu
objek dan tabrakan dengan lini riset. **Skema `bayu-vN` sudah dipensiunkan.** Pemetaannya,
untuk siapa pun yang membaca commit, issue atau folder Drive lama:

| Folder sekarang | Dulu | Sebutan Fab Lab Bali |
|---|---|---|
| `node-v3.2/` | `node-v3.2/` | Node V3.2 |
| `node-v3.1/` | `node-v3.1/` | Node V3.1 |
| `node-v2/` | `node-v2/` | Node V2 |

`node-v3.1/` dan Node V3.1 adalah enam file STL yang sama, diverifikasi byte demi byte
terhadap rilis Fab Lab Bali — bukan disimpulkan dari nama file.

Perhatikan bahwa `previous-iterations/archive/v2-lantern/` **bukan** `node-v2/`. Silsilah
casing lama dan generasi node sama-sama melewati angka 2 dan tidak berkaitan.

## Dua jalur, dan mengapa keduanya terpisah

| | Folder ini | [`../enclosure-research/`](../enclosure-research/) |
|---|---|---|
| Asal | Fab Lab Bali | Studi parametrik Juni 2026 |
| Bentuk | Badan horizontal ringkas | Menara meru modular, kisi gyroid |
| Aliran udara | Asupan dari sisi bawah; BME680 di samping radio | Cerobong: BME680 di bawah, XIAO di atas, semua bukaan menghadap ke bawah |
| Rantai perkakas | CAD manual, rilis STL | Generator build123d + Rhino |
| **Dicetak** | **Ya — terpasang di lapangan** | **Tidak. Sama sekali belum.** |
| Tervalidasi secara termal | Tidak | Tidak |

Kedua sistem penomoran memakai `vN` polos, dan itulah sebabnya keduanya tidak lagi berbagi folder.

**Posisi jujurnya.** Evaluasi lapangan Node V2 menghasilkan dua persyaratan: asupan udara
dari atas atau dari sisi yang terbuka, dan BME680 dikeluarkan dari ruang elektronik dan
diberi pelindung. Generasi V3 tidak memenuhi keduanya — ia memperbaiki masalah ketiga,
tersedotnya kembali udara buangan, dengan sebuah saluran. Jalur riset memenuhi keduanya, di
layar, tanpa pernah dicetak. Tidak ada jalur yang sudah selesai. `node-v3.2/` bersifat
kanonik karena itulah satu-satunya desain yang bisa dibangun siapa pun hari ini, bukan
karena pertanyaan aliran udara sudah terjawab.

Sampai sebuah v3.2 dikolokasi dengan SCK, **perlakukan kanal suhu dan kelembapannya sebagai
belum terverifikasi dan harap maklum puncak PM akan terbaca rendah.** Itu bukan alasan untuk
berhenti memasang — justru itulah alasan kampanye ini mewajibkan satu minggu pertama
kolokasi untuk setiap node baru.

## Sebelum ini siap direplikasi

Diurutkan berdasarkan apa yang menghambat pemakaian ulang, bukan berdasarkan usaha:

1. **Terbitkan sumber CAD untuk v3.2** (dan v3.1). Hanya STL berarti tidak ada seorang pun
   di luar Fab Lab Bali yang bisa memodifikasinya. Ini lebih penting pada v3.2: setiap
   sambungan adalah snap fit yang disetel presisi, dan kait kantilever tidak bisa disetel
   ulang dari sekumpulan segitiga mentah.
2. **Kolokasikan sebuah v3.2 dengan SCK selama seminggu** dan terbitkan Δ°C serta jeda PM-nya.
   Entah badan ringkas ini mengulangi galat V2 atau tidak, dan tidak ada yang tahu.
3. **Ekspor ulang `OUTFLOW_DUCT_HM3301.stl`** — 1 tepi terbuka, 1 segitiga degenerat,
   terbawa tanpa perubahan dari v3.1 tempat hal itu sudah ditandai.
4. **Pengaturan cetak.** Material lebih dulu: PLA tidak akan bertahan di atap tropis, dan
   pada desain snap-fit, orientasi cetak menentukan apakah kaitnya selamat saat perakitan.
5. **Biaya.** Tidak ada harga untuk build ini dalam mata uang apa pun. Itu pertanyaan
   pertama yang diajukan setiap banjar.
6. **Foto perakitan.** Setiap gambar di kedua folder adalah render CAD.

Poin 1 dan 2 menentukan apakah Fab Lab lain bisa membangun ini dan memercayai apa yang
dilaporkannya, atau hanya melihat-lihat fotonya.

## CAD Node V2

`Meaningful-Design-Group/Enclosure-DIY-Node-V2` berisi tepat satu file,
`Enclosure DIY Node V2.f3z`, tanpa README dan tanpa lisensi. File itu menjawab TODO
penghambat yang ada di dokumentasi Node V2 sendiri:

```bash
git clone https://github.com/Meaningful-Design-Group/Enclosure-DIY-Node-V2 /tmp/v2cad
mkdir -p hardware/diy-node/enclosure/node-v2/cad
cp "/tmp/v2cad/Enclosure DIY Node V2.f3z" hardware/diy-node/enclosure/node-v2/cad/
```

Setelah itu, arsipkan repo tersebut dengan deskripsi yang mengarah ke sini. Satu rumah publik per desain.

## Teks lisensi

Lihat [`LICENSES/README.md`](LICENSES/README.md) — dua perintah `curl`. Jangan
menyalinnya dengan tangan.
