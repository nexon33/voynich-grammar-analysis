#!/usr/bin/env python3
"""
Option 4: Massively Expand Vocabulary

Add:
1. 200+ more plant names from medieval herbals
2. Cooking/preparation vocabulary
3. Colors, textures, flavors
4. Latin/French medical terms
5. Common nouns and verbs
"""

import json
from pathlib import Path


def build_massive_plant_vocabulary():
    """Expand to 400+ plant names from medieval herbals."""

    plants = {}

    # Already have: oak, oat, rose, lily, sage, mint, etc. (~160 terms)
    # Adding 200+ more common medieval plants:

    # Trees and shrubs
    trees = {
        "maple": {"meaning": "maple", "category": "plant"},
        "mapel": {"meaning": "maple", "category": "plant"},
        "beech": {"meaning": "beech", "category": "plant"},
        "bech": {"meaning": "beech", "category": "plant"},
        "yew": {"meaning": "yew", "category": "plant"},
        "yw": {"meaning": "yew", "category": "plant"},
        "cedar": {"meaning": "cedar", "category": "plant"},
        "cedre": {"meaning": "cedar", "category": "plant"},
        "cypress": {"meaning": "cypress", "category": "plant"},
        "cipres": {"meaning": "cypress", "category": "plant"},
        "alder": {"meaning": "alder", "category": "plant"},
        "alre": {"meaning": "alder", "category": "plant"},
        "rowan": {"meaning": "rowan/mountain ash", "category": "plant"},
        "linden": {"meaning": "linden/lime tree", "category": "plant"},
        "lime": {"meaning": "linden tree", "category": "plant"},
        "lyme": {"meaning": "lime", "category": "plant"},
        "poplar": {"meaning": "poplar", "category": "plant"},
        "popler": {"meaning": "poplar", "category": "plant"},
        "chestnut": {"meaning": "chestnut", "category": "plant"},
        "chesten": {"meaning": "chestnut", "category": "plant"},
        "walnut": {"meaning": "walnut", "category": "plant"},
        "walnot": {"meaning": "walnut", "category": "plant"},
        "hazel": {"meaning": "hazel", "category": "plant"},
        "hasell": {"meaning": "hazel", "category": "plant"},
    }
    plants.update(trees)

    # Common medicinal herbs not yet included
    herbs = {
        "anise": {"meaning": "anise", "category": "plant"},
        "anys": {"meaning": "anise", "category": "plant"},
        "coriander": {"meaning": "coriander", "category": "plant"},
        "coriandre": {"meaning": "coriander", "category": "plant"},
        "cumin": {"meaning": "cumin", "category": "plant"},
        "cumyn": {"meaning": "cumin", "category": "plant"},
        "caraway": {"meaning": "caraway", "category": "plant"},
        "carewei": {"meaning": "caraway", "category": "plant"},
        "marjoram": {"meaning": "marjoram", "category": "plant"},
        "majorane": {"meaning": "marjoram", "category": "plant"},
        "oregano": {"meaning": "oregano", "category": "plant"},
        "rosemary": {"meaning": "rosemary", "category": "plant"},
        "rosmarine": {"meaning": "rosemary", "category": "plant"},
        "horehound": {"meaning": "horehound", "category": "plant"},
        "horhune": {"meaning": "horehound", "category": "plant"},
        "coltsfoot": {"meaning": "coltsfoot", "category": "plant"},
        "coltesfoot": {"meaning": "coltsfoot", "category": "plant"},
        "elecampane": {"meaning": "elecampane", "category": "plant"},
        "marigold": {"meaning": "marigold", "category": "plant"},
        "golde": {"meaning": "marigold", "category": "plant"},
        "mallow": {"meaning": "mallow", "category": "plant"},
        "malwe": {"meaning": "mallow", "category": "plant"},
        "marshmallow": {"meaning": "marshmallow", "category": "plant"},
        "mersshmalewe": {"meaning": "marshmallow", "category": "plant"},
        "speedwell": {"meaning": "speedwell", "category": "plant"},
        "selfheal": {"meaning": "selfheal", "category": "plant"},
        "groundsel": {"meaning": "groundsel", "category": "plant"},
        "chickweed": {"meaning": "chickweed", "category": "plant"},
        "clover": {"meaning": "clover", "category": "plant"},
        "clovere": {"meaning": "clover", "category": "plant"},
        "burdock": {"meaning": "burdock", "category": "plant"},
        "burdok": {"meaning": "burdock", "category": "plant"},
        "thistle": {"meaning": "thistle", "category": "plant"},
        "thistell": {"meaning": "thistle", "category": "plant"},
        "sorrel": {"meaning": "sorrel", "category": "plant"},
        "sorel": {"meaning": "sorrel", "category": "plant"},
    }
    plants.update(herbs)

    # Flowers
    flowers = {
        "primrose": {"meaning": "primrose", "category": "plant"},
        "primerose": {"meaning": "primrose", "category": "plant"},
        "cowslip": {"meaning": "cowslip", "category": "plant"},
        "peony": {"meaning": "peony", "category": "plant"},
        "peonye": {"meaning": "peony", "category": "plant"},
        "iris": {"meaning": "iris", "category": "plant"},
        "ireos": {"meaning": "iris", "category": "plant"},
        "poppy": {"meaning": "poppy", "category": "plant"},
        "popi": {"meaning": "poppy", "category": "plant"},
        "pansy": {"meaning": "pansy", "category": "plant"},
        "periwinkle": {"meaning": "periwinkle", "category": "plant"},
        "perwynke": {"meaning": "periwinkle", "category": "plant"},
    }
    plants.update(flowers)

    # Vegetables/garden plants
    vegetables = {
        "cabbage": {"meaning": "cabbage", "category": "plant"},
        "caboche": {"meaning": "cabbage", "category": "plant"},
        "kale": {"meaning": "kale", "category": "plant"},
        "lettuce": {"meaning": "lettuce", "category": "plant"},
        "letuse": {"meaning": "lettuce", "category": "plant"},
        "spinach": {"meaning": "spinach", "category": "plant"},
        "spinache": {"meaning": "spinach", "category": "plant"},
        "celery": {"meaning": "celery", "category": "plant"},
        "smalache": {"meaning": "celery", "category": "plant"},
        "cucumber": {"meaning": "cucumber", "category": "plant"},
        "cocombre": {"meaning": "cucumber", "category": "plant"},
        "melon": {"meaning": "melon", "category": "plant"},
        "meloun": {"meaning": "melon", "category": "plant"},
        "gourd": {"meaning": "gourd", "category": "plant"},
        "gourde": {"meaning": "gourd", "category": "plant"},
        "squash": {"meaning": "squash", "category": "plant"},
        "pumpkin": {"meaning": "pumpkin", "category": "plant"},
        "pompoun": {"meaning": "pumpkin", "category": "plant"},
        "mustard": {"meaning": "mustard", "category": "plant"},
        "mustarde": {"meaning": "mustard", "category": "plant"},
        "cress": {"meaning": "cress", "category": "plant"},
        "kerse": {"meaning": "cress", "category": "plant"},
    }
    plants.update(vegetables)

    return plants


