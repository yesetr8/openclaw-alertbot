# OpenClaw AlertBot

## 🇰🇷 한국어

### 이 리포가 해결하는 문제
OpenClaw 운영 중 발생하는 장애를 **메인/인박스 대화창 오염 없이** alerts 계정으로 분리 전송하고,
- P1 즉시 알림
- P2 시간당 집계
- Cron 장애 라우팅
- 하루 2회 이상 징후 요약
을 재현 가능하게 운영한다.

### 핵심 구성요소
- `ALERTS_POLICY.md` — 알림 정책(P1/P2/쿨다운/복구 규칙)
- `scripts/clawmetry_monitor.py` — Clawmetry P1/P2 감시 엔진
- `scripts/alert_log_digest.py` — 12h 이상 징후 요약기(09:30/21:30)
- `memory/clawmetry-monitor-state.json` — 상태 저장
- `memory/cron-alert-router-state.json` — 라우팅 상태 저장

### 최소 설치/실행 절차
1. 정책 파일 복사: `ALERTS_POLICY.md`
2. 스크립트 배치:
   - `clawmetry_monitor.py`
   - `alert_log_digest.py`
3. OpenClaw cron 등록
   - Clawmetry P1 monitor (*/30)
   - Clawmetry P2 summary (0 * * * *)
   - Cron Error Router (0 * * * *)
   - Alert Log Digest (30 9,21 * * *)
4. 텔레그램 `accountId=alerts` 전송 테스트

### 릴리즈 포함 조건
- [ ] README 설치 절차 재현 테스트 성공
- [ ] 샘플 알림 3종(P1/P2/복구) 캡처 확보
- [ ] 민감정보(API key/token) 제외 확인
- [ ] LICENSE/버전 태그 준비

### Output 승격 조건
- 발행 완료 가이드 URL 또는 GitHub release 태그 확보 시 `30-output` 이동

---

## 🇺🇸 English

### Problem This Repository Solves
This repository provides a reproducible OpenClaw AlertBot observability setup, keeping incidents out of main/inbox chats and routing alerts through a dedicated `alerts` account:
- P1 immediate alerts
- P2 hourly summaries
- Cron error routing
- Twice-daily anomaly digest

### Core Components
- `ALERTS_POLICY.md` — alert policy (P1/P2/cooldown/recovery)
- `scripts/clawmetry_monitor.py` — Clawmetry P1/P2 monitor
- `scripts/alert_log_digest.py` — 12-hour anomaly digest generator (09:30/21:30)
- `memory/clawmetry-monitor-state.json` — monitor state
- `memory/cron-alert-router-state.json` — router state

### Minimum Setup / Run Steps
1. Copy policy file: `ALERTS_POLICY.md`
2. Place scripts:
   - `clawmetry_monitor.py`
   - `alert_log_digest.py`
3. Register OpenClaw cron jobs:
   - Clawmetry P1 monitor (*/30)
   - Clawmetry P2 summary (0 * * * *)
   - Cron Error Router (0 * * * *)
   - Alert Log Digest (30 9,21 * * *)
4. Test Telegram delivery with `accountId=alerts`

### Release Checklist
- [ ] README setup steps are reproducible
- [ ] Capture sample alerts for P1/P2/recovery
- [ ] Confirm no secrets are included (API keys/tokens)
- [ ] Prepare LICENSE and version tag

### Output Promotion Rule
- Move to `30-output` only after publication URL or GitHub release tag is confirmed.
