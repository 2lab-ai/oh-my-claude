# Decision Gate — 자율 판단 vs 유저 질문 판별기

## 핵심 원칙

**최대한 자율 판단. 나중에 바꾸기 어려운 것만 물어본다.**

모든 기술적 결정에서 "이걸 나중에 뒤집으려면 몇 줄 고쳐야 하나?" (switching cost)를 예측하고, 그 tier에 따라 행동한다.

## Switching Cost Tiers

| Tier   | Lines  | 예시                              |
|--------|--------|-----------------------------------|
| tiny   | ~5     | Config 값, 상수, 문자열 리터럴      |
| small  | ~20    | 한 함수, 한 파일, 로컬 리팩터       |
| medium | ~50    | 여러 파일, 인터페이스 변경           |
| large  | ~100   | 횡단 관심사, 스키마 마이그레이션      |
| xlarge | ~500   | 아키텍처 전환, 프레임워크 교체        |

## 판단 알고리즘

```
for each decision:
  1. switching_cost 예측 = 나중에 이 결정을 뒤집으려면 몇 줄 변경?

  2. if switching_cost < small (~20줄):
       → 자율 판단. 유저에게 묻지 않음.
       → 판단 로그를 spec/trace 문서에 기록.

  3. elif switching_cost == small (~20줄):
       → 자율 결정. 유저에게 묻지 않음.
       → 결과를 유저에게 보고.
       → 판단 로그를 spec/trace 문서에 기록.

  4. elif switching_cost >= medium (~50줄):
       → 유저에게 질문 (AskUserQuestion)
       → 질문에 [tier ~N줄] 표기 필수
       → 선택지 + 트레이드오프 제시
```

## small 자율 결정 보고 형식

small tier 결정은 자율적으로 내리되, 유저에게 결과를 보고한다:

```markdown
### Auto-Decision: [결정 제목]
- **결정**: [선택한 옵션]
- **switching cost**: small (~N줄)
- **판단 근거**: [왜 이렇게 결정했는가]
- **변경 시 영향**: [나중에 바꾸려면 어디를 고치면 되는지]
```

## 유저 질문 시 필수 포함 사항

1. **`[tier ~N줄]` prefix** — 결정의 무게를 즉시 파악
2. **현재 상태** — 코드/설계 스니펫 포함
3. **각 선택지의 구체적 행동** — 어떤 파일, 어떤 변경, 작업량
4. **트레이드오프** — 장단점, 리스크
5. **추천** — 왜 이 방향이 좋은지

## 자율 판단 영역 (switching cost < small) — 묻지 않는다

- 변수/함수 이름, 파일 위치, 에러 메시지 문구
- Config 값, 상수, UI 스타일링
- 한 함수 내 구현 방식

## 자율 결정 + 보고 영역 (switching cost == small) — 결정 후 보고

- 유틸리티 구조, DTO 필드명
- 기존 패턴과 동일한 validation/auth 흐름
- 한 파일 내 리팩터

## 유저 질문 영역 (switching cost >= medium) — 반드시 묻는다

- 데이터 모델/스키마, 아키텍처 패턴
- 주요 라이브러리 선택, 보안 방식
- 여러 파일 걸친 인터페이스 설계

## NEVER

- switching cost 예측 없이 "일단 물어보자"
- tier 표기 없이 유저에게 질문
- 사소한 결정으로 유저 피로도 증가시키기
- small 자율 결정 후 보고를 생략하기
