# 비공개 장부(dippers-world)에서 「지도」 화까지 연재된 장소만 골라 공개 지도 map/names.json에 넣는다.
# 공개 저장소의 로그는 누구나 보므로, 장소 이름은 출력하지 않고 개수만 출력한다.
import sys, json, re, yaml
ledger, positions, names, upto = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d = json.load(open(names, encoding="utf-8"))
keep = [n for n in d["names"] if n.get("src") != "ledger"]          # 나라 이름 등 손으로 넣은 것은 그대로
try:
    upto = int(float(upto))
except ValueError:
    upto = None
added = []
if upto:
    L = yaml.safe_load(open(ledger, encoding="utf-8"))
    P = {p["id"]: p for p in (yaml.safe_load(open(positions, encoding="utf-8")).get("places") or [])}
    for pl in L.get("places") or []:
        ep = pl.get("first_ep")
        if not isinstance(ep, int) or ep > upto or pl.get("status") != "원고" or pl["id"] not in P:
            continue
        name = re.sub(r"\s*\(.*$", "", str(pl["name"])).strip()      # 「(이름 미정)」 같은 괄호 설명은 뺀다
        tier = P[pl["id"]].get("importance") or "보통"      # 주요 · 보통 · 작은(점만)
        added.append({"name": name, "kind": tier, "x": P[pl["id"]]["x"], "y": P[pl["id"]]["y"], "ep": ep, "src": "ledger"})
d["names"] = keep + added
# 강 이름: 장부 rivers에 처음 나온 화(first_ep)가 있고 그 화가 공개 범위 안이면, positions의 강줄기와 함께 낸다
rivers = []
if upto:
    PR = {r["id"]: r for r in (yaml.safe_load(open(positions, encoding="utf-8")).get("rivers") or [])}
    for rv in L.get("rivers") or []:
        ep = rv.get("first_ep")
        if isinstance(ep, int) and ep <= upto and rv.get("id") in PR:
            rivers.append({"name": str(rv.get("name") or PR[rv["id"]]["name"]), "path": PR[rv["id"]]["path"]})
d["rivers"] = rivers
d["published_upto"] = upto
json.dump(d, open(names, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("공개 범위:", upto, "화까지 / 장부에서 넣은 장소", len(added), "곳 / 강 이름", len(rivers), "개")
