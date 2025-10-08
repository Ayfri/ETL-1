"""
Scraper des ingrédients Marmiton.

Parcourt les pages par lettre (a..z) et les pages paginées (/b/2, /b/3 ...)
et extrait les éléments contenant la classe `card-needed`.

Génère un CSV `data/raw/ingredients_raw.csv` avec les colonnes:
  - image_url
  - name

Usage: python scripts/extract/scrape_marmiton_ingredients.py
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


BASE_URL = "https://www.marmiton.org/recettes/index/ingredient"
OUTPUT_CSV = Path("data/raw/ingredients_raw.csv")


def fetch_page(url: str, timeout: float = 10.0) -> Optional[requests.Response]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.HTTPError as e:
        print(f"HTTP error for {url}: {e}")
        return None
    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {url}: {e}")
        return None


def parse_ingredients_from_soup(soup: BeautifulSoup) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []

    for card in soup.select(".card-needed"):
        a = card.find("a", class_="card-needed__link")
        if not a:
            continue

        name_span = a.find(class_="card-needed__name")
        img = a.find("img", class_="card-needed__image")

        name = (name_span.get_text(strip=True) if name_span else "").strip()
        image_url = img.get("src") if img and img.get("src") else ""

        if name:
            results.append((image_url, name))

    return results


def scrape_all_letters(delay: float = 0.6) -> list[tuple[str, str]]:
    all_items: list[tuple[str, str]] = []
    seen_names = set()

    letters = [chr(c) for c in range(ord("a"), ord("z") + 1)]

    for letter in letters:
        page = 1
        print(f"Scraping lettre: {letter}")
        while True:
            url = f"{BASE_URL}/{letter}"
            if page > 1:
                url = f"{url}/{page}"

            print(f"  -> page {page}: {url}")
            resp = fetch_page(url)
            if not resp:
                print(f"   x page {page} non disponible ou erreur")
                break

            soup = BeautifulSoup(resp.content, "html.parser")
            items = parse_ingredients_from_soup(soup)

            if not items:
                print(f"   - aucun ingrédient trouvé sur la page {page}")
                break

            new_found = 0
            for image_url, name in items:
                key = name.lower()
                if key not in seen_names:
                    seen_names.add(key)
                    all_items.append((image_url, name))
                    new_found += 1

            print(f"   + {new_found} nouveaux sur la page {page}")

            # Si aucun nouvel item trouvé, on sort de la pagination
            if new_found == 0:
                break

            page += 1
            time.sleep(delay)

    return all_items


def save_to_csv(items: list[tuple[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["image_url", "name"])
        for image_url, name in items:
            writer.writerow([image_url or "", name])


def main() -> None:
    print("Scraping ingrédients Marmiton...")
    items = scrape_all_letters()
    print(f"Trouvé {len(items)} ingrédients uniques")
    save_to_csv(items, OUTPUT_CSV)
    print(f"Sauvegardé dans {OUTPUT_CSV}")


if __name__ == "__main__":
    main()


