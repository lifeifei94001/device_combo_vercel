# -*- coding: utf-8 -*-
"""
轻量级 DataFrame 兼容层与通用日期清洗工具 (零 pandas 依赖，100% 兼容 Vercel Serverless 与本地单测)
"""
import csv
import io
import re
from datetime import datetime
from typing import List, Dict, Any, Iterable, Optional, Union


def clean_date_str(val: Any) -> str:
    """将任意日期字符串或对象规范化为 YYYY/MM/DD，彻底摆脱 pandas.to_datetime 依赖"""
    if val is None:
        return ''
    if isinstance(val, datetime):
        return val.strftime('%Y/%m/%d')
    s = str(val).strip()
    if not s or s.lower() in ('nan', 'none', 'nat'):
        return ''
    # 去掉时间部分
    date_part = s.split(' ')[0].split('T')[0].strip()
    # 匹配 YYYY-M-D 或 YYYY/M/D 或 YYYY.M.D
    m = re.match(r'^(\d{4})[-/\.](\d{1,2})[-/\.](\d{1,2})$', date_part)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}/{mo:02d}/{d:02d}"
    # 匹配 YYYYMMDD
    m2 = re.match(r'^(\d{4})(\d{2})(\d{2})$', date_part)
    if m2:
        return f"{m2.group(1)}/{m2.group(2)}/{m2.group(3)}"
    return date_part.replace('-', '/')


class _IlocIndexer:
    def __init__(self, rows: List[Dict[str, Any]]):
        self._rows = rows

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        return self._rows[idx]


class LightSeries(list):
    """兼容 df['col'].values 与列表迭代"""
    @property
    def values(self):
        return list(self)


class LightDataFrame:
    """
    轻量级 DataFrame，完美替代 pandas.DataFrame：
    支持 .columns, .iloc, len(df), df['col'], .to_csv(path_or_buf, index=False, encoding=...)
    """
    def __init__(self, rows: Optional[List[Dict[str, Any]]] = None, columns: Optional[Iterable[str]] = None):
        self._rows: List[Dict[str, Any]] = list(rows or [])
        if columns is not None:
            self.columns: List[str] = list(columns)
        elif self._rows:
            self.columns = list(self._rows[0].keys())
        else:
            self.columns = []
        self.iloc = _IlocIndexer(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self):
        return iter(self._rows)

    def __getitem__(self, key: str) -> LightSeries:
        return LightSeries([r.get(key, '') for r in self._rows])

    def to_dicts(self) -> List[Dict[str, Any]]:
        return self._rows

    def to_csv(self, path_or_buf: Union[str, io.StringIO, io.BytesIO], index: bool = False, encoding: str = 'utf-8-sig'):
        out_str_io = io.StringIO()
        writer = csv.writer(out_str_io, lineterminator='\r\n')
        writer.writerow(self.columns)
        for row in self._rows:
            writer.writerow([row.get(col, '') for col in self.columns])
        csv_text = out_str_io.getvalue()

        if isinstance(path_or_buf, str):
            with open(path_or_buf, 'w', encoding=encoding, newline='') as f:
                f.write(csv_text)
        elif isinstance(path_or_buf, io.StringIO):
            path_or_buf.write(csv_text)
        elif isinstance(path_or_buf, io.BytesIO):
            path_or_buf.write(csv_text.encode(encoding))
        else:
            path_or_buf.write(csv_text)
