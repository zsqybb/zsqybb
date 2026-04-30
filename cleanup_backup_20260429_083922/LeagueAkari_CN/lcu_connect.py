#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LCU连接模块 - 健壮的lockfile查找 + 自动重连 + 指数退避重试 + 管理员检测
核心优化:
  1. lockfile路径持久化（记住上次成功的路径）
  2. 强制重连方法（供UI重连按钮调用）
  3. 管理员权限检测与提示
  4. 5级lockfile发现策略
  5. 心跳 + 指数退避自动重连
  6. 每种错误都有中文友好提示
"""
import os
import json
import time
import logging
import subprocess
import glob
import ctypes
import threading
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("LeagueAkari.LCU")


class LCUClient:
    """LCU客户端 - 自动发现 + 指数退避重连 + 友好错误 + 强制重连"""

    # 国服WeGame常见安装路径
    WEGAME_PATHS = [
        r"D:\英雄联盟",
        r"E:\英雄联盟",
        r"F:\英雄联盟",
        r"C:\英雄联盟",
        r"D:\Game\英雄联盟",
        r"D:\Games\英雄联盟",
        r"E:\Game\英雄联盟",
        r"F:\Game\英雄联盟",
        r"D:\WeGame\英雄联盟",
        r"C:\WeGame\英雄联盟",
        r"E:\WeGame\英雄联盟",
        r"D:\腾讯游戏\英雄联盟",
        r"C:\腾讯游戏\英雄联盟",
        r"E:\腾讯游戏\英雄联盟",
    ]

    # 拳头客户端路径
    RIOT_PATHS = [
        r"C:\Riot Games\League of Legends",
        r"D:\Riot Games\League of Legends",
        r"C:\Program Files\Riot Games\League of Legends",
        r"D:\Program Files\Riot Games\League of Legends",
    ]

    # 持久化路径
    _PERSIST_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static_data", ".lcu_last_path"
    )

    def __init__(self):
        self.port = None
        self.token = None
        self.base_url = None
        self.session = None
        self.connected = False
        self.last_check = 0
        self._reconnect_count = 0
        self._max_reconnect = 10
        self._lockfile_path = None
        self._last_error = ""
        self._is_admin = self._check_admin()

        self._build_session()

    def _build_session(self):
        """构建带重试策略的requests Session"""
        self.session = requests.Session()
        self.session.verify = False
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    @staticmethod
    def _check_admin():
        """检测是否以管理员身份运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    @property
    def is_admin(self):
        return self._is_admin

    @property
    def last_error(self):
        return self._last_error

    # ========== 持久化 ==========

    def _save_last_path(self, path):
        """保存上次成功的lockfile路径"""
        try:
            os.makedirs(os.path.dirname(self._PERSIST_FILE), exist_ok=True)
            with open(self._PERSIST_FILE, 'w', encoding='utf-8') as f:
                json.dump({"lockfile_dir": os.path.dirname(path)}, f)
        except Exception:
            pass

    def _load_last_path(self):
        """读取上次成功的lockfile目录"""
        try:
            if os.path.exists(self._PERSIST_FILE):
                with open(self._PERSIST_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lockfile_dir = data.get("lockfile_dir", "")
                    if lockfile_dir:
                        lf = os.path.join(lockfile_dir, "lockfile")
                        if os.path.exists(lf):
                            return lf
        except Exception:
            pass
        return None

    # ========== Lockfile 发现 ==========

    def find_lockfile(self):
        """多策略查找lockfile，按可靠性排序"""
        # 策略0: 持久化路径（最快）
        path = self._load_last_path()
        if path:
            logger.info(f"[持久化] 找到lockfile: {path}")
            self._lockfile_path = path
            return path

        # 策略1: 通过进程命令行参数
        path = self._find_via_process()
        if path:
            logger.info(f"[进程] 找到lockfile: {path}")
            self._save_last_path(path)
            self._lockfile_path = path
            return path

        # 策略2: 通过WeGame注册表
        path = self._find_via_registry()
        if path:
            logger.info(f"[注册表] 找到lockfile: {path}")
            self._save_last_path(path)
            self._lockfile_path = path
            return path

        # 策略3: WeGame/Riot常见路径
        path = self._find_via_common_paths()
        if path:
            logger.info(f"[常见路径] 找到lockfile: {path}")
            self._save_last_path(path)
            self._lockfile_path = path
            return path

        # 策略4: 盘符根目录搜索
        path = self._find_via_drive_scan()
        if path:
            logger.info(f"[盘符搜索] 找到lockfile: {path}")
            self._save_last_path(path)
            self._lockfile_path = path
            return path

        # 策略5: 宽搜索
        path = self._find_via_glob()
        if path:
            logger.info(f"[通配搜索] 找到lockfile: {path}")
            self._save_last_path(path)
            self._lockfile_path = path
            return path

        logger.warning("所有策略均未找到lockfile，请确保英雄联盟客户端已启动")
        return None

    def _find_via_process(self):
        try:
            result = subprocess.run(
                ['wmic', 'process', 'where', "name='LeagueClient.exe'", 'get', 'CommandLine'],
                capture_output=True, text=True, timeout=8,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0 and result.stdout:
                path = self._extract_install_dir(result.stdout)
                if path:
                    return path
        except Exception as e:
            logger.debug(f"wmic查找失败: {e}")

        try:
            ps_cmd = (
                "Get-CimInstance Win32_Process -Filter \"Name='LeagueClient.exe'\" | "
                "Select-Object -ExpandProperty CommandLine"
            )
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_cmd],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0 and result.stdout.strip():
                path = self._extract_install_dir(result.stdout)
                if path:
                    return path
        except Exception as e:
            logger.debug(f"PowerShell查找失败: {e}")

        return None

    def _extract_install_dir(self, cmd_output):
        for line in cmd_output.splitlines():
            line = line.strip()
            if not line:
                continue
            if '--install-directory=' in line:
                idx = line.find('--install-directory=')
                start = idx + len('--install-directory=')
                rest = line[start:]
                if rest.startswith('"'):
                    end = rest.find('"', 1)
                    if end > 0:
                        install_dir = rest[1:end]
                    else:
                        install_dir = rest.split('"')[0]
                else:
                    install_dir = rest.split(' ')[0].strip('"')
                lockfile = os.path.join(install_dir, 'lockfile')
                if os.path.exists(lockfile):
                    return lockfile
                parent = os.path.join(os.path.dirname(install_dir), 'lockfile')
                if os.path.exists(parent):
                    return parent
        return None

    def _find_via_registry(self):
        try:
            import winreg
            keys_to_try = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Tencent\LOL"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tencent\LOL"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Tencent\LOL"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Tencent\WeGame"),
            ]
            for hive, key_path in keys_to_try:
                try:
                    with winreg.OpenKey(hive, key_path) as key:
                        for val_name in ['InstallPath', 'InstallDir', 'Path', 'GamePath']:
                            try:
                                val, _ = winreg.QueryValueEx(key, val_name)
                                if val and os.path.isdir(val):
                                    lockfile = os.path.join(val, 'lockfile')
                                    if os.path.exists(lockfile):
                                        return lockfile
                            except FileNotFoundError:
                                continue
                except FileNotFoundError:
                    continue
        except Exception as e:
            logger.debug(f"注册表查找失败: {e}")
        return None

    def _find_via_common_paths(self):
        all_paths = self.WEGAME_PATHS + self.RIOT_PATHS
        for game_dir in all_paths:
            for sub in ['', 'Game', 'TCLS', 'LeagueClient']:
                lf = os.path.join(game_dir, sub, 'lockfile')
                if os.path.exists(lf):
                    return lf
        return None

    def _find_via_drive_scan(self):
        for drive in [f"{d}:\\" for d in 'CDEFGH' if os.path.isdir(f"{d}:\\")]:
            for dirname in ['英雄联盟', 'League of Legends', 'LoL', 'WeGame', '腾讯游戏']:
                for sub in ['', 'Game', 'TCLS']:
                    lf = os.path.join(drive, dirname, sub, 'lockfile')
                    if os.path.exists(lf):
                        return lf
        return None

    def _find_via_glob(self):
        for drive in ['C:', 'D:', 'E:', 'F:']:
            for pattern in [
                f"{drive}\\*\\英雄联盟\\lockfile",
                f"{drive}\\*\\*\\英雄联盟\\lockfile",
                f"{drive}\\*\\League of Legends\\lockfile",
            ]:
                try:
                    matches = glob.glob(pattern)
                    if matches:
                        return matches[0]
                except Exception:
                    continue
        return None

    # ========== Lockfile 解析 ==========

    def _parse_lockfile(self):
        if not self._lockfile_path or not os.path.exists(self._lockfile_path):
            return False
        try:
            with open(self._lockfile_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            parts = content.split(':')
            if len(parts) >= 5:
                self.port = parts[2]
                self.token = parts[3]
                self.base_url = f"https://127.0.0.1:{self.port}"
                return True
            else:
                logger.warning(f"lockfile格式异常: {content}")
        except PermissionError:
            logger.warning("lockfile被占用，可能客户端正在启动中")
        except Exception as e:
            logger.error(f"解析lockfile失败: {e}")
        return False

    # ========== 连接管理 ==========

    def auto_connect(self, callback=None):
        """自动连接LCU，带指数退避重试"""
        now = time.time()
        if now - self.last_check < 3:
            return
        self.last_check = now

        # 如果已连接，心跳检测
        if self.connected and self.session:
            if self._heartbeat():
                if callback:
                    callback(True, "LCU已连接")
                return
            else:
                self.connected = False
                logger.info("LCU心跳失败，准备重连")

        # 尝试连接
        success, msg = self._try_connect()

        if success:
            self._reconnect_count = 0
            self._last_error = ""
            if callback:
                callback(True, msg)
        else:
            self._reconnect_count += 1
            self._last_error = msg
            backoff = min(30, 5 * (2 ** min(self._reconnect_count - 1, 3)))
            self.last_check = now - (3 - min(backoff, 3))
            logger.info(f"LCU连接失败({self._reconnect_count}次)，{backoff:.0f}秒后重试")
            if callback:
                callback(False, msg)

    def force_reconnect(self):
        """强制重连（供UI重连按钮调用）"""
        self._lockfile_path = None
        self.connected = False
        self.port = None
        self.token = None
        self.base_url = None
        self.session = None
        self._reconnect_count = 0
        self._last_error = ""
        self._build_session()
        # 立即尝试连接
        success, msg = self._try_connect()
        if success:
            self._reconnect_count = 0
            self._last_error = ""
        else:
            self._last_error = msg
        return success, msg

    def _try_connect(self):
        """尝试连接LCU，返回 (success, message)"""
        # 步骤1: 查找lockfile
        if not self._lockfile_path or not os.path.exists(self._lockfile_path):
            path = self.find_lockfile()
            if not path:
                admin_hint = ""
                if not self._is_admin:
                    admin_hint = "（尝试以管理员身份运行）"
                return False, f"未找到lockfile{admin_hint}，请启动客户端"

        # 步骤2: 解析lockfile
        if not self._parse_lockfile():
            return False, "lockfile解析失败，客户端正在启动中"

        # 步骤3: 建立连接
        try:
            self.session = requests.Session()
            self.session.verify = False
            self.session.auth = HTTPBasicAuth('riot', self.token)
            self.session.headers.update({
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
            retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("https://", adapter)

            resp = self.session.get(
                f"{self.base_url}/lol-summoner/v1/current-summoner",
                timeout=(3, 5)
            )

            if resp.status_code == 200:
                self.connected = True
                self._reconnect_count = 0
                self._last_error = ""
                logger.info(f"LCU连接成功! 端口:{self.port}")
                return True, "LCU连接成功"
            elif resp.status_code == 401:
                return False, "认证失败，token已过期，请重启客户端"
            elif resp.status_code == 403:
                return False, "访问被拒绝，客户端版本不匹配"
            else:
                return False, f"连接测试失败(状态码:{resp.status_code})"

        except requests.exceptions.ConnectionError:
            return False, "连接被拒绝，客户端启动中..."
        except requests.exceptions.Timeout:
            return False, "连接超时，请检查客户端状态"
        except Exception as e:
            return False, f"连接异常: {str(e)[:50]}"

    def _heartbeat(self):
        """心跳检测"""
        try:
            resp = self.session.get(
                f"{self.base_url}/lol-summoner/v1/current-summoner",
                timeout=(2, 3)
            )
            return resp.status_code == 200
        except Exception:
            return False

    # ========== API 请求封装 ==========

    def _api_request(self, endpoint, method='GET', data=None, timeout=(3, 5)):
        """统一API请求"""
        if not self.connected or not self.session:
            return False, None, "LCU未连接"

        url = f"{self.base_url}{endpoint}"
        try:
            if method == 'GET':
                resp = self.session.get(url, timeout=timeout)
            elif method == 'POST':
                resp = self.session.post(url, json=data, timeout=timeout)
            elif method == 'PUT':
                resp = self.session.put(url, json=data, timeout=timeout)
            elif method == 'DELETE':
                resp = self.session.delete(url, timeout=timeout)
            else:
                return False, None, f"不支持的方法: {method}"

            if resp.status_code == 200:
                try:
                    return True, resp.json(), None
                except ValueError:
                    return True, resp.text, None
            elif resp.status_code == 204:
                return True, None, None
            elif resp.status_code == 404:
                return False, None, "资源不存在"
            else:
                return False, None, f"请求失败({resp.status_code})"

        except requests.exceptions.Timeout:
            return False, None, "请求超时"
        except requests.exceptions.ConnectionError:
            self.connected = False
            return False, None, "连接断开"
        except Exception as e:
            return False, None, f"请求异常: {str(e)[:50]}"

    # ========== 业务API ==========

    def is_connected(self):
        return self.connected

    def get_current_summoner(self):
        ok, data, _ = self._api_request("/lol-summoner/v1/current-summoner")
        return data if ok else None

    def get_champion_select(self):
        ok, data, _ = self._api_request("/lol-champ-select/v1/session")
        return data if ok else None

    def get_current_game(self):
        ok, data, err = self._api_request("/lol-gameflow/v1/gameflow-phase")
        if ok and data:
            return data.strip('"') if isinstance(data, str) else str(data)
        return None

    def get_game_session(self):
        ok, data, _ = self._api_request("/lol-gameflow/v1/session")
        return data if ok else None

    def get_ranked_stats(self, summoner_id):
        ok, data, _ = self._api_request(f"/lol-ranked/v1/ranked-stats/{summoner_id}")
        return data if ok else None

    def get_summoner_by_name(self, name):
        ok, data, _ = self._api_request(f"/lol-summoner/v1/summoners?name={name}")
        return data if ok else None

    def get_summoner_by_puuid(self, puuid):
        ok, data, _ = self._api_request(f"/lol-summoner/v2/summoners/puuid/{puuid}")
        return data if ok else None

    def get_champion_mastery(self, summoner_id, champion_id):
        ok, data, _ = self._api_request(
            f"/lol-collections/v1/inventories/{summoner_id}/champion-mastery/{champion_id}"
        )
        return data if ok else None

    def get_friends_list(self):
        ok, data, _ = self._api_request("/lol-chat/v1/friends")
        return data if ok else None

    def get_loot(self):
        ok, data, _ = self._api_request("/lol-loot/v1/player-loot")
        return data if ok else None

    def refresh_lockfile(self):
        """强制刷新lockfile路径"""
        self._lockfile_path = None
        self.connected = False
        self.session = None
        return self.find_lockfile() is not None
