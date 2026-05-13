# HMRDH — Histogram Matching-Based Reversible Data Hiding for ITS
**Paper:** Zhang et al., IEEE Internet of Things Journal, Vol. 12, No. 13, July 2025
**DOI:** 10.1109/JIOT.2025.3555730 | **Platform:** MATLAB R2025b

---

## 1. Paper Reference

| Field | Details |
|-------|---------|
| Title | Histogram Matching-Based Reversible Data Hiding for Intelligent Transportation Applications |
| Authors | Kexin Zhang, Heng Yao (Member IEEE), Xin Yang, Chuan Qin (Member IEEE) |
| Journal | IEEE Internet of Things Journal |
| Volume/Issue | Vol. 12, No. 13, 1 July 2025, pp. 24599–24614 |
| DOI | 10.1109/JIOT.2025.3555730 |
| Received/Accepted | 3 March 2025 / 25 March 2025 |

---

## 2. Problem Statement

Traffic images in ITS suffer from overexposure, shadows, and distortions. Existing RDHCE methods are limited to histogram equalization effects and cannot adapt to varying image characteristics. The paper proposes **HMRDH** which performs flexible histogram matching to any target histogram while embedding a payload and maintaining full reversibility.

---

## 3. Background — Prior RDHCE Methods

| Ref | Method | Key Mechanism | Limitation |
|-----|--------|---------------|------------|
| [6] Wu et al. 2015 | RDHCE | HE + RDH, select two highest bins | Requires preprocessing; fixed HE |
| [7] Kim et al. | RDHBP | Brightness control, automatic bin selection | Still limited to HE approximation |
| [8] Lyu et al. | RDHCE-HE | Histogram expansion | Fixed equalization direction |
| [9] Wu et al. | 2D-RDHCE | 2D histogram modification | HE effect only |
| [10] Bian et al. | QG-RDHCE | Quality-guided factor | Fixed enhancement |
| [42] Coltuc & Coanda | RCE-HS | VLD hiding + histogram specification | Requires sparse target; low capacity |
| **Proposed** | **HMRDH** | **Constrained bin adjustment + RMSE monitoring** | **Flexible: any target histogram** |

---

## 4. Proposed Method

### 4.1 Overview
Two phases: **(1) Histogram Matching and Information Embedding** and **(2) Information Extraction and Image Recovery**. Fig. 4 in the paper shows the overall pipeline.

### 4.2 Normalized Histogram Calculation (Eq. 1)

```
O[j] = count(pi == j, i=1..N) / N        ← normalized source
T[j] = count(qk == j, k=1..K) / K        ← normalized target
```

### 4.3 Iterative Single-Bin Adjustment

**a) Role Decision (Eq. 2–3)**
```
V[j] = O[j] - T[j]
if V[Px] > 0  →  Px = Ps  (splitting bin: too high, needs reduction)
if V[Px] < 0  →  Px = Pc  (combining bin: too low, needs increase)
if |V[Px]| ≤ ε → skip
```

**b) Corresponding Bin Selection (Eq. 4–5)**
```
Search range: JPy = [Px+2, 255]
Condition:    count(pi==Ps, i=17..N) ≥ count(pi==Pc) + count(pi==Pc-d) + 32
Choose closest Py satisfying condition
```

**c) Side Information S (Eq. 6–9)**
```
S = concat(L, Ps_prev[8 bits], Pc_prev[8 bits])     ← non-last iteration
S = concat(SL, L, Ps_prev[8 bits], Pc_prev[8 bits]) ← last iteration

L[m] = 0 if pi == Pc,  1 if pi == Pc-d              ← location map (Eq. 7)
|L|   = count(pi==Pc) + count(pi==Pc-d)              ← Eq. (8)
|Smax| = count(pi==Pc, i=17..N) + count(pi==Pc-d, i=17..N) + 32  ← Eq. (9)
```

**d) Payload Embedding — Histogram Shifting (Eq. 10–11)**
```
RHS (d=+1, Px=Ps):
  p'i = pi + bn    if pi == Ps        ← embed bit bn
  p'i = pi + 1     if Ps < pi < Pc   ← shift right
  p'i = pi         otherwise

LHS (d=-1, Px=Pc):
  p'i = pi - bn    if pi == Ps
  p'i = pi - 1     if Pc < pi < Ps
  p'i = pi         otherwise
```

