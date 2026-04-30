"""
LOL数据助手 - Web服务器
Flask后端，提供API端点和静态资源
"""
from flask import Flask, jsonify, request, send_from_directory
import json
import os
import glob
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='/static')

# ==================== 英雄数据缓存 ====================
_champions_data = None
_champion_map = {}  # id -> data
_champion_key_map = {}  # key (如"Akali") -> data
_champion_builds = None  # 英雄build数据

BUILD_FILE = os.path.join(os.path.dirname(__file__), 'static', 'champion_builds.json')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'static', 'data', 'zh_CN', 'champion')

# AI 配置
AI_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'ai_config.json')

def load_ai_config():
    """加载 AI 配置"""
    if os.path.exists(AI_CONFIG_FILE):
        try:
            with open(AI_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载 AI 配置失败: {e}")
            return {}
    return {}

def save_ai_config(config):
    """保存 AI 配置"""
    try:
        with open(AI_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存 AI 配置失败: {e}")
        return False


def load_champions():
    """加载所有英雄数据"""
    global _champions_data, _champion_map, _champion_key_map
    if _champions_data is not None:
        return _champions_data

    champions = []
    if not os.path.exists(DATA_DIR):
        logger.warning(f"英雄数据目录不存在: {DATA_DIR}")
        return champions

    for filepath in glob.glob(os.path.join(DATA_DIR, '*.json')):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for champ_id, champ in data.get('data', {}).items():
                entry = {
                    'id': champ.get('id', ''),
                    'key': int(champ.get('key', 0)),
                    'name': champ.get('name', ''),
                    'title': champ.get('title', ''),
                    'tags': champ.get('tags', []),
                    'info': champ.get('info', {}),
                    'image': champ.get('image', {}).get('full', ''),
                    'blurb': champ.get('blurb', ''),
                }
                champions.append(entry)
                _champion_map[entry['key']] = entry
                _champion_key_map[entry['id']] = entry
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}")

    _champions_data = sorted(champions, key=lambda x: x['key'])
    logger.info(f"Loaded {len(_champions_data)} champions")
    return _champions_data


def get_champion_by_key(key):
    """通过英雄key(数字ID)获取英雄信息"""
    load_champions()
    return _champion_map.get(int(key))


def load_builds():
    """加载英雄build数据"""
    global _champion_builds
    if _champion_builds is not None:
        return _champion_builds
    try:
        with open(BUILD_FILE, 'r', encoding='utf-8') as f:
            _champion_builds = json.load(f)
        logger.info(f"Loaded builds for {len(_champion_builds)} champions")
    except Exception as e:
        logger.error(f"Failed to load builds: {e}")
        _champion_builds = {}
    return _champion_builds


def get_champion_build(champ_id):
    """获取英雄的build数据"""
    load_builds()
    return _champion_builds.get(champ_id, {})


def get_champion_by_id(champ_id):
    """通过英雄id(英文名)获取英雄信息"""
    load_champions()
    return _champion_key_map.get(champ_id)


# ==================== 路由 ====================

@app.route('/')
def index():
    """主页"""
    return send_from_directory('.', 'index.html')


# ==================== API端点（必须在catch-all之前） ====================

@app.route('/api/champions')
def api_champions():
    """获取所有英雄列表"""
    champions = load_champions()
    return jsonify({"success": True, "champions": champions})


@app.route('/api/champion/<champ_id>')
def api_champion_detail(champ_id):
    """获取单个英雄详情（含build数据）"""
    # 读取完整JSON
    filepath = os.path.join(DATA_DIR, f'{champ_id}.json')
    if not os.path.exists(filepath):
        # 尝试通过id/key查找
        champ = get_champion_by_id(champ_id)
        if not champ:
            try:
                champ = get_champion_by_key(int(champ_id))
                if champ:
                    filepath = os.path.join(DATA_DIR, f'{champ["id"]}.json')
            except ValueError:
                pass

    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": f"英雄 {champ_id} 未找到"}), 404

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 附加build数据
    build_data = get_champion_build(champ_id)
    if build_data:
        # 在data中为所有英雄添加build
        for cid, cdata in data.get('data', {}).items():
            cdata['build'] = get_champion_build(cid)
    else:
        # 至少附加当前英雄的build
        for cid in data.get('data', {}):
            data['data'][cid]['build'] = get_champion_build(cid)

    return jsonify({"success": True, "data": data.get("data", {})})


@app.route('/api/champion-build/<champ_id>')
def api_champion_build(champ_id):
    """获取英雄的推荐装备/符文/分路，支持?position=TOP参数"""
    position = request.args.get('position', '')
    build_data = get_champion_build(champ_id)
    if not build_data:
        return jsonify({"success": False, "error": "无此英雄的build数据"}), 404

    # 如果指定了分路，优先使用分路专属数据，不足部分用通用数据补全
    if position and build_data.get('positions'):
        pos_data = next((p for p in build_data['positions'] if isinstance(p, dict) and p.get('name') == position), None)
        if pos_data:
            result = dict(build_data)
            # 用分路统计数据覆盖通用统计
            for key in ['win_rate', 'pick_rate', 'ban_rate', 'kda', 'tier', 'tier_label']:
                if key in pos_data:
                    result[key] = pos_data[key]
            
            # 合并builds：分路专属 > 通用 > 空
            pos_builds = pos_data.get('builds', {})
            top_builds = build_data.get('builds', {})
            if pos_builds and any(v for v in pos_builds.values() if v):
                result['builds'] = pos_builds
            elif top_builds:
                # 分路没有装备数据时用通用数据，但标记为fallback
                result['builds'] = top_builds
                result['builds_fallback'] = True
            
            # 合并runes
            pos_runes = pos_data.get('runes', {})
            top_runes = build_data.get('runes', {})
            if pos_runes and pos_runes.get('primary'):
                result['runes'] = pos_runes
            elif top_runes and top_runes.get('primary'):
                result['runes'] = top_runes
                result['runes_fallback'] = True
            
            # 合并skills
            for key in ['skills', 'skill_sequence']:
                pos_val = pos_data.get(key)
                top_val = build_data.get(key)
                if pos_val:
                    result[key] = pos_val
                elif top_val:
                    result[key] = top_val
            
            result['current_position'] = position
            return jsonify({"success": True, "build": result})

    return jsonify({"success": True, "build": build_data})


@app.route('/api/update-rankings', methods=['POST'])
def api_update_rankings():
    """手动触发排行数据更新（从OP.GG抓取）"""
    try:
        import subprocess
        result = subprocess.run(
            ['python', os.path.join(os.path.dirname(__file__), 'scrape_rankings.py')],
            capture_output=True, text=True, timeout=60
        )
        # 刷新内存中的build数据
        global _champion_builds
        _champion_builds = None
        load_builds()
        return jsonify({
            "success": True,
            "message": "排行数据更新完成",
            "output": result.stdout[-500:] if result.stdout else "",
            "errors": result.stderr[-500:] if result.stderr else ""
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/champions/with-build')
def api_champions_with_build():
    """获取所有英雄列表（含build数据，用于图鉴排序/筛选）"""
    champions = load_champions()
    builds = load_builds()
    # 为每个英雄附加排行和build数据
    result = []
    for c in champions:
        entry = dict(c)
        build = builds.get(c['id'], {})
        entry['roles_cn'] = build.get('roles_cn', [])
        entry['difficulty'] = build.get('difficulty', 2)
        entry['win_rate'] = build.get('win_rate')
        entry['pick_rate'] = build.get('pick_rate')
        entry['ban_rate'] = build.get('ban_rate')
        entry['tier'] = build.get('tier', 0)
        entry['tier_label'] = build.get('tier_label', '')
        entry['rank'] = build.get('rank', 0)
        entry['kda'] = build.get('kda')
        entry['main_position'] = build.get('main_position', '')
        result.append(entry)
    return jsonify({"success": True, "champions": result})


@app.route('/api/player')
def api_player():
    """查询玩家信息 (通过Riot API)"""
    from riot_api_client import get_player_full_info, search_players_by_name

    game_name = request.args.get('name', '')
    tag_line = request.args.get('tag', '')
    platform = request.args.get('platform', 'kr')

    if not game_name:
        return jsonify({"success": False, "error": "请输入游戏名"})

    # 如果没有标签，搜索多个标签返回所有匹配玩家
    if not tag_line:
        result = search_players_by_name(game_name, platform)
        # 补充英雄名称
        load_champions()
        for player in result.get("players", []):
            summoner = player.get("summoner") or {}
            if summoner.get("profile_icon_id"):
                player["profile_icon_path"] = f"/static/img/profileicon/{summoner['profile_icon_id']}.png"
        return jsonify(result)

    result = get_player_full_info(game_name, tag_line, platform)

    # 补充英雄名称
    load_champions()
    if result.get("success"):
        # 熟练度加上英雄名称
        for m in result.get("masteries", []):
            champ = _champion_map.get(m.get("champion_id", 0))
            if champ:
                m["champion_name"] = champ["name"]
                m["champion_image"] = champ["image"]

        # 比赛加上英雄名称
        for match in result.get("matches", []):
            for p in match.get("participants", []):
                champ = _champion_map.get(p.get("champion_id", 0))
                if champ:
                    p["champion_name_cn"] = champ["name"]
                    p["champion_image"] = champ["image"]

        # 召唤师头像路径
        if result.get("summoner"):
            icon_id = result["summoner"].get("profile_icon_id", 0)
            result["summoner"]["profile_icon_path"] = f"/static/img/profileicon/{icon_id}.png"

    return jsonify(result)


@app.route('/api/lcu/status')
def api_lcu_status():
    """获取LCU连接状态"""
    from lcu_connect import get_lcu_status
    return jsonify({"success": True, **get_lcu_status()})


@app.route('/api/lcu/connect')
def api_lcu_connect():
    """尝试连接LCU"""
    from lcu_connect import find_lcu
    result = find_lcu()
    return jsonify(result)


@app.route('/api/lcu/current-summoner')
def api_lcu_current_summoner():
    """从LCU获取当前登录的召唤师信息"""
    from lcu_connect import get_current_summoner, get_current_rank, get_lcu_status
    
    # 先检查连接状态
    status = get_lcu_status()
    if not status.get('connected'):
        return jsonify({
            "success": False, 
            "error": "LCU未连接，请先点击'重新连接'"
        })
    
    result = get_current_summoner()

    # 补充英雄名称
    load_champions()
    if result.get("success"):
        icon_id = result.get("profile_icon_id", 0)
        result["profile_icon_path"] = f"/static/img/profileicon/{icon_id}.png"
        
        # 同时获取排位信息
        puuid = result.get("puuid", "")
        if puuid:
            rank_result = get_current_rank(puuid)
            if rank_result.get("success"):
                result["rank_data"] = rank_result["data"]

    return jsonify(result)


@app.route('/api/lcu/rank/<puuid>')
def api_lcu_rank(puuid):
    """从LCU获取排位信息"""
    from lcu_connect import get_current_rank
    result = get_current_rank(puuid)
    return jsonify(result)


@app.route('/api/mastery')
def api_mastery():
    """查询指定英雄熟练度"""
    from riot_api_client import get_champion_mastery

    puuid = request.args.get('puuid', '')
    champion_id = request.args.get('champion_id', '84')
    platform = request.args.get('platform', 'kr')

    if not puuid:
        return jsonify({"success": False, "error": "缺少puuid参数"})

    result = get_champion_mastery(puuid, int(champion_id), platform)

    # 补充英雄名称
    load_champions()
    if result.get("success"):
        champ = _champion_map.get(int(champion_id))
        if champ:
            result["champion_name"] = champ["name"]
            result["champion_image"] = champ["image"]

    return jsonify(result)


@app.route('/api/matches')
def api_matches():
    """查询最近比赛"""
    from riot_api_client import get_match_ids, get_match_detail

    puuid = request.args.get('puuid', '')
    count = int(request.args.get('count', '10'))

    if not puuid:
        return jsonify({"success": False, "error": "缺少puuid参数"})

    match_result = get_match_ids(puuid, count)
    if not match_result.get("success"):
        return jsonify(match_result)

    # 获取比赛详情
    load_champions()
    matches = []
    for mid in match_result["match_ids"][:count]:
        detail = get_match_detail(mid)
        if detail.get("success"):
            # 补充英雄名称
            for p in detail.get("participants", []):
                champ = _champion_map.get(p.get("champion_id", 0))
                if champ:
                    p["champion_name_cn"] = champ["name"]
                    p["champion_image"] = champ["image"]
            matches.append(detail)

    return jsonify({"success": True, "matches": matches})


@app.route('/api/match/<match_id>')
def api_match_detail(match_id):
    """获取单场比赛详情（含双方完整阵容）"""
    from riot_api_client import get_match_detail

    detail = get_match_detail(match_id)
    if detail.get("success"):
        # 补充英雄名称
        load_champions()
        for p in detail.get("participants", []):
            champ = _champion_map.get(p.get("champion_id", 0))
            if champ:
                p["champion_name_cn"] = champ["name"]
                p["champion_image"] = champ["image"]

    return jsonify(detail)


# ==================== AI 智能问答（讯飞星火 Spark X）====================

import hashlib
import hmac
import base64
import datetime
from urllib.parse import quote, urlparse
import websocket

XINGHUO_CONFIG = {
    'app_id': 'b3105b92',
    'api_key': '09ed8f5ee8ab99d26e36841fc8872606',
    'api_secret': 'ZTAzMjMzMmYxNTRhZjA3NGYxYWU1ZTg3',
    'spark_domain': 'spark-x',
    'api_url': 'wss://spark-api.xf-yun.com/x2',
}

def build_lol_context(query):
    """根据用户问题构建英雄联盟相关上下文数据"""
    load_champions()
    load_builds()
    context_parts = []
    matched_pos = None
    
    # 检测问题中是否提到具体英雄（同时匹配中文名、别名和英文名）
    mentioned_champs = []
    query_lower = query.lower()
    for champ_id, champ_info in _champion_key_map.items():
        name = champ_info.get('name', '')   # 中文名（如"疾风剑豪"）
        title = champ_info.get('title', '') # 别名（如"亚索"）
        champ_id_lower = champ_id.lower()   # 英文名（如"yasuo"）
        if (name and name in query) or (title and title in query) or (champ_id_lower in query_lower):
            mentioned_champs.append(champ_id)
    
    # 如果提到了具体英雄，提供该英雄的详细数据
    for champ_id in mentioned_champs[:3]:  # 最多3个英雄
        champ = _champion_key_map.get(champ_id, {})
        build = _champion_builds.get(champ_id, {})
        if champ:
            champ_title = champ.get('title', '')
            champ_name = champ.get('name', champ_id)
            display_name = champ_title if champ_title else champ_name
            info_str = f"英雄【{display_name}】："
            info_str += f"定位{champ.get('tags', [])}，"
            if build:
                info_str += f"主要位置{build.get('main_position', '')}，"
                info_str += f"胜率{build.get('win_rate', '')}%，"
                info_str += f"选取率{build.get('pick_rate', '')}%，"
                info_str += f"禁用率{build.get('ban_rate', '')}%，"
                info_str += f"KDA {build.get('kda', '')}，"
                info_str += f"梯队{build.get('tier_label', '')}，"
                b = build.get('builds', {})
                if b.get('core'):
                    info_str += f"核心装备：{'、'.join(b['core'])}，"
                if b.get('boots'):
                    info_str += f"鞋子：{'、'.join(b['boots'])}，"
                r = build.get('runes', {})
                if r.get('primary'):
                    info_str += f"主系符文：{r['primary']}({','.join(r.get('primary_runes', []))})，"
                if r.get('secondary'):
                    info_str += f"副系符文：{r['secondary']}({','.join(r.get('secondary_runes', []))})，"
                if build.get('skills'):
                    info_str += f"加点：{build['skills']}，"
                positions = build.get('positions', [])
                if positions:
                    pos_info = '、'.join([f"{p['name']}({p.get('win_rate','')}%胜率)" for p in positions])
                    info_str += f"可选位置：{pos_info}"
            context_parts.append(info_str)
    
    # 如果问题是关于版本强势英雄的（且不是特定位置查询），提供T1列表
    if any(kw in query for kw in ['最强', '版本', 'T1', '强势', '推荐', 'OP', '超模', 't1']) and not matched_pos:
        t1_champs = []
        for cid, b in _champion_builds.items():
            if b.get('tier') == 1:
                champ_info = _champion_key_map.get(cid, {})
                champ_title = champ_info.get('title', '')
                champ_name = champ_info.get('name', cid)
                display_name = champ_title if champ_title else champ_name
                t1_champs.append(f"{display_name}({b.get('main_position', '')} 胜率{b.get('win_rate', '')}% 选取{b.get('pick_rate', '')}%)")
        if t1_champs:
            context_parts.append(f"当前韩服T1英雄：{'、'.join(t1_champs[:10])}")
    
    # 如果问题是关于某个位置的
    pos_keywords = {'上单': 'TOP', '打野': 'JUNGLE', '中单': 'MID', 'ADC': 'ADC', '辅助': 'SUPPORT',
                    '上': 'TOP', '野': 'JUNGLE', '中': 'MID', '下路': 'ADC', '辅': 'SUPPORT',
                    'top': 'TOP', 'jungle': 'JUNGLE', 'mid': 'MID', 'adc': 'ADC', 'support': 'SUPPORT'}
    for kw, pos_name in pos_keywords.items():
        if kw in query_lower:
            pos_champs = []
            for cid, b in _champion_builds.items():
                for p in b.get('positions', []):
                    if p.get('name') == pos_name and p.get('tier', 0) <= 2:
                        champ_name = _champion_key_map.get(cid, {}).get('name', cid)
                        champ_title = _champion_key_map.get(cid, {}).get('title', '')
                        display_name = champ_title if champ_title else champ_name
                        pos_champs.append(f"{display_name}({p.get('win_rate', '')}%胜率 {b.get('tier_label', '')})")
                        break
            if pos_champs:
                cn_pos = {'TOP': '上单', 'JUNGLE': '打野', 'MID': '中单', 'ADC': 'ADC', 'SUPPORT': '辅助'}.get(pos_name, pos_name)
                context_parts.append(f"【{cn_pos}】强势英雄(T1/T2)：{'、'.join(pos_champs[:10])}")
            matched_pos = pos_name
            break
    
    return '\n'.join(context_parts) if context_parts else ''


def _build_ws_url(config):
    """构建讯飞星火 WebSocket 鉴权 URL"""
    api_key = config['api_key']
    api_secret = config['api_secret']
    api_url = config.get('api_url', 'wss://spark-api.xf-yun.com/x2')

    parsed = urlparse(api_url)
    host = parsed.hostname
    path = parsed.path

    now = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    signature_origin = f'host: {host}\ndate: {now}\nGET {path} HTTP/1.1'
    signature_sha = hmac.new(api_secret.encode(), signature_origin.encode(), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode()
    authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode()).decode()
    full_url = f'{api_url}?authorization={quote(authorization)}&date={quote(now)}&host={host}'
    return full_url


def generate_ai_reply_xinghuo(query, history=None):
    """使用讯飞星火 Spark X (X2) 模型生成回复 - 直接WebSocket方式"""
    config = XINGHUO_CONFIG

    system_prompt = """你是"LOL数据助手"的AI顾问，专门为英雄联盟玩家提供专业、详尽的游戏指导。

## 你的核心能力
1. **版本分析**：基于韩服排位数据（OP.GG），分析英雄梯队、胜率、选取率趋势
2. **出装建议**：提供当前版本最优出装路线，解释核心装备的选配理由
3. **符文搭配**：推荐适配英雄和位置的符文配置，说明符文选择的博弈思路
4. **对线策略**：分析对线优劣势，提供换血、控线、游走等具体打法建议
5. **团战定位**：讲解英雄在不同阵容中的职责和团战站位、切入时机

## 回答规范
- **结构化**：使用序号、分段组织回答，重点内容用【】标注
- **有数据支撑**：引用具体胜率、KDA等数据佐证观点
- **解释原因**：不仅给出建议，还要解释"为什么这样做"
- **实用导向**：给出可操作的具体建议，而非空泛的理论
- **版本意识**：明确说明建议基于当前版本，版本更迭可能影响结论

## 数据来源
你拥有韩服排位赛实时数据（来自OP.GG），包括英雄胜率、选取率、禁用率、KDA、梯队排名等。回答时优先引用这些数据。

## 注意事项
- 区分排位赛和休闲玩法的差异
- 承认不确定性，不要编造数据
- 对于冷门英雄/玩法，说明数据量有限
- 回答使用中文"""

    lol_context = build_lol_context(query)
    if lol_context:
        enhanced_query = f"【参考数据】\n{lol_context}\n\n【用户问题】{query}"
    else:
        enhanced_query = query

    messages = [{"role": "user", "content": system_prompt},
                {"role": "assistant", "content": "好的，我是LOL数据助手的AI顾问，已准备好为玩家提供专业的英雄联盟指导。我会基于韩服排位数据分析，给出有数据支撑的详细建议。"}]

    if history:
        for msg in history[-8:]:
            role = msg.get('role', 'user')
            if role in ('user', 'assistant'):
                messages.append({"role": role, "content": msg.get('content', '')})

    messages.append({"role": "user", "content": enhanced_query})

    request_data = {
        "header": {"app_id": config['app_id'], "uid": "lol_assistant"},
        "parameter": {"chat": {"domain": config.get('spark_domain', 'spark-x')}},
        "payload": {"message": {"text": messages}}
    }

    full_url = _build_ws_url(config)

    content_parts = []
    error_msg = None

    def on_message(ws, message):
        nonlocal error_msg
        try:
            data = json.loads(message)
            code = data.get("header", {}).get("code", -1)
            if code != 0:
                error_msg = f"API错误({code}): {data.get('header', {}).get('message', '未知')}"
                ws.close()
                return

            choices = data.get("payload", {}).get("choices", {})
            text_list = choices.get("text", [])
            status = choices.get("status", 0)

            for item in text_list:
                c = item.get("content", "")
                if c:
                    content_parts.append(c)

            if status == 2:
                ws.close()
        except Exception as e:
            error_msg = str(e)
            ws.close()

    def on_error(ws, error):
        nonlocal error_msg
        error_msg = str(error)

    def on_open(ws):
        ws.send(json.dumps(request_data))

    try:
        ws = websocket.WebSocketApp(
            full_url,
            on_message=on_message,
            on_error=on_error,
            on_open=on_open,
        )
        ws.run_forever()

        if error_msg:
            logger.error(f"讯飞星火调用出错: {error_msg}")
            return None

        if content_parts:
            return ''.join(content_parts)

        return None

    except Exception as e:
        logger.error(f"讯飞星火 API 调用失败: {e}")
        return None


@app.route('/api/save-ai-config', methods=['POST'])
def api_save_ai_config():
    """保存AI配置"""
    try:
        data = request.get_json()
        config = {
            'aiApiKey': data.get('aiApiKey', ''),
            'xinghuoAppId': data.get('xinghuoAppId', ''),
            'xinghuoApiSecret': data.get('xinghuoApiSecret', ''),
        }
        if save_ai_config(config):
            # 同步更新运行时配置
            if config['xinghuoAppId']:
                XINGHUO_CONFIG['app_id'] = config['xinghuoAppId']
            if config['aiApiKey']:
                XINGHUO_CONFIG['api_key'] = config['aiApiKey']
            if config['xinghuoApiSecret']:
                XINGHUO_CONFIG['api_secret'] = config['xinghuoApiSecret']
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "保存失败"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/get-ai-config')
def api_get_ai_config():
    """获取AI配置"""
    config = load_ai_config()
    return jsonify({"success": True, "config": config})


@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    """AI 智能问答接口（讯飞星火）"""
    try:
        data = request.get_json()
        query = data.get('message', '')
        history = data.get('history', [])
        champ_id = data.get('champ_id', '')  # 可选：当前查看的英雄ID
        
        if not query:
            return jsonify({"success": False, "error": "请输入问题"})
        
        # 如果用户正在查看某个英雄，自动附加该英雄的上下文
        if champ_id and champ_id not in query:
            build = get_champion_build(champ_id)
            champ_info = get_champion_by_id(champ_id)
            if build and champ_info:
                champ_name = champ_info.get('name', champ_id)
                # 如果用户问的问题可能跟当前英雄相关，附加英雄名
                if any(kw in query for kw in ['出装', '符文', '加点', '玩法', '攻略', '怎么玩', '对线', '技能', '装备', '推荐']):
                    query = f"关于{champ_name}：{query}"
        
        # 生成回复
        reply = generate_ai_reply_xinghuo(query, history)
        
        if not reply:
            return jsonify({"success": False, "error": "生成回复失败，请稍后重试"})
        
        return jsonify({"success": True, "reply": reply})
    except Exception as e:
        logger.error(f"AI 聊天失败: {e}")
        return jsonify({"success": False, "error": str(e)})


# ==================== 静态文件（catch-all，放在最后） ====================

@app.route('/<path:filename>')
def serve_file(filename):
    """提供静态文件"""
    if os.path.exists(os.path.join('.', filename)):
        return send_from_directory('.', filename)
    return jsonify({"error": "File not found"}), 404


# ==================== 启动 ====================

if __name__ == '__main__':
    # 加载英雄数据
    load_champions()

    print("=" * 50)
    print("  LOL数据助手 - 国服版")
    print("  访问地址: http://127.0.0.1:5000")
    print("=" * 50)

    app.run(host='127.0.0.1', port=5000, debug=True)
