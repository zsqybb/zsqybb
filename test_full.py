import urllib.request
import json
import time

# 等待服务器初始化
time.sleep(3)

# 测试亚索（访问腾讯API，需要较长时间）
try:
    print("正在获取亚索数据（可能需要10-20秒）...")
    req = urllib.request.urlopen('http://localhost:8800/api/hero/%E4%BA%9A%E7%B4%A2', timeout=30)
    data = json.loads(req.read())
    
    print(f"\n=== Hero: {data.get('hero_name')} ===")
    
    # 检查符文图标
    runes = data.get('build', {}).get('runes', [])
    if runes:
        r = runes[0]
        print(f"Rune names: {r.get('runes', [])}")
        print(f"Rune icons: {r.get('rune_icons', 'MISSING')}")
    else:
        print("No runes data!")
    
    # 检查装备 item_ids
    core = data.get('build', {}).get('core_items', [])
    if core:
        c = core[0]
        print(f"Item IDs: {c.get('item_ids', 'MISSING')}")
        print(f"Item names: {c.get('names', [])}")
    else:
        print("No core items data!")
    
    # 检查技能图标
    spells = data.get('spells', [])
    if spells:
        s = spells[0]
        print(f"Spell icon: {s.get('icon', 'MISSING')}")
        print(f"Spell name: {s.get('name', '')}")
    
    # 检查克制关系 alias
    strong = data.get('counter', {}).get('strong_against', [])
    if strong:
        h = strong[0]
        print(f"Counter alias: {h.get('alias', 'MISSING')}")
        print(f"Counter hero: {h.get('hero_name', '')}")
    
    print("\nAll icon fields check completed!")
    
except Exception as e:
    print(f"Test failed: {e}")
