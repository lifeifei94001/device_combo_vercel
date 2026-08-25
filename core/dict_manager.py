# -*- coding: utf-8 -*-
"""
3C 机型字典库管理引擎 (Vercel Serverless 云端自适应版)
"""
import os
import sys
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class DictManager:
    def __init__(self):
        self.dict_file_paths = [
            os.path.join(BASE_DIR, "3C机型字典库.xlsx"),
            os.path.join(os.getcwd(), "3C机型字典库.xlsx"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "3C机型字典库.xlsx"),
            "/var/task/3C机型字典库.xlsx"
        ]
        
        self.brands: List[Dict[str, str]] = []
        self.brand_name_to_id: Dict[str, str] = {}
        self.brand_id_to_name: Dict[str, str] = {}
        
        # 手机&平板 参数字典
        self.mobile_colors: List[str] = []
        self.mobile_networks: List[str] = []
        self.mobile_channels: List[str] = []
        self.mobile_rams: List[str] = []
        self.mobile_roms: List[str] = []

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

        self.load_dictionary()

    def find_dict_path(self) -> Optional[str]:
        for p in self.dict_file_paths:
            if os.path.exists(p):
                return p
        return None

    def load_dictionary(self):
        """加载《3C机型字典库.xlsx》"""
        dict_path = self.find_dict_path()
        if dict_path and os.path.exists(dict_path):
            try:
                excel = pd.ExcelFile(dict_path)
                if "品牌id" in excel.sheet_names:
                    df_b = pd.read_excel(excel, sheet_name="品牌id", dtype=str).fillna("")
                    for _, row in df_b.iterrows():
                        bid = str(row.get("ID", "")).strip()
                        if bid.endswith(".0"): bid = bid[:-2]
                        bname = str(row.get("品牌名称", "")).strip()
                        if bid and bname:
                            self.brands.append({"id": bid, "name": bname})
                            self.brand_name_to_id[bname.lower()] = bid
                            self.brand_name_to_id[bname] = bid
                            self.brand_id_to_name[bid] = bname

                phone_sheet = "手机&平板" if "手机&平板" in excel.sheet_names else "手机" if "手机" in excel.sheet_names else ""
                if phone_sheet:
                    df_m = pd.read_excel(excel, sheet_name=phone_sheet, dtype=str).fillna("")
                    self.mobile_colors.extend([c.strip() for c in df_m.get("机型颜色", []) if str(c).strip() and str(c) != 'nan'])
                    self.mobile_networks.extend([n.strip() for n in df_m.get("网络制式", []) if str(n).strip() and str(n) != 'nan'])
                    self.mobile_channels.extend([ch.strip() for ch in df_m.get("购买渠道", []) if str(ch).strip() and str(ch) != 'nan'])
                    self.mobile_rams.extend([r.strip() for r in df_m.get("RAM", []) if str(r).strip() and str(r) != 'nan'])
                    self.mobile_roms.extend([ro.strip() for ro in df_m.get("ROM", []) if str(ro).strip() and str(ro) != 'nan'])

                if "笔记本" in excel.sheet_names:
                    df_l = pd.read_excel(excel, sheet_name="笔记本", dtype=str).fillna("")
                    self.laptop_ssds.extend([s.strip() for s in df_l.get("固态硬盘", []) if str(s).strip() and str(s) != 'nan'])
                    self.laptop_hdds.extend([h.strip() for h in df_l.get("机械硬盘", []) if str(h).strip() and str(h) != 'nan'])
                    self.laptop_cpus.extend([cp.strip() for cp in df_l.get("处理器", []) if str(cp).strip() and str(cp) != 'nan'])
                    self.laptop_gpus.extend([gp.strip() for gp in df_l.get("显卡", []) if str(gp).strip() and str(gp) != 'nan'])

                if "手表" in excel.sheet_names:
                    df_w = pd.read_excel(excel, sheet_name="手表", dtype=str).fillna("")
                    self.watch_materials.extend([m.strip() for m in df_w.get("表壳材质", []) if str(m).strip() and str(m) != 'nan'])
                    self.watch_sizes.extend([s.strip() for s in df_w.get("表壳尺寸", []) if str(s).strip() and str(s) != 'nan'])
                    self.watch_connections.extend([cn.strip() for cn in df_w.get("连接", []) if str(cn).strip() and str(cn) != 'nan'])
                    self.watch_networks.extend([wn.strip() for wn in df_w.get("网络制式", []) if str(wn).strip() and str(wn) != 'nan'])
            except Exception as e:
                print(f"读取字典异常: {e}")

        # 默认备用
        if not self.watch_straps:
            self.watch_straps = ['TPU表带', '硅胶表带', '氟橡胶表带', '皮质表带', '真皮表带', '米兰尼斯表带', '不锈钢表带', '编织表带', '无表带', '有表带']
        if not self.watch_materials:
            self.watch_materials = ['铝金属表壳', '不锈钢表壳', '钛金属表壳', '精密陶瓷', '纤维高强度聚合物', '高分子材料', '陶瓷表壳', '纳米微晶陶瓷', '精钢表壳', '316L不锈钢材质']
        if not self.watch_sizes:
            self.watch_sizes = ['41毫米', '45毫米', '40毫米', '44毫米', '38毫米', '42毫米', '46毫米', '49毫米', '1.85寸', '1.43英寸', '1.91英寸', '2.07英寸']
        if not self.watch_connections:
            self.watch_connections = ['GPS', 'GPS+蜂窝网络', '蓝牙', 'WIFI', 'eSIM独立通话']

        self.mobile_colors = list(dict.fromkeys(self.mobile_colors))
        self.mobile_networks = list(dict.fromkeys(self.mobile_networks))
        self.mobile_channels = list(dict.fromkeys(self.mobile_channels))
        self.laptop_ssds = list(dict.fromkeys(self.laptop_ssds))
        self.laptop_hdds = list(dict.fromkeys(self.laptop_hdds))
        self.laptop_cpus = list(dict.fromkeys(self.laptop_cpus))
        self.laptop_gpus = list(dict.fromkeys(self.laptop_gpus))
        self.watch_materials = list(dict.fromkeys(self.watch_materials))
        self.watch_sizes = list(dict.fromkeys(self.watch_sizes))
        self.watch_connections = list(dict.fromkeys(self.watch_connections))
        self.watch_straps = list(dict.fromkeys(self.watch_straps))

dict_manager = DictManager()
