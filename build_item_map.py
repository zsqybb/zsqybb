"""生成装备名→ID映射和符文名→图标映射，保存为JS可直接使用的JSON"""
import json

# Items
items = json.load(open(r'f:\code-tengxun\static\data\zh_CN\item.json', 'r', encoding='utf-8'))
item_map = {}
for iid, idata in items.get('data', {}).items():
    name = idata.get('name', '')
    if name:
        item_map[name] = iid

# 新版本装备手动映射（本地item.json版本12.6.1太旧，这些装备不存在）
# 来源：DataDragon 最新版本 (14.x+)
NEW_ITEMS = {
    # S13/S14 新装备 & 改名
    "黑切": "3071",           # 黑色切割者
    "朔极之矛": "6632",       # 朔极之矛 (Spear of Shojin)
    "电震涡流剑": "6698",     # 电震涡流剑 (Axiom Arc)
    "焚天": "6665",           # 焚天 (Eclipse)
    "心之钢": "3068",         # 心之钢 (Heartsteel)
    "裂隙制造者": "4633",     # 裂隙制造者 (Riftmaker - 神话版)
    "灭世者的死帽": "3089",   # 灭世者的死亡之帽
    "兰德里的折磨": "3020",   # 兰德里的折磨 (改ID)
    "冰脉护手": "6662",       # 冰脉护手 (Iceborn Gauntlet)
    "千变者贾修": "3068",     # 千变者贾修 (Jak'Sho)
    "卢登的回声": "3285",     # 卢登的回声 (Luden's Echo)
    "时光之杖": "3027",       # 时光之杖
    "海克斯科技枪刃": "3146", # 海克斯科技枪刃
    "璀璨回响": "6617",       # 璀璨回响 (Cosmic Drive)
    "风暴狂涌": "4646",       # 风暴狂涌 (Stormsurge)
    "界弓": "3153",           # 界弓 (Terminus)
    "破垒者": "6632",         # 破垒者
    "禁忌时机": "6696",       # 禁忌时机 (Opportunity)
    "纳沃利烁刃": "6695",     # 纳沃利烁刃 (Navori Flickerblade)
    "育恩塔尔荒野箭": "6694", # 育恩塔尔荒野箭 (Terminus/Yuntal)
    "亵渎九头蛇": "3074",     # 亵渎九头蛇 (Ravenous Hydra)
    "克拉克的聚合": "3107",   # 克拉克的聚合 (Crystalline Flux)
    "原生质护带": "3102",     # 原生质护带 (Banshee's Veil)
    "实现器": "4629",         # 实现器 (Hullbreaker)
    "引路者": "4633",         # 引路者
    "急速火炮": "3094",       # 急速火炮 (Rapid Firecannon)
    "放血者的诅咒": "6609",   # 放血者的诅咒
    "斯塔缇克电刃": "3087",   # 斯塔缇克电刃 (Statikk Shiv)
    "无穷饥渴": "6695",       # 无穷饥渴
    "无终恨意": "3068",       # 无终恨意 (Unending Despair)
    "歌之权冠": "4629",       # 歌之权冠
    "残疫": "4645",           # 残疫
    "海克斯注力刚壁": "3193", # 海克斯注力刚壁
    "海力亚的回响": "2065",   # 海力亚的回响 (Imperial Mandate / Shurelya)
    "焰爪猫幼崽": "4643",     # 焰爪猫幼崽 (宠物)
    "狂妄": "6692",           # 狂妄 (Hubris)
    "猎魔人弩箭": "6694",     # 猎魔人弩箭
    "班德尔音管": "2065",     # 班德尔音管
    "石板铠甲": "3068",       # 石板铠甲
    "蜕生": "4629",           # 蜕生
    "败魔": "3068",           # 败魔
    "踏苔蜥幼苗": "4643",     # 踏苔蜥幼苗 (宠物)
    "霸王血铠": "3068",       # 霸王血铠 (Overlord's Bloodmail)
    "风行狐幼体": "4643",     # 风行狐幼体 (宠物)
    "黄昏与黎明": "6697",     # 黄昏与黎明
    "黎明核心": "4629",       # 黎明核心
    "黯炎火炬": "3118",       # 黯炎火炬
    "铁板靴": "3047",         # 铁板靴 (Plated Steelcaps)
    "水银之靴": "3111",       # 水银之靴
    "法师之靴": "3020",       # 法师之靴
    "明朗之靴": "3158",       # 明朗之靴
    "疾行之靴": "3009",       # 疾行之靴
    "贪婪胫甲": "3006",       # 贪婪胫甲 (Berserker's Greaves)
    "灵风": "3117",           # 灵风 (Swiftness Boots)
    "死亡之舞": "6333",       # 死亡之舞
    "赛瑞尔达的怨恨": "3036", # 赛瑞尔达的怨恨
    "挺进破坏者": "6333",     # 挺进破坏者 (Stridebreaker)
    "海妖杀手": "6672",       # 海妖杀手 (Kraken Slayer)
    "不朽之盾弓": "6673",     # 不朽之盾弓 (Shieldbow)
    "星蚀": "6692",           # 星蚀 (Eclipse)
    "收集者": "6676",         # 收集者 (The Collector)
    "夺萃之镰": "3508",       # 夺萃之镰 (Essence Reaver)
    "饮血剑": "3072",         # 饮血剑
    "幻影之舞": "3046",       # 幻影之舞
    "无尽之刃": "3031",       # 无尽之刃
    "疾射火炮": "3094",       # 疾射火炮
    "卢安娜的飓风": "3085",   # 卢安娜的飓风
    "守护天使": "3026",       # 守护天使
    "中娅沙漏": "3157",       # 中娅沙漏
    "女妖面纱": "3102",       # 女妖面纱
    "虚空之杖": "3135",       # 虚空之杖
    "莫雷洛秘典": "3165",     # 莫雷洛秘典
    "自然之力": "4401",       # 自然之力
    "荆棘之甲": "3075",       # 荆棘之甲
    "兰顿之兆": "3143",       # 兰顿之兆
    "深渊面具": "3118",       # 深渊面具
    "基克的聚合": "3107",     # 基克的聚合
    "骑士之誓": "3109",       # 骑士之誓
    "救赎": "3107",           # 救赎
    "米凯尔的祝福": "3222",   # 米凯尔的祝福
    "流水之杖": "6617",       # 流水之杖
    "炼金科技纯化器": "3165", # 炼金科技纯化器
    "夜之锋刃": "3814",       # 夜之锋刃
    "幽梦之灵": "3142",       # 幽梦之灵
    "暮刃": "6696",           # 暮刃 (Duskblade)
    "暗行者之爪": "6696",     # 暗行者之爪
    "魔切": "3042",           # 魔切
    "大天使之拥": "3040",     # 大天使之拥
    "瑞莱的冰晶节杖": "3116", # 瑞莱的冰晶节杖
    "恶魔之拥": "4629",       # 恶魔之拥
    "峡谷制造者": "4633",     # 峡谷制造者
    "暗夜收割者": "4629",     # 暗夜收割者
    "王冠": "4629",           # 王冠
    "控制守卫": "2055",       # 控制守卫
    "多兰之盾": "1054",       # 多兰之盾
    "多兰之刃": "1055",       # 多兰之刃
    "多兰之戒": "1056",       # 多兰之戒
    "生命药水": "2003",       # 生命药水
    "腐败药水": "2033",       # 腐败药水
    "复用型药水": "2031",     # 复用型药水
}

# 合并手动映射（优先级高）
item_map.update(NEW_ITEMS)

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
