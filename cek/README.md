# cek.py — pendeteksi TODO, fungsi panjang, dan sintaks error

CLI kecil untuk file Python berbasis tree-sitter. Untuk setiap file `.py` di sebuah folder, `cek.py` melaporkan:

1. Komentar yang mengandung `TODO` atau `FIXME` (query dengan `#match?`).
2. Fungsi yang lebih dari 30 baris (dari `start_point` dan `end_point`).
3. File yang pohonnya mengandung error sintaks (`root_node.has_error`), lengkap dengan baris pertama yang bermasalah.

## Memasang dependensi

```bash
pip install tree-sitter tree-sitter-python
```

Diuji dengan Python 3.14, `tree-sitter` 0.26, dan `tree-sitter-python` 0.25.

## Menjalankan

```bash
python cek.py <folder>
```

Contoh pada folder uji bawaan:

```bash
python cek.py uji
```

Menyimpan hasil ke file (di PowerShell, dengan encoding UTF-8):

```powershell
python cek.py <folder> | Out-File -Encoding utf8 output.txt
```

## Contoh output

```
uji\panjang.py:1: FUNGSI PANJANG: panjang (37 baris)
uji\rusak.py:1: SINTAKS ERROR
uji\todo.py:1: TODO: # TODO: tambah validasi
uji\todo.py:3: TODO: # FIXME: salah
```

Format tiap baris: `file:baris: jenis temuan`.

## Catatan

- Semua fungsi dihitung, termasuk metode di dalam kelas dan fungsi bersarang. Fungsi bersarang bisa muncul dua kali (sekali sebagai dirinya, sekali sebagai bagian fungsi induknya).
- Folder `venv`, `.venv`, `.git`, `node_modules`, dan `__pycache__` dilewati.
- Batas fungsi panjang diatur di konstanta `BATAS_BARIS` (default 30).
- Karakter yang tidak bisa didekode dicetak dengan pengganti (`errors="replace"`), jadi tidak ada `UnicodeDecodeError`.
- Hanya file `.py` yang diperiksa.

## Hasil pada repo nyata

Dijalankan pada repo [psf/requests](https://github.com/psf/requests): hasil lengkap ada di `output_requests.txt`. Dua file dicek manual:

- `src/requests/hooks.py`: satu TODO di baris 29, sama dengan hitungan manual.
- `src/requests/api.py`: fungsi `request` dimulai di baris 24 dan berakhir di baris 71, yaitu 48 baris, sama dengan hasil `cek.py`.