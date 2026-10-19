# -*- coding: utf-8 -*-
"""
安卓与平板机型排列组合算法引擎 (全链路去重 + 价格规范化 + 八级结构化排序)
排序规则：
1. 品牌 (品牌ID数值升序 + 品牌名称)
2. 型号 (机型编号数值升序)
3. 副型号 (型号(副名称)：具体副型号优先 -> "其他"次之 -> 空值最后，同级保持录入顺序)
4. 购买渠道 ("国行"第一 -> 其他具名渠道次之 -> 含"其他"的渠道靠后 -> 空值最后，同级保持录入顺序)
5. 网络制式 (全网通 > 5G > 4G > WIFI/WiFi > 蜂窝版/插卡版 > 其他录入顺序 > 空值)
6. 颜色 (严格保持用户录入先后顺序 -> 空值最后)
7. 内存 (容量ROM：按实际存储容量从大到小，如 2TB > 1TB > 512G > 256G > 128G > 64G)
8. 运存 (运行内存：按实际运行内存从大到小，如 32G > 24G > 16G > 12G > 8G > 6G > 4G)
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


def parse_id_sort_key(val: Any) -> Tuple[int, int, str]:
    """
    ID / 编号智能升序键：
    - 纯数字按整数大小升序 (如 27 排在 101 前面)
    - 含字母/符号的编号按字符串升序
    - 空值排最后
    """
    s = str(val).strip()
    if not s:
        return (2, 0, '')
    if s.isdigit():
        return (0, int(s), '')
    return (1, 0, s)


def parse_storage_size_gb(val: Any) -> Tuple[int, float, str]:
    """
    容量从大到小降序键 (兼容 TB/T/GB/G/MB/M 及多段组合)：
    - 有效容量返回 (0, -total_gb, s)，实现从大到小排列 (如 1TB=1024G > 512G > 256G > 128G)
    - 非数值文本 (如 "无") 返回 (1, 0.0, s)
    - 空字符串返回 (2, 0.0, '')
    """
    s = str(val).strip()
    if not s:
        return (2, 0.0, '')
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


NETWORK_PRIORITY_MAP = {
    '全网通': 0,
    '5G': 1,
    '4G': 2,
    'WIFI': 3,
    'WI-FI': 3,
    'WLAN': 3,
    '蜂窝版': 4,
    '插卡版': 4,
    '5G全网通': 0,
    '4G全网通': 2,
}


def generate_android_combinations(records: List[Dict[str, Any]]) -> Tuple[LightDataFrame, int]:
    """
    接收多条录入数据，生成笛卡尔积排列组合结果 DataFrame（自动去重 + 八级结构化排序）。
    """
    all_combinations = set()

    # 记录各维度首次出现的顺序，保证同优先级下严格维持用户录入先后顺序
    first_seen_sub: Dict[str, int] = {}
    first_seen_chan: Dict[str, int] = {}
    first_seen_net: Dict[str, int] = {}
    first_seen_color: Dict[str, int] = {}

    for row in records:
        brand_id = clean_id(row.get('品牌编号', ''))
        brand_name = str(row.get('品牌名称', '')).strip()
        if brand_name.lower() == 'nan':
            brand_name = ''
        model_id = clean_id(row.get('机型编号', ''))
        clean_time = clean_date(row.get('上市时间', ''))

        on_price = str(row.get('开机价', '')).strip()
        if on_price.lower() == 'nan':
            on_price = ''
        off_price = str(row.get('关机价', '')).strip()
        if off_price.lower() == 'nan':
            off_price = ''
        min_price = str(row.get('开机最低价', '')).strip()
        if min_price.lower() == 'nan':
            min_price = ''

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

        for ch in dim_chan:
            if ch not in first_seen_chan:
                first_seen_chan[ch] = len(first_seen_chan)
        for nt in dim_net:
            if nt not in first_seen_net:
                first_seen_net[nt] = len(first_seen_net)
        for cl in dim_color:
            if cl not in first_seen_color:
                first_seen_color[cl] = len(first_seen_color)

        for combo in product(dim_mem, dim_chan, dim_color, dim_net, dim_small):
            c_mem, c_chan, c_color, c_net, c_small = combo

            ram, rom = "", ""
            if "+" in c_mem:
                m_parts = c_mem.split('+')
                ram, rom = m_parts[0].strip(), m_parts[1].strip()
                # 规范化 1T -> 1TB
                if rom.upper() == '1T':
                    rom = '1TB'
                elif rom.upper() == '2T':
                    rom = '2TB'
                elif rom.upper() == '4T':
                    rom = '4TB'
            else:
                ram = c_mem.strip()

            if "其他" in c_chan:
                sub_name = "其他"
            else:
                sub_name = c_small.strip()
            alias = sub_name

            if sub_name not in first_seen_sub:
                first_seen_sub[sub_name] = len(first_seen_sub)

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

    def sub_model_sort_key(sub_val: str) -> Tuple[int, int, str]:
        s = str(sub_val).strip()
        if not s:
            return (2, 999999, '')
        if s == '其他' or '其他' in s:
            return (1, first_seen_sub.get(s, 999999), s)
        return (0, first_seen_sub.get(s, 999999), s)

    def channel_sort_key(chan_val: str) -> Tuple[int, int, str]:
        s = str(chan_val).strip()
        if not s:
            return (3, 999999, '')
        if s == '国行':
            return (0, 0, s)
        if '其他' in s:
            return (2, first_seen_chan.get(s, 999999), s)
        return (1, first_seen_chan.get(s, 999999), s)

    def network_sort_key(net_val: str) -> Tuple[int, int, str]:
        s = str(net_val).strip()
        if not s:
            return (9, 999999, '')
        prio = NETWORK_PRIORITY_MAP.get(s.upper(), 5)
        return (prio, first_seen_net.get(s, 999999), s)

    def color_sort_key(color_val: str) -> Tuple[int, int, str]:
        s = str(color_val).strip()
        if not s:
            return (1, 999999, '')
        return (0, first_seen_color.get(s, 999999), s)

    def android_sort_key(d: Dict[str, Any]):
        return (
            # 1. 品牌 (品牌ID数值升序 + 品牌名称)
            parse_id_sort_key(d.get('品牌ID', '')),
            str(d.get('品牌名称', '')).strip(),
            # 2. 型号 (机型编号数值升序)
            parse_id_sort_key(d.get('型号', '')),
            # 3. 副型号 (具体副型号优先 -> 其他次之 -> 空值置后)
            sub_model_sort_key(d.get('型号(副名称)', '')),
            # 4. 购买渠道 (国行第一 -> 具名渠道 -> 其他版本 -> 空值)
            channel_sort_key(d.get('购买渠道', '')),
            # 5. 网络制式 (全网通 > 5G > 4G > 其他录入顺序)
            network_sort_key(d.get('网络制式', '')),
            # 6. 颜色 (严格保持用户录入先后顺序)
            color_sort_key(d.get('手机颜色', '')),
            # 7. 内存 容量ROM (从大到小)
            parse_storage_size_gb(d.get('容量ROM', '')),
            # 8. 运存 运行内存 (从大到小)
            parse_storage_size_gb(d.get('运行内存', '')),
        )

    rows_dict_list.sort(key=android_sort_key)
    result_df = LightDataFrame(rows_dict_list, columns=TARGET_COLUMNS)
    return result_df, len(result_df)
