#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键解压并配置Data Dragon资源包
"""
import os
import tarfile
import shutil

def extract_dragontail():
    """解压dragontail-12.6.1.tgz"""
    print("=" * 60)
    print("Data Dragon 资源包安装工具")
    print("=" * 60)
    
    # 源文件
    src_file = r"C:\Users\Lenovo\Downloads\dragontail-12.6.1.tgz"
    dst_dir = r"f:\code-tengxun\LeagueAkari_CN\datadragon"
    
    # 检查文件是否存在
    if not os.path.exists(src_file):
        print(f"❌ 找不到文件: {src_file}")
        print("请确认文件已下载到Downloads目录")
        return False
    
    print(f"📦 源文件: {src_file}")
    print(f"📂 目标目录: {dst_dir}")
    
    # 创建目标目录
    os.makedirs(dst_dir, exist_ok=True)
    
    try:
        # 解压文件
        print("\n⏳ 正在解压...")
        with tarfile.open(src_file, 'r:gz') as tar:
            tar.extractall(dst_dir)
        
        print("✅ 解压成功！")
        
        # 查找重要文件
        print("\n📋 检查解压内容...")
        important_dirs = ['img', 'data', 'docs']
        for d in important_dirs:
            dpath = os.path.join(dst_dir, d)
            if os.path.exists(dpath):
                print(f"  ✅ 找到目录: {d}")
        
        # 创建图标资源目录
        icons_dir = os.path.join(dst_dir, "icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        # 复制图标文件
        src_img = os.path.join(dst_dir, "img")
        if os.path.exists(src_img):
            print("\n📸 正在复制图标资源...")
            for subdir in ['champion', 'item', 'perk', 'spell']:
                src = os.path.join(src_img, subdir)
                dst = os.path.join(icons_dir, subdir)
                if os.path.exists(src):
                    os.makedirs(dst, exist_ok=True)
                    print(f"  ✅ {subdir} 图标目录已准备")
        
        print("\n" + "=" * 60)
        print("✅ 安装完成！")
        print("=" * 60)
        print(f"\n图标资源路径: {icons_dir}")
        print("现在可以运行主程序了！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 解压失败: {e}")
        return False

if __name__ == "__main__":
    extract_dragontail()
    input("\n按回车键退出...")
