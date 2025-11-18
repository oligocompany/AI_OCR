# 시장 가판대 상품정보 OCR 시스템

## 📖 프로젝트 개요
시장 가판대 사진에서 상품명과 가격 정보를 자동으로 인식하여 JSON 형태로 변환하는 AI OCR 시스템입니다.

## 🎯 주요 기능
- 📸 이미지 업로드 (로컬 파일 또는 URL)
- 🔍 한글 손글씨 가격표 인식
- 📊 상품명과 가격 자동 추출
- 💾 JSON 형식으로 결과 저장
- 🌐 웹 인터페이스 제공

## 🛠 사용 기술
- **OCR**: **Naver Clova OCR (추천, 무료)** / Google Cloud Vision API / GPT-4 Vision
- **이미지 처리**: OpenCV, Pillow
- **백엔드**: Python, FastAPI
- **프론트엔드**: Streamlit (웹 UI)

> ✨ **추천**: 한국어 시장 가판대 인식에는 **네이버 Clova OCR**을 사용하세요! (월 1,000건 무료)

## 📦 설치 방법

### 1. 필수 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정

#### ⭐ 추천: 네이버 Clova OCR (무료, 한국어 특화)

1. `sibangaiocr.env` 파일을 `.env`로 이름 변경
2. 네이버 클라우드 플랫폼에서 API 키 발급 (자세한 방법은 `NAVER_OCR_SETUP.md` 참조)
3. `.env` 파일에 정보 입력:

```env
# 네이버 Clova OCR (한국어 최적화, 월 1,000건 무료)
NAVER_OCR_SECRET_KEY=발급받은_Secret_Key
NAVER_OCR_API_URL=발급받은_API_URL

# 선택 1: Google Cloud Vision
# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# 선택 2: OpenAI GPT-4 Vision (유료)
# OPENAI_API_KEY=your_openai_api_key_here
```

📖 **자세한 설정 가이드**: [NAVER_OCR_SETUP.md](NAVER_OCR_SETUP.md) 문서를 확인하세요!

## 🚀 실행 방법

### 방법 1: 웹 인터페이스 (Streamlit)
```bash
streamlit run app_streamlit.py
```

### 방법 2: 커맨드라인
```bash
python ocr_processor.py --image path/to/image.jpg
```

### 방법 3: FastAPI 서버
```bash
python app_fastapi.py
```
브라우저에서 `http://localhost:8000/docs` 접속

## 📱 모바일 앱 (선택사항)
React Native 앱은 `mobile/` 폴더 참조

## 📝 사용 예시

### Python 코드에서 직접 사용
```python
from ocr_processor import MarketOCRProcessor

processor = MarketOCRProcessor(method='gpt4_vision')
result = processor.process_image('market_photo.jpg')
print(result)
```

### 결과 예시
```json
{
  "products": [
    {
      "product_name": "계란 조개류",
      "price": "800원",
      "unit": "1개",
      "confidence": 0.95
    },
    {
      "product_name": "귤 오렌지 (한라봉)",
      "price": "5000원",
      "unit": "1봉",
      "confidence": 0.92
    }
  ],
  "total_items": 2,
  "timestamp": "2025-10-12T10:30:00"
}
```

## 💰 비용 안내 (OCR 엔진별)

| OCR 엔진 | 무료 제공량 | 비용 (초과 시) | 한글 인식 | 추천도 |
|---------|------------|---------------|----------|--------|
| **Naver Clova OCR** | 월 1,000건 | 건당 ~₩50 | ⭐⭐⭐⭐⭐ | ✅ 추천 |
| Google Cloud Vision | 월 1,000건 | 건당 $0.0015 | ⭐⭐⭐⭐ | 👍 좋음 |
| GPT-4 Vision | 없음 | 건당 $0.01~0.03 | ⭐⭐⭐⭐⭐ | 💰 유료 |

> **결론**: 한국 시장 가판대에는 **네이버 Clova OCR**이 가장 적합하고 경제적입니다!

## 🔧 문제 해결

### ❌ OpenAI API Quota 초과 에러
- **해결**: 네이버 Clova OCR로 전환 ([NAVER_OCR_SETUP.md](NAVER_OCR_SETUP.md) 참조)
- 월 1,000건 무료로 사용 가능

### 일반적인 문제
- **인식률이 낮을 때**: 이미지 품질을 높이거나 조명을 개선
- **API 에러**: API 키와 크레딧 잔액 확인
- **한글 인식 실패**: 네이버 Clova OCR 또는 GPT-4 Vision 사용 권장
- **설정 문제**: [NAVER_OCR_SETUP.md](NAVER_OCR_SETUP.md)의 "문제 해결" 섹션 참조

## 📞 지원
문제가 있으면 이슈를 등록해주세요.

