#!/usr/bin/env python3
"""
Build specialized Middle English vocabulary for medical/herbal recipes.
Focus on women's health, gynecology, and herbal terminology.
"""

import json
from pathlib import Path


def build_recipe_instructions():
    """Common Middle English recipe instruction words."""
    return {
        # Taking/obtaining
        "take": {"meaning": "take", "category": "instruction"},
        "tak": {"meaning": "take", "category": "instruction"},
        "takun": {"meaning": "taken", "category": "instruction"},
        "takyn": {"meaning": "taken", "category": "instruction"},
        "taak": {"meaning": "take", "category": "instruction"},
        # Preparation
        "boil": {"meaning": "boil", "category": "instruction"},
        "boyle": {"meaning": "boil", "category": "instruction"},
        "boylyn": {"meaning": "boiling", "category": "instruction"},
        "sethe": {"meaning": "boil/seethe", "category": "instruction"},
        "seeþ": {"meaning": "boil", "category": "instruction"},
        "grind": {"meaning": "grind", "category": "instruction"},
        "grynde": {"meaning": "grind", "category": "instruction"},
        "grynd": {"meaning": "grind", "category": "instruction"},
        "pound": {"meaning": "pound", "category": "instruction"},
        "pounde": {"meaning": "pound", "category": "instruction"},
        "pownde": {"meaning": "pound", "category": "instruction"},
        "stamp": {"meaning": "crush/stamp", "category": "instruction"},
        "stampe": {"meaning": "crush", "category": "instruction"},
        "mix": {"meaning": "mix", "category": "instruction"},
        "myx": {"meaning": "mix", "category": "instruction"},
        "mixyn": {"meaning": "mixing", "category": "instruction"},
        "menge": {"meaning": "mix", "category": "instruction"},
        "temper": {"meaning": "temper/mix", "category": "instruction"},
        "tempere": {"meaning": "mix properly", "category": "instruction"},
        "steep": {"meaning": "steep/soak", "category": "instruction"},
        "stepe": {"meaning": "steep", "category": "instruction"},
        # Application
        "drink": {"meaning": "drink", "category": "instruction"},
        "drynke": {"meaning": "drink", "category": "instruction"},
        "drynk": {"meaning": "drink", "category": "instruction"},
        "drinken": {"meaning": "drink", "category": "instruction"},
        "apply": {"meaning": "apply", "category": "instruction"},
        "applye": {"meaning": "apply", "category": "instruction"},
        "use": {"meaning": "use", "category": "instruction"},
        "usen": {"meaning": "use", "category": "instruction"},
        "usyn": {"meaning": "using", "category": "instruction"},
        "lay": {"meaning": "lay/apply", "category": "instruction"},
        "leye": {"meaning": "lay", "category": "instruction"},
        "leggen": {"meaning": "lay", "category": "instruction"},
        "make": {"meaning": "make", "category": "instruction"},
        "maken": {"meaning": "make", "category": "instruction"},
        "mak": {"meaning": "make", "category": "instruction"},
    }


def build_womens_health_terms():
    """Women's health and gynecological terms."""
    return {
        # Reproductive anatomy
        "womb": {"meaning": "womb/uterus", "category": "womens_health"},
        "wombbe": {"meaning": "womb", "category": "womens_health"},
        "matrice": {"meaning": "womb/uterus", "category": "womens_health"},
        "matrix": {"meaning": "womb", "category": "womens_health"},
        # Menstruation
        "menstrue": {"meaning": "menstruation", "category": "womens_health"},
        "menisoun": {
            "meaning": "menstruation/period pain",
            "category": "womens_health",
        },
        "floures": {"meaning": "menstrual flow", "category": "womens_health"},
        "monethes": {"meaning": "monthly period", "category": "womens_health"},
        "cours": {"meaning": "menstrual course", "category": "womens_health"},
        # Childbirth
        "child": {"meaning": "child", "category": "womens_health"},
        "childe": {"meaning": "child", "category": "womens_health"},
        "childyng": {"meaning": "childbirth", "category": "womens_health"},
        "birthe": {"meaning": "birth", "category": "womens_health"},
        "travaile": {"meaning": "labor pains", "category": "womens_health"},
        # Female person
        "womman": {"meaning": "woman", "category": "womens_health"},
        "woman": {"meaning": "woman", "category": "womens_health"},
        "women": {"meaning": "women", "category": "womens_health"},
        "wymmen": {"meaning": "women", "category": "womens_health"},
        "wife": {"meaning": "woman/wife", "category": "womens_health"},
        "wyf": {"meaning": "woman", "category": "womens_health"},
        # Breast
        "breast": {"meaning": "breast", "category": "womens_health"},
        "brest": {"meaning": "breast", "category": "womens_health"},
        "breste": {"meaning": "breast", "category": "womens_health"},
        "pappes": {"meaning": "breasts/nipples", "category": "womens_health"},
        "tetys": {"meaning": "breasts", "category": "womens_health"},
    }


