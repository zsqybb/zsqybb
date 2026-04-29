"""
主程序入口 - 启动LOL数据助手
集成所有4个功能：个人信息、查询他人、英雄榜单、数据更新
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    try:
        print("=" * 80)
        print("LOL数据助手 - 国服版 v1.0")
        print("=" * 80)
        print()
        
        # 导入PyQt6
        print("[1/3] 正在加载界面库...")
        from PyQt6.QtWidgets import QApplication
        print("  ✅ PyQt6 加载成功！")
        
        # 导入主窗口
        print("[2/3] 正在加载主界面...")
        from ui_window_new import MainWindow
        print("  ✅ 主界面加载成功！")
        
        # 创建应用程序
        print("[3/3] 正在启动应用程序...")
        app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        print()
        print("=" * 80)
        print("✅ 程序启动成功！")
        print("=" * 80)
        print()
        print("功能说明：")
        print("  1. 📊 个人信息 - 查询自己的LOL数据")
        print("  2. 🔍 查询他人 - 查询其他玩家的数据")
        print("  3. 🏆 英雄榜单 - 查看英雄排名和出装推荐")
        print("  4. ⚙️ 设置/更新 - 更新本地数据")
        print()
        print("提示：输入游戏名和标签（默认CN）后点击查询即可。")
        print("=" * 80)
        print()
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print()
        print("请确保已安装必要的库：")
        print("  pip install PyQt6 requests")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
