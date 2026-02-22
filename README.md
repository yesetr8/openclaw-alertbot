# OpenClaw AlertBot

> Telegram-based alert routing for OpenClaw / Clawmetry incidents

![OpenClaw AlertBot Infographic](docs/images/alertbot-infographic.png)

## 🇰🇷 한국어

### 한 줄 소개
OpenClaw/Clawmetry에서 발생하는 장애·경고를 **텔레그램 알림 채널**로 분리 전송해서, 주요 대화 채널을 깔끔하게 유지하는 AlertBot 운영 패키지다.

### 무엇을 해결하나?
- 운영 장애 알림이 일반 대화 채널을 오염시키는 문제
- 반복 오류를 사람이 직접 감시해야 하는 문제
- 장애(P1)와 경고(P2)의 대응 우선순위가 불명확한 문제

### 동작 구조
1. `clawmetry_monitor.py`가 헬스/로그를 점검
2. `alert_log_digest.py`가 이상 징후를 집계
3. OpenClaw cron이 이벤트를 라우팅
4. `accountId=alerts`를 통해 텔레그램 알림 채널로 전송

### 용어 정의 (P1 / P2)
- **P1 (Priority 1)**: 서비스 중단, 치명 오류처럼 **즉시 대응이 필요한** 장애 등급
- **P2 (Priority 2)**: 반복/간헐 오류처럼 서비스 전체 중단은 아니지만 **추적·개선이 필요한** 경고 등급

### Telegram AlertBot 설정(핵심)
1. OpenClaw에서 Telegram 연동을 활성화
2. 알림 전용 계정/채널을 `alerts`로 분리 설정
3. `ALERTS_POLICY.md`의 대상을 실제 채팅 ID로 지정
   - `accountId: alerts`
   - `target: <TELEGRAM_CHAT_ID>`
4. 테스트 알림 1회 전송으로 라우팅 확인

### 최소 설치/실행 절차
1. `ALERTS_POLICY.md` 정책 확인
2. 스크립트 배치:
   - `scripts/clawmetry_monitor.py`
   - `scripts/alert_log_digest.py`
3. OpenClaw cron 등록:
   - Clawmetry P1 monitor (*/30)
   - Clawmetry P2 summary (0 * * * *)
   - Cron Error Router (0 * * * *)
   - Alert Log Digest (30 9,21 * * *)
4. 텔레그램 알림 채널 전송 테스트

### 샘플 알림 포맷
- 🔴 P1 장애
  - 원인: health check 2회 연속 실패
  - 영향: 자동관제 신뢰도 저하
  - 조치: launchctl + error log 즉시 확인
- 🟡 P2 경고
  - 원인: 1시간 내 간헐 오류 반복
  - 영향: 성능/안정성 저하 가능
  - 조치: 추세 관찰 및 임계치 재조정
- 🟢 복구
  - 원인: 연속 정상 상태 확인
  - 영향: 모니터링 정상화
  - 조치: 추적 지속

### 핵심 구성요소
- `ALERTS_POLICY.md` — 알림 정책(P1/P2/쿨다운/복구 규칙)
- `scripts/clawmetry_monitor.py` — Clawmetry 모니터링 스크립트
- `scripts/alert_log_digest.py` — 이상 징후 다이제스트 생성 스크립트
- `state/clawmetry-monitor-state.json` — 모니터 상태 파일(런타임 생성)
- `state/cron-alert-router-state.json` — 라우터 상태 파일(런타임 생성)

### 릴리즈 체크리스트
- [ ] 설치/실행 절차 재현 테스트 성공
- [ ] P1/P2/복구 샘플 알림 검증
- [ ] 민감정보(토큰/개인식별자) 제외 확인
- [ ] LICENSE 및 릴리즈 노트 준비

### 서드파티 출처
- 본 프로젝트에는 **clawmetry** 기반 파생/수정 코드가 포함됩니다.
  - Source: https://github.com/vivekchand/clawmetry
  - License: MIT
- 상세 내용:
  - `THIRD_PARTY_NOTICES.md`
  - `licenses/UPSTREAM_CLAWMETRY_MIT_LICENSE.txt`

---

## 🇺🇸 English

### One-line Summary
An AlertBot operations package that routes OpenClaw/Clawmetry incidents and warnings to a **dedicated Telegram alert channel**, keeping primary conversations clean.

### What Problem Does It Solve?
- Incident alerts polluting normal conversation channels
- Manual monitoring burden for repeated failures
- Unclear response priority between critical incidents (P1) and warnings (P2)

### How It Works
1. `clawmetry_monitor.py` checks health and error logs
2. `alert_log_digest.py` aggregates anomaly signals
3. OpenClaw cron routes alert events
4. Events are delivered to Telegram via `accountId=alerts`

### Term Definitions (P1 / P2)
- **P1 (Priority 1)**: Incident level for failures that require **immediate response**, such as service downtime or critical errors
- **P2 (Priority 2)**: Warning level for **track-and-improve** issues, such as repeated/intermittent errors without full service outage

### Telegram AlertBot Setup (Key)
1. Enable Telegram integration in OpenClaw
2. Separate a dedicated alert account/channel as `alerts`
3. Set real target chat ID in `ALERTS_POLICY.md`
   - `accountId: alerts`
   - `target: <TELEGRAM_CHAT_ID>`
4. Send one test alert to verify routing

### Minimum Setup / Run Steps
1. Review policy in `ALERTS_POLICY.md`
2. Place scripts:
   - `scripts/clawmetry_monitor.py`
   - `scripts/alert_log_digest.py`
3. Register OpenClaw cron jobs:
   - Clawmetry P1 monitor (*/30)
   - Clawmetry P2 summary (0 * * * *)
   - Cron Error Router (0 * * * *)
   - Alert Log Digest (30 9,21 * * *)
4. Test delivery on the Telegram alert channel

### Sample Alert Format
- 🔴 P1 Incident
  - Cause: health check failed 2 times in a row
  - Impact: monitoring reliability degraded
  - Action: check launchctl + error logs immediately
- 🟡 P2 Warning
  - Cause: intermittent failures repeated within 1 hour
  - Impact: potential stability/performance degradation
  - Action: monitor trend and tune thresholds
- 🟢 Recovery
  - Cause: consecutive healthy checks confirmed
  - Impact: monitoring restored to normal
  - Action: continue observation

### Core Components
- `ALERTS_POLICY.md` — alert policy (P1/P2/cooldown/recovery)
- `scripts/clawmetry_monitor.py` — Clawmetry monitoring script
- `scripts/alert_log_digest.py` — anomaly digest generator script
- `state/clawmetry-monitor-state.json` — monitor state file (runtime-generated)
- `state/cron-alert-router-state.json` — router state file (runtime-generated)

### Release Checklist
- [ ] Setup/run steps are reproducible
- [ ] P1/P2/recovery sample alerts verified
- [ ] No sensitive data (tokens/personal identifiers) included
- [ ] LICENSE and release notes prepared

### Third-Party Attribution
- This project includes derived/adapted code from **clawmetry**.
  - Source: https://github.com/vivekchand/clawmetry
  - License: MIT
- See details in:
  - `THIRD_PARTY_NOTICES.md`
  - `licenses/UPSTREAM_CLAWMETRY_MIT_LICENSE.txt`