def build_pain_terms():
    """Pain and medical condition terms."""
    return {
        # Pain
        "sor": {"meaning": "sore/pain", "category": "conditions"},
        "sore": {"meaning": "painful/wound", "category": "conditions"},
        "sory": {"meaning": "painful/sore", "category": "conditions"},
        "soar": {"meaning": "sore", "category": "conditions"},
        "ache": {"meaning": "ache/pain", "category": "conditions"},
        "aken": {"meaning": "aching", "category": "conditions"},
        "peyn": {"meaning": "pain", "category": "conditions"},
        "peyne": {"meaning": "pain", "category": "conditions"},
        "pein": {"meaning": "pain", "category": "conditions"},
        # Inflammation
        "swellyng": {"meaning": "swelling", "category": "conditions"},
        "swellyn": {"meaning": "swollen", "category": "conditions"},
        "bolne": {"meaning": "swollen", "category": "conditions"},
        # Healing
        "hele": {"meaning": "heal", "category": "treatments"},
        "heele": {"meaning": "heal", "category": "treatments"},
        "helyn": {"meaning": "healing", "category": "treatments"},
        "helen": {"meaning": "heal", "category": "treatments"},
        "healen": {"meaning": "heal", "category": "treatments"},
        # Cure/remedy
        "cure": {"meaning": "cure", "category": "treatments"},
        "curen": {"meaning": "cure", "category": "treatments"},
        "remedie": {"meaning": "remedy", "category": "treatments"},
        "remedye": {"meaning": "remedy", "category": "treatments"},
        "leche": {"meaning": "medicine/physician", "category": "treatments"},
        "leechecraft": {"meaning": "medicine/healing", "category": "treatments"},
    }


def build_body_parts():
    """Body part terminology."""
    return {
        # Head
        "hed": {"meaning": "head", "category": "body_parts"},
        "head": {"meaning": "head", "category": "body_parts"},
        "heued": {"meaning": "head", "category": "body_parts"},
        "heved": {"meaning": "head", "category": "body_parts"},
        # Eyes/ears
        "eye": {"meaning": "eye", "category": "body_parts"},
        "eyen": {"meaning": "eyes", "category": "body_parts"},
        "ye": {"meaning": "eye", "category": "body_parts"},
        "yhe": {"meaning": "eye", "category": "body_parts"},
        "ear": {"meaning": "ear", "category": "body_parts"},
        "ere": {"meaning": "ear", "category": "body_parts"},
        "earen": {"meaning": "ears", "category": "body_parts"},
        # Internal organs
        "herte": {"meaning": "heart", "category": "body_parts"},
        "heart": {"meaning": "heart", "category": "body_parts"},
        "stomak": {"meaning": "stomach", "category": "body_parts"},
        "stomac": {"meaning": "stomach", "category": "body_parts"},
        "belly": {"meaning": "belly", "category": "body_parts"},
        "belye": {"meaning": "belly", "category": "body_parts"},
        "wombe": {"meaning": "belly/womb", "category": "body_parts"},
        # Blood/bones
        "blod": {"meaning": "blood", "category": "body_parts"},
        "blood": {"meaning": "blood", "category": "body_parts"},
        "bon": {"meaning": "bone", "category": "body_parts"},
        "bones": {"meaning": "bones", "category": "body_parts"},
        "boon": {"meaning": "bone", "category": "body_parts"},
    }


