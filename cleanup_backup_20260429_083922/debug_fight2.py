import sys
sys.path.insert(0, r'f:\code-tengxun\LeagueAkari_CN')

from data_spider import DataSpider
import json

spider = DataSpider()

hero_id = spider._get_hero_id('亚索')
url = f"https://lol.qq.com/act/lbp/common/guides/champDetail/champDetail_{hero_id}.js"
print(f"Fetching: {url}")

raw = spider._fetch_js_json(url)
if raw:
    fight_data = raw.get('list', {}).get('championFight', {})
    print(f"championFight has {len(fight_data)} records")
    # 打印第一条记录的所有字段
    for k, v in list(fight_data.items())[:1]:
        print(f"\nFirst record key={k}")
        print(f"  fields: {list(v.keys())}")
        print(f"  sample: {json.dumps(v, ensure_ascii=False)[:300]}")
        # 检查 enemy_id 字段
        print(f"\n  Possible enemy ID fields:")
        for f in ['championid2', 'championId2', 'enemy_id', 'target_id', 'id']:
            if f in v:
                print(f"    {f} = {v[f]}")
else:
    print("Failed to fetch")