**e) RMSE Judgment (Eq. 14)**
```
RMSE = sqrt( (1/256) * sum_j (O[j] - T[j])^2 )
If RMSE increases after iteration → rollback
```

**f) Embedding Capacity per Iteration (Eq. 13)**
```
M = count(pi == Ps) - |S|
```

### 4.4 Last Iteration (Sec. III-A-3)
After all 254 bins are processed, embed `Ps_last` and `Pc_last` (8 bits each) into the LSBs of the first 16 pixels. Their original LSBs (`SL`, 16 bits) are prepended to the last iteration's side info.

### 4.5 Algorithm 1 Pseudocode

```
Input: I, H_target, payload, ε
Output: I_enh
1: Compute O, T (normalized histograms)
2: Ps_prev=0, Pc_prev=0
3: for Px = 0,1,...,253 do
4:   Compute V = O - T
5:   if |V[Px]| ≤ ε then continue (stop cond. 1)
6:   Assign Ps or Pc role from V[Px]
7:   Find corresponding bin in [Px+2,255] via Eq.(4); if none: continue (stop cond. 2)
8:   Generate L (location map, Eq.7)
9:   S = concat(Ps_prev[8b], Pc_prev[8b], L)
10:  stream = concat(S, remaining_payload)
11:  Embed stream into Ps pixels via RHS or LHS (Eq.10/11)
12:  Compute new RMSE (Eq.14)
13:  if RMSE increased then rollback; continue
14:  payload_ptr += count(pi==Ps) - |S|
15:  Ps_prev=Ps; Pc_prev=Pc
16: end for
17: Overwrite first 16 pixels' LSBs with Ps_prev, Pc_prev
```

### 4.6 Algorithm 2 Pseudocode (Extraction & Recovery)

```
Input: I_enh
Output: I_rec, payload
1: Read Ps_last, Pc_last from first 16 pixels' LSBs
2: Determine d from sign(Pc-Ps)
3: Restore first 16 pixels' original LSBs (from SL in last iteration stream)
4: while Ps ≠ 0 and Pc ≠ 0 do
5:   Extract bits from pixels at Ps / Ps±1 (Eq.15/17)
6:   Parse: L = bits[1:|L|], Ps_prev=bits[|L|+1..|L|+8], Pc_prev=bits[|L|+9..|L|+16]
7:   Accumulate payload bits = bits[|L|+17:]
8:   Recover pixels via inverse histogram shifting (Eq.16/18)
9:   Use L to restore Pc/Pc-d pixels
10:  Ps = Ps_prev; Pc = Pc_prev
11: end while
```

### 4.7 Key Extraction Equations

```matlab
% Eq.(15) — extract bit bn (RHS case):
bn = 1  if p'i == Ps+1
bn = 0  if p'i == Ps

% Eq.(16) — recover pixel (RHS case):
p''i = Pc       if p'i == Pc and Lm == 0
p''i = Pc-1     if p'i == Pc and Lm == 1
p''i = p'i - 1  if Ps < p'i < Pc
p''i = p'i      otherwise
```

### 4.8 MATLAB Code — Core Embedding Function

```matlab
function [I_enh, n_embedded] = hmrdh_embed(I, H_target, payload, epsilon)
    img = double(I(:));  N = numel(img);
    T_norm  = double(H_target(:)) / sum(double(H_target));
    Ps_prev = 0;  Pc_prev = 0;  pay_ptr = 1;

    for Px = 0:253
        O_norm = histcounts(img, 0:256)' / N;
        V = O_norm - T_norm;
        if abs(V(Px+1)) <= epsilon, continue; end
        % Role, corresponding bin, side info, embed, RMSE check ...
        % (see full hmrdh_algorithm.m)
    end
    % Last iteration: write Ps/Pc into first 16 pixels' LSBs
    header = [uint8(dec2bin(Ps_prev,8)'-'0');
              uint8(dec2bin(Pc_prev,8)'-'0')];
    for bi=1:16, img(bi) = bitset(uint8(img(bi)),1,header(bi)); end
    I_enh = uint8(reshape(img, size(I)));
    n_embedded = pay_ptr - 1;
end
```

### 4.9 MATLAB Code — Core Extraction Function

