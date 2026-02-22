#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

def resolve_path(env_key: str, default_rel: str) -> Path:
    raw = os.getenv(env_key, "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (REPO_ROOT / default_rel).resolve()

LABEL = os.getenv("CLAWMETRY_SERVICE_LABEL", "com.openclaw.clawmetry")
HEALTH_URL = os.getenv("CLAWMETRY_HEALTH_URL", "http://127.0.0.1:8900")
STATE_PATH = resolve_path("CLAWMETRY_STATE_PATH", "state/clawmetry-monitor-state.json")
ERROR_LOG = resolve_path("CLAWMETRY_ERROR_LOG_PATH", "logs/clawmetry.error.log")
COOLDOWN_SEC = 30 * 60

CRITICAL_PATTERNS = [
    re.compile(r"traceback", re.I),
    re.compile(r"\bexception\b", re.I),
    re.compile(r"\bcritical\b", re.I),
    re.compile(r"\bfatal\b", re.I),
    re.compile(r"address already in use", re.I),
]
IGNORE_PATTERNS = [
    re.compile(r"WARNING: This is a development server", re.I),
]

RUNTIME_LOG_DIR = Path("/tmp/openclaw")
RUNTIME_LOG_GLOB = "openclaw-*.log"
MAX_INITIAL_READ_BYTES = 200_000


def load_state():
    default = {
        "fail_streak": 0,
        "ok_streak": 0,
        "incident_active": False,
        "incident_signature": "",
        "last_alert_at": {},
        "log_offsets": {},
        "p2_counts": {},
        "p2_window_start": int(time.time()),
    }
    if not STATE_PATH.exists():
        return default
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        default.update(data if isinstance(data, dict) else {})
    except Exception:
        pass
    return default


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def check_launchctl():
    try:
        out = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=5)
        if out.returncode != 0:
            return False, "launchctl list failed"
        line = next((ln for ln in out.stdout.splitlines() if LABEL in ln), "")
        if not line:
            return False, "LaunchAgent not loaded"
        parts = line.split()
        pid = parts[0] if len(parts) >= 1 else "-"
        status = parts[1] if len(parts) >= 2 else "?"
        if pid == "-":
            return False, f"LaunchAgent not running (status={status})"
        return True, f"pid={pid}"
    except Exception as e:
        return False, f"launchctl error: {e}"


