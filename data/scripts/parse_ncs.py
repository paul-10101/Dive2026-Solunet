"""
해양직무_NCS_데이터.xls 파서
원본은 표가 아니라 '폼(form)' 레이아웃 - 능력단위 32개가 세로로 이어붙여진 형태.
분류번호 / 능력단위명칭 / 정의 / 능력단위요소+수행준거 / 지식·기술·태도 를 구조화해서 추출.
"""

import pandas as pd
import json
import re


def parse_ncs(path: str) -> list[dict]:
    df = pd.read_excel(path, sheet_name=0, header=None, engine="xlrd")
    col0 = df[0].astype(str)

    # '분류번호 :' 로 시작하는 행 = 새 능력단위 블록의 시작
    start_idxs = df.index[col0.str.contains("분류번호", na=False)].tolist()
    start_idxs.append(len(df))  # 마지막 블록 끝 처리용

    units = []
    for i in range(len(start_idxs) - 1):
        s, e = start_idxs[i], start_idxs[i + 1]
        block = df.iloc[s:e]

        code = str(block.iloc[0, 3]).strip() if pd.notna(block.iloc[0, 3]) else None
        if not code or code == "nan":
            continue

        # 능력단위 명칭 (보통 다음 행의 4번째 컬럼)
        name_row = block[block[0].astype(str).str.contains("능력단위 명칭", na=False)]
        name = str(name_row.iloc[0, 3]).strip() if len(name_row) else ""

        def_row = block[block[0].astype(str).str.contains("능력단위 정의", na=False)]
        definition = str(def_row.iloc[0, 3]).strip() if len(def_row) else ""

        # 능력단위요소(컬럼0) + 수행준거(컬럼4) 쌍
        elements = []
        for _, row in block.iterrows():
            c0 = str(row[0]) if pd.notna(row[0]) else ""
            c4 = str(row[4]) if pd.notna(row[4]) else ""
            if re.match(r"^\d", c0) and "\n" in c0:
                elements.append({"element": c0.strip(), "criteria": c4.strip()})

        # 지식/기술/태도 블록 (컬럼4에 【지식】【기술】【태도】 형태로 존재)
        knowledge, skill, attitude = "", "", ""
        for _, row in block.iterrows():
            c4 = str(row[4]) if pd.notna(row[4]) else ""
            if c4.startswith("【지식】"):
                knowledge += c4 + "\n"
            elif c4.startswith("【기술】"):
                skill += c4 + "\n"
            elif c4.startswith("【태도】"):
                attitude += c4 + "\n"

        units.append({
            "code": code,
            "name": name,
            "definition": definition,
            "elements": elements,
            "knowledge": knowledge.strip(),
            "skill": skill.strip(),
            "attitude": attitude.strip(),
        })

    return units


if __name__ == "__main__":
    units = parse_ncs("/mnt/user-data/uploads/샘플데이터_해양직무_NCS_데이터.xls")
    print(f"파싱된 능력단위 수: {len(units)}")
    with open("/home/claude/didisam-kb/output/ncs_units.json", "w", encoding="utf-8") as f:
        json.dump(units, f, ensure_ascii=False, indent=2)
    for u in units[:3]:
        print(u["code"], "-", u["name"], f"({len(u['elements'])}개 요소)")
