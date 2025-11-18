"""
Sibang OCR 프로토타입 - 즉시 시작 가능한 버전
TrOCR 기반 전통시장 특화 OCR 엔진
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import json
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

class SibangOCRPrototype:
    """
    Sibang OCR 프로토타입
    TrOCR 기반 전통시장 특화 OCR 엔진
    """
    
    def __init__(self):
        """프로토타입 초기화"""
        load_dotenv("sibangaiocr.env")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.processor = None
        
        # 전통시장 특화 설정
        self.market_keywords = self._load_market_keywords()
        self.price_patterns = self._load_price_patterns()
        
        # 모델 로드
        self._load_model()
    
    def _load_market_keywords(self) -> List[str]:
        """전통시장 특화 키워드 로드"""
        return [
            # 과일류
            "사과", "배", "포도", "딸기", "바나나", "오렌지", "귤", "레몬", "복숭아", "자두",
            "수박", "참외", "멜론", "키위", "파인애플", "망고", "체리", "살구", "감", "대추",
            "하우스귤", "송이포도", "무농약", "유기농",
            
            # 채소류
            "배추", "무", "당근", "양파", "마늘", "생강", "고추", "피망", "토마토", "오이",
            "가지", "호박", "시금치", "상추", "깻잎", "미나리", "쑥갓", "부추", "파", "대파",
            
            # 곡물류
            "쌀", "보리", "밀", "옥수수", "콩", "팥", "녹두", "참깨", "들깨", "땅콩",
            
            # 해산물
            "생선", "고등어", "삼치", "꽁치", "멸치", "새우", "게", "문어", "오징어", "낙지",
            "전복", "소라", "홍합", "굴", "바지락", "조개", "해삼", "멍게", "성게",
            
            # 육류
            "소고기", "돼지고기", "닭고기", "오리고기", "양고기", "햄", "소시지", "베이컨",
            
            # 기타 식품
            "두부", "순두부", "콩나물", "숙주", "버섯", "표고버섯", "팽이버섯", "느타리버섯",
            
            # 특수 상품
            "옻나무", "국산", "제주", "고척근린시장",
            
            # 단위 및 가격 관련
            "원", "개", "봉", "포기", "단", "kg", "g", "근", "말", "되", "가마",
            "할인", "특가", "세일", "무료", "공짜", "증정", "사은품"
        ]
    
    def _load_price_patterns(self) -> List[str]:
        """가격 패턴 로드"""
        return [
            r'\d{1,3}(?:,\d{3})*\s*원',  # 1,000원, 500원 등
            r'\d+\s*원',                  # 1000원, 500원 등
            r'\d{1,2}\s*만\s*원',         # 1만원, 5만원 등
            r'\d+\s*천\s*원',             # 1000원, 5000원 등
            r'\d+\s*/\s*kg',              # 1000/kg 등
            r'\d+\s*/\s*개',              # 1000/개 등
        ]
    
    def _load_model(self):
        """TrOCR 모델 로드"""
        try:
            print("🔄 TrOCR 모델 로딩 중...")
            
            # TrOCR 모델 로드 (한국어 지원 버전)
            model_name = "microsoft/trocr-base-printed"
            self.processor = TrOCRProcessor.from_pretrained(model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
            self.model.to(self.device)
            
            print("✅ TrOCR 모델 로드 완료")
            
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            print("💡 인터넷 연결을 확인하고 다시 시도해주세요.")
            self.model = None
            self.processor = None
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        이미지 전처리 - 전통시장 특화
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            전처리된 이미지 배열
        """
        # 이미지 읽기
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"이미지를 불러올 수 없습니다: {image_path}")
        
        # 1. 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. 노이즈 제거 (가우시안 블러)
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 3. 대비 향상 (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 4. 적응적 임계값 처리
        binary = cv2.adaptiveThreshold(
            enhanced, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # 5. 모폴로지 연산으로 노이즈 제거
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 6. 텍스트 영역 강조 (반전)
        inverted = cv2.bitwise_not(cleaned)
        
        return inverted
    
    def recognize_text(self, image: np.ndarray) -> str:
        """
        TrOCR을 사용한 텍스트 인식
        
        Args:
            image: 이미지 배열
            
        Returns:
            인식된 텍스트
        """
        if self.model is None or self.processor is None:
            return "모델이 로드되지 않았습니다."
        
        try:
            # PIL Image로 변환
            pil_image = Image.fromarray(image)
            
            # TrOCR 처리
            pixel_values = self.processor(pil_image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)
            
            # 텍스트 생성
            generated_ids = self.model.generate(pixel_values)
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return generated_text.strip()
            
        except Exception as e:
            print(f"TrOCR 인식 오류: {e}")
            return ""
    
    def extract_market_info(self, text: str) -> Dict[str, str]:
        """
        전통시장 정보 추출
        
        Args:
            text: 인식된 텍스트
            
        Returns:
            구조화된 정보 딕셔너리
        """
        result = {
            "raw_text": text,
            "product_name": "",
            "price": "",
            "unit": "",
            "origin": "",
            "additional_info": ""
        }
        
        # 가격 패턴 매칭
        for pattern in self.price_patterns:
            price_match = re.search(pattern, text)
            if price_match:
                result["price"] = price_match.group(0)
                break
        
        # 상품명 추출 (키워드 매칭)
        for keyword in self.market_keywords:
            if keyword in text:
                result["product_name"] = keyword
                break
        
        # 가격 앞부분을 상품명으로 추정
        if result["price"] and not result["product_name"]:
            price_start = text.find(result["price"])
            product_part = text[:price_start].strip()
            result["product_name"] = product_part
        
        # 원산지 정보 추출
        origin_keywords = ["국산", "제주", "제주도", "무농약", "유기농", "하우스"]
        for keyword in origin_keywords:
            if keyword in text:
                result["origin"] = keyword
                break
        
        # 단위 정보 추출
        unit_patterns = [r'(\d+)\s*개', r'(\d+)\s*kg', r'(\d+)\s*근', r'(\d+)\s*봉', r'(\d+)\s*포기']
        for pattern in unit_patterns:
            unit_match = re.search(pattern, text)
            if unit_match:
                result["unit"] = unit_match.group(0)
                break
        
        return result
    
    def process_image(self, image_path: str) -> Dict:
        """
        이미지 처리 메인 함수
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            인식 결과 딕셔너리
        """
        try:
            print(f"🔄 이미지 처리 중: {image_path}")
            
            # 1. 이미지 전처리
            processed_image = self.preprocess_image(image_path)
            
            # 2. 텍스트 인식
            recognized_text = self.recognize_text(processed_image)
            
            if not recognized_text:
                return {
                    "success": False,
                    "error": "텍스트를 인식할 수 없습니다.",
                    "engine": "Sibang OCR Prototype"
                }
            
            # 3. 전통시장 정보 추출
            market_info = self.extract_market_info(recognized_text)
            
            return {
                "success": True,
                "engine": "Sibang OCR Prototype",
                "text": recognized_text,
                "market_info": market_info,
                "confidence": 0.8  # 프로토타입이므로 고정값
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "engine": "Sibang OCR Prototype"
            }

# Flask 애플리케이션에 통합하기 위한 함수
def integrate_with_flask():
    """
    Flask 애플리케이션에 Sibang OCR 통합
    """
    # simple_web_ocr.py의 Sibang OCR 부분을 이 함수로 교체
    pass

# 테스트 함수
def test_sibang_ocr():
    """Sibang OCR 프로토타입 테스트"""
    print("🏪 Sibang OCR 프로토타입 테스트 시작")
    print("=" * 50)
    
    # 프로토타입 생성
    ocr = SibangOCRPrototype()
    
    # 테스트 이미지 경로들
    test_images = [
        "sample_images/test_market_1.jpg",
        "sample_images/test_market_2.jpg", 
        "sample_images/test_market_3.jpg"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n📷 테스트 이미지: {image_path}")
            result = ocr.process_image(image_path)
            
            if result["success"]:
                print("✅ OCR 성공!")
                print(f"📝 인식된 텍스트: {result['text']}")
                print(f"🏪 상품명: {result['market_info']['product_name']}")
                print(f"💰 가격: {result['market_info']['price']}")
                print(f"📍 원산지: {result['market_info']['origin']}")
            else:
                print(f"❌ OCR 실패: {result['error']}")
        else:
            print(f"⚠️ 테스트 이미지를 찾을 수 없습니다: {image_path}")
    
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    test_sibang_ocr()







