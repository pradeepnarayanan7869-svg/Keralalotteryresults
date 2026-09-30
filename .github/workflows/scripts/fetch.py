import requests, json, re, os
from datetime import datetime, timedelta, timezone
os.makedirs("data", exist_ok=True)
ist = timezone(timedelta(hours=5, minutes=30))
headers = {"User-Agent": "Mozilla/5.0"}
try:
    r = requests.get("https://www.keralalotteriesresults.in/2016/12/kerala-lottery-result-today.html", headers=headers, timeout=20)
    rows = re.findall(r"\|\s*\*\*(\d{2}-\d{2}-\d{4})\*\*\s*\|\s*\*\*(.+?)\*\*\s*\|\s*\*\*(.+?)\*\*\s*\|", r.text)
    daily = {"2026":[]}
    if os.path.exists("data/daily.json"):
        try:
            daily = json.load(open("data/daily.json", encoding="utf-8"))
        except:
            pass
    if "2026" not in daily:
        daily["2026"] = []
    for d, name, code in rows[:5]:
        try:
            dt = datetime.strptime(d, "%d-%m-%Y")
            iso = dt.strftime("%Y-%m-%d")
            if any(x["date"]==iso for x in daily["2026"]):
                continue
            # try first prize
            first = ""
            num = ""
            try:
                r2 = requests.get("https://www.keralalotteryresult.net/", headers=headers, timeout=10)
                m = re.search(r"First Prize.*?([A-Z]{1,2}\s*\d{6})", r2.text, re.I | re.S)
                if m:
                    first = m.group(1).strip()
                    num = re.sub(r"[^0-9]","",first)[-6:]
            except:
                pass
            daily["2026"].append({"date":iso,"date_display":dt.strftime("%d/%m/%Y"),"month":dt.month,"year":dt.year,"code":code.strip(),"first":first,"number_only":num})
        except:
            pass
    daily["2026"] = sorted(daily["2026"], key=lambda x:x["date"], reverse=True)[:50]
    json.dump(daily, open("data/daily.json","w",encoding="utf-8"), indent=2)
    # update index.html
    if os.path.exists("index.html") and daily["2026"]:
        html = open("index.html","r",encoding="utf-8").read()
        top = daily["2026"][:6]
        entries = ",\n    ".join([f'{{date:"{e["date"]}", date_display:"{e["date_display"]}", month:{e["month"]}, year:{e["year"]}, code:"{e["code"]}", first:"{e.get("first","")}", number_only:"{e.get("number_only","")}"}}' for e in top])
        block = f'// AUTO {datetime.now(ist).strftime("%d/%m/%Y")}\n(function(){{const entries=[{entries}]; if(!DATA["2026"]) DATA["2026"]=[]; DATA["2026"]=DATA["2026"].filter(x=>!{json.dumps([e["date"] for e in top])}.includes(x.date)); DATA["2026"]=[...entries,...DATA["2026"]]; DATA["2026"].sort((a,b)=> new Date(b.date)-new Date(a.date)); setTimeout(()=>{{if(typeof renderRecent==="function") renderRecent()}},200);}})();'
        if "// AUTO" in html:
            html = re.sub(r"// AUTO.*?\)\(\);", block, html, flags=re.S)
        else:
            html = html.replace("function renderRecent(){", block+"\n\nfunction renderRecent(){")
        open("index.html","w",encoding="utf-8").write(html)
        print("index.html updated")
    print("Done daily.json")
except Exception as e:
    print(e)
