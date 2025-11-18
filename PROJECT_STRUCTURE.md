# 📁 프로젝트 구조

```
051012_SibangAIOCR/
│
├── 📄 README.md                    # 프로젝트 소개 및 설치 가이드
├── 📄 QUICK_START.md              # 5분 빠른 시작 가이드
├── 📄 TECHNICAL_DETAILS.md        # 기술 상세 설명
├── 📄 PROJECT_STRUCTURE.md        # 이 파일 (프로젝트 구조)
├── 📄 mobile_guide.md             # 모바일 앱 개발 가이드
│
├── 📦 requirements.txt             # Python 패키지 의존성
├── 📄 .gitignore                   # Git 제외 파일 목록
├── 📄 env_template.txt            # 환경 변수 템플릿
│
├── 🐍 ocr_processor.py            # 핵심 OCR 처리 클래스
├── 🌐 app_streamlit.py            # Streamlit 웹 인터페이스
├── 🚀 app_fastapi.py              # FastAPI REST API 서버
├── 🧪 test_ocr.py                 # 테스트 및 설정 확인 스크립트
│
├── 📂 sample_images/               # 테스트용 이미지 폴더
│   └── 📄 README.md               # 이미지 사용 가이드
│
└── 📂 mobile/                      # 모바일 앱 (선택사항)
    ├── App.tsx                     # React Native 메인 컴포넌트
    ├── package.json                # Node.js 의존성
    └── README.md                   # 모바일 앱 설명
```

## 📚 파일별 설명

### 핵심 파일

#### 📄 `ocr_processor.py`
**역할**: OCR 처리 핵심 로직
- `MarketOCRProcessor` 클래스
  - 이미지 전처리
  - 여러 OCR 엔진 지원
  - JSON 결과 생성
- 단독 실행 가능 (커맨드라인)

**주요 메서드**:
```python
processor = MarketOCRProcessor(method="gpt4_vision")
result = processor.process_image("image.jpg")
processor.save_result(result, "output.json")
```

**의존성**:
- OpenCV (이미지 전처리)
- OpenAI SDK (GPT-4 Vision)
- Google Cloud Vision SDK
- Pillow (이미지 처리)

---

#### 🌐 `app_streamlit.py`
**역할**: 웹 기반 사용자 인터페이스
- 브라우저에서 이미지 업로드
- 실시간 OCR 처리
- 결과 시각화
- JSON 다운로드

**실행 방법**:
```bash
streamlit run app_streamlit.py
```

**포트**: 8501

**특징**:
- 드래그 앤 드롭 지원
- 실시간 프로그레스 바
- 결과 JSON 다운로드
- OCR 방법 선택 가능

---

#### 🚀 `app_fastapi.py`
**역할**: REST API 서버
- 프로그래밍 방식으로 OCR 호출
- 모바일 앱, 다른 서비스와 연동
- 배치 처리 지원

**실행 방법**:
```bash
python app_fastapi.py
```

**주요 엔드포인트**:
- `POST /ocr` - 단일 이미지 처리
- `POST /ocr/batch` - 여러 이미지 배치 처리
- `GET /health` - 서버 상태 확인
- `GET /docs` - Swagger UI (API 문서)

**포트**: 8000

**사용 예시**:
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@market_photo.jpg" \
  -F "method=gpt4_vision"
```

---

#### 🧪 `test_ocr.py`
**역할**: 시스템 테스트 및 검증
- API 키 설정 확인
- 필수 패키지 검증
- 샘플 이미지 테스트
- 대화형 메뉴

**실행 방법**:
```bash
python test_ocr.py
```

**기능**:
1. 환경 설정 검증
2. 빠른 OCR 테스트
3. 사용자 지정 이미지 처리
4. 웹/API 서버 실행

---

### 문서 파일

#### 📄 `README.md`
- 프로젝트 개요
- 주요 기능
- 설치 방법
- 기본 사용법
- API 키 설정

#### 📄 `QUICK_START.md`
- 5분 빠른 시작
- 단계별 설치 가이드
- 예상 소요 시간 표시
- 문제 해결 팁
- 비용 안내

#### 📄 `TECHNICAL_DETAILS.md`
- 시스템 아키텍처
- 각 OCR 엔진 상세 비교
- 이미지 전처리 알고리즘
- 성능 최적화
- 보안 고려사항
- 배포 가이드

#### 📄 `mobile_guide.md`
- React Native 앱 개발
- Flutter 앱 개발
- 웹뷰 방식
- 권한 설정
- 앱 스토어 배포

---

### 설정 파일

#### 📦 `requirements.txt`
Python 패키지 목록:
```
openai>=1.0.0              # GPT-4 Vision
google-cloud-vision>=3.4.0 # Google Vision API
pillow>=10.0.0             # 이미지 처리
opencv-python>=4.8.0       # 이미지 전처리
streamlit>=1.28.0          # 웹 UI
fastapi>=0.104.0           # REST API
uvicorn>=0.24.0            # ASGI 서버
python-dotenv>=1.0.0       # 환경 변수
```

#### 📄 `env_template.txt`
환경 변수 템플릿:
```bash
OPENAI_API_KEY=sk-your-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
NAVER_OCR_SECRET_KEY=your-key
NAVER_OCR_API_URL=https://your-url
```

#### 📄 `.gitignore`
Git에서 제외할 파일:
- `.env` (API 키)
- `__pycache__/`
- `venv/`
- 결과 파일
- 업로드된 이미지

---

## 🔄 데이터 흐름

### 1. 웹 인터페이스 (Streamlit)
```
사용자
  │
  ├─ 이미지 업로드
  │   └─ app_streamlit.py
  │       └─ ocr_processor.py
  │           ├─ 전처리 (OpenCV)
  │           ├─ OCR API 호출
  │           │   ├─ OpenAI
  │           │   ├─ Google
  │           │   └─ Naver
  │           └─ JSON 결과
  │               └─ 브라우저 표시
  └─ 결과 다운로드
