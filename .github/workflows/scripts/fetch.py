import requests, json, re, os
from datetime import datetime, timedelta, timezone

DATA_DIR = "data"
INDEX_FILE = "index.html"

def get_ist():
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def fetch_latest():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get("https://www.keralalotteriesresults.in/2016/12/kerala-lottery-result-today.html", headers=headers, timeout=20)
        rows = re.findall(r"\|\s*\*\*(\d{2}-\d{2}-\d{4})\*\*\s*\|\s*\*\*(.+?)\*\*\s*\|\s*\*\*(.+?)\*\*\s*\|", r.text)
        for d, name, code in rows[:8]:
            try:
                dt = datetime.strptime(d, "%d-%m-%Y")
                results.append({"date": dt.strftime("%Y-%m-%d"), "date_display": dt.strftime("%d/%m/%Y"), "month": dt.month, "year": dt.year, "code": code.strip(), "name": name.strip()})
            except:
                pass
    except Exception as e:
        print(e)
    try:
        r = requests.get("https://www.keralalotteryresult.net/", headers=headers, timeout=15)
        m = re.search(r"First Prize.*?([A-Z]{1,2}\s*\d{6})", r.text, re.I | re.S)
        if m and results:
            first = re.sub(r"\s+", " ", m.group(1).strip())
            num = re.sub(r"[^0-9]", "", first)[-6:]
            today = get_ist().strftime("%Y-%m-%d")
            for res in results:
                if res["date"] == today:
                    res["first"] = first
                    res["number_only"] = num
    except:
        pass
    return results

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    latest = fetch_latest()
    if not latest:
        return
    path = os.path.join(DATA_DIR, "daily.json")
    daily = {}
    if os.path.exists(path):
        try:
            daily = json.load(open(path, encoding='utf-8'))
        except:
            daily = {}
    if "2026" not in daily:
        daily["2026"] = []
    for e in latest:
        if "first" not in e:
            continue
        ex = next((x for x in daily["2026"] if x["date"] == e["date"]), None)
        if ex:
            ex.update(e)
        else:
            daily["2026"].append(e)
    daily["2026"] = sorted(daily["2026"], key=lambda x: x["date"], reverse=True)[:100]
    json.dump(daily, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    # update index.html
    if os.path.exists(INDEX_FILE) and daily["2026"]:
        try:
            html = open(INDEX_FILE, "r", encoding="utf-8").read()
            top = daily["2026"][:6]
            entries = ",\n    ".join([f'{{date:"{e["date"]}", date_display:"{e["date_display"]}", month:{e["month"]}, year:{e["year"]}, code:"{e["code"]}", first:"{e.get("first","")}", number_only:"{e.get("number_only","")}"}}' for e in top])
            block = f'// AUTO {get_ist().strftime("%d/%m/%Y")}\n(function(){{const entries=[{entries}]; if(!DATA["2026"]) DATA["2026"]=[]; DATA["2026"]=DATA["2026"].filter(x=>!{json.dumps([e["date"] for e in top])}.includes(x.date)); DATA["2026"]=[...entries,...DATA["2026"]]; DATA["2026"].sort((a,b)=> new Date(b.date)-new Date(a.date)); setTimeout(()=>{{if(typeof renderRecent==="function") renderRecent()}},200);}})();'
            if "// AUTO" in html:
                html = re.sub(r"// AUTO.*?\)\(\);", block, html, flags=re.S)
            else:
                html = html.replace("function renderRecent(){", block+"\n\nfunction renderRecent(){")
            open(INDEX_FILE, "w", encoding="utf-8").write(html)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
