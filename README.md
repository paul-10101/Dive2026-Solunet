# 스마트 해도 · DIVE 2026

발제사(한국해양수산연수원·국립해양박물관·㈜산타) 제공 데이터를 활용한 연령 맞춤형 해양 교육 플랫폼.
디디쌤(no-code 홈페이지 빌더) 코드블럭 위에서 동작.

Claude Code로 이어서 작업하려면 `CLAUDE.md`를 먼저 읽어주세요 (자동으로 로드됩니다).

## 빠른 시작

```bash
# 데이터 파이프라인 재실행 (원본 파일이 로컬에 있을 때)
cd data/scripts
python3 parse_ncs.py      # → ../processed/ncs_units.json
python3 build_kb.py       # → ../processed/tier{1,2,3}_*.csv
```

`site/block_a_home_game.html`, `site/block_b_diagnosis.html`을 순서대로
디디쌤 코드블럭 2개에 붙여넣으면 배포됨. 자세한 배포 시 주의사항은 `docs/didisam-constraints.md` 참고.

## 폴더 설명

| 경로 | 내용 |
|---|---|
| `data/processed/` | 연령별로 가공된 최종 데이터 (CSV 3종 + NCS JSON) |
| `data/scripts/` | 원본 → 가공 데이터를 만드는 파이썬 스크립트 |
| `site/` | 디디쌤에 실제로 배포하는 HTML 코드블럭 2개 |
| `docs/` | 디디쌤 플랫폼 자체의 기술 제약사항 정리 |
