import sys
sys.path.insert(0, r'f:\code-tengxun\LeagueAkari_CN')

from data_spider import DataSpider

spider = DataSpider()

# 测试 _get_hero_alias 方法
test_names = ['纳尔', '亚索', '盖伦']
for name in test_names:
    alias = spider._get_hero_alias(name)
    print(f"{name} -> alias: {alias}")

# 测试 HERO_BY_ID 中的 alias 字段
print("\n=== HERO_BY_ID sample ===")
for hid, info in list(spider.HERO_BY_ID.items())[:3]:
    print(f"ID={hid}, name_cn={info.get('name_cn')}, alias={info.get('alias')}")

# 测试 纳尔 的 hero_id 和 alias
print("\n=== 纳尔 info ===")
naer_id = spider._get_hero_id('纳尔')
print(f"纳尔 hero_id: {naer_id}")
if naer_id:
    info = spider.HERO_BY_ID.get(naer_id, {})
    print(f"纳尔 info: {info}")
