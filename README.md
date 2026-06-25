# Cart Discount TDD Practice

## 목적

장바구니 할인 계산 로직을 **TDD(Test-Driven Development)** 방식으로 구현하는 연습 프로젝트입니다.

모든 테스트와 구현은 **계약 ID**(INV-*, E-*, UC-*, UE-*)를 기준으로 추적합니다. 계약 ID는 테스트와 구현을 잇는 **추적의 못**이며, RED → GREEN → REFACTOR 사이클 전 과정에서 동일한 ID를 참조합니다.

## 릴리스 노트

### v0.1 — 장바구니 할인 계산기 초기 릴리스

Dual-Track TDD로 장바구니 소계·문턱/VIP 할인 계산과 최소 웹 폼을 구현한 첫 버전입니다. (`pytest -q` 18 passed)

#### ✨ 기능

- **장바구니 소계 계산** — 품목별 `price × qty` 합산 (INV-1)
- **문턱 할인** — 소계 50,000원 이상 시 10% 할인, 경계값 포함 (INV-2)
- **VIP 할인** — 문턱 할인 적용 후 추가 5% 할인, 적용 순서 문턱 → VIP 고정 (INV-3)
- **결제 금액 불변식** — `0 ≤ final_total ≤ subtotal` 보장 (INV-4)
- **입력 검증 (Entity)** — `items`가 `None`이면 `TypeError`, 음수 `price`/`qty`면 인덱스 포함 `ValueError` (E-1, E-2)
- **웹 폼 (Boundary)** — `GET /` 주문 폼, `POST /calc` 최종 금액 계산·표시 (UC-1, UC-2)
- **폼 입력 검증** — `qty`가 숫자가 아니면 HTTP 400 (UE-1)
- **ECB 계층 분리** — Entity(`cart.py`)와 Boundary(`app.py`) 독립 구조

#### 🧹 기타

- Product Discovery 계약 문서 및 MomTest 발견 기록 추가
- PRD v0.1, 세션 export·Cursor 에이전트 도구 추가
- README ARRR 단계·계약 ID·REFACTOR 이력 정리 (`_validate_line_items` 추출)
- Dual-Track TDD 워크플로 규칙 (`AGENTS.md`, `.cursor/rules`)

#### 알려진 제한

- Discovery **E-2** (`items` 없이 POST 시 HTTP 500 방지) — **미구현**, 다음 사이클 예정

## 현재 ARRR 단계

`pytest -q` 기준 **18 passed**.

| Track | 범위 | RED | GREEN | REFACTOR |
| ----- | ---- | --- | ----- | -------- |
| **B — Entity** | `src/cart.py`, `tests/entity/` | ✅ | ✅ | ✅ E-2 → `_validate_line_items` |
| **A — Boundary** | `src/app.py`, `tests/boundary/` | ✅ | ✅ | — |

**다음 사이클 (미착수):** Discovery E-2 — `items` 없이 POST 시 HTTP 500 방지 ([Discovery §4](./Report/01.product-discovery-contracts.md))

### Track B — Entity RED 테스트 매핑

`tests/entity/test_cart.py`에 계약 ID별 RED 테스트가 모두 작성되어 있으며, 구현(`src/cart.py`)과 함께 GREEN 상태입니다.

| 계약 ID | 테스트 함수 | 검증 내용 | 케이스 수 |
| ------- | ----------- | --------- | --------- |
| INV-1 | `test_inv_1_subtotal_sums_price_times_qty` | `Σ(price × qty)` | 1 |
| INV-2 | `test_inv_2_threshold_discount_at_boundary` | `50000 → 45000` (경계 포함) | 1 |
| INV-2 | `test_inv_2_threshold_discount_below_boundary` | `49999 → 49999` (할인 없음) | 1 |
| INV-3 | `test_inv_3_final_total_vip_after_threshold` | VIP: `60000 → 54000 → 51300` | 1 |
| INV-4 | `test_inv_4_final_total_bounded_by_subtotal` | `0 ≤ final_total ≤ subtotal` | 8 (parametrize) |

INV-4 parametrize 입력: 빈 장바구니(VIP/비VIP), `49999`(VIP/비VIP), `50000`(VIP/비VIP), `60000`(VIP/비VIP).

```bash
pytest tests/entity/test_cart.py -k "inv_3 or inv_4" -v   # INV-3·4 — 9 passed
```

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
├── .cursor/
│   ├── hooks.json           # Cursor Hook 이벤트 등록 (프로젝트 루트 필수)
│   ├── hooks/
│   │   ├── audit.mjs        # 감사 로그·셸 허용 스크립트
│   │   └── logs/            # audit.log (런타임 생성)
│   └── rules/               # Dual-Track TDD 워크플로 규칙
├── src/
│   ├── cart.py          # Entity — INV-*, E-1, E-2
│   └── app.py           # Boundary — UC-*, UE-1
├── tests/
│   ├── entity/          # Track B — INV-*
│   └── boundary/        # Track A — UC-*, UE-1, E-*
└── Report/              # Discovery, PRD, C4
```

## Cursor Hooks

에이전트의 파일 편집·셸 실행을 감사(audit)하기 위해 [Cursor Hooks](https://cursor.com/docs/agent/hooks)를 프로젝트에 적용했습니다. 설정은 **`.cursor/hooks.json`**(프로젝트 루트)에 두어야 Cursor가 로드합니다. 저장 시 자동으로 다시 로드되며, 반영되지 않으면 Cursor를 재시작하세요.

| 이벤트 | 스크립트 | 동작 |
| ------ | -------- | ---- |
| `afterFileEdit` | `audit.mjs` | 파일 편집 후 stdin JSON을 감사 로그에 기록 |
| `beforeShellExecution` | `audit.mjs` | 셸 명령 실행 전 로그 기록 후 `{ "permission": "allow" }` 반환 |

`audit.mjs`는 stdin으로 전달된 Hook 페이로드를 ISO 타임스탬프와 함께 `.cursor/hooks/logs/audit.log`에 append합니다. `beforeShellExecution`에서는 페이로드에 `command` 필드가 있을 때만 stdout으로 허용 응답을 반환합니다.

```text
.cursor/
├── hooks.json    # version 1, 이벤트 → command 매핑
└── hooks/
    ├── audit.mjs     # Node.js (ESM) — 로그 기록·셸 허용
    └── logs/
        └── audit.log # 에이전트 편집·셸 이벤트 누적 (로컬 생성)
```

Hook 동작 확인은 Cursor **Settings → Hooks** 탭 또는 **Hooks** 출력 채널에서 할 수 있습니다. `logs/` 디렉터리는 에이전트 세션 중 자동 생성되며, 감사 로그는 로컬 개발용입니다.

**동작하지 않을 때**

- `hooks.json` 위치가 `.cursor/hooks.json`인지 확인 (`.cursor/hooks/hooks.json`은 Cursor가 읽지 않음)
- 프로젝트 **폴더**를 워크스페이스로 열었는지 확인 (단일 파일만 열면 Hook 미로드)
- Settings → Hooks에 프로젝트 Hook이 표시되는지 확인; 없으면 Cursor 재시작
- `beforeShellExecution`은 Chat 설정에서 **Run Everything** 모드일 때만 실행될 수 있음 (`afterFileEdit`는 Agent 편집 시 동작)

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
- [Cursor Hooks 설정](./.cursor/hooks.json) · [감사 스크립트](./.cursor/hooks/audit.mjs)
