"""
Marmiton recipe scraper.

Extracts recipes from Marmiton.org with structured ingredient parsing.
"""

import csv
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


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


def get_marmiton_urls_from_page(url: str, max_results: int = 50) -> list[str]:
    """
    Récupère les URLs de recettes depuis une page Marmiton.
    
    Args:
        url: URL de la page à scraper
        max_results: Nombre maximum de résultats
        
    Returns:
        Liste d'URLs de recettes
    """
    urls = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            
            if '/recettes/recette' in href or (href.startswith('/recettes/') and '_' in href):
                if href.startswith('/'):
                    href = f"https://www.marmiton.org{href}"
                elif not href.startswith('http'):
                    continue
                
                if href not in urls and '/recettes/recette' in href:
                    urls.append(href)
                    
                if len(urls) >= max_results:
                    break
        
    except Exception as e:
        pass
    
    return urls


def search_marmiton_urls(query: str, max_results: int = 30) -> list[str]:
    """
    Cherche des URLs de recettes sur Marmiton.
    
    Args:
        query: Mot-clé de recherche
        max_results: Nombre maximum de résultats
        
    Returns:
        Liste d'URLs de recettes
    """
    search_url = f"https://www.marmiton.org/recettes/recherche.aspx?qs={quote(query)}"
    return get_marmiton_urls_from_page(search_url, max_results)


