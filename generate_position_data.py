"""
生成分路专属装备/符文/技能加点数据
- 从OP.GG API获取分路统计
- 为每个分路生成装备/符文/技能加点（从OP.GG抓取或基于英雄类型推断）
- 生成1-18级技能加点序列
- 更新champion_builds.json
"""
import json
import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BUILD_FILE = os.path.join(os.path.dirname(__file__), 'static', 'champion_builds.json')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'static', 'data', 'zh_CN', 'champion')
OPGG_RANKED_API = "https://lol-api-champion.op.gg/api/KR/champions/ranked"

# ==================== 技能加点序列生成 ====================

def generate_skill_sequence(priority_str):
    """
    从 "R>Q>W>E" 格式生成1-18级加点序列
    返回: ["Q", "W", "E", "Q", "Q", "R", "Q", "W", "Q", "W", "R", "W", "W", "E", "E", "R", "E", "E"]
    """
    if not priority_str or '>' not in priority_str:
        # 默认加点：R>Q>W>E
        priority_str = "R>Q>W>E"
    
    parts = [p.strip().upper() for p in priority_str.split('>')]
    if len(parts) < 4:
        parts = ['R', 'Q', 'W', 'E']
    
    # 确保R在第一位
    if 'R' not in parts:
        parts.insert(0, 'R')
    elif parts[0] != 'R':
        parts.remove('R')
        parts.insert(0, 'R')
    
    # 确保有Q, W, E
    for skill in ['Q', 'W', 'E']:
        if skill not in parts:
            parts.append(skill)
    
    # 技能优先级（排除R）：决定加满顺序
    skill_order = [p for p in parts if p != 'R']  # e.g., ['Q', 'W', 'E']
    
    # R的等级：6, 11, 16
    r_levels = {6, 11, 16}
    
    # 每个技能最多5点
    skill_points = {s: 0 for s in ['Q', 'W', 'E', 'R']}
    max_points = {'Q': 5, 'W': 5, 'E': 5, 'R': 3}
    
    sequence = []
    current_priority_idx = 0  # 当前正在加满的技能索引
    
    for level in range(1, 19):
        if level in r_levels:
            sequence.append('R')
            skill_points['R'] += 1
        else:
            # 按优先级加点
            placed = False
            for skill in skill_order:
                if skill_points[skill] < max_points[skill]:
                    sequence.append(skill)
                    skill_points[skill] += 1
                    placed = True
                    break
            if not placed:
                # 不应该发生，但以防万一
                sequence.append(skill_order[0])
    
    return sequence


# ==================== 分路专属数据生成 ====================

# 分路常见的装备偏好
POSITION_ITEMS = {
    'TOP': {
        'starts': ['多兰剑', '生命药水'],
        'boots': ['铁板靴', '明朗之靴'],
        'core_tank': ['日炎圣盾', '荆棘之甲', '自然之力'],
        'core_fighter': ['挺进破坏者', '黑色切割者', '死亡之舞'],
        'core_mage': ['峡谷制造者', '瑞莱的冰晶节杖', '兰德里的折磨'],
    },
    'JUNGLE': {
        'starts': ['冰雹刀刃', '复用型药水'],
        'boots': ['铁板靴', '明朗之靴'],
        'core_tank': ['日炎圣盾', '荆棘之甲', '自然之力'],
        'core_fighter': ['挺进破坏者', '黑色切割者', '死亡之舞'],
        'core_mage': ['暗夜收割者', '灭世者的死亡之帽', '虚空之杖'],
        'core_assassin': ['暗行者之爪', '赛瑞尔达的怨恨', '夜之锋刃'],
    },
    'MID': {
        'starts': ['多兰戒', '生命药水'],
        'boots': ['法师之靴', '明朗之靴'],
        'core_mage': ['卢登的伙伴', '影焰', '灭世者的死亡之帽'],
        'core_assassin': ['暗行者之爪', '赛瑞尔达的怨恨', '夜之锋刃'],
        'core_fighter': ['挺进破坏者', '黑色切割者', '死亡之舞'],
    },
    'ADC': {
        'starts': ['多兰剑', '生命药水'],
        'boots': ['狂战士胫甲', '铁板靴'],
        'core': ['海妖杀手', '幻影之舞', '无尽之刃'],
    },
    'SUPPORT': {
        'starts': ['生命药水', '生命药水', '控制守卫'],
        'boots': ['明朗之靴', '灵巧之靴'],
        'core_enchanter': ['月石再生器', '流水法杖', '救赎'],
        'core_tank': ['帝国指令', '骑士之誓', '基克的聚合'],
    },
}

