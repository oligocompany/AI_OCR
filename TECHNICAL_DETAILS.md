# 🔬 기술 상세 설명

시장 가판대 OCR 시스템의 기술적 구조와 작동 원리

## 📐 시스템 아키텍처

```
┌─────────────────┐
│  사용자 인터페이스 │
│  (웹/모바일)      │
└────────┬────────┘
         │ 이미지 업로드
         ▼
┌─────────────────────────┐
│  이미지 전처리           │
│  - 크기 조정             │
│  - 노이즈 제거           │
│  - 대비 향상             │
└────────┬────────────────┘
         │ 전처리된 이미지
         ▼
┌─────────────────────────┐
│  OCR 엔진               │
│  ┌─────────────────┐   │
│  │ GPT-4 Vision    │   │
│  ├─────────────────┤   │
│  │ Google Vision   │   │
│  ├─────────────────┤   │
│  │ Naver Clova     │   │
│  └─────────────────┘   │
└────────┬────────────────┘
         │ 추출된 텍스트
         ▼
┌─────────────────────────┐
│  텍스트 파싱 & 구조화    │
│  - 상품명 추출           │
│  - 가격 추출             │
│  - 단위 추출             │
└────────┬────────────────┘
         │ JSON 데이터
         ▼
┌─────────────────────────┐
│  결과 반환              │
│  - JSON 형식            │
│  - 메타데이터           │
└─────────────────────────┘
```

## 🧠 핵심 기술

### 1. 이미지 전처리 (OpenCV)

#### 목적
- OCR 인식률 향상
- 노이즈 제거
- 텍스트 선명도 개선

#### 주요 기법

**a) 그레이스케일 변환**
```python
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
```
- 컬러 정보를 제거하여 텍스트 추출에 집중
- 처리 속도 향상

**b) 가우시안 블러 (노이즈 제거)**
```python
denoised = cv2.GaussianBlur(gray, (5, 5), 0)
```
- 이미지의 미세한 노이즈 제거
- 가격표 배경의 불필요한 패턴 제거

**c) CLAHE (대비 향상)**
```python
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(denoised)
```
- Contrast Limited Adaptive Histogram Equalization
- 어두운 부분과 밝은 부분의 대비를 개선
- 손글씨의 획을 더 선명하게 만듦

**d) 적응형 이진화**
```python
binary = cv2.adaptiveThreshold(
    enhanced, 255, 
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    cv2.THRESH_BINARY, 11, 2
)
```
- 조명이 불균일한 환경에서도 텍스트 추출
- 배경과 글자를 명확하게 분리

### 2. OCR 엔진 비교

#### A. GPT-4 Vision (OpenAI) ⭐

**작동 원리:**
- 대규모 언어 모델(LLM) + 비전 트랜스포머
- 이미지를 토큰화하여 텍스트와 함께 처리
- 맥락을 이해하여 상품명과 가격을 구조화

**장점:**
- 손글씨 인식 정확도 최고
- 맥락 이해 (예: "만원" → "10000원" 변환)
- 구조화된 JSON 직접 출력
- 추가 학습 불필요

**단점:**
- 비용이 가장 높음 (이미지당 $0.01~0.03)
- 처리 속도 중간 (5-10초)
- 인터넷 연결 필수

**사용 케이스:**
- 손글씨가 많은 전통 시장
- 높은 정확도가 필요한 경우
- 복잡한 레이아웃

#### B. Google Cloud Vision

**작동 원리:**
- CNN(Convolutional Neural Network) 기반
- 텍스트 영역 감지 → 문자 인식 → 단어 조합
- 다국어 모델 (한글 지원)

**장점:**
- 빠른 속도 (2-5초)
- 비용 효율적 ($0.0015/이미지)
- 월 1,000건 무료
- 안정적인 API

**단점:**
- 손글씨 인식률 중간
- 구조화 파싱 추가 필요
- 맥락 이해 제한적

**사용 케이스:**
- 인쇄된 가격표
- 대량 처리
- 비용 절감 필요

#### C. Naver Clova OCR

**작동 원리:**
- 한글에 특화된 딥러닝 모델
- 한국 환경에 최적화
- 템플릿 기반 + AI 인식

**장점:**
- 한글 손글씨 우수
- 한국 시장 특화 (원, 만원 등)
- 월 1,000건 무료
- 국내 서버로 빠른 응답

**단점:**
- API 신청 절차 필요
- 문서 위주 최적화
- 구조화 파싱 추가 필요

**사용 케이스:**
- 한국 시장 전용
- 개인정보 보호 (국내 서버)
- 한글 특화 필요

### 3. 텍스트 파싱

#### 정규표현식 기반 파싱
```python
# 가격 패턴
price_pattern = r'(\d[\d,]*)\s*원|(\d+)\s*만\s*원'

# 예시:
# "800원" → 800원
# "5,000원" → 5000원
# "1만원" → 10000원
# "1소쿠리 만원" → 10000원
```

#### GPT-4 Vision의 구조화
- 프롬프트 엔지니어링으로 JSON 직접 생성
- 상품명, 가격, 단위를 자동 분류
- 추가 정보 (괄호 안 내용 등) 추출

### 4. API 설계 (FastAPI)

#### RESTful 엔드포인트

**POST /ocr**
- 이미지 업로드 및 처리
- FormData 형식 (multipart/form-data)
- 응답: JSON 형식 결과

**POST /ocr/batch**
- 여러 이미지 동시 처리
- 배치 처리로 효율성 향상
- 최대 10개 이미지

