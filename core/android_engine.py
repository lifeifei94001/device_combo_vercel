# -*- coding: utf-8 -*-
"""
安卓与平板机型排列组合算法引擎 (已加入全链路去重与价格规范化)
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

def split_tolerant_space(val: Any) -> List[str]:
    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return ['']
    items = [i.strip() for i in s.split(' ') if i.strip()]
    items = list(dict.fromkeys(items))
    return items if items else ['']

def split_tolerant_color(val: Any) -> List[str]:
    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return ['']
    if '、' in s:
        items = [i.strip() for i in s.split('、') if i.strip()]
    elif ' ' in s:
        items = [i.strip() for i in s.split(' ') if i.strip()]
    elif ',' in s:
        items = [i.strip() for i in s.split(',') if i.strip()]
    else:
        items = [s]
    items = list(dict.fromkeys(items))
    return items if items else ['']

def generate_android_combinations(records: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, int]:
    """
    接收多条录入数据，生成笛卡尔积排列组合结果 DataFrame（自动去重）。
    """
    all_combinations = set()

    for row in records:
        brand_id = clean_id(row.get('品牌编号', ''))
        brand_name = str(row.get('品牌名称', '')).strip()
        if brand_name.lower() == 'nan': brand_name = ''
        model_id = clean_id(row.get('机型编号', ''))
        clean_time = clean_date(row.get('上市时间', ''))
        
        on_price = str(row.get('开机价', '')).strip()
        if on_price.lower() == 'nan': on_price = ''
        off_price = str(row.get('关机价', '')).strip()
        if off_price.lower() == 'nan': off_price = ''
        min_price = str(row.get('开机最低价', '')).strip()
        if min_price.lower() == 'nan': min_price = ''

        dim_mem = split_tolerant_space(row.get('内存', ''))
        dim_chan = split_tolerant_space(row.get('购买渠道', ''))
        dim_net = split_tolerant_space(row.get('网络制式', ''))
        dim_color = split_tolerant_color(row.get('颜色', ''))

        # 小型号不拆分
        v_small = str(row.get('小型号', '')).strip()
        if not v_small or v_small.lower() == 'nan':
            dim_small = ['']
        else:
            dim_small = [v_small]

        for combo in product(dim_mem, dim_chan, dim_color, dim_net, dim_small):
            c_mem, c_chan, c_color, c_net, c_small = combo

            ram, rom = "", ""
            if "+" in c_mem:
                m_parts = c_mem.split('+')
                ram, rom = m_parts[0].strip(), m_parts[1].strip()
                # 规范化 1T -> 1TB
                if rom.upper() == '1T': rom = '1TB'
                elif rom.upper() == '2T': rom = '2TB'
            else:
                ram = c_mem.strip()

            if "其他" in c_chan:
                sub_name = "其他"
            else:
                sub_name = c_small.strip()
            alias = sub_name

            res_row = {
                'detailID': "",
                '品牌ID': brand_id,
                '品牌名称': brand_name,
                '别名': alias,
                '型号': model_id,
                '型号(副名称)': sub_name,
                '苹果小型号': "",
                '运行内存': ram,
                '容量ROM': rom,
                '购买渠道': c_chan,
                '手机颜色': c_color,
                '网络制式': c_net,
                '开机价': on_price,
                '关机价': off_price,
                '开机最低价': min_price,
                '发布时间': clean_time,
                '是否默认': "",
                '表壳材质': "",
                '表壳尺寸': "",
                '表带': "",
                '连接': "",
                '固态硬盘': "",
                '机械硬盘': "",
                '显卡型号': "",
                '处理器': "",
                '默认查询范围 (0/1)': 1
            }
            row_tuple = tuple(res_row.get(col, "") for col in TARGET_COLUMNS)
            all_combinations.add(row_tuple)

    rows_dict_list = [dict(zip(TARGET_COLUMNS, r)) for r in all_combinations]
    result_df = pd.DataFrame(rows_dict_list, columns=TARGET_COLUMNS)
    return result_df, len(result_df)
