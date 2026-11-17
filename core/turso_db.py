# -*- coding: utf-8 -*-
"""
Turso HTTP (/v2/pipeline) + 本地 SQLite WAL 探针双模存储引擎
- 零 Rust/C 扩展编译依赖，仅使用标准库与 requests.Session()
- 自动清洗环境变量（反引号/引号/空格），错误提示绝不回显 Token 任何字符
- 单事务原子提交 + 900 参数上限多值 INSERT 展开
"""
import json
import os
import re
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests
from config.settings import BASE_DIR, DATA_DIR

_JWT_RE = re.compile(r"(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)")
_CN_TZ = timezone(timedelta(hours=8))
_VALID_MODULES = ("android", "laptop", "watch")


def now_str() -> str:
    """返回北京时间格式化字符串（严禁向 SQLite/Turso 传原生 datetime 对象）"""
    return datetime.now(_CN_TZ).strftime("%Y-%m-%d %H:%M:%S")


def _strip_clean(val: str) -> str:
    return (val or "").strip().strip("`'\"").strip()


def _load_local_env_files() -> None:
    """仅在本地开发且环境变量未设置时，从 .env / .env.local 补充配置（不覆盖已有系统变量）"""
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        return
    root = Path(BASE_DIR)
    for fname in (".env.local", ".env"):
        env_path = root / fname
        if not env_path.is_file():
            continue
        try:
            for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                key = _strip_clean(k)
                if key and key not in os.environ:
                    os.environ[key] = _strip_clean(v)
        except Exception:
            pass


_load_local_env_files()


def _get_clean_env(key_name: str) -> str:
    """全局唯一环境变量提纯函数：兼容键或值误带反引号、引号、空格"""
    if key_name in os.environ:
        val = _strip_clean(os.environ[key_name])
        if val:
            return val
    for k, v in os.environ.items():
        if _strip_clean(k) == key_name:
            return _strip_clean(v)
    return ""


def _normalize_turso_host(raw_url: str) -> str:
    u = _strip_clean(raw_url)
    for prefix in (
        "sqlite+libsql://",
        "libsql://",
        "turso://",
        "wss://",
        "ws://",
        "https://",
        "http://",
    ):
        if u.lower().startswith(prefix):
            u = u[len(prefix) :]
            break
    if "?" in u:
        u = u.split("?", 1)[0]
    for suffix in ("/v2/pipeline", "/v2", "/"):
        if u.endswith(suffix):
            u = u[: -len(suffix)]
    return u.strip("/")


def _extract_clean_jwt(raw_token: str) -> str:
    t = _strip_clean(raw_token)
    m = _JWT_RE.search(t)
    return m.group(1) if m else t


def _encode_arg(val: Any) -> Dict[str, Any]:
    if val is None:
        return {"type": "null"}
    if isinstance(val, bool):
        return {"type": "integer", "value": "1" if val else "0"}
    if isinstance(val, int):
        return {"type": "integer", "value": str(val)}
    if isinstance(val, float):
        return {"type": "float", "value": float(val)}
    return {"type": "text", "value": str(val)}


def _decode_cell(cell: Dict[str, Any]) -> Any:
    t = cell.get("type")
    if t == "null" or t is None:
        return None
    if t == "integer":
        return int(cell["value"])
    if t == "float":
        return float(cell["value"])
    return str(cell.get("value", ""))


class TursoBackend:
    """Turso HTTP /v2/pipeline 轻量驱动（Keep-Alive 复用连接）"""

    def __init__(self, raw_url: str, raw_token: str) -> None:
        self.host = _normalize_turso_host(raw_url)
        scheme = "http" if self.host.startswith(("127.0.0.1", "localhost")) else "https"
        self.pipeline_url = f"{scheme}://{self.host}/v2/pipeline"
        self.auth_token = _extract_clean_jwt(raw_token)
        self.session = requests.Session()

    def execute_pipeline(self, statements: Sequence[Tuple[str, Sequence[Any]]]) -> List[Dict[str, Any]]:
        requests_payload: List[Dict[str, Any]] = []
        for sql, args in statements:
            stmt: Dict[str, Any] = {"sql": sql}
            if args:
                stmt["args"] = [_encode_arg(a) for a in args]
            requests_payload.append({"type": "execute", "stmt": stmt})
        requests_payload.append({"type": "close"})

        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        resp = self.session.post(
            self.pipeline_url,
            json={"requests": requests_payload},
            headers=headers,
            timeout=30,
        )
        if resp.status_code != 200:
            err_body = resp.text[:300]
            if "JWT" in err_body or resp.status_code in (400, 401, 403):
                token_state = (
                    "已填写且形如 JWT" if self.auth_token.startswith("eyJ") else "已填写但非 eyJ 开头"
                ) if self.auth_token else "为空"
                raise RuntimeError(
                    f"Turso 认证校验未通过 (当前状态: {token_state}，长度 {len(self.auth_token)})。"
                    f"请核对 Vercel 环境变量 TURSO_DATABASE_URL 与 TURSO_AUTH_TOKEN，修改后需重新部署。"
                )
            raise RuntimeError(f"Turso 响应异常 (HTTP {resp.status_code}): {err_body}")

        data = resp.json()
        results: List[Dict[str, Any]] = []
        for item in data.get("results", []):
            if item.get("type") == "error":
                err_msg = (item.get("error") or {}).get("message") or "未知 SQL 错误"
                raise RuntimeError(f"Turso SQL 执行失败: {err_msg}")
            resp_obj = item.get("response") or {}
            if resp_obj.get("type") == "execute":
                results.append(resp_obj.get("result") or {})
        return results

    def query(self, sql: str, args: Sequence[Any] = ()) -> List[Tuple[Any, ...]]:
        res_list = self.execute_pipeline([(sql, args)])
        if not res_list:
            return []
        rows = res_list[0].get("rows") or []
        return [tuple(_decode_cell(c) for c in row) for row in rows]

    def execute_tx(self, statements: Sequence[Tuple[str, Sequence[Any]]]) -> None:
        if not statements:
            return
        tx_stmts: List[Tuple[str, Sequence[Any]]] = [("BEGIN", ())]
        tx_stmts.extend(statements)
        tx_stmts.append(("COMMIT", ()))
        self.execute_pipeline(tx_stmts)


