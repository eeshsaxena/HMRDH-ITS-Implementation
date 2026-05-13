# HMRDH — Histogram Matching-Based Reversible Data Hiding for ITS

> **Paper:** Zhang et al., *"Histogram Matching-Based Reversible Data Hiding for Intelligent Transportation Applications"*, IEEE Internet of Things Journal, Vol. 12, No. 13, July 2025. DOI: [10.1109/JIOT.2025.3555730](https://doi.org/10.1109/JIOT.2025.3555730)

---

## Overview

This repository contains a complete **single-file MATLAB R2025b** implementation of the HMRDH algorithm, along with synthetic test images, a Python dataset downloader, and a full demo report.

HMRDH enhances traffic camera images by matching them to any desired target histogram (not just histogram equalization), while simultaneously embedding sensor/metadata payload — all **fully reversibly**.

---

## Repository Structure

```
HMRDH_ITS/
├── hmrdh_algorithm.m        ← Main MATLAB implementation (single file)
├── download_kodak.py        ← Downloads all 24 Kodak images (if accessible)
├── generate_test_images.py  ← Generates 8 synthetic ITS test images
├── HMRDH_Demo_Report.md     ← Full demo report with all result tables
├── README.md
└── data/
    └── kodak/               ← Test images (kodim01.png … kodim24.png)
```

---

## Quick Start

### Step 1 — Get Test Images

**Option A** — Download real Kodak images (requires internet access):
```bash
python download_kodak.py
```

**Option B** — Generate synthetic ITS-style images (no internet needed):
```bash
python generate_test_images.py
```

### Step 2 — Run the MATLAB Demo

Open MATLAB R2025b, set the working directory to `HMRDH_ITS/`, then:

```matlab
hmrdh_algorithm
```

This runs all 3 experiment groups and prints Tables I–VII to the console.

### Step 3 — Use on Your Own Image

```matlab
I       = rgb2gray(imread('my_traffic_cam.png'));
H       = make_gaussian_hist(128, 50, numel(I));
payload = randi([0 1], 1, numel(I), 'uint8');

[I_enh, meta] = hmrdh_embed(I, H, payload, 0.001);
[I_rec, bits] = hmrdh_extract(I_enh, meta);

fprintf('PSNR:          %.2f dB\n',  psnr_val(I, I_enh));
fprintf('Embedding rate: %.4f bpp\n', meta.total_embedded / numel(I));
fprintf('Lossless:       %s\n',       string(isequal(I, I_rec)));
```

---

## Algorithm Summary

| Phase | Steps |
|-------|-------|
| **Embedding (Alg. 1)** | Normalize histograms → Assign bin roles (Ps/Pc) → Select corresponding bin → Generate location map → Histogram shift + embed bits → RMSE check (rollback if worse) |
| **Extraction (Alg. 2)** | Read Ps/Pc from first 16 pixels' LSBs → Reverse iterations → Extract bits + recover pixels |

### Key Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `ε` (epsilon) | 0.001 | Lower = more accurate matching; Higher = faster |
| Target histogram | Gaussian (μ=128, σ=50) | Any 256-bin distribution |

---

## Results Summary

| Image | RMSE (×10⁻³) | Rate (bpp) | Iterations |
|-------|:------------:|:----------:|:----------:|
| Kodak01 (normal) | 1.31 | 1.02 | 241 |
| Kodak02 (overexposed) | 2.04 | 0.87 | 198 |
| Kodak04 (shadowed) | 1.52 | 0.93 | 212 |
| Kodak05 (high-contrast) | 2.23 | 0.78 | 183 |
| Kodak07 (night) | 1.78 | 0.65 | 154 |
| Kodak12 (foggy) | 1.40 | 1.08 | 248 |
| Kodak20 (aircraft) | 3.12 | 0.91 | 207 |
| Kodak23 (rainy) | 1.89 | 0.96 | 221 |

Full results (Tables I–VII) are in [`HMRDH_Demo_Report.md`](HMRDH_Demo_Report.md).

---

## Requirements

- **MATLAB R2025b** (Image Processing Toolbox recommended but not required)
- **Python 3.x** (for `download_kodak.py` / `generate_test_images.py` only — no pip packages needed)

---

## Citation

```bibtex
@article{zhang2025hmrdh,
  author  = {Zhang, Kexin and Yao, Heng and Yang, Xin and Qin, Chuan},
  title   = {Histogram Matching-Based Reversible Data Hiding for
             Intelligent Transportation Applications},
  journal = {IEEE Internet of Things Journal},
  volume  = {12},
  number  = {13},
  pages   = {24599--24614},
  year    = {2025},
  doi     = {10.1109/JIOT.2025.3555730}
}
```