def build_herb_names():
    """Common medicinal herb names in Middle English."""
    return {
        # Common herbs
        "betony": {"meaning": "betony plant", "category": "herbs"},
        "betonye": {"meaning": "betony", "category": "herbs"},
        "rue": {"meaning": "rue", "category": "herbs"},
        "ruta": {"meaning": "rue (Latin)", "category": "herbs"},
        "fennel": {"meaning": "fennel", "category": "herbs"},
        "fenel": {"meaning": "fennel", "category": "herbs"},
        "sage": {"meaning": "sage", "category": "herbs"},
        "sawge": {"meaning": "sage", "category": "herbs"},
        # Women's health herbs
        "tansy": {"meaning": "tansy", "category": "herbs"},
        "tansye": {"meaning": "tansy", "category": "herbs"},
        "mugwort": {"meaning": "mugwort", "category": "herbs"},
        "moderwort": {"meaning": "motherwort", "category": "herbs"},
        "modirwort": {"meaning": "motherwort", "category": "herbs"},
        # Plant parts
        "rote": {"meaning": "root", "category": "herbs"},
        "root": {"meaning": "root", "category": "herbs"},
        "roote": {"meaning": "root", "category": "herbs"},
        "lef": {"meaning": "leaf", "category": "herbs"},
        "leaf": {"meaning": "leaf", "category": "herbs"},
        "leef": {"meaning": "leaf", "category": "herbs"},
        "leves": {"meaning": "leaves", "category": "herbs"},
        "seed": {"meaning": "seed", "category": "herbs"},
        "sede": {"meaning": "seed", "category": "herbs"},
        "flour": {"meaning": "flower", "category": "herbs"},
        "floure": {"meaning": "flower", "category": "herbs"},
    }


def build_quantities_and_timing():
    """Quantities, measurements, and timing words."""
    return {
        # Quantities
        "ounce": {"meaning": "ounce", "category": "measure"},
        "unce": {"meaning": "ounce", "category": "measure"},
        "pound": {"meaning": "pound weight", "category": "measure"},
        "punde": {"meaning": "pound", "category": "measure"},
        "handfull": {"meaning": "handful", "category": "measure"},
        "handful": {"meaning": "handful", "category": "measure"},
        "pynch": {"meaning": "pinch", "category": "measure"},
        "litil": {"meaning": "little/small", "category": "measure"},
        "litel": {"meaning": "little", "category": "measure"},
        "muche": {"meaning": "much", "category": "measure"},
        "moche": {"meaning": "much", "category": "measure"},
        # Timing
        "day": {"meaning": "day", "category": "time"},
        "dai": {"meaning": "day", "category": "time"},
        "nyght": {"meaning": "night", "category": "time"},
        "night": {"meaning": "night", "category": "time"},
        "morwe": {"meaning": "morning", "category": "time"},
        "morn": {"meaning": "morning", "category": "time"},
        "even": {"meaning": "evening", "category": "time"},
        "eve": {"meaning": "evening", "category": "time"},
        # Moon/menstrual
        "mone": {"meaning": "moon", "category": "lunar"},
        "moon": {"meaning": "moon", "category": "lunar"},
        "moneth": {"meaning": "month", "category": "lunar"},
        "month": {"meaning": "month", "category": "lunar"},
        "new": {"meaning": "new (moon)", "category": "lunar"},
        "full": {"meaning": "full (moon)", "category": "lunar"},
        "ful": {"meaning": "full", "category": "lunar"},
    }


def main():
    print("Building specialized Middle English medical vocabulary...")
    print("=" * 80)
    print()

    # Build all vocabularies
    vocab = {}

    categories = {
        "recipe_instructions": build_recipe_instructions(),
        "womens_health": build_womens_health_terms(),
        "pain_conditions": build_pain_terms(),
        "body_parts": build_body_parts(),
        "herbs": build_herb_names(),
        "quantities_timing": build_quantities_and_timing(),
    }

    total = 0
    for category_name, terms in categories.items():
        vocab.update(terms)
        print(f"{category_name}: {len(terms)} terms")
        total += len(terms)

    print()
    print(f"Total specialized vocabulary: {total} terms")
    print()

    # Save to file
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    output_path = results_dir / "specialized_medical_vocabulary.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2)

    print(f"Saved to: {output_path}")
    print()

    # Show sample entries
    print("Sample entries:")
    for i, (word, info) in enumerate(list(vocab.items())[:20]):
        print(f"  {word:15s} → {info['meaning']:20s} ({info['category']})")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
