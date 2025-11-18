# 🇰🇷 네이버 클라우드 OCR 설정 완벽 가이드

> **OpenAI API quota 초과 문제 해결을 위한 무료 대체 솔루션**
> 
> 네이버 Clova OCR은 한국어에 특화되어 있으며, **월 1,000건 무료**로 제공됩니다!

---

## 📋 목차

1. [왜 네이버 Clova OCR인가?](#-왜-네이버-clova-ocr인가)
2. [계정 생성 및 서비스 신청](#-1단계-계정-생성-및-서비스-신청)
3. [API 키 발급](#-2단계-api-키-발급)
4. [프로젝트 설정](#-3단계-프로젝트-설정)
5. [동작 확인](#-4단계-동작-확인)
6. [문제 해결](#-문제-해결)

---

## 🎯 왜 네이버 Clova OCR인가?

### ✅ 장점

| 항목 | 네이버 Clova OCR | OpenAI GPT-4 Vision |
|------|------------------|---------------------|
| **무료 제공량** | 월 1,000건 | 없음 (quota 제한) |
| **한글 인식** | ⭐⭐⭐⭐⭐ 특화 | ⭐⭐⭐⭐ 우수 |
| **손글씨 인식** | ⭐⭐⭐⭐ 우수 | ⭐⭐⭐⭐⭐ 최고 |
| **처리 속도** | 3-7초 | 5-10초 |
| **비용 (1,000건 초과 시)** | 건당 ~₩50 | 건당 ~₩15-45 |
| **설정 난이도** | 중간 | 쉬움 |
| **국내 서버** | ✅ 예 (빠름) | ❌ 아니오 |

### 💰 비용 비교

- **네이버 Clova**: 월 1,000건까지 **완전 무료**
- **OpenAI GPT-4 Vision**: 모든 요청 유료 (이미지당 $0.01~0.03)

**결론**: 시장 가판대 OCR처럼 한국어 중심 프로젝트에는 **네이버 Clova OCR이 최적**입니다!

---

## 🚀 1단계: 계정 생성 및 서비스 신청

### 1-1. 네이버 클라우드 플랫폼 가입

1. **네이버 클라우드 플랫폼 접속**
   ```
   https://www.ncloud.com
   ```

2. **회원가입 진행**
   - 우측 상단 **"회원가입"** 클릭
   - 네이버 계정으로 로그인 (없으면 네이버 계정 먼저 생성)
   - 본인인증 (휴대폰 인증 필수)

3. **무료 크레딧 받기** 🎁
   - 신규 가입 시 최대 **10만원 크레딧** 제공
   - 3개월 동안 사용 가능

### 1-2. Clova OCR 서비스 신청

4. **콘솔 접속**
   - 로그인 후 상단의 **[Console]** 버튼 클릭
   ```
   https://console.ncloud.com
   ```

5. **Clova OCR 찾기**
   - 왼쪽 메뉴에서 **"Services"** 클릭
   - **"AI·NAVER API"** 카테고리 선택
   - **"Clova OCR"** 클릭

6. **서비스 생성**
   - **"이용 신청하기"** 또는 **"Application 등록"** 버튼 클릭
   - 아래 정보 입력:
     ```
     Application 이름: market-ocr
     서비스 선택: General OCR (일반 OCR)
     ```
   - **중요**: "Template OCR"이 아닌 **"General OCR"** 선택!
   - 이용약관 동의 후 **"등록"** 클릭

7. **서비스 활성화 대기**
   - 보통 **즉시 활성화**되지만, 최대 1-2분 소요될 수 있음

---

## 🔑 2단계: API 키 발급

### 2-1. Secret Key 확인

1. **Clova OCR 대시보드**로 이동
   - Console > Services > AI·NAVER API > Clova OCR

2. **생성한 서비스 클릭** (`market-ocr`)

3. **Secret Key 복사**
   - 화면에 표시된 **"Secret Key"** 옆의 복사 버튼 클릭
   - 예시: `dGhpc2lzc2VjcmV0a2V5ZXhhbXBsZQ==`
   - ⚠️ **주의**: 이 키는 비밀번호처럼 안전하게 보관하세요!

### 2-2. API Gateway URL 확인

4. **APIGW Invoke URL 복사**
   - 같은 화면에서 **"APIGW Invoke URL"** 찾기
   - 복사 버튼 클릭
   - 예시: `https://[your-domain].apigw.ntruss.com/custom/v1/12345/[your-id]/general`
   - 이 URL은 나중에 API 호출 시 사용됩니다

### 2-3. 정보 기록

복사한 정보를 메모장에 임시 저장:

```
Secret Key: dGhpc2lzc2VjcmV0a2V5ZXhhbXBsZQ==
API URL: https://[your-domain].apigw.ntruss.com/custom/v1/12345/[your-id]/general
```

---

## ⚙️ 3단계: 프로젝트 설정

### 3-1. .env 파일 수정

1. **프로젝트 폴더 열기**
   ```bash
   cd /Users/seungjaihan/Documents/051012_SibangAIOCR
   ```

2. **sibangaiocr.env 파일 열기**
   - 텍스트 에디터로 `sibangaiocr.env` 파일 열기

3. **API 정보 입력**
   
   현재 파일 내용:
   ```env
   # 네이버 Clova OCR 설정 (현재 사용 중) ✅
   NAVER_OCR_SECRET_KEY=여기에_Secret_Key_입력
   NAVER_OCR_API_URL=여기에_API_URL_입력
   ```

   아래처럼 실제 값으로 변경:
   ```env
   # 네이버 Clova OCR 설정 (현재 사용 중) ✅
   NAVER_OCR_SECRET_KEY=dGhpc2lzc2VjcmV0a2V5ZXhhbXBsZQ==
   NAVER_OCR_API_URL=https://your-domain.apigw.ntruss.com/custom/v1/12345/your-id/general
   ```

4. **파일 이름 변경 (중요!)**
   ```bash
   # sibangaiocr.env를 .env로 이름 변경
   mv sibangaiocr.env .env
   ```
   
   또는 파인더에서:
   - `sibangaiocr.env` 파일 우클릭
   - "이름 바꾸기" 선택
   - `.env`로 변경

### 3-2. 환경 변수 로드 확인

프로젝트는 자동으로 `.env` 파일을 로드합니다:

```python
# ocr_processor.py에서 자동 로드됨
from dotenv import load_dotenv
load_dotenv()  # .env 파일의 환경 변수를 시스템에 로드
```

---

## ✅ 4단계: 동작 확인

### 4-1. Streamlit 앱 실행

```bash
# 터미널에서 실행
streamlit run app_streamlit.py
```

**예상 소요 시간**: 앱이 열리기까지 약 3-5초

### 4-2. OCR 엔진 선택

1. 브라우저에서 자동으로 `http://localhost:8501` 열림
2. 왼쪽 사이드바에서 **OCR 엔진 선택** 확인
3. **"naver_clova"**가 기본으로 선택되어 있어야 함 ✅
4. **"🔑 API 키 상태"** 섹션에서 녹색 체크 확인:
   ```
   ✅ Naver Clova OCR 설정 완료
   ```

### 4-3. 테스트 이미지로 OCR 실행

1. **이미지 업로드**
   - "시장 가판대 사진을 선택하세요" 클릭
   - 테스트 이미지 선택 (예: 화면에 보이는 바나나 이미지)

2. **OCR 시작**
   - **"🚀 OCR 시작"** 버튼 클릭
   - 처리 중... (약 3-7초 소요)

3. **결과 확인**
   - 성공 시:
     ```
     ✅ OCR 처리 완료!
     📊 인식된 상품 정보
     1. 바나나
        가격: 3500원
        단위: 1소쿠리
     ```
   - 실패 시: 아래 "문제 해결" 섹션 참조

---

## 🔧 문제 해결

### ❌ 문제 1: "Naver Clova OCR 키가 설정되지 않았습니다"

**원인**: `.env` 파일이 없거나 변수명이 잘못됨

**해결 방법**:
1. 파일 이름이 정확히 `.env`인지 확인 (`.env.txt` 아님!)
2. 변수명 확인:
   ```env
   NAVER_OCR_SECRET_KEY=실제키값   # 띄어쓰기 없이, 따옴표 없이
   NAVER_OCR_API_URL=실제URL     # 띄어쓰기 없이, 따옴표 없이
   ```
3. 앱 재시작:
   ```bash
   # Ctrl+C로 앱 종료 후 다시 실행
   streamlit run app_streamlit.py
   ```

### ❌ 문제 2: "Error 401: Unauthorized"

**원인**: Secret Key가 잘못됨

**해결 방법**:
1. 네이버 클라우드 콘솔에서 Secret Key 다시 확인
2. 복사할 때 공백이나 개행 포함 안 되도록 주의
3. `.env` 파일에 정확히 붙여넣기 (양쪽 공백 제거)

### ❌ 문제 3: "Error 404: Not Found"

**원인**: API URL이 잘못됨

**해결 방법**:
1. 네이버 클라우드 콘솔에서 "APIGW Invoke URL" 다시 확인
2. URL 끝에 `/general` 포함되어 있는지 확인
3. 전체 URL을 복사했는지 확인 (https://부터 끝까지)

### ❌ 문제 4: "텍스트를 찾을 수 없습니다"

**원인**: 이미지 품질이 낮거나 가격표가 너무 작음

**해결 방법**:
1. **이미지 품질 개선**:
   - 조명이 밝은 곳에서 재촬영
   - 가격표가 선명하게 보이도록 클로즈업
   - 초점이 맞는지 확인

2. **다른 OCR 엔진 시도**:
   - GPT-4 Vision (손글씨 인식 더 우수, 유료)
   - Google Vision (인쇄체에 강함)

### ❌ 문제 5: "모듈을 찾을 수 없습니다"

**원인**: 필요한 패키지가 설치되지 않음

**해결 방법**:
```bash
# 모든 필요한 패키지 재설치
pip install -r requirements.txt
```

**예상 소요 시간**: 패키지 설치 약 1-2분

---

## 📊 성능 및 비용

### 처리 성능

| 이미지 크기 | 처리 시간 | 정확도 (한글) | 정확도 (손글씨) |
|------------|----------|--------------|----------------|
| 1MB 미만 | 3-5초 | 95%+ | 85%+ |
| 1-5MB | 5-7초 | 95%+ | 85%+ |
| 5MB 이상 | 7-10초 | 95%+ | 85%+ |

### 월별 예상 비용

```
무료 제공량: 1,000건/월

사용량별 비용:
- 1,000건 이하: ₩0 (무료)
- 2,000건: 약 ₩50,000
- 5,000건: 약 ₩200,000
- 10,000건: 약 ₩450,000
```

**팁**: 개인 프로젝트나 소규모 사업장이라면 **월 1,000건으로 충분**합니다!

---

## 🎓 사용 팁

### 1. 인식률 높이는 방법

✅ **DO (권장)**:
- 밝은 조명에서 촬영
- 가격표를 화면 중앙에 배치
- 가능한 정면에서 촬영
- 초점이 선명하게 맞춘 상태로 촬영
- 가격표만 크롭하여 업로드

❌ **DON'T (비권장)**:
- 어두운 환경에서 촬영
- 가격표가 비스듬한 각도
- 흐릿하거나 흔들린 사진
- 가격표가 너무 작게 나온 사진

### 2. 비용 절감 방법

1. **이미지 크기 최적화**
   - 10MB 이상의 고화질은 불필요
   - 2-3MB 정도면 충분

2. **배치 처리**
   - 여러 상품이 있는 경우, 한 번에 촬영
   - API 호출 횟수 감소

3. **실패한 요청 재시도 최소화**
   - 이미지 품질을 먼저 확인 후 전송

### 3. 손글씨 인식 개선

손글씨가 잘 인식되지 않을 때:

1. **이미지 전처리 활용** (자동 적용됨)
   ```python
   # 이미 ocr_processor.py에 구현되어 있음
   processor.preprocess_image(image_path)
   ```

2. **GPT-4 Vision으로 전환** (더 높은 정확도)
   ```python
   # Streamlit 앱에서 OCR 엔진 선택 변경
   ocr_method = "gpt4_vision"
   ```

---

## 📞 추가 지원

### 네이버 클라우드 지원

- **FAQ**: https://guide.ncloud-docs.com/docs/clovaocr-overview
- **API 문서**: https://api.ncloud-docs.com/docs/ai-naver-clovaocr
- **고객 지원**: Console > 우측 상단 "고객지원" 클릭

### 프로젝트 관련 문제

- **GitHub Issues**: 프로젝트 저장소에 이슈 등록
- **로그 확인**: 터미널에서 에러 메시지 확인

---

## ✨ 성공적으로 설정 완료!

축하합니다! 🎉 이제 네이버 Clova OCR을 사용할 준비가 되었습니다.

**다음 단계**:
1. ✅ 실제 시장 가판대 사진으로 테스트
2. ✅ 인식 결과를 JSON으로 저장
3. ✅ 필요 시 모바일 앱 구축 (`mobile_guide.md` 참조)

---

**마지막 업데이트**: 2025년 10월 12일  
**작성자**: AI OCR 시스템 개발팀


