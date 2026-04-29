"""
英雄排行数据抓取脚本
从OP.GG API抓取胜率/选取率/BAN率等排行数据，更新到champion_builds.json
"""
import json
import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# OP.GG API端点
OPGG_API = "https://lol-api-champion.op.gg/api/KR/champions/ranked"

# 文件路径
BUILD_FILE = os.path.join(os.path.dirname(__file__), 'static', 'champion_builds.json')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'static', 'data', 'zh_CN', 'champion')


def load_champion_key_map():
    """加载 英雄key(数字ID) -> 英雄id(英文名) 的映射"""
    import glob
    key_map = {}  # int key -> champion id string
    if not os.path.exists(DATA_DIR):
        logger.warning(f"英雄数据目录不存在: {DATA_DIR}")
        return key_map

    for filepath in glob.glob(os.path.join(DATA_DIR, '*.json')):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for champ_id, champ in data.get('data', {}).items():
                key = int(champ.get('key', 0))
                key_map[key] = champ_id
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}")
    
    logger.info(f"Loaded {len(key_map)} champion key mappings")
    return key_map


def fetch_opgg_data():
    """从OP.GG API获取韩服排位英雄排行数据"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    try:
        logger.info(f"Fetching data from OP.GG API: {OPGG_API}")
        resp = requests.get(OPGG_API, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        champions = data.get('data', [])
        logger.info(f"Fetched {len(champions)} champions from OP.GG")
        return champions
    except Exception as e:
        logger.error(f"Failed to fetch OP.GG data: {e}")
        return []


def parse_opgg_champion(champ_data):
    """
    解析单个英雄的OP.GG数据
    返回: {win_rate, pick_rate, ban_rate, tier, rank, kda, positions: [...]}
    """
    avg = champ_data.get('average_stats') or {}
    
    # 解析位置信息
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
    
    # 确定主要位置（选取率最高的位置）
    main_position = ''
    if positions:
        main_position = max(positions, key=lambda p: p.get('pick_rate', 0)).get('name', '')
    
    # OP.GG API返回的win_rate/pick_rate/ban_rate是小数(0.49=49%)，转为百分比
    return {
        'win_rate': round(avg.get('win_rate', 0) * 100, 2),
        'pick_rate': round(avg.get('pick_rate', 0) * 100, 2),
        'ban_rate': round(avg.get('ban_rate', 0) * 100, 2),
        'tier': avg.get('tier', 0),
        'rank': avg.get('rank', 0),
        'kda': round(avg.get('kda', 0), 2),
        'play': avg.get('play', 0),
        'main_position': main_position,
        'positions': positions,
    }


def position_to_cn(pos_name):
    """将OP.GG位置名转为中文"""
    pos_map = {
        'TOP': '上单',
        'JUNGLE': '打野',
        'MID': '中单',
        'ADC': 'ADC',
        'SUPPORT': '辅助',
    }
    return pos_map.get(pos_name, pos_name)


def tier_to_label(tier):
    """将tier数字转为标签"""
    tier_map = {
        1: 'T1',
        2: 'T2',
        3: 'T3',
        4: 'T4',
        5: 'T5',
    }
    return tier_map.get(tier, f'T{tier}')


def update_builds_with_rankings(opgg_champions, key_map):
    """
    将OP.GG排行数据合并到champion_builds.json
    """
    # 加载现有build数据
    if os.path.exists(BUILD_FILE):
        with open(BUILD_FILE, 'r', encoding='utf-8') as f:
            builds = json.load(f)
        logger.info(f"Loaded existing builds for {len(builds)} champions")
    else:
        builds = {}
    
    # 建立OP.GG数据的key映射
    opgg_by_key = {}
    for champ in opgg_champions:
        champ_id_num = champ.get('id', 0)
        opgg_by_key[champ_id_num] = champ
    
    # 更新每个英雄的数据
    updated = 0
    for key_num, champ_english_id in key_map.items():
        if key_num not in opgg_by_key:
            continue
        
        parsed = parse_opgg_champion(opgg_by_key[key_num])
        
        if champ_english_id not in builds:
            builds[champ_english_id] = {
                'roles': [],
                'roles_cn': [],
                'difficulty': 2,
                'builds': {},
                'runes': {},
                'skills': '',
            }
        
        # 更新排行数据
        builds[champ_english_id]['win_rate'] = parsed['win_rate']
        builds[champ_english_id]['pick_rate'] = parsed['pick_rate']
        builds[champ_english_id]['ban_rate'] = parsed['ban_rate']
        builds[champ_english_id]['tier'] = parsed['tier']
        builds[champ_english_id]['rank'] = parsed['rank']
        builds[champ_english_id]['kda'] = parsed['kda']
        builds[champ_english_id]['main_position'] = parsed['main_position']
        builds[champ_english_id]['positions'] = parsed['positions']
        
        # 如果原有roles_cn为空，用OP.GG数据补充
        if not builds[champ_english_id].get('roles_cn') and parsed['positions']:
            roles_cn = []
            for pos in parsed['positions']:
                cn = position_to_cn(pos['name'])
                if cn not in roles_cn:
                    roles_cn.append(cn)
            builds[champ_english_id]['roles_cn'] = roles_cn
            builds[champ_english_id]['roles'] = [pos['name'] for pos in parsed['positions']]
        
        # tier标签
        builds[champ_english_id]['tier_label'] = tier_to_label(parsed['tier'])
        
        updated += 1
    
    logger.info(f"Updated ranking data for {updated} champions")
    return builds


def main():
    logger.info("=" * 60)
    logger.info("英雄排行数据抓取脚本")
    logger.info("=" * 60)
    
    # 1. 加载英雄ID映射
    key_map = load_champion_key_map()
    if not key_map:
        logger.error("无法加载英雄ID映射，请检查数据目录")
        return
    
    # 2. 从OP.GG获取排行数据
    opgg_champions = fetch_opgg_data()
    if not opgg_champions:
        logger.error("未能获取OP.GG数据")
        return
    
    # 3. 合并到build数据
    builds = update_builds_with_rankings(opgg_champions, key_map)
    
    # 4. 保存
    with open(BUILD_FILE, 'w', encoding='utf-8') as f:
        json.dump(builds, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved updated builds to {BUILD_FILE}")
    
    # 5. 输出统计
    tier_counts = {}
    for champ_id, data in builds.items():
        tier = data.get('tier', 0)
        tier_label = tier_to_label(tier)
        tier_counts[tier_label] = tier_counts.get(tier_label, 0) + 1
    
    logger.info("\n=== 英雄梯队分布 ===")
    for tier in sorted(tier_counts.keys()):
        logger.info(f"  {tier}: {tier_counts[tier]} 个英雄")
    
    # T1英雄列表
    t1_champs = [(cid, d) for cid, d in builds.items() if d.get('tier') == 1]
    if t1_champs:
        logger.info("\n=== T1 英雄 ===")
        for cid, d in sorted(t1_champs, key=lambda x: x[1].get('rank', 999)):
            logger.info(f"  #{d.get('rank', '?')} {cid}: 胜率{d.get('win_rate', 0)}% 选取{d.get('pick_rate', 0)}% 禁用{d.get('ban_rate', 0)}%")


if __name__ == '__main__':
    main()
