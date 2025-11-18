# ⚡ 5분만에 시작하기 - 네이버 Clova OCR

> **OpenAI API quota 초과 문제 해결** - 무료 대안으로 빠르게 전환하기

---

## 🎯 전체 과정 요약 (5분)

```
1️⃣ 네이버 클라우드 가입 (2분)
2️⃣ Clova OCR 신청 & API 키 발급 (2분)
3️⃣ .env 파일 설정 (1분)
4️⃣ 앱 실행 및 테스트 (즉시)
```

---

## 📝 단계별 가이드

### 1️⃣ 네이버 클라우드 가입 (2분)

```bash
# 브라우저에서 접속
https://www.ncloud.com
```

1. 우측 상단 **"회원가입"** 클릭
2. 네이버 계정으로 로그인
3. 휴대폰 본인인증 완료
4. 무료 크레딧 10만원 받기 🎁

### 2️⃣ Clova OCR 서비스 신청 (2분)

```bash
# 콘솔 접속
https://console.ncloud.com
```

**A. 서비스 찾기**
```
Console → Services → AI·NAVER API → Clova OCR
```

**B. 서비스 생성**
```
1. "이용 신청하기" 클릭
2. Application 이름: market-ocr
3. 서비스 선택: General OCR ✅ (Template OCR ❌)
4. 등록 버튼 클릭
```

**C. API 정보 복사**
```
✅ Secret Key 복사 → 메모장에 임시 저장
✅ APIGW Invoke URL 복사 → 메모장에 임시 저장
```

예시:
```
Secret Key: dGhpc2lzc2VjcmV0a2V5ZXhhbXBsZQ==
API URL: https://abc123.apigw.ntruss.com/custom/v1/12345/general
```

### 3️⃣ .env 파일 설정 (1분)

**A. 파일 이름 변경**
```bash
# 터미널에서 실행
cd /Users/seungjaihan/Documents/051012_SibangAIOCR
mv sibangaiocr.env .env
```

**B. .env 파일 편집**
```bash
# 텍스트 에디터로 열기
open -a TextEdit .env

# 또는
nano .env
```

**C. API 정보 입력**
```env
# 아래 두 줄만 수정하면 됩니다!
NAVER_OCR_SECRET_KEY=여기에_실제_Secret_Key_붙여넣기
NAVER_OCR_API_URL=여기에_실제_API_URL_붙여넣기
```

**⚠️ 주의사항**:
- 따옴표 없이 입력
- 앞뒤 공백 없이 입력
- `=` 기호 양옆에 공백 없이

**올바른 예시**:
```env
NAVER_OCR_SECRET_KEY=dGhpc2lzc2VjcmV0a2V5ZXhhbXBsZQ==
NAVER_OCR_API_URL=https://abc123.apigw.ntruss.com/custom/v1/12345/general
```

**잘못된 예시** ❌:
```env
NAVER_OCR_SECRET_KEY = "dGhpc2lzc2VjcmV0a2V5ZXhhbXBsZQ=="  # 공백과 따옴표 있음
NAVER_OCR_API_URL="URL"  # 따옴표 있음
```

### 4️⃣ 앱 실행 (즉시)

```bash
# Streamlit 앱 실행
streamlit run app_streamlit.py
```

**예상 소요 시간**: 앱 실행까지 3-5초

**브라우저 자동 열림**: `http://localhost:8501`

---

## ✅ 동작 확인

### 화면 확인사항

1. **왼쪽 사이드바 확인**
   ```
   ⚙️ 설정
   OCR 엔진 선택: naver_clova ✅
   
   🔑 API 키 상태
   ✅ Naver Clova OCR 설정 완료
   ```

2. **이미지 업로드**
   - "시장 가판대 사진을 선택하세요" 클릭
   - 테스트 이미지 선택

3. **OCR 실행**
   - "🚀 OCR 시작" 버튼 클릭
   - 처리 중... (약 3-7초)
   - ✅ OCR 처리 완료!

---

## 🚨 문제 해결 (1분 안에 해결)

### ❌ "API 키가 설정되지 않았습니다"

**원인**: 파일 이름 또는 변수명 오류

**해결 (30초)**:
```bash
# 1. 파일 이름 확인
ls -la | grep .env
# ".env" 파일이 보여야 함 (".env.txt" 아님!)

# 2. 파일 내용 확인
cat .env
# Secret Key와 URL이 제대로 입력되었는지 확인

# 3. 앱 재시작
# Ctrl+C로 종료 후
streamlit run app_streamlit.py
```

### ❌ "Error 401: Unauthorized"

**원인**: Secret Key가 잘못됨

**해결 (1분)**:
1. 네이버 클라우드 콘솔에서 Secret Key 다시 복사
2. `.env` 파일 열기
3. `NAVER_OCR_SECRET_KEY=` 뒤에 정확히 붙여넣기
4. 저장 후 앱 재시작

### ❌ "Error 404: Not Found"

**원인**: API URL이 잘못됨

**해결 (1분)**:
1. 네이버 클라우드 콘솔에서 "APIGW Invoke URL" 다시 복사
2. URL 전체(https://부터 끝까지) 복사되었는지 확인
3. `.env` 파일에 정확히 붙여넣기
4. 저장 후 앱 재시작

---

## 🎉 완료!

이제 **월 1,000건 무료**로 시장 가판대 OCR을 사용할 수 있습니다!

### 다음 단계

✅ **테스트 완료 후**:
- 실제 시장 사진으로 테스트
- JSON 결과를 다운로드하여 활용
- 모바일 앱 구축 고려 (`mobile_guide.md` 참조)

✅ **더 자세한 정보**:
- 📖 [NAVER_OCR_SETUP.md](NAVER_OCR_SETUP.md) - 상세 가이드
- 📖 [README.md](README.md) - 프로젝트 전체 정보
- 📖 [TECHNICAL_DETAILS.md](TECHNICAL_DETAILS.md) - 기술 상세

---

## 💡 팁

### 인식률 높이는 방법
- ✅ 밝은 조명에서 촬영
- ✅ 가격표를 화면 중앙에 배치
- ✅ 초점 선명하게
- ✅ 정면에서 촬영

### 비용 절감 방법
- ✅ 이미지 크기 2-3MB로 최적화
- ✅ 여러 상품을 한 번에 촬영 (배치 처리)
- ✅ 실패한 요청 재시도 최소화

### 무료 제공량 관리
```
월 1,000건 = 하루 약 33건

사용 예시:
- 개인 프로젝트: 충분 ✅
- 소규모 상점: 충분 ✅
- 대규모 마트: 추가 요금 필요
```

---

**작성일**: 2025년 10월 12일  
**소요 시간**: 총 5분 (가입 2분 + 설정 2분 + 실행 1분)  
**무료 제공**: 월 1,000건 🎁


