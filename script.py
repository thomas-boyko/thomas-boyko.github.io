import requests
from bs4 import BeautifulSoup
import os
import re
import time

# --- Config ---
OUTPUT_DIR = "albumart"
OUTPUT_HTML = "albums.html"

SPOTIFY_URLS = [
"https://open.spotify.com/album/3icT9XGrBfhlV8BKK4WEGX?si=c68d37efdb1b4c69",
"https://open.spotify.com/album/1ZfETfec0U02KrKNI8w3Gf?si=0a88a1b2f63e441b",
"https://open.spotify.com/album/0BE7TLLZoUhr9M8RlmFY3T?si=zP8NixU-SaubZecRbLD06g",
"https://open.spotify.com/album/2xkZV2Hl1Omi8rk2D7t5lN?si=ee16f930188c495d",
"https://open.spotify.com/album/5fZ7T0PCttjDWxJ0SMFtuF?si=_UF4U3bgQRGAZQ4vmmVjJw",
"https://open.spotify.com/album/2oJo7cB45gMVuRsaWNwDq2?si=H09q4AcoRUStb1lIcZ0hIg",
]

def get_album_link(spotify_url):
    r = requests.get(f"https://api.song.link/v1-alpha.1/links?url={spotify_url}&userCountry=US")
    return r.json().get("pageUrl", spotify_url)

def scrape_cover(album_link_url):
    r = requests.get(album_link_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    # album.link puts the cover in an og:image meta tag
    og_img = soup.find("meta", property="og:image")
    title = soup.find("meta", property="og:title")
    return og_img["content"] if og_img else None, title["content"] if title else "unknown"

def download_image(img_url, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    r = requests.get(img_url)
    with open(path, "wb") as f:
        f.write(r.content)
    return path

def slugify(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def main():
    html_lines = []

    for url in SPOTIFY_URLS:
        print(f"Processing {url}")
        album_link = get_album_link(url)
        img_url, title = scrape_cover(album_link)

        if not img_url:
            print(f"  Could not find image for {url}, skipping.")
            continue

        filename = f"{slugify(title)}.jpg"
        download_image(img_url, filename)

        html_lines.append(
            f'<a href="{album_link}"><img src="{OUTPUT_DIR}/{filename}" alt="{title}"></a>'
        )
        time.sleep(0.5)

    with open(OUTPUT_HTML, "w") as f:
        f.write("\n".join(html_lines))

    print(f"Done! Output written to {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
