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

_PAGE_STYLE = """
    * { box-sizing: border-box; }
    body {
        margin: 0;
        font-family: "Segoe UI", system-ui, sans-serif;
        line-height: 1.5;
        color: #1a1a1a;
        background: #f4f6f8;
    }
    main {
        max-width: 32rem;
        margin: 2rem auto;
        padding: 1.5rem;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    }
    h1 { margin: 0 0 0.5rem; font-size: 1.35rem; }
    .lead { margin: 0 0 1.25rem; color: #444; }
    .field { margin-bottom: 1rem; }
    .field label {
        display: block;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .field input[type="text"] {
        width: 100%;
        padding: 0.5rem 0.65rem;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 1rem;
    }
    .field-hint { margin: 0.25rem 0 0; font-size: 0.875rem; color: #666; }
    .checkbox-row {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.75rem;
        background: #f9fafb;
        border-radius: 4px;
    }
    .checkbox-row input { margin-top: 0.2rem; }
    .info {
        margin: 1.25rem 0;
        padding: 0.75rem 1rem;
        background: #eef6ff;
        border-left: 3px solid #3b82f6;
        border-radius: 0 4px 4px 0;
        font-size: 0.9rem;
    }
    .info ul { margin: 0.35rem 0 0; padding-left: 1.2rem; }
    button[type="submit"] {
        width: 100%;
        padding: 0.65rem 1rem;
        font-size: 1rem;
        font-weight: 600;
        color: #fff;
        background: #2563eb;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    button[type="submit"]:hover { background: #1d4ed8; }
    .result-amount {
        margin: 1rem 0;
        padding: 1rem;
        text-align: center;
        background: #f0fdf4;
        border-radius: 6px;
    }
    .result-amount strong { font-size: 1.75rem; color: #15803d; }
    .back-link { display: inline-block; margin-top: 1rem; color: #2563eb; }
    .error-box {
        padding: 0.75rem 1rem;
        background: #fef2f2;
        border-left: 3px solid #dc2626;
        border-radius: 0 4px 4px 0;
        color: #991b1b;
    }
"""


def _html_page(title, body):
    return (
        f"<!DOCTYPE html><html lang=\"ko\"><head>"
        f"<meta charset=\"utf-8\">"
        f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{title}</title>"
        f"<style>{_PAGE_STYLE}</style></head>"
        f"<body><main>{body}</main></body></html>"
    )


@app.get("/")
def index():
    body = (
        "<h1>장바구니 할인 계산기</h1>"
        "<p class=\"lead\">품목의 <strong>단가</strong>와 <strong>수량</strong>을 입력하고, "
        "해당되면 <strong>VIP</strong> 회원 여부를 선택한 뒤 계산하세요.</p>"
        '<form method="post" action="/calc">'
        '<div class="field">'
        '<label for="price">단가 (원)</label>'
        '<input id="price" name="price" type="text" inputmode="numeric" '
        'placeholder="예: 60000" required>'
        '<p class="field-hint">품목 1개당 가격입니다.</p>'
        "</div>"
        '<div class="field">'
        '<label for="qty">수량</label>'
        '<input id="qty" name="qty" type="text" inputmode="numeric" '
        'placeholder="예: 1" required>'
        '<p class="field-hint">구매 개수입니다. 숫자만 입력하세요.</p>'
        "</div>"
        '<div class="checkbox-row">'
        '<input id="vip" name="vip" type="checkbox">'
        '<label for="vip">VIP 회원 (문턱 할인 적용 후 추가 5% 할인)</label>'
        "</div>"
        '<div class="info">'
        "<strong>적용되는 할인</strong>"
        "<ul>"
        "<li>소계 50,000원 이상 → 10% 문턱 할인</li>"
        "<li>VIP 회원 → 문턱 할인 후 5% 추가 할인</li>"
        "</ul>"
        "</div>"
        '<button type="submit">최종 금액 계산</button>'
        "</form>"
    )
    return _html_page("장바구니 할인 계산기", body), 200  # UC-1


@app.post("/calc")
def calc():
    try:
        qty = int(request.form.get("qty", ""))  # UE-1
    except ValueError:
        body = (
            "<h1>입력 오류</h1>"
            '<div class="error-box">'
            "<strong>수량</strong>에는 숫자만 입력할 수 있습니다. "
            "다시 확인해 주세요."
            "</div>"
            '<a class="back-link" href="/">← 다시 계산</a>'
        )
        return _html_page("입력 오류", body), 400  # UE-1
    price = int(request.form.get("price", "0"))  # UC-2
    is_vip = "vip" in request.form  # UC-2
    items = [{"price": price, "qty": qty}]
    total = final_total(items, is_vip=is_vip)  # UC-2
    vip_note = " (VIP 5% 추가 할인 적용)" if is_vip else ""
    body = (
        "<h1>계산 결과</h1>"
        "<p class=\"lead\">입력하신 내용을 바탕으로 최종 결제 금액을 계산했습니다.</p>"
        '<div class="result-amount">'
        f"<div>최종 결제 금액{vip_note}</div>"
        f"<strong>{total}</strong>원"
        "</div>"
        f"<p>단가 {price}원 × 수량 {qty}개</p>"
        '<a class="back-link" href="/">← 다시 계산</a>'
    )
    return _html_page("계산 결과", body), 200  # UC-2