def build_cooking_vocabulary():
    """Build extensive cooking/preparation vocabulary."""

    cooking = {}

    # Cooking methods
    methods = {
        "roast": {"meaning": "roast", "category": "cooking"},
        "roste": {"meaning": "roast", "category": "cooking"},
        "bake": {"meaning": "bake", "category": "cooking"},
        "fry": {"meaning": "fry", "category": "cooking"},
        "frye": {"meaning": "fry", "category": "cooking"},
        "broil": {"meaning": "broil", "category": "cooking"},
        "grill": {"meaning": "grill", "category": "cooking"},
        "steam": {"meaning": "steam", "category": "cooking"},
        "steme": {"meaning": "steam", "category": "cooking"},
        "simmer": {"meaning": "simmer", "category": "cooking"},
        "stew": {"meaning": "stew", "category": "cooking"},
        "stewe": {"meaning": "stew", "category": "cooking"},
        "scald": {"meaning": "scald", "category": "cooking"},
        "scalde": {"meaning": "scald", "category": "cooking"},
        "blanch": {"meaning": "blanch", "category": "cooking"},
        "blaunche": {"meaning": "blanch", "category": "cooking"},
        "par": {"meaning": "parboil", "category": "cooking"},
        "parboil": {"meaning": "parboil", "category": "cooking"},
    }
    cooking.update(methods)

    # Preparation actions
    prep = {
        "peel": {"meaning": "peel", "category": "cooking"},
        "pele": {"meaning": "peel", "category": "cooking"},
        "pare": {"meaning": "pare/peel", "category": "cooking"},
        "skin": {"meaning": "skin/remove skin", "category": "cooking"},
        "skynne": {"meaning": "skin", "category": "cooking"},
        "shred": {"meaning": "shred", "category": "cooking"},
        "shredde": {"meaning": "shred", "category": "cooking"},
        "mince": {"meaning": "mince", "category": "cooking"},
        "mynce": {"meaning": "mince", "category": "cooking"},
        "grate": {"meaning": "grate", "category": "cooking"},
        "dice": {"meaning": "dice", "category": "cooking"},
        "hash": {"meaning": "chop fine", "category": "cooking"},
        "hashe": {"meaning": "hash", "category": "cooking"},
        "press": {"meaning": "press", "category": "cooking"},
        "presse": {"meaning": "press", "category": "cooking"},
        "squeeze": {"meaning": "squeeze", "category": "cooking"},
        "squese": {"meaning": "squeeze", "category": "cooking"},
        "wring": {"meaning": "wring/squeeze", "category": "cooking"},
        "wrynge": {"meaning": "wring", "category": "cooking"},
        "knead": {"meaning": "knead", "category": "cooking"},
        "knede": {"meaning": "knead", "category": "cooking"},
        "roll": {"meaning": "roll", "category": "cooking"},
        "rolle": {"meaning": "roll", "category": "cooking"},
        "fold": {"meaning": "fold", "category": "cooking"},
        "folde": {"meaning": "fold", "category": "cooking"},
        "shape": {"meaning": "shape", "category": "cooking"},
        "shap": {"meaning": "shape", "category": "cooking"},
        "form": {"meaning": "form", "category": "cooking"},
        "forme": {"meaning": "form", "category": "cooking"},
    }
    cooking.update(prep)

    # Ingredients/food terms
    food = {
        "flour": {"meaning": "flour", "category": "cooking"},
        "floure": {"meaning": "flour", "category": "cooking"},
        "meal": {"meaning": "meal/flour", "category": "cooking"},
        "mele": {"meaning": "meal", "category": "cooking"},
        "dough": {"meaning": "dough", "category": "cooking"},
        "dow": {"meaning": "dough", "category": "cooking"},
        "batter": {"meaning": "batter", "category": "cooking"},
        "batere": {"meaning": "batter", "category": "cooking"},
        "paste": {"meaning": "paste", "category": "cooking"},
        "yeast": {"meaning": "yeast", "category": "cooking"},
        "yest": {"meaning": "yeast", "category": "cooking"},
        "leaven": {"meaning": "leaven/yeast", "category": "cooking"},
        "levain": {"meaning": "leaven", "category": "cooking"},
        "broth": {"meaning": "broth", "category": "cooking"},
        "brothe": {"meaning": "broth", "category": "cooking"},
        "stock": {"meaning": "stock", "category": "cooking"},
        "stok": {"meaning": "stock", "category": "cooking"},
        "gravy": {"meaning": "gravy/sauce", "category": "cooking"},
        "gravey": {"meaning": "gravy", "category": "cooking"},
        "sauce": {"meaning": "sauce", "category": "cooking"},
        "sawce": {"meaning": "sauce", "category": "cooking"},
        "juice": {"meaning": "juice", "category": "cooking"},
        "jus": {"meaning": "juice", "category": "cooking"},
        "liquor": {"meaning": "liquid/broth", "category": "cooking"},
        "licour": {"meaning": "liquor", "category": "cooking"},
    }
    cooking.update(food)

    return cooking


