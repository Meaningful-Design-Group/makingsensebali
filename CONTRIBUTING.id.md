[English](CONTRIBUTING.md) · **Bahasa Indonesia** · [Español](CONTRIBUTING.es.md)

# Berkontribusi untuk Making Sense Bali

Ini kampanye penginderaan lingkungan yang dipimpin komunitas untuk Bali, dijangkarkan oleh
[Fab Lab Bali](https://fablabbali.com). Sensor, laporan warga, dan perkakas yang
menghubungkan keduanya.

Anda tidak perlu jadi pemrogram untuk berkontribusi, dan tidak perlu izin untuk mulai.
Buka *issue*, atau buka *pull request*.

## Satu aturan sebelum yang lain: jangan pernah mempublikasikan identitas orang

Repositori ini menangani laporan warga; sebagian dari mereka menyatakan terus terang bahwa
mereka takut bersuara soal pembakaran di dekat rumahnya. Anonimitas di sini bukan pelengkap
— itulah alasan orang mau ikut sama sekali.

Jadi, dalam *issue*, *pull request*, tangkapan layar, tempelan log, atau data uji apa pun:

- **Tanpa nomor telepon, nama, akun WhatsApp, atau ID obrolan.**
- **Tanpa koordinat persis sebuah laporan.** Laporan yang terbit sengaja digeser ke titik
  tengah desa. Jangan membatalkan itu, dan jangan menempelkan koordinat presisi dari data
  privat ke *issue* publik.
- **Tanpa foto asli dari laporan.** Foto yang terbit sudah dihapus EXIF-nya; aslinya tetap
  privat.
- **Tanpa stempel waktu sampai menit** pada laporan individual. Waktu presisi pada laporan
  berulang menandai seseorang dengan rutinitas.

Jika Anda menemukan hal di atas sudah terlanjur terbit di repo ini, itu masalah keamanan,
bukan *bug* — kirim surel ke tomas@fab.city, jangan buka *issue* publik.

## Apa yang berguna

**Perangkat keras.** Desain wadah, varian node sensor, perbaikan lapangan. Aturannya
*sumber dan ekspor, selalu*: sertakan `.step` atau `.scad` bersama `.stl`, agar lab
berikutnya bisa memodifikasi, bukan sekadar mencetak. Kontribusi ekspor-saja tetap
diterima tetapi ditandai belum lengkap. Mulai dari `hardware/diy-node/enclosure/` — desain
saat ini `bayu-v6/`, dan `previous-iterations/` menjelaskan kesalahan tiap desain lama.

**Firmware dan perkakas.** `hardware/diy-node/firmware/`, `tools/`, `worker/`. Catatan
integrasi Smart Citizen ada di `docs/`. Jika menambah kanal sensor, baca dulu aturan
kejujuran data: tanpa nol palsu, tanpa NaN, rata-ratakan alih-alih mencuplik. Pembacaan
yang gagal tidak boleh menyumbang apa pun, karena di dasbor `PM = 0` tidak bisa dibedakan
dari udara bersih.

**Terjemahan.** Semua terbit dalam bahasa Inggris, Indonesia, dan Spanyol. Inggris adalah
acuan; dua lainnya terjemahan. String ada di `i18n.js` — tambahkan kunci ke ketiga kamus
atau situs akan diam-diam mundur ke acuan. Mutu bahasa Indonesia paling penting: situs ini
melayani warga Bali lebih dahulu.

**Pengetahuan komunitas.** [`docs/community-knowledge.id.md`](docs/community-knowledge.id.md)
disarikan dari grup komunitas [Bali Air Dispatch](https://baliairdispatch.com/). Jika ada
yang keliru, kurang lengkap, atau dinyatakan dengan keyakinan melebihi buktinya,
memperbaikinya adalah kontribusi nyata.

**Replikasi.** Jika Anda membangun node, atau mem-*fork* ini menjadi *Making Sense [kota
Anda]*, beri tahu kami. Apa yang harus Anda ubah demi mendapatkan komponen secara lokal
lebih berguna bagi lab berikutnya daripada apa pun yang bisa kami tulis dari sini.

**Melapor.** Kontribusi paling ringan dan yang menjadi tumpuan kampanye:
[laporkan apa yang Anda lihat](https://bali-aq.fab.city/report). Anonim, tanpa akun, tanpa
nomor telepon.

## Cara mengirim

1. *Fork*, buat cabang dari `main`. Beri nama sesuai fungsinya — `hardware/…`, `docs/…`,
   `fix/…`.
2. Satu *pull request* untuk satu urusan. PR yang memperbaiki *bug* *sekaligus* merapikan
   folder itu dua PR.
3. Jelaskan apa yang Anda ubah dan, untuk perangkat keras, diuji terhadap apa. "Dicetak dan
   dipasang tiga minggu di Denpasar" lebih bernilai daripada render.
4. Bahasa Indonesia atau Spanyol boleh dipakai di *issue* dan deskripsi PR. Komentar kode
   dalam bahasa Inggris, agar terbaca oleh kontributor seluas mungkin.

Tidak ada CLA. Dengan berkontribusi, Anda setuju karya Anda dirilis di bawah lisensi
berikut.

## Lisensi

| Apa | Lisensi |
|---|---|
| Perangkat lunak — firmware, perkakas, situs | MIT |
| Perangkat keras — CAD, STL, desain mekanis | CERN-OHL-W-2.0 |
| Dokumentasi, gambar, pengetahuan komunitas | CC-BY-SA-4.0 |
| Data laporan yang terbit | CC-BY-4.0 |

CERN-OHL-W bersifat resiprokal lemah: bengkel boleh membuat dan menjual node secara
komersial, dan perbaikan pada desainnya kembali ke proyek.

## Peta repositori

```
hardware/diy-node/     wadah (bayu-v6 yang terkini), firmware, perkakas
dashboard/             dasbor sensor langsung
docs/                  metodologi, pengetahuan komunitas, catatan platform
reports/               alur laporan dan dasbor moderasi
worker/                Cloudflare worker proksi OpenAQ
data/                  data laporan terbit dan termoderasi — ditulis mesin
i18n.js                semua string situs, tiga bahasa
```

`data/` ditulis oleh sinkronisasi otomatis. Jangan disunting manual.

## Kontak

Tomas Diez — tomas@fab.city. Untuk apa pun yang menyangkut identitas atau keselamatan
seseorang, kirim surel alih-alih membuka *issue*.
