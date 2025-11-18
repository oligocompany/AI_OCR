# 📝 프로젝트 요약 - 시장 가판대 OCR 시스템

## 🎯 프로젝트 목표

핸드폰으로 촬영한 시장 가판대 사진에서 **상품명**과 **가격** 정보를 자동으로 인식하여 **JSON 형식**으로 변환하는 AI OCR 시스템을 개발했습니다.

---

## ✨ 주요 기능

### 1. 📸 이미지 인식
- 핸드폰 카메라로 촬영한 사진 지원
- 한글 손글씨 가격표 인식
- 여러 상품이 있는 이미지도 처리 가능

### 2. 🤖 AI OCR 엔진 (3가지 선택)
- **GPT-4 Vision** (OpenAI) - 가장 정확, 손글씨 우수
- **Google Cloud Vision** - 빠르고 안정적
- **Naver Clova OCR** - 한국어 특화

### 3. 📊 JSON 출력
```json
{
  "products": [
    {
      "product_name": "계란 조개류",
      "price": "800원",
      "unit": "1개"
    }
  ]
}
```

### 4. 💻 다양한 사용 방법
- **웹 인터페이스** (Streamlit) - 브라우저에서 사용
- **API 서버** (FastAPI) - 모바일 앱 연동
- **커맨드라인** - 자동화 스크립트

---

## 🛠️ 사용된 기술

### 핵심 기술
| 분야 | 기술/라이브러리 | 역할 |
|-----|----------------|------|
| **AI/ML** | OpenAI GPT-4 Vision | 이미지에서 텍스트 이해 및 추출 |
| | Google Cloud Vision | OCR 처리 |
| | Naver Clova OCR | 한글 특화 OCR |
| **이미지 처리** | OpenCV | 이미지 전처리 (노이즈 제거, 대비 향상) |
| | Pillow (PIL) | 이미지 읽기/변환 |
| **웹 프레임워크** | Streamlit | 사용자 친화적 웹 UI |
| | FastAPI | REST API 서버 |
| **언어** | Python 3.8+ | 메인 프로그래밍 언어 |

### 이미지 전처리 기법
1. **그레이스케일 변환** - 색상 정보 제거
2. **가우시안 블러** - 노이즈 제거
3. **CLAHE** - 대비 향상 (어두운 부분 개선)
4. **적응형 이진화** - 배경과 글자 분리

---

## 📁 프로젝트 구조

```
051012_SibangAIOCR/
│
├── 핵심 코드
│   ├── ocr_processor.py      # OCR 처리 클래스
│   ├── app_streamlit.py      # 웹 UI
│   ├── app_fastapi.py        # API 서버
│   └── test_ocr.py           # 테스트 스크립트
│
├── 문서
│   ├── README.md             # 프로젝트 소개
│   ├── QUICK_START.md        # 빠른 시작 가이드
│   ├── TECHNICAL_DETAILS.md  # 기술 상세
│   ├── mobile_guide.md       # 모바일 앱 개발
│   └── PROJECT_STRUCTURE.md  # 프로젝트 구조
│
├── 설정
│   ├── requirements.txt      # Python 패키지
│   ├── env_template.txt      # API 키 템플릿
│   └── .gitignore           # Git 제외 파일
│
├── 실행 스크립트
│   ├── run.sh               # Mac/Linux
│   └── run.bat              # Windows
│
└── 샘플
    └── sample_images/       # 테스트 이미지
```

---

## 🚀 사용 방법 (3단계)

### 1단계: 설치 (2-3분)
```bash
# 패키지 설치
pip install -r requirements.txt

# API 키 설정
cp env_template.txt .env
# .env 파일을 열어 OPENAI_API_KEY 입력
```

### 2단계: 실행 (10초)
```bash
# 방법 1: 웹 인터페이스 (가장 쉬움)
streamlit run app_streamlit.py

# 방법 2: 간편 스크립트
./run.sh  # Mac/Linux
run.bat   # Windows
```

### 3단계: 이미지 업로드
1. 브라우저에서 http://localhost:8501 열기
2. 시장 가판대 사진 업로드
3. "🚀 OCR 시작" 클릭
4. 5-10초 대기
5. 결과 확인 및 JSON 다운로드

---

## 💡 실제 사용 예시

