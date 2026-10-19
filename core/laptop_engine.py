# -*- coding: utf-8 -*-
"""
笔记本机型排列组合算法引擎 (全链路自动去重 + 七级结构化排序)
排序规则：
1. 品牌 (品牌ID数值升序 + 品牌名称)
2. 型号 (型号ID数值升序)
3. 别名 (具体别名优先 -> "其他"次之 -> 空值最后，同级保持录入顺序)
4. 处理器 (保持用户录入先后顺序 -> 空值最后)
5. 显卡型号 (保持用户录入先后顺序 -> 空值最后)
6. 固态硬盘 (按实际容量从大到小，如 4TB > 2TB > 1TB > 512G > 256G > 无)
7. 机械硬盘 (按实际容量从大到小，如 4TB > 2TB > 1TB > 500G > 无)
"""
import re
from itertools import product
from typing import List, Dict, Any, Tuple
from config.constants import TARGET_COLUMNS
from core.df_compat import LightDataFrame, clean_date_str


def clean_date(val: Any) -> str:
    return clean_date_str(val)


def clean_id(val: Any) -> str:
    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return ''
    if s.endswith('.0') and s[:-2].isdigit():
        return s[:-2]
    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
    except Exception:
        pass
    return s


def split_tolerant_pause(val: Any) -> List[str]:
    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return ['']
    if '、' in s:
        items = [i.strip() for i in s.split('、') if i.strip()]
    elif ',' in s:
        items = [i.strip() for i in s.split(',') if i.strip()]
    elif ' ' in s:
        items = [i.strip() for i in s.split(' ') if i.strip()]
    else:
        items = [s]
    items = list(dict.fromkeys(items))
    return items if items else ['']


def parse_id_sort_key(val: Any) -> Tuple[int, int, str]:
    s = str(val).strip()
    if not s:
        return (2, 0, '')
    if s.isdigit():
        return (0, int(s), '')
    return (1, 0, s)


def parse_disk_size_gb(val: Any) -> Tuple[int, float, str]:
    """
    硬盘容量从大到小降序键 (兼容 2TB / 1TB / 512G / 512G+1TB / 无)：
    - 有效容量返回 (0, -total_gb, s)，从大到小排列
    - "无" / "无机械" / "无固态" 等非数值文本返回 (1, 0.0, s)
    - 空字符串返回 (2, 0.0, '')
    """
    s = str(val).strip()
    if not s:
        return (2, 0.0, '')
    if s in ('无', '无机械', '无固态', '无硬盘', '-'):
        return (1, 0.0, s)
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*(TB|T|GB|G|MB|M)?', s, flags=re.IGNORECASE)
    valid_matches = [m for m in matches if m[0]]
    if not valid_matches:
        return (1, 0.0, s)

    total_gb = 0.0
    for num_str, unit in valid_matches:
        num = float(num_str)
        u = (unit or 'G').upper()
        if u in ('TB', 'T'):
            total_gb += num * 1024.0
        elif u in ('MB', 'M'):
            total_gb += num / 1024.0
        else:
            total_gb += num
    return (0, -total_gb, s)


