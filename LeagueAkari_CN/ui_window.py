#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
界面模块 - 英雄联盟深蓝黑+金色电竞风格
特点:
  1. LOL客户端配色: 深蓝黑底 + 金色强调
  2. 统一控件样式: 圆角卡片、hover高亮、金色渐变按钮
  3. 加载状态: 骨架屏 + 动画点 + 友好提示
  4. 网络错误: 独立ErrorCard + 重试按钮
  5. 对局页: LCU加载动画 + 重新连接按钮
  6. 英雄数据页: 本地缓存优先提示 + 刷新缓存按钮
  7. mock数据不展示，显示"找不到"卡片
  8. 自定义标题栏 + 状态指示灯 + 金色分割线
"""
import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QTabWidget,
    QGroupBox, QCheckBox, QSpinBox, QComboBox, QMessageBox,
    QSystemTrayIcon, QMenu, QApplication, QStyle,
    QCompleter, QSizePolicy, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QStringListModel, QThread, pyqtSlot,
    QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
    QLinearGradient, QBrush, QPen, QFontMetrics
)

# ==================== 色彩体系 ====================
C_BG            = "#010a13"
C_BG_SURFACE    = "#0a1428"
C_BG_ELEVATED   = "#091428"
C_BG_INPUT      = "#0a1428"

C_BORDER        = "#1e3a5f"
C_BORDER_FOCUS  = "#c89b3c"
C_BORDER_HOVER  = "#463714"

C_TEXT          = "#a09b8c"
C_TEXT_BRIGHT   = "#f0e6d2"
C_TEXT_DIM      = "#5b5a56"
C_TEXT_GOLD     = "#c89b3c"

C_GOLD          = "#c89b3c"
C_GOLD_LIGHT    = "#f0e6d2"
C_GOLD_DARK     = "#463714"
C_BLUE          = "#0ac8b9"
C_RED           = "#e84057"
C_GREEN         = "#0ac8b9"
C_ORANGE        = "#e97451"
C_YELLOW        = "#c8a82c"

# ==================== 全局样式表 ====================
GLOBAL_QSS = f"""
QMainWindow {{
    background-color: {C_BG};
}}
QLabel {{
    color: {C_TEXT};
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}}
QGroupBox {{
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 14px 14px 14px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: {C_GOLD};
    font-weight: bold;
    font-size: 13px;
}}
QPushButton {{
    background-color: {C_BG_ELEVATED};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 7px 18px;
    color: {C_TEXT_BRIGHT};
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 13px;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: {C_GOLD_DARK};
    border-color: {C_GOLD};
    color: {C_GOLD_LIGHT};
}}
QPushButton:pressed {{
    background-color: {C_BG};
    color: {C_TEXT};
}}
QPushButton#goldBtn {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #c89b3c, stop:1 #9e7a28);
    border: 1px solid #c89b3c;
    color: #010a13;
    font-weight: bold;
}}
QPushButton#goldBtn:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ddb65e, stop:1 #c89b3c);
}}
QPushButton#goldBtn:pressed {{
    background: #9e7a28;
}}
QPushButton#reconnectBtn {{
    background: transparent;
    border: 1px solid {C_ORANGE};
    border-radius: 4px;
    padding: 5px 14px;
    color: {C_ORANGE};
    font-size: 12px;
}}
QPushButton#reconnectBtn:hover {{
    background-color: #3a1a0a;
    color: #ffaa88;
}}
QPushButton#refreshBtn {{
    background: transparent;
    border: 1px solid {C_BLUE};
    border-radius: 4px;
    padding: 5px 14px;
    color: {C_BLUE};
    font-size: 12px;
}}
QPushButton#refreshBtn:hover {{
    background-color: #0a2a28;
    color: #44eedd;
}}
QComboBox {{
    background-color: {C_BG_INPUT};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 7px 12px;
    color: {C_TEXT_BRIGHT};
    font-size: 13px;
    min-height: 22px;
}}
QComboBox:focus {{
    border-color: {C_GOLD};
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {C_GOLD};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {C_BG_SURFACE};
    border: 1px solid {C_GOLD};
    color: {C_TEXT_BRIGHT};
    selection-background-color: {C_GOLD_DARK};
    selection-color: {C_GOLD_LIGHT};
    outline: none;
    padding: 4px;
}}
QLineEdit {{
    background-color: {C_BG_INPUT};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 7px 12px;
    color: {C_TEXT_BRIGHT};
    font-size: 13px;
}}
QLineEdit:focus {{
    border-color: {C_GOLD};
}}
QSpinBox {{
    background-color: {C_BG_INPUT};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 7px 12px;
    color: {C_TEXT_BRIGHT};
}}
QCheckBox {{
    color: {C_TEXT};
    font-size: 13px;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px; height: 18px;
    border-radius: 3px;
    border: 1px solid {C_BORDER};
    background-color: {C_BG_INPUT};
}}
QCheckBox::indicator:checked {{
    background-color: {C_GOLD};
    border-color: {C_GOLD};
}}
QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollBar:vertical {{
    background-color: {C_BG};
    width: 5px;
    border-radius: 2px;
}}
QScrollBar::handle:vertical {{
    background-color: {C_GOLD_DARK};
    border-radius: 2px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {C_GOLD};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QTabWidget::pane {{
    border: none;
    background-color: transparent;
    top: -1px;
}}
QTabBar::tab {{
    background-color: transparent;
    color: {C_TEXT_DIM};
    padding: 10px 24px;
    margin-right: 0;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
QTabBar::tab:selected {{
    color: {C_GOLD};
    border-bottom: 2px solid {C_GOLD};
}}
QTabBar::tab:hover:!selected {{
    color: {C_TEXT};
    border-bottom: 2px solid {C_GOLD_DARK};
}}
"""


# ==================== 数据加载线程 ====================
class HeroDataWorker(QThread):
    """后台英雄数据加载线程"""
    finished = pyqtSignal(str, dict, bool)  # hero_name, data, is_refresh

    def __init__(self, spider, hero_name, force_refresh=False):
        super().__init__()
        self.spider = spider
        self.hero_name = hero_name
        self.force_refresh = force_refresh

    def run(self):
        try:
            data = self.spider.search_hero_data(
                self.hero_name, force_refresh=self.force_refresh
            )
            self.finished.emit(self.hero_name, data or {}, self.force_refresh)
        except Exception:
            self.finished.emit(self.hero_name, {}, self.force_refresh)


# ==================== 自定义组件 ====================

class StatusDot(QLabel):
    """状态指示灯"""
    def __init__(self, color=C_RED, size=8):
        super().__init__()
        self.setFixedSize(size, size)
        self._color = color
        self._apply()

    def set_color(self, color):
        self._color = color
        self._apply()

    def _apply(self):
        self.setStyleSheet(f"""
            background-color: {self._color};
            border-radius: {self.width()//2}px;
        """)


class GoldDivider(QFrame):
    """金色分割线"""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(1)
        self.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.2 {C_GOLD_DARK},
                stop:0.5 {C_GOLD}, stop:0.8 {C_GOLD_DARK},
                stop:1 transparent);
        """)


class LoLCard(QFrame):
    """LoL风格卡片"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_BG_SURFACE};
                border: 1px solid {C_BORDER};
                border-radius: 6px;
                padding: 2px;
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 14)
        self._layout.setSpacing(8)
        if title:
            title_frame = QHBoxLayout()
            title_lbl = QLabel(title.upper())
            title_lbl.setStyleSheet(f"""
                color: {C_GOLD};
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 2px;
                border: none;
                padding: 0;
                margin: 0;
            """)
            title_frame.addWidget(title_lbl)
            title_frame.addStretch()
            self._layout.addLayout(title_frame)
            self._layout.addWidget(GoldDivider())

    def add_widget(self, w):
        self._layout.addWidget(w)

    def add_layout(self, l):
        self._layout.addLayout(l)

    def add_stretch(self):
        self._layout.addStretch()


class LoadingPlaceholder(QFrame):
    """加载中占位 + 动画点"""
    def __init__(self, text="加载中", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: transparent; border: none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._base_text = text
        self._label = QLabel(text)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet(f"""
            color: {C_GOLD};
            font-size: 14px;
            border: none;
            padding: 30px 20px 4px 20px;
        """)
        layout.addWidget(self._label)

        self._hint = QLabel("正在读取本地缓存或请求数据...")
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint.setStyleSheet(f"""
            color: {C_TEXT_DIM};
            font-size: 11px;
            border: none;
            padding: 0 20px 30px 20px;
        """)
        layout.addWidget(self._hint)

        self._dots = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(350)

    def _animate(self):
        self._dots = (self._dots + 1) % 4
        self._label.setText(self._base_text + '.' * self._dots)

    def stop(self):
        self._timer.stop()


class LCUConnectingWidget(QFrame):
    """LCU连接中动画"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: transparent; border: none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel("正在连接LCU...")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet(f"""
            color: {C_YELLOW};
            font-size: 13px;
            border: none;
            padding: 20px;
        """)
        layout.addWidget(self._label)

        self._dots = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(400)

    def _animate(self):
        self._dots = (self._dots + 1) % 4
        self._label.setText("正在连接LCU" + '.' * self._dots)

    def stop(self):
        self._timer.stop()
        self._label.setText("")


class PlayerCard(QFrame):
    """玩家信息卡片"""
    def __init__(self, name, champion, rank, spells, is_ally=True, parent=None):
        super().__init__(parent)
        accent = C_GREEN if is_ally else C_RED
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_BG_SURFACE};
                border-left: 3px solid {accent};
                border-top: 1px solid {C_BORDER};
                border-right: 1px solid {C_BORDER};
                border-bottom: 1px solid {C_BORDER};
                border-radius: 4px;
                padding: 1px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        avatar = QLabel("⚔")
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {C_BG};
            border: 1px solid {C_BORDER};
            border-radius: 16px;
            font-size: 15px;
            color: {accent};
        """)

        info = QVBoxLayout()
        info.setSpacing(1)
        n = QLabel(name)
        n.setStyleSheet(f"color: {C_TEXT_BRIGHT}; font-weight: bold; font-size: 13px; border: none;")
        c = QLabel(champion)
        c.setStyleSheet(f"color: {C_GOLD}; font-size: 12px; border: none;")
        d = QLabel(f"{rank}  ·  {spells}")
        d.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")
        info.addWidget(n)
        info.addWidget(c)
        info.addWidget(d)
        layout.addWidget(avatar)
        layout.addLayout(info, 1)


class CounterRow(QFrame):
    """克制关系行"""
    def __init__(self, name, win_rate, reason="", is_counter=True, parent=None):
        super().__init__(parent)
        color = C_GREEN if not is_counter else C_RED
        arrow = "▲" if not is_counter else "▼"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_BG};
                border: 1px solid {C_BORDER};
                border-radius: 3px;
                padding: 1px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        a = QLabel(arrow)
        a.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold; border: none;")
        a.setFixedWidth(16)
        n = QLabel(name)
        n.setStyleSheet(f"color: {C_TEXT_BRIGHT}; font-size: 12px; font-weight: bold; border: none;")
        r = QLabel(f"{win_rate}%")
        r.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold; border: none;")
        re = QLabel(reason)
        re.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")

        layout.addWidget(a)
        layout.addWidget(n)
        layout.addStretch()
        layout.addWidget(r)
        layout.addWidget(re)


class NotFoundCard(QFrame):
    """找不到数据卡片"""
    def __init__(self, hero_name, hint="请检查网络连接或稍后重试", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_BG_SURFACE};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
                padding: 2px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)

        icon = QLabel("◈")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"color: {C_GOLD_DARK}; font-size: 36px; border: none;")

        title = QLabel(f"找不到 {hero_name} 的真实数据")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet(f"color: {C_TEXT_BRIGHT}; font-size: 15px; font-weight: bold; border: none;")

        h = QLabel(hint)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.setWordWrap(True)
        h.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 12px; border: none;")

        layout.addWidget(icon)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addSpacing(4)
        layout.addWidget(h)