# 分路常见符文
POSITION_RUNES = {
    'TOP': {
        'fighter': {
            'primary': '精密', 'primary_runes': ['征服者', '凯旋', '传说：欢欣', '坚毅不倒'],
            'secondary': '坚决', 'secondary_runes': ['骸骨镀层', '复苏'],
            'shards': ['自适应', '护甲', '生命值']
        },
        'tank': {
            'primary': '坚决', 'primary_runes': ['不灭之握', '爆破', '调节', '过度生长'],
            'secondary': '精密', 'secondary_runes': ['传说：欢欣', '坚毅不倒'],
            'shards': ['自适应', '护甲', '生命值']
        },
        'mage': {
            'primary': '巫术', 'primary_runes': ['相位猛冲', '灵光披风', '超然', '风暴聚集'],
            'secondary': '坚决', 'secondary_runes': ['骸骨镀层', '复苏'],
            'shards': ['自适应', '自适应', '护甲']
        },
    },
    'JUNGLE': {
        'fighter': {
            'primary': '精密', 'primary_runes': ['征服者', '凯旋', '传说：欢欣', '坚毅不倒'],
            'secondary': '坚决', 'secondary_runes': ['调节', '过度生长'],
            'shards': ['自适应', '护甲', '生命值']
        },
        'assassin': {
            'primary': '主宰', 'primary_runes': ['电刑', '猛然冲击', '眼球收集器', '贪欲猎手'],
            'secondary': '精密', 'secondary_runes': ['凯旋', '传说：欢欣'],
            'shards': ['自适应', '自适应', '护甲']
        },
        'tank': {
            'primary': '坚决', 'primary_runes': ['余震', '生命源泉', '调节', '过度生长'],
            'secondary': '巫术', 'secondary_runes': ['水上行走', '超然'],
            'shards': ['自适应', '护甲', '生命值']
        },
        'mage': {
            'primary': '黑暗收割', 'primary_runes': ['黑暗收割', '猛然冲击', '眼球收集器', '贪欲猎手'],
            'secondary': '巫术', 'secondary_runes': ['水上行走', '超然'],
            'shards': ['自适应', '自适应', '护甲']
        },
    },
    'MID': {
        'mage': {
            'primary': '巫术', 'primary_runes': ['电刑', '灵光披风', '超然', '风暴聚集'],
            'secondary': '主宰', 'secondary_runes': ['贪欲猎手', '血之滋味'],
            'shards': ['自适应', '自适应', '护甲']
        },
        'assassin': {
            'primary': '主宰', 'primary_runes': ['电刑', '猛然冲击', '眼球收集器', '贪欲猎手'],
            'secondary': '精密', 'secondary_runes': ['凯旋', '传说：欢欣'],
            'shards': ['自适应', '自适应', '魔抗']
        },
        'fighter': {
            'primary': '精密', 'primary_runes': ['征服者', '凯旋', '传说：欢欣', '坚毅不倒'],
            'secondary': '坚决', 'secondary_runes': ['骸骨镀层', '复苏'],
            'shards': ['自适应', '自适应', '魔抗']
        },
    },
    'ADC': {
        'default': {
            'primary': '精密', 'primary_runes': ['致命节奏', '凯旋', '传说：血统', '砍倒'],
            'secondary': '坚决', 'secondary_runes': ['骸骨镀层', '复苏'],
            'shards': ['自适应', '自适应', '护甲']
        },
    },
    'SUPPORT': {
        'enchanter': {
            'primary': '巫术', 'primary_runes': ['召唤艾黎', '法力流系带', '超然', '焦灼'],
            'secondary': '坚决', 'secondary_runes': ['骸骨镀层', '复苏'],
            'shards': ['自适应', '护甲', '生命值']
        },
        'tank': {
            'primary': '坚决', 'primary_runes': ['余震', '生命源泉', '骸骨镀层', '过度生长'],
            'secondary': '启迪', 'secondary_runes': ['六神装', '星界洞悉'],
            'shards': ['自适应', '护甲', '生命值']
        },
    },
}

# 分路技能加点优先级
POSITION_SKILLS = {
    'TOP': 'R>Q>W>E',
    'JUNGLE': 'R>Q>E>W',
    'MID': 'R>Q>W>E',
    'ADC': 'R>Q>W>E',
    'SUPPORT': 'R>Q>W>E',
}

# 英雄分类到角色类型的映射
CHAMPION_CLASS_MAP = {
    'Fighter': 'fighter',
    'Tank': 'tank',
    'Mage': 'mage',
    'Assassin': 'assassin',
    'Marksman': 'marksman',
    'Support': 'enchanter',
}