def generate_laptop_combinations(records: List[Dict[str, Any]]) -> Tuple[LightDataFrame, int]:
    """
    接收多条笔记本录入数据，生成四维笛卡尔积排列组合结果 DataFrame（自动去重 + 七级结构化排序）。
    """
    all_combinations = set()
    COMBO_FIELDS = ['固态硬盘', '机械硬盘', '显卡型号', '处理器']

    first_seen_alias: Dict[str, int] = {}
    first_seen_cpu: Dict[str, int] = {}
    first_seen_gpu: Dict[str, int] = {}

    for row in records:
        brand_id = clean_id(row.get('品牌ID', ''))
        brand_name = str(row.get('品牌名称', '')).strip()
        if brand_name.lower() == 'nan':
            brand_name = ''
        alias = str(row.get('别名', '')).strip()
        if alias.lower() == 'nan':
            alias = ''
        model_id = clean_id(row.get('型号', ''))

        on_price = str(row.get('开机价', '')).strip()
        if on_price.lower() == 'nan':
            on_price = ''
        off_price = str(row.get('关机价', '')).strip()
        if off_price.lower() == 'nan':
            off_price = ''
        min_price = str(row.get('开机最低价', '')).strip()
        if min_price.lower() == 'nan':
            min_price = ''

        release = clean_date(row.get('发布时间', ''))

        if alias not in first_seen_alias:
            first_seen_alias[alias] = len(first_seen_alias)

        dims = [split_tolerant_pause(row.get(f, '')) for f in COMBO_FIELDS]
        dim_ssd, dim_hdd, dim_gpu, dim_cpu = dims

        for cp in dim_cpu:
            if cp not in first_seen_cpu:
                first_seen_cpu[cp] = len(first_seen_cpu)
        for gp in dim_gpu:
            if gp not in first_seen_gpu:
                first_seen_gpu[gp] = len(first_seen_gpu)

        for combo in product(dim_ssd, dim_hdd, dim_gpu, dim_cpu):
            ssd, hdd, gpu, cpu = combo
            # 规范化 1T -> 1TB, 2T -> 2TB
            if ssd.upper() == '1T':
                ssd = '1TB'
            elif ssd.upper() == '2T':
                ssd = '2TB'
            elif ssd.upper() == '4T':
                ssd = '4TB'
            if hdd.upper() == '1T':
                hdd = '1TB'
            elif hdd.upper() == '2T':
                hdd = '2TB'
            elif hdd.upper() == '4T':
                hdd = '4TB'

            res_row = {
                'detailID': '',
                '品牌ID': brand_id,
                '品牌名称': brand_name,
                '别名': alias,
                '型号': model_id,
                '型号(副名称)': '',
                '苹果小型号': '',
                '运行内存': '',
                '容量ROM': '',
                '购买渠道': '',
                '手机颜色': '',
                '网络制式': '',
                '开机价': on_price,
                '关机价': off_price,
                '开机最低价': min_price,
                '发布时间': release,
                '是否默认': '',
                '表壳材质': '',
                '表壳尺寸': '',
                '表带': '',
                '连接': '',
                '固态硬盘': ssd,
                '机械硬盘': hdd,
                '显卡型号': gpu,
                '处理器': cpu,
                '默认查询范围 (0/1)': ''
            }
            row_tuple = tuple(res_row.get(col, '') for col in TARGET_COLUMNS)
            all_combinations.add(row_tuple)

    rows_dict_list = [dict(zip(TARGET_COLUMNS, r)) for r in all_combinations]

    def alias_sort_key(val: str) -> Tuple[int, int, str]:
        s = str(val).strip()
        if not s:
            return (2, 999999, '')
        if s == '其他' or '其他' in s:
            return (1, first_seen_alias.get(s, 999999), s)
        return (0, first_seen_alias.get(s, 999999), s)

    def cpu_sort_key(val: str) -> Tuple[int, int, str]:
        s = str(val).strip()
        if not s:
            return (1, 999999, '')
        return (0, first_seen_cpu.get(s, 999999), s)

    def gpu_sort_key(val: str) -> Tuple[int, int, str]:
        s = str(val).strip()
        if not s:
            return (1, 999999, '')
        return (0, first_seen_gpu.get(s, 999999), s)

    def laptop_sort_key(d: Dict[str, Any]):
        return (
            # 1. 品牌 (品牌ID数值升序 + 品牌名称)
            parse_id_sort_key(d.get('品牌ID', '')),
            str(d.get('品牌名称', '')).strip(),
            # 2. 型号 (型号ID数值升序)
            parse_id_sort_key(d.get('型号', '')),
            # 3. 别名 (具体别名优先 -> 其他 -> 空值)
            alias_sort_key(d.get('别名', '')),
            # 4. 处理器 (保持用户录入顺序)
            cpu_sort_key(d.get('处理器', '')),
            # 5. 显卡型号 (保持用户录入顺序)
            gpu_sort_key(d.get('显卡型号', '')),
            # 6. 固态硬盘 (容量从大到小，无排后面)
            parse_disk_size_gb(d.get('固态硬盘', '')),
            # 7. 机械硬盘 (容量从大到小，无排后面)
            parse_disk_size_gb(d.get('机械硬盘', '')),
        )

    rows_dict_list.sort(key=laptop_sort_key)
    result_df = LightDataFrame(rows_dict_list, columns=TARGET_COLUMNS)
    return result_df, len(result_df)
