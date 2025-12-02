#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 OCR 테스트 스크립트
ASCII 인코딩 문제를 우회하는 방법
"""

import os
import base64
import json
from openai import OpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv("sibangaiocr.env")

def simple_base64_encode(image_path):
    """
    가장 간단한 Base64 인코딩
    """
    with open(image_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode('ascii')

def test_ocr_simple(image_path):
    """
    간단한 OCR 테스트
    """
    try:
        # OpenAI 클라이언트
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 이미지 인코딩
        base64_image = simple_base64_encode(image_path)
        
        # 영어 프롬프트 (ASCII 전용)
        prompt = """Analyze this image and extract product information. 
        Return only a JSON object with this format:
        {"product_name": "name", "price": "price"}
        """
        
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
            max_tokens=1000
        )
        
        result = response.choices[0].message.content
        print("✅ OCR 성공!")
        print("결과:", result)
        return {"success": True, "result": result}
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # 테스트 이미지 경로 (실제 경로로 변경 필요)
    test_image = "test_image.jpg"
    
    if os.path.exists(test_image):
        print("🚀 간단한 OCR 테스트 시작...")
        result = test_ocr_simple(test_image)
    else:
        print("❌ 테스트 이미지를 찾을 수 없습니다.")
        print("이미지 파일을 'test_image.jpg'로 저장해주세요.")