### 입력: 시장 가판대 사진
- 건강조개류 800원
- 귤 오렌지 (한라봉) 5000원
- 죽은 척하는 도루묵 1소쿠리 만원

### 출력: JSON
```json
{
  "products": [
    {
      "product_name": "건강조개류",
      "price": "800원",
      "unit": "1개",
      "confidence": 0.95
    },
    {
      "product_name": "귤 오렌지 (한라봉)",
      "price": "5000원",
      "unit": "1봉",
      "confidence": 0.92
    },
    {
      "product_name": "죽은 척하는 도루묵",
      "price": "만원",
      "unit": "1소쿠리",
      "confidence": 0.88
    }
  ],
  "metadata": {
    "method": "gpt4_vision",
    "total_items": 3,
    "timestamp": "2025-10-12T10:30:00"
  }
}
```

---

## 📊 성능 비교

| OCR 방법 | 정확도 | 속도 | 비용/이미지 | 한글 손글씨 | 추천도 |
|---------|--------|------|------------|------------|--------|
| **GPT-4 Vision** | ⭐⭐⭐⭐⭐ | 5-10초 | $0.01-0.03 | ✅ 우수 | ⭐⭐⭐⭐⭐ |
| **Google Vision** | ⭐⭐⭐⭐ | 2-5초 | $0.0015 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Naver Clova** | ⭐⭐⭐⭐ | 3-7초 | 월 1000건 무료 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**결론**: 처음 사용자는 **GPT-4 Vision** 추천 (가장 쉽고 정확)

---

## 💰 비용 안내

### 테스트 단계 (100장 처리)
- GPT-4 Vision: 약 $1-3
- Google Vision: 무료 (월 1,000건)
- Naver Clova: 무료 (월 1,000건)

### 실제 운영 (월 10,000장)
- GPT-4 Vision: $100-300
- Google Vision: $13.50
- Naver Clova: $85 + 무료 1,000건

**💡 팁**: 처음에는 무료 할당량으로 충분히 테스트 가능!

---

## 🎯 활용 방안

### 1. 시장 가격 모니터링 앱
- 여러 시장의 가격 비교
- 시간대별 가격 변동 추적
- 저렴한 시장 추천

### 2. 온라인 쇼핑몰 자동 등록
- 시장 상품을 촬영만 하면 자동 등록
- 가격 자동 업데이트
- 재고 관리

### 3. 가계부 자동화
- 장보기 영수증 대신 사진 촬영
- 자동으로 지출 기록
- 월별 통계

### 4. 배달 대행 서비스
- 고객이 원하는 상품 사진만 보내면
- 자동으로 가격 확인
- 주문 처리

### 5. 시장 데이터 분석
- 지역별 가격 차이
- 계절별 가격 변동
- 빅데이터 구축

---

## 📱 모바일 앱 확장

### React Native 앱 (크로스 플랫폼)
```typescript
// 카메라로 촬영
const photo = await launchCamera();

// API 서버로 전송
const result = await fetch('http://server/ocr', {
  method: 'POST',
  body: formData
});

// 결과 표시
setProducts(result.products);
```

### 주요 기능
- ✅ 카메라 실시간 촬영
- ✅ 갤러리에서 선택
- ✅ 이미지 크롭/회전
- ✅ 결과 저장 및 공유
- ✅ 오프라인 모드 (로컬 저장 후 동기화)

**자세한 내용**: `mobile_guide.md` 참고

---

## 🔒 보안 및 프라이버시

### API 키 관리
- ✅ `.env` 파일 사용 (Git에서 제외)
- ✅ 환경 변수로 관리
- ❌ 코드에 직접 입력 금지

### 이미지 처리
- ✅ 임시 파일은 처리 후 즉시 삭제
- ✅ 서버에 이미지 저장 안 함
- ✅ HTTPS 사용 (배포 시)

### API 사용
- ✅ 요청 제한 (Rate Limiting)
- ✅ 파일 크기 제한 (10MB)
- ✅ 허용된 파일 형식만 처리

---

## 🐛 문제 해결

### Q1: "OPENAI_API_KEY not found" 오류
**해결**: `.env` 파일을 생성하고 API 키를 입력하세요.
```bash
cp env_template.txt .env
nano .env
```