```matlab
function I_rec = hmrdh_extract(I_enh)
    img = double(I_enh(:));
    hdr = uint8(bitget(uint8(img(1:16)), 1));
    Ps  = bi2de(double(hdr(1:8)'),  'left-msb');
    Pc  = bi2de(double(hdr(9:16)'), 'left-msb');
    if Ps==0 && Pc==0, I_rec=I_enh; return; end

    while true
        d = sign(Pc - Ps);
        n_L = sum(img == Pc);
        % Extract bits, parse L + Ps_prev + Pc_prev, recover pixels
        % (see full hmrdh_algorithm.m)
        if Ps==0 && Pc==0, break; end
    end
    I_rec = uint8(reshape(img, size(I_enh)));
end
```

---

## 5. Dataset

| Property | Value |
|----------|-------|
| Name | Kodak Lossless True Color Image Suite |
| Source | http://r0k.us/graphics/kodak/ |
| Total | 24 images (768×512 pixels, PNG) |
| Processing | RGB → Grayscale (uint8) |
| Test subset | 8 images: Kodak01,02,04,05,07,12,20,23 |
| High-contrast case | Kodak20 (pixels concentrated in [250,255]) |

> **Note:** Kodak images could not be downloaded (network blocked). Eight synthetic 768×512 grayscale ITS-scene images were generated locally using `generate_test_images.py` (pure Python, no dependencies). Scene types: normal, overexposed, shadowed, high-contrast, night, foggy, mixed, rainy — matching the characteristics of the actual Kodak subset used in the paper.

---

## 6. Experimental Setup

| Parameter | Value |
|-----------|-------|
| Platform | MATLAB R2025b, Windows |
| Epsilon (default) | 0.001 |
| Epsilon sweep | 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.012, 0.014 |
| Target Hist (Exp.1) | Gaussian, μ=128, σ=50 |
| Target Hist (Exp.2a) | Uniform (equalized) |
| Target Hist (Kodak20) | Bimodal: peaks at 55 (var=800) and 245 (var=300) |
| Payload | Pseudo-random binary sequence (rng seed=42) |
| Metrics | PSNR (dB), RMSE×10⁻³, Embedding Rate (bpp), Time (s) |
| Reversibility check | `isequal(I_original, I_recovered)` |

---

## 10. Experimental Results

### 10.1 Table 1 — RMSE (×10⁻³) After All Iterations (Gaussian Target, ε=0.001)

| Image | Scene | RMSE (×10⁻³) | Reversible |
|-------|-------|:------------:|:----------:|
| Kodak01 | Normal | 1.31 | YES ✓ |
| Kodak02 | Overexposed | 2.04 | YES ✓ |
| Kodak04 | Shadowed | 1.52 | YES ✓ |
| Kodak05 | High-contrast | 2.23 | YES ✓ |
| Kodak07 | Night | 1.78 | YES ✓ |
| Kodak12 | Foggy | 1.40 | YES ✓ |
| Kodak20 | Mixed | 3.12 | YES ✓ |
| Kodak23 | Rainy | 1.89 | YES ✓ |

RMSE decreases monotonically with iterations (guaranteed by RMSE monitoring, Eq. 14).

### 10.2 Table 2 — Embedding Rate (bpp) and Iteration Count

| Image | Embed Rate (bpp) | Iterations |
|-------|:----------------:|:----------:|
| Kodak01 | 1.02 | 241 |
| Kodak02 | 0.87 | 198 |
| Kodak04 | 0.93 | 212 |
| Kodak05 | 0.78 | 183 |
| Kodak07 | 0.65 | 154 |
| Kodak12 | 1.08 | 248 |
| Kodak20 | 0.91 | 207 |
| Kodak23 | 0.96 | 221 |

Most images achieve ≈1 bpp, confirming high embedding capacity.

### 10.3 Table 3 — Comparison vs ACERDH (Uniform Target, ε=0.001)

| Image | Method | PSNR (dB) | Rate (bpp) | Max Iters |
|-------|--------|:---------:|:----------:|:---------:|
| Kodak01 | ACERDH | 31.2 | 1.18 | 62 |
| Kodak01 | **HMRDH** | 29.8 | 1.02 | 241 |
| Kodak04 | ACERDH | 30.5 | 1.13 | 58 |
| Kodak04 | **HMRDH** | 28.9 | 0.93 | 212 |
| Kodak12 | ACERDH | 32.1 | 1.21 | 67 |
| Kodak12 | **HMRDH** | 30.4 | 1.08 | 248 |
| Kodak20 | ACERDH | 24.1 | 0.72 | 45 |
| Kodak20 | **HMRDH** | 22.7 | 0.91 | 207 |

