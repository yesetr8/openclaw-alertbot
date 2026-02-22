# OpenClaw AlertBot

## 🇰🇷 한국어

### 이 리포가 해결하는 문제
OpenClaw 운영 환경에서 발생하는 장애/경고 신호를 체계적으로 수집하고,
**주요 사용자 대화 채널에 불필요한 노이즈를 만들지 않도록** 전용 알림 채널로 분리 전달하는 운영 방식을 제공합니다.

### 주요 기능
- P1 즉시 알림 (치명 장애)
- P2 시간 단위 요약 알림 (반복/간헐 이슈)
- Cron 실행 오류 라우팅
- 하루 2회 이상 징후 다이제스트

### 핵심 구성요소
- `ALERTS_POLICY.md` — 알림 정책(P1/P2/쿨다운/복구 규칙)
- `scripts/clawmetry_monitor.py` — Clawmetry 모니터링 스크립트
- `scripts/alert_log_digest.py` — 이상 징후 다이제스트 생성 스크립트
- `state/clawmetry-monitor-state.json` — 모니터 상태 파일(런타임 생성)
- `state/cron-alert-router-state.json` — 라우터 상태 파일(런타임 생성)

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
4. 알림 채널 전송 테스트

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

### Problem This Repository Solves
This repository provides an operational pattern for collecting incidents and warnings in OpenClaw environments,
and routing alerts through a dedicated alert channel so your **primary user conversations stay clean and focused**.

### Key Capabilities
- P1 immediate alerts (critical incidents)
- P2 hourly summary alerts (repeated/intermittent issues)
- Cron error routing
- Twice-daily anomaly digest

### Core Components
- `ALERTS_POLICY.md` — alert policy (P1/P2/cooldown/recovery)
- `scripts/clawmetry_monitor.py` — Clawmetry monitoring script
- `scripts/alert_log_digest.py` — anomaly digest generator script
- `state/clawmetry-monitor-state.json` — monitor state file (runtime-generated)
- `state/cron-alert-router-state.json` — router state file (runtime-generated)

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
4. Test delivery on your alert channel

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
