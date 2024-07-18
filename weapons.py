# weapons.py
import random

SIMPLE_WEAPONS = [
    {'name': 'Каменный топор', 'durability': 50, 'damage': 10, 'wear': 5, 'chance': 20.0},
    {'name': 'Лук', 'durability': 80, 'damage': 15, 'wear': 4, 'chance': 15.0},
    {'name': 'Палица', 'durability': 70, 'damage': 12, 'wear': 5, 'chance': 15.0}
]

WEAPONS = SIMPLE_WEAPONS + [
    {'name': 'Железный топор', 'durability': 100, 'damage': 20, 'wear': 3, 'chance': 10.0},
    {'name': 'Арбалет', 'durability': 90, 'damage': 25, 'wear': 4, 'chance': 8.0},
    {'name': 'Револьвер', 'durability': 60, 'damage': 30, 'wear': 6, 'chance': 5.0},
    {'name': 'Пистолет', 'durability': 150, 'damage': 35, 'wear': 3, 'chance': 5.0},
    {'name': 'Двуствольное ружье', 'durability': 100, 'damage': 40, 'wear': 5, 'chance': 4.0},
    {'name': 'Дробовик', 'durability': 120, 'damage': 45, 'wear': 4, 'chance': 3.0},
    {'name': 'Самодельная винтовка', 'durability': 80, 'damage': 50, 'wear': 6, 'chance': 2.0},
    {'name': 'Магнум', 'durability': 100, 'damage': 55, 'wear': 5, 'chance': 2.0},
    {'name': 'СМГ', 'durability': 130, 'damage': 25, 'wear': 2, 'chance': 2.0},
    {'name': 'Автомат Томпсона', 'durability': 140, 'damage': 30, 'wear': 2, 'chance': 1.0},
    {'name': 'Снайперская винтовка', 'durability': 100, 'damage': 60, 'wear': 5, 'chance': 1.0},
    {'name': 'Автомат Калашникова', 'durability': 200, 'damage': 70, 'wear': 3, 'chance': 1.0}
]

def get_random_weapon():
    total_weight = sum(weapon['chance'] for weapon in WEAPONS)
    rand = random.uniform(0, total_weight)
    cumulative_weight = 0
    for weapon in WEAPONS:
        cumulative_weight += weapon['chance']
        if rand < cumulative_weight:
            return weapon
    return None
