# Push Steps

- project: `alertbot-observability`
- recommended_repo: `yesetr8/openclaw-alertbot`

## 1) 로컬 검증
```bash
git status
```

## 2) 저장소 초기화
```bash
git init
git checkout -b main
git add .
git commit -m "release: initial bundle"
```

## 3) GitHub 생성/푸시
```bash
gh repo create yesetr8/openclaw-alertbot --private --source=. --remote=origin --push
# 또는 기존 origin 사용 시
git remote add origin <repo-url>
git push -u origin main
```

## 4) 릴리즈 태그
```bash
git tag v0.1.0
git push origin v0.1.0
```

⚠️ 실제 푸시는 외부 전송이므로 파트너 승인 후 실행