class CachedDataBanner(QFrame):
    """本地缓存数据提示条"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a2a10;
                border: 1px solid #3a5a20;
                border-radius: 4px;
                padding: 2px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(6)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {C_YELLOW}; font-size: 10px; border: none;")
        text = QLabel("当前显示本地缓存数据（网络请求失败，已降级到缓存）")
        text.setStyleSheet(f"color: {C_YELLOW}; font-size: 11px; border: none;")
        layout.addWidget(dot)
        layout.addWidget(text, 1)


# ==================== 主窗口 ====================

class MainWindow(QMainWindow):
    game_status_changed = pyqtSignal(bool, bool, str)
    lcu_status_changed = pyqtSignal(bool, str)

    def __init__(self, monitor, lcu_client, spider, config):
        super().__init__()
        self.monitor = monitor
        self.lcu_client = lcu_client
        self.spider = spider
        self.config = config

        self.always_on_top = config.getboolean('UI', 'always_on_top', fallback=True)
        self.refresh_interval = config.getint('UI', 'refresh_interval', fallback=3)
        self.window_width = config.getint('UI', 'width', fallback=480)
        self.window_height = config.getint('UI', 'height', fallback=720)

        self.hero_list = self._load_hero_list()
        self._data_worker = None
        self._loading_widget = None
        self._current_hero = ""

        self.init_ui()

        self.game_status_changed.connect(self._update_game_status_ui)
        self.lcu_status_changed.connect(self._update_lcu_status_ui)
        self.monitor.register_callback(self.update_game_status)

        self._create_tray()

    def _load_hero_list(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static_data', 'hero_list.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    # ========== UI 初始化 ==========

    def init_ui(self):
        self.setWindowTitle("LeagueAkari 国服复刻助手")
        self.setGeometry(100, 100, self.window_width, self.window_height)
        self.setMinimumSize(440, 620)

        if self.always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.setStyleSheet(GLOBAL_QSS)
        self._set_palette()

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_title_bar())
        root.addWidget(GoldDivider())
        root.addWidget(self._build_status_bar())
        root.addWidget(GoldDivider())

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self._build_game_tab()
        self._build_hero_tab()
        self._build_settings_tab()
        root.addWidget(self.tabs, 1)

    def _set_palette(self):
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(C_BG))
        p.setColor(QPalette.ColorRole.WindowText, QColor(C_TEXT))
        p.setColor(QPalette.ColorRole.Base, QColor(C_BG_INPUT))
        p.setColor(QPalette.ColorRole.Text, QColor(C_TEXT_BRIGHT))
        p.setColor(QPalette.ColorRole.Button, QColor(C_BG_SURFACE))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(C_TEXT_BRIGHT))
        p.setColor(QPalette.ColorRole.Highlight, QColor(C_GOLD))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor(C_BG))
        self.setPalette(p)

    # ========== 标题栏 ==========

    def _build_title_bar(self):
        frame = QFrame()
        frame.setFixedHeight(44)
        frame.setStyleSheet(f"background-color: {C_BG}; border: none;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 0, 10, 0)
        layout.setSpacing(6)

        title = QLabel("LEAGUEAKARI")
        title.setStyleSheet(f"""
            color: {C_GOLD};
            font-size: 15px;
            font-weight: bold;
            letter-spacing: 3px;
            border: none;
        """)
        sub = QLabel("国服")
        sub.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addStretch()

        self.btn_top = QPushButton("📌")
        self.btn_top.setFixedSize(30, 30)
        self.btn_top.setCheckable(True)
        self.btn_top.setChecked(self.always_on_top)
        self.btn_top.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; font-size: 14px; color: {C_TEXT_DIM};
            }}
            QPushButton:checked {{ color: {C_GOLD}; }}
            QPushButton:hover {{ background-color: {C_GOLD_DARK}; border-radius: 4px; }}
        """)
        self.btn_top.toggled.connect(self.toggle_always_on_top)

        btn_min = QPushButton("─")
        btn_min.setFixedSize(30, 30)
        btn_min.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; color: {C_TEXT_DIM}; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {C_GOLD_DARK}; border-radius: 4px; color: {C_TEXT}; }}
        """)
        btn_min.clicked.connect(self.showMinimized)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; color: {C_TEXT_DIM}; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {C_RED}; border-radius: 4px; color: #fff; }}
        """)
        btn_close.clicked.connect(self.close)

        layout.addWidget(self.btn_top)
        layout.addWidget(btn_min)
        layout.addWidget(btn_close)
        return frame

    # ========== 状态栏 ==========

    def _build_status_bar(self):
        frame = QFrame()
        frame.setFixedHeight(34)
        frame.setStyleSheet(f"background-color: {C_BG}; border: none;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        self.game_dot = StatusDot(C_RED, 7)
        self.game_text = QLabel("游戏未运行")
        self.game_text.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")

        self.lcu_dot = StatusDot(C_RED, 7)
        self.lcu_text = QLabel("LCU未连接")
        self.lcu_text.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")

        self.mode_text = QLabel("")
        self.mode_text.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")

        layout.addWidget(self.game_dot)
        layout.addWidget(self.game_text)
        layout.addSpacing(6)
        layout.addWidget(self.lcu_dot)
        layout.addWidget(self.lcu_text)
        layout.addStretch()
        layout.addWidget(self.mode_text)
        return frame

    # ========== 对局标签页 ==========

    def _build_game_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # LCU连接状态卡
        self.lcu_status_card = LoLCard("LCU 连接")
        lcu_row = QHBoxLayout()
        lcu_row.setSpacing(10)

        self.lcu_status_label = QLabel("未连接")
        self.lcu_status_label.setStyleSheet(f"""
            color: {C_RED}; font-size: 13px; font-weight: bold; border: none;
        """)

        self.lcu_detail_label = QLabel("请启动英雄联盟客户端")
        self.lcu_detail_label.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")

        self.btn_reconnect = QPushButton("重新连接")
        self.btn_reconnect.setObjectName("reconnectBtn")
        self.btn_reconnect.clicked.connect(self._reconnect_lcu)

        lcu_row.addWidget(self.lcu_status_label, 1)
        lcu_row.addWidget(self.lcu_detail_label, 1)
        lcu_row.addWidget(self.btn_reconnect)
        self.lcu_status_card.add_layout(lcu_row)
        layout.addWidget(self.lcu_status_card)

        # 对局信息卡
        self.game_card = LoLCard("当前对局")
        self.game_info_label = QLabel("未检测到对局")
        self.game_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_info_label.setStyleSheet(f"color: {C_TEXT_DIM}; padding: 30px; font-size: 13px; border: none;")
        self.game_card.add_widget(self.game_info_label)
        layout.addWidget(self.game_card)

        self.players_scroll = QScrollArea()
        self.players_scroll.setWidgetResizable(True)
        self.players_widget = QWidget()
        self.players_layout = QVBoxLayout(self.players_widget)
        self.players_layout.setSpacing(5)
        self.players_layout.setContentsMargins(0, 0, 0, 0)
        self.players_scroll.setWidget(self.players_widget)
        layout.addWidget(self.players_scroll, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.btn_refresh = QPushButton("刷新对局")
        self.btn_refresh.setObjectName("goldBtn")
        self.btn_refresh.clicked.connect(self.refresh_game_data)
        self.btn_auto = QCheckBox("自动刷新")
        self.btn_auto.setChecked(True)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_auto)
        layout.addLayout(btn_row)

        self.tabs.addTab(tab, "对局")

    # ========== 英雄数据标签页 ==========

    def _build_hero_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # 搜索栏
        search_card = LoLCard()
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self.hero_combo = QComboBox()
        self.hero_combo.setEditable(True)
        self.hero_combo.setPlaceholderText("搜索英雄...")
        self.hero_combo.setMinimumHeight(34)
        le = self.hero_combo.lineEdit()
        if le:
            le.setPlaceholderText("搜索英雄...")

        self.btn_search = QPushButton("搜索")
        self.btn_search.setObjectName("goldBtn")
        self.btn_search.setMinimumHeight(34)
        self.btn_search.clicked.connect(self._search_hero)

        self.btn_refresh_cache = QPushButton("刷新缓存")
        self.btn_refresh_cache.setObjectName("refreshBtn")
        self.btn_refresh_cache.setMinimumHeight(34)
        self.btn_refresh_cache.setToolTip("强制重新从网络获取数据，跳过本地缓存")
        self.btn_refresh_cache.clicked.connect(self._refresh_hero_cache)

        search_row.addWidget(self.hero_combo, 1)
        search_row.addWidget(self.btn_search)
        search_row.addWidget(self.btn_refresh_cache)
        search_card.add_layout(search_row)
        layout.addWidget(search_card)

        self._populate_hero_combo()

        # 数据展示区
        self.hero_scroll = QScrollArea()
        self.hero_scroll.setWidgetResizable(True)
        self.hero_widget = QWidget()
        self.hero_layout = QVBoxLayout(self.hero_widget)
        self.hero_layout.setSpacing(8)
        self.hero_layout.setContentsMargins(0, 0, 0, 0)

        hint = QLabel("搜索英雄查看数据")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(f"color: {C_TEXT_DIM}; padding: 50px; font-size: 14px; border: none;")
        self.hero_layout.addWidget(hint)

        self.hero_scroll.setWidget(self.hero_widget)
        layout.addWidget(self.hero_scroll, 1)

        self.tabs.addTab(tab, "英雄数据")

    # ========== 设置标签页 ==========

    def _build_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # 界面设置
        ui_card = LoLCard("界面设置")
        top_cb = QCheckBox("窗口置顶")
        top_cb.setChecked(self.always_on_top)
        top_cb.toggled.connect(self.toggle_always_on_top)
        ui_card.add_widget(top_cb)

        row = QHBoxLayout()
        row.addWidget(QLabel("刷新间隔:"))
        spin = QSpinBox()
        spin.setRange(1, 30)
        spin.setValue(self.refresh_interval)
        spin.setSuffix(" 秒")
        spin.valueChanged.connect(self.change_refresh_interval)
        row.addWidget(spin)
        row.addStretch()
        ui_card.add_layout(row)
        layout.addWidget(ui_card)

        # 数据设置
        data_card = LoLCard("数据设置")
        data_card.add_widget(QCheckBox("启用本地缓存"))

        cache_hint = QLabel("本地缓存可减少网络请求，无网络时也能查看已爬取数据")
        cache_hint.setWordWrap(True)
        cache_hint.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")
        data_card.add_widget(cache_hint)

        btn_clear = QPushButton("清除缓存")
        btn_clear.setObjectName("reconnectBtn")
        btn_clear.clicked.connect(self.clear_cache)
        data_card.add_widget(btn_clear)

        btn_update = QPushButton("更新全部英雄数据")
        btn_update.setObjectName("goldBtn")
        btn_update.clicked.connect(self.update_all_hero_data)
        data_card.add_widget(btn_update)
        layout.addWidget(data_card)

        # LCU设置
        lcu_card = LoLCard("LCU 连接")
        admin_text = "是" if self.lcu_client.is_admin else "否"
        admin_color = C_GREEN if self.lcu_client.is_admin else C_ORANGE
        admin_lbl = QLabel(f"管理员权限: {admin_text}")
        admin_lbl.setStyleSheet(f"color: {admin_color}; font-size: 12px; border: none;")
        lcu_card.add_widget(admin_lbl)

        if not self.lcu_client.is_admin:
            hint = QLabel("提示: 以管理员身份运行可更稳定地读取lockfile")
            hint.setWordWrap(True)
            hint.setStyleSheet(f"color: {C_ORANGE}; font-size: 11px; border: none;")
            lcu_card.add_widget(hint)

        btn_lcu = QPushButton("强制重连LCU")
        btn_lcu.setObjectName("reconnectBtn")
        btn_lcu.clicked.connect(self._reconnect_lcu)
        lcu_card.add_widget(btn_lcu)
        layout.addWidget(lcu_card)

        # 关于
        about_card = LoLCard("关于")
        txt = QLabel(
            "LeagueAkari 国服复刻助手 v2.0\n\n"
            "数据来源: OP.GG 公开数据 + 本地缓存\n"
            "安全声明: 仅读取本地 LCU 接口\n"
            "不修改游戏数据 · 不违反用户协议\n\n"
            "本地缓存优先: 无网络也可查看已有数据\n"
            "刷新缓存: 强制重新从网络获取最新数据\n\n"
            "仅供学习交流使用"
        )
        txt.setStyleSheet(f"color: {C_TEXT_DIM}; line-height: 1.5; border: none;")
        txt.setWordWrap(True)
        about_card.add_widget(txt)
        layout.addWidget(about_card)

        layout.addStretch()
        self.tabs.addTab(tab, "设置")

    # ========== 系统托盘 ==========

    def _create_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self)
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {C_BG_SURFACE};
                border: 1px solid {C_BORDER};
                color: {C_TEXT_BRIGHT};
                padding: 4px;
            }}
            QMenu::item:selected {{
                background-color: {C_GOLD_DARK};
                color: {C_GOLD_LIGHT};
            }}
        """)
        show_act = menu.addAction("显示主窗口")
        show_act.triggered.connect(self._show_normal)
        menu.addSeparator()
        exit_act = menu.addAction("退出")
        exit_act.triggered.connect(QApplication.quit)
        self.tray.setContextMenu(menu)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray.setIcon(icon)
        self.tray.activated.connect(
            lambda r: self._show_normal() if r == QSystemTrayIcon.ActivationReason.Trigger else None
        )
        self.tray.show()

    def _show_normal(self):
        self.show()
        self.activateWindow()
        self.raise_()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage(
            "LeagueAkari", "已最小化到系统托盘",
            QSystemTrayIcon.MessageIcon.Information, 2000
        )

    # ========== 状态更新 ==========

    def update_game_status(self, client_running, game_running, status_text):
        self.game_status_changed.emit(client_running, game_running, status_text)

    def _update_game_status_ui(self, client, game, text):
        self.game_dot.set_color(C_GREEN if client else C_RED)
        self.game_text.setText(text)
        self.game_text.setStyleSheet(
            f"color: {C_GREEN if client else C_TEXT_DIM}; font-size: 11px; border: none;"
        )
        if game:
            self.mode_text.setText("🎮 游戏中")
            self.mode_text.setStyleSheet(f"color: {C_ORANGE}; font-size: 11px; border: none;")
        elif client:
            self.mode_text.setText("🏠 大厅")
            self.mode_text.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")
        else:
            self.mode_text.setText("")

        # 更新LCU状态卡
        if client:
            self.lcu_status_label.setText("客户端运行中")
            self.lcu_status_label.setStyleSheet(
                f"color: {C_GREEN}; font-size: 13px; font-weight: bold; border: none;"
            )
            self.lcu_detail_label.setText("等待LCU连接...")
            self.lcu_detail_label.setStyleSheet(
                f"color: {C_YELLOW}; font-size: 11px; border: none;"
            )
        else:
            self.lcu_status_label.setText("客户端未运行")
            self.lcu_status_label.setStyleSheet(
                f"color: {C_RED}; font-size: 13px; font-weight: bold; border: none;"
            )
            self.lcu_detail_label.setText("请启动英雄联盟客户端")
            self.lcu_detail_label.setStyleSheet(
                f"color: {C_TEXT_DIM}; font-size: 11px; border: none;"
            )

    def update_lcu_status(self, connected, message):
        self.lcu_status_changed.emit(connected, message)

    def _update_lcu_status_ui(self, connected, message):
        self.lcu_dot.set_color(C_GREEN if connected else C_RED)
        self.lcu_text.setText(message)
        self.lcu_text.setStyleSheet(
            f"color: {C_GREEN if connected else C_TEXT_DIM}; font-size: 11px; border: none;"
        )

        # 更新LCU连接卡
        if connected:
            self.lcu_status_label.setText("已连接")
            self.lcu_status_label.setStyleSheet(
                f"color: {C_GREEN}; font-size: 13px; font-weight: bold; border: none;"
            )
            self.lcu_detail_label.setText(f"端口: {self.lcu_client.port or '未知'}")
            self.lcu_detail_label.setStyleSheet(
                f"color: {C_TEXT_DIM}; font-size: 11px; border: none;"
            )
        else:
            self.lcu_status_label.setText("连接失败")
            self.lcu_status_label.setStyleSheet(
                f"color: {C_RED}; font-size: 13px; font-weight: bold; border: none;"
            )
            error_msg = self.lcu_client.last_error or message
            self.lcu_detail_label.setText(error_msg[:40])
            self.lcu_detail_label.setStyleSheet(
                f"color: {C_RED}; font-size: 11px; border: none;"
            )

    # ========== LCU重连 ==========

    def _reconnect_lcu(self):
        """强制重连LCU"""
        self.lcu_status_label.setText("重连中...")
        self.lcu_status_label.setStyleSheet(
            f"color: {C_YELLOW}; font-size: 13px; font-weight: bold; border: none;"
        )
        self.lcu_detail_label.setText("正在查找lockfile并重连...")
        self.lcu_detail_label.setStyleSheet(
            f"color: {C_YELLOW}; font-size: 11px; border: none;"
        )
        self.btn_reconnect.setEnabled(False)

        # 在后台线程执行重连
        QTimer.singleShot(100, self._do_reconnect)

    def _do_reconnect(self):
        success, msg = self.lcu_client.force_reconnect()
        self.btn_reconnect.setEnabled(True)
        if success:
            self.lcu_dot.set_color(C_GREEN)
            self.lcu_text.setText("LCU已连接")
            self.lcu_text.setStyleSheet(f"color: {C_GREEN}; font-size: 11px; border: none;")
            self.lcu_status_label.setText("已连接")
            self.lcu_status_label.setStyleSheet(
                f"color: {C_GREEN}; font-size: 13px; font-weight: bold; border: none;"
            )
            self.lcu_detail_label.setText(f"端口: {self.lcu_client.port or '未知'}")
            self.lcu_detail_label.setStyleSheet(
                f"color: {C_TEXT_DIM}; font-size: 11px; border: none;"
            )
        else:
            self.lcu_dot.set_color(C_RED)
            self.lcu_text.setText(msg)
            self.lcu_text.setStyleSheet(f"color: {C_RED}; font-size: 11px; border: none;")
            self.lcu_status_label.setText("连接失败")
            self.lcu_status_label.setStyleSheet(
                f"color: {C_RED}; font-size: 13px; font-weight: bold; border: none;"
            )
            self.lcu_detail_label.setText(msg[:40])
            self.lcu_detail_label.setStyleSheet(
                f"color: {C_RED}; font-size: 11px; border: none;"
            )

    # ========== 功能方法 ==========

    def toggle_always_on_top(self, checked):
        self.always_on_top = checked
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        self.save_settings()

    def change_refresh_interval(self, v):
        self.refresh_interval = v
        self.save_settings()

    def refresh_game_data(self):
        if not self.lcu_client.is_connected():
            # 友好提示，不弹窗
            self.game_info_label.setText("LCU未连接，请点击上方「重新连接」")
            self.game_info_label.setStyleSheet(
                f"color: {C_ORANGE}; padding: 30px; font-size: 13px; border: none;"
            )
            return
        phase = self.lcu_client.get_current_game()
        if phase:
            if 'ChampSelect' in phase:
                self.game_info_label.setText("英雄选择阶段")
                self.game_info_label.setStyleSheet(
                    f"color: {C_GREEN}; padding: 10px; font-size: 13px; border: none;"
                )
                champ = self.lcu_client.get_champion_select()
                if champ:
                    self.display_champ_select(champ)
            elif 'InProgress' in phase:
                self.game_info_label.setText("游戏进行中")
                self.game_info_label.setStyleSheet(
                    f"color: {C_ORANGE}; padding: 10px; font-size: 13px; border: none;"
                )
            else:
                self.game_info_label.setText(f"阶段: {phase}")
                self.game_info_label.setStyleSheet(
                    f"color: {C_TEXT}; padding: 10px; font-size: 13px; border: none;"
                )
        else:
            self.game_info_label.setText("未检测到对局")
            self.game_info_label.setStyleSheet(
                f"color: {C_TEXT_DIM}; padding: 30px; font-size: 13px; border: none;"
            )

    def display_champ_select(self, data):
        self._clear_layout(self.players_layout)
        try:
            my = data.get('myTeam', [])
            their = data.get('theirTeam', [])
            if not my and not their:
                l = QLabel("等待玩家加入...")
                l.setStyleSheet(f"color: {C_TEXT_DIM}; padding: 10px; border: none;")
                self.players_layout.addWidget(l)
                return
            if my:
                hdr = QLabel("── 我方 ──")
                hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
                hdr.setStyleSheet(f"color: {C_GREEN}; font-weight: bold; font-size: 12px; border: none;")
                self.players_layout.addWidget(hdr)
                for p in my:
                    cid = p.get('championId', 0)
                    cname = self._champ_name(cid)
                    sname = p.get('summonerName', '未知')
                    s1 = self._spell_name(p.get('spell1Id', 0))
                    s2 = self._spell_name(p.get('spell2Id', 0))
                    self.players_layout.addWidget(
                        PlayerCard(sname, cname, "段位未知", f"{s1}/{s2}", True)
                    )
            if their:
                hdr = QLabel("── 敌方 ──")
                hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
                hdr.setStyleSheet(f"color: {C_RED}; font-weight: bold; font-size: 12px; border: none;")
                self.players_layout.addWidget(hdr)
                for p in their:
                    cid = p.get('championId', 0)
                    cname = self._champ_name(cid)
                    sname = p.get('summonerName', '未知')
                    s1 = self._spell_name(p.get('spell1Id', 0))
                    s2 = self._spell_name(p.get('spell2Id', 0))
                    self.players_layout.addWidget(
                        PlayerCard(sname, cname, "段位未知", f"{s1}/{s2}", False)
                    )
            self.players_layout.addStretch()
        except Exception as e:
            l = QLabel(f"解析失败: {e}")
            l.setStyleSheet(f"color: {C_RED}; padding: 10px; border: none;")
            self.players_layout.addWidget(l)

    def _champ_name(self, cid):
        if cid == 0: return "未选择"
        for _, info in self.hero_list.items():
            if info.get('id') == cid:
                return info.get('name_cn', f'英雄#{cid}')
        return f'英雄#{cid}'

    def _spell_name(self, sid):
        m = {1:"净化",3:"虚弱",4:"闪现",6:"幽灵疾步",7:"治疗术",
             11:"惩戒",12:"传送",14:"引燃",21:"屏障",32:"标记",39:"雪球"}
        return m.get(sid, f"#{sid}")

    # ========== 英雄搜索 ==========

    def _search_hero(self, force_refresh=False):
        text = self.hero_combo.currentText().strip()
        name = text.split('(')[0].strip() if '(' in text else text.strip()
        if not name:
            return

        self._current_hero = name
        self._clear_layout(self.hero_layout)

        if force_refresh:
            load_text = f"正在刷新 {name} 的数据"
        else:
            load_text = f"正在获取 {name} 的数据"

        self._loading_widget = LoadingPlaceholder(load_text)
        self.hero_layout.addWidget(self._loading_widget)

        if self._data_worker and self._data_worker.isRunning():
            self._data_worker.terminate()
        self._data_worker = HeroDataWorker(self.spider, name, force_refresh=force_refresh)
        self._data_worker.finished.connect(self._on_data_loaded)
        self._data_worker.start()

    def _refresh_hero_cache(self):
        """强制刷新当前英雄的缓存"""
        if self._current_hero:
            self._search_hero(force_refresh=True)
        else:
            text = self.hero_combo.currentText().strip()
            name = text.split('(')[0].strip() if '(' in text else text.strip()
            if name:
                self._current_hero = name
                self._search_hero(force_refresh=True)

    def _on_data_loaded(self, hero_name, data, is_refresh):
        self._clear_layout(self.hero_layout)
        if self._loading_widget:
            self._loading_widget.stop()
            self._loading_widget = None

        if not data:
            self.hero_layout.addWidget(
                NotFoundCard(hero_name, "网络请求失败且无本地缓存")
            )
            self.hero_layout.addStretch()
            return

        has_real = False
        has_cached = False

        # 检查是否有缓存降级数据
        for key in ['win_rate', 'counter', 'build']:
            d = data.get(key)
            if d and d.get('source', '').endswith('_cached'):
                has_cached = True
                break

        # 如果有缓存降级，显示提示
        if has_cached and not is_refresh:
            self.hero_layout.addWidget(CachedDataBanner())

        # 胜率
        wr = data.get('win_rate')
        if wr and wr.get('source') != 'local_mock':
            self.hero_layout.addWidget(self._wr_card(wr))
            has_real = True

        # 克制
        ct = data.get('counter')
        if ct and ct.get('source') != 'local_mock':
            self.hero_layout.addWidget(self._counter_card(ct))
            has_real = True

        # 出装
        bd = data.get('build')
        if bd and bd.get('source') != 'local_mock':
            self.hero_layout.addWidget(self._build_card(bd))
            has_real = True

        # 详情（本地mock也显示，因为wanplus始终是本地的）
        wp = data.get('wanplus')
        if wp:
            self.hero_layout.addWidget(self._detail_card(wp))
            has_real = True

        if not has_real:
            hint = "OP.GG 数据源暂时不可用\n点击「刷新缓存」可重试"
            self.hero_layout.addWidget(NotFoundCard(hero_name, hint))

        self.hero_layout.addStretch()

    def _clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            w = layout.itemAt(i).widget()
            if w:
                w.deleteLater()

    # ========== 数据卡片 ==========

    def _wr_card(self, wr):
        card = LoLCard("胜率数据")
        o = wr.get('overall', {})
        wr_val = o.get('win_rate', 0)
        wr_c = C_GREEN if wr_val >= 50 else C_RED

        # 来源标记
        source = wr.get('source', '')
        if source.endswith('_cached'):
            src_lbl = QLabel("● 本地缓存")
            src_lbl.setStyleSheet(f"color: {C_YELLOW}; font-size: 10px; border: none;")
            card.add_widget(src_lbl)
        elif source.startswith('op.gg'):
            src_lbl = QLabel("● OP.GG")
            src_lbl.setStyleSheet(f"color: {C_GREEN}; font-size: 10px; border: none;")
            card.add_widget(src_lbl)

        row = QHBoxLayout()
        row.setSpacing(24)
        for label, val, color in [
            ("胜率", f"{wr_val}%", wr_c),
            ("选取率", f"{o.get('pick_rate',0)}%", C_BLUE),
            ("禁用率", f"{o.get('ban_rate',0)}%", C_ORANGE),
            ("梯队", o.get('tier','未知'), C_GOLD),
        ]:
            col = QVBoxLayout()
            col.setSpacing(2)
            l = QLabel(label)
            l.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 10px; border: none;")
            v = QLabel(str(val))
            v.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold; border: none;")
            col.addWidget(l)
            col.addWidget(v)
            row.addLayout(col)
        card.add_layout(row)

        for pn, pd in wr.get('positions', {}).items():
            r = QHBoxLayout()
            pw = pd.get('win_rate', 0)
            pc = C_GREEN if pw >= 50 else C_RED
            n = QLabel(pn)
            n.setStyleSheet(f"color: {C_TEXT_BRIGHT}; font-size: 12px; font-weight: bold; border: none;")
            v = QLabel(f"{pw}%  ·  {pd.get('tier','')}")
            v.setStyleSheet(f"color: {pc}; font-size: 12px; border: none;")
            r.addWidget(n)
            r.addStretch()
            r.addWidget(v)
            card.add_layout(r)
        return card

    def _counter_card(self, ct):
        card = LoLCard("克制关系")

        source = ct.get('source', '')
        if source.endswith('_cached'):
            src_lbl = QLabel("● 本地缓存")
            src_lbl.setStyleSheet(f"color: {C_YELLOW}; font-size: 10px; border: none;")
            card.add_widget(src_lbl)
        elif source.startswith('op.gg'):
            src_lbl = QLabel("● OP.GG")
            src_lbl.setStyleSheet(f"color: {C_GREEN}; font-size: 10px; border: none;")
            card.add_widget(src_lbl)

        tips = ct.get('counter_tips', '')
        if tips:
            t = QLabel(tips)
            t.setWordWrap(True)
            t.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 12px; font-style: italic; border: none;")
            card.add_widget(t)

        strong = ct.get('strong_against', [])
        if strong:
            l = QLabel("克制英雄")
            l.setStyleSheet(f"color: {C_GREEN}; font-size: 12px; font-weight: bold; border: none;")
            card.add_widget(l)
            for h in strong[:5]:
                card.add_widget(
                    CounterRow(h.get('hero_name',''), h.get('win_rate',0), h.get('reason',''), False)
                )

        weak = ct.get('weak_against', [])
        if weak:
            l = QLabel("被克制英雄")
            l.setStyleSheet(f"color: {C_RED}; font-size: 12px; font-weight: bold; border: none;")
            card.add_widget(l)
            for h in weak[:5]:
                card.add_widget(
                    CounterRow(h.get('hero_name',''), h.get('win_rate',0), h.get('reason',''), True)
                )
        return card

    def _build_card(self, bd):
        card = LoLCard("出装推荐")

        source = bd.get('source', '')
        if source.endswith('_cached'):
            src_lbl = QLabel("● 本地缓存")
            src_lbl.setStyleSheet(f"color: {C_YELLOW}; font-size: 10px; border: none;")
            card.add_widget(src_lbl)
        elif source.startswith('op.gg'):
            src_lbl = QLabel("● OP.GG")
            src_lbl.setStyleSheet(f"color: {C_GREEN}; font-size: 10px; border: none;")
            card.add_widget(src_lbl)

        for label, items, color in [
            ("核心装备", bd.get('core_items',[]), C_GOLD),
            ("鞋子", bd.get('boots',[]), C_TEXT_DIM),
        ]:
            if items:
                l = QLabel(label)
                l.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold; border: none;")
                card.add_widget(l)
                for item in items:
                    r = QHBoxLayout()
                    n = QLabel(f"● {item.get('name','')}")
                    n.setStyleSheet(f"color: {C_TEXT_BRIGHT}; font-size: 12px; border: none;")
                    d = QLabel(item.get('description',''))
                    d.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px; border: none;")
                    r.addWidget(n)
                    r.addStretch()
                    r.addWidget(d)
                    card.add_layout(r)

        skills = bd.get('skill_order', [])
        if skills:
            l = QLabel("技能加点")
            l.setStyleSheet(f"color: {C_BLUE}; font-size: 12px; font-weight: bold; border: none;")
            card.add_widget(l)
            s = QLabel(" → ".join(skills[:10]))
            s.setStyleSheet(f"color: {C_BLUE}; font-size: 13px; font-family: Consolas, monospace; border: none;")
            card.add_widget(s)

        runes = bd.get('runes', [])
        if runes:
            l = QLabel("符文推荐")
            l.setStyleSheet(f"color: {C_GOLD}; font-size: 12px; font-weight: bold; border: none;")
            card.add_widget(l)
            for rs in runes:
                tag = "主系" if rs.get('primary') else "副系"
                txt = f"{tag} {rs.get('name','')}: {', '.join(rs.get('runes',[]))}"
                r = QLabel(txt)
                r.setWordWrap(True)
                r.setStyleSheet(f"color: {C_TEXT}; font-size: 12px; border: none;")
                card.add_widget(r)
        return card

    def _detail_card(self, wp):
        card = LoLCard("英雄详情")
        role = wp.get('role','未知')
        diff = wp.get('difficulty',0)
        r = QLabel(f"定位: {role}    难度: {'★'*diff}{'☆'*(10-diff)}")
        r.setStyleSheet(f"color: {C_TEXT_BRIGHT}; font-size: 13px; font-weight: bold; border: none;")
        card.add_widget(r)

        for label, items, color in [
            ("优点", wp.get('strengths',[]), C_GREEN),
            ("缺点", wp.get('weaknesses',[]), C_RED),
        ]:
            if items:
                l = QLabel(label)
                l.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold; border: none;")
                card.add_widget(l)
                for item in items:
                    i = QLabel(f"  • {item}")
                    i.setStyleSheet(f"color: {C_TEXT}; font-size: 12px; border: none;")
                    card.add_widget(i)

        combo = wp.get('combo_tips','')
        if combo:
            l = QLabel("连招技巧")
            l.setStyleSheet(f"color: {C_GOLD}; font-size: 12px; font-weight: bold; border: none;")
            card.add_widget(l)
            t = QLabel(f"  {combo}")
            t.setWordWrap(True)
            t.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 12px; font-style: italic; border: none;")
            card.add_widget(t)
        return card

    # ========== 工具方法 ==========

    def _populate_hero_combo(self):
        if not self.hero_list:
            return
        names = []
        for _, info in self.hero_list.items():
            cn = info.get('name_cn','')
            title = info.get('title_cn','')
            if cn:
                names.append(f"{cn} ({title})")
        names.sort()
        self.hero_combo.addItems(names)
        comp = QCompleter()
        comp.setModel(QStringListModel(names))
        comp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        comp.setFilterMode(Qt.MatchFlag.MatchContains)
        self.hero_combo.setCompleter(comp)

    def clear_cache(self):
        if QMessageBox.question(self, "确认", "确定清除所有缓存？",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
            ) == QMessageBox.StandardButton.Yes:
            cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static_data', 'cache')
            if os.path.exists(cache):
                import shutil
                try:
                    shutil.rmtree(cache)
                    os.makedirs(cache, exist_ok=True)
                    QMessageBox.information(self, "成功", "缓存已清除")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"清除失败: {e}")

    def update_all_hero_data(self):
        if QMessageBox.question(self, "确认", "更新英雄数据需要几分钟，继续？",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
            ) == QMessageBox.StandardButton.Yes:
            QTimer.singleShot(100, self._do_update)

    def _do_update(self):
        try:
            updated = self.spider.update_all_heroes_data()
            msg = "数据更新完成" if updated else "数据已是最新或无法获取"
            QMessageBox.information(self, "提示", msg)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新失败: {e}")

    def save_settings(self):
        try:
            c = self.config
            c['UI']['width'] = str(self.width())
            c['UI']['height'] = str(self.height())
            c['UI']['always_on_top'] = str(self.always_on_top).lower()
            c['UI']['refresh_interval'] = str(self.refresh_interval)
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
            with open(path, 'w', encoding='utf-8') as f:
                c.write(f)
        except Exception:
            pass
