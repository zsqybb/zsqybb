# LeagueAkari 国服复刻助手

一个基于Python + PyQt6的LeagueAkari风格英雄联盟助手，专为国服设计，无需外服API、无需翻墙、无封号风险。

## 功能特性

### ✅ 核心功能
1. **自动化检测**：后台轮询检测LOL客户端进程状态
2. **LCU自动连接**：自动获取本地LCU端口和授权令牌
3. **对局阵容读取**：选人/加载阶段自动获取双方英雄信息
4. **英雄数据联动**：实时展示英雄克制关系、出装、符文
5. **暗色主题界面**：模仿LeagueAkari风格，支持悬浮窗、置顶模式

### ✅ 安全合规
- 仅使用国服LCU本地客户端API，无需拳头官方外网API
- 纯只读查询，不读取游戏内存、不进程注入、不修改游戏数据
- 数据来源为OP.GG国服、玩加电竞公开页面
- 不违反腾讯用户协议，无封号风险

## 项目结构

```
LeagueAkari_CN/
├── main.py              # 程序入口、全局调度
├── lcu_connect.py       # LCU连接模块
├── game_monitor.py      # 进程检测模块
├── data_spider.py       # 数据爬取模块
├── ui_window.py         # 界面模块
├── static_data/         # 静态资源文件夹
│   ├── hero_list.json   # 英雄ID-名称映射表
│   └── item_data.json   # 装备基础数据
├── config.ini           # 配置文件
├── 启动器.bat           # Windows一键启动脚本
└── requirements.txt     # Python依赖包列表
```

## 快速开始

### 方式一：使用启动脚本（推荐）
1. 双击运行 `启动器.bat`
2. 脚本会自动安装所需依赖包
3. 启动英雄联盟客户端
4. 程序会自动检测并连接

### 方式二：手动安装运行
1. 安装Python 3.8或更高版本
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python main.py
   ```

## 功能说明

### 1. 游戏状态检测
- 自动检测LeagueClient.exe和League of Legends.exe进程
- 实时显示客户端运行状态
- 支持后台持续监控

### 2. LCU自动连接
- 自动查找lockfile文件
- 解析端口和授权令牌
- 建立本地HTTPS连接
- 连接状态实时显示

### 3. 对局信息展示
- 英雄选择阶段显示双方阵容
- 展示英雄、召唤师技能、段位信息
- 支持自动刷新和手动刷新

### 4. 英雄数据分析
- 胜率统计（总体+分位置）
- 克制关系（强对抗/弱对抗英雄）
- 出装推荐（核心装备+鞋子+起始装）
- 符文搭配和技能加点顺序
- 英雄定位和技巧提示

### 5. 界面特性
- 暗色简约主题
- 窗口置顶/取消置顶
- 系统托盘最小化
- 可调节刷新间隔
- 响应式布局设计

## 配置说明

### config.ini 配置文件
```ini
[UI]
width = 400             # 窗口宽度
height = 600            # 窗口高度
always_on_top = true    # 是否置顶
refresh_interval = 3    # 刷新间隔(秒)

[Data]
cache_days = 7          # 数据缓存天数
use_cache = true        # 是否使用缓存

[Game]
auto_detect = true      # 自动检测游戏
auto_connect = true     # 自动连接LCU
```

## 打包成EXE

### 使用PyInstaller打包
1. 安装PyInstaller：
   ```bash
   pip install pyinstaller
   ```

2. 执行打包命令：
   ```bash
   pyinstaller --onefile --windowed --icon=static_data/icon.ico --name="LeagueAkari助手" main.py
   ```

3. 高级打包选项（推荐）：
   ```bash
   pyinstaller --onefile --windowed ^
     --icon=static_data/icon.ico ^
     --name="LeagueAkari国服助手" ^
     --add-data="static_data;static_data" ^
     --add-data="config.ini;." ^
     --hidden-import=PyQt6.sip ^
     --clean ^
     main.py
   ```

4. 打包后的EXE位于 `dist/` 目录

### 打包注意事项
- 确保所有依赖包已正确安装
- 静态资源文件需要包含在打包中
- 图标文件需要转换为.ico格式
- 建议在干净的虚拟环境中打包

## 常见问题

### Q1: 程序无法检测到游戏
- 确保英雄联盟客户端已启动
- 以管理员权限运行程序
- 检查防火墙设置

### Q2: LCU连接失败
- 确保游戏客户端完全启动（进入大厅）
- 检查lockfile文件权限
- 重启游戏客户端

### Q3: 数据无法加载
- 检查网络连接
- 确保可以访问OP.GG国服网站
- 尝试清除缓存后重试

### Q4: 界面显示异常
- 更新显卡驱动程序
- 确保安装了正确的PyQt6版本
- 检查系统DPI设置

## 开发说明

### 技术栈
- **Python 3.8+**：核心编程语言
- **PyQt6**：桌面GUI框架
- **requests**：HTTP请求库
- **psutil**：系统进程管理
- **beautifulsoup4**：网页数据解析

### 编码规范
- 使用UTF-8编码
- 所有路径使用os.path.join处理
- 关键函数添加中文注释
- 遵循PEP 8代码风格

## 免责声明

1. 本程序仅供学习交流使用
2. 不修改游戏数据，不影响游戏平衡
3. 仅读取公开数据，不涉及用户隐私
4. 请勿用于商业用途
5. 使用风险由用户自行承担

## 更新日志

### v1.0.0 (2024-04-28)
- 初始版本发布
- 实现基础功能框架
- 支持LCU自动连接
- 完成暗色主题界面

## 联系方式

如有问题或建议，请通过GitHub Issues提交。

---
**注意**：请合理使用本程序，遵守游戏规则和用户协议。