#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Dragon资源包安装脚本
解压并配置dragontail-12.6.1.tgz中的所有图标资源
"""

import os
import tarfile
import shutil
from pathlib import Path

def extract_datadragon():
    """解压Data Dragon资源包"""
    download_path = r"C:\Users\Lenovo\Downloads\dragontail-12.6.1.tgz"
    extract_to = r"f:\code-tengxun\LeagueAkari_CN\datadragon"
    
    print("=" * 60)
    print("Data Dragon 资源包安装")
    print("=" * 60)
    
    # 检查源文件
    if not os.path.exists(download_path):
        print(f"❌ 找不到文件: {download_path}")
        print("请确保文件已下载到Downloads目录")
        return False
    
    print(f"📦 源文件: {download_path}")
    print(f"📂 解压到: {extract_to}")
    
    # 创建目标目录
    os.makedirs(extract_to, exist_ok=True)
    
    try:
        # 解压tar.gz文件
        print("\n⏳ 正在解压...")
        with tarfile.open(download_path, 'r:gz') as tar:
            tar.extractall(extract_to)
        
        print("✅ 解压成功！")
        
        # 查找并复制图标文件到正确位置
        print("\n⏳ 正在配置图标资源...")
        
        # 查找解压后的目录结构
        for root, dirs, files in os.walk(extract_to):
            for file in files:
                if file.endswith(('.png', '.jpg', '.webp')):
                    rel_path = os.path.relpath(os.path.join(root, file), extract_to)
                    print(f"  找到图标: {rel_path}")
        
        # 创建图标资源目录
        icons_dir = os.path.join(extract_to, "icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        # 复制英雄图标
        champion_src = os.path.join(extract_to, "img", "champion")
        champion_dst = os.path.join(icons_dir, "champions")
        if os.path.exists(champion_src):
            os.makedirs(champion_dst, exist_ok=True)
            print(f"✅ 英雄图标目录: {champion_dst}")
        
        # 复制装备图标
        item_src = os.path.join(extract_to, "img", "item")
        item_dst = os.path.join(icons_dir, "items")
        if os.path.exists(item_src):
            os.makedirs(item_dst, exist_ok=True)
            print(f"✅ 装备图标目录: {item_dst}")
        
        # 复制符文图标
        rune_src = os.path.join(extract_to, "img", "perk")
        rune_dst = os.path.join(icons_dir, "runes")
        if os.path.exists(rune_src):
            os.makedirs(rune_dst, exist_ok=True)
            print(f"✅ 符文图标目录: {rune_dst}")
        
        # 复制召唤师技能图标
        summoner_src = os.path.join(extract_to, "img", "spell")
        summoner_dst = os.path.join(icons_dir, "summoner")
        if os.path.exists(summoner_src):
            os.makedirs(summoner_dst, exist_ok=True)
            print(f"✅ 召唤师技能图标目录: {summoner_dst}")
        
        print("\n" + "=" * 60)
        print("✅ Data Dragon 资源配置完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 解压失败: {e}")
        return False

if __name__ == "__main__":
    extract_datadragon()
    input("\n按回车键退出...")