def get_champion_tags():
    """加载英雄标签（Fighter, Tank, Mage等）"""
    import glob
    tags = {}
    if not os.path.exists(DATA_DIR):
        return tags
    for filepath in glob.glob(os.path.join(DATA_DIR, '*.json')):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for champ_id, champ in data.get('data', {}).items():
                tags[champ_id] = champ.get('tags', [])
        except Exception:
            pass
    return tags


def get_primary_role(champ_tags):
    """从英雄标签推断主要角色类型"""
    if not champ_tags:
        return 'fighter'
    for tag in champ_tags:
        if tag in CHAMPION_CLASS_MAP:
            return CHAMPION_CLASS_MAP[tag]
    return 'fighter'


def generate_position_builds(position_name, champ_tags, existing_builds, existing_runes, existing_skills):
    """
    为指定分路生成装备/符文/技能数据
    优先使用已有数据，没有则根据英雄类型和分路推断
    """
    role = get_primary_role(champ_tags)
    
    # 技能加点：不同分路可能有不同加点
    # 大部分英雄各分路加点相同，但部分英雄不同
    pos_skills = existing_skills or POSITION_SKILLS.get(position_name, 'R>Q>W>E')
    
    # 装备：优先使用已有数据
    if existing_builds and isinstance(existing_builds, dict) and existing_builds.get('core'):
        builds = existing_builds
    else:
        # 根据分路和角色类型推断
        pos_items = POSITION_ITEMS.get(position_name, POSITION_ITEMS['TOP'])
        if position_name == 'ADC':
            builds = {
                'starts': pos_items.get('starts', ['多兰剑', '生命药水']),
                'boots': pos_items.get('boots', ['狂战士胫甲']),
                'core': pos_items.get('core', ['海妖杀手', '幻影之舞', '无尽之刃']),
            }
        elif position_name == 'SUPPORT':
            builds = {
                'starts': pos_items.get('starts', ['生命药水', '控制守卫']),
                'boots': pos_items.get('boots', ['明朗之靴']),
                'core': pos_items.get(f'core_{role}', pos_items.get('core_enchanter', ['月石再生器', '流水法杖', '救赎'])),
            }
        elif position_name == 'JUNGLE':
            core_key = f'core_{role}' if f'core_{role}' in pos_items else 'core_fighter'
            builds = {
                'starts': pos_items.get('starts', ['冰雹刀刃', '复用型药水']),
                'boots': pos_items.get('boots', ['铁板靴']),
                'core': pos_items.get(core_key, ['挺进破坏者', '黑色切割者', '死亡之舞']),
            }
        else:
            core_key = f'core_{role}' if f'core_{role}' in pos_items else 'core_fighter'
            builds = {
                'starts': pos_items.get('starts', ['多兰剑', '生命药水']),
                'boots': pos_items.get('boots', ['铁板靴']),
                'core': pos_items.get(core_key, ['挺进破坏者', '黑色切割者', '死亡之舞']),
            }
    
    # 符文：优先使用已有数据
    if existing_runes and isinstance(existing_runes, dict) and existing_runes.get('primary'):
        runes = existing_runes
    else:
        pos_runes = POSITION_RUNES.get(position_name, POSITION_RUNES['TOP'])
        rune_key = role if role in pos_runes else 'default' if 'default' in pos_runes else list(pos_runes.keys())[0]
        rune_data = pos_runes.get(rune_key, pos_runes[list(pos_runes.keys())[0]])
        runes = {
            'primary': rune_data['primary'],
            'primary_runes': rune_data['primary_runes'],
            'secondary': rune_data['secondary'],
            'secondary_runes': rune_data['secondary_runes'],
            'shards': rune_data['shards'],
        }
    
    return builds, runes, pos_skills


