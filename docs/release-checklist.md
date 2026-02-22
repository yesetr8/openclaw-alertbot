# AlertBot Observability — Release Checklist (Draft)

## A. 기능 검증
- [ ] P1: 장애 감지 시 즉시 alerts 계정 전송
- [ ] P2: 시간당 집계 전송(이상 없으면 무전송)
- [ ] Cron Error Router: main/inbox 오류만 라우팅
- [ ] Digest: 09:30/21:30, 이상 시만 전송(B 모드)

## B. 안전/노이즈
- [ ] 중복 억제 30분 확인
- [ ] 복구 알림 1회 규칙 확인
- [ ] 장문 리포트/불필요 전송 없음
- [ ] 민감정보 로그 출력 없음

## C. 문서화
- [ ] README 재현 절차 완료
- [ ] setup/troubleshooting/runbook 작성
- [ ] 샘플 알림 포맷 4줄 규칙 명시

## D. 릴리즈
- [ ] main 브랜치 태깅 준비
- [ ] 릴리즈 노트 작성
- [ ] 발행용 설명 콘텐츠 초안 작성
