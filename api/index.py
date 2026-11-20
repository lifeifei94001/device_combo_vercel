# -*- coding: utf-8 -*-
"""
Vercel Serverless API 路由中心 (Flask ASGI/WSGI 适配器 · 零 pandas 极速版)
"""
import os
import sys
import io
import time
import base64
from urllib.parse import unquote, urlparse
import requests
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
from core.turso_db import turso_store

app = Flask(__name__)

_VALID_MODULES = {"android", "laptop", "watch"}


def _normalize_module(raw: str) -> str:
    m = (raw or "android").strip().lower()
    return m if m in _VALID_MODULES else "android"


@app.errorhandler(Exception)
def handle_unexpected_error(err):
    return jsonify({"status": "error", "msg": str(err)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """检查服务与 Turso / SQLite 存储引擎连通性"""
    try:
        info = turso_store.check_health()
        return jsonify(info)
    except Exception as e:
        return jsonify({"status": "error", "backend": turso_store.get_backend_info().get("mode"), "msg": str(e)}), 500


@app.route('/api/dict/data', methods=['GET'])
def get_dict_data():
    """获取全量字典库数据 (直接从 Turso / SQLite 数据库读取)"""
    data = dict_manager.to_dict()
    data["backend"] = turso_store.get_backend_info().get("mode")
    return jsonify(data)


@app.route('/api/dict/add', methods=['POST'])
def add_dict_item():
    """在线新增字典项并持久化至 Turso / SQLite"""
    try:
        data = request.get_json(force=True) or {}
        category = data.get('category', '')
        item_value = data.get('item_value', '')
        item_key = data.get('item_key', '')
        added = turso_store.add_dict_item(category, item_value, item_key)
        dict_manager.load_dictionary(force=True)
        return jsonify({"status": "ok", "item": added})
    except ValueError as ve:
        return jsonify({"status": "error", "msg": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "msg": f"新增字典项失败: {str(e)}"}), 500


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
        module_id = _normalize_module(data.get('module', 'android'))
        base64_file = data.get('file_base64', '')

        raw_bytes = base64.b64decode(base64_file.split(',')[-1])
        ok, records, msg = TemplateManager.parse_uploaded_file(module_id, raw_bytes)
        if ok:
            try:
                turso_store.append_log(
                    module_id,
                    "import",
                    record_count=len(records),
                    output_count=0,
                    detail=f"Excel 导入解析成功 {len(records)} 条记录",
                )
            except Exception:
                pass
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
        module_id = _normalize_module(data.get('module', 'android'))
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

        try:
            turso_store.append_log(
                module_id,
                "generate",
                record_count=len(records),
                output_count=count,
                detail=f"生成 {count} 行排列组合并导出 {csv_filename}",
            )
        except Exception:
            pass

        return jsonify({
            "status": "ok",
            "count": count,
            "filename": csv_filename,
            "csv_base64": csv_base64
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": f"生成异常: {str(e)}"}), 500


@app.route('/api/records', methods=['GET'])
def get_records():
    """读取 Turso / SQLite 中保存的模块机型列表或全模块摘要"""
    try:
        raw_mod = (request.args.get('module') or 'android').strip().lower()
        backend_mode = turso_store.get_backend_info().get("mode")
        if raw_mod == 'all':
            summary = turso_store.load_all_summary()
            return jsonify({"status": "ok", "backend": backend_mode, "summary": summary})
        module_id = _normalize_module(raw_mod)
        records = turso_store.load_records(module_id)
        return jsonify({
            "status": "ok",
            "module": module_id,
            "backend": backend_mode,
            "records": records,
            "data": records,
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": f"读取云端记录失败: {str(e)}"}), 500


@app.route('/api/records/save', methods=['POST'])
def save_records():
    """原子化保存指定模块的机型列表至 Turso / SQLite"""
    try:
        data = request.get_json(force=True) or {}
        module_id = _normalize_module(data.get('module', 'android'))
        records = data.get('records', [])
        if not isinstance(records, list):
            return jsonify({"status": "error", "msg": "records 必须为数组"}), 400
        skip_log = bool(data.get('skip_log', False))
        log_action = None if skip_log else (data.get('action') or 'save')
        log_detail = str(data.get('detail') or '')
        count = turso_store.save_records(
            module_id,
            records,
            log_action=log_action,
            log_detail=log_detail,
        )
        return jsonify({
            "status": "ok",
            "module": module_id,
            "backend": turso_store.get_backend_info().get("mode"),
            "count": count,
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": f"保存云端记录失败: {str(e)}"}), 500


@app.route('/api/records/clear', methods=['POST'])
def clear_records():
    """清空指定模块的云端机型列表"""
    try:
        data = request.get_json(force=True) or {}
        module_id = _normalize_module(data.get('module', 'android'))
        turso_store.clear_records(module_id)
        return jsonify({
            "status": "ok",
            "module": module_id,
            "backend": turso_store.get_backend_info().get("mode"),
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": f"清空云端记录失败: {str(e)}"}), 500


@app.route('/api/logs', methods=['GET'])
def get_operation_logs():
    """获取云端操作与导出历史日志"""
    try:
        limit = request.args.get('limit', 100)
        logs = turso_store.list_logs(limit=int(limit))
        return jsonify({
            "status": "ok",
            "backend": turso_store.get_backend_info().get("mode"),
            "logs": logs,
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": f"读取操作日志失败: {str(e)}"}), 500


@app.route('/api/logs/clear', methods=['POST'])
def clear_operation_logs():
    """清空云端操作日志"""
    try:
        turso_store.clear_logs()
        return jsonify({"status": "ok", "backend": turso_store.get_backend_info().get("mode")})
    except Exception as e:
        return jsonify({"status": "error", "msg": f"清空日志失败: {str(e)}"}), 500


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """获取云端多端同步偏好设置（如大将怪兽摧毁模式开关等）"""
    try:
        settings = turso_store.get_all_settings()
        return jsonify({
            "status": "ok",
            "backend": turso_store.get_backend_info().get("mode"),
            "settings": settings,
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": f"读取云端配置失败: {str(e)}"}), 500


@app.route('/api/settings', methods=['POST'])
def save_settings():
    """保存或更新全局偏好设置（跨浏览器实时同步）"""
    try:
        data = request.get_json(force=True) or {}
        incoming_settings = data.get('settings') if 'settings' in data else data
        if not isinstance(incoming_settings, dict):
            return jsonify({"status": "error", "msg": "settings 必须为 JSON 对象"}), 400
        saved = turso_store.set_settings(incoming_settings)
        return jsonify({
            "status": "ok",
            "backend": turso_store.get_backend_info().get("mode"),
            "settings": saved,
        })
    except Exception as e:
        return jsonify({"status": "error", "msg": f"保存云端配置失败: {str(e)}"}), 500


_PROXY_SESSION = requests.Session()
_PROXY_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
}
_PROXY_ALLOWLIST = {
    'v.api.aa1.cn',
    'api.yujn.cn',
    '60s.viki.moe',
    'wttr.in',
    'whois.pconline.com.cn',
    'ipwho.is',
    'ipapi.co',
    'ipinfo.io',
    'ip-api.com',
    'api.ipify.org',
    'api.open-meteo.com',
    'v1.hitokoto.cn',
    'api.thecatapi.com',
    'cataas.com',
    'dog.ceo',
}

_WEATHER_DESC_ZH = {
    'clear': ('晴朗', '☀️'),
    'sunny': ('晴天', '☀️'),
    'partly cloudy': ('多云', '⛅'),
    'cloudy': ('阴天', '☁️'),
    'overcast': ('阴', '☁️'),
    'mist': ('薄雾', '🌫️'),
    'fog': ('大雾', '🌫️'),
    'haze': ('霾', '🌫️'),
    'light drizzle': ('毛毛雨', '🌦️'),
    'patchy light drizzle': ('零星小雨', '🌦️'),
    'patchy rain possible': ('局部有雨', '🌦️'),
    'patchy rain nearby': ('附近有雨', '🌦️'),
    'light rain': ('小雨', '🌦️'),
    'light rain shower': ('小阵雨', '🌦️'),
    'moderate rain': ('中雨', '🌧️'),
    'heavy rain': ('大雨', '🌧️'),
    'torrential rain shower': ('暴雨', '⛈️'),
    'thundery outbreaks possible': ('可能有雷雨', '⛈️'),
    'thunderstorm': ('雷阵雨', '⛈️'),
    'light snow': ('小雪', '❄️'),
    'moderate snow': ('中雪', '❄️'),
    'heavy snow': ('大雪', '❄️'),
}


def _translate_weather_desc(raw_desc: str) -> tuple:
    text = (raw_desc or '').strip()
    low = text.lower()
    if low in _WEATHER_DESC_ZH:
        return _WEATHER_DESC_ZH[low]
    for key, pair in _WEATHER_DESC_ZH.items():
        if key in low:
            return pair
    if any(ch in text for ch in ('雷', '暴')):
        return text, '⛈️'
    if '雨' in text or 'rain' in low or 'drizzle' in low:
        return text or '有雨', '🌧️'
    if '雪' in text or 'snow' in low:
        return text or '降雪', '❄️'
    if '雾' in text or '霾' in text or 'fog' in low or 'mist' in low:
        return text or '有雾', '🌫️'
    if '阴' in text or 'cloud' in low:
        return text or '多云', '⛅'
    if '晴' in text or 'sun' in low or 'clear' in low:
        return text or '晴天', '☀️'
    return text or '晴朗', '🌤️'


def _extract_client_ip() -> str:
    xff = (request.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
    if xff and not xff.startswith(('127.', '10.', '192.168.', '::1')):
        return xff
    real_ip = (request.headers.get('X-Real-IP') or '').strip()
    if real_ip and not real_ip.startswith(('127.', '10.', '192.168.', '::1')):
        return real_ip
    return ''


def _resolve_client_geo() -> dict:
    """结合 Vercel Edge 请求头与第三方 IP 库精准识别客户端地理位置"""
    client_ip = _extract_client_ip()
    v_city = unquote(request.headers.get('X-Vercel-IP-City') or '').strip()
    v_region = unquote(request.headers.get('X-Vercel-IP-Country-Region') or '').strip()
    v_country = unquote(request.headers.get('X-Vercel-IP-Country') or '').strip()
    v_lat = (request.headers.get('X-Vercel-IP-Latitude') or '').strip()
    v_lon = (request.headers.get('X-Vercel-IP-Longitude') or '').strip()

    geo = {
        'ip': client_ip or '',
        'city': v_city,
        'region': v_region,
        'country': v_country,
        'isp': '',
        'lat': v_lat,
        'lon': v_lon,
        'source': 'vercel-edge' if v_city else '',
    }

    # 若 Vercel 边际头已提供城市/经纬度，中国大陆城市补充中文归属地展示或直接返回
    if v_city and (not client_ip or v_country != 'CN'):
        return geo

    # 对国内 IP 优先使用太平洋网络 IP 库（中文省市/运营商极准），若指定 client_ip 则精准查该 IP
    try:
        pc_url = 'https://whois.pconline.com.cn/ipJson.jsp?json=true'
        if client_ip:
            pc_url += f'&ip={client_ip}'
        resp = _PROXY_SESSION.get(pc_url, headers=_PROXY_HEADERS, timeout=4.5)
        if resp.status_code == 200:
            resp.encoding = 'gbk'
            pc = resp.json()
            city_raw = (pc.get('city') or '').strip()
            pro_raw = (pc.get('pro') or '').strip()
            addr_raw = (pc.get('addr') or '').strip()
            ip_val = (pc.get('ip') or client_ip or '').strip()
            if city_raw or pro_raw:
                clean_city = city_raw.rstrip('市') or pro_raw.rstrip('省市')
                geo.update({
                    'ip': ip_val,
                    'city': clean_city,
                    'region': pro_raw,
                    'country': '中国',
                    'isp': addr_raw,
                    'source': 'pconline',
                })
                if v_lat and v_lon:
                    geo['lat'] = v_lat
                    geo['lon'] = v_lon
                return geo
    except Exception:
        pass

    if geo['city']:
        return geo

    # 兜底：ipwho.is / ip-api.com
    try:
        target = f'https://ipwho.is/{client_ip}' if client_ip else 'https://ipwho.is/'
        r = _PROXY_SESSION.get(target, headers=_PROXY_HEADERS, timeout=5)
        if r.status_code == 200:
            j = r.json()
            if j.get('success', True) and j.get('city'):
                return {
                    'ip': j.get('ip') or client_ip,
                    'city': j.get('city') or '',
                    'region': j.get('region') or '',
                    'country': j.get('country') or '',
                    'isp': (j.get('connection') or {}).get('isp') or '',
                    'lat': str(j.get('latitude') or ''),
                    'lon': str(j.get('longitude') or ''),
                    'source': 'ipwho.is',
                }
    except Exception:
        pass

    return {
        'ip': client_ip or '127.0.0.1',
        'city': '广州',
        'region': '广东省',
        'country': '中国',
        'isp': '本地默认节点',
        'lat': '23.1291',
        'lon': '113.2644',
        'source': 'fallback',
    }


@app.route('/api/geo', methods=['GET'])
def get_client_geo():
    """返回客户端公网 IP 与地理位置"""
    try:
        return jsonify({"status": "ok", **_resolve_client_geo()})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route('/api/weather', methods=['GET'])
def get_weather():
    """根据 IP 定位（或传入经纬度/城市）自动获取中文实时天气"""
    city_arg = (request.args.get('city') or '').strip()
    lat_arg = (request.args.get('lat') or '').strip()
    lon_arg = (request.args.get('lon') or '').strip()

    geo = _resolve_client_geo() if not (city_arg or (lat_arg and lon_arg)) else {
        'city': city_arg or '当前位置',
        'region': '',
        'country': '',
        'ip': _extract_client_ip(),
        'lat': lat_arg,
        'lon': lon_arg,
        'source': 'client-param',
    }

    display_city = geo.get('city') or geo.get('region') or '广州'
    query_loc = (
        f"{geo['lat']},{geo['lon']}"
        if geo.get('lat') and geo.get('lon')
        else display_city
    )

    # 1. 主数据源：wttr.in
    try:
        wttr_url = f"https://wttr.in/{query_loc}?format=j1&lang=zh"
        r = _PROXY_SESSION.get(wttr_url, headers=_PROXY_HEADERS, timeout=6)
        if r.status_code == 200:
            data = r.json()
            cur = (data.get('current_condition') or [{}])[0]
            temp = cur.get('temp_C')
            if temp is not None:
                raw_desc = ''
                if cur.get('lang_zh'):
                    raw_desc = (cur['lang_zh'][0] or {}).get('value', '')
                if not raw_desc and cur.get('weatherDesc'):
                    raw_desc = (cur['weatherDesc'][0] or {}).get('value', '')
                desc_zh, icon = _translate_weather_desc(raw_desc)
                humidity = cur.get('humidity', '--')
                wind = cur.get('windspeedKmph', '--')
                feels = cur.get('FeelsLikeC', temp)
                return jsonify({
                    "status": "ok",
                    "city": display_city,
                    "geo": geo,
                    "temp_c": str(temp),
                    "feels_like_c": str(feels),
                    "humidity": str(humidity),
                    "wind_kmph": str(wind),
                    "desc": desc_zh,
                    "icon": icon,
                    "tip": f"体感 {feels}℃ · 湿度 {humidity}% · 风速 {wind}km/h",
                    "provider": "wttr.in",
                })
    except Exception:
        pass

    # 2. 备用数据源：Open-Meteo（需经纬度）
    if geo.get('lat') and geo.get('lon'):
        try:
            om_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={geo['lat']}&longitude={geo['lon']}"
                f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            )
            r = _PROXY_SESSION.get(om_url, headers=_PROXY_HEADERS, timeout=6)
            if r.status_code == 200:
                cur = r.json().get('current') or {}
                temp = cur.get('temperature_2m')
                if temp is not None:
                    code = int(cur.get('weather_code') or 0)
                    wmo_map = {
                        0: ('晴朗', '☀️'), 1: ('晴间多云', '🌤️'), 2: ('多云', '⛅'), 3: ('阴天', '☁️'),
                        45: ('有雾', '🌫️'), 48: ('冻雾', '🌫️'), 51: ('小毛毛雨', '🌦️'), 53: ('毛毛雨', '🌦️'),
                        61: ('小雨', '🌦️'), 63: ('中雨', '🌧️'), 65: ('大雨', '🌧️'),
                        80: ('阵雨', '🌦️'), 95: ('雷阵雨', '⛈️'),
                    }
                    desc_zh, icon = wmo_map.get(code, ('多云', '🌤️'))
                    humidity = cur.get('relative_humidity_2m', '--')
                    wind = cur.get('wind_speed_10m', '--')
                    return jsonify({
                        "status": "ok",
                        "city": display_city,
                        "geo": geo,
                        "temp_c": str(round(float(temp))),
                        "feels_like_c": str(round(float(temp))),
                        "humidity": str(humidity),
                        "wind_kmph": str(wind),
                        "desc": desc_zh,
                        "icon": icon,
                        "tip": f"湿度 {humidity}% · 风速 {wind}km/h",
                        "provider": "open-meteo",
                    })
        except Exception:
            pass

    return jsonify({
        "status": "fallback",
        "city": display_city,
        "geo": geo,
        "temp_c": "24",
        "desc": "晴转多云",
        "icon": "🌤️",
        "tip": "实时气象接口暂忙，已启用本地兜底显示",
        "provider": "fallback",
    })


_HOTLIST_CACHE = {}


@app.route('/api/fun_proxy', methods=['GET'])
def fun_proxy():
    """安全代理外部公开 API：白名单防 SSRF + requests 长超时 + 自动编码修复 + 热榜短缓存"""
    target_url = (request.args.get('url') or '').strip()
    if not target_url:
        return jsonify({"status": "error", "msg": "Missing url parameter"}), 400

    parsed = urlparse(target_url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        return jsonify({"status": "error", "msg": "Invalid url scheme"}), 400
    host_low = parsed.hostname.lower()
    if host_low not in _PROXY_ALLOWLIST:
        return jsonify({"status": "error", "msg": f"Domain not allowed: {parsed.hostname}"}), 403

    if host_low == '60s.viki.moe':
        cached = _HOTLIST_CACHE.get(target_url)
        if cached and (time.time() - cached['ts'] < 300):
            response = app.response_class(
                response=cached['body'],
                status=200,
                mimetype='application/json; charset=utf-8',
            )
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

    try:
        resp = _PROXY_SESSION.get(target_url, headers=_PROXY_HEADERS, timeout=8, allow_redirects=True)
        raw_text = resp.content.decode(resp.apparent_encoding or 'utf-8', errors='replace').lstrip('\ufeff').strip()
        if raw_text.startswith('<') and ('<!DOCTYPE' in raw_text[:80].upper() or '<HTML' in raw_text[:80].upper()):
            return jsonify({"status": "error", "msg": "Upstream returned HTML instead of JSON"}), 502

        content_type = resp.headers.get('Content-Type', 'application/json; charset=utf-8')
        if raw_text.startswith('{') or raw_text.startswith('['):
            content_type = 'application/json; charset=utf-8'

        encoded = raw_text.encode('utf-8')
        if host_low == '60s.viki.moe' and resp.status_code == 200:
            _HOTLIST_CACHE[target_url] = {'ts': time.time(), 'body': encoded}

        response = app.response_class(
            response=encoded,
            status=resp.status_code,
            mimetype=content_type,
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 502


@app.route('/api/pet/companion', methods=['GET'])
def pet_companion():
    """桌面宠物第三方 API 聚合接口：获取实时萌宠写真 (TheCatAPI/CATAAS/DogCEO) 与治愈台词 (Hitokoto/夏柔)"""
    pet_type = (request.args.get('type') or 'cat').strip().lower()
    need_image = request.args.get('image', '1') != '0'

    quote_text = ''
    quote_source = ''
    try:
        r_q = _PROXY_SESSION.get(
            'https://v1.hitokoto.cn/?c=d&c=i&c=k&encode=json',
            headers=_PROXY_HEADERS,
            timeout=3.5,
        )
        if r_q.status_code == 200:
            hq = r_q.json()
            if hq.get('hitokoto'):
                from_who = hq.get('from') or '一言'
                quote_text = f"{hq['hitokoto']} ——{from_who}"
                quote_source = 'hitokoto.cn'
    except Exception:
        pass

    if not quote_text:
        try:
            r_a = _PROXY_SESSION.get(
                'https://v.api.aa1.cn/api/api-wenan-gaoxiao/index.php?aa1=json',
                headers=_PROXY_HEADERS,
                timeout=4.0,
            )
            if r_a.status_code == 200:
                arr = r_a.json()
                if isinstance(arr, list) and arr and arr[0].get('gaoxiao'):
                    quote_text = str(arr[0]['gaoxiao']).strip()
                    quote_source = 'api.aa1.cn'
        except Exception:
            pass

    image_url = ''
    image_source = ''
    if need_image:
        if pet_type == 'dog':
            try:
                r_d = _PROXY_SESSION.get('https://dog.ceo/api/breeds/image/random', headers=_PROXY_HEADERS, timeout=4.5)
                if r_d.status_code == 200:
                    dj = r_d.json()
                    if dj.get('status') == 'success' and dj.get('message'):
                        image_url = dj['message']
                        image_source = 'dog.ceo'
            except Exception:
                pass
        else:
            try:
                r_c = _PROXY_SESSION.get('https://api.thecatapi.com/v1/images/search', headers=_PROXY_HEADERS, timeout=4.5)
                if r_c.status_code == 200:
                    cj = r_c.json()
                    if isinstance(cj, list) and cj and cj[0].get('url'):
                        image_url = cj[0]['url']
                        image_source = 'thecatapi.com'
            except Exception:
                pass
            if not image_url:
                try:
                    r_c2 = _PROXY_SESSION.get('https://cataas.com/cat?json=true', headers=_PROXY_HEADERS, timeout=4.5)
                    if r_c2.status_code == 200:
                        c2j = r_c2.json()
                        if c2j.get('url'):
                            image_url = c2j['url'] if c2j['url'].startswith('http') else f"https://cataas.com{c2j['url']}"
                            image_source = 'cataas.com'
                except Exception:
                    pass

    return jsonify({
        "status": "ok",
        "quote": quote_text or "今天也要元气满满地把 3C 机型排得整整齐齐喵！",
        "quote_source": quote_source or "builtin",
        "image_url": image_url,
        "image_source": image_source,
    })


if __name__ == '__main__':
    app.run(port=8765, debug=True)
