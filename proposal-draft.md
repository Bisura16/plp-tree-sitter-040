# cek-web: Quality Gate Berbasis Tree-sitter untuk Repositori Web Enterprise (Python & JavaScript)

**Bimo Surya Anggara** · D4 Teknik Informatika, Politeknik Negeri Bandung, 2B · Draf proposal proyek (tidak dinilai)

## 1. Masalah
Di tim web enterprise, basis kode besar dan dikerjakan banyak developer, tetapi tiga hal ini masih sering lolos saat code review: (a) sisa debug (`print`, `console.log`) yang ikut ke produksi dan bisa mencetak data pengguna ke log, (b) komentar `TODO`/`FIXME` tanpa nomor tiket sehingga utang teknis tidak terlacak, dan (c) fungsi yang terlalu panjang sehingga sulit di-review. Yang mengalami: developer dan reviewer, yang kini mengeceknya manual. Bukti dari Tugas 6: `cek.py` pada `psf/requests` (37 file) melaporkan 63 temuan di 16 file, yaitu 56 fungsi panjang dan 7 TODO. Proyek ini memperluas `cek.py` menjadi tool CI dengan aturan modular dan dukungan dua bahasa.

## 2. Kenapa tidak cukup dengan AI saja
Meminta AI me-review setiap commit itu probabilistik (hasil bisa berbeda tiap kali) dan berbiaya token per file. Tool tree-sitter deterministik, hampir tanpa biaya, dan bisa dijalankan otomatis di setiap commit lewat CI. Catatan AI di laporan saya menunjukkan alasannya: pada keenam tugas selalu ada kesalahan AI (mis. query import melewatkan `import numpy as np`, regex TODO salah menangkap `# MASTODON`), jadi aturan harus dibuktikan dengan kasus uji, bukan dipercaya begitu saja. Pembagian kerjanya: AI membantu menulis aturan, tree-sitter menjalankannya. Regex/`grep` juga tidak cukup: `grep "print("` ikut menangkap komentar, string, dan `pprint(`, sedangkan query tree-sitter hanya cocok dengan node `call`.

## 3. Bahasa, framework, dan grammar
Python (Flask/Django/FastAPI) dengan `tree-sitter-python`, dan JavaScript (Express) dengan `tree-sitter-javascript`; keduanya ada di PyPI. Pengayaan: TypeScript (`tree-sitter-typescript`).

## 4. Contoh kode
| Harus terdeteksi | Tidak boleh terdeteksi |
| --- | --- |
| `print(user.email)` di view Flask | `# print(debug)`, `"print(x)"`, `pprint(u)`, `laporan.print_all()` |
| `console.log("debug", req.body)` | `// console.log(x)`, `logger.info(req.id)`, `console.error(e)` |
| `# TODO: validasi input`, `# FIXME perbaiki` | `# TODO(#142): migrasi`, `x = "TODO bukan komentar"` |

## 5. Rancangan query (sudah dicoba dan berjalan pada contoh di atas)
**Aturan 1, debug tertinggal.** Python (dari Tugas 3):
```scheme
(call function: (identifier) @fn (#eq? @fn "print")) @temuan
```
JavaScript:
```scheme
(call_expression
  function: (member_expression
    object: (identifier) @obj
    property: (property_identifier) @prop)
  (#eq? @obj "console") (#match? @prop "^(log|debug)$")) @temuan
```
**Aturan 2, TODO tanpa tiket** (tiket berbentuk `(#123)` atau `(ABC-123)`):
```scheme
((comment) @c (#match? @c "\\b(TODO|FIXME)\\b")
            (#not-match? @c "\\((#|[A-Z]+-)[0-9]+\\)"))
```
**Aturan 3, fungsi panjang:** query `function_definition` dari Tugas 6, ditambah `function_declaration`, `arrow_function`, dan `method_definition` untuk JavaScript; ambang batas dapat diatur (bawaan 30 baris).

## 6. Bentuk output
Laporan terminal `file:baris: ATURAN: pesan` (seperti `cek.py` sekarang), opsi `--format json`, dan kode keluar 1 jika ada temuan, sehingga bisa dipasang sebagai langkah di GitHub Actions. Komentar `cek:ignore` dan daftar folder yang dikecualikan (`scripts/`, `tests/`) untuk kasus yang disengaja.

## 7. Cara evaluasi
Repositori uji: `pallets/flask` (Python), `expressjs/express` (JavaScript), dan satu proyek kuliah saya sendiri. Per aturan, ambil 20 temuan acak dan cek manual untuk menghitung presisi (target ≥ 90%). Untuk melihat recall, sisipkan 10 pelanggaran buatan ke repo uji dan hitung berapa yang terdeteksi. Bandingkan jumlah temuan dan false positive dengan baseline `grep`, serta catat waktu eksekusi terhadap ukuran repo. Setiap aturan punya folder uji berisi kasus positif dan negatif seperti tabel di atas.

## 8. Rencana kerja (5 pertemuan) dan risiko
| Minggu | Kegiatan |
| --- | --- |
| 1 | Pecah `cek.py` menjadi aturan modular; Aturan 1 untuk Python dan JavaScript beserta kasus uji |
| 2 | Aturan 2 (TODO tanpa tiket) dan Aturan 3 (fungsi panjang) untuk kedua bahasa |
| 3 | Output JSON, kode keluar, dan workflow GitHub Actions |
| 4 | Evaluasi pada Flask, Express, dan proyek kuliah; perbandingan dengan `grep` |
| 5 | Perbaikan dari hasil evaluasi, laporan, dan demo |

**Risiko:** (1) bentuk fungsi JavaScript beragam (arrow, method, anonim); mitigasi: lihat pohonnya dengan `jelajah.py` dulu, jangan menebak nama node (pelajaran Tugas 3). (2) `console.log` yang disengaja pada skrip CLI; mitigasi: pengecualian per folder dan `cek:ignore`. (3) Tree-sitter hanya paham sintaks, sehingga `log = print` atau pemanggilan lewat alias tidak terdeteksi; dicatat sebagai keterbatasan di laporan.