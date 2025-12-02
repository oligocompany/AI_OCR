# 🚀 시작 명령어

## 웹 인터페이스 실행 (가장 쉬움)

터미널에서 다음 명령어를 입력하세요:

```bash
python3 -m streamlit run app_streamlit.py
```

### 📍 접속 주소
브라우저에서 자동으로 열리거나, 다음 주소로 접속:
- **http://localhost:8501**
- 또는 **http://127.0.0.1:8501**

### 🛑 종료 방법
터미널에서 **Ctrl + C** 누르기

---

## 🔑 중요: API 키 설정 (처음 한 번만)

웹에서 OCR을 실행하려면 API 키가 필요합니다.

### 1. `.env` 파일 생성
```bash
cp env_template.txt .env
```

### 2. API 키 입력
`.env` 파일을 열어서 OpenAI API 키를 입력:
```bash
OPENAI_API_KEY=sk-여기에-실제-키-입력
```

### 3. API 키 받는 방법
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. 생성된 키 복사 (sk-로 시작)
4. `.env` 파일에 붙여넣기

---

## 📱 다른 실행 방법

### API 서버 (개발자용)
```bash
python3 app_fastapi.py
```
접속: http://localhost:8000/docs

### 테스트 실행
```bash
python3 test_ocr.py
```

### 커맨드라인 OCR
```bash
python3 ocr_processor.py --image 이미지.jpg
```

---

## ⏱️ 예상 소요 시간
- 웹 실행: 5초
- OCR 처리: 5-10초 (이미지당)

---

## 💡 사용 방법
1. 웹 인터페이스 실행 ✅
2. 브라우저에서 http://localhost:8501 열기
3. 시장 가판대 사진 업로드
4. OCR 방법 선택 (GPT-4 Vision 추천)
5. "🚀 OCR 시작" 버튼 클릭
6. 결과 확인 및 JSON 다운로드

---

**문제가 있으면 QUICK_START.md를 참고하세요!** 📚