**GET /health**
- 서비스 상태 확인
- 로드 밸런서 헬스 체크용

#### 비동기 처리
```python
async def process_ocr(file: UploadFile):
    # 비동기로 파일 읽기
    content = await file.read()
    
    # OCR 처리 (별도 스레드)
    result = await asyncio.to_thread(
        processor.process_image, 
        temp_path
    )
```

### 5. 웹 인터페이스 (Streamlit)

#### 실시간 처리
```python
if st.button("OCR 시작"):
    with st.spinner("처리 중..."):
        result = processor.process_image(image_path)
    st.success("완료!")
    st.json(result)
```

#### 상태 관리
- 세션 상태로 이미지 및 결과 유지
- 캐싱으로 반복 처리 방지

## 🔐 보안 고려사항

### API 키 관리
```python
# .env 파일 사용 (Git에서 제외)
OPENAI_API_KEY=sk-...

# 코드에서 직접 노출 금지
# ❌ api_key = "sk-xxxxx"
# ✅ api_key = os.getenv("OPENAI_API_KEY")
```

### 파일 업로드 검증
```python
# 파일 형식 제한
allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]

# 파일 크기 제한
max_file_size = 10 * 1024 * 1024  # 10MB

# 악성 파일 방지
if not is_valid_image(file):
    raise HTTPException(400, "유효하지 않은 이미지")
```

### 임시 파일 관리
```python
# 임시 파일은 처리 후 즉시 삭제
try:
    process_image(temp_file)
finally:
    os.unlink(temp_file)
```

## 📊 성능 최적화

### 1. 이미지 크기 최적화
```python
# 너무 큰 이미지는 리사이즈
max_dimension = 2048
if width > max_dimension or height > max_dimension:
    scale = max_dimension / max(width, height)
    new_size = (int(width * scale), int(height * scale))
    image = image.resize(new_size)
```

### 2. 캐싱
```python
# Streamlit 캐싱
@st.cache_data
def load_model():
    return OCRProcessor()

# 결과 캐싱 (동일 이미지 재처리 방지)
```

### 3. 병렬 처리
```python
# 배치 처리 시 병렬 실행
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(process_image, image_list)
```

## 🧪 테스트 전략

### 단위 테스트
```python
def test_preprocess_image():
    image = cv2.imread("test.jpg")
    result = preprocess_image(image)
    assert result is not None
    assert result.shape[2] == 1  # 그레이스케일

def test_parse_price():
    text = "사과 5,000원"
    result = parse_text_to_products(text)
    assert result[0]["price"] == "5,000원"
```

### 통합 테스트
```python
def test_end_to_end():
    processor = MarketOCRProcessor()
    result = processor.process_image("sample.jpg")
    assert "products" in result
    assert len(result["products"]) > 0
```

### 부하 테스트
```bash
# Apache Bench로 API 부하 테스트
ab -n 100 -c 10 -p image.json -T application/json \
   http://localhost:8000/ocr
```

## 🚀 배포 옵션

### 1. 로컬 개발
```bash
streamlit run app_streamlit.py
# 또는
uvicorn app_fastapi:app --reload
```

### 2. Docker 컨테이너
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app_streamlit.py"]
```

### 3. 클라우드 배포

**Heroku:**
```bash
git push heroku main
```

**Google Cloud Run:**
```bash
gcloud run deploy --source .
```

**AWS Lambda + API Gateway:**
- Serverless 프레임워크 사용
- 이미지는 S3에 저장

## 📈 확장 가능성

### 1. 데이터베이스 연동
```python
# PostgreSQL에 결과 저장
import psycopg2

conn = psycopg2.connect(database_url)
cursor = conn.cursor()
cursor.execute(
    "INSERT INTO products (name, price) VALUES (%s, %s)",
    (product_name, price)
)
```

### 2. 실시간 카메라 스트림
```python
# 웹캠에서 실시간 OCR
import cv2

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    result = processor.process_frame(frame)
    # 결과 오버레이
```

### 3. 가격 변동 추적
```python
# 시간별 가격 변화 모니터링
def track_price_changes(product_name):
    history = get_price_history(product_name)
    return calculate_trend(history)
```

### 4. 다국어 지원
```python
# 언어 감지 및 처리
from langdetect import detect

language = detect(extracted_text)
if language == 'ko':
    parse_korean_format(text)
elif language == 'en':
    parse_english_format(text)
```

## 🔬 알려진 제한사항

### 1. 손글씨 품질
- 매우 흐릿하거나 특이한 필체는 인식 어려움
- 해결책: 이미지 품질 향상, GPT-4 Vision 사용

### 2. 복잡한 배경
- 상품과 가격표가 겹쳐있는 경우
- 해결책: Object Detection으로 가격표만 추출

### 3. 비표준 표기
- "만원", "천원" 등 한글 표기
- 해결책: GPT-4 Vision의 맥락 이해 활용

### 4. 네트워크 의존성
- 모든 OCR 방법이 API 호출 필요
- 해결책: Tesseract 등 오프라인 OCR 추가

## 📚 참고 자료

- [OpenAI Vision API 문서](https://platform.openai.com/docs/guides/vision)
- [Google Cloud Vision 가이드](https://cloud.google.com/vision/docs)
- [Naver Clova OCR](https://www.ncloud.com/product/aiService/ocr)
- [OpenCV 튜토리얼](https://docs.opencv.org/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Streamlit 문서](https://docs.streamlit.io/)












