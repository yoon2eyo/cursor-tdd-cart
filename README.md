# Cart Discount TDD Practice

## 목적

장바구니 할인 계산 로직을 **TDD(Test-Driven Development)** 방식으로 구현하는 연습 프로젝트입니다.

모든 테스트와 구현은 **계약 ID**(INV-*, E-*)를 기준으로 추적합니다. 계약 ID는 테스트와 구현을 잇는 **추적의 못**이며, RED → GREEN → REFACTOR 사이클 전 과정에서 동일한 ID를 참조합니다.

현재 단계는 **RED 준비 단계**입니다. 아직 구현이 완료되었다고 가정하지 않습니다.

## 핵심 원칙

- **ID에 없는 동작은 만들지 않는다.** 계약표에 없는 할인 정책, 예외, 기능은 구현하지 않습니다.
- **테스트가 먼저다.** 구현보다 실패하는 테스트가 항상 앞섭니다.
- **RED → GREEN → REFACTOR** 순서를 따릅니다.
- **과잉 구현을 금지한다.** "좋아 보이는" 기능, 추측 기반 확장, 요청되지 않은 리팩터링을 하지 않습니다.

## 계약 ID 목록

| ID    | 계약(불변식 / 에러)                                                 | 근거 레벨 | 계층        |
| ----- | ------------------------------------------------------------ | ----- | --------- |
| INV-1 | `subtotal(items) == Σ(price × qty)`                          | —     | Entity    |
| INV-2 | `amount ≥ 50000 → round(amount×0.9)` / `< 50000 → 그대로` 경계 포함 | L1    | Entity    |
| INV-3 | `final = 문턱할인 적용 후, VIP면 round(×0.95)`. 순서 문턱→VIP 고정         | L2    | Entity    |
| INV-4 | 모든 입력에서 `0 ≤ final_total ≤ subtotal`. 할인은 금액을 늘리지 않는다        | L3    | Entity    |
| E-1   | `items is None → TypeError`                                  | L0    | Boundary* |
| E-2   | `price` 또는 `qty`가 음수 → `ValueError`, 인덱스 포함                  | L0    | Boundary* |

## 계약 ID 설명

### INV-1

장바구니 소계는 각 품목의 `price × qty`를 모두 더한 값과 같아야 합니다. 순수 도메인 계산의 기본 불변식입니다.

### INV-2

문턱 할인 규칙입니다. 소계(또는 `amount`)가 50,000원 이상이면 `round(amount × 0.9)`를 적용하고, 50,000원 미만이면 할인 없이 그대로 반환합니다. 경계값 50,000원은 할인 적용 대상에 포함됩니다.

### INV-3

VIP 할인은 문턱 할인 **이후**에만 적용합니다. VIP 고객이면 문턱 할인 결과에 `round(× 0.95)`를 추가로 적용합니다. 적용 순서는 **문턱 → VIP**로 고정됩니다.

### INV-4

유효한 입력에 대해 최종 결제 금액(`final_total`)은 0 이상이며 소계(`subtotal`) 이하여야 합니다. 할인은 결제 금액을 늘리지 않습니다.

### E-1

`items`가 `None`이면 `TypeError`를 발생시킵니다. 입력 누락·타입 오류에 대한 경계 계약입니다.

### E-2

`price` 또는 `qty`가 음수이면 해당 인덱스를 포함한 `ValueError`를 발생시킵니다. 잘못된 입력을 0원 등으로 조용히 처리하지 않습니다.

## 계층 의미

### Entity

`src/cart.py`는 **Entity 계층**입니다. Flask 등 외부 프레임워크를 import하지 않으며, 순수 도메인 계산 로직과 불변식(INV-*)을 담당합니다.

### Boundary*

E-1, E-2는 **Boundary*** 계약입니다. 원래는 HTTP 폼·API 등 입력 검증 경계에 가까운 규칙이지만, **현재 실습에서는 도메인 함수 진입점에서 검증**합니다. 즉, `cart.py`의 함수가 호출될 때 `items is None`, 음수 `price`/`qty`를 검사합니다.

## 예상 파일 구조

```text
.
├── README.md
├── src/
│   └── cart.py
└── tests/
    └── test_cart.py
```

## TDD 진행 순서

1. **RED** — 계약 ID별 실패 테스트를 작성합니다. 테스트 파일·함수·docstring에 계약 ID(INV-*, E-*)를 명시합니다.
2. **GREEN** — 해당 ID를 만족하는 **최소 구현**만 작성합니다. 구현 줄에는 충족한 계약 ID를 주석으로 표기합니다.
3. **REFACTOR** — 모든 테스트가 통과한 상태에서만 구조를 개선합니다. REFACTOR 전후로 `pytest -q`로 동작 불변을 확인합니다.

## REFACTOR 계획 (Track B · subtotal)

E-2 검증을 `_validate_line_items(items)` private helper로 추출하는 리팩터입니다.

| 항목 | 내용 |
| ---- | ---- |
| 목적 | Mixed Responsibilities 해소 — E-2만 분리, E-1은 `subtotal`에 유지 |
| 변경 | `subtotal` 내 음수 검증 루프 → `_validate_line_items(items)` |
| 변경 파일 | `src/cart.py`만 (`tests/` 수정 없음) |
| 제외 | `sum()` 변환, 상수 추출, `apply_threshold_discount` / `final_total` / `THRESHOLD` |
| 예상 diff | `cart.py` +3~5줄 |

### 동작 불변 체크리스트

| ID | 확인 |
| ---- | ---- |
| E-1 | `subtotal(None)` → `TypeError` |
| E-2 | 음수 `price`/`qty` → `ValueError`, 메시지에 인덱스 포함 |
| INV-1 | `[{price:1000,qty:3},{price:2000,qty:2}]` → `7000` |

### 완료 기준

- REFACTOR 전후 `pytest -q` GREEN
- (커밋 시) `refactor: extract E-2 validation to _validate_line_items`

- [x] REFACTOR 완료 (E-2 → `_validate_line_items` 추출)

## 테스트 실행

```bash
pytest -q
```

`-q`는 **quiet mode**입니다. 테스트 결과를 간략하게 출력합니다.

## 구현 금지 사항

- 할인 정책 추가 금지
- 쿠폰, 세금, 배송비, 포인트 기능 추가 금지
- ID에 없는 예외 처리 추가 금지
- UI, CLI, DB, API 코드 추가 금지
