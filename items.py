# items.py
import random

ITEMS = [
    {'name': 'Швейный набор', 'max_quantity': 100},
    {'name': 'Шестеренка', 'max_quantity': 100},
    {'name': 'Труба', 'max_quantity': 100},
    {'name': 'Дорожный знак', 'max_quantity': 100}
]

def get_random_item():
    return random.choice(ITEMS)
