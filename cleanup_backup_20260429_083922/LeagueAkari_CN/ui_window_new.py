"""
图形界面 - 集成所有4个功能
支持：个人信息、查询他人、英雄榜单、数据更新
"""

import sys
import json
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QTextEdit, QTabWidget, QMessageBox, QProgressBar,
                             QComboBox, QListWidget, QListWidgetItem, QTableWidget,
                             QTableWidgetItem, QHeaderView, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QImage
import requests


class WorkerThread(QThread):
    """工作线程（避免界面卡顿）"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 导入数据爬取模块
        from data_spider import DataSpider
        self.spider = DataSpider()
        
        self.setWindowTitle("LOL数据助手 - 国服版 v1.0")
        self.setMinimumSize(1200, 800)
        
        # 中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel("⚔️ LOL数据助手 - 国服版")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #FF6B00;
                padding: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建4个标签页
        self.create_self_info_tab()      # 功能1
        self.create_search_player_tab()  # 功能2
        self.create_champion_tier_tab()  # 功能3
        self.create_update_tab()         # 功能4
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        print("✅ 主窗口初始化完成")
    
    # ==================== 功能1：个人信息 ====================
    def create_self_info_tab(self):
        """创建个人信息标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 输入区域
        input_group = QGroupBox("查询个人信息")
        input_layout = QHBoxLayout()
        
        input_layout.addWidget(QLabel("游戏名:"))
        self.self_game_name_input = QLineEdit()
        self.self_game_name_input.setPlaceholderText("输入游戏名（如: G2）")
        input_layout.addWidget(self.self_game_name_input)
        
        input_layout.addWidget(QLabel("标签:"))
        self.self_tag_input = QLineEdit("CN")
        self.self_tag_input.setMaximumWidth(100)
        input_layout.addWidget(self.self_tag_input)
        
        btn_search = QPushButton("查询")
        btn_search.clicked.connect(self.search_self_info)
        input_layout.addWidget(btn_search)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 结果显示区域
        self.self_result_text = QTextEdit()
        self.self_result_text.setReadOnly(True)
        self.self_result_text.setPlaceholderText("查询结果将显示在这里...")
        layout.addWidget(self.self_result_text)
        
        self.tab_widget.addTab(tab, "📊 个人信息")
    
    def search_self_info(self):
        """查询个人信息"""
        game_name = self.self_game_name_input.text().strip()
        tag_line = self.self_tag_input.text().strip() or "CN"
        
        if not game_name:
            QMessageBox.warning(self, "警告", "请输入游戏名！")
            return
        
        self.statusBar().showMessage(f"正在查询 {game_name}#{tag_line} 的个人信息...")
        self.self_result_text.clear()
        
        # 使用工作线程
        self.worker = WorkerThread(self.spider.get_self_info, game_name, tag_line)
        self.worker.finished.connect(self.on_self_info_received)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_self_info_received(self, result: dict):
        """接收个人信息查询结果"""
        if result.get("success"):
            data = result.get("data", {})
            
            # 格式化显示
            text = f"""
════════════════════════════════════════
             个人信息
════════════════════════════════════════

【账号信息】
游戏名: {data.get('game_name', 'N/A')}#{data.get('tag_line', 'N/A')}
PUUID: {data.get('puuid', 'N/A')[:20]}...

【召唤师信息】
"""
            summoner_info = data.get("summoner_info", {})
            if summoner_info:
                text += f"""等级: {summoner_info.get('summonerLevel', 'N/A')}
名称: {summoner_info.get('name', 'N/A')}
"""
            
            text += "\n【英雄熟练度TOP5】\n"
            masteries = data.get("champion_masteries", [])
            for idx, mastery in enumerate(masteries[:5], 1):
                text += f"{idx}. 英雄ID: {mastery.get('championId', 'N/A')} - 熟练度: {mastery.get('championPoints', 'N/A')}\n"
            
            text += "\n【最近比赛】\n"
            matches = data.get("recent_matches", [])
            for idx, match in enumerate(matches[:3], 1):
                text += f"{idx}. 比赛ID: {match.get('metadata', {}).get('matchId', 'N/A')[:30]}...\n"
            
            text += "\n════════════════════════════════════════"
            
            self.self_result_text.setText(text)
            self.statusBar().showMessage("查询成功！")
        else:
            error_msg = result.get("error", "未知错误")
            self.self_result_text.setText(f"❌ 查询失败: {error_msg}")
            self.statusBar().showMessage("查询失败")
    
    # ==================== 功能2：查询他人 ====================
    def create_search_player_tab(self):
        """创建查询他人标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 输入区域
        input_group = QGroupBox("查询其他玩家")
        input_layout = QHBoxLayout()
        
        input_layout.addWidget(QLabel("游戏名:"))
        self.search_game_name_input = QLineEdit()
        self.search_game_name_input.setPlaceholderText("输入要查询的游戏名")
        input_layout.addWidget(self.search_game_name_input)
        
        input_layout.addWidget(QLabel("标签:"))
        self.search_tag_input = QLineEdit("CN")
        self.search_tag_input.setMaximumWidth(100)
        input_layout.addWidget(self.search_tag_input)
        
        btn_search = QPushButton("查询")
        btn_search.clicked.connect(self.search_player)
        input_layout.addWidget(btn_search)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 结果显示区域
        self.search_result_text = QTextEdit()
        self.search_result_text.setReadOnly(True)
        self.search_result_text.setPlaceholderText("查询结果将显示在这里...")
        layout.addWidget(self.search_result_text)
        
        self.tab_widget.addTab(tab, "🔍 查询他人")
    
    def search_player(self):
        """查询其他玩家"""
        game_name = self.search_game_name_input.text().strip()
        tag_line = self.search_tag_input.text().strip() or "CN"
        
        if not game_name:
            QMessageBox.warning(self, "警告", "请输入游戏名！")
            return
        
        self.statusBar().showMessage(f"正在查询玩家 {game_name}#{tag_line}...")
        self.search_result_text.clear()
        
        # 使用工作线程
        self.worker2 = WorkerThread(self.spider.search_player, game_name, tag_line)
        self.worker2.finished.connect(self.on_player_info_received)
        self.worker2.error.connect(self.on_error)
        self.worker2.start()
    
    def on_player_info_received(self, result: dict):
        """接收玩家查询结果"""
        if result.get("success"):
            data = result.get("data", {})
            
            # 格式化显示（类似个人信息）
            text = f"""
