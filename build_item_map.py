"""生成装备名→ID映射和符文名→图标映射，保存为JS可直接使用的JSON"""
import json

# Items
items = json.load(open(r'f:\code-tengxun\static\data\zh_CN\item.json', 'r', encoding='utf-8'))
item_map = {}
for iid, idata in items.get('data', {}).items():
    name = idata.get('name', '')
    if name:
        item_map[name] = iid

# Runes
runes = json.load(open(r'f:\code-tengxun\static\data\zh_CN\runesReforged.json', 'r', encoding='utf-8'))
rune_map = {}
rune_tree_icons = {}  # 符文树名 -> 图标
for tree in runes:
    tree_name = tree.get('name', '')
    tree_icon = tree.get('icon', '')
    if tree_name:
        rune_tree_icons[tree_name] = tree_icon
    for slot in tree.get('slots', []):
        for rune in slot.get('runes', []):
            name = rune.get('name', '')
            icon = rune.get('icon', '')
            if name:
                rune_map[name] = icon

result = {"items": item_map, "runes": rune_map, "rune_trees": rune_tree_icons}
with open(r'f:\code-tengxun\static\icon_maps.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Done: {len(item_map)} items, {len(rune_map)} runes, {len(rune_tree_icons)} rune trees")