```

### 2. API 서버 (FastAPI)
```
클라이언트 (모바일/웹)
  │
  ├─ POST /ocr
  │   └─ app_fastapi.py
  │       └─ ocr_processor.py
  │           └─ (동일한 처리)
  └─ JSON 응답
```

### 3. 커맨드라인
```
터미널
  │
  ├─ python ocr_processor.py --image photo.jpg
  │   └─ ocr_processor.py (직접 실행)
  │       └─ result.json 저장
  └─ 파일 출력
```

---

## 🎯 사용 시나리오별 선택

### 시나리오 1: 간단한 테스트
**추천**: Streamlit 웹 인터페이스
```bash
streamlit run app_streamlit.py
```
- 가장 쉬움
- 시각적 피드백
- 즉시 결과 확인

### 시나리오 2: 자동화 스크립트
**추천**: 커맨드라인
```bash
python ocr_processor.py --image photo.jpg --output result.json
```
- 배치 처리
- cron job 설정 가능
- 파이프라인 통합

### 시나리오 3: 모바일 앱 개발
**추천**: FastAPI 서버
```bash
python app_fastapi.py
```
- REST API 제공
- 여러 클라이언트 지원
- 확장 가능

### 시나리오 4: 대량 처리
**추천**: Python 스크립트 작성
```python
from ocr_processor import MarketOCRProcessor

processor = MarketOCRProcessor()
for image_path in image_list:
    result = processor.process_image(image_path)
    save_to_database(result)
```

---

## 🔧 개발 워크플로우

### 1. 초기 설정
```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp env_template.txt .env
nano .env  # API 키 입력

# 4. 테스트
python test_ocr.py
```

### 2. 개발 및 테스트
```bash
# 로컬 웹 서버 실행
streamlit run app_streamlit.py

# 또는 API 서버
python app_fastapi.py

# 코드 수정 후 자동 리로드됨
```

### 3. 디버깅
```bash
# 자세한 로그 출력
python ocr_processor.py --image test.jpg --verbose

# Python 디버거
python -m pdb app_fastapi.py
```

### 4. 배포
```bash
# Docker 이미지 빌드
docker build -t market-ocr .

# 실행
docker run -p 8000:8000 market-ocr

# 클라우드 배포
git push heroku main
```

---

## 📊 성능 벤치마크

### 처리 시간 (이미지 1장 기준)

| 단계 | 소요 시간 |
|-----|----------|
| 이미지 전처리 | 0.1초 |
| GPT-4 Vision | 5-10초 |
| Google Vision | 2-5초 |
| Naver Clova | 3-7초 |
| JSON 파싱 | 0.01초 |
| **총합** | **5-10초** |

### 메모리 사용량

| 구성요소 | 메모리 |
|---------|--------|
| Python 런타임 | 50MB |
| OpenCV | 100MB |
| 이미지 버퍼 | 10-50MB |
| **총합** | **~200MB** |

---

## 🎓 학습 경로

### 초급 (1-2일)
1. ✅ 프로젝트 클론 및 설정
2. ✅ Streamlit 웹 실행
3. ✅ 샘플 이미지 테스트
4. ✅ 결과 확인

### 중급 (1주)
1. ✅ `ocr_processor.py` 코드 이해
2. ✅ API 서버 구축
3. ✅ 이미지 전처리 파라미터 조정
4. ✅ 커스텀 파싱 로직 추가

### 고급 (2-4주)
1. ✅ 모바일 앱 개발
2. ✅ 데이터베이스 연동
3. ✅ 실시간 카메라 스트림
4. ✅ 클라우드 배포
5. ✅ 가격 추적 시스템 구축

---

## 🤝 기여 및 확장

### 추가 가능한 기능

1. **Object Detection**
   - YOLO로 가격표 영역 자동 감지
   - 크롭 후 OCR로 정확도 향상

2. **데이터베이스**
   - PostgreSQL/MySQL 연동
   - 가격 이력 저장
   - 트렌드 분석

3. **알림 시스템**
   - 가격 변동 알림
   - 특정 상품 모니터링
   - 이메일/SMS 발송

4. **관리자 패널**
   - 사용 통계
   - 비용 모니터링
   - 사용자 관리

5. **오프라인 모드**
   - Tesseract OCR 통합
   - 로컬 처리
   - 네트워크 없이 작동

---

## 📞 지원 및 문의

- **문서**: 이 폴더의 모든 `.md` 파일 참고
- **테스트**: `python test_ocr.py` 실행
- **디버깅**: 상세 로그 확인

---

**프로젝트를 즐겁게 사용하세요!** 🎉









