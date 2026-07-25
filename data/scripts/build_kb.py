"""
디디쌤 3-Tier 지식베이스 빌더
DIVE 2026 Track 6 (해양수산연수원 x 해양박물관 x 산타)

입력: /mnt/user-data/uploads/ 의 8개 원본 파일
출력: output/tier1_kids.csv, tier2_teens.csv, tier3_adults.csv
      각 row = {source, category, title, target_raw, content, tags}
"""

import re
import json
import pandas as pd

UPLOAD = "/mnt/user-data/uploads"
OUT = "/home/claude/didisam-kb/output"

records = {"tier1": [], "tier2": [], "tier3": []}


def add(tier, source, category, title, target_raw, content, tags=""):
    content = str(content).strip()
    if not content or content == "0" or content == "nan":
        return
    records[tier].append({
        "source": source, "category": category, "title": str(title).strip(),
        "target_raw": target_raw, "content": content, "tags": tags,
    })


def fix_date(v):
    """엑셀 시리얼 넘버 또는 문자열 날짜를 YYYY-MM-DD로 정규화."""
    if pd.isna(v):
        return ""
    if isinstance(v, (int, float)):
        try:
            return pd.to_datetime(v, unit="D", origin="1899-12-30").strftime("%Y-%m-%d")
        except Exception:
            return str(v)
    return str(v)[:10]


# ── 1. 박물관 교육운영 데이터 (핵심 소스: 대상별로 이미 분리돼 있음) ──
df = pd.read_excel(f"{UPLOAD}/샘플데이터_국립해양박물관_교육_운영_데이터.xlsx")
TIER_MAP = {
    "어린이": ["tier1"], "가족": ["tier1"],
    "청소년": ["tier2"], "전체": ["tier1", "tier2"],
    "성인": ["tier3"], "전문가": ["tier3"],
}
for _, row in df.iterrows():
    tiers = TIER_MAP.get(row["대상"], [])
    period = f"{fix_date(row['시작일자'])}~{fix_date(row['종료일자'])}"
    for t in tiers:
        add(t, "교육운영데이터", "박물관 체험/교육 프로그램", row["교육명"],
            row["대상"], row["교육내용"], tags=f"세부대상:{row['세부대상']}|기간:{period}")

# ── 2. 박물관 교육행사 데이터 (공연/이벤트 - 흥미유발용) ──
df = pd.read_excel(f"{UPLOAD}/샘플데이터_국립해양박물관_교육행사_운영_데이터.xlsx")
for _, row in df.iterrows():
    add("tier1", "교육행사데이터", "박물관 이벤트/공연", row["교육행사명"], row["대상"], row["내용"])

# ── 3. 만족도 설문 데이터 (15세 미만 응답자의 생생한 목소리 → 흥미유발 콘텐츠 기획 참고자료) ──
df = pd.read_excel(f"{UPLOAD}/샘플데이터_국립해양박물관_관람객_만족도_설문_데이터.xlsx")
kids = df[df["연령"] == "15세 미만"]
for _, row in kids.iterrows():
    voice = " / ".join(str(row[c]) for c in
                        ["박물관 관람 후 느낀점", "박물관에서 운영했으면 하는 교육체험 프로그램은?", "박물관에서 만나보고 싶은 전시는?"]
                        if pd.notna(row.get(c)) and str(row[c]) not in ("0", "nan"))
    if voice:
        add("tier1", "만족도설문(아동목소리)", "실제 어린이 관심사 원자료", "설문응답", "15세 미만", voice,
            tags="※콘텐츠 원문 아님, 흥미유발 소재 발굴용 참고자료")

# ── 4. 해양수산연수원 교육과정 데이터 ──
df = pd.read_excel(f"{UPLOAD}/샘플데이터_한국해양수산연수원_교육_과정_데이터.xlsx")
for _, row in df.iterrows():
    biz = str(row.get("비고", "")).replace("_x000D_", " ").strip()
    add("tier3", "연수원교육과정", "해기사/직무 자격과정", row["교육과목"], "성인(직업인)",
        biz or row["교육과목"], tags=f"과정코드:{row['번호']}")
    # 진로탐색용 라이트 버전 (과정명만, 10대 대상)
    add("tier2", "연수원교육과정(진로탐색용)", "해양 관련 자격/진로 소개", row["교육과목"], "13~19세",
        f"'{row['교육과목']}'은 해양수산업계에서 일하기 위해 필요한 전문 교육과정 중 하나입니다.",
        tags=f"과정코드:{row['번호']}")

# ── 5. 해양기관 현황 데이터 (취업처 DB) ──
df = pd.read_excel(f"{UPLOAD}/샘플데이터_해양기관_현황_데이터.xlsx")
by_cat = df.groupby("분류")["업체명"].apply(list)
for cat, companies in by_cat.items():
    add("tier3", "해양기관현황", "해양산업 취업처", cat, "성인(구직자)",
        f"{cat} 분야 주요 기관/업체: {', '.join(companies[:15])}" + (" 외" if len(companies) > 15 else ""))
    add("tier2", "해양기관현황(진로탐색용)", "해양산업 직업군 소개", cat, "13~19세",
        f"해양 관련 진로 중 '{cat}' 분야가 있습니다. 예: {', '.join(companies[:3])} 등")

# ── 6. NCS 능력단위 (parse_ncs.py 결과 사용) ──
with open(f"{OUT}/ncs_units.json", encoding="utf-8") as f:
    ncs_units = json.load(f)
for u in ncs_units:
    full_text = f"[정의] {u['definition']}\n\n"
    for el in u["elements"]:
        full_text += f"- {el['element'].splitlines()[-1]}: {el['criteria'][:300]}\n"
    full_text += f"\n{u['knowledge'][:500]}\n{u['skill'][:500]}\n{u['attitude'][:300]}"
    add("tier3", "NCS능력단위", "해양 직무 국가직무능력표준(NCS)", u["name"], "성인(직업인)",
        full_text, tags=f"NCS코드:{u['code']}")
    add("tier2", "NCS능력단위(진로탐색용)", "해양 관련 전문 직무 소개", u["name"], "13~19세",
        f"항해사/기관사가 실제로 배우는 기술 중 하나인 '{u['name']}': {u['definition']}")

# ── 7. 강의계획서.hwp (상세 커리큘럼 원문 - 목차 기준 청크) ──
with open("/tmp/lecture_plan.txt", encoding="utf-8") as f:
    text = f.read()
chapters = re.split(r"\n(?=\d{1,2}\.\s?[가-힣])", text)
for ch in chapters:
    ch = ch.strip()
    if len(ch) < 30:
        continue
    title = ch.splitlines()[0][:40]
    add("tier3", "강의계획서", "해기사 법정교육 상세 커리큘럼", title, "성인(교육생)", ch[:3000])

# ── 8. 교육안내책자.hwp (제도/시험 정보 원문 - 문단 청크) ──
with open("/tmp/guidebook.txt", encoding="utf-8") as f:
    text = f.read()
paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 80]
for i, p in enumerate(paragraphs):
    add("tier3", "교육안내책자", "2026 해기사교육/시험 제도 안내", f"안내책자_{i+1}", "성인(수험생)", p[:2000])


# ── 저장 ──
for tier, rows in records.items():
    out_df = pd.DataFrame(rows)
    path = f"{OUT}/{tier}_{'kids' if tier=='tier1' else 'teens' if tier=='tier2' else 'adults'}.csv"
    out_df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"{tier}: {len(out_df)}건 → {path}")