def check_health():
    try:
        req = urllib.request.Request(HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200, f"http={resp.status}"
    except Exception as e:
        return False, f"health error: {e}"


def scan_error_log(state):
    path = ERROR_LOG
    if not path.exists():
        return []

    key = str(path)
    offset = int(state.get("log_offsets", {}).get(key, 0) or 0)
    size = path.stat().st_size
    if offset > size:
        offset = 0

    with path.open("rb") as f:
        f.seek(offset)
        chunk = f.read()

    state.setdefault("log_offsets", {})[key] = size
    if not chunk:
        return []

    text = chunk.decode("utf-8", errors="ignore")
    hits = []
    for ln in text.splitlines():
        if any(p.search(ln) for p in IGNORE_PATTERNS):
            continue
        for pat in CRITICAL_PATTERNS:
            if pat.search(ln):
                sig = f"log:{pat.pattern}"
                hits.append((sig, ln.strip()[:140]))
                break
    return hits


def scan_runtime_heartbeat(state):
    """
    Runtime 로그에서 heartbeat 관련 '실제 오류'만 감지한다.
    - 정상 문자열(예: next-heartbeat, heartbeat started, messageChannel=heartbeat)은 제외
    - cron dump(JSON jobs) 라인은 제외
    """
    if not RUNTIME_LOG_DIR.exists():
        return []

    benign_markers = [
        "next-heartbeat",
        "heartbeat: started",
        "messagechannel=heartbeat",
        "heartbeat: using explicit accountid",
        "embedded run start",
    ]

    files = sorted(RUNTIME_LOG_DIR.glob(RUNTIME_LOG_GLOB))[-3:]
    hits = []
    for path in files:
        key = f"runtime:{path}"
        size = path.stat().st_size
        prev = state.setdefault("log_offsets", {}).get(key)
        if prev is None:
            offset = max(0, size - MAX_INITIAL_READ_BYTES)
        else:
            offset = int(prev or 0)
            if offset > size:
                offset = 0

        with path.open("rb") as f:
            f.seek(offset)
            chunk = f.read()

        state.setdefault("log_offsets", {})[key] = size
        if not chunk:
            continue

        text = chunk.decode("utf-8", errors="ignore")
        for ln in text.splitlines():
            if '"jobs": [' in ln:
                # cron list 대량 dump 라인 (오탐 원인)
                continue

            # 구조화 로그(JSON)면 주요 필드만 합쳐서 판단
            inspect_text = ln
            try:
                obj = json.loads(ln)
                if isinstance(obj, dict):
                    parts = []
                    for k in ("0", "1", "2"):
                        if k in obj:
                            v = obj[k]
                            if isinstance(v, (dict, list)):
                                parts.append(json.dumps(v, ensure_ascii=False))
                            else:
                                parts.append(str(v))
                    if parts:
                        inspect_text = " ".join(parts)
            except Exception:
                pass

            l = inspect_text.lower()
            if "heartbeat" not in l:
                continue
            if any(marker in l for marker in benign_markers):
                continue

            has_err_word = any(w in l for w in ["error", "failed", "fail", "timeout", "exception"])
            near_heartbeat_error = bool(
                re.search(r"heartbeat.{0,80}(error|failed|fail|timeout|exception)", l)
                or re.search(r"(error|failed|fail|timeout|exception).{0,80}heartbeat", l)
            )
            gateway_ctx = "gateway/heartbeat" in l

            if has_err_word and (gateway_ctx or near_heartbeat_error):
                snippet = inspect_text.strip()[:140]
                sig = f"runtime:heartbeat:{snippet[:60]}"
                hits.append((sig, snippet))
                break
        if hits:
            break

    return hits


def in_cooldown(state, signature, now_ts):
    last = int(state.get("last_alert_at", {}).get(signature, 0) or 0)
    return (now_ts - last) < COOLDOWN_SEC


def stamp_alert(state, signature, now_ts):
    state.setdefault("last_alert_at", {})[signature] = now_ts


def inc_p2(state, key):
    p2 = state.setdefault("p2_counts", {})
    p2[key] = int(p2.get(key, 0) or 0) + 1


def fmt_p1(signature, reason, impact, action):
    return "\n".join([
        f"🔴 Clawmetry 장애 ({signature})",
        f"원인: {reason}",
        f"영향: {impact}",
        f"조치: {action}",
    ])


def fmt_recovery(signature):
    return "\n".join([
        f"🟢 Clawmetry 복구 ({signature})",
        "원인: 장애 조건 해소 + 연속 2회 정상 확인",
        "영향: 모니터링/대시보드 정상",
        "조치: 추적 지속",
    ])


def fmt_p2_summary(p2_counts):
    items = sorted(p2_counts.items(), key=lambda x: x[1], reverse=True)
    top = ", ".join([f"{k}:{v}" for k, v in items[:3]])
    return "\n".join([
        "🟡 Clawmetry 경고 집계 (최근 1시간)",
        f"원인: {top}",
        "영향: 간헐 이슈(자동복구)",
        "조치: 추세 악화 시 P1 상향",
    ])


def run_check_mode(state):
    now_ts = int(time.time())
    launch_ok, launch_note = check_launchctl()
    health_ok, health_note = check_health()
    log_hits = scan_error_log(state)
    runtime_hits = scan_runtime_heartbeat(state)

    p1_sig = None
    p1_reason = ""

    if log_hits:
        p1_sig, line = log_hits[0]
        p1_reason = line
    elif runtime_hits:
        p1_sig, line = runtime_hits[0]
        p1_reason = line

    if not launch_ok:
        state["fail_streak"] = int(state.get("fail_streak", 0) or 0) + 1
        p1_sig = p1_sig or "service:not-running"
        p1_reason = p1_reason or launch_note
    elif not health_ok:
        state["fail_streak"] = int(state.get("fail_streak", 0) or 0) + 1
        inc_p2(state, "health:single-fail")
        if state["fail_streak"] >= 2:
            p1_sig = p1_sig or "health:down"
            p1_reason = p1_reason or health_note
    else:
        state["fail_streak"] = 0

    if p1_sig:
        state["incident_active"] = True
        state["incident_signature"] = p1_sig
        state["ok_streak"] = 0
        if not in_cooldown(state, p1_sig, now_ts):
            stamp_alert(state, p1_sig, now_ts)
            impact = "clawmetry 대시보드/자동관제 신뢰도 저하"
            action = "launchctl 상태 + error.log 즉시 확인"
            if p1_sig.startswith("runtime:heartbeat"):
                impact = "main/inbox heartbeat 신뢰도 저하"
                action = "/tmp/openclaw 로그에서 heartbeat 오류 즉시 확인"
            return fmt_p1(
                p1_sig,
                p1_reason,
                impact,
                action,
            )
        return ""

    # 정상 경로
    if state.get("incident_active"):
        state["ok_streak"] = int(state.get("ok_streak", 0) or 0) + 1
        if state["ok_streak"] >= 2:
            sig = state.get("incident_signature", "unknown")
            state["incident_active"] = False
            state["incident_signature"] = ""
            state["ok_streak"] = 0
            return fmt_recovery(sig)
    else:
        state["ok_streak"] = 0

    return ""


def run_summary_mode(state):
    now_ts = int(time.time())
    p2 = state.get("p2_counts", {}) or {}
    if not p2:
        state["p2_window_start"] = now_ts
        return ""

    text = fmt_p2_summary(p2)
    state["p2_counts"] = {}
    state["p2_window_start"] = now_ts
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["check", "summary"], default="check")
    args = parser.parse_args()

    state = load_state()
    if args.mode == "check":
        out = run_check_mode(state)
    else:
        out = run_summary_mode(state)

    save_state(state)
    if out.strip():
        print(out.strip())


if __name__ == "__main__":
    main()
