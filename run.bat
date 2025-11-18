@echo off
chcp 65001 >nul
REM 시장 가판대 OCR 시스템 실행 스크립트 (Windows용)

echo ======================================================
echo 🏪 시장 가판대 OCR 시스템
echo ======================================================
echo.

REM 가상환경 확인
if not exist "venv" (
    echo ⚠️  가상환경이 없습니다. 생성하시겠습니까? (y/n)
    set /p response=
    if /i "%response%"=="y" (
        echo 🔧 가상환경 생성 중...
        python -m venv venv
        call venv\Scripts\activate.bat
        echo 📦 패키지 설치 중... (약 2-3분 소요)
        pip install --upgrade pip
        pip install -r requirements.txt
        echo ✅ 설치 완료!
    ) else (
        echo ❌ 가상환경이 필요합니다.
        pause
        exit /b 1
    )
) else (
    call venv\Scripts\activate.bat
)

REM .env 파일 확인
if not exist ".env" (
    echo ⚠️  .env 파일이 없습니다.
    echo env_template.txt를 .env로 복사하고 API 키를 입력하세요.
    echo.
    echo 간단한 설정을 도와드릴까요? (y/n)
    set /p response=
    if /i "%response%"=="y" (
        copy env_template.txt .env
        echo ✅ .env 파일 생성됨
        echo.
        echo .env 파일을 메모장으로 열어 API 키를 입력하세요.
        notepad .env
    ) else (
        echo 나중에 .env 파일을 수동으로 설정하세요.
    )
)

REM 메뉴 표시
echo.
echo ======================================================
echo 실행할 모드를 선택하세요:
echo ======================================================
echo 1. 🌐 웹 인터페이스 (Streamlit) - 가장 쉬움
echo 2. 🚀 API 서버 (FastAPI) - 개발자용
echo 3. 🧪 테스트 실행
echo 4. 📋 도움말
echo 5. ❌ 종료
echo.
set /p choice=선택 (1-5): 

if "%choice%"=="1" (
    echo.
    echo 🌐 Streamlit 웹 인터페이스 시작...
    echo 브라우저에서 http://localhost:8501 이 열립니다.
    echo 종료하려면 Ctrl+C를 누르세요.
    echo.
    streamlit run app_streamlit.py
) else if "%choice%"=="2" (
    echo.
    echo 🚀 FastAPI 서버 시작...
    echo API 문서: http://localhost:8000/docs
    echo 종료하려면 Ctrl+C를 누르세요.
    echo.
    python app_fastapi.py
) else if "%choice%"=="3" (
    echo.
    echo 🧪 테스트 실행 중...
    echo.
    python test_ocr.py
) else if "%choice%"=="4" (
    echo.
    echo 📋 도움말
    echo.
    echo 주요 명령어:
    echo   - 웹 실행: streamlit run app_streamlit.py
    echo   - API 실행: python app_fastapi.py
    echo   - 테스트: python test_ocr.py
    echo   - OCR 처리: python ocr_processor.py --image 이미지.jpg
    echo.
    echo 문서:
    echo   - README.md - 전체 설명
    echo   - QUICK_START.md - 빠른 시작
    echo   - TECHNICAL_DETAILS.md - 기술 상세
    echo   - mobile_guide.md - 모바일 앱
    echo.
    pause
) else if "%choice%"=="5" (
    echo.
    echo 👋 종료합니다.
    exit /b 0
) else (
    echo.
    echo ❌ 잘못된 선택입니다.
    pause
    exit /b 1
)

echo.
echo ======================================================
echo 작업 완료!
echo ======================================================
pause

