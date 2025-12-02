#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
초안전 OCR 프로세서 - ASCII 인코딩 문제 완전 회피
"""

import os
import base64
import json
import tempfile
import uuid
from typing import Dict

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv("sibangaiocr.env")

class UltraSafeOCR:
    """
    ASCII 인코딩 문제를 완전히 회피하는 OCR 프로세서
    """
    
    def __init__(self):
        """초기화"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        # OpenAI 클라이언트 생성
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
    
    def safe_encode_image(self, image_path: str) -> str:
        """
        완전히 안전한 이미지 인코딩
        """
        try:
            # 1단계: 안전한 임시 파일 생성
            safe_filename = f"safe_image_{uuid.uuid4().hex}.jpg"
            temp_dir = tempfile.gettempdir()
            safe_path = os.path.join(temp_dir, safe_filename)
            
            # 2단계: 원본 파일을 안전한 경로로 복사
            import shutil
            shutil.copy2(image_path, safe_path)
            
            # 3단계: 안전한 경로에서 이미지 읽기
            with open(safe_path, "rb") as f:
                image_data = f.read()
            
            # 4단계: Base64 인코딩 (ASCII 디코딩)
            encoded = base64.b64encode(image_data)
            result = encoded.decode('ascii')
            
            # 5단계: 임시 파일 정리
            try:
                os.unlink(safe_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            raise Exception(f"Image encoding failed: {str(e)}")
    
    def process_image(self, image_path: str) -> Dict:
        """
        이미지 OCR 처리 (완전 안전 버전)
        """
        try:
            # 이미지 인코딩
            base64_image = self.safe_encode_image(image_path)
            
            # 영어 프롬프트 (ASCII 전용)
            prompt = """Analyze this image and extract product information. 
            Return JSON format: {"products": [{"product_name": "name", "price": "price"}]}
            Focus on Korean text recognition."""
            
            # API 호출
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # 결과 처리
            result_text = response.choices[0].message.content
            
            # JSON 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            return {
                "success": True,
                "products": result.get("products", []),
                "raw_response": result_text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "OCR processing failed"
            }

# 테스트 함수
def test_ultra_safe_ocr():
    """초안전 OCR 테스트"""
    try:
        ocr = UltraSafeOCR()
        
        # 테스트 이미지 경로
        test_image = "/tmp/test_image.jpg"
        
        if os.path.exists(test_image):
            print(f"🚀 Ultra Safe OCR Test: {test_image}")
            result = ocr.process_image(test_image)
            
            if result["success"]:
                print("✅ Success!")
                print("Result:", json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("❌ Failed:", result["error"])
        else:
            print("❌ Test image not found")
            
    except Exception as e:
        print(f"❌ Initialization error: {e}")

if __name__ == "__main__":
    test_ultra_safe_ocr()











