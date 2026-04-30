import sys, json, time
sys.path.insert(0, r'f:\code-tengxun\LeagueAkari_CN')
from data_spider import DataSpider

spider = DataSpider()
hero_id = spider._get_hero_id('亚索')
url = f"https://lol.qq.com/act/lbp/common/guides/champDetail/champDetail_{hero_id}.js"
print(f"URL: {url}")

raw = spider._fetch_js_json(url)
if not raw:
    print("Failed to fetch")
else:
    fight_data = raw.get('list', {}).get('championFight', {})
    print(f"championFight has {len(fight_data)} records")
    for k, v in list(fight_data.items())[:2]:
        print(f"\n--- Record key={k} ---")
        if isinstance(v, dict):
            print(f"  keys: {list(v.keys())}")
            # 找包含 id 的字段
            for key in v.keys():
                if 'id' in key.lower() or 'champ' in key.lower():
                    print(f"  {key} = {v[key]}")
        elif isinstance(v, list) and v:
            print(f"  list[0] type: {type(v[0])}")
            if isinstance(v[0], dict):
                print(f"  list[0] keys: {list(v[0].keys())}")
