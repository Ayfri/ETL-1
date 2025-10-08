"""
Marmiton ingredients scraper.

Crawls through pages by letter (a..z) and paginated pages (/b/2, /b/3 ...)
and extracts elements containing the `card-needed` class.

Generates a CSV `data/raw/ingredients_raw.csv` with columns:
  - image_url
  - name
  - recipe_urls (pipe-separated list of recipe URLs)

Usage: python scripts/extract/scrape_marmiton_ingredients.py
"""

from __future__ import annotations

import csv
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.marmiton.org/recettes/index/ingredient"
OUTPUT_CSV = Path("data/raw/ingredients_raw.csv")


def fetch_page(url: str, timeout: float = 10.0, silent_404: bool = False) -> requests.Response | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.HTTPError as e:
        # Silently ignore 404 errors during pagination
        if e.response.status_code == 404 and silent_404:
            return None
        if e.response.status_code != 404:
            print(f"HTTP error for {url}: {e}")
        return None
    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {url}: {e}")
        return None


def parse_ingredients_from_soup(soup: BeautifulSoup) -> list[tuple[str, str, str]]:
    """
    Parse ingredients from ingredient listing page.
    
    Extracts ingredients from <a class="card-needed__link"> elements.
    
    Args:
        soup: BeautifulSoup object of the ingredient listing page
        
    Returns:
        List of tuples (image_url, name, ingredient_page_url)
    """
    results: list[tuple[str, str, str]] = []

    # Find all ingredient cards with class "card-needed__link"
    for a in soup.select("a.card-needed__link"):
        name_span = a.find(class_="card-needed__name")
        img = a.find("img", class_="card-needed__image")

        name = (name_span.get_text(strip=True) if name_span else "").strip()
        image_url = str(img.get("src", "")) if img else ""
        
        # Get the ingredient detail page URL (e.g., /recettes/index/ingredient/beurre)
        ingredient_page_url = str(a.get("href", ""))
        if ingredient_page_url and not ingredient_page_url.startswith("http"):
            ingredient_page_url = f"https://www.marmiton.org{ingredient_page_url}"

        if name and ingredient_page_url:
            results.append((image_url, name, ingredient_page_url))

    return results


def fetch_recipes_for_ingredient(ingredient_url: str, max_recipes: int = 100, delay: float = 0.3) -> list[str]:
    """
    Fetch recipe URLs from an ingredient detail page with pagination support.
    
    Args:
        ingredient_url: URL of the ingredient page
        max_recipes: Maximum number of recipes to fetch
        delay: Delay between page requests
        
    Returns:
        List of unique recipe URLs
    """
    recipe_urls: list[str] = []
    seen_urls: set[str] = set()
    page = 1
    
    while len(recipe_urls) < max_recipes:
        # Build paginated URL
        if page == 1:
            url = ingredient_url
        else:
            url = f"{ingredient_url}/{page}"
        
        # Silently ignore 404 errors for pagination (ingredient has fewer pages)
        resp = fetch_page(url, silent_404=(page > 1))
        if not resp:
            break
        
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Find recipe links on the page
        links = soup.find_all("a", href=True)
        
        found_on_page = 0
        for link in links:
            href = str(link.get("href", ""))
            
            # Check if it's a recipe URL (format: /recettes/recette_name_id.aspx)
            if "/recettes/recette_" in href and href.endswith(".aspx"):
                if href.startswith("/"):
                    href = f"https://www.marmiton.org{href}"
                elif not href.startswith("http"):
                    continue
                
                if href not in seen_urls:
                    seen_urls.add(href)
                    recipe_urls.append(href)
                    found_on_page += 1
                    
                if len(recipe_urls) >= max_recipes:
                    break
        
        # If no recipes found on this page, stop pagination
        if found_on_page == 0:
            break
        
        page += 1
        
        # Reduced delay between pages
        if page > 1:
            time.sleep(delay)
    
    return recipe_urls


def scrape_all_letters(delay: float = 0.4, max_recipes_per_ingredient: int = 100) -> list[tuple[str, str, list[str]]]:
    """
    Scrape all ingredient listing pages (by letter) and fetch recipe URLs for each ingredient.
    
    For each letter (a-z):
      1. Visit /recettes/index/ingredient/{letter} (and paginated pages)
      2. Extract ingredient cards with their detail page URLs
      3. For each ingredient, visit its detail page to get recipe URLs
    
    Args:
        delay: Delay between requests in seconds
        max_recipes_per_ingredient: Maximum recipes to fetch per ingredient
        
    Returns:
        List of tuples (image_url, name, recipe_urls_list)
    """
    all_items: list[tuple[str, str, list[str]]] = []
    seen_names: set[str] = set()

    letters = [chr(c) for c in range(ord("a"), ord("z") + 1)]

    for letter in letters:
        page = 1
        print(f"\nScraping letter: {letter.upper()}")
        
        while True:
            # Build URL for ingredient listing page
            url = f"{BASE_URL}/{letter}"
            if page > 1:
                url = f"{url}/{page}"

            print(f"  -> Listing page {page}: {url}")
            resp = fetch_page(url, silent_404=(page > 1))
            if not resp:
                if page == 1:
                    print(f"     ✗ Page {page} not available")
                break

            soup = BeautifulSoup(resp.content, "html.parser")
            ingredients_on_page = parse_ingredients_from_soup(soup)

            if not ingredients_on_page:
                break

            new_found = 0
            for image_url, name, ingredient_page_url in ingredients_on_page:
                key = name.lower()
                if key not in seen_names:
                    seen_names.add(key)
                    
                    # Fetch recipes from the ingredient's detail page
                    print(f"     → {name}", end="", flush=True)
                    recipe_urls = fetch_recipes_for_ingredient(
                        ingredient_page_url, 
                        max_recipes=max_recipes_per_ingredient, 
                        delay=0.3
                    )
                    print(f" → {len(recipe_urls)} recipes")
                    
                    all_items.append((image_url, name, recipe_urls))
                    new_found += 1
                    
                    # Save progress after each ingredient
                    save_to_csv(all_items, OUTPUT_CSV)
                    
                    time.sleep(delay)

            print(f"     + {new_found} new ingredients on page {page}")

            # If no new ingredients found, stop pagination for this letter
            if new_found == 0:
                break

            page += 1
            time.sleep(delay)

    return all_items


def save_to_csv(items: list[tuple[str, str, list[str]]], output: Path) -> None:
    """
    Save ingredients and their recipe URLs to CSV.
    
    Args:
        items: List of (image_url, name, recipe_urls_list) tuples
        output: Output CSV file path
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["image_url", "name", "recipe_urls"])
        for image_url, name, recipe_urls in items:
            # Join recipe URLs with pipe separator
            recipe_urls_str = "|".join(recipe_urls) if recipe_urls else ""
            writer.writerow([image_url or "", name, recipe_urls_str])


def main() -> None:
    """Main entry point."""
    print("Scraping Marmiton ingredients and their recipes...")
    items = scrape_all_letters()
    print(f"\n✓ Scraping complete! Found {len(items)} unique ingredients")
    print(f"✓ CSV saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()


