"""Boundary tests — Track A (Flask) · Entity 진입점(E-*).

계약: UC-1 GET / 폼 · UC-2 POST /calc 결과표시 · UE-1 비숫자 qty → 400
"""

import pytest

from src.app import app
from src.cart import subtotal


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_uc_1_get_root_returns_200_with_qty_input(client):
    """UC-1: GET / → 200, 본문에 name="qty" 입력."""
    response = client.get("/")
    assert response.status_code == 200
    assert 'name="qty"' in response.get_data(as_text=True)


def test_uc_2_post_calc_displays_final_total(client):
    """UC-2: POST /calc (price·qty·vip) → 본문에 51300."""
    response = client.post(
        "/calc",
        data={"price": 60000, "qty": 1, "vip": "on"},
    )
    assert response.status_code == 200
    assert "51300" in response.get_data(as_text=True)


def test_ue_1_non_numeric_qty_returns_400(client):
    """UE-1: qty가 숫자가 아니면 400."""
    response = client.post(
        "/calc",
        data={"price": 60000, "qty": "abc"},
    )
    assert response.status_code == 400


def test_e_1_subtotal_none_raises_type_error():
    """E-1: subtotal(None) raises TypeError."""
    with pytest.raises(TypeError):
        subtotal(None)


def test_e_2_negative_price_raises_value_error_with_index():
    """E-2: negative price raises ValueError with index in message."""
    items = [{"price": -100, "qty": 1}]
    with pytest.raises(ValueError, match=r"0"):
        subtotal(items)


def test_e_2_negative_qty_raises_value_error_with_index():
    """E-2: negative qty raises ValueError with index in message."""
    items = [{"price": 100, "qty": -1}]
    with pytest.raises(ValueError, match=r"0"):
        subtotal(items)
