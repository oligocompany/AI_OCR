# 🚀 빠른 시작 가이드

5분 안에 시작하는 시장 가판대 OCR 시스템

## ⏱️ 예상 소요 시간
- **설치**: 2-3분
- **API 키 설정**: 1-2분
- **첫 실행**: 10초 이내

---

## 📋 사전 준비

### 1. Python 설치 확인
```bash
python --version
# Python 3.8 이상 필요
```

### 2. Git 클론 (이미 완료)
```bash
cd /Users/seungjaihan/Documents/051012_SibangAIOCR
```

---

## 🔧 설치 단계

### 1단계: 필요한 패키지 설치 (약 2분)
```bash
pip install -r requirements.txt
```

**문제가 생기면:**
```bash
# 가상환경 사용 권장
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2단계: API 키 설정 (약 1분)

#### 방법 A: OpenAI API 사용 (추천) ⭐

1. **API 키 발급**
   - https://platform.openai.com/api-keys 접속
   - "Create new secret key" 클릭
   - 키 복사 (sk-로 시작)

2. **.env 파일 생성**
```bash
# env_template.txt를 복사
cp env_template.txt .env

# .env 파일 편집
nano .env  # 또는 VS Code로 열기
```

3. **API 키 입력**
```bash
OPENAI_API_KEY=sk-여기에-실제-키-입력
```

#### 방법 B: Google Cloud Vision (무료 크레딧)
1. Google Cloud Console에서 프로젝트 생성
2. Vision API 활성화
3. 서비스 계정 생성 후 JSON 다운로드
4. .env에 경로 입력

#### 방법 C: Naver Clova OCR (한국어 특화)
1. https://www.ncloud.com/ 가입
2. AI Service > OCR 신청
3. API 키 발급
4. .env에 입력

---

## 🎬 실행 방법

### 방법 1: 웹 인터페이스 (가장 쉬움) ⭐

```bash
streamlit run app_streamlit.py
```

**자동으로 브라우저가 열립니다!**
- 주소: http://localhost:8501
- 이미지를 드래그 앤 드롭하거나 업로드
- "🚀 OCR 시작" 버튼 클릭
- 결과 확인!

**⏱️ 대기 시간**: 5-10초

### 방법 2: 커맨드라인 (빠름)

```bash
# 이미지 파일 경로 지정
python ocr_processor.py --image your_image.jpg

# OCR 방법 선택
python ocr_processor.py --image your_image.jpg --method gpt4_vision

# 결과 저장 경로 지정
python ocr_processor.py --image your_image.jpg --output result.json
```

**⏱️ 대기 시간**: 5-10초

### 방법 3: API 서버 (개발자용)

```bash
# 서버 시작
python app_fastapi.py
```

브라우저에서 http://localhost:8000/docs 접속
- Swagger UI에서 API 테스트 가능
- `/ocr` 엔드포인트 사용

**⏱️ 대기 시간**: 5-10초

---

## 📸 테스트 이미지

제공하신 이미지들을 `sample_images/` 폴더에 저장하세요:
- 건강조개류 이미지
- 채소 가판대 이미지
- 귤 오렌지 이미지
- 도루묵 이미지

```bash
# 테스트 실행
python ocr_processor.py --image sample_images/test1.jpg
```

---

## 📊 결과 예시

### JSON 출력
```json
{
  "products": [
    {
      "product_name": "계란 조개류",
      "price": "800원",
      "unit": "1개"
    },
    {
      "product_name": "귤 오렌지 (한라봉)",
      "price": "5000원",
      "unit": "1봉"
    }
  ],
  "metadata": {
    "method": "gpt4_vision",
    "total_items": 2,
    "timestamp": "2025-10-12T10:30:00"
  }
}
```

---

## 🎯 성능 비교

| OCR 방법 | 정확도 | 속도 | 비용 | 한글 손글씨 |
|---------|--------|------|------|------------|
| **GPT-4 Vision** | ⭐⭐⭐⭐⭐ | 5-10초 | $0.01/이미지 | ✅ 우수 |
| **Google Vision** | ⭐⭐⭐⭐ | 2-5초 | $0.0015/이미지 | ✅ 양호 |
| **Naver Clova** | ⭐⭐⭐⭐ | 3-7초 | 월 1000건 무료 | ⭐ 최고 |

**추천**: 처음에는 GPT-4 Vision으로 시작 (가장 쉽고 정확)

---

## 🔍 문제 해결

### 1. "OPENAI_API_KEY not found" 오류
```bash
# .env 파일 확인
cat .env

# API 키가 제대로 입력되었는지 확인
# 공백이나 따옴표 없이 입력
```

### 2. "Module not found" 오류
```bash
# 패키지 재설치
pip install --upgrade -r requirements.txt
```

### 3. 포트 충돌 (8501 or 8000 이미 사용 중)
```bash
# Streamlit 다른 포트로 실행
streamlit run app_streamlit.py --server.port 8502

# FastAPI 다른 포트로 실행
uvicorn app_fastapi:app --port 8001
```

### 4. 인식률이 낮을 때
- **이미지 품질 확인**: 해상도를 높이세요 (최소 800x600)
- **조명 개선**: 밝은 곳에서 촬영
- **각도 조정**: 가격표를 정면에서 촬영
- **크롭**: 가격표만 잘라서 촬영

### 5. 속도가 느릴 때
- **인터넷 연결 확인**: OCR은 API를 사용하므로 네트워크 필요
- **이미지 크기 줄이기**: 너무 큰 이미지는 처리 시간 증가
- **서버 지역**: 가까운 서버 사용

---

## 💰 비용 안내

### OpenAI GPT-4 Vision
- 이미지당 약 $0.01~0.03
- 100장 처리: 약 $1~3
- 크레딧 충전: https://platform.openai.com/billing

### Google Cloud Vision
- 월 1,000건 무료
- 이후 건당 $0.0015
- 무료 크레딧: $300 (신규 가입 시)

### Naver Clova OCR
- 월 1,000건 무료
- 이후 100건당 1,100원 (약 $0.85)

**💡 팁**: 테스트는 무료 할당량으로 충분합니다!

---

## 📞 도움이 필요하면

1. **문서 확인**: README.md
2. **모바일 앱**: mobile_guide.md
3. **이슈 등록**: GitHub Issues (있는 경우)
4. **로그 확인**: 에러 메시지를 자세히 읽어보세요

---

## ✅ 체크리스트

- [ ] Python 3.8+ 설치됨
- [ ] requirements.txt 설치 완료
- [ ] .env 파일 생성 및 API 키 입력
- [ ] 테스트 이미지 준비
- [ ] 웹 인터페이스 실행 성공
- [ ] OCR 결과 확인

**모두 체크했다면 준비 완료!** 🎉

---

## 🚀 다음 단계

1. **성능 최적화**: 이미지 전처리 파라미터 조정
2. **모바일 앱**: mobile_guide.md 참고
3. **데이터베이스 연동**: 인식 결과 저장
4. **배치 처리**: 여러 이미지 한 번에 처리
5. **배포**: 클라우드 서버에 배포

---

**즐거운 개발 되세요!** 💻✨









