# Cart Discount TDD Practice

## 목적

장바구니 할인 계산 로직을 **TDD(Test-Driven Development)** 방식으로 구현하는 연습 프로젝트입니다.

모든 테스트와 구현은 **계약 ID**(INV-*, E-*, UC-*, UE-*)를 기준으로 추적합니다. 계약 ID는 테스트와 구현을 잇는 **추적의 못**이며, RED → GREEN → REFACTOR 사이클 전 과정에서 동일한 ID를 참조합니다.

## 현재 ARRR 단계

`pytest -q` 기준 **18 passed**.

| Track | 범위 | RED | GREEN | REFACTOR |
| ----- | ---- | --- | ----- | -------- |
| **B — Entity** | `src/cart.py`, `tests/entity/` | ✅ | ✅ | ✅ E-2 → `_validate_line_items` |
| **A — Boundary** | `src/app.py`, `tests/boundary/` | ✅ | ✅ | — |

**다음 사이클 (미착수):** Discovery E-2 — `items` 없이 POST 시 HTTP 500 방지 ([Discovery §4](./Report/01.product-discovery-contracts.md))

## 핵심 원칙

- **ID에 없는 동작은 만들지 않는다.** 계약표에 없는 할인 정책, 예외, 기능은 구현하지 않습니다.
- **테스트가 먼저다.** 구현보다 실패하는 테스트가 항상 앞섭니다.
- **RED → GREEN → REFACTOR** 순서를 따릅니다.
- **과잉 구현을 금지한다.** "좋아 보이는" 기능, 추측 기반 확장, 요청되지 않은 리팩터링을 하지 않습니다.

## 계약 ID 목록

### Entity (`src/cart.py`)

| ID    | 계약(불변식 / 에러)                                                 | ARRR  |
| ----- | ------------------------------------------------------------ | ----- |
| INV-1 | `subtotal(items) == Σ(price × qty)`                          | GREEN |
| INV-2 | `amount ≥ 50000 → round(amount×0.9)` / `< 50000 → 그대로` 경계 포함 | GREEN |
| INV-3 | `final = 문턱할인 적용 후, VIP면 round(×0.95)`. 순서 문턱→VIP 고정         | GREEN |
| INV-4 | 모든 입력에서 `0 ≤ final_total ≤ subtotal`. 할인은 금액을 늘리지 않는다        | GREEN |
| E-1   | `items is None → TypeError`                                  | GREEN |
| E-2   | `price` 또는 `qty`가 음수 → `ValueError`, 인덱스 포함                  | REFACTOR |

### Boundary (`src/app.py`)

| ID    | 계약                                              | ARRR  |
| ----- | ----------------------------------------------- | ----- |
| UC-1  | `GET /` → 200, price·qty·vip 폼 포함                | GREEN |
| UC-2  | `POST /calc` → `final_total` 위임, 결과 표시          | GREEN |
| UE-1  | `qty` 비숫자 → HTTP 400                            | GREEN |

E-1, E-2 테스트는 `tests/boundary/`에 있으며, 구현은 Entity 진입점(`cart.py`)에서 수행합니다.

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

## 계층 (ECB)

| 계층 | 경로 | 책임 |
| ---- | ---- | ---- |
| **Entity** | `src/cart.py` | 소계·할인·불변식. Flask import 금지 |
| **Boundary** | `src/app.py` | HTTP 폼·입력 파싱. 할인 공식 재구현 금지 |

## 파일 구조

```text
.
├── README.md
├── AGENTS.md
├── src/
│   ├── cart.py          # Entity — INV-*, E-1, E-2
│   └── app.py           # Boundary — UC-*, UE-1
├── tests/
│   ├── entity/          # Track B — INV-*
│   └── boundary/        # Track A — UC-*, UE-1, E-*
└── Report/              # Discovery, PRD, C4
```

## TDD 진행 순서 (ARRR)

1. **RED** — 계약 ID별 실패 테스트를 작성합니다. 테스트 파일·함수·docstring에 계약 ID를 명시합니다.
2. **GREEN** — 해당 ID를 만족하는 **최소 구현**만 작성합니다. 구현 줄에는 충족한 계약 ID를 주석으로 표기합니다.
3. **REFACTOR** — 모든 테스트가 통과한 상태에서만 구조를 개선합니다. REFACTOR 전후로 `pytest -q`로 동작 불변을 확인합니다.

## REFACTOR 이력 (Track B · subtotal)

E-2 검증을 `_validate_line_items(items)` private helper로 추출했습니다.

| 항목 | 내용 |
| ---- | ---- |
| 목적 | Mixed Responsibilities 해소 — E-2만 분리, E-1은 `subtotal`에 유지 |
| 변경 | `subtotal` 내 음수 검증 루프 → `_validate_line_items(items)` |
| 변경 파일 | `src/cart.py`만 (`tests/` 수정 없음) |

- [x] REFACTOR 완료 (E-2 → `_validate_line_items` 추출)
- [x] REFACTOR 전후 `pytest -q` GREEN

## 테스트 실행

```bash
pytest -q                    # 전체 (18 tests)
pytest tests/entity -q       # Track B — Entity
pytest tests/boundary -q     # Track A — Boundary
```

## 구현 금지 사항

- 계약 ID 없는 할인 정책·예외·기능 추가
- 쿠폰, 세금, 배송비, 포인트
- Entity에 Flask 의존성
- Boundary에 할인 공식 중복 구현

## 참조

- [Product Discovery 계약](./Report/01.product-discovery-contracts.md)
- [PRD](./Report/03.PRD.md)
- [C4 Architecture](./Report/04.c4-architecture.md)
- [프로젝트 지도](./AGENTS.md)
