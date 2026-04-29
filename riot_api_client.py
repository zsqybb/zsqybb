"""
Riot API Client - 国服版
使用 Riot API 获取玩家数据
API端点: asia(账号/比赛), kr/sg2(召唤师/熟练度)
"""
import requests
import time
import logging

logger = logging.getLogger(__name__)

API_KEY = "RGAPI-32e586c5-5391-4738-8b1c-9bbdc86ddd53"

# 区域端点配置
REGIONAL = {
    "asia": "https://asia.api.riotgames.com",
    "americas": "https://americas.api.riotgames.com",
    "europe": "https://europe.api.riotgames.com",
}

PLATFORM = {
    "kr": "https://kr.api.riotgames.com",
    "sg2": "https://sg2.api.riotgames.com",
    "na1": "https://na1.api.riotgames.com",
    "euw1": "https://euw1.api.riotgames.com",
}

# 默认使用KR平台（国服玩家在asia区域注册）
DEFAULT_REGIONAL = "asia"
DEFAULT_PLATFORM = "kr"

# 请求限速
_last_request_time = 0
MIN_INTERVAL = 1.2  # 秒


def _rate_limit():
    """简单的请求限速"""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    _last_request_time = time.time()


def _get(url, params=None):
    """发送GET请求，带限速和错误处理"""
    _rate_limit()
    params = params or {}
    params["api_key"] = API_KEY

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        elif resp.status_code == 404:
            return {"success": False, "error": "未找到数据", "status": 404}
        elif resp.status_code == 401:
            return {"success": False, "error": "API密钥无效或已过期", "status": 401}
        elif resp.status_code == 429:
            return {"success": False, "error": "请求过于频繁，请稍后再试", "status": 429}
        else:
            try:
                msg = resp.json().get("status", {}).get("message", resp.text[:200])
            except Exception:
                msg = resp.text[:200]
            return {"success": False, "error": msg, "status": resp.status_code}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "网络连接失败，请检查网络"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "请求超时，请稍后再试"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_account_by_riot_id(game_name, tag_line, regional=None):
    """
    Account-V1: 通过游戏名+标签获取puuid
    端点: asia.api.riotgames.com
    """
    regional = regional or DEFAULT_REGIONAL
    base = REGIONAL[regional]
    url = f"{base}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    result = _get(url)
    if result["success"]:
        data = result["data"]
        return {
            "success": True,
            "puuid": data.get("puuid", ""),
            "game_name": data.get("gameName", game_name),
            "tag_line": data.get("tagLine", tag_line),
        }
    return result


def get_summoner_by_puuid(puuid, platform=None):
    """
    Summoner-V4: 通过puuid获取召唤师信息（等级、头像、ID）
    端点: kr.api.riotgames.com / sg2.api.riotgames.com
    """
    platform = platform or DEFAULT_PLATFORM
    base = PLATFORM[platform]
    url = f"{base}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    result = _get(url)
    if result["success"]:
        data = result["data"]
        return {
            "success": True,
            "id": data.get("id", ""),
            "account_id": data.get("accountId", ""),
            "puuid": data.get("puuid", puuid),
            "name": data.get("name", ""),
            "profile_icon_id": data.get("profileIconId", 0),
            "revision_date": data.get("revisionDate", 0),
            "summoner_level": data.get("summonerLevel", 0),
        }
    return result


def get_champion_mastery(puuid, champion_id, platform=None):
    """
    Champion-Mastery-V4: 获取指定英雄的熟练度
    champion_id: 英雄ID（阿卡丽=84）
    端点: kr.api.riotgames.com
    """
    platform = platform or DEFAULT_PLATFORM
    base = PLATFORM[platform]
    url = f"{base}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}"
    result = _get(url)
    if result["success"]:
        data = result["data"]
        return {
            "success": True,
            "champion_id": data.get("championId", champion_id),
            "champion_level": data.get("championLevel", 0),
            "champion_points": data.get("championPoints", 0),
            "last_play_time": data.get("lastPlayTime", 0),
            "champion_points_since_last_level": data.get("championPointsSinceLastLevel", 0),
            "champion_points_until_next_level": data.get("championPointsUntilNextLevel", 0),
            "tokens_earned": data.get("tokensEarned", 0),
        }
    return result


