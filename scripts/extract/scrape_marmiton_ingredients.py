"""
Marmiton ingredients and recipes scraper.

Scrapes ingredients from listing pages, then extracts all recipes that use each ingredient.
Optimized version with asyncio and multiprocessing for maximum speed.
"""

from __future__ import annotations

import asyncio
import csv
import json
import multiprocessing as mp
import re
import time
from pathlib import Path
from typing import Any
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup


BASE_URL = "https://www.marmiton.org/recettes/index/ingredient"
OUTPUT_CSV = Path("data/raw/marmiton_recipes.csv")

# Performance settings
MAX_CONCURRENT_REQUESTS = 40  # Limit concurrent HTTP requests
REQUEST_TIMEOUT = 6.0
RATE_LIMIT_DELAY = 0.05  # Minimum delay between requests
MAX_WORKERS = min(mp.cpu_count() * 2, 8)  # Number of worker processes


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


@dataclass
class RateLimiter:
    """Simple rate limiter for HTTP requests."""
    delay: float
    last_request: float = 0.0

    async def wait(self):
        """Wait for rate limit."""
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)
        self.last_request = time.time()


async def fetch_page_async(session: aiohttp.ClientSession, url: str, rate_limiter: RateLimiter, silent_404: bool = False) -> str | None:
    """
    Fetch a page asynchronously with rate limiting.

    Args:
        session: aiohttp session
        url: URL to fetch
        rate_limiter: Rate limiter instance
        silent_404: Whether to silently ignore 404 errors

    Returns:
        Page content as string or None if failed
    """
    await rate_limiter.wait()

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
            if response.status == 404 and silent_404:
                return None
            response.raise_for_status()
            # Read raw bytes and handle encoding properly
            content = await response.read()
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to latin-1 which can decode any byte sequence
                return content.decode('latin-1')
    except aiohttp.ClientError as e:
        if not (silent_404 and "404" in str(e)):
            print(f"Request error for {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {url}: {e}")
        return None


async def extract_recipe_details_async(session: aiohttp.ClientSession, url: str, rate_limiter: RateLimiter) -> dict[str, Any] | None:
    """
    Extract all recipe details from HTML using JSON-LD structured data asynchronously.

    Args:
        session: aiohttp session
        url: Recipe URL
        rate_limiter: Rate limiter instance

    Returns:
        Dictionary with recipe details or None if extraction fails
    """
    html = await fetch_page_async(session, url, rate_limiter)
    if not html:
        return None

    try:
        soup = BeautifulSoup(html, 'html.parser')

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


async def parse_ingredients_from_soup_async(html: str) -> list[tuple[str, str, str]]:
    """
    Parse ingredients from ingredient listing page HTML.

    Extracts ingredients from <a class="card-needed__link"> elements.

    Args:
        html: HTML content of the ingredient listing page

    Returns:
        List of tuples (image_url, name, ingredient_page_url)
    """
    results: list[tuple[str, str, str]] = []

    soup = BeautifulSoup(html, "html.parser")

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