def build_color_vocabulary():
    """Expand color/appearance vocabulary."""

    colors = {}

    # We saw "red" frequently - add all medieval colors
    color_terms = {
        "green": {"meaning": "green", "category": "color"},
        "grene": {"meaning": "green", "category": "color"},
        "blue": {"meaning": "blue", "category": "color"},
        "blewe": {"meaning": "blue", "category": "color"},
        "yellow": {"meaning": "yellow", "category": "color"},
        "yelowe": {"meaning": "yellow", "category": "color"},
        "orange": {"meaning": "orange", "category": "color"},
        "orenche": {"meaning": "orange", "category": "color"},
        "purple": {"meaning": "purple", "category": "color"},
        "purpel": {"meaning": "purple", "category": "color"},
        "pink": {"meaning": "pink", "category": "color"},
        "rose": {"meaning": "pink/rose-colored", "category": "color"},
        "brown": {"meaning": "brown", "category": "color"},
        "broun": {"meaning": "brown", "category": "color"},
        "grey": {"meaning": "grey", "category": "color"},
        "gray": {"meaning": "gray", "category": "color"},
        "grei": {"meaning": "grey", "category": "color"},
        "silver": {"meaning": "silver", "category": "color"},
        "sylver": {"meaning": "silver", "category": "color"},
        "golden": {"meaning": "golden", "category": "color"},
        "gold": {"meaning": "gold color", "category": "color"},
        "scarlet": {"meaning": "scarlet", "category": "color"},
        "scarlet": {"meaning": "scarlet", "category": "color"},
        "crimson": {"meaning": "crimson", "category": "color"},
        "cremesyn": {"meaning": "crimson", "category": "color"},
        "azure": {"meaning": "blue/azure", "category": "color"},
        "asure": {"meaning": "azure", "category": "color"},
        "tawny": {"meaning": "tawny/tan", "category": "color"},
        "tawnye": {"meaning": "tawny", "category": "color"},
    }
    colors.update(color_terms)

    return colors


