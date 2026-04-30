import sys
sys.path.insert(0, r'f:\code-tengxun\LeagueAkari_CN')

from data_spider import DataSpider
import json, os

spider = DataSpider()

# 直接获取腾讯攻略中心原始数据
hero_id = spider._get_hero_id('亚索')
alias = spider._get_hero_alias('亚索')
print(f"亚索 hero_id={hero_id}, alias={alias}")

# 获取原始数据
raw = spider._fetch_js_json(spider.CHAMP_DETAIL_URL.format(hero_id))
if raw:
    list_data = raw.get('list', {})
    fight_data = list_data.get('championFight', {})
    print(f"\n=== championFight 有 {len(fight_data)} 条记录 ===")
    for k, v in list(fight_data.items())[:2]:
        print(f"Key={k}")
        print(f"  keys={list(v.keys())}")
        print(f"  sample={json.dumps(v, ensure_ascii=False)[:200]}")
else:
    print("Failed to fetch champDetail")
