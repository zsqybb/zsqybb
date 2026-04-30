import sys
sys.path.insert(0, r'f:\code-tengxun\LeagueAkari_CN')

from data_spider import DataSpider
import json

spider = DataSpider()

# 模拟解析亚索的克制关系
# 先获取亚索的数据
data = spider.search_hero_data('亚索')
counter = data.get('counter', {})
strong = counter.get('strong_against', [])

print(f"=== 克制关系数量: {len(strong)} ===")
if strong:
    h = strong[0]
    print(f"hero_name: {h.get('hero_name')}")
    print(f"hero_id: {h.get('hero_id')}")
    print(f"alias: {h.get('alias')}")

    # 检查 HERO_BY_ID 的 key 格式
    enemy_id = h.get('hero_id')
    print(f"\nenemy_id type: {type(enemy_id)}, value: {enemy_id}")

    # 尝试不同格式查找
    info1 = spider.HERO_BY_ID.get(str(enemy_id), {})
    print(f"HERO_BY_ID.get(str): {info1.get('alias', 'EMPTY') if info1 else 'NOT FOUND'}")

    try:
        info2 = spider.HERO_BY_ID.get(int(enemy_id), {})
        print(f"HERO_BY_ID.get(int): {info2.get('alias', 'EMPTY') if info2 else 'NOT FOUND'}")
    except:
        pass

    # 检查 HERO_BY_ID 的前3个key
    print(f"\nHERO_BY_ID sample keys (first 3):")
    for k in list(spider.HERO_BY_ID.keys())[:3]:
        print(f"  key={k}, type={type(k)}")

    # 测试 _get_hero_name_by_id
    name = spider._get_hero_name_by_id(enemy_id)
    print(f"\n_get_hero_name_by_id result: {name}")

    # 测试 _get_hero_alias
    alias = spider._get_hero_alias(name) if name else 'NAME EMPTY'
    print(f"_get_hero_alias result: {alias}")
