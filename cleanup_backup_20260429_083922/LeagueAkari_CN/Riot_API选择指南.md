# Riot API 选择指南

## 📌 重要提示：你可能需要的是 Data Dragon（免费，无需API密钥）

---

## 1️⃣ Riot API 分类

### 🆓 无需API密钥（免费访问）

#### **Data Dragon (DDragon)** - 游戏静态数据
**用途**：获取英雄、装备、符文、召唤师技能等静态数据
**访问方式**：直接HTTP请求，无需注册
**适用场景**：你的项目最需要这个！

**主要接口**：
```
# 英雄列表和详情
https://cdn.communitydragon.org/{version}/cdragon/lolpony/plugin/rcp-be-lol-game-data/global/default/v1/champions.json

# 装备数据
https://cdn.communitydragon.org/{version}/cdragon/lolpony/plugin/rcp-be-lol-game-data/global/default/v1/items.json

# 符文数据
https://cdn.communitydragon.org/{version}/cdragon/lolpony/plugin/rcp-be-lol-game-data/global/default/v1/perks.json

# 召唤师技能
https://cdn.communitydragon.org/{version}/cdragon/lolpony/plugin/rcp-be-lol-game-data/global/default/v1/summoner-spells.json
```

**版本号获取**：
```
https://ddragon.leagueoflegends.com/api/versions.json
```

---

### 🔑 需要API密钥（需注册）

#### **Riot Games API** - 动态游戏数据
**用途**：获取玩家排名、比赛记录、召唤师信息等
**注册地址**：https://developer.riotgames.com/

**主要接口**：
1. **Summoner API** - 召唤师信息
   - `/lol/summoner/v4/summoners/by-name/{summonerName}`
   - 获取召唤师等级、ID等

2. **League API** - 排位信息
   - `/lol/league/v4/entries/by-summoner/{encryptedSummonerId}`
   - 获取排位、胜率等

3. **Match API** - 比赛数据
   - `/lol/match/v5/matches/{matchId}`
   - 获取比赛详情

4. **Spectator API** - 观战数据
   - `/lol/spectator/v4/active-games/by-summoner/{encryptedSummonerId}`
   - 获取当前游戏信息

5. **Champion Mastery API** - 英雄熟练度
   - `/lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}`
   - 获取英雄熟练度

---

## 2️⃣ 你应该选择哪个？

### ✅ 推荐方案：Data Dragon（免费）

根据你的 `data_spider.py`，你需要的是：
- ✅ 英雄列表和数据
- ✅ 装备数据
- ✅ 符文数据
- ✅ 英雄头像

**这些Data Dragon都可以免费提供！**

### 📝 集成示例

```python
import requests

class RiotDataSpider:
    def __init__(self):
        self.base_url = "https://cdn.communitydragon.org"
        self.version = self._get_latest_version()
    
    def _get_latest_version(self):
        """获取最新游戏版本"""
        url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(url, timeout=10)
        versions = response.json()
        return versions[0]  # 第一个是最新版本
    
    def fetch_champions(self):
        """获取英雄列表"""
        url = f"{self.base_url}/{self.version}/cdragon/lolpony/plugin/rcp-be-lol-game-data/global/default/v1/champions.json"
        response = requests.get(url, timeout=10)
        return response.json()
    
    def fetch_items(self):
        """获取装备列表"""
        url = f"{self.base_url}/{self.version}/cdragon/lolpony/plugin/rcp-be-lol-game-data/global/default/v1/items.json"
        response = requests.get(url, timeout=10)
        return response.json()
```

---

## 3️⃣ API密钥申请流程（如果需要）

### 步骤1：注册账号
1. 访问 https://developer.riotgames.com/
2. 点击 "Sign Up" 注册
3. 验证邮箱

### 步骤2：创建应用
1. 登录后进入 Dashboard
2. 点击 "Register Product"
3. 选择 "Personal API Key"
4. 填写应用信息：
   - Application Name: 你的应用名
   - Description: 应用描述
   - OAuth2 Callback URL: `https://localhost` (开发用)

