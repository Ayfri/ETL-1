"""
Marmiton ingredients and recipes scraper.

Scrapes ingredients from listing pages, then extracts all recipes that use each ingredient.
Similar to scrape_marmiton.py but focused on ingredient-based recipe collection.
"""

from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path
from typing import Any, cast

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.marmiton.org/recettes/index/ingredient"
OUTPUT_CSV = Path("data/raw/marmiton_recipes_from_ingredients.csv")


def parse_ingredient(ingredient_text: str) -> dict[str, str]:
    """
    Parse an ingredient to extract quantity, unit and name.
    
    Args:
        ingredient_text: Raw ingredient text
        
    Returns:
        Dict with 'quantity', 'unit', 'name', 'raw'
    """
    result = {
        'quantity': '',
        'unit': '',
        'name': ingredient_text.strip(),
        'raw': ingredient_text.strip()
    }
    
    text = ingredient_text.strip()
    
    # Pattern 1: Quantity + metric unit + de/d' + name (350 g de thon)
    match = re.match(r'^(\d+(?:[.,]\d+)?)\s*([a-zA-Zéèàç]+)\s+(?:de|d\')\s+(.+)$', text, re.IGNORECASE)
    if match:
        result['quantity'] = match.group(1).replace(',', '.')
        result['unit'] = match.group(2).strip()
        result['name'] = match.group(3).strip()
        return result
    
    # Pattern 2: Quantity + cooking unit + de/d' + name (2 cuillères à soupe de sauce)
    match = re.match(
        r'^(\d+(?:[.,]\d+)?)\s+(cuillères?(?:\s+à\s+(?:soupe|café|thé))?|verres?|sachets?|boîtes?|bocaux?|tranches?|gousses?|branches?|feuilles?|pincées?|poignées?|cubes?|noix)\s+(?:de|d\')\s+(.+)$',
        text, re.IGNORECASE
    )
    if match:
        result['quantity'] = match.group(1).replace(',', '.')
        result['unit'] = match.group(2).strip()
        result['name'] = match.group(3).strip()
        return result
    
    # Pattern 3: Fraction + unit + de/d' + name (1/2 verre de lait)
    match = re.match(
        r'^(\d+/\d+)\s+(cuillères?(?:\s+à\s+(?:soupe|café|thé))?|verres?|sachets?|boîtes?|bocaux?|tranches?|gousses?|branches?|feuilles?|pincées?|poignées?|cubes?|noix)\s+(?:de|d\')\s+(.+)$',
        text, re.IGNORECASE
    )
    if match:
        result['quantity'] = match.group(1)
        result['unit'] = match.group(2).strip()
        result['name'] = match.group(3).strip()
        return result
    
    # Pattern 4: Quantity + metric unit without "de" (50 cl d'eau)
    match = re.match(r'^(\d+(?:[.,]\d+)?)\s*([a-zA-Zéèàç]+)\s+d\'(.+)$', text, re.IGNORECASE)
    if match:
        result['quantity'] = match.group(1).replace(',', '.')
        result['unit'] = match.group(2).strip()
        result['name'] = match.group(3).strip()
        return result
    
    # Pattern 5: Quantity + simple name (2 oeufs, 1 pâte brisée)
    match = re.match(r'^(\d+(?:[.,]\d+)?)\s+(.+)$', text)
    if match:
        result['quantity'] = match.group(1).replace(',', '.')
        result['name'] = match.group(2).strip()
        return result
    
    # Pattern 6: Fraction + name (1/2 chou-fleur)
    match = re.match(r'^(\d+/\d+)\s+(.+)$', text)
    if match:
        result['quantity'] = match.group(1)
        result['name'] = match.group(2).strip()
        return result
    
    return result


