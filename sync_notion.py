import os
import urllib.request
import json
from datetime import datetime, timezone, timedelta

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
DATABASE_ID = "419ac4c8763c80f5851fc00a8e8f50eb"

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode("utf-8"))
    tasks = []
    for row in result.get("results", []):
        props = row["properties"]
        
        def get_text(prop_name):
            p = props.get(prop_name, {})
            t = p.get("type")
            if t == "title":
                return "".join([x["plain_text"] for x in p["title"]])
            elif t == "rich_text":
                return "".join([x["plain_text"] for x in p["rich_text"]])
            elif t == "select" and p["select"]:
                return p["select"]["name"]
            elif t == "status" and p["status"]:
                return p["status"]["name"]
            return ""

        tasks.append({
            "title": get_text("업무명"),
            "dept": get_text("담당 부서"),
            "ai": get_text("담당 AI"),
            "status": get_text("진행 상태"),
            "phase": get_text("단계(Phase)"),
            "bubble": get_text("말풍선 요약")
        })

    # 한국 시간(KST) 기준 갱신 시각 기록
    kst = timezone(timedelta(hours=9))
    output = {
        "updated_at": datetime.now(kst).strftime("%Y-%m-%d %H:%M KST"),
        "tasks": tasks
    }

    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"동기화 완료: {len(tasks)}건")