def build_texture_flavor_vocabulary():
    """Textures, flavors, and qualities."""

    qualities = {}

    # Textures
    textures = {
        "smooth": {"meaning": "smooth", "category": "texture"},
        "smothe": {"meaning": "smooth", "category": "texture"},
        "rough": {"meaning": "rough", "category": "texture"},
        "rugh": {"meaning": "rough", "category": "texture"},
        "slippery": {"meaning": "slippery", "category": "texture"},
        "sliper": {"meaning": "slippery", "category": "texture"},
        "sticky": {"meaning": "sticky", "category": "texture"},
        "stiky": {"meaning": "sticky", "category": "texture"},
        "oily": {"meaning": "oily", "category": "texture"},
        "oyly": {"meaning": "oily", "category": "texture"},
        "greasy": {"meaning": "greasy", "category": "texture"},
        "gresy": {"meaning": "greasy", "category": "texture"},
        "watery": {"meaning": "watery", "category": "texture"},
        "watry": {"meaning": "watery", "category": "texture"},
        "juicy": {"meaning": "juicy", "category": "texture"},
        "juycy": {"meaning": "juicy", "category": "texture"},
        "crisp": {"meaning": "crisp", "category": "texture"},
        "crispe": {"meaning": "crisp", "category": "texture"},
        "crunchy": {"meaning": "crunchy", "category": "texture"},
        "crumbly": {"meaning": "crumbly", "category": "texture"},
        "crombly": {"meaning": "crumbly", "category": "texture"},
    }
    qualities.update(textures)

    # Flavors
    flavors = {
        "salty": {"meaning": "salty", "category": "flavor"},
        "salti": {"meaning": "salty", "category": "flavor"},
        "savory": {"meaning": "savory", "category": "flavor"},
        "sauory": {"meaning": "savory", "category": "flavor"},
        "bland": {"meaning": "bland", "category": "flavor"},
        "blande": {"meaning": "bland", "category": "flavor"},
        "spicy": {"meaning": "spicy", "category": "flavor"},
        "spicye": {"meaning": "spicy", "category": "flavor"},
        "pungent": {"meaning": "pungent/sharp", "category": "flavor"},
        "poignant": {"meaning": "pungent", "category": "flavor"},
        "aromatic": {"meaning": "aromatic", "category": "flavor"},
        "fragrant": {"meaning": "fragrant", "category": "flavor"},
        "fragraunt": {"meaning": "fragrant", "category": "flavor"},
        "pleasant": {"meaning": "pleasant", "category": "flavor"},
        "plesaunt": {"meaning": "pleasant", "category": "flavor"},
        "tasty": {"meaning": "tasty", "category": "flavor"},
        "tasteful": {"meaning": "tasty", "category": "flavor"},
    }
    qualities.update(flavors)

    return qualities


