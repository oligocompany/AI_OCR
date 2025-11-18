"""
간단한 OCR 프로세서 - ASCII 인코딩 문제 우회
"""

import os
import base64
import json
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("sibangaiocr.env")

class SimpleOCRProcessor:
    """
    ASCII 인코딩 문제를 우회하는 간단한 OCR 프로세서
    """
    
    def __init__(self):
        """초기화"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def encode_image_safe(self, image_path: str) -> str:
        """
        안전한 이미지 인코딩 (ASCII 전용)
        """
        try:
            # 바이너리 모드로 읽기
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Base64 인코딩 후 ASCII 디코딩
            encoded = base64.b64encode(image_data)
            return encoded.decode('ascii')
            
        except Exception as e:
            raise Exception(f"이미지 인코딩 실패: {str(e)}")
    
    def process_image(self, image_path: str) -> Dict:
        """
        이미지 OCR 처리
        """
        try:
            # 이미지 인코딩
            base64_image = self.encode_image_safe(image_path)
            
            # 영어 프롬프트 (ASCII 전용)
            prompt = (
                "Analyze this image of a market stall product and extract information. "
                "Return JSON format: "
                '{"products": [{"product_name": "name", "price": "price", "unit": "unit"}]}'
            )
            
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
            
            # 결과 파싱
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
                "message": "OCR 처리 중 오류가 발생했습니다."
            }

# 테스트 함수
def test_ocr():
    """OCR 테스트"""
    try:
        processor = SimpleOCRProcessor()
        
        # 테스트 이미지 경로 (실제 경로로 변경)
        image_path = "sample_image.jpg"
        
        if os.path.exists(image_path):
            print(f"🚀 OCR 테스트 시작: {image_path}")
            result = processor.process_image(image_path)
            
            if result["success"]:
                print("✅ OCR 성공!")
                print("결과:", json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("❌ OCR 실패:", result["error"])
        else:
            print("❌ 테스트 이미지를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 초기화 오류: {e}")

if __name__ == "__main__":
    test_ocr()








