#!/usr/bin/env python3
"""
src/template.html + data/*.json -> dist/daily_job_block.html 생성.

- .env(레포 루트)의 WORKNET_API_KEY를 읽어 템플릿의 __WORKNET_API_KEY__ 플레이스홀더에 치환한다.
- ocean_jobs_whitelist.json(오늘의 직업 로테이션 대상)을 JS 상수로 인라인한다
  (디디쌤 코드블럭은 정적 파일 하나만 붙여넣는 구조라 런타임에 별도 JSON을 fetch할 수 없음).
- 상세 데이터는 mock이 아니라 워크넷 오픈API를 브라우저에서 직접 실시간 호출한다(src/template.html 참고).
- .env는 git에 커밋되지 않으므로, 이 스크립트는 붙여넣기 직전에 로컬에서 매번 실행해야 한다.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
ENV_PATH = REPO_ROOT / ".env"
TEMPLATE_PATH = ROOT / "src" / "template.html"
WHITELIST_PATH = ROOT / "data" / "ocean_jobs_whitelist.json"
OUT_PATH = ROOT / "dist" / "daily_job_block.html"
PREVIEW_PATH = ROOT / "dist" / "preview.html"

PREVIEW_WRAPPER = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>일일 직업 추천 블록 - 로컬 미리보기</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0;padding:32px;background:#0f0f0f;">
{fragment}
</body>
</html>
"""


def read_env_var(name):
    if not ENV_PATH.exists():
        raise SystemExit(f"'.env' 파일이 없습니다: {ENV_PATH}\n.env.example을 참고해서 만들어주세요.")
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == name:
            return value.strip()
    raise SystemExit(f"'.env'에 {name} 값이 없습니다.")


def main():
    api_key = read_env_var("WORKNET_API_KEY")

    whitelist_data = json.loads(WHITELIST_PATH.read_text(encoding="utf-8"))
    whitelist_jobs_json = json.dumps(whitelist_data["jobs"], ensure_ascii=False)

    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = html.replace("__WORKNET_API_KEY__", api_key)
    html = html.replace("/*__SNC_WHITELIST_JSON__*/[]", whitelist_jobs_json)

    remaining_placeholders = re.findall(r"__[A-Z_]+__|/\*__[A-Z_]+__\*/", html)
    if remaining_placeholders:
        raise SystemExit(f"치환되지 않은 플레이스홀더가 남아있습니다: {remaining_placeholders}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")

    # dist/daily_job_block.html은 디디쌤에 붙여넣는 조각 그대로라 <meta charset>이 없다.
    # file://로 직접 열면 브라우저가 인코딩을 잘못 추측해 한글이 깨지므로, 로컬 확인용 문서를 따로 만든다.
    PREVIEW_PATH.write_text(PREVIEW_WRAPPER.format(fragment=html), encoding="utf-8")

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"생성 완료: {OUT_PATH} ({size_kb:.1f} KB)")
    print(f"로컬 확인용: {PREVIEW_PATH} (브라우저로 이 파일을 열어서 테스트할 것)")
    if size_kb > 30:
        print("⚠️  30KB를 초과했습니다. docs/didisam-constraints.md 4번 항목 참고 (스크립트가 잘릴 수 있음).")


if __name__ == "__main__":
    main()