def get_all_champion_masteries(puuid, platform=None):
    """
    Champion-Mastery-V4: 获取所有英雄熟练度
    端点: kr.api.riotgames.com
    """
    platform = platform or DEFAULT_PLATFORM
    base = PLATFORM[platform]
    url = f"{base}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
    result = _get(url)
    if result["success"]:
        masteries = []
        for m in result["data"][:20]:  # 只返回前20个
            masteries.append({
                "champion_id": m.get("championId", 0),
                "champion_level": m.get("championLevel", 0),
                "champion_points": m.get("championPoints", 0),
                "last_play_time": m.get("lastPlayTime", 0),
                "tokens_earned": m.get("tokensEarned", 0),
            })
        return {"success": True, "masteries": masteries}
    return result


def get_match_ids(puuid, count=20, regional=None):
    """
    Match-V5: 获取最近比赛ID列表
    端点: asia.api.riotgames.com
    """
    regional = regional or DEFAULT_REGIONAL
    base = REGIONAL[regional]
    url = f"{base}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    result = _get(url, params={"count": count})
    if result["success"]:
        return {"success": True, "match_ids": result["data"]}
    return result


def get_match_detail(match_id, regional=None):
    """
    Match-V5: 获取比赛详情
    端点: asia.api.riotgames.com
    """
    regional = regional or DEFAULT_REGIONAL
    base = REGIONAL[regional]
    url = f"{base}/lol/match/v5/matches/{match_id}"
    result = _get(url)
    if result["success"]:
        data = result["data"]
        info = data.get("info", {})
        metadata = data.get("metadata", {})

        participants = []
        for p in info.get("participants", []):
            participants.append({
                "puuid": p.get("puuid", ""),
                "champion_id": p.get("championId", 0),
                "champion_name": p.get("championName", ""),
                "kills": p.get("kills", 0),
                "deaths": p.get("deaths", 0),
                "assists": p.get("assists", 0),
                "win": p.get("win", False),
                "lane": p.get("lane", ""),
                "role": p.get("individualPosition", ""),
                "summoner_level": p.get("summonerLevel", 0),
                "items": [p.get(f"item{i}", 0) for i in range(6)],
                "total_minions_killed": p.get("totalMinionsKilled", 0),
                "vision_score": p.get("visionScore", 0),
                "gold_earned": p.get("goldEarned", 0),
                "total_damage_dealt": p.get("totalDamageDealtToChampions", 0),
                "game_duration": info.get("gameDuration", 0),
            })

        return {
            "success": True,
            "match_id": match_id,
            "game_mode": info.get("gameMode", ""),
            "game_type": info.get("gameType", ""),
            "game_duration": info.get("gameDuration", 0),
            "game_creation": info.get("gameCreation", 0),
            "participants": participants,
        }
    return result


def get_player_full_info(game_name, tag_line, platform=None):
    """
    一站式查询：获取玩家完整信息
    返回: 账号信息 + 召唤师信息 + 英雄熟练度 + 最近比赛
    """
    platform = platform or DEFAULT_PLATFORM

    # 1. 获取puuid
    account = get_account_by_riot_id(game_name, tag_line)
    if not account.get("success"):
        return account

    puuid = account["puuid"]

    # 2. 获取召唤师信息
    summoner = get_summoner_by_puuid(puuid, platform)
    if not summoner.get("success"):
        # 召唤师不在该平台，尝试其他平台
        for alt_platform in ["sg2", "na1"]:
            if alt_platform == platform:
                continue
            summoner = get_summoner_by_puuid(puuid, alt_platform)
            if summoner.get("success"):
                platform = alt_platform
                break

    # 3. 获取英雄熟练度
    masteries = get_all_champion_masteries(puuid, platform)

    # 4. 获取最近5场比赛
    match_result = get_match_ids(puuid, count=5)
    matches = []
    if match_result.get("success") and match_result.get("match_ids"):
        for mid in match_result["match_ids"][:3]:  # 只查3场详情
            detail = get_match_detail(mid)
            if detail.get("success"):
                matches.append(detail)

    return {
        "success": True,
        "account": account,
        "summoner": summoner if summoner.get("success") else None,
        "masteries": masteries.get("masteries", []) if masteries.get("success") else [],
        "matches": matches,
    }


if __name__ == "__main__":
    # 测试
    print("=== 测试Riot API ===")
    result = get_account_by_riot_id("Hide on bush", "KR1")
    print(f"Account: {result}")

    if result.get("success"):
        puuid = result["puuid"]
        summoner = get_summoner_by_puuid(puuid)
        print(f"Summoner: {summoner}")

        mastery = get_champion_mastery(puuid, 84)
        print(f"Akali Mastery: {mastery}")

        match_ids = get_match_ids(puuid, count=3)
        print(f"Match IDs: {match_ids}")