### 步骤3：获取API密钥
1. 创建后会显示 "API Key"
2. 格式类似：`RGAPI-xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
3. **注意**：API密钥有请求限制（20请求/秒，100请求/2分钟）

### 步骤4：使用API密钥
```python
headers = {
    "X-Riot-Token": "RGAPI-xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}

response = requests.get(
    "https://jp1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Hide on bush",
    headers=headers
)
```

---

## 4️⃣ 区域选择（重要！）

Riot API按区域划分，你需要选择正确的区域：

| 区域代码 | 覆盖服务器 | API地址 |
|---------|-----------|---------|
| **JP1** | 日服、韩服 | jp1.api.riotgames.com |
| **KR** | 韩服 | kr.api.riotgames.com |
| **NA1** | 北美 | na1.api.riotgames.com |
| **EUW1** | 西欧 | euw1.api.riotgames.com |
| **EUN1** | 北欧东欧 | eun1.api.riotgames.com |
| **RU** | 俄服 | ru.api.riotgames.com |
| **BR1** | 巴西 | br1.api.riotgames.com |
| **LA1** | 拉美北 | la1.api.riotgames.com |
| **LA2** | 拉美南 | la2.api.riotgames.com |
| **OC1** | 大洋洲 | oc1.api.riotgames.com |
| **TR1** | 土耳其 | tr1.api.riotgames.com |
| **SG2** | 新马服 | sg2.api.riotgames.com |
| **TW2** | 台服 | tw2.api.riotgames.com |
| **VN2** | 越服 | vn2.api.riotgames.com |

**⚠️ 注意**：国服（腾讯代理）不使用Riot API，而是使用腾讯自己的接口！

---

## 5️⃣ 推荐方案对比

### 方案A：Data Dragon（推荐）✅
**优点**：
- ✅ 完全免费
- ✅ 无需注册
- ✅ 无需API密钥
- ✅ 数据全面（英雄、装备、符文等）
- ✅ 官方维护，更新及时

**缺点**：
- ❌ 只有静态数据（无排位、比赛等动态数据）

**适用**：你需要英雄/装备/符文数据 → **选这个！**

---

### 方案B：Riot API（需注册）
**优点**：
- ✅ 动态数据（排位、比赛、召唤师信息）
- ✅ 官方API，数据准确

**缺点**：
- ❌ 需要注册和API密钥
- ❌ 有请求频率限制
- ❌ 不包含国服数据

**适用**：你需要玩家数据、排位信息 → 选这个

---

## 6️⃣ 快速决策表

| 你需要的数据 | 推荐API | 需要密钥？ |
|------------|---------|----------|
| 英雄列表/详情 | Data Dragon | ❌ 不需要 |
| 装备数据 | Data Dragon | ❌ 不需要 |
| 符文数据 | Data Dragon | ❌ 不需要 |
| 英雄头像 | Data Dragon | ❌ 不需要 |
| 召唤师排位 | Riot API - League | ✅ 需要 |
| 比赛记录 | Riot API - Match | ✅ 需要 |
| 英雄熟练度 | Riot API - Champion Mastery | ✅ 需要 |
| 当前游戏信息 | Riot API - Spectator | ✅ 需要 |

---

## 7️⃣ 下一步行动

### 如果你只需要英雄/装备/符文数据：
1. ✅ 直接使用 Data Dragon
2. ✅ 参考我上面提供的集成示例
3. ✅ 无需注册，立刻可用

### 如果你需要玩家排位/比赛数据：
1. 📝 访问 https://developer.riotgames.com/
2. 📝 注册账号并创建应用
3. 📝 获取API密钥
4. 📝 选择对应区域（日服JP1、韩服KR等）

---

## 📞 需要帮助？

告诉我：
1. 你需要什么类型的数据？（英雄/装备/排位/比赛等）
2. 你是否有API密钥？
3. 你想查询哪个服务器的数据？

我可以为你提供具体的代码示例！
