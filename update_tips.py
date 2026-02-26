from datetime import datetime
import json

tips = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "free": [
        {"match": "Arsenal vs Chelsea", "tip": "Over 1.5 Goals"},
        {"match": "Inter vs Milan", "tip": "BTTS"},
        {"match": "PSG vs Lyon", "tip": "Home Win"}
    ],
    "vip": [
        {"match": "Man City vs Liverpool", "tip": "2-1"},
        {"match": "Barcelona vs Sevilla", "tip": "3-0"}
    ]
}

with open("tips.json", "w") as f:
    json.dump(tips, f)
