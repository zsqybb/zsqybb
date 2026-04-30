import urllib.request
import json
import sys

def test():
    # 测试服务器状态
    try:
        req = urllib.request.urlopen('http://localhost:8800/api/status', timeout=5)
        data = json.loads(req.read())
        print(f"Status: {data}")
    except Exception as e:
        print(f"Server test failed: {e}")
        return False

    # 测试亚索数据 - 检查图标字段
    try:
        url = 'http://localhost:8800/api/hero/%E4%BA%9A%E7%B4%A2'
        req = urllib.request.urlopen(url, timeout=15)
        data = json.loads(req.read())

        print(f"\n=== Hero: {data.get('hero_name')} ===")

        # 检查符文图标
        runes = data.get('build', {}).get('runes', [])
        if runes:
            r = runes[0]
            print(f"Rune icons: {r.get('rune_icons', 'MISSING')}")
            print(f"Rune names: {r.get('runes', [])}")

        # 检查装备 item_ids
        core = data.get('build', {}).get('core_items', [])
        if core:
            c = core[0]
            print(f"Item IDs: {c.get('item_ids', 'MISSING')}")
            print(f"Item names: {c.get('names', [])}")

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
        return True
    except Exception as e:
        print(f"Hero API test failed: {e}")
        return False

if __name__ == '__main__':
    test()
