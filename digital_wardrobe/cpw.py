"""Cost-per-wear, derived on read so it can never drift from the counters.

    CPW = purchase_price / MAX(wear_count, 1)
"""


def cost_per_wear(purchase_price, wear_count) -> float:
    price = float(purchase_price)
    count = max(int(wear_count), 1)
    return round(price / count, 2)
