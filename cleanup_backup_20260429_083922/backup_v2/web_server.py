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
    """获取英雄的推荐装备/符文/分路"""
    build_data = get_champion_build(champ_id)
    if build_data:
        return jsonify({"success": True, "build": build_data})
    return jsonify({"success": False, "error": "无此英雄的build数据"}), 404


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
    from riot_api_client import get_player_full_info

    game_name = request.args.get('name', '')
    tag_line = request.args.get('tag', 'CN1')
    platform = request.args.get('platform', 'kr')

    if not game_name:
        return jsonify({"success": False, "error": "请输入游戏名"})

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

    # 获取前5场详情
    load_champions()
    matches = []
    for mid in match_result["match_ids"][:5]:
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
