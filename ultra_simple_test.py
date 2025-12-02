#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
초간단 OCR 테스트 - 모든 복잡한 부분 제거
"""

import os
import base64
import json

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv("sibangaiocr.env")

def ultra_simple_ocr():
    """
    초간단 OCR 테스트 - ASCII 문제 완전 회피
    """
    try:
        # OpenAI 클라이언트 생성
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 테스트 이미지 경로 (실제 이미지로 변경 필요)
        image_path = "/tmp/test_image.jpg"
        
        # 이미지가 없으면 메시지 출력
        if not os.path.exists(image_path):
            print("❌ 테스트 이미지를 /tmp/test_image.jpg에 저장해주세요")
            return
        
        # 이미지를 바이너리로 읽기
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Base64 인코딩 (ASCII 디코딩)
        base64_image = base64.b64encode(image_data).decode('ascii')
        
        # 초간단 영어 프롬프트
        prompt = "Extract text from this image. Return JSON: {\"text\": \"extracted text\"}"
        
        # API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        print("✅ 성공!")
        print("결과:", result)
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        print(f"오류 타입: {type(e)}")

if __name__ == "__main__":
    print("🚀 초간단 OCR 테스트 시작...")
    ultra_simple_ocr()











