# -*- coding: utf-8 -*-
"""
笔记本机型排列组合算法引擎 (已加入全链路自动去重)
"""
import pandas as pd
from itertools import product
from typing import List, Dict, Any, Tuple
from config.constants import TARGET_COLUMNS

def clean_date(val: Any) -> str:
    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return ''
    try:
        return pd.to_datetime(s).strftime('%Y/%m/%d')
    except Exception:
        return s.split(' ')[0].replace('-', '/')

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

def generate_laptop_combinations(records: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, int]:
    """
    接收多条笔记本录入数据，生成四维笛卡尔积排列组合结果 DataFrame（自动去重）。
    """
    all_combinations = set()
    COMBO_FIELDS = ['固态硬盘', '机械硬盘', '显卡型号', '处理器']

    for row in records:
        brand_id = clean_id(row.get('品牌ID', ''))
        brand_name = str(row.get('品牌名称', '')).strip()
        if brand_name.lower() == 'nan': brand_name = ''
        alias = str(row.get('别名', '')).strip()
        if alias.lower() == 'nan': alias = ''
        model_id = clean_id(row.get('型号', ''))
        
        on_price = str(row.get('开机价', '')).strip()
        if on_price.lower() == 'nan': on_price = ''
        off_price = str(row.get('关机价', '')).strip()
        if off_price.lower() == 'nan': off_price = ''
        min_price = str(row.get('开机最低价', '')).strip()
        if min_price.lower() == 'nan': min_price = ''
        
        release = clean_date(row.get('发布时间', ''))

        dims = [split_tolerant_pause(row.get(f, '')) for f in COMBO_FIELDS]

        for combo in product(*dims):
            ssd, hdd, gpu, cpu = combo

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
    result_df = pd.DataFrame(rows_dict_list, columns=TARGET_COLUMNS)
    return result_df, len(result_df)
