#!/bin/bash

# 시장 가판대 OCR 시스템 실행 스크립트
# Mac/Linux용

echo "======================================================"
echo "🏪 시장 가판대 OCR 시스템"
echo "======================================================"
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  가상환경이 없습니다. 생성하시겠습니까? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${BLUE}🔧 가상환경 생성 중...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        echo -e "${BLUE}📦 패키지 설치 중... (약 2-3분 소요)${NC}"
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ 설치 완료!${NC}"
    else
        echo -e "${RED}❌ 가상환경이 필요합니다.${NC}"
        exit 1
    fi
else
    source venv/bin/activate
fi

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다.${NC}"
    echo -e "${BLUE}env_template.txt를 .env로 복사하고 API 키를 입력하세요.${NC}"
    echo ""
    echo "간단한 설정을 도와드릴까요? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cp env_template.txt .env
        echo -e "${GREEN}✅ .env 파일 생성됨${NC}"
        echo ""
        echo "OpenAI API 키를 입력하세요 (Enter로 건너뛰기):"
        read -r openai_key
        if [ ! -z "$openai_key" ]; then
            sed -i "" "s/sk-your-api-key-here/$openai_key/" .env
            echo -e "${GREEN}✅ OpenAI API 키 저장됨${NC}"
        fi
    else
        echo -e "${YELLOW}나중에 .env 파일을 수동으로 설정하세요.${NC}"
    fi
fi

# 메뉴 표시
echo ""
echo "======================================================"
echo "실행할 모드를 선택하세요:"
echo "======================================================"
echo "1. 🌐 웹 인터페이스 (Streamlit) - 가장 쉬움"
echo "2. 🚀 API 서버 (FastAPI) - 개발자용"
echo "3. 🧪 테스트 실행"
echo "4. 📋 도움말"
echo "5. ❌ 종료"
echo ""
echo -n "선택 (1-5): "
read -r choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}🌐 Streamlit 웹 인터페이스 시작...${NC}"
        echo -e "${GREEN}브라우저에서 http://localhost:8501 이 열립니다.${NC}"
        echo -e "${YELLOW}종료하려면 Ctrl+C를 누르세요.${NC}"
        echo ""
        streamlit run app_streamlit.py
        ;;
    2)
        echo ""
        echo -e "${BLUE}🚀 FastAPI 서버 시작...${NC}"
        echo -e "${GREEN}API 문서: http://localhost:8000/docs${NC}"
        echo -e "${YELLOW}종료하려면 Ctrl+C를 누르세요.${NC}"
        echo ""
        python app_fastapi.py
        ;;
    3)
        echo ""
        echo -e "${BLUE}🧪 테스트 실행 중...${NC}"
        echo ""
        python test_ocr.py
        ;;
    4)
        echo ""
        echo -e "${BLUE}📋 도움말${NC}"
        echo ""
        echo "주요 명령어:"
        echo "  - 웹 실행: streamlit run app_streamlit.py"
        echo "  - API 실행: python app_fastapi.py"
        echo "  - 테스트: python test_ocr.py"
        echo "  - OCR 처리: python ocr_processor.py --image 이미지.jpg"
        echo ""
        echo "문서:"
        echo "  - README.md - 전체 설명"
        echo "  - QUICK_START.md - 빠른 시작"
        echo "  - TECHNICAL_DETAILS.md - 기술 상세"
        echo "  - mobile_guide.md - 모바일 앱"
        echo ""
        ;;
    5)
        echo ""
        echo -e "${GREEN}👋 종료합니다.${NC}"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

echo ""
echo "======================================================"
echo -e "${GREEN}작업 완료!${NC}"
echo "======================================================"

