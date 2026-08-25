# -*- coding: utf-8 -*-
"""
模板管理与智能精确对齐导入引擎 (支持文件路径与 BytesIO 内存流)
"""
import os
import io
import re
import pandas as pd
from typing import List, Dict, Any, Tuple
from config.constants import (
    ANDROID_INPUT_COLUMNS, ANDROID_SAMPLE_DATA,
    LAPTOP_INPUT_COLUMNS, LAPTOP_SAMPLE_DATA,
    WATCH_INPUT_COLUMNS, WATCH_SAMPLE_DATA
)

class TemplateManager:
    @staticmethod
    def generate_template(module_id: str, output_target: Any) -> bool:
        """生成标准 Excel 模版文件 (支持保存到文件路径或 BytesIO 内存流)"""
        try:
            if isinstance(output_target, str):
                os.makedirs(os.path.dirname(output_target), exist_ok=True)

            if module_id == "android":
                df = pd.DataFrame(ANDROID_SAMPLE_DATA, columns=ANDROID_INPUT_COLUMNS)
            elif module_id == "laptop":
                df = pd.DataFrame(LAPTOP_SAMPLE_DATA, columns=LAPTOP_INPUT_COLUMNS)
            elif module_id == "watch":
                df = pd.DataFrame(WATCH_SAMPLE_DATA, columns=WATCH_INPUT_COLUMNS)
            else:
                df = pd.DataFrame(ANDROID_SAMPLE_DATA, columns=ANDROID_INPUT_COLUMNS)

            with pd.ExcelWriter(output_target, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="机型配置填报模版")
                worksheet = writer.sheets["机型配置填报模版"]
                for col in worksheet.columns:
                    max_len = max(len(str(cell.value or '')) for cell in col)
                    col_letter = col[0].column_letter
                    worksheet.column_dimensions[col_letter].width = max(max_len * 2, 14)
            return True
        except Exception as e:
            print(f"生成模板失败: {e}")
            return False

    @staticmethod
    def parse_uploaded_file(module_id: str, file_path_or_bytes: Any) -> Tuple[bool, List[Dict[str, Any]], str]:
        """两趟严格对齐解析用户上传的 WPS / Excel 表格"""
        try:
            if isinstance(file_path_or_bytes, bytes):
                df = pd.read_excel(io.BytesIO(file_path_or_bytes), dtype=str)
            elif isinstance(file_path_or_bytes, str):
                if file_path_or_bytes.endswith('.csv'):
                    df = pd.read_csv(file_path_or_bytes, dtype=str)
                else:
                    df = pd.read_excel(file_path_or_bytes, dtype=str)
            else:
                return False, [], "未知的文件格式"

            df = df.fillna('')
            df.columns = [str(c).strip() for c in df.columns]

            def normalize_str(s):
                return re.sub(r'[\s\(\)\[\]（）_\-]', '', str(s)).lower()

            def find_col_val(row, aliases):
                for alias in aliases:
                    for col in row.index:
                        if str(col).strip().lower() == alias.strip().lower():
                            v = str(row[col]).strip()
                            if v: return v
                for alias in aliases:
                    norm_alias = normalize_str(alias)
                    for col in row.index:
                        if normalize_str(col) == norm_alias:
                            v = str(row[col]).strip()
                            if v: return v
                return ""

            records = []
            if module_id == "android":
                for _, row in df.iterrows():
                    rec = {
                        '品牌编号': find_col_val(row, ['品牌编号', '品牌ID', '品牌代码']),
                        '品牌名称': find_col_val(row, ['品牌名称', '品牌', '厂商']),
                        '机型编号': find_col_val(row, ['机型编号', '机型ID', '型号', '型号ID']),
                        '内存': find_col_val(row, ['内存', '内存配置', '运行内存']),
                        '购买渠道': find_col_val(row, ['购买渠道', '渠道', '版本']),
                        '网络制式': find_col_val(row, ['网络制式', '网络', '制式']),
                        '颜色': find_col_val(row, ['颜色', '手机颜色', '机型颜色']),
                        '小型号': find_col_val(row, ['小型号', '苹果小型号', '副名称']),
                        '上市时间': find_col_val(row, ['上市时间', '发布时间', '时间', '上市日期']),
                        '开机价': find_col_val(row, ['开机价', '开机价格']),
                        '关机价': find_col_val(row, ['关机价', '关机价格']),
                        '开机最低价': find_col_val(row, ['开机最低价', '最低价', '开机最低'])
                    }
                    if rec.get('品牌编号') or rec.get('机型编号') or rec.get('品牌名称'):
                        records.append(rec)

            elif module_id == "laptop":
                for _, row in df.iterrows():
                    rec = {
                        '品牌ID': find_col_val(row, ['品牌ID', '品牌编号']),
                        '品牌名称': find_col_val(row, ['品牌名称', '品牌', '厂商']),
                        '别名': find_col_val(row, ['别名', '副名称', '机型别名']),
                        '型号': find_col_val(row, ['型号', '型号ID', '机型编号']),
                        '固态硬盘': find_col_val(row, ['固态硬盘', '固态', 'SSD']),
                        '机械硬盘': find_col_val(row, ['机械硬盘', '机械', 'HDD']),
                        '显卡型号': find_col_val(row, ['显卡型号', '显卡', 'GPU']),
                        '处理器': find_col_val(row, ['处理器', 'CPU', '处理器型号']),
                        '开机价': find_col_val(row, ['开机价', '开机价格']),
                        '关机价': find_col_val(row, ['关机价', '关机价格']),
                        '开机最低价': find_col_val(row, ['开机最低价', '最低价', '开机最低']),
                        '发布时间': find_col_val(row, ['发布时间', '上市时间', '时间'])
                    }
                    if rec.get('品牌ID') or rec.get('型号') or rec.get('品牌名称'):
                        records.append(rec)

            elif module_id == "watch":
                for _, row in df.iterrows():
                    rec = {
                        '机型编号': find_col_val(row, ['机型编号', '型号ID']),
                        '品牌ID': find_col_val(row, ['品牌ID', '品牌编号']),
                        '品牌名称': find_col_val(row, ['品牌名称', '品牌', '厂商']),
                        '型号': find_col_val(row, ['型号', '别名', '机型名称', '副名称']),
                        '购买渠道': find_col_val(row, ['购买渠道', '渠道', '版本']),
                        '手机颜色': find_col_val(row, ['手机颜色', '颜色', '机型颜色']),
                        '表壳材质': find_col_val(row, ['表壳材质', '材质']),
                        '表壳尺寸': find_col_val(row, ['表壳尺寸', '尺寸']),
                        '表带': find_col_val(row, ['表带', '表带类型']),
                        '连接': find_col_val(row, ['连接', '连接方式']),
                        '开机价': find_col_val(row, ['开机价', '开机价格']),
                        '关机价': find_col_val(row, ['关机价', '关机价格']),
                        '开机最低价': find_col_val(row, ['开机最低价', '最低价', '开机最低']),
                        '发布时间': find_col_val(row, ['发布时间', '上市时间', '时间'])
                    }
                    if rec.get('机型编号') or rec.get('品牌ID') or rec.get('品牌名称'):
                        records.append(rec)

            if not records:
                return False, [], "文件中未检测到有效机型数据，请核对表头。"

            return True, records, f"成功精准对齐并导入 {len(records)} 条机型配置数据！"
        except Exception as e:
            return False, [], f"解析表格失败: {str(e)}"