def extract_recipe_details(url: str) -> dict[str, Any] | None:
    """
    Extract all recipe details from HTML using JSON-LD structured data.
    
    Args:
        url: Recipe URL
        
    Returns:
        Dictionary with recipe details or None if extraction fails
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        recipe = {
            'url': url,
            'name': '',
            'rate': '',
            'nb_comments': '',
            'difficulty': '',
            'budget': '',
            'prep_time': '',
            'cook_time': '',
            'total_time': '',
            'recipe_quantity': '',
            'ingredients_raw': '',
            'ingredients_json': '',
            'steps': '',
            'images': '',
            'tags': '',
        }
        
        # Try to extract from JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        recipe_data: dict[str, Any] | None = None
        
        for script in json_ld_scripts:
            try:
                script_content = script.string
                if script_content:
                    data = json.loads(script_content)
                    if isinstance(data, dict) and data.get('@type') == 'Recipe':
                        recipe_data = data
                        break
            except:
                continue
        
        if recipe_data:
            # Extract from JSON-LD
            recipe['name'] = str(recipe_data.get('name', ''))
            
            # Rating
            if 'aggregateRating' in recipe_data:
                rating = recipe_data['aggregateRating']
                if isinstance(rating, dict):
                    recipe['rate'] = str(rating.get('ratingValue', ''))
                    recipe['nb_comments'] = str(rating.get('ratingCount', ''))
            
            # Times
            prep_time = str(recipe_data.get('prepTime', ''))
            if prep_time:
                # Convert ISO 8601 duration to readable format
                match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', prep_time)
                if match:
                    hours, mins = match.groups()
                    parts: list[str] = []
                    if hours:
                        parts.append(f"{hours}h")
                    if mins:
                        parts.append(f"{mins}min")
                    recipe['prep_time'] = ' '.join(parts) if parts else prep_time
            
            cook_time = str(recipe_data.get('cookTime', ''))
            if cook_time:
                match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', cook_time)
                if match:
                    hours, mins = match.groups()
                    parts: list[str] = []
                    if hours:
                        parts.append(f"{hours}h")
                    if mins:
                        parts.append(f"{mins}min")
                    recipe['cook_time'] = ' '.join(parts) if parts else cook_time
            
            total_time = str(recipe_data.get('totalTime', ''))
            if total_time:
                match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', total_time)
                if match:
                    hours, mins = match.groups()
                    parts: list[str] = []
                    if hours:
                        parts.append(f"{hours}h")
                    if mins:
                        parts.append(f"{mins}min")
                    recipe['total_time'] = ' '.join(parts) if parts else total_time
            
            # Servings
            recipe['recipe_quantity'] = str(recipe_data.get('recipeYield', ''))
            
            # Ingredients
            ingredients_raw = recipe_data.get('recipeIngredient', [])
            if isinstance(ingredients_raw, list):
                recipe['ingredients_raw'] = ' | '.join(str(ing) for ing in ingredients_raw)
                # Parse ingredients
                ingredients_structured = [parse_ingredient(str(ing)) for ing in ingredients_raw]
                recipe['ingredients_json'] = json.dumps(ingredients_structured, ensure_ascii=False)
            
            # Instructions
            instructions = recipe_data.get('recipeInstructions', [])
            steps: list[str] = []
            if isinstance(instructions, list):
                for i, step in enumerate(instructions, 1):
                    if isinstance(step, dict):
                        step_text = str(step.get('text', ''))
                    elif isinstance(step, str):
                        step_text = step
                    else:
                        continue
                        
                    if step_text:
                        steps.append(f"{i}. {step_text}")
            
            if steps:
                recipe['steps'] = ' | '.join(steps)
            
            # Image
            image = recipe_data.get('image')
            if isinstance(image, list) and image:
                recipe['images'] = str(image[0]) if isinstance(image[0], str) else str(image[0].get('url', '')) if isinstance(image[0], dict) else ''
            elif isinstance(image, str):
                recipe['images'] = image
            elif isinstance(image, dict):
                recipe['images'] = str(image.get('url', ''))
            
            # Categories/Keywords
            keywords = recipe_data.get('keywords', '')
            category = recipe_data.get('recipeCategory', '')
            tags: list[str] = []
            if keywords:
                tags.append(str(keywords))
            if category:
                tags.append(str(category))
            if tags:
                recipe['tags'] = ' | '.join(tags)
        
        # Fallback to HTML parsing if JSON-LD is incomplete
        if not recipe['name']:
            title = soup.find('h1')
            if title:
                recipe['name'] = title.get_text(strip=True)
        
        # Verify we have minimum data
        if recipe['name'] and (recipe['ingredients_raw'] or recipe['steps']):
            return recipe
        else:
            return None
        
    except Exception as e:
        return None


BASE_URL = "https://www.marmiton.org/recettes/index/ingredient"
OUTPUT_CSV = Path("data/raw/marmiton_recipes.csv")


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


def fetch_recipes_for_ingredient(ingredient_url: str, max_recipes: int = 100, delay: float = 0.3, seen_recipe_urls: set[str] | None = None) -> list[dict[str, Any]]:
    """
    Fetch full recipe details from an ingredient detail page with pagination support.
    
    Args:
        ingredient_url: URL of the ingredient page
        max_recipes: Maximum number of recipes to fetch
        delay: Delay between page requests
        seen_recipe_urls: Global set to track already seen recipe URLs
        
    Returns:
        List of recipe dictionaries with full details
    """
    if seen_recipe_urls is None:
        seen_recipe_urls = set()
        
    recipes: list[dict[str, Any]] = []
    page = 1
    
    while len(recipes) < max_recipes:
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
                
                # Skip if we've already seen this recipe URL
                if href in seen_recipe_urls:
                    continue
                    
                seen_recipe_urls.add(href)
                
                # Extract full recipe details instead of just URL
                print(f"      → Extracting recipe: {href}", end="", flush=True)
                recipe_details = extract_recipe_details(href)
                if recipe_details:
                    recipes.append(recipe_details)
                    found_on_page += 1
                    print(" ✓")
                else:
                    print(" ✗")
                    
                if len(recipes) >= max_recipes:
                    break
        
        # If no recipes found on this page, stop pagination
        if found_on_page == 0:
            break
        
        page += 1
        
        # Reduced delay between pages
        if page > 1:
            time.sleep(delay)
    
    return recipes


def scrape_all_letters(delay: float = 0.4, max_recipes_per_ingredient: int = 100) -> list[tuple[str, str, list[dict[str, Any]]]]:
    """
    Scrape all ingredient listing pages (by letter) and fetch full recipe details for each ingredient.
    
    For each letter (a-z):
      1. Visit /recettes/index/ingredient/{letter} (and paginated pages)
      2. Extract ingredient cards with their detail page URLs
      3. For each ingredient, visit its detail page to get full recipe details
    
    Args:
        delay: Delay between requests in seconds
        max_recipes_per_ingredient: Maximum recipes to fetch per ingredient
        
    Returns:
        List of tuples (image_url, name, recipes_list)
    """
    all_items: list[tuple[str, str, list[dict[str, Any]]]] = []
    seen_names: set[str] = set()
    seen_recipe_urls: set[str] = set()  # Global set to avoid duplicate recipes

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
                    
                    # Fetch full recipes from the ingredient's detail page
                    print(f"     → {name}")
                    recipes = fetch_recipes_for_ingredient(
                        ingredient_page_url, 
                        max_recipes=max_recipes_per_ingredient, 
                        delay=0.3,
                        seen_recipe_urls=seen_recipe_urls
                    )
                    print(f"       → {len(recipes)} recipes extracted")
                    
                    all_items.append((image_url, name, recipes))
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

    # Final save (in case there were no ingredients processed in the last batch)
    save_to_csv(all_items, OUTPUT_CSV)
    return all_items


def save_to_csv(items: list[tuple[str, str, list[dict[str, Any]]]], output: Path) -> None:
    """
    Save full recipe details to CSV.
    
    Args:
        items: List of (image_url, name, recipes_list) tuples
        output: Output CSV file path
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        # Write header row with all recipe fields
        writer.writerow([
            "url", "name", "rate", "nb_comments", "difficulty", "budget", 
            "prep_time", "cook_time", "total_time", "recipe_quantity", 
            "ingredients_raw", "ingredients_json", "steps", "images", "tags"
        ])
        
        for _, _, recipes in items:
            for recipe in recipes:
                writer.writerow([
                    recipe.get("url", ""),
                    recipe.get("name", ""),
                    recipe.get("rate", ""),
                    recipe.get("nb_comments", ""),
                    recipe.get("difficulty", ""),
                    recipe.get("budget", ""),
                    recipe.get("prep_time", ""),
                    recipe.get("cook_time", ""),
                    recipe.get("total_time", ""),
                    recipe.get("recipe_quantity", ""),
                    recipe.get("ingredients_raw", ""),
                    recipe.get("ingredients_json", ""),
                    recipe.get("steps", ""),
                    recipe.get("images", ""),
                    recipe.get("tags", "")
                ])


def main() -> None:
    """Main entry point."""
    print("Scraping Marmiton ingredients and extracting full recipe details...")
    items = scrape_all_letters()
    total_recipes = sum(len(recipes) for _, _, recipes in items)
    print(f"\n✓ Scraping complete! Processed {len(items)} ingredients")
    print(f"✓ Extracted {total_recipes} full recipes")
    print(f"✓ Recipes saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()


