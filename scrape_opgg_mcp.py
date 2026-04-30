"""
从OP.GG MCP API获取所有英雄的分路专属数据
- 按分路分别存储出装、符文、技能加点
- 提取核心装备、起始装备、鞋子、可选装备(situational)
- 修复：合并到已有数据，不覆盖positions统计信息
"""
import json
import os
import re
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BUILD_FILE = os.path.join(os.path.dirname(__file__), 'static', 'champion_builds.json')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'static', 'data', 'zh_CN', 'champion')
MCP_URL = 'https://mcp-api.op.gg/mcp'
MCP_HEADERS = {'Content-Type': 'application/json', 'Accept': 'application/json'}

# 所有位置
POSITIONS = ['top', 'jungle', 'mid', 'adc', 'support']

# 位置名映射
POS_NAME_MAP = {
    'top': 'TOP',
    'jungle': 'JUNGLE',
    'mid': 'MID',
    'adc': 'ADC',
    'support': 'SUPPORT'
}


def mcp_initialize():
    """初始化MCP会话"""
    payload = {
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05', 'capabilities': {},
            'clientInfo': {'name': 'lol-data-scraper', 'version': '1.0.0'}
        }
    }
    resp = requests.post(MCP_URL, json=payload, headers=MCP_HEADERS, timeout=15)
    return resp.json()


def mcp_get_champion_analysis(champion, position, lang='zh_CN'):
    """调用OP.GG MCP获取英雄分析数据"""
    payload = {
        'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
        'params': {
            'name': 'lol_get_champion_analysis',
            'arguments': {
                'champion': champion.upper(),
                'position': position,
                'game_mode': 'ranked',
                'lang': lang,
            }
        }
    }
    try:
        resp = requests.post(MCP_URL, json=payload, headers=MCP_HEADERS, timeout=30)
        data = resp.json()
        content = data.get('result', {}).get('content', [])
        for c in content:
            if c.get('type') == 'text':
                return c['text']
        return None
    except Exception as e:
        logger.error(f"MCP call failed for {champion}/{position}: {e}")
        return None


def extract_core_items(text):
    """提取核心三件套 - 第一个CoreItems"""
    matches = list(re.finditer(r'CoreItems\(\[([^\]]+)\],\[([^\]]+)\]', text))
    if matches:
        ids_str = matches[0].group(1)
        names_str = matches[0].group(2)
        ids = [int(x.strip()) for x in ids_str.split(',') if x.strip().isdigit()]
        names = re.findall(r'"([^"]*)"', names_str)
        return {'ids': ids, 'names': names}
    return None


def extract_boots(text):
    """提取鞋子 - 第二个CoreItems"""
    matches = list(re.finditer(r'CoreItems\(\[([^\]]+)\],\[([^\]]+)\]', text))
    if len(matches) >= 2:
        ids_str = matches[1].group(1)
        names_str = matches[1].group(2)
        ids = [int(x.strip()) for x in ids_str.split(',') if x.strip().isdigit()]
        names = re.findall(r'"([^"]*)"', names_str)
        return {'ids': ids, 'names': names}
    return None


def extract_starter_items(text):
    """提取起始装备 - 第三个CoreItems"""
    matches = list(re.finditer(r'CoreItems\(\[([^\]]+)\],\[([^\]]+)\]', text))
    if len(matches) >= 3:
        ids_str = matches[2].group(1)
        names_str = matches[2].group(2)
        ids = [int(x.strip()) for x in ids_str.split(',') if x.strip().isdigit()]
        names = re.findall(r'"([^"]*)"', names_str)
        return {'ids': ids, 'names': names}
    return None


def extract_situational_items(text, core_names=None):
    """提取可选装备 - 第4-8个CoreItems (fourth_items, fifth_items, sixth_items, last_items)
    去重：排除已出现在核心装备中的物品
    """
    matches = list(re.finditer(r'CoreItems\(\[([^\]]+)\],\[([^\]]+)\]', text))
    situational = []
    # 第4-8个是各个位置的可选装备
    for match in matches[3:9]:
        ids_str = match.group(1)
        names_str = match.group(2)
        names = re.findall(r'"([^"]*)"', names_str)
        for name in names:
            if name and not name.isdigit():
                if name not in situational:
                    # 排除已在核心装备中的
                    if core_names and name in core_names:
                        continue
                    situational.append(name)
    return situational if situational else None