def fetch_opgg_ranked():
    """从OP.GG获取排行数据（含分路统计）"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    try:
        resp = requests.get(OPGG_RANKED_API, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        champions = data.get('data', [])
        logger.info(f"Fetched {len(champions)} champions from OP.GG ranked API")
        return champions
    except Exception as e:
        logger.error(f"Failed to fetch OP.GG data: {e}")
        return []


def parse_opgg_positions(champ_data):
    """解析OP.GG英雄的分路信息"""
    positions = []
    for pos in champ_data.get('positions', []):
        pos_name = pos.get('name', '')
        pos_stats = pos.get('stats') or {}
        positions.append({
            'name': pos_name,
            'win_rate': round(pos_stats.get('win_rate', 0) * 100, 2),
            'pick_rate': round(pos_stats.get('pick_rate', 0) * 100, 2),
            'ban_rate': round(pos_stats.get('ban_rate', 0) * 100, 2),
            'role_rate': round(pos_stats.get('role_rate', 0) * 100, 2),
            'kda': round(pos_stats.get('kda', 0), 2),
            'tier': pos_stats.get('tier_data', {}).get('tier', 0) if pos_stats.get('tier_data') else 0,
        })
    return positions


def main():
    logger.info("=" * 60)
    logger.info("生成英雄分路数据 & 技能加点序列")
    logger.info("=" * 60)
    
    # 1. 加载现有数据
    if os.path.exists(BUILD_FILE):
        with open(BUILD_FILE, 'r', encoding='utf-8') as f:
            builds = json.load(f)
        logger.info(f"Loaded {len(builds)} champions from champion_builds.json")
    else:
        builds = {}
    
    # 2. 加载英雄标签
    champ_tags = get_champion_tags()
    logger.info(f"Loaded tags for {len(champ_tags)} champions")
    
    # 3. 从OP.GG获取分路数据
    opgg_data = fetch_opgg_ranked()
    
    # 建立OP.GG数据的ID映射
    import glob
    key_map = {}
    for filepath in glob.glob(os.path.join(DATA_DIR, '*.json')):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for champ_id, champ in data.get('data', {}).items():
                key = int(champ.get('key', 0))
                key_map[key] = champ_id
        except Exception:
            pass
    
    opgg_by_key = {}
    for champ in opgg_data:
        opgg_by_key[champ.get('id', 0)] = champ
    
    # 4. 更新每个英雄的数据
    updated = 0
    for champ_id, data in builds.items():
        tags = champ_tags.get(champ_id, [])
        
        # 4.1 生成技能加点序列
        skills_str = data.get('skills', 'R>Q>W>E')
        if skills_str:
            skill_sequence = generate_skill_sequence(skills_str)
            data['skill_sequence'] = skill_sequence
        
        # 4.2 更新分路数据
        # 先从OP.GG获取分路统计
        # 找到该英雄的OP.GG key
        champ_key = None
        for k, v in key_map.items():
            if v == champ_id:
                champ_key = k
                break
        
        opgg_positions = []
        if champ_key and champ_key in opgg_by_key:
            opgg_positions = parse_opgg_positions(opgg_by_key[champ_key])
        
        existing_positions = data.get('positions', [])
        
        # 4.3 为每个分路添加装备/符文/技能
        new_positions = []
        for pos in (opgg_positions if opgg_positions else existing_positions):
            pos_name = pos.get('name', '')
            if not pos_name:
                continue
            
            # 检查是否已有分路专属builds/runes
            pos_builds = pos.get('builds')
            pos_runes = pos.get('runes')
            pos_skills = pos.get('skills')
            
            # 如果没有分路专属数据，根据英雄类型生成
            if not pos_builds or not pos_runes:
                gen_builds, gen_runes, gen_skills = generate_position_builds(
                    pos_name, tags,
                    data.get('builds') if not pos_builds else pos_builds,
                    data.get('runes') if not pos_runes else pos_runes,
                    pos_skills or data.get('skills', '')
                )
                if not pos_builds:
                    pos['builds'] = gen_builds
                if not pos_runes:
                    pos['runes'] = gen_runes
                if not pos_skills:
                    pos['skills'] = gen_skills
                    pos['skill_sequence'] = generate_skill_sequence(pos['skills'])
            
            # 确保skill_sequence存在
            if 'skill_sequence' not in pos and pos.get('skills'):
                pos['skill_sequence'] = generate_skill_sequence(pos['skills'])
            
            new_positions.append(pos)
        
        if new_positions:
            data['positions'] = new_positions
        
        # 4.4 更新OP.GG排行数据
        if champ_key and champ_key in opgg_by_key:
            avg = opgg_by_key[champ_key].get('average_stats') or {}
            data['win_rate'] = round(avg.get('win_rate', 0) * 100, 2)
            data['pick_rate'] = round(avg.get('pick_rate', 0) * 100, 2)
            data['ban_rate'] = round(avg.get('ban_rate', 0) * 100, 2)
            data['tier'] = avg.get('tier', 0)
            data['rank'] = avg.get('rank', 0)
            data['kda'] = round(avg.get('kda', 0), 2)
            
            if not data.get('main_position') and new_positions:
                data['main_position'] = max(new_positions, key=lambda p: p.get('pick_rate', 0)).get('name', '')
        
        # 4.5 更新tier标签
        tier = data.get('tier', 0)
        data['tier_label'] = {1: 'T1', 2: 'T2', 3: 'T3', 4: 'T4', 5: 'T5'}.get(tier, f'T{tier}')
        
        updated += 1
    
    # 5. 保存
    with open(BUILD_FILE, 'w', encoding='utf-8') as f:
        json.dump(builds, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Updated {updated} champions")
    logger.info(f"Saved to {BUILD_FILE}")


if __name__ == '__main__':
    main()