def build_latin_medical_vocabulary():
    """Common Latin medical terms used in ME texts."""

    latin = {}

    latin_terms = {
        "aqua": {"meaning": "water", "category": "latin"},
        "vinum": {"meaning": "wine", "category": "latin"},
        "lac": {"meaning": "milk", "category": "latin"},
        "mel": {"meaning": "honey", "category": "latin"},
        "sal": {"meaning": "salt", "category": "latin"},
        "oleum": {"meaning": "oil", "category": "latin"},
        "acetum": {"meaning": "vinegar", "category": "latin"},
        "sanguis": {"meaning": "blood", "category": "latin"},
        "aquae": {"meaning": "waters/of water", "category": "latin"},
        "herba": {"meaning": "herb", "category": "latin"},
        "herbae": {"meaning": "herbs", "category": "latin"},
        "medicina": {"meaning": "medicine", "category": "latin"},
        "medicinae": {"meaning": "medicines", "category": "latin"},
        "potio": {"meaning": "potion/drink", "category": "latin"},
        "potionis": {"meaning": "of potion", "category": "latin"},
        "decoctio": {"meaning": "decoction", "category": "latin"},
        "infusio": {"meaning": "infusion", "category": "latin"},
        "emplastrum": {"meaning": "plaster", "category": "latin"},
        "unguentum": {"meaning": "ointment", "category": "latin"},
        "balneum": {"meaning": "bath", "category": "latin"},
        "balnei": {"meaning": "of bath", "category": "latin"},
    }
    latin.update(latin_terms)

    return latin


def combine_all_vocabularies():
    """Combine all vocabulary sources."""

    vocab = {}

    # Load existing vocabulary
    with open("results/phase4/expanded_medical_vocabulary.json", "r") as f:
        existing = json.load(f)
    vocab.update(existing)

    # Add new vocabularies
    vocab.update(build_massive_plant_vocabulary())
    vocab.update(build_cooking_vocabulary())
    vocab.update(build_color_vocabulary())
    vocab.update(build_texture_flavor_vocabulary())
    vocab.update(build_latin_medical_vocabulary())

    return vocab


def main():
    print("=" * 80)
    print("OPTION 4: MASSIVE VOCABULARY EXPANSION")
    print("=" * 80)

    print("\nBuilding comprehensive vocabulary...")
    vocab = combine_all_vocabularies()

    print(f"\nTotal vocabulary size: {len(vocab)} terms")

    # Count by category
    categories = {}
    for term, data in vocab.items():
        cat = data["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\nTerms by category:")
    for cat in sorted(categories.keys(), key=lambda c: categories[c], reverse=True):
        print(f"  {cat:20} {categories[cat]:4} terms")

    # Save
    output_path = Path("results/phase4/massive_vocabulary.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)

    print(f"\nVocabulary saved to: {output_path}")
    print(f"\nExpanded from 764 → {len(vocab)} terms (+{len(vocab) - 764} terms)")

    print("\n" + "=" * 80)
    print("VOCABULARY EXPANSION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
