[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md)

# Iterasi sebelumnya

Desain enklosur yang sudah pensiun, disimpan karena kegagalannyalah pengetahuan
yang paling bisa dipakai ulang dalam repositori ini. Persyaratan di
[`../node-v3.2/`](../node-v3.2/) ada karena salah satu desain ini mengajarkannya.

> **Tidak satu pun dari ini adalah desain saat ini.** Bangun [`../node-v3.2/`](../node-v3.2/).

| Iterasi | Dulunya apa | Pensiun karena |
|---|---|---|
| [v5 "pine cone"](README.v5-and-earlier.id.md) | Cangkang OpenSCAD parametrik, sepuluh daun yang saling tumpang tindih; pembuangan air hujan dan ventilasi adalah geometri yang sama. Sumber: [`enclosure.scad`](enclosure.scad) · STL di [`stl/`](stl/) · render di [`img/`](img/) | Digantikan oleh lini Fab Lab Bali V3, yang memang itulah yang benar-benar dibangun dan diterapkan Fab Lab Bali. v5 memecahkan brief aliran udara secara lebih meyakinkan daripada V3 — lihat catatan di bawah. |
| [`archive/`](archive/) — v1-box, v2-lantern, v3-gourd, v4-column | Empat bentuk yang lebih awal, masing-masing dengan catatannya sendiri | Masing-masing digantikan oleh yang berikutnya; disimpan sebagai catatan tentang apa yang pernah dicoba |

**Node V2 tidak ada di sini.** Ia berada di [`../node-v2/`](../node-v2/), saudara dari
desain saat ini, karena ia adalah sebuah generasi *node* dan bukan iterasi enklosur, dan
karena evaluasi lapangannya masih merupakan dokumen yang paling banyak dikutip di pohon ini.

## Catatan v5 yang layak disimpan

v5 menempatkan setiap slot pernapasan dalam bayangan hujan sebuah sisik dan menjalankan
cerobong dari masukan rendah setinggi BME680 ke pembuangan tinggi di bawah tudung. Itu persis
topologi aliran udara yang diminta oleh ko-lokasi Node V2, dan lini V3 — yang menggantikan v5
— **tidak** meneruskannya: V3 mempertahankan masukan di sisi bawah dan membiarkan BME680
berada di samping radio.

Jadi v5 pensiun dengan alasan yang baik (ia bukan yang dibangun Fab Lab Bali, dan ia juga
tidak pernah diko-lokasikan), tetapi ia tidak begitu saja lebih buruk daripada yang
menggantikannya. Siapa pun yang mengangkat kembali masalah aliran udara sebaiknya membaca
[`README.v5-and-earlier.id.md`](README.v5-and-earlier.id.md)
dan [`../../enclosure-research/DESIGN_LOG.md`](../../enclosure-research/DESIGN_LOG.md)
sebelum memulai dari nol.

## Penamaan

Dua penghitungan yang tidak berhubungan melintasi folder ini.

- **Lini enklosur**, yang merupakan tempat `archive/` dan v5 berada:
  v1-box → v2-lantern → v3-gourd → v4-column → v5 "pine cone". Ia berhenti di v5.
  Desain-desain berikutnya dalam repo ini sempat dinomori `bayu-v6` dan `bayu-v7`; skema itu
  sudah pensiun dan folder-folder tersebut kini menjadi [`../node-v3.1/`](../node-v3.1/) dan
  [`../node-v3.2/`](../node-v3.2/). Tabel pemetaannya ada di [`../README.id.md`](../README.id.md).
- **Generasi node Fab Lab Bali**: Node V1 → V2 → V3.1 → V3.2. Jalur terpisah yang
  berbagi elektronik dan firmware.

Jangan membaca `archive/v2-lantern/` dan [`../node-v2/`](../node-v2/) sebagai generasi yang sama.
Keduanya berbagi satu angka dan tidak ada yang lain.
