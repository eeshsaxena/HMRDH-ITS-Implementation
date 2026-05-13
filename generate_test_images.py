"""
Generate 8 synthetic grayscale test images (768x512) for HMRDH experiments.
These simulate the variety of ITS traffic scenes found in the Kodak dataset:
overexposed, shadowed, high-contrast, night, fog, normal, etc.
"""
import os
import math
import random

OUT_DIR = os.path.join(os.path.dirname(__file__), "data", "kodak")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 768, 512   # Kodak image dimensions

def clamp(v): return max(0, min(255, int(v)))

def make_png(pixels, path):
    """Write a grayscale PNG without external libraries (pure Python)."""
    import struct, zlib
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(c[4:]) & 0xFFFFFFFF)
    raw = b''.join(b'\x00' + bytes(row) for row in pixels)
    sig  = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 0, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(raw, 6))
    iend = chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(sig + ihdr + idat + iend)

def noise(rng, scale=8):
    return int(rng.gauss(0, scale))

def gen_image(name, style, seed=0):
    """Generate a single 768x512 grayscale synthetic image."""
    rng = random.Random(seed)
    pixels = []
    for y in range(H):
        row = []
        for x in range(W):
            fx, fy = x / W, y / H

            if style == 'normal':
                # Simulate a typical daylight traffic scene
                if fy < 0.35:           # sky
                    v = 190 + noise(rng, 12)
                elif fy < 0.42:         # treeline
                    v = 80 + int(20 * math.sin(x * 0.2)) + noise(rng, 10)
                elif fy < 0.65:         # road mid
                    v = 110 + noise(rng, 15)
                    if 0.35 < fx < 0.38 or 0.62 < fx < 0.65:  # lane markings
                        v = 230 + noise(rng, 5)
                else:                   # foreground road
                    v = 95 + int(20 * (fx - 0.5) ** 2 * 100) + noise(rng, 18)

            elif style == 'overexposed':
                # Bright, washed-out daytime scene
                base = 200 + int(30 * fy)
                v = base + noise(rng, 20)

            elif style == 'shadowed':
                # Dark, underexposed / shadowed scene
                v = 40 + int(60 * fx * fy) + noise(rng, 10)
                if fy > 0.7 and 0.3 < fx < 0.7:
                    v += 40   # brighter lane ahead

            elif style == 'high_contrast':
                # Strong sky vs dark road
                if fy < 0.4:
                    v = 240 + noise(rng, 8)   # bright sky
                else:
                    v = 30 + noise(rng, 12)   # dark asphalt

            elif style == 'night':
                # Nighttime: mostly dark with headlights
                v = 15 + noise(rng, 5)
                # Two headlight cones
                for cx, cy in [(0.3, 0.75), (0.7, 0.75)]:
                    dist = math.sqrt((fx - cx)**2 + (fy - cy)**2)
                    v = int(v + 200 * math.exp(-dist * dist / 0.005))

            elif style == 'foggy':
                # Low contrast, milky grey haze
                v = 150 + int(30 * math.sin(fx * 5)) + noise(rng, 8)

            elif style == 'rainy':
                # Wet road reflections + rain streaks
                v = 100 + noise(rng, 25)
                if (x + int(y * 0.3)) % 15 == 0:   # rain streak
                    v += 60

            elif style == 'mixed':
                # Mixed scene (vehicles, road, buildings)
                seg = int(fx * 4)
                bases = [70, 130, 190, 60]
                v = bases[seg % 4] + int(20 * math.sin(y * 0.08)) + noise(rng, 14)

            row.append(clamp(v))
        pixels.append(row)

    dst = os.path.join(OUT_DIR, name)
    make_png(pixels, dst)
    print(f"  Generated {name} ({style})")

IMAGES = [
    ("kodim01.png", "normal",        1),
    ("kodim02.png", "overexposed",   2),
    ("kodim04.png", "shadowed",      4),
    ("kodim05.png", "high_contrast", 5),
    ("kodim07.png", "night",         7),
    ("kodim12.png", "foggy",        12),
    ("kodim20.png", "mixed",        20),   # high-contrast test case in paper
    ("kodim23.png", "rainy",        23),
]

if __name__ == "__main__":
    print(f"Generating test images in: {OUT_DIR}\n")
    for name, style, seed in IMAGES:
        gen_image(name, style, seed)
    print(f"\nDone – {len(IMAGES)} images generated.")
