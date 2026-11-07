# Analisis Keterlambatan Pengiriman E-Commerce

Studi kasus operasional dengan SQL (SQLite) dan dashboard HTML interaktif. Tujuannya adalah menentukan wilayah tujuan yang sebaiknya diselidiki lebih dulu untuk mengurangi jumlah pesanan yang terlambat.

## Hasil

Dari 99.441 pesanan sumber, 96.470 memenuhi kriteria analisis. Sebanyak 6.534 pesanan (6,8%) tiba setelah tanggal estimasi. Cakupan tanggal tiba aktual adalah 11 Oktober 2016 hingga 17 Oktober 2018.

| Prioritas | Wilayah tujuan | Pesanan dianalisis | Terlambat | Tingkat |
| --- | --- | ---: | ---: | ---: |
| 1 | São Paulo (SP) | 40.494 | 1.820 | 4,5% |
| 2 | Rio de Janeiro (RJ) | 12.350 | 1.495 | 12,1% |
| 3 | Minas Gerais (MG) | 11.354 | 519 | 4,6% |

- **Mulai dari São Paulo** jika targetnya mengurangi jumlah pesanan terdampak. Wilayah ini menyumbang sekitar 28% dari seluruh pesanan terlambat. Rio de Janeiro juga layak diselidiki karena tingkat keterlambatannya lebih tinggi dan volumenya cukup besar.
- **Gunakan Agustus 2018 sebagai titik awal investigasi di São Paulo.** Ada 358 keterlambatan dari 3.859 pesanan (9,3%). Sebagai pembanding, September mencatat 100% dengan hanya 20 pesanan yang tercatat. Jumlah pesanan dan cakupan periode penting saat membaca grafik.
- **Bandingkan Januari–Agustus 2017 dan 2018.** Dengan minimal 500 pesanan per wilayah per periode, São Paulo dan Rio de Janeiro tetap di peringkat pertama dan kedua. Jumlah pesanan terlambat di São Paulo naik dari 243 dari 8.237 pesanan menjadi 1.238 dari 23.846. Di Rio de Janeiro, angkanya naik dari 88 dari 2.777 menjadi 1.136 dari 6.856. Selisih jumlah keterlambatan menyempit dari 155 menjadi 102.

Untuk menyelidiki penyebab, pisahkan waktu dari pembelian hingga serah terima ke kurir dan dari serah terima hingga tiba. Bandingkan segmen dengan volume memadai. Hasil ini mengukur pola berdasarkan wilayah tujuan. Penentuan penyebab memerlukan analisis lanjutan.

## Definisi dan cakupan

- Satu baris analisis mewakili satu pesanan. Tabel pesanan dan pelanggan digabung melalui customer_id, dengan validasi kunci dan jumlah pesanan unik.
- Pesanan masuk cakupan jika berstatus delivered dan kedua tanggal dapat dibaca oleh SQLite. Ada 2.971 pesanan sumber di luar cakupan ini.
- Pesanan terlambat jika tanggal tiba aktual melewati tanggal estimasi pada tingkat tanggal kalender. Pesanan yang tiba pada tanggal estimasi masuk kategori tepat waktu.
- Tingkat keterlambatan adalah jumlah pesanan terlambat dibagi jumlah pesanan yang memenuhi kriteria. Tren bulanan mengikuti tanggal tiba aktual.
- Data bersifat historis. Wilayah adalah negara bagian tujuan pelanggan.

## Jalankan

Buka [dashboard.html](dashboard.html) di browser. Pemilih wilayah mengubah grafik tren bulanan. Dashboard HTML dapat dibuka secara lokal dan datanya sudah tertanam.

Untuk membangun ulang, unduh [dataset publik Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) sebagai ZIP, simpan sebagai olist-source.zip di folder proyek, lalu jalankan dari folder tersebut dengan Python 3.

    python build.py

Skrip membuat ulang dashboard.html dan delivery.sqlite, dengan validasi satu baris per pesanan dan rekonsiliasi total per wilayah serta per bulan. Untuk memakai arsip dari lokasi lain, berikan lokasinya sebagai argumen.

| Berkas SQL | Isi |
| --- | --- |
| sql/01_delivery_orders.sql | Tampilan satu baris per pesanan yang memenuhi kriteria |
| sql/02_state_priority.sql | Peringkat wilayah berdasarkan jumlah pesanan terlambat |
| sql/03_monthly_trend.sql | Tren keterlambatan per wilayah dan bulan tiba |
| sql/04_priority_sensitivity.sql | Peringkat dengan cakupan waktu berbeda dan batas minimum volume |

Database yang dihasilkan sudah memuat tampilan delivery_orders. Jalankan berkas 02–04 untuk meninjau hasil query di SQLite. Arsip sumber dan database hasil build dikecualikan dari Git melalui .gitignore.

## Tes

Jalankan tes SQL dengan data sintetis. Arsip Olist tidak diperlukan.

    python -m unittest discover -s tests -v
