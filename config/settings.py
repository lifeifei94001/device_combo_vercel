# -*- coding: utf-8 -*-
"""
全局运行配置与路径管理 (Vercel Serverless 只读文件系统自适应版)
"""
import os
import sys
import tempfile

APP_NAME = "3C Matrix - 3C数码信息排列组合工具箱"
APP_VERSION = "v3.5.0"
WINDOW_SIZE = "1360x880"

if getattr(sys, 'frozen', False):
    RESOURCE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    BASE_DIR = os.path.dirname(sys.executable)
else:
    RESOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR = RESOURCE_DIR

# 在 Vercel 等只读 Serverless 环境下自动切换到 /tmp
if os.environ.get("VERCEL") or not os.access(BASE_DIR, os.W_OK):
    WRITABLE_ROOT = os.path.join(tempfile.gettempdir(), "3c_matrix")
else:
    WRITABLE_ROOT = BASE_DIR

DATA_DIR = os.path.join(WRITABLE_ROOT, "data")
TEMPLATES_DIR = os.path.join(WRITABLE_ROOT, "templates")

try:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
except Exception:
    pass

DB_FILE = os.path.join(DATA_DIR, "app_memory.json")
APPEARANCE_MODE = "Light"
COLOR_THEME = "blue"
