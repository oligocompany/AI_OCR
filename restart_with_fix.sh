#!/bin/bash
# 최종 해결책 적용 및 재실행 스크립트

echo "🔄 ASCII 인코딩 문제 최종 해결 중..."

# 기존 프로세스 중지
pkill -f streamlit
sleep 3

# 환경변수 설정
export PYTHONIOENCODING=utf-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

echo "🚀 앱을 재시작합니다..."
python3 -m streamlit run app_streamlit.py











