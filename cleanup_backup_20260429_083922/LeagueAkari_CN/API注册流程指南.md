# 🔑 英雄联盟数据API注册流程指南

本指南帮助您注册并配置主流LOL数据API，以获取真实的游戏数据。

---

## 📋 目录

1. [Riot Games官方API](#1-riot-games官方api推荐)
2. [OP.GG API](#2-opgg-api)
3. [Champion.gg API](#3-championgg-api)
4. [腾讯LOL开发者平台](#4-腾讯lol开发者平台)
5. [配置使用](#5-配置使用)

---

## 1. Riot Games官方API ⭐ (推荐)

### 优点
- ✅ **官方权威**：Riot Games官方提供，数据最准确
- ✅ **免费**：个人开发者免费使用
- ✅ **数据全面**：英雄、装备、符文、比赛数据、召唤师信息
- ✅ **更新及时**：版本更新后同步更新

### 注册步骤

#### 步骤1: 注册Riot账号
1. 访问 https://developer.riotgames.com/
2. 点击 **"Register"** 按钮
3. 填写注册信息：
   - Username (用户名)
   - Password (密码)
   - Email (邮箱)
   - Date of Birth (出生日期)
4. 验证邮箱

#### 步骤2: 创建应用
1. 登录后，进入 **"Dashboard"**
2. 点击 **"Register Product"**
3. 选择 **"Personal API Key"**
4. 填写应用信息：
   - Application Name: `LeagueAkari CN` (可自定义)
   - Description: `LOL Data Spider for Chinese Server`
5. 提交后会获得 **API Key** (格式类似: `RGAPI-xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

#### 步骤3: 配置API Key
1. 复制您的API Key
2. 打开 `api_config.json` 文件
3. 修改以下部分：
```json
"riot_api": {
  "enabled": true,
  "api_key": "RGAPI-xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "region": "na1",
  "description": "Riot Games官方API - 最权威的数据源",
  "register_url": "https://developer.riotgames.com/",
  "free_quota": "100 requests/24小时（个人免费版）"
}
```

#### 注意事项
- ⚠️ **免费版限制**: 100 requests/24小时
- 💡 **升级方案**: 如果需要更多请求，可以申请升级到Production Key
- 🔒 **保密**: 不要将API Key泄露给他人
- 🌍 **区域选择**: 
  - 国服: `na1` (Riot未提供中国服务器API，需用外服数据)
  - 推荐: `kr` (韩服), `na1` (北美)

---

## 2. OP.GG API

### 优点
- ✅ **高分段数据**: 提供韩服高分段统计
- ✅ **实时更新**: 数据更新频率高
- ✅ **克制关系**: 包含英雄克制数据

### 注册步骤

#### 步骤1: 访问OP.GG开发者页面
1. 访问 https://op.gg/developer (可能需要VPN)
2. 点击 **"Apply for API Access"**

#### 步骤2: 填写申请表格
- Name (姓名)
- Email (邮箱)
- Purpose (用途): `Personal project - LOL data analysis tool`
- Expected API Calls (预计调用次数): `1000/month`

#### 步骤3: 等待审核
- 审核时间: 3-7个工作日
- 审核通过后会被发送API Key

#### 配置API Key
```json
"opgg_api": {
  "enabled": true,
  "api_key": "YOUR_OPGG_API_KEY",
  "base_url": "https://opgg-api.com",
  "description": "OP.GG数据API - 韩服高分段数据"
}
```

---

## 3. Champion.gg API

### 优点
- ✅ **统计数据**: 提供英雄胜率、选取率等统计
- ✅ **免费**: 基础版免费

### 注册步骤

#### 步骤1: 访问Champion.gg
1. 访问 https://champion.gg/developer
2. 点击 **"Get API Key"**

#### 步骤2: 注册账号
- 使用Google账号登录 或 注册新账号
- 验证邮箱

#### 步骤3: 获取API Key
- 登录后，在Dashboard页面可以看到API Key

#### 配置API Key
```json
"champion_gg": {
  "enabled": true,
  "api_key": "YOUR_CHAMPIONGG_API_KEY",
  "base_url": "https://champion.gg/api",
  "description": "Champion.gg数据API"
}
```

---

## 4. 腾讯LOL开发者平台 (国服数据)

### 优点
- ✅ **国服数据**: 提供中国服务器真实数据
- ✅ **官方支持**: 腾讯官方提供

### 注册步骤

#### 步骤1: 访问腾讯开放平台
1. 访问 https://open.tencent.com/ (腾讯开放平台)
2. 搜索 "英雄联盟" 或 "LOL"

#### 步骤2: 申请内测资格
- 腾讯的LOL API可能不对外公开
- 需要企业资质或特殊申请
- 建议联系腾讯游戏开发者关系部门

#### 备选方案: 使用腾讯CDN公开数据
- 当前代码已支持 `game.gtimg.cn` 公开数据
- 无需注册，但数据可能不及时

---

## 5. 配置使用

### 步骤1: 修改配置文件
编辑 `api_config.json`:
```json
{
  "riot_api": {
    "enabled": true,
    "api_key": "您的API_KEY",
    ...
  },
  ...
}
```

### 步骤2: 测试API连接
运行测试脚本:
```bash
python test_api_connection.py
```

### 步骤3: 使用API获取数据
```python
from data_spider import DataSpider

spider = DataSpider()
spider.load_api_config("api_config.json")

# 获取英雄详情
detail = spider.get_champ_detail("亚索")
print(detail)
```

---

## 🔧 常见问题

### Q1: Riot API免费版不够用怎么办？
**A**: 
1. 申请升级到Production Key (需要说明用途)
2. 使用多个API源组合 (Riot + OP.GG + Champion.gg)
3. 添加本地缓存机制 (当前代码已支持)

### Q2: API Key泄露了怎么办？
**A**: 
1. 立即登录开发者平台
2. 撤销当前API Key
3. 生成新的API Key
4. 更新配置文件

### Q3: 国服数据用什么API？
**A**: 
- Riot API不支持国服，建议使用:
  1. 腾讯CDN公开数据 (当前代码已支持)
  2. 多玩、17173等第三方网站数据
  3. 自己爬取国服官网数据

### Q4: 获取API Key后代码如何修改？
**A**: 
我已经为您修改了 `data_spider.py`，支持从 `api_config.json` 读取配置。
只需填写API Key并启用对应数据源即可。

---

## 📞 技术支持

如果遇到问题，可以:
1. 查看 `server.log` 日志文件
2. 运行 `python debug_fight.py` 调试
3. 联系开发者

---

**最后更新**: 2026-04-28  
**作者**: LeagueAkari CN Team