### Q2: 인식률이 낮아요
**해결**:
- 밝은 곳에서 촬영
- 가격표를 정면에서 촬영
- 초점을 맞춰 선명하게
- GPT-4 Vision 사용

### Q3: 속도가 느려요
**해결**:
- 인터넷 연결 확인
- 이미지 크기를 줄이기 (1-2MB 권장)
- Google Vision 사용 (더 빠름)

### Q4: 모듈을 찾을 수 없어요
**해결**:
```bash
pip install -r requirements.txt
# 또는 가상환경 사용
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 학습 자료

### 프로젝트 문서 (순서대로 읽기)
1. **README.md** - 프로젝트 전체 개요
2. **QUICK_START.md** - 5분 빠른 시작
3. **PROJECT_STRUCTURE.md** - 파일 구조 이해
4. **TECHNICAL_DETAILS.md** - 기술 깊이 있게 배우기
5. **mobile_guide.md** - 모바일 앱 만들기

### 외부 자료
- [OpenAI Vision API](https://platform.openai.com/docs/guides/vision)
- [Google Cloud Vision](https://cloud.google.com/vision/docs)
- [OpenCV 튜토리얼](https://docs.opencv.org/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Streamlit 가이드](https://docs.streamlit.io/)

---

## 🎓 코드에서 배울 수 있는 것

### 1. 이미지 처리 (OpenCV)
- 전처리 기법
- 노이즈 제거
- 대비 향상

### 2. AI API 사용
- OpenAI API 호출
- Google Cloud API
- 프롬프트 엔지니어링

### 3. 웹 개발
- Streamlit 인터페이스
- FastAPI REST API
- 비동기 처리

### 4. 시스템 설계
- 모듈화
- 에러 처리
- 로깅

### 5. 배포
- 환경 변수 관리
- Docker 컨테이너
- 클라우드 배포

---

## 🚀 다음 단계 (확장 아이디어)

### 단기 (1-2주)
- [ ] 더 많은 이미지로 테스트
- [ ] 정확도 개선 (전처리 파라미터 조정)
- [ ] 배치 처리 최적화

### 중기 (1개월)
- [ ] 모바일 앱 개발 (React Native)
- [ ] 데이터베이스 연동 (PostgreSQL)
- [ ] 가격 이력 저장 및 분석

### 장기 (2-3개월)
- [ ] Object Detection 추가 (YOLO)
- [ ] 실시간 카메라 스트림 처리
- [ ] 클라우드 배포 (AWS/GCP)
- [ ] 관리자 대시보드
- [ ] 알림 시스템 (가격 변동)

---

## 🤝 기여 및 피드백

이 프로젝트는 학습 및 실용 목적으로 만들어졌습니다.

### 개선 아이디어
- 더 빠른 OCR 엔진 추가
- 오프라인 모드 (Tesseract)
- 다국어 지원
- 영수증 인식 확장
- 바코드/QR코드 인식

### 피드백
- 버그 발견 시 이슈 등록
- 개선 제안
- 사용 후기 공유

---

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 자유롭게 사용 가능합니다.

단, 각 API 서비스(OpenAI, Google, Naver)의 이용 약관을 준수해야 합니다.

---

## 🎉 마무리

시장 가판대 OCR 시스템을 만들기 위해 필요한 모든 것을 준비했습니다!

### ✅ 완성된 것
1. ✅ 핵심 OCR 처리 코드
2. ✅ 웹 인터페이스 (Streamlit)
3. ✅ API 서버 (FastAPI)
4. ✅ 이미지 전처리
5. ✅ 3가지 OCR 엔진 지원
6. ✅ JSON 결과 출력
7. ✅ 상세한 문서
8. ✅ 테스트 스크립트
9. ✅ 모바일 앱 가이드
10. ✅ 실행 스크립트

### 🚀 시작하기
```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. API 키 설정
cp env_template.txt .env
# .env 파일 편집

# 3. 실행!
./run.sh  # Mac/Linux
run.bat   # Windows
```

### 📞 도움이 필요하면
- 문서를 차근차근 읽어보세요
- `test_ocr.py`로 설정 확인
- 오류 메시지를 자세히 읽기

---

**즐거운 개발 되세요!** 🎊🎈

질문이 있으면 언제든지 문의하세요! 😊