class LocalSqliteBackend:
    """本地开发或未配置 Turso 时的 SQLite 兜底驱动（含 WAL 共享内存探针降级）"""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._mode_probed = False

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10, check_same_thread=False)
        if not self._mode_probed:
            cur = conn.cursor()
            try:
                cur.execute("PRAGMA journal_mode=WAL;")
                cur.execute("SELECT name FROM sqlite_master LIMIT 1;")
            except sqlite3.OperationalError:
                try:
                    cur.execute("PRAGMA journal_mode=DELETE;")
                except Exception:
                    pass
            try:
                cur.execute("PRAGMA synchronous=NORMAL;")
                cur.execute("PRAGMA busy_timeout=5000;")
            except Exception:
                pass
            cur.close()
            self._mode_probed = True
        return conn

    def query(self, sql: str, args: Sequence[Any] = ()) -> List[Tuple[Any, ...]]:
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute(sql, list(args))
                return cur.fetchall()
            finally:
                conn.close()

    def execute_tx(self, statements: Sequence[Tuple[str, Sequence[Any]]]) -> None:
        if not statements:
            return
        with self._lock:
            conn = self._connect()
            try:
                conn.execute("BEGIN")
                for sql, args in statements:
                    conn.execute(sql, list(args))
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()


class TursoDualStore:
    """3C Matrix 云端/本地双模数据持久层"""

    _DDL_STATEMENTS: List[Tuple[str, Sequence[Any]]] = [
        (
            """
            CREATE TABLE IF NOT EXISTS device_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """.strip(),
            (),
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_device_records_module_sort ON device_records (module, sort_order, id)",
            (),
        ),
        (
            """
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT NOT NULL,
                action TEXT NOT NULL,
                record_count INTEGER NOT NULL DEFAULT 0,
                output_count INTEGER NOT NULL DEFAULT 0,
                detail TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """.strip(),
            (),
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_operation_logs_id_desc ON operation_logs (id DESC)",
            (),
        ),
    ]

    def __init__(self) -> None:
        self._init_lock = threading.Lock()
        self._initialized = False
        self._backend: Any = None
        self._mode: str = "uninitialized"
        self._turso_host: str = ""
        self._init_backend()

    def _init_backend(self) -> None:
        turso_url = _get_clean_env("TURSO_DATABASE_URL")
        turso_token = _extract_clean_jwt(_get_clean_env("TURSO_AUTH_TOKEN"))
        if turso_url:
            backend = TursoBackend(turso_url, turso_token)
            self._backend = backend
            self._mode = "turso"
            self._turso_host = backend.host
        else:
            db_path = Path(DATA_DIR) / "3c_matrix.db"
            self._backend = LocalSqliteBackend(db_path)
            self._mode = "sqlite"
            self._turso_host = str(db_path)

    def ensure_db_ready(self) -> None:
        """幂等冷启动建表：先查 sqlite_master，仅当缺表时下发 DDL"""
        if self._initialized:
            return
        with self._init_lock:
            if self._initialized:
                return
            rows = self._backend.query(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('device_records', 'operation_logs')"
            )
            existing_count = int(rows[0][0]) if rows else 0
            if existing_count < 2:
                self._backend.execute_tx(self._DDL_STATEMENTS)
            self._initialized = True

    def get_backend_info(self) -> Dict[str, Any]:
        return {
            "mode": self._mode,
            "target": self._turso_host if self._mode == "turso" else "local-sqlite",
            "initialized": self._initialized,
        }

    def check_health(self) -> Dict[str, Any]:
        self.ensure_db_ready()
        counts_rows = self._backend.query(
            "SELECT module, count(*) FROM device_records GROUP BY module"
        )
        counts = {m: 0 for m in _VALID_MODULES}
        for mod, cnt in counts_rows:
            counts[str(mod)] = int(cnt)
        log_rows = self._backend.query("SELECT count(*) FROM operation_logs")
        log_count = int(log_rows[0][0]) if log_rows else 0
        return {
            "status": "ok",
            "backend": self._mode,
            "target": self._turso_host if self._mode == "turso" else "local-sqlite",
            "record_counts": counts,
            "log_count": log_count,
        }

    def load_records(self, module_id: str) -> List[Dict[str, Any]]:
        self.ensure_db_ready()
        rows = self._backend.query(
            "SELECT payload_json FROM device_records WHERE module = ? ORDER BY sort_order ASC, id ASC",
            (module_id,),
        )
        out: List[Dict[str, Any]] = []
        for (raw_json,) in rows:
            if not raw_json:
                continue
            try:
                item = json.loads(raw_json)
                if isinstance(item, dict):
                    out.append(item)
            except Exception:
                continue
        return out

    def load_all_summary(self) -> Dict[str, Any]:
        """一次查询获取 3 个模块的云端记录统计与最近样本预览"""
        self.ensure_db_ready()
        rows = self._backend.query(
            "SELECT module, payload_json, updated_at FROM device_records ORDER BY module ASC, sort_order ASC, id ASC"
        )
        modules_data: Dict[str, Dict[str, Any]] = {
            m: {"count": 0, "updated_at": "", "records": []} for m in _VALID_MODULES
        }
        for mod, raw_json, updated_at in rows:
            mod_key = str(mod)
            if mod_key not in modules_data:
                modules_data[mod_key] = {"count": 0, "updated_at": "", "records": []}
            entry = modules_data[mod_key]
            entry["count"] += 1
            if updated_at and str(updated_at) > entry["updated_at"]:
                entry["updated_at"] = str(updated_at)
            try:
                parsed = json.loads(raw_json)
                if isinstance(parsed, dict):
                    entry["records"].append(parsed)
            except Exception:
                pass
        return modules_data

    def save_records(
        self,
        module_id: str,
        records: List[Dict[str, Any]],
        log_action: Optional[str] = "save",
        log_detail: str = "",
    ) -> int:
        """单事务原子替换指定模块的记录列表，并按 900 参数上限分块多值 INSERT"""
        self.ensure_db_ready()
        ts = now_str()
        stmts: List[Tuple[str, Sequence[Any]]] = [
            ("DELETE FROM device_records WHERE module = ?", (module_id,))
        ]

        cols_per_row = 5
        rows_per_stmt = max(1, min(120, 900 // cols_per_row))
        if records:
            for offset in range(0, len(records), rows_per_stmt):
                chunk = records[offset : offset + rows_per_stmt]
                placeholders = ", ".join(["(?, ?, ?, ?, ?)"] * len(chunk))
                sql = (
                    "INSERT INTO device_records "
                    "(module, sort_order, payload_json, created_at, updated_at) "
                    f"VALUES {placeholders}"
                )
                flat_args: List[Any] = []
                for idx, rec in enumerate(chunk):
                    payload = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
                    flat_args.extend([module_id, offset + idx, payload, ts, ts])
                stmts.append((sql, flat_args))

        if log_action:
            detail_text = log_detail or f"保存 {len(records)} 条待处理机型记录"
            stmts.append(
                (
                    "INSERT INTO operation_logs (module, action, record_count, output_count, detail, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (module_id, log_action, len(records), 0, detail_text, ts),
                )
            )

        self._backend.execute_tx(stmts)
        return len(records)

    def clear_records(self, module_id: str) -> int:
        self.ensure_db_ready()
        ts = now_str()
        stmts: List[Tuple[str, Sequence[Any]]] = [
            ("DELETE FROM device_records WHERE module = ?", (module_id,)),
            (
                "INSERT INTO operation_logs (module, action, record_count, output_count, detail, created_at) "
                "VALUES (?, 'clear', 0, 0, '清空当前模块机型列表', ?)",
                (module_id, ts),
            ),
        ]
        self._backend.execute_tx(stmts)
        return 0

    def append_log(
        self,
        module_id: str,
        action: str,
        record_count: int = 0,
        output_count: int = 0,
        detail: str = "",
    ) -> None:
        self.ensure_db_ready()
        ts = now_str()
        self._backend.execute_tx(
            [
                (
                    "INSERT INTO operation_logs (module, action, record_count, output_count, detail, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (module_id, action, int(record_count), int(output_count), detail, ts),
                )
            ]
        )

    def list_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        self.ensure_db_ready()
        safe_limit = max(1, min(int(limit or 100), 300))
        rows = self._backend.query(
            "SELECT id, module, action, record_count, output_count, detail, created_at "
            "FROM operation_logs ORDER BY id DESC LIMIT ?",
            (safe_limit,),
        )
        return [
            {
                "id": int(r[0]),
                "module": str(r[1]),
                "action": str(r[2]),
                "record_count": int(r[3] or 0),
                "output_count": int(r[4] or 0),
                "detail": str(r[5] or ""),
                "created_at": str(r[6] or ""),
            }
            for r in rows
        ]

    def clear_logs(self) -> None:
        self.ensure_db_ready()
        self._backend.execute_tx([("DELETE FROM operation_logs", ())])


turso_store = TursoDualStore()