def extract_skills(text):
    """从MCP响应中提取技能加点序列"""
    pattern = r'Skills\(\[([^\]]+)\]'
    matches = re.findall(pattern, text)
    if not matches:
        return None
    skills = re.findall(r'"([^"]+)"', matches[0])
    return skills


def extract_skill_masteries(text):
    """提取技能加点优先级 (如 Q>E>W)"""
    match = re.search(r'SkillMasteries\(\[([^\]]+)\]', text)
    if match:
        skills = re.findall(r'"([^"]+)"', match.group(1))
        if len(skills) == 3:
            return f"R>{'>'.join(skills)}"
    return None


def extract_runes(text):
    """从MCP响应中提取符文配置"""
    # Runes格式: Runes(id, primary_page_id, "primary_page_name", [primary_rune_ids], ["primary_rune_names"], 
    #                secondary_page_id, "secondary_page_name", [secondary_rune_ids], ["secondary_rune_names"], 
    #                [stat_mod_ids], [stat_mod_names], play, win, pick_rate)
    runes_match = re.search(r'Runes\(([^)]+(?:\([^)]*\))*[^)]*)\)', text)
    if not runes_match:
        return None
    
    runes_text = runes_match.group(0)
    
    # 提取所有引用字符串
    quoted_strings = re.findall(r'"([^"]*)"', runes_text)
    
    # 提取列表内容
    lists_in_runes = []
    i = 0
    while i < len(runes_text):
        if runes_text[i] == '[':
            depth = 0
            j = i
            while j < len(runes_text):
                if runes_text[j] == '[':
                    depth += 1
                elif runes_text[j] == ']':
                    depth -= 1
                    if depth == 0:
                        lists_in_runes.append(runes_text[i+1:j])
                        i = j + 1
                        break
                elif runes_text[j] == '"':
                    j += 1
                    while j < len(runes_text) and runes_text[j] != '"':
                        if runes_text[j] == '\\':
                            j += 1
                        j += 1
                j += 1
            else:
                i += 1
        else:
            i += 1
    
    if len(lists_in_runes) < 5 or len(quoted_strings) < 2:
        return None
    
    try:
        # 列表顺序:
        # [0] primary_rune_ids, [1] primary_rune_names, 
        # [2] secondary_rune_ids, [3] secondary_rune_names
        # [4+] stat_mods
        primary_names = re.findall(r'"([^"]*)"', lists_in_runes[1])
        secondary_names = re.findall(r'"([^"]*)"', lists_in_runes[3])
        
        # 主系名称是第一个quoted string
        primary_page = quoted_strings[0] if quoted_strings else ''
        
        # 副系名称在primary_rune_names之后
        secondary_page = ''
        if len(quoted_strings) > len(primary_names) + 1:
            secondary_page = quoted_strings[len(primary_names) + 1]
        
        result = {
            'primary': primary_page,
            'primary_runes': primary_names,
            'secondary': secondary_page,
            'secondary_runes': secondary_names,
        }
        return result
    except Exception as e:
        logger.error(f"Failed to parse runes: {e}")
        return None


def complete_skill_sequence(partial_seq):
    """将OP.GG的部分技能加点序列（15个元素）补全为18个"""
    if not partial_seq:
        return None
    
    seq = list(partial_seq)
    counts = {'Q': 0, 'W': 0, 'E': 0, 'R': 0}
    for s in seq:
        if s in counts:
            counts[s] += 1
    
    while len(seq) < 18:
        next_level = len(seq) + 1
        if next_level in [6, 11, 16] and counts['R'] < 3:
            seq.append('R')
            counts['R'] += 1
        else:
            priority = []
            for s in seq:
                if s != 'R' and s not in priority:
                    priority.append(s)
            placed = False
            for skill in priority:
                if counts[skill] < 5:
                    seq.append(skill)
                    counts[skill] += 1
                    placed = True
                    break
            if not placed:
                for skill in ['Q', 'W', 'E']:
                    if counts[skill] < 5:
                        seq.append(skill)
                        counts[skill] += 1
                        placed = True
                        break
    
    return seq


