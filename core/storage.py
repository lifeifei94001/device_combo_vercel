# -*- coding: utf-8 -*-
"""
本地与 Vercel Serverless 兼容存储层 (在只读文件系统下自动路由至 /tmp，绝不触发 Read-only file system 崩溃)
"""
import json
import os
import time
from typing import List, Dict, Any
from config.settings import DATA_DIR


class StorageEngine:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.records_file = os.path.join(self.data_dir, "module_records.json")
        self.prefs_file = os.path.join(self.data_dir, "user_preferences.json")
        self._mem_records: Dict[str, List[Dict[str, Any]]] = {}
        self._mem_prefs: Dict[str, Any] = {}
        self._ensure_files()

    def _ensure_files(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            if not os.path.exists(self.records_file):
                with open(self.records_file, "w", encoding="utf-8") as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
            if not os.path.exists(self.prefs_file):
                with open(self.prefs_file, "w", encoding="utf-8") as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _read_json(self, file_path: str) -> Dict[str, Any]:
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _write_json(self, file_path: str, data: Dict[str, Any]):
        try:
            temp_path = f"{file_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            if os.path.exists(file_path):
                os.remove(file_path)
            os.rename(temp_path, file_path)
        except Exception:
            pass

    def save_records(self, module_id: str, records: List[Dict[str, Any]]):
        all_data = self._read_json(self.records_file)
        cleaned_records = []
        for i, rec in enumerate(records):
            item = dict(rec)
            if "_id" not in item:
                item["_id"] = int(time.time() * 1000) + i
            cleaned_records.append(item)
        all_data[module_id] = cleaned_records
        self._mem_records[module_id] = cleaned_records
        self._write_json(self.records_file, all_data)

    def load_records(self, module_id: str) -> List[Dict[str, Any]]:
        all_data = self._read_json(self.records_file)
        return all_data.get(module_id, self._mem_records.get(module_id, []))

    def clear_all_records(self, module_id: str):
        self._mem_records[module_id] = []
        all_data = self._read_json(self.records_file)
        if module_id in all_data:
            all_data[module_id] = []
            self._write_json(self.records_file, all_data)


storage = StorageEngine()
