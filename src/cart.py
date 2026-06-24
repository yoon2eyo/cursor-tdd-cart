"""장바구니 할인 계산 — Entity 계층 (Track B / Domain).

계약(Contracts):
INV-1 subtotal == Σ(price*qty)
INV-2 amount>=50000 → round(*0.9) / <50000 그대로 (경계 포함)
INV-3 문턱할인 후 VIP면 round(*0.95). 순서 문턱→VIP 고정
INV-4 0 <= final_total <= subtotal (할인은 금액을 늘리지 않는다)
E-1   items is None → TypeError
E-2   price/qty 음수 → ValueError(인덱스 포함)
"""

THRESHOLD = 50000  # INV-2 문턱 금액 (SSOT)
THRESHOLD_RATE = 0.9  # INV-2 문턱 할인율 (SSOT)


def _validate_line_items(items):
    for i, item in enumerate(items):  # E-2
        if item["price"] < 0 or item["qty"] < 0:  # E-2
            raise ValueError(f"negative value at index {i}")  # E-2


def subtotal(items):
    if items is None:  # E-1
        raise TypeError("items is None")  # E-1
    _validate_line_items(items)  # E-2
    total = 0  # INV-1
    for item in items:  # INV-1
        total += item["price"] * item["qty"]  # INV-1
    return total  # INV-1


def apply_threshold_discount(amount):
    if amount >= THRESHOLD:  # INV-2
        return round(amount * THRESHOLD_RATE)  # INV-2
    return amount  # INV-2


def final_total(items, is_vip=False):
    st = subtotal(items)  # INV-4
    amount = apply_threshold_discount(st)  # INV-3
    if is_vip:  # INV-3
        amount = round(amount * 0.95)  # INV-3
    return amount  # INV-4