def parse_champion_data(raw_text):
    """解析OP.GG MCP返回的完整英雄数据"""
    if not raw_text:
        return None
    
    result = {
        'skills': None,
        'skill_sequence': None,
        'skill_priority': None,
        'runes': None,
        'core_items': None,
        'starter_items': None,
        'boots': None,
        'situational_items': None,
    }
    
    # 1. 技能加点
    skills = extract_skills(raw_text)
    if skills:
        result['skills'] = skills
        result['skill_sequence'] = complete_skill_sequence(skills)
    
    # 2. 技能优先级
    priority = extract_skill_masteries(raw_text)
    if priority:
        result['skill_priority'] = priority
    
    # 3. 符文
    runes = extract_runes(raw_text)
    if runes:
        result['runes'] = runes
    
    # 4. 核心装备
    core = extract_core_items(raw_text)
    if core:
        result['core_items'] = core
    
    # 5. 起始装备
    starter = extract_starter_items(raw_text)
    if starter:
        result['starter_items'] = starter
    
    # 6. 鞋子
    boots = extract_boots(raw_text)
    if boots:
        result['boots'] = boots
    
    # 7. 可选装备
    situational = extract_situational_items(raw_text)
    if situational:
        result['situational_items'] = situational
    
    return result


def get_all_champion_names():
    """从本地数据获取所有英雄名"""
    champions = {}
    if not os.path.exists(DATA_DIR):
        return champions
    
    import glob
    for filepath in glob.glob(os.path.join(DATA_DIR, '*.json')):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for champ_id, champ in data.get('data', {}).items():
                champion_name = champ_id.upper().replace("'", "").replace(" ", "").replace(".", "")
                champions[champ_id] = {
                    'opgg_name': champion_name,
                    'name_cn': champ.get('name', ''),
                    'key': int(champ.get('key', 0)) if champ.get('key') else 0
                }
        except Exception:
            pass
    
    return champions


