# -*- coding: utf-8 -*-
"""
Vercel Serverless API 路由中心 (Flask ASGI/WSGI 适配器 · 零 pandas 极速版)
"""
import os
import sys
import io
import base64
from flask import Flask, request, jsonify, send_file

# 确保项目根路径与 core 可被导入
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.android_engine import generate_android_combinations
from core.laptop_engine import generate_laptop_combinations
from core.watch_engine import generate_watch_combinations
from core.dict_manager import dict_manager
from core.template_manager import TemplateManager

app = Flask(__name__)


@app.route('/api/dict/data', methods=['GET'])
def get_dict_data():
    """获取字典库数据 (内置全量字典 + Excel 双保险)"""
    return jsonify({
        "brands": dict_manager.brands,
        "mobile_colors": dict_manager.mobile_colors,
        "mobile_networks": dict_manager.mobile_networks,
        "mobile_channels": dict_manager.mobile_channels,
        "mobile_rams": dict_manager.mobile_rams,
        "mobile_roms": dict_manager.mobile_roms,
        "laptop_ssds": dict_manager.laptop_ssds,
        "laptop_hdds": dict_manager.laptop_hdds,
        "laptop_cpus": dict_manager.laptop_cpus,
        "laptop_gpus": dict_manager.laptop_gpus,
        "watch_materials": dict_manager.watch_materials,
        "watch_sizes": dict_manager.watch_sizes,
        "watch_connections": dict_manager.watch_connections,
        "watch_straps": dict_manager.watch_straps,
        "watch_networks": dict_manager.watch_networks
    })


@app.route('/api/template/download', methods=['GET'])
def download_template():
    """生成并流式下载 Excel 标准模版 (纯内存流 io.BytesIO)"""
    module_id = request.args.get('module', 'android')
    if module_id == 'android':
        tmpl_filename = "安卓机型基本信息排列组合模版.xlsx"
    elif module_id == 'laptop':
        tmpl_filename = "笔记本信息排列组合模板.xlsx"
    elif module_id == 'watch':
        tmpl_filename = "手表新增模版.xlsx"
    else:
        tmpl_filename = f"{module_id}_template.xlsx"

    output = io.BytesIO()
    TemplateManager.generate_template(module_id, output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=tmpl_filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route('/api/upload_excel', methods=['POST'])
def upload_excel():
    """解析上传的 Excel/WPS 表格"""
    try:
        data = request.get_json(force=True) or {}
        module_id = data.get('module', 'android')
        base64_file = data.get('file_base64', '')

        raw_bytes = base64.b64decode(base64_file.split(',')[-1])
        ok, records, msg = TemplateManager.parse_uploaded_file(module_id, raw_bytes)
        if ok:
            return jsonify({"status": "ok", "records": records, "msg": msg})
        else:
            return jsonify({"status": "error", "msg": msg}), 400
    except Exception as e:
        return jsonify({"status": "error", "msg": f"解析异常: {str(e)}"}), 500


@app.route('/api/generate', methods=['POST'])
def generate():
    """执行笛卡尔积排列组合与结构化排序，并直接生成 Base64 下载流"""
    try:
        data = request.get_json(force=True) or {}
        module_id = data.get('module', 'android')
        records = data.get('records', [])

        if not records:
            return jsonify({"status": "error", "msg": "待处理机型列表为空！"}), 400

        if module_id == 'android':
            df, count = generate_android_combinations(records)
            csv_filename = "手机平板机型基本信息排列组合_最终导入版.csv"
        elif module_id == 'laptop':
            df, count = generate_laptop_combinations(records)
            csv_filename = "笔记本机型信息排列组合_最终导入版.csv"
        elif module_id == 'watch':
            df, count = generate_watch_combinations(records)
            csv_filename = "智能手表机型基本信息排列组合_最终导入版.csv"
        else:
            df, count = generate_android_combinations(records)
            csv_filename = "导出结果.csv"

        # 生成 utf-8-sig 格式 csv 文本流，保证 Excel / WPS 打开无乱码
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')
        csv_base64 = base64.b64encode(csv_bytes).decode('utf-8')

        return jsonify({
            "status": "ok",
            "count": count,
            "filename": csv_filename,
            "csv_base64": csv_base64
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": f"生成异常: {str(e)}"}), 500


# 兼容旧前端可能发起的 /api/records 请求（防止 404/500）
@app.route('/api/records', methods=['GET'])
def get_records_compat():
    return jsonify({"status": "ok", "data": []})


@app.route('/api/records/save', methods=['POST'])
def save_records_compat():
    return jsonify({"status": "ok", "count": 0})


@app.route('/api/records/clear', methods=['POST'])
def clear_records_compat():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(port=8765, debug=True)
