# 해기사 CBT 모의고사 블록

Figma Make 시안("CBT 모의고사")을 디디쌤 코드블럭으로 이식한 것.
2025년 정기 제1회 해기사 시험(소형선박조종사 / 3급항해사(상선) / 3급항해사(어선)) 기출문제를
과목 무관 무작위 최대 20문항으로 출제하고, 제출 시 채점 + 오답만 정답과 함께 보여준다.

## 빌드 방법

API 키 등 비밀값이 없으므로 `.env` 없이 바로 실행하면 된다.

```bash
python3 site/blocks/cbt_exam/build.py
```

산출물 3종이 `dist/`에 생성됨(전부 git-ignored):

- `preview.html` — 로컬에서 `file://`로 바로 열어 확인하는 미리보기.
- **`loader.html` (권장)** — 짧은 로더 스크립트. GitHub의 `src/template.html` +
  `data/questions.json`을 실행 시점에 fetch해와서 렌더링한다.
  **디디쌤에는 이걸 붙여넣을 것.** 이후 `src/template.html`을 GitHub main에 수정·push하면
  디디쌤에 다시 붙여넣지 않아도 바로 반영됨.
- `cbt_exam_block.html` — 통짜 코드블럭(문제 데이터 인라인, 약 69KB). `docs/didisam-constraints.md`
  4번 항목(30KB 초과 시 스크립트 잘림 위험)에 걸릴 수 있어 `loader.html`이 안 될 때의 대체 수단.

⚠️ `loader.html`은 `raw.githubusercontent.com`을 fetch한다 — 발행된 디디쌤 사이트가 이 도메인을
허용하는지 실제 배포로 아직 검증 전(`docs/didisam-constraints.md`의 jsdelivr 차단 사례 참고,
다른 도메인이라 막힐 가능성은 낮음). 안 되면 `cbt_exam_block.html`로 대체할 것.
또한 `main`에 아직 이 파일들이 머지되기 전에는 raw URL이 404가 나므로, 브랜치 상태에서 테스트하려면
`loader_template.html`의 URL을 임시로 현재 브랜치명으로 바꿔서 확인해야 한다.

## 검증

- `node`로 최소 DOM 스텁을 만들어 실제 문제 데이터를 넣고 선택→응시(20문항 자동 응답)→제출→채점→
  재시작 전체 플로우를 헤드리스로 실행 확인함(브라우저 자동화 도구가 없는 환경이라 대체 검증).
- 문제 은행은 3종(소형선박조종사 28문항, 3급항해사(상선) 40문항, 3급항해사(어선) 40문항) —
  Figma Make 원본 `questions.json`을 그대로 옮김, 가공 없음.

## 파일 구조

- `src/template.html` — 실제 위젯 코드(HTML+CSS+JS 한 파일, `#snc-root` 스코프, `snc` 접두사 준수).
  문제 데이터는 `/*__SNC_CBT_QUESTIONS_JSON__*/[]` 플레이스홀더로 분리되어 있음(파일 크기 30KB 제한 대응).
- `data/questions.json` — 문제 은행 원본(Figma Make에서 그대로 이관).
- `build.py` — 위 둘을 합쳐 `dist/`에 통짜 파일 + 로더 + 미리보기를 생성하는 스크립트(표준 라이브러리만 사용).

## TODO

- [ ] 디디쌤 실제 발행 사이트에서 `loader.html` 붙여넣기 테스트 (raw.githubusercontent.com 허용 여부 확인)
- [ ] 오답 해설 텍스트 추가 여부 검토 (원본 문제지에 해설이 없어 현재는 정답만 표시)
