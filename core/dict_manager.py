# -*- coding: utf-8 -*-
"""
3C 机型字典库管理引擎 (纯数据库驱动版：Turso / SQLite 持久化 + 内置全量种子兜底)
已彻底移除对 3C机型字典库.xlsx 的文件依赖。
"""
import threading
from typing import Any, Dict, List

from config.builtin_dict import BUILTIN_BRANDS, BUILTIN_LAPTOP, BUILTIN_MOBILE, BUILTIN_WATCH


class DictManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._loaded_from_db = False

        self.brands: List[Dict[str, str]] = []
        self.brand_name_to_id: Dict[str, str] = {}
        self.brand_id_to_name: Dict[str, str] = {}

        # 手机&平板 参数字典
        self.mobile_colors: List[str] = []
        self.mobile_networks: List[str] = []
        self.mobile_channels: List[str] = []
        self.mobile_rams: List[str] = []
        self.mobile_roms: List[str] = []
        self.mobile_memory_combos: List[str] = []

        # 笔记本 参数字典
        self.laptop_ssds: List[str] = []
        self.laptop_hdds: List[str] = []
        self.laptop_cpus: List[str] = []
        self.laptop_gpus: List[str] = []

        # 手表 参数字典
        self.watch_materials: List[str] = []
        self.watch_sizes: List[str] = []
        self.watch_connections: List[str] = []
        self.watch_straps: List[str] = []
        self.watch_networks: List[str] = []

        self._load_builtin_fallback()

    def _reset_collections(self) -> None:
        self.brands = []
        self.brand_name_to_id = {}
        self.brand_id_to_name = {}
        self.mobile_colors = []
        self.mobile_networks = []
        self.mobile_channels = []
        self.mobile_rams = []
        self.mobile_roms = []
        self.mobile_memory_combos = []
        self.laptop_ssds = []
        self.laptop_hdds = []
        self.laptop_cpus = []
        self.laptop_gpus = []
        self.watch_materials = []
        self.watch_sizes = []
        self.watch_connections = []
        self.watch_straps = []
        self.watch_networks = []

    def _add_brand(self, bid: str, bname: str) -> None:
        bid = str(bid or "").strip()
        if bid.endswith(".0"):
            bid = bid[:-2]
        bname = str(bname or "").strip()
        if not bid or not bname or bname.lower() == "nan":
            return
        if bname.lower() not in self.brand_name_to_id:
            self.brands.append({"id": bid, "name": bname})
            self.brand_name_to_id[bname.lower()] = bid
            self.brand_name_to_id[bname] = bid
            self.brand_id_to_name[bid] = bname

    def _dedupe(self) -> None:
        self.mobile_colors = list(dict.fromkeys(self.mobile_colors))
        self.mobile_networks = list(dict.fromkeys(self.mobile_networks))
        self.mobile_channels = list(dict.fromkeys(self.mobile_channels))
        self.mobile_rams = list(dict.fromkeys(self.mobile_rams))
        self.mobile_roms = list(dict.fromkeys(self.mobile_roms))
        self.mobile_memory_combos = list(dict.fromkeys(self.mobile_memory_combos))
        self.laptop_ssds = list(dict.fromkeys(self.laptop_ssds))
        self.laptop_hdds = list(dict.fromkeys(self.laptop_hdds))
        self.laptop_cpus = list(dict.fromkeys(self.laptop_cpus))
        self.laptop_gpus = list(dict.fromkeys(self.laptop_gpus))
        self.watch_materials = list(dict.fromkeys(self.watch_materials))
        self.watch_sizes = list(dict.fromkeys(self.watch_sizes))
        self.watch_connections = list(dict.fromkeys(self.watch_connections))
        self.watch_straps = list(dict.fromkeys(self.watch_straps))
        self.watch_networks = list(dict.fromkeys(self.watch_networks))

    def _load_builtin_fallback(self) -> None:
        self._reset_collections()
        for b in BUILTIN_BRANDS:
            self._add_brand(b.get("id", ""), b.get("name", ""))

        self.mobile_colors.extend(BUILTIN_MOBILE.get("机型颜色", []))
        self.mobile_networks.extend(BUILTIN_MOBILE.get("网络制式", []))
        self.mobile_channels.extend(BUILTIN_MOBILE.get("购买渠道", []))
        self.mobile_rams.extend(BUILTIN_MOBILE.get("RAM", []))
        self.mobile_roms.extend(BUILTIN_MOBILE.get("ROM", []))
        self.mobile_memory_combos.extend([
            "4G+64G", "4G+128G", "6G+128G", "6G+256G",
            "8G+128G", "8G+256G", "8G+512G", "8G+1TB",
            "12G+128G", "12G+256G", "12G+512G", "12G+1TB",
            "16G+256G", "16G+512G", "16G+1TB", "16G+2TB",
            "24G+512G", "24G+1TB", "24G+2TB",
            "32G+512G", "32G+1TB", "32G+2TB",
        ])

        self.laptop_ssds.extend(BUILTIN_LAPTOP.get("固态硬盘", []))
        self.laptop_hdds.extend(BUILTIN_LAPTOP.get("机械硬盘", []))
        self.laptop_cpus.extend(BUILTIN_LAPTOP.get("处理器", []))
        self.laptop_gpus.extend(BUILTIN_LAPTOP.get("显卡", []))

        self.watch_materials.extend(BUILTIN_WATCH.get("表壳材质", []))
        self.watch_sizes.extend(BUILTIN_WATCH.get("表壳尺寸", []))
        self.watch_connections.extend(BUILTIN_WATCH.get("连接", []))
        self.watch_straps.extend(BUILTIN_WATCH.get("表带", []))
        self.watch_networks.extend(BUILTIN_WATCH.get("网络制式", []))
        self._dedupe()

    def load_dictionary(self, force: bool = False) -> None:
        """从 Turso / SQLite 数据库加载字典，失败时自动回退至内置种子数据"""
        with self._lock:
            if self._loaded_from_db and not force:
                return
            try:
                from core.turso_db import turso_store

                db_data = turso_store.load_dict_data()
                if any(db_data.values()):
                    self._reset_collections()
                    for b in db_data.get("brands", []):
                        self._add_brand(b.get("id", ""), b.get("name", ""))
                    self.mobile_colors.extend(db_data.get("mobile_colors", []))
                    self.mobile_networks.extend(db_data.get("mobile_networks", []))
                    self.mobile_channels.extend(db_data.get("mobile_channels", []))
                    self.mobile_rams.extend(db_data.get("mobile_rams", []))
                    self.mobile_roms.extend(db_data.get("mobile_roms", []))
                    self.mobile_memory_combos.extend(db_data.get("mobile_memory_combos", []))
                    self.laptop_ssds.extend(db_data.get("laptop_ssds", []))
                    self.laptop_hdds.extend(db_data.get("laptop_hdds", []))
                    self.laptop_cpus.extend(db_data.get("laptop_cpus", []))
                    self.laptop_gpus.extend(db_data.get("laptop_gpus", []))
                    self.watch_materials.extend(db_data.get("watch_materials", []))
                    self.watch_sizes.extend(db_data.get("watch_sizes", []))
                    self.watch_connections.extend(db_data.get("watch_connections", []))
                    self.watch_straps.extend(db_data.get("watch_straps", []))
                    self.watch_networks.extend(db_data.get("watch_networks", []))
                    self._dedupe()
                    self._loaded_from_db = True
                    return
            except Exception as e:
                print(f"从数据库加载字典异常，已使用内置全量种子兜底: {e}")

            self._load_builtin_fallback()

    def to_dict(self) -> Dict[str, Any]:
        self.load_dictionary()
        return {
            "brands": self.brands,
            "mobile_colors": self.mobile_colors,
            "mobile_networks": self.mobile_networks,
            "mobile_channels": self.mobile_channels,
            "mobile_rams": self.mobile_rams,
            "mobile_roms": self.mobile_roms,
            "mobile_memory_combos": self.mobile_memory_combos,
            "laptop_ssds": self.laptop_ssds,
            "laptop_hdds": self.laptop_hdds,
            "laptop_cpus": self.laptop_cpus,
            "laptop_gpus": self.laptop_gpus,
            "watch_materials": self.watch_materials,
            "watch_sizes": self.watch_sizes,
            "watch_connections": self.watch_connections,
            "watch_straps": self.watch_straps,
            "watch_networks": self.watch_networks,
        }


dict_manager = DictManager()
