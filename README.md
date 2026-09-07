# Data Pipeline - Automobile EDA Dataset

Pipeline ini membaca dataset mentah `automobileEDA_dirty_training.csv`, melakukan
pemeriksaan awal, data cleaning, dan data transformation, lalu menyimpan hasilnya
sebagai `automobileEDA_processed.csv`. Alur mengikuti konsep ETL:

| Tahap | Proses |
|---|---|
| Extract | Membaca dataset CSV dari `data/raw/` (`load_data`) |
| Transform | Memeriksa (`inspect_data`), membersihkan (`clean_data`), dan mentransformasi (`transform_data`) data |
| Load | Menyimpan processed dataset ke `data/processed/` (`save_data`) |

Cara menjalankan:
```
pip install -r requirements.txt
python src/pipeline.py
```

> **Catatan:** bagian di bawah ini berisi kerangka temuan yang perlu diisi dengan
> angka aktual setelah menjalankan `pipeline.py` terhadap file
> `automobileEDA_dirty_training.csv` yang sebenarnya (file tersebut belum tersedia
> saat pipeline ini disusun, sehingga angka pasti tidak bisa dicantumkan di sini).

## 1. Temuan Pemeriksaan Awal Dataset
- Ukuran awal dataset: **[isi: jumlah baris x kolom]**
- Kolom yang memiliki missing values: **[isi berdasarkan output `inspect_data`]**
- Jumlah baris yang terduplikasi: **[isi berdasarkan output]**
- Kolom dengan tipe data yang belum sesuai: **[misal `transaction_date` masih berupa teks dengan format tanggal tidak konsisten]**
- Penulisan kategori yang belum konsisten: **[misal `make` memiliki variasi huruf besar/kecil, contoh: `alfa-romero` vs `ALFA-ROMERO`]**
- Permasalahan lain: **[isi jika ditemukan]**

## 2. Data Cleaning
- Permasalahan yang ditemukan: **[isi]**
- Kolom yang dibersihkan: **[isi]**
- Metode cleaning yang digunakan:
  - Kolom kategorikal (huruf besar/kecil, spasi berlebih) → diseragamkan dengan `.str.lower().str.strip()`
  - `transaction_date` → dikonversi ke tipe datetime dengan `pd.to_datetime(dayfirst=True, format="mixed")`
  - Duplicate records → dihapus dengan `drop_duplicates()`
  - Missing values kategorikal → diisi dengan modus kolom terkait
  - Missing values numerik (`stroke`, `bore`, `compression-ratio`, `peak-rpm`) → diisi dengan rata-rata (mean)
  - Missing values numerik (`horsepower`, `price`, `normalized-losses`) → diisi dengan median (lebih tahan terhadap outlier)
- Alasan pemilihan metode: median digunakan untuk kolom yang berpotensi memiliki outlier (harga, tenaga mesin) agar tidak bias, sedangkan mean digunakan untuk kolom numerik yang distribusinya relatif normal. Modus digunakan untuk kolom kategorikal karena nilai yang paling sering muncul adalah representasi paling wajar.
- Jumlah data sebelum dan sesudah cleaning: **[isi berdasarkan output `clean_data`]**

## 3. Data Transformation
| Kolom | Metode Transformasi | Alasan |
|---|---|---|
| Seluruh kolom numerik | Min-Max Scaling | Menyamakan skala antar fitur numerik untuk keperluan pemodelan |
| `body-style`, `drive-wheels` | One-Hot Encoding | Kategori tidak memiliki urutan (nominal) |
| `make`, `engine-type`, `fuel-system` | Frequency Encoding | Jumlah kategori cukup banyak, frequency encoding menjaga informasi proporsi tanpa menambah terlalu banyak kolom |
| `aspiration`, `engine-location`, `horsepower-binned` | Label Encoding | Jumlah kategori sedikit (biner/rendah) |

Contoh nilai sebelum-sesudah transformasi: **[isi dengan contoh nilai aktual dari output `transform_data`, misal untuk `horsepower` sebelum: 111.0, sesudah (hasil Min-Max Scaling): 0.xx]**

## 4. Struktur Project
```
data-pipeline-assignment/
├── data/
│   ├── raw/
│   │   └── automobileEDA_dirty_training.csv
│   └── processed/
│       └── automobileEDA_processed.csv
├── src/
│   └── pipeline.py
├── documentation/
│   └── data-flow-diagram.png
├── README.md
└── requirements.txt
```

## 5. Data Flow Diagram
Lihat `documentation/data-flow-diagram.png`:

Raw Dataset → Load Data → Data Inspection → Data Cleaning → Data Transformation → Processed Dataset
