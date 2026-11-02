"""
Exploration script: shows the real format of DefiLlama's free token-unlock (emissions) data.
Usage:  python probe_unlocks.py            (tries ONDO)
        python probe_unlocks.py arbitrum   (another slug)
The output contains no keys or secrets.
"""
import sys
import requests

slugs = sys.argv[1:] or ["ondo-finance", "ondo"]
urls = []
for sl in slugs:
    urls += [f"https://defillama-datasets.llama.fi/emissions/{sl}",
             f"https://api.llama.fi/emission/{sl}"]
urls.append("https://api.llama.fi/emissions")

for u in urls:
    print("=" * 72)
    try:
        r = requests.get(u, timeout=25)
        print(u, "->", r.status_code, r.headers.get("content-type"))
        print(r.text[:1200])
    except Exception as e:
        print(u, "-> ERROR:", e)
