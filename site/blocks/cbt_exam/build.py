#!/usr/bin/env python3
"""
두 가지 산출물을 만든다 (둘 다 dist/, .gitignore로 커밋 제외됨):

1. dist/cbt_exam_block.html — 통짜 코드블럭(문제 데이터 인라인). 디디쌤에 그대로 붙여넣는 방식.
   template.html(~25KB) + questions.json(~45KB) 합쳐 70KB를 넘기 때문에
   docs/didisam-constraints.md 4번 항목(스크립트 잘림 위험)에 걸릴 가능성이 있음 — 가급적 loader.html 사용.
2. dist/loader.html (권장) — GitHub raw로 src/template.html + data/questions.json을
   fetch해와서 실행 시점에 플레이스홀더를 채우는 짧은 로더. 디디쌤에는 이것만 붙여넣으면 되고,
   이후 template.html/questions.json을 GitHub main에 수정·push하면 재배포 없이 반영됨.
3. dist/preview.html — 로컬 브라우저(file://)로 바로 열어서 확인하는 미리보기 문서.

API 키 등 비밀값이 없으므로 build.py 실행에 별도 .env가 필요 없다.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "src" / "template.html"
LOADER_TEMPLATE_PATH = ROOT / "src" / "loader_template.html"
DATA_PATH = ROOT / "data" / "questions.json"
OUT_PATH = ROOT / "dist" / "cbt_exam_block.html"
LOADER_OUT_PATH = ROOT / "dist" / "loader.html"
PREVIEW_PATH = ROOT / "dist" / "preview.html"

PLACEHOLDER = "/*__SNC_CBT_QUESTIONS_JSON__*/[]"

PREVIEW_WRAPPER = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>해기사 CBT 모의고사 - 로컬 미리보기</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0;">
{fragment}
</body>
</html>
"""


def main():
    questions_json = DATA_PATH.read_text(encoding="utf-8").strip()

    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    if PLACEHOLDER not in html:
        raise SystemExit(f"template.html에서 플레이스홀더를 찾을 수 없습니다: {PLACEHOLDER}")
    html = html.replace(PLACEHOLDER, questions_json)

    remaining_placeholders = re.findall(r"__[A-Z_]+__|/\*__[A-Z_]+__\*/", html)
    if remaining_placeholders:
        raise SystemExit(f"치환되지 않은 플레이스홀더가 남아있습니다: {remaining_placeholders}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    PREVIEW_PATH.write_text(PREVIEW_WRAPPER.format(fragment=html), encoding="utf-8")

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"생성 완료: {OUT_PATH} ({size_kb:.1f} KB)")
    print(f"로컬 확인용: {PREVIEW_PATH} (브라우저로 이 파일을 열어서 테스트할 것)")
    if size_kb > 30:
        print("⚠️  30KB를 초과했습니다. 디디쌤에는 가급적 dist/loader.html을 붙여넣을 것.")

    loader_html = LOADER_TEMPLATE_PATH.read_text(encoding="utf-8")
    LOADER_OUT_PATH.write_text(loader_html, encoding="utf-8")
    print(f"생성 완료(GitHub 로더 방식): {LOADER_OUT_PATH} "
          f"({len(loader_html.encode('utf-8')) / 1024:.1f} KB) — 이 짧은 스크립트만 디디쌤에 붙여넣으면 됨")


if __name__ == "__main__":
    main()
