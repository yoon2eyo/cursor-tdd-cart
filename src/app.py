"""Flask 주문 폼 — Boundary 계층 (Track A / HTTP·입력).

계약(Contracts):
UC-1  GET / → 200, 본문에 qty·price·VIP 입력 폼 포함
UC-2  POST /calc (price·qty·vip) → 본문에 final_total 결과 표시
UE-1  qty가 숫자가 아니면 400 + 에러 메시지

ECB 역할:
- Boundary: Flask 라우트·폼 입력·응답만 담당한다.
- Entity: 할인 계산은 src.cart.final_total에 위임한다 (할인 공식·문턱·VIP 순서 재구현 금지).
- cart.py는 Flask를 import하지 않는다; 이 모듈만 cart → Boundary 방향으로 의존한다.

폼 필드 SSOT: price, qty, vip(checkbox), POST action=/calc
"""

from flask import Flask, request

from src.cart import final_total

app = Flask(__name__)


@app.get("/")
def index():
    return (
        '<form method="post" action="/calc">'
        '<input name="price" type="text">'
        '<input name="qty" type="text">'
        '<input name="vip" type="checkbox">'
        '<button type="submit">Calc</button>'
        '</form>'
    ), 200  # UC-1


@app.post("/calc")
def calc():
    try:
        qty = int(request.form.get("qty", ""))  # UE-1
    except ValueError:
        return "invalid qty", 400  # UE-1
    price = int(request.form.get("price", "0"))  # UC-2
    is_vip = "vip" in request.form  # UC-2
    items = [{"price": price, "qty": qty}]
    total = final_total(items, is_vip=is_vip)  # UC-2
    return str(total), 200  # UC-2