def get_champion_positions_from_ranked():
    """从OP.GG ranked API获取每个英雄的位置列表"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        resp = requests.get('https://lol-api-champion.op.gg/api/KR/champions/ranked', headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        positions = {}
        for champ in data.get('data', []):
            champ_id = champ.get('id', 0)
            pos_list = []
            for pos in champ.get('positions', []):
                pos_name = pos.get('name', '').upper()
                if pos_name in POS_NAME_MAP.values():
                    for k, v in POS_NAME_MAP.items():
                        if v == pos_name:
                            pos_list.append(k)
                            break
            positions[champ_id] = pos_list
        return positions
    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        return {}


def main():
    logger.info("=" * 60)
    logger.info("从OP.GG MCP API获取英雄分路专属数据")
    logger.info("=" * 60)
    
    # 1. 初始化MCP
    mcp_initialize()
    logger.info("MCP session initialized")
    
    # 2. 加载现有数据
    if os.path.exists(BUILD_FILE):
        with open(BUILD_FILE, 'r', encoding='utf-8') as f:
            builds = json.load(f)
        logger.info(f"Loaded {len(builds)} champions from champion_builds.json")
    else:
        builds = {}
    
    # 3. 获取英雄名称映射
    champion_map = get_all_champion_names()
    logger.info(f"Found {len(champion_map)} champions in local data")
    
    # 4. 获取每个英雄的位置列表
    ranked_positions = get_champion_positions_from_ranked()
    logger.info(f"Got positions for {len(ranked_positions)} champions from OP.GG")
    
    # 5. 建立key到champ_id的映射
    key_to_id = {}
    for champ_id, info in champion_map.items():
        key_to_id[info['key']] = champ_id
    
    # 6. 逐个英雄获取数据
    total = len(champion_map)
    updated = 0
    errors = 0
    
    for champ_id, info in champion_map.items():
        opgg_name = info['opgg_name']
        champ_key = info['key']
        
        # 获取该英雄的位置
        positions = ranked_positions.get(champ_key, ['top'])
        if not positions:
            positions = ['top']
        
        logger.info(f"[{updated+1}/{total}] {champ_id} ({opgg_name}) - positions: {positions}")
        
        # 确保英雄在builds中
        if champ_id not in builds:
            builds[champ_id] = {'name': info['name_cn']}
        
        # 获取每个位置的数据
        for pos in positions:
            pos_name = POS_NAME_MAP.get(pos, pos.upper())
            
            try:
                raw_text = mcp_get_champion_analysis(opgg_name, pos)
                if raw_text:
                    parsed = parse_champion_data(raw_text)
                    
                    if parsed:
                        # 确保positions列表存在
                        if 'positions' not in builds[champ_id] or not isinstance(builds[champ_id]['positions'], list):
                            builds[champ_id]['positions'] = []
                        
                        # 查找或创建位置条目
                        pos_entry = None
                        for p in builds[champ_id]['positions']:
                            if isinstance(p, dict) and p.get('name') == pos_name:
                                pos_entry = p
                                break
                        
                        if not pos_entry:
                            pos_entry = {'name': pos_name}
                            builds[champ_id]['positions'].append(pos_entry)
                        
                        # 更新位置专属数据
                        if parsed.get('skill_sequence'):
                            pos_entry['skill_sequence'] = parsed['skill_sequence']
                        if parsed.get('skill_priority'):
                            pos_entry['skills'] = parsed['skill_priority']
                        if parsed.get('runes'):
                            pos_entry['runes'] = parsed['runes']
                        
                        # 构建该位置的builds
                        pos_builds = {}
                        if parsed.get('core_items'):
                            pos_builds['core'] = parsed['core_items'].get('names', [])
                            pos_builds['core_ids'] = parsed['core_items'].get('ids', [])
                        if parsed.get('starter_items'):
                            pos_builds['starts'] = parsed['starter_items'].get('names', [])
                        if parsed.get('boots'):
                            pos_builds['boots'] = parsed['boots'].get('names', [])
                        if parsed.get('situational_items'):
                            pos_builds['situational'] = parsed['situational_items']
                        
                        if pos_builds:
                            pos_entry['builds'] = pos_builds
                        
                        # 同时更新顶级数据（使用主位置的数据）
                        if pos == positions[0]:
                            if parsed.get('skill_sequence'):
                                builds[champ_id]['skill_sequence'] = parsed['skill_sequence']
                            if parsed.get('skill_priority'):
                                builds[champ_id]['skills'] = parsed['skill_priority']
                            if parsed.get('runes'):
                                builds[champ_id]['runes'] = parsed['runes']
                            
                            top_builds = {}
                            if parsed.get('core_items'):
                                top_builds['core'] = parsed['core_items'].get('names', [])
                                top_builds['core_ids'] = parsed['core_items'].get('ids', [])
                            if parsed.get('starter_items'):
                                top_builds['starts'] = parsed['starter_items'].get('names', [])
                            if parsed.get('boots'):
                                top_builds['boots'] = parsed['boots'].get('names', [])
                            if parsed.get('situational_items'):
                                top_builds['situational'] = parsed['situational_items']
                            
                            if top_builds:
                                builds[champ_id]['builds'] = top_builds
                        
                        logger.info(f"  {pos}: skills={parsed.get('skill_priority')}, runes={parsed.get('runes', {}).get('primary')}, core={[n for n in (parsed.get('core_items') or {}).get('names', [])]}, situ={parsed.get('situational_items')}")
                    else:
                        logger.warning(f"  {pos}: Failed to parse data")
                        errors += 1
                else:
                    logger.warning(f"  {pos}: No data returned")
                    errors += 1
                
                # 限速
                time.sleep(1.5)
                
            except Exception as e:
                logger.error(f"  {pos}: Error - {e}")
                errors += 1
                time.sleep(3)
        
        updated += 1
        
        # 每20个英雄保存一次
        if updated % 20 == 0:
            with open(BUILD_FILE, 'w', encoding='utf-8') as f:
                json.dump(builds, f, ensure_ascii=False, indent=2)
            logger.info(f"  [Auto-save] {updated}/{total} champions saved")
    
    # 7. 最终保存
    with open(BUILD_FILE, 'w', encoding='utf-8') as f:
        json.dump(builds, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\nDone! Updated: {updated}, Errors: {errors}")
    logger.info(f"Saved to {BUILD_FILE}")


if __name__ == '__main__':
    main()
