# CHANGELOG FIXES — Resume Classifier

File ini mendokumentasikan setiap bug, temuan data quality, dan perbaikan selama project berjalan.

## Konvensi Penulisan

```
### Fix #N — Judul Singkat: Gejala + Akar
```

| Field | Deskripsi |
|-------|-----------|
| Tanggal | `YYYY-MM-DD` |
| File | File yang diubah |
| Masalah | Deskripsi gejala/bug |
| Akar | Penyebab utama |
| Fix | Solusi yang diterapkan |
| Verifikasi | Cara memverifikasi fix bekerja |
| Pelajaran | Insight untuk sesi berikutnya |
| Deploy | Phase / commit terkait |

## Log

### Fix #1 — Finalisasi v1.0.0: paths hard-coded + exec() + artifacts orphan + confidence belum terdokumentasi

| Tanggal | File | Masalah | Akar | Fix | Verifikasi | Pelajaran | Deploy |
|---------|------|---------|------|-----|------------|-----------|--------|
| 2026-11-04 | scripts/*.py, predict.py, .gitignore, requirements.txt, reports/CLEANUP_REPORT.md | 12 skrip memakai path absolut C:/Users/ardut/...; phase10 memakai exec(); 2 artifacts joblib orphan (102MB+613B); 11 empty dirs; confidence_score tidak terdokumentasi di FINAL_REPORT | Sesi pengembangan eksploratif single-machine; audit sebelumnya mengubah requirements.txt jadi unpinned | Path env-var (RESUME_CSV/RESUME_DATA_DIR, default data/); exec() diganti `from predict import predict_resume`; requirements.txt dipin dari lock (11 paket langsung + 136 lock penuh); artifacts orphan & empty dirs dihapus; blok caveat confidence ditambahkan | 17/17 pytest pass; CLI ENGINEERING (score -0.4034); sha256 ketiga artifacts aktif identik sebelum-sesudah; fitur 535,692 dimensi tetap | Jangan hapus artifacts tanpa dokumentasi dulu (lihat PROJECT_UNKNOWN_RESOLUTION U1); catat juga kesalahan sesi sendiri bila ada regresi | Phase final (pre-v1.0.0) |
