#!/bin/bash
# 시장 가판대 OCR 시스템 재시작 스크립트

echo "🔄 Streamlit 앱을 재시작합니다..."

# 기존 프로세스 중지
pkill -f streamlit
sleep 2

# 앱 재시작
echo "🚀 앱을 시작합니다..."
python3 -m streamlit run app_streamlit.py