async def fetch_recipes_for_ingredient_async(
    session: aiohttp.ClientSession,
    ingredient_url: str,
    rate_limiter: RateLimiter,
    max_recipes: int = 100,
    seen_recipe_urls: set[str] | None = None
) -> list[dict[str, Any]]:
    """
    Fetch full recipe details from an ingredient detail page with pagination support asynchronously.

    Args:
        session: aiohttp session
        ingredient_url: URL of the ingredient page
        rate_limiter: Rate limiter instance
        max_recipes: Maximum number of recipes to fetch
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
        html = await fetch_page_async(session, url, rate_limiter, silent_404=(page > 1))
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")

        # Find recipe links on the page
        recipe_urls: list[str] = []
        links = soup.find_all("a", href=True)

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
                recipe_urls.append(href)

        # Extract recipe details in parallel with semaphore to limit concurrency
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def extract_with_semaphore(url: str) -> dict[str, Any] | None:
            async with semaphore:
                return await extract_recipe_details_async(session, url, rate_limiter)

        # Process recipes in batches to avoid overwhelming the server
        batch_size = 10
        for i in range(0, len(recipe_urls), batch_size):
            batch_urls = recipe_urls[i:i + batch_size]
            batch_tasks = [extract_with_semaphore(url) for url in batch_urls]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    continue  # Skip failed extractions
                if result:
                    recipes.append(result)
                    if len(recipes) >= max_recipes:
                        break

            if len(recipes) >= max_recipes:
                break

        # If no recipes found on this page, stop pagination
        if not recipe_urls:
            break

        page += 1

    return recipes


async def scrape_ingredient_pages_async(session: aiohttp.ClientSession, rate_limiter: RateLimiter, letter: str, seen_names: set[str]) -> list[tuple[str, str, str]]:
    """
    Scrape all ingredient listing pages for a given letter asynchronously.

    Args:
        session: aiohttp session
        rate_limiter: Rate limiter instance
        letter: Letter to scrape (a-z)
        seen_names: Set of already seen ingredient names

    Returns:
        List of (image_url, name, ingredient_page_url) tuples
    """
    ingredients: list[tuple[str, str, str]] = []
    page = 1

    while True:
        # Build URL for ingredient listing page
        url = f"{BASE_URL}/{letter}"
        if page > 1:
            url = f"{url}/{page}"

        print(f"  -> Listing page {page}: {url}")
        html = await fetch_page_async(session, url, rate_limiter, silent_404=(page > 1))
        if not html:
            if page == 1:
                print(f"     ✗ Page {page} not available")
            break

        ingredients_on_page = await parse_ingredients_from_soup_async(html)

        if not ingredients_on_page:
            break

        new_found = 0
        for image_url, name, ingredient_page_url in ingredients_on_page:
            key = name.lower()
            if key not in seen_names:
                seen_names.add(key)
                ingredients.append((image_url, name, ingredient_page_url))
                new_found += 1

        print(f"     + {new_found} new ingredients on page {page}")

        # If no new ingredients found, stop pagination for this letter
        if new_found == 0:
            break

        page += 1

    return ingredients


def process_ingredient_worker(ingredient_data: tuple[str, str, str], max_recipes: int) -> tuple[str, str, list[dict[str, Any]]]:
    """
    Worker function to process a single ingredient (runs in separate process).

    Args:
        ingredient_data: (image_url, name, ingredient_page_url)
        max_recipes: Maximum recipes per ingredient

    Returns:
        (image_url, name, recipes_list)
    """
    image_url, name, ingredient_page_url = ingredient_data

    # Create new event loop for this process
    asyncio.set_event_loop(asyncio.new_event_loop())

    async def process_async():
        # Shared seen URLs across all ingredients (but not across processes)
        seen_recipe_urls = set()

        # Create session and rate limiter for this process
        rate_limiter = RateLimiter(RATE_LIMIT_DELAY)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)

        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        ) as session:
            recipes = await fetch_recipes_for_ingredient_async(
                session, ingredient_page_url, rate_limiter, max_recipes, seen_recipe_urls
            )
            return image_url, name, recipes

    return asyncio.run(process_async())


async def scrape_all_letters_async(max_recipes_per_ingredient: int = 100) -> list[tuple[str, str, list[dict[str, Any]]]]:
    """
    Scrape all ingredient listing pages (by letter) and fetch full recipe details for each ingredient using multiprocessing.

    For each letter (a-z):
      1. Visit /recettes/index/ingredient/{letter} (and paginated pages)
      2. Extract ingredient cards with their detail page URLs
      3. For each ingredient, fetch full recipe details using multiprocessing

    Args:
        max_recipes_per_ingredient: Maximum recipes to fetch per ingredient

    Returns:
        List of tuples (image_url, name, recipes_list)
    """
    all_items: list[tuple[str, str, list[dict[str, Any]]]] = []
    seen_names: set[str] = set()

    # Initialize CSV file with headers
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT_CSV.exists():
        OUTPUT_CSV.unlink()  # Remove existing file to start fresh
    
    # Create file with header
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "url", "name", "rate", "nb_comments", "difficulty", "budget",
            "prep_time", "cook_time", "total_time", "recipe_quantity",
            "ingredients_raw", "ingredients_json", "steps", "images", "tags"
        ])

    # Create shared rate limiter for ingredient listing
    rate_limiter = RateLimiter(RATE_LIMIT_DELAY)
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    ) as session:

        letters = [chr(c) for c in range(ord("a"), ord("z") + 1)]

        for letter in letters:
            print(f"\nScraping letter: {letter.upper()}")

            # Scrape ingredient listing pages for this letter
            ingredients = await scrape_ingredient_pages_async(session, rate_limiter, letter, seen_names)

            if not ingredients:
                continue

            print(f"  Found {len(ingredients)} ingredients for letter {letter}")

            # Process ingredients in parallel using multiprocessing
            # Use ProcessPoolExecutor for CPU-bound recipe processing
            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Submit all ingredient processing tasks
                future_to_ingredient = {
                    executor.submit(process_ingredient_worker, ingredient, max_recipes_per_ingredient): ingredient
                    for ingredient in ingredients
                }

                # Collect results as they complete
                for future in future_to_ingredient:
                    try:
                        image_url, name, recipes = future.result()
                        print(f"     ✓ {name}: {len(recipes)} recipes")
                        all_items.append((image_url, name, recipes))

                        # Save only this ingredient's recipes incrementally
                        save_to_csv([(image_url, name, recipes)], OUTPUT_CSV, append=True)

                    except Exception as e:
                        ingredient = future_to_ingredient[future]
                        print(f"     ✗ Error processing {ingredient[1]}: {e}")

    return all_items


def save_to_csv(items: list[tuple[str, str, list[dict[str, Any]]]], output: Path, append: bool = False) -> None:
    """
    Save full recipe details to CSV.

    Args:
        items: List of (image_url, name, recipes_list) tuples
        output: Output CSV file path
        append: If True, append to existing file. If False, overwrite.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine if we need to write header (new file or overwrite mode)
    write_header = not append or not output.exists()
    mode = "a" if append else "w"
    
    with output.open(mode, encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        
        # Write header row only if needed
        if write_header:
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
    print("🚀 Starting optimized Marmiton scraper with asyncio + multiprocessing...")
    print(f"⚙️  Settings: {MAX_CONCURRENT_REQUESTS} concurrent requests, {MAX_WORKERS} workers, {RATE_LIMIT_DELAY}s delay")

    start_time = time.time()

    # Run the async scraper
    items = asyncio.run(scrape_all_letters_async())

    total_recipes = sum(len(recipes) for _, _, recipes in items)
    elapsed_time = time.time() - start_time

    print("\n✅ Scraping complete!")
    print(f"📊 Processed {len(items)} ingredients")
    print(f"🍳 Extracted {total_recipes} full recipes")
    print(f"⏱️  Time elapsed: {elapsed_time:.2f}s")
    print(f"💾 Recipes saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
