"""
完整功能测试脚本 - 测试所有4个功能
"""

import sys
import json
from data_spider import DataSpider

def test_all_features():
    """测试所有4个功能"""
    
    print("=" * 80)
    print("LOL数据助手 - 功能测试")
    print("=" * 80)
    
    # 创建数据爬取器
    spider = DataSpider()
    
    # 测试用的游戏名
    test_game_name = "G2"
    test_tag = "CN"
    
    # ==================== 功能1：个人信息 ====================
    print("\n" + "=" * 80)
    print("功能1：个人信息")
    print("=" * 80)
    
    result1 = spider.get_self_info(test_game_name, test_tag)
    
    if result1.get("success"):
        print("✅ 功能1测试通过！")
        data = result1.get("data", {})
        
        print(f"\n【账号信息】")
        print(f"  游戏名: {data.get('game_name')}#{data.get('tag_line')}")
        print(f"  PUUID: {data.get('puuid')[:30]}...")
        
        print(f"\n【召唤师信息】")
        summoner_info = data.get("summoner_info", {})
        if summoner_info and "error" not in summoner_info:
            print(f"  等级: {summoner_info.get('summonerLevel')}")
            print(f"  名称: {summoner_info.get('name')}")
        
        print(f"\n【英雄熟练度TOP5】")
        masteries = data.get("champion_masteries", [])
        for idx, mastery in enumerate(masteries[:5], 1):
            print(f"  {idx}. 英雄ID: {mastery.get('championId')} - 熟练度: {mastery.get('championPoints')}")
        
        print(f"\n【最近比赛】")
        matches = data.get("recent_matches", [])
        for idx, match in enumerate(matches[:3], 1):
            match_id = match.get("metadata", {}).get("matchId", "N/A")
            print(f"  {idx}. 比赛ID: {match_id[:40]}...")
    else:
        print("❌ 功能1测试失败！")
        print(f"  错误: {result1.get('error')}")
    
    # ==================== 功能2：查询他人 ====================
    print("\n" + "=" * 80)
    print("功能2：查询他人")
    print("=" * 80)
    
    result2 = spider.search_player(test_game_name, test_tag)
    
    if result2.get("success"):
        print("✅ 功能2测试通过！")
        print(f"  查询结果与方法1相同（因为是同一个API）")
    else:
        print("❌ 功能2测试失败！")
        print(f"  错误: {result2.get('error')}")
    
    # ==================== 功能3：英雄榜单 ====================
    print("\n" + "=" * 80)
    print("功能3：英雄榜单")
    print("=" * 80)
    
    result3 = spider.get_champion_tier_list("ALL")
    
    if result3.get("success"):
        print("✅ 功能3测试通过！")
        data = result3.get("data", [])
        print(f"  共获取 {len(data)} 个英雄")
        
        print(f"\n【TOP5英雄】")
        for idx, hero in enumerate(data[:5], 1):
            print(f"  {idx}. {hero.get('hero_name')} - {hero.get('hero_title')}")
            print(f"     胜率: {hero.get('win_rate')}% | 选取率: {hero.get('pick_rate')}% | 等级: {hero.get('tier')}")
    else:
        print("❌ 功能3测试失败！")
        print(f"  错误: {result3.get('error')}")
    
    # 测试获取英雄出装
    print(f"\n【测试：获取英雄出装】")
    if result3.get("success") and len(result3.get("data", [])) > 0:
        first_hero_id = result3["data"][0].get("hero_id")
        build_result = spider.get_champion_build(first_hero_id)
        
        if build_result.get("success"):
            print(f"  ✅ 获取英雄 {first_hero_id} 的出装成功！")
        else:
            print(f"  ❌ 获取出装失败: {build_result.get('error')}")
    
    # ==================== 功能4：更新数据 ====================
    print("\n" + "=" * 80)
    print("功能4：更新数据")
    print("=" * 80)
    
    result4 = spider.update_all_data()
    
    if result4.get("success"):
        print("✅ 功能4测试通过！")
        
        details = result4.get("details", [])
        for idx, detail in enumerate(details, 1):
            name = detail.get("name")
            status = detail.get("status")
            count = detail.get("count", 0)
            print(f"  {idx}. {name}: {status} (共 {count} 条)")
    else:
        print("❌ 功能4测试失败！")
        print(f"  错误: {result4.get('error')}")
    
    # ==================== 总结 ====================
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    success_count = 0
    if result1.get("success"):
        success_count += 1
    if result2.get("success"):
        success_count += 1
    if result3.get("success"):
        success_count += 1
    if result4.get("success"):
        success_count += 1
    
    print(f"\n✅ 成功: {success_count}/4")
    print(f"❌ 失败: {4 - success_count}/4")
    
    if success_count == 4:
        print("\n🎉 所有功能测试通过！程序可以正常使用！")
        print("\n下次可以直接运行: python main_new.py")
    else:
        print("\n⚠️ 部分功能测试失败，请检查错误信息。")
        print("\n可能的原因：")
        print("  1. API密钥无效或过期")
        print("  2. 网络连接问题")
        print("  3. 游戏名或标签错误")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        test_all_features()
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按回车键退出...")
