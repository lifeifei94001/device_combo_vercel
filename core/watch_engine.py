# -*- coding: utf-8 -*-
"""
智能手表机型排列组合算法引擎 (零 pandas 依赖极速版)
完整实现逻辑：
1. 购买渠道、手机颜色、表壳材质、表壳尺寸、表带、连接 六大维度笛卡尔积排列
2. 自动去重与智能排序 (国行优先，型号/品牌ID聚合)
3. 别名自动填充 "其他"
4. 输出标准 26 列表头格式
"""
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


def split_tolerant(val: Any) -> List[str]:
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
    return items if items else ['']


def generate_watch_combinations(records: List[Dict[str, Any]]) -> Tuple[LightDataFrame, int]:
    """
    接收多条手表录入数据，生成六维笛卡尔积组合结果 DataFrame。
    """
    all_combinations = set()

    for row in records:
        model_num = clean_id(row.get('机型编号', '') or row.get('型号', ''))
        brand_id = clean_id(row.get('品牌ID', '') or row.get('品牌编号', ''))
        brand_name = str(row.get('品牌名称', '')).strip()
        if brand_name.lower() == 'nan':
            brand_name = ''

        on_price = str(row.get('开机价', '')).strip()
        if on_price.lower() == 'nan':
            on_price = ''
        off_price = str(row.get('关机价', '')).strip()
        if off_price.lower() == 'nan':
            off_price = ''
        min_price = str(row.get('开机最低价', '')).strip()
        if min_price.lower() == 'nan':
            min_price = ''

        clean_time = clean_date(row.get('发布时间', '') or row.get('上市时间', ''))

        dim_chan = split_tolerant(row.get('购买渠道', ''))
        dim_color = split_tolerant(row.get('手机颜色', '') or row.get('颜色', ''))
        dim_mat = split_tolerant(row.get('表壳材质', ''))
        dim_size = split_tolerant(row.get('表壳尺寸', ''))
        dim_strap = split_tolerant(row.get('表带', ''))
        dim_conn = split_tolerant(row.get('连接', ''))

        for combo in product(dim_chan, dim_color, dim_mat, dim_size, dim_strap, dim_conn):
            c_chan, c_color, c_mat, c_size, c_strap, c_conn = combo

            new_row = {
                'detailID': '',
                '品牌ID': brand_id,
                '品牌名称': brand_name,
                '别名': '其他',
                '型号': model_num,
                '型号(副名称)': '',
                '苹果小型号': '',
                '运行内存': '',
                '容量ROM': '',
                '购买渠道': c_chan,
                '手机颜色': c_color,
                '网络制式': '',
                '开机价': on_price,
                '关机价': off_price,
                '开机最低价': min_price,
                '发布时间': clean_time,
                '是否默认': '',
                '表壳材质': c_mat,
                '表壳尺寸': c_size,
                '表带': c_strap,
                '连接': c_conn,
                '固态硬盘': '',
                '机械硬盘': '',
                '显卡型号': '',
                '处理器': '',
                '默认查询范围 (0/1)': 1
            }
            row_tuple = tuple(new_row.get(col, '') for col in TARGET_COLUMNS)
            all_combinations.add(row_tuple)

    rows_dict_list = [dict(zip(TARGET_COLUMNS, row_tuple)) for row_tuple in all_combinations]

    sort_fields = ["型号", "品牌ID", "购买渠道", "手机颜色", "表壳材质", "表壳尺寸", "表带", "连接"]

    def sort_key(d):
        key_parts = []
        for field in sort_fields:
            val = d.get(field, "")
            if field == "购买渠道":
                if val == "国行":
                    key_parts.append(('0', val))
                elif val == "":
                    key_parts.append(('2', ''))
                else:
                    key_parts.append(('1', val))
            else:
                if val == "":
                    key_parts.append(('1', ''))
                else:
                    key_parts.append(('0', val))
        return tuple(key_parts)

    rows_dict_list.sort(key=sort_key)
    result_df = LightDataFrame(rows_dict_list, columns=TARGET_COLUMNS)
    return result_df, len(result_df)