════════════════════════════════════════
             玩家信息
════════════════════════════════════════

【账号信息】
游戏名: {data.get('game_name', 'N/A')}#{data.get('tag_line', 'N/A')}
PUUID: {data.get('puuid', 'N/A')[:20]}...

【召唤师信息】
"""
            summoner_info = data.get("summoner_info", {})
            if summoner_info:
                text += f"""等级: {summoner_info.get('summonerLevel', 'N/A')}
名称: {summoner_info.get('name', 'N/A')}
"""
            
            text += "\n【英雄熟练度TOP5】\n"
            masteries = data.get("champion_masteries", [])
            for idx, mastery in enumerate(masteries[:5], 1):
                text += f"{idx}. 英雄ID: {mastery.get('championId', 'N/A')} - 熟练度: {mastery.get('championPoints', 'N/A')}\n"
            
            text += "\n════════════════════════════════════════"
            
            self.search_result_text.setText(text)
            self.statusBar().showMessage("查询成功！")
        else:
            error_msg = result.get("error", "未知错误")
            self.search_result_text.setText(f"❌ 查询失败: {error_msg}")
            self.statusBar().showMessage("查询失败")
    
    # ==================== 功能3：英雄榜单 ====================
    def create_champion_tier_tab(self):
        """创建英雄榜单标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 控制区域
        control_group = QGroupBox("英雄榜单")
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("分路:"))
        self.lane_combo = QComboBox()
        self.lane_combo.addItems(["ALL", "TOP", "JUNGLE", "MID", "ADC", "SUPPORT"])
        control_layout.addWidget(self.lane_combo)
        
        btn_refresh = QPushButton("刷新榜单")
        btn_refresh.clicked.connect(self.refresh_champion_tier)
        control_layout.addWidget(btn_refresh)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 榜单表格
        self.tier_table = QTableWidget()
        self.tier_table.setColumnCount(6)
        self.tier_table.setHorizontalHeaderLabels(["排名", "英雄", "等级", "胜率", "选取率", "操作"])
        
        # 设置表格样式
        header = self.tier_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.tier_table)
        
        self.tab_widget.addTab(tab, "🏆 英雄榜单")
    
    def refresh_champion_tier(self):
        """刷新英雄榜单"""
        lane = self.lane_combo.currentText()
        
        self.statusBar().showMessage(f"正在获取 {lane} 分路的英雄榜单...")
        self.tier_table.setRowCount(0)
        
        # 使用工作线程
        self.worker3 = WorkerThread(self.spider.get_champion_tier_list, lane)
        self.worker3.finished.connect(self.on_champion_tier_received)
        self.worker3.error.connect(self.on_error)
        self.worker3.start()
    
    def on_champion_tier_received(self, result: dict):
        """接收英雄榜单数据"""
        if result.get("success"):
            data = result.get("data", [])
            
            self.tier_table.setRowCount(len(data))
            
            for row, hero in enumerate(data):
                # 排名
                self.tier_table.setItem(row, 0, QTableWidgetItem(str(hero.get("rank", ""))))
                
                # 英雄名称
                self.tier_table.setItem(row, 1, QTableWidgetItem(f"{hero.get('hero_name', '')} - {hero.get('hero_title', '')}"))
                
                # 等级
                self.tier_table.setItem(row, 2, QTableWidgetItem(hero.get("tier", "")))
                
                # 胜率
                self.tier_table.setItem(row, 3, QTableWidgetItem(f"{hero.get('win_rate', 0)}%"))
                
                # 选取率
                self.tier_table.setItem(row, 4, QTableWidgetItem(f"{hero.get('pick_rate', 0)}%"))
                
                # 操作按钮
                btn_view = QPushButton("查看出装")
                btn_view.clicked.connect(lambda checked, h=hero: self.view_champion_build(h))
                self.tier_table.setCellWidget(row, 5, btn_view)
            
            self.statusBar().showMessage(f"榜单加载完成！共 {len(data)} 个英雄")
        else:
            error_msg = result.get("error", "未知错误")
            self.statusBar().showMessage(f"获取失败: {error_msg}")
    
    def view_champion_build(self, hero: dict):
        """查看英雄出装和符文"""
        champion_id = hero.get("hero_id")
        
        self.statusBar().showMessage(f"正在获取 {hero.get('hero_name')} 的出装和符文...")
        
        # 使用工作线程
        self.worker4 = WorkerThread(self.spider.get_champion_build, champion_id)
        self.worker4.finished.connect(self.on_champion_build_received)
        self.worker4.error.connect(self.on_error)
        self.worker4.start()
    
    def on_champion_build_received(self, result: dict):
        """接收英雄出装数据"""
        if result.get("success"):
            data = result.get("data", {})
            
            # 显示详情（可以打开新窗口或显示在文本区域）
            text = "【推荐出装】\n"
            items = data.get("items", [])
            for item in items[:6]:
                text += f"- {item.get('name', 'N/A')}\n"
            
            text += "\n【推荐符文】\n"
            runes = data.get("runes", [])
            for rune in runes[:6]:
                text += f"- {rune.get('name', 'N/A')}\n"
            
            QMessageBox.information(self, "出装推荐", text)
            self.statusBar().showMessage("出装数据加载完成！")
        else:
            error_msg = result.get("error", "未知错误")
            self.statusBar().showMessage(f"获取失败: {error_msg}")
    
    # ==================== 功能4：更新数据 ====================
    def create_update_tab(self):
        """创建数据更新标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 更新按钮
        btn_update = QPushButton("🔄 更新所有数据")
        btn_update.setMinimumHeight(50)
        btn_update.clicked.connect(self.update_all_data)
        layout.addWidget(btn_update)
        
        # 进度条
        self.update_progress = QProgressBar()
        self.update_progress.setTextVisible(True)
        layout.addWidget(self.update_progress)
        
        # 更新日志
        self.update_log = QTextEdit()
        self.update_log.setReadOnly(True)
        self.update_log.setPlaceholderText("更新日志将显示在这里...")
        layout.addWidget(self.update_log)
        
        self.tab_widget.addTab(tab, "⚙️ 设置/更新")
    
    def update_all_data(self):
        """更新所有数据"""
        self.statusBar().showMessage("正在更新数据...")
        self.update_log.clear()
        self.update_progress.setValue(0)
        
        # 使用工作线程
        self.worker5 = WorkerThread(self.spider.update_all_data)
        self.worker5.finished.connect(self.on_update_completed)
        self.worker5.error.connect(self.on_error)
        self.worker5.start()
    
    def on_update_completed(self, result: dict):
        """接收更新结果"""
        if result.get("success"):
            details = result.get("details", [])
            
            log_text = "════════════════════════════════════════\n"
            log_text += "             数据更新完成\n"
            log_text += "════════════════════════════════════════\n\n"
            
            for idx, detail in enumerate(details, 1):
                name = detail.get("name", "N/A")
                status = detail.get("status", "N/A")
                count = detail.get("count", 0)
                
                log_text += f"{idx}. {name}: {status} (共 {count} 条)\n"
            
            self.update_log.setText(log_text)
            self.update_progress.setValue(100)
            self.statusBar().showMessage("数据更新完成！")
        else:
            self.update_log.setText("❌ 更新失败")
            self.statusBar().showMessage("更新失败")
    
    # ==================== 错误处理 ====================
    def on_error(self, error_msg: str):
        """处理错误"""
        QMessageBox.critical(self, "错误", f"发生错误:\n{error_msg}")
        self.statusBar().showMessage("发生错误")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
