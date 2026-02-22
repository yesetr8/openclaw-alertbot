# AlertBot Observability — 권장 리포 구조 (Draft)

```text
alertbot-observability/
  README.md
  ALERTS_POLICY.md
  scripts/
    clawmetry_monitor.py
    alert_log_digest.py
  docs/
    setup.md
    troubleshooting.md
    runbook.md
  examples/
    cron_payloads/
      p1_monitor.md
      p2_summary.md
      cron_error_router.md
      alert_digest.md
  state-schema/
    clawmetry-monitor-state.schema.json
    cron-alert-router-state.schema.json
```

## 운영 포인트
- 상태파일(JSON)은 런타임 생성(리포에는 schema만 포함)
- cron payload는 문서/예제로 관리
- production 경로 하드코딩은 `.env.example` 또는 설정 파일로 추출 권장
