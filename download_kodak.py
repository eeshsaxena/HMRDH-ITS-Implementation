"""
Download all 24 Kodak images for HMRDH experiments (tries multiple mirrors).
"""
import urllib.request, os, ssl

OUT_DIR = os.path.join(os.path.dirname(__file__), "data", "kodak")
os.makedirs(OUT_DIR, exist_ok=True)

# Multiple mirror sources for the Kodak dataset
MIRRORS = [
    "https://r0k.us/graphics/kodak/{name}",
    "http://www.cs.albany.edu/~xypan/research/snr/Kodak/{name}",
    "https://huggingface.co/datasets/gchhablani/kodak/resolve/main/{name}",
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download(n):
    name = f"kodim{n:02d}.png"
    dst  = os.path.join(OUT_DIR, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        print(f"  [exists] {name}")
        return True
    for mirror in MIRRORS:
        url = mirror.format(name=name)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as r, \
                 open(dst, "wb") as f:
                f.write(r.read())
            sz = os.path.getsize(dst)
            if sz > 10000:
                print(f"  [ok] {name} ({sz//1024} KB) from {url.split('/')[2]}")
                return True
            os.remove(dst)
        except Exception as e:
            pass
    print(f"  [FAILED] {name} - all mirrors failed")
    return False

if __name__ == "__main__":
    print(f"Saving to: {OUT_DIR}\n")
    ok = sum(download(i) for i in range(1, 25))
    print(f"\nTotal downloaded/available: {ok}/24")