def extract_recipe_details(url: str) -> dict[str, Any] | None:
    """
    Extract all recipe details from HTML.
    
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
        
        # Title
        title = soup.find('h1', class_='main-title')
        if title:
            recipe['name'] = title.get_text(strip=True)
        
        # Rating
        rating_div = soup.find('div', class_='recipe-header__rating')
        if rating_div:
            rating_span = rating_div.find('span', class_='rating')
            if rating_span:
                rating_text = rating_span.get_text(strip=True)
                match = re.search(r'(\d+(?:[.,]\d+)?)', rating_text)
                if match:
                    recipe['rate'] = match.group(1).replace(',', '.')
        
        # Number of comments
        comments = soup.find('a', class_='recipe-header__comments')
        if comments:
            comments_text = comments.get_text(strip=True)
            match = re.search(r'(\d+)', comments_text)
            if match:
                recipe['nb_comments'] = match.group(1)
        
        # Metadata (difficulty, budget, times)
        recipe_infos = soup.find_all('div', class_='recipe-infos__item')
        for info in recipe_infos:
            label_elem = info.find('span', class_='recipe-infos__item-label')
            value_elem = info.find('span', class_='recipe-infos__item-value')
            
            if label_elem and value_elem:
                label = label_elem.get_text(strip=True).lower()
                value = value_elem.get_text(strip=True)
                
                if 'difficulté' in label or 'niveau' in label:
                    recipe['difficulty'] = value
                elif 'coût' in label or 'budget' in label or 'prix' in label:
                    recipe['budget'] = value
                elif 'préparation' in label or 'prep' in label:
                    recipe['prep_time'] = value
                elif 'cuisson' in label or 'cook' in label:
                    recipe['cook_time'] = value
                elif 'total' in label or 'temps total' in label:
                    recipe['total_time'] = value
        
        # Servings
        servings = soup.find('span', class_='recipe-infos__quantity')
        if servings:
            recipe['recipe_quantity'] = servings.get_text(strip=True)
        
        # Ingredients
        ingredients_raw = []
        ingredients_structured = []
        
        ingredients_section = soup.find('div', class_='recipe-ingredients')
        if ingredients_section:
            ingredient_items = ingredients_section.find_all('li', class_='recipe-ingredients__list-item')
            for item in ingredient_items:
                ingredient_text = item.get_text(' ', strip=True)
                ingredients_raw.append(ingredient_text)
                
                # Parse ingredient
                parsed = parse_ingredient(ingredient_text)
                ingredients_structured.append(parsed)
        
        if ingredients_raw:
            recipe['ingredients_raw'] = ' | '.join(ingredients_raw)
            recipe['ingredients_json'] = json.dumps(ingredients_structured, ensure_ascii=False)
        
        # Steps
        steps = []
        steps_section = soup.find('div', class_='recipe-steps')
        if steps_section:
            step_items = steps_section.find_all('li', class_='recipe-steps__list-item')
            for i, step in enumerate(step_items, 1):
                step_text = step.get_text(' ', strip=True)
                if step_text:
                    steps.append(f"{i}. {step_text}")
        
        if steps:
            recipe['steps'] = ' | '.join(steps)
        
        # Main image
        img = soup.find('img', class_='recipe-media__image')
        if img and img.get('src'):
            recipe['images'] = img['src']
        elif img and img.get('data-src'):
            recipe['images'] = img['data-src']
        
        # Tags/categories
        tags = []
        tags_section = soup.find('div', class_='recipe-tags')
        if tags_section:
            tag_links = tags_section.find_all('a')
            for tag in tag_links:
                tag_text = tag.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text)
        
        if tags:
            recipe['tags'] = ' | '.join(tags)
        
        # Verify we have minimum data
        if recipe['name'] and (recipe['ingredients_raw'] or recipe['steps']):
            return recipe
        else:
            return None
        
    except Exception as e:
        return None


def scrape_marmiton_to_csv(
    queries: list[str],
    output_file: str,
    max_results_per_query: int = 30,
    append: bool = False,
    delay: float = 0.8,
    max_workers: int = 5
) -> None:
    """
    Scrape Marmiton recipes and save to CSV.
    
    Args:
        queries: List of search keywords
        output_file: Output CSV file path
        max_results_per_query: Max recipes per search
        append: If True, append to existing file
        delay: Delay between requests in seconds
        max_workers: Number of parallel threads
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("Collecting recipe URLs")
    print("="*60)
    
    all_urls = []
    seen_urls = set()
    
    # Popular categories
    category_urls = [
        "https://www.marmiton.org/recettes/top-recettes.aspx",
        "https://www.marmiton.org/recettes/recettes-rapides.aspx",
        "https://www.marmiton.org/recettes/index/categorie/entree",
        "https://www.marmiton.org/recettes/index/categorie/plat-principal",
        "https://www.marmiton.org/recettes/index/categorie/dessert",
        "https://www.marmiton.org/recettes/index/categorie/accompagnement",
    ]
    
    print("Fetching from popular categories...")
    for cat_url in category_urls:
        urls = get_marmiton_urls_from_page(cat_url, 50)
        for url in urls:
            if url not in seen_urls:
                seen_urls.add(url)
                all_urls.append(url)
        time.sleep(delay)
    
    print(f"  {len(all_urls)} recipes from categories\n")
    
    # Print the URLs
    print("Popular recipe URLs:")
    for i, url in enumerate(all_urls[:20], 1):  # Show first 20
        print(f"  {i}. {url}")
    if len(all_urls) > 20:
        print(f"  ... and {len(all_urls) - 20} more")
    
    if not all_urls:
        print("\n❌ No URLs found!")
        return
    
    print(f"\n{'='*60}")
    print("Extracting details")
    print("="*60)
    
    fieldnames = [
        'name',
        'url',
        'rate',
        'nb_comments',
        'difficulty',
        'budget',
        'prep_time',
        'cook_time',
        'total_time',
        'recipe_quantity',
        'ingredients_raw',
        'ingredients_json',
        'steps',
        'images',
        'tags',
    ]
    
    mode = 'a' if append else 'w'
    file_exists = output_path.exists() and append
    
    recipes_written = 0
    
    with open(output_file, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        # Parallel extraction
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(extract_recipe_details, url): url for url in all_urls}
            
            with tqdm(total=len(all_urls), desc="Extracting", unit="recipe") as pbar:
                for future in as_completed(futures):
                    recipe = future.result()
                    if recipe:
                        writer.writerow(recipe)
                        csvfile.flush()  # Save progressively
                        recipes_written += 1
                    pbar.update(1)
                    time.sleep(delay / max_workers)
    
    action = "added" if append else "written"
    print(f"\n✓ {recipes_written}/{len(all_urls)} recipes {action} to {output_file}")
    
    failed = len(all_urls) - recipes_written
    if failed > 0:
        print(f"⚠️  {failed} recipes could not be extracted")


def main():
    """Main entry point."""
    output_file = "data/raw/marmiton_recipes.csv"
    
    print("="*60)
    print("Marmiton Scraper")
    print("="*60)
    print(f"Source: Popular categories only")
    print(f"Output: {output_file}")
    print("="*60)
    
    try:
        scrape_marmiton_to_csv(
            [],  # No keyword searches
            output_file,
            max_results_per_query=0,
            append=False,
            delay=0.5,
            max_workers=6
        )
        
        print(f"\n{'='*60}")
        print("✓ Extraction complete!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
