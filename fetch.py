import requests, json, re, os
from datetime import datetime

def main():
    os.makedirs("data", exist_ok=True)
    today_iso = datetime.now().strftime("%Y-%m-%d")
    today_display = datetime.now().strftime("%d/%m/%Y")
    try:
        r = requests.get("https://www.keralalotteryresult.net/", headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        text = r.text
        m1 = re.search(r'(?:First Prize|1st Prize)[\s\S]{0,300}([A-Z]{2}\s*\d{6})', text, re.I)
        mcode = re.search(r'\b([A-Z]{2}-\d+)\b', text)
        if m1:
            first = m1.group(1).strip()
            code = mcode.group(1) if mcode else "BT-73"
            number_only = re.sub(r'[^0-9]','',first)[-6:]
            daily = {}
            if os.path.exists("data/daily.json"):
                daily = json.load(open("data/daily.json"))
            if "2026" not in daily:
                daily["2026"]=[]
            if not any(x["date"]==today_iso for x in daily["2026"]):
                daily["2026"].append({"date":today_iso,"date_display":today_display,"month":int(today_iso.split("-")[1]),"year":int(today_iso.split("-")[0]),"code":code,"first":first,"number_only":number_only})
                daily["2026"] = sorted(daily["2026"], key=lambda x:x["date"], reverse=True)
                open("data/daily.json",'w').write(json.dumps(daily, indent=2))
    except Exception as e:
        print(e)

if __name__=="__main__":
    main()
