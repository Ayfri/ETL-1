"""
Scraper de recettes Marmiton optimisé.

Utilise recipe-scrapers pour extraire les recettes de Marmiton.org.
"""

import csv
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me
from tqdm import tqdm


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


def extract_recipe_with_scrapers(url: str) -> dict[str, Any] | None:
    """
    Extrait les détails d'une recette avec recipe-scrapers.
    
    Args:
        url: URL de la recette
        
    Returns:
        Dictionnaire avec les détails ou None si échec
    """
    try:
        scraper = scrape_me(url)
        
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
            'ingredients': '',
            'steps': '',
            'images': '',
            'author_tip': '',
        }
        
        try:
            recipe['name'] = scraper.title() or ''
        except:
            pass
        
        try:
            recipe['total_time'] = str(scraper.total_time()) if scraper.total_time() else ''
        except:
            pass
        
        try:
            recipe['cook_time'] = str(scraper.cook_time()) if scraper.cook_time() else ''
        except:
            pass
        
        try:
            yields = scraper.yields()
            recipe['recipe_quantity'] = yields if yields else ''
        except:
            pass
        
        try:
            ingredients = scraper.ingredients()
            recipe['ingredients'] = ' | '.join(ingredients) if ingredients else ''
        except:
            pass
        
        try:
            instructions = scraper.instructions()
            if instructions:
                steps = [s.strip() for s in instructions.split('\n') if s.strip()]
                numbered_steps = [f"{i}. {step}" for i, step in enumerate(steps, 1)]
                recipe['steps'] = ' | '.join(numbered_steps)
        except:
            pass
        
        try:
            image = scraper.image()
            recipe['images'] = image if image else ''
        except:
            pass
        
        try:
            rating = scraper.ratings()
            recipe['rate'] = str(rating) if rating else ''
        except:
            pass
        
        try:
            author = scraper.author()
            if author:
                recipe['author_tip'] = author
        except:
            pass
        
        if recipe['name'] and (recipe['ingredients'] or recipe['steps']):
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
    Scrape des recettes Marmiton et sauvegarde en CSV.
    
    Args:
        queries: Liste de mots-clés de recherche
        output_file: Chemin du fichier CSV de sortie
        max_results_per_query: Nombre max de recettes par recherche
        append: Si True, ajoute au fichier existant
        delay: Délai entre les requêtes en secondes
        max_workers: Nombre de threads parallèles
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("Collecte des URLs de recettes")
    print("="*60)
    
    all_urls = []
    seen_urls = set()
    
    # Ajouter des pages de catégories populaires
    category_urls = [
        "https://www.marmiton.org/recettes/top-recettes.aspx",
        "https://www.marmiton.org/recettes/recettes-rapides.aspx",
        "https://www.marmiton.org/recettes/index/categorie/entree",
        "https://www.marmiton.org/recettes/index/categorie/plat-principal",
        "https://www.marmiton.org/recettes/index/categorie/dessert",
    ]
    
    print("Récupération depuis les catégories populaires...")
    for cat_url in category_urls:
        urls = get_marmiton_urls_from_page(cat_url, 50)
        for url in urls:
            if url not in seen_urls:
                seen_urls.add(url)
                all_urls.append(url)
        time.sleep(delay)
    
    print(f"  {len(all_urls)} recettes depuis les catégories")
    
    # Puis recherches par mots-clés
    for query in queries:
        print(f"Recherche: '{query}'...", end=' ')
        urls = search_marmiton_urls(query, max_results_per_query)
        
        new_urls = 0
        for url in urls:
            if url not in seen_urls:
                seen_urls.add(url)
                all_urls.append(url)
                new_urls += 1
        
        if new_urls > 0:
            print(f"{new_urls} nouvelles")
        else:
            print("0 nouvelles")
        time.sleep(delay)
    
    if not all_urls:
        print("\n❌ Aucune URL trouvée!")
        return
    
    print(f"\n✓ Total: {len(all_urls)} recettes uniques")
    
    print(f"\n{'='*60}")
    print("Extraction des détails")
    print("="*60)
    
    fieldnames = [
        'author_tip',
        'budget',
        'cook_time',
        'difficulty',
        'images',
        'ingredients',
        'name',
        'nb_comments',
        'prep_time',
        'rate',
        'recipe_quantity',
        'steps',
        'total_time',
        'url',
    ]
    
    mode = 'a' if append else 'w'
    file_exists = output_path.exists() and append
    
    recipes_written = 0
    
    with open(output_file, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        # Extraction parallèle pour accélérer
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(extract_recipe_with_scrapers, url): url for url in all_urls}
            
            with tqdm(total=len(all_urls), desc="Extraction") as pbar:
                for future in as_completed(futures):
                    recipe = future.result()
                    if recipe:
                        writer.writerow(recipe)
                        recipes_written += 1
                    pbar.update(1)
                    time.sleep(delay / max_workers)  # Délai réduit car parallèle
    
    action = "ajoutées" if append else "écrites"
    print(f"\n✓ {recipes_written} recettes {action} dans {output_file}")


def main():
    """Point d'entrée principal."""
    queries = [
        # Sélection réduite mais variée
        "poulet roti", "boeuf bourguignon", "blanquette de veau",
        "saumon grillé", "moules marinières", "sole meunière",
    ]
    
    output_file = "data/raw/marmiton_recipes.csv"
    max_results_per_query = 20
    
    print("="*60)
    print("Scraper Marmiton - Version Optimisée")
    print("="*60)
    print(f"Recherches: {len(queries)} mots-clés")
    print(f"Max par recherche: {max_results_per_query}")
    print(f"Fichier: {output_file}")
    print("="*60)
    
    try:
        scrape_marmiton_to_csv(
            queries,
            output_file,
            max_results_per_query=max_results_per_query,
            append=False,
            delay=0.6,
            max_workers=8
        )
        
        print(f"\n{'='*60}")
        print("✓ Extraction terminée!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompu par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
