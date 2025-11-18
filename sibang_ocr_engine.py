"""
Sibang OCR 엔진 - 전통시장 특화 OCR
향후 개발 예정
"""

import os
from dotenv import load_dotenv

class SibangOCREngine:
    """
    Sibang OCR 엔진 - 전통시장 특화 텍스트 인식
    
    향후 개발 예정 기능:
    - 전통시장 가격표 특화 인식
    - 한글 필기체 최적화
    - 상품명 및 가격 자동 추출
    - 시장 특화 용어 사전
    """
    
    def __init__(self):
        """Sibang OCR 엔진 초기화"""
        load_dotenv("sibangaiocr.env")
        self.is_available = False  # 아직 개발 중
        self.version = "0.1.0-dev"
        
    def is_ready(self):
        """엔진 사용 가능 여부 확인"""
        return self.is_available
    
    def process_image(self, image_file):
        """
        이미지에서 텍스트 추출
        
        Args:
            image_file: 업로드된 이미지 파일
            
        Returns:
            str: 추출된 텍스트
            
        Raises:
            NotImplementedError: 아직 개발 중
        """
        raise NotImplementedError(
            "🏪 Sibang OCR은 아직 개발 중입니다.\n"
            "전통시장 특화 OCR 엔진으로 향후 개발 예정입니다."
        )
    
    def get_engine_info(self):
        """엔진 정보 반환"""
        return {
            "name": "Sibang OCR",
            "version": self.version,
            "description": "전통시장 특화 OCR 엔진",
            "status": "개발 예정",
            "features": [
                "전통시장 가격표 특화 인식",
                "한글 필기체 최적화", 
                "상품명 및 가격 자동 추출",
                "시장 특화 용어 사전"
            ]
        }

# 향후 개발을 위한 예시 구현
class SibangOCRProcessor:
    """Sibang OCR 프로세서 - 향후 개발 예정"""
    
    def __init__(self):
        self.engine = SibangOCREngine()
    
    def process_market_image(self, image_file):
        """
        전통시장 이미지 처리 (향후 구현)
        
        특화 기능:
        - 가격표 인식
        - 상품명 추출
        - 할인 정보 파싱
        """
        if not self.engine.is_ready():
            raise NotImplementedError("Sibang OCR은 아직 개발 중입니다.")
        
        # 향후 구현 예정
        pass

