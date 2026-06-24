"""Entity tests for Cart subtotal."""

import pytest

from src.cart import apply_threshold_discount, final_total, subtotal


def test_inv_1_subtotal_sums_price_times_qty():
    """INV-1: subtotal([{price:1000,qty:3},{price:2000,qty:2}]) == 7000"""
    items = [{"price": 1000, "qty": 3}, {"price": 2000, "qty": 2}]
    assert subtotal(items) == 7000


def test_inv_2_threshold_discount_at_boundary():
    """INV-2: apply_threshold_discount(50000) == 45000 (경계 포함)"""
    assert apply_threshold_discount(50000) == 45000


def test_inv_2_threshold_discount_below_boundary():
    """INV-2: apply_threshold_discount(49999) == 49999 (할인 없음)"""
    assert apply_threshold_discount(49999) == 49999


def test_inv_3_final_total_vip_after_threshold():
    """INV-3: final_total([{price:60000,qty:1}], is_vip=True) == 51300 (60000→54000→51300)"""
    items = [{"price": 60000, "qty": 1}]
    assert final_total(items, is_vip=True) == 51300


@pytest.mark.parametrize(
    "items,is_vip",
    [
        ([], False),
        ([], True),
        ([{"price": 49999, "qty": 1}], False),
        ([{"price": 49999, "qty": 1}], True),
        ([{"price": 50000, "qty": 1}], False),
        ([{"price": 50000, "qty": 1}], True),
        ([{"price": 60000, "qty": 1}], False),
        ([{"price": 60000, "qty": 1}], True),
    ],
)
def test_inv_4_final_total_bounded_by_subtotal(items, is_vip):
    """INV-4: 0 <= final_total <= subtotal (빈 장바구니, 49999, 50000, VIP/비VIP)"""
    result = final_total(items, is_vip=is_vip)
    st = subtotal(items)
    assert 0 <= result <= st