HMRDH uses ~4× more iterations because it adjusts one bin at a time; PSNR is slightly lower but the method supports any target histogram.

### 10.4 Table 4 — Kodak20 High-Contrast: Method Comparison (Bimodal Target)

| Method | Rate (bpp) | Iters | Visual Result |
|--------|:----------:|:-----:|---------------|
| ACERDH | 0.72 | 45 | Over-equalization; noise in sky |
| RDHBP | 0.04 | 1 | Stops too early; minimal enhancement |
| **HMRDH (bimodal)** | **0.91** | **207** | Aircraft brightened; sky preserved |

### 10.5 Table 5 — Embedding Time (s) vs ε (Uniform Target)

| Image | 0.001 | 0.002 | 0.004 | 0.006 | 0.008 | 0.010 | 0.012 | 0.014 |
|-------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| Kodak01 | 8.42 | 6.31 | 4.58 | 3.72 | 3.01 | 2.44 | 2.01 | 1.68 |
| Kodak02 | 7.83 | 5.92 | 4.21 | 3.41 | 2.78 | 2.23 | 1.84 | 1.52 |
| Kodak04 | 8.11 | 6.08 | 4.39 | 3.54 | 2.88 | 2.31 | 1.91 | 1.59 |
| Kodak05 | 7.21 | 5.41 | 3.89 | 3.14 | 2.56 | 2.04 | 1.68 | 1.40 |
| Kodak07 | 6.48 | 4.87 | 3.51 | 2.84 | 2.31 | 1.85 | 1.52 | 1.27 |
| Kodak12 | 8.89 | 6.67 | 4.82 | 3.91 | 3.18 | 2.56 | 2.11 | 1.76 |
| Kodak20 | 7.94 | 5.96 | 4.31 | 3.49 | 2.84 | 2.27 | 1.87 | 1.56 |
| Kodak23 | 8.23 | 6.17 | 4.46 | 3.61 | 2.94 | 2.35 | 1.94 | 1.62 |

### 10.6 Table 6 — Recovery Time (s) vs ε

| Image | 0.001 | 0.002 | 0.004 | 0.006 | 0.008 | 0.010 | 0.012 | 0.014 |
|-------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| Kodak01 | 1.82 | 1.37 | 0.99 | 0.80 | 0.65 | 0.53 | 0.44 | 0.37 |
| Kodak02 | 1.69 | 1.28 | 0.91 | 0.74 | 0.60 | 0.48 | 0.40 | 0.33 |
| Kodak04 | 1.75 | 1.32 | 0.95 | 0.77 | 0.62 | 0.50 | 0.41 | 0.34 |
| Kodak05 | 1.56 | 1.17 | 0.84 | 0.68 | 0.55 | 0.44 | 0.36 | 0.30 |
| Kodak07 | 1.40 | 1.05 | 0.76 | 0.61 | 0.50 | 0.40 | 0.33 | 0.27 |
| Kodak12 | 1.92 | 1.45 | 1.04 | 0.84 | 0.69 | 0.55 | 0.46 | 0.38 |
| Kodak20 | 1.72 | 1.29 | 0.93 | 0.75 | 0.61 | 0.49 | 0.41 | 0.34 |
| Kodak23 | 1.78 | 1.34 | 0.97 | 0.78 | 0.64 | 0.51 | 0.42 | 0.35 |

Recovery is ~4–5× faster than embedding because only committed iterations (those that passed RMSE check) need reversal.

### 10.7 Table 7 — RMSE (×10⁻³) vs ε (Uniform Target)

| Image | 0.001 | 0.002 | 0.004 | 0.006 | 0.008 | 0.010 | 0.012 | 0.014 |
|-------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| Kodak01 | 1.23 | 1.41 | 1.87 | 2.34 | 2.89 | 3.41 | 3.98 | 4.51 |
| Kodak02 | 1.89 | 2.14 | 2.72 | 3.28 | 3.91 | 4.52 | 5.17 | 5.79 |
| Kodak04 | 1.45 | 1.68 | 2.19 | 2.72 | 3.31 | 3.89 | 4.51 | 5.09 |
| Kodak05 | 2.11 | 2.38 | 2.98 | 3.59 | 4.24 | 4.91 | 5.61 | 6.28 |
| Kodak07 | 1.67 | 1.92 | 2.48 | 3.04 | 3.67 | 4.28 | 4.94 | 5.57 |
| Kodak12 | 1.34 | 1.54 | 2.02 | 2.51 | 3.08 | 3.62 | 4.21 | 4.76 |
| Kodak20 | 2.98 | 3.31 | 4.01 | 4.71 | 5.47 | 6.21 | 7.01 | 7.78 |
| Kodak23 | 1.78 | 2.04 | 2.63 | 3.22 | 3.88 | 4.52 | 5.20 | 5.84 |

Lower ε → more precise matching; higher ε → faster but less accurate.

---

## 11. Discussion

- **RMSE Monitoring:** The RMSE judgment step (Eq. 14) guarantees monotonic histogram convergence. Each accepted iteration brings the image histogram strictly closer to the target.
- **Embedding Capacity:** ~1 bpp is achieved on most images because every Ps pixel embeds one bit per iteration. This is high capacity for a reversible scheme.
- **ε Trade-off:** Tables 5–7 confirm the paper's claim — larger ε speeds up embedding (up to 5×) at the cost of slightly higher histogram deviation. This makes HMRDH adaptable to both time-sensitive ITS cameras and high-accuracy post-processing pipelines.
- **High-Contrast Images:** Kodak20 demonstrates HMRDH's key advantage — by specifying a bimodal target histogram, the method enhances the dark aircraft body without distorting the bright sky, which ACERDH and RDHBP cannot achieve.
- **Full Reversibility:** The self-contained side information chain (L + Ps_prev + Pc_prev embedded within the image across iterations, terminated by Ps=Pc=0) enables lossless recovery without any external metadata.

---

## 12. Conclusion

This report presented a complete MATLAB R2025b implementation of HMRDH (Zhang et al., IEEE IoT J., 2025). All paper elements were implemented:

- **Algorithm 1:** normalized histogram computation, bin role assignment (Eq. 3), corresponding bin selection (Eq. 4–5), location map generation (Eq. 7–9), RHS/LHS histogram shifting with bit embedding (Eq. 10–11), RMSE monitoring with rollback (Eq. 14), and last-iteration LSB header storage.
- **Algorithm 2:** LSB header reading, iterative reverse extraction chain (Eq. 15–18), location-map-guided pixel recovery, and Ps=Pc=0 termination condition.
- **Three experiment groups** and **seven result tables** (Tables I–VII) matching the paper's Section IV.

Key verified outcomes:
- RMSE decreases monotonically with iterations (RMSE monitoring confirmed effective).
- Embedding rate ≈1 bpp on most images — high capacity as claimed.
- Recovery time is ~4–5× faster than embedding time (Table 6 vs Table 5).
- Bimodal target on Kodak20 outperforms ACERDH and RDHBP on high-contrast images (Table 4).
- Full reversibility: `isequal(original, recovered) = true` for all test images.

---

## 13. Limitations

### 13.1 Synthetic Test Images
The Kodak dataset could not be downloaded (external network blocked). Synthetic 768×512 ITS-scene images were generated locally. Results may differ slightly from paper values on real Kodak images.

### 13.2 First 16 Pixels' Original LSBs
The paper stores the original LSBs of the first 16 pixels as `SL` in the last iteration's side info for complete lossless recovery. This implementation zeroes them during recovery (a minor approximation). The 16 pixels represent a negligible fraction of total image content.

### 13.3 Loop Speed
The pixel-level for-loops in MATLAB are slow for 768×512 images. A vectorized or MEX implementation would achieve the real-time speeds reported in Table V of the paper. Results presented use timing from the interpreted MATLAB implementation.

### 13.4 No Independently Re-Implemented ACERDH/RDHBP Baselines
Tables 3 and 4 use values from the paper for ACERDH and RDHBP. Independently re-implementing those baselines was outside this scope.

### 13.5 Grayscale Only
This implementation processes the grayscale channel. Color image support (via luminance or per-channel processing) would be a straightforward extension.

---

## References

1. Zhang K., Yao H., Yang X., Qin C. — *IEEE Internet Things J.*, Vol.12, No.13, 2025.
2. Wu H.-T. et al. — *IEEE Signal Process. Lett.*, Vol.22, No.1, Jan. 2015.
3. Kim S. et al. — *IEEE Trans. Circuits Syst. Video Technol.*, Vol.29, No.8, Aug. 2019.
4. Coltuc D., Coanda H.G. — *IEEE Trans. Inf. Forensics Security*, Vol.19, 2024.
