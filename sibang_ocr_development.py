"""
Sibang OCR 엔진 개발 가이드
전통시장 특화 OCR 엔진 개발을 위한 단계별 구현 계획
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pytesseract
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import json
import re
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

class SibangOCREngine:
    """
    Sibang OCR 엔진 - 전통시장 특화 OCR
    
    개발 단계:
    1. 데이터 수집 및 전처리
    2. 모델 아키텍처 설계
    3. 학습 및 검증
    4. 배포 및 최적화
    """
    
    def __init__(self):
        """Sibang OCR 엔진 초기화"""
        load_dotenv("sibangaiocr.env")
        self.is_available = False
        self.version = "0.1.0-dev"
        
        # 모델 관련 속성들
        self.model = None
        self.processor = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 전통시장 특화 설정
        self.market_keywords = self._load_market_keywords()
        self.price_patterns = self._load_price_patterns()
        
    def _load_market_keywords(self) -> List[str]:
        """전통시장 특화 키워드 로드"""
        return [
            # 과일류
            "사과", "배", "포도", "딸기", "바나나", "오렌지", "귤", "레몬", "복숭아", "자두",
            "수박", "참외", "멜론", "키위", "파인애플", "망고", "체리", "살구", "감", "대추",
            
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

class SibangDataset(Dataset):
    """
    Sibang OCR용 데이터셋 클래스
    전통시장 이미지와 텍스트 쌍을 관리
    """
    
    def __init__(self, image_paths: List[str], labels: List[str], transform=None):
        """
        데이터셋 초기화
        
        Args:
            image_paths: 이미지 파일 경로 리스트
            labels: 해당하는 텍스트 라벨 리스트
            transform: 이미지 변환 함수
        """
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # 이미지 로드
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        
        # 변환 적용
        if self.transform:
            image = self.transform(image)
        
        # 라벨
        label = self.labels[idx]
        
        return image, label

class SibangOCRProcessor:
    """
    Sibang OCR 프로세서 - 실제 구현
    """
    
    def __init__(self):
        self.engine = SibangOCREngine()
        self._initialize_models()
    
    def _initialize_models(self):
        """모델 초기화"""
        try:
            # TrOCR 모델 로드 (Microsoft의 Vision-Language 모델)
            model_name = "microsoft/trocr-base-printed"
            self.processor = TrOCRProcessor.from_pretrained(model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
            self.model.to(self.engine.device)
            
            print("✅ TrOCR 모델 로드 완료")
            
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
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
        
        # 6. 텍스트 영역 강조
        # 텍스트는 일반적으로 어두운 색이므로 반전
        inverted = cv2.bitwise_not(cleaned)
        
        return inverted
    
    def extract_text_regions(self, image: np.ndarray) -> List[np.ndarray]:
        """
        텍스트 영역 추출
        
        Args:
            image: 전처리된 이미지
            
        Returns:
            텍스트 영역 리스트
        """
        # 윤곽선 찾기
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        
        for contour in contours:
            # 경계 상자 계산
            x, y, w, h = cv2.boundingRect(contour)
            
            # 너무 작은 영역 제외
            if w < 20 or h < 10:
                continue
            
            # 텍스트 영역 추출
            text_region = image[y:y+h, x:x+w]
            text_regions.append(text_region)
        
        return text_regions
    
    def recognize_with_trocr(self, image: np.ndarray) -> str:
        """
        TrOCR을 사용한 텍스트 인식
        
        Args:
            image: 이미지 배열
            
        Returns:
            인식된 텍스트
        """
        if self.model is None or self.processor is None:
            return ""
        
        try:
            # PIL Image로 변환
            pil_image = Image.fromarray(image)
            
            # TrOCR 처리
            pixel_values = self.processor(pil_image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.engine.device)
            
            # 텍스트 생성
            generated_ids = self.model.generate(pixel_values)
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return generated_text.strip()
            
        except Exception as e:
            print(f"TrOCR 인식 오류: {e}")
            return ""
    
    def recognize_with_tesseract(self, image: np.ndarray) -> str:
        """
        Tesseract를 사용한 텍스트 인식 (백업)
        
        Args:
            image: 이미지 배열
            
        Returns:
            인식된 텍스트
        """
        try:
            # PIL Image로 변환
            pil_image = Image.fromarray(image)
            
            # Tesseract 설정 (한국어 최적화)
            config = r'--oem 3 --psm 6 -l kor+eng'
            text = pytesseract.image_to_string(pil_image, config=config)
            
            return text.strip()
            
        except Exception as e:
            print(f"Tesseract 인식 오류: {e}")
            return ""
    
    def post_process_text(self, text: str) -> Dict[str, str]:
        """
        텍스트 후처리 - 전통시장 특화
        
        Args:
            text: 원본 텍스트
            
        Returns:
            구조화된 정보 딕셔너리
        """
        result = {
            "raw_text": text,
            "product_name": "",
            "price": "",
            "unit": "",
            "additional_info": ""
        }
        
        # 가격 패턴 매칭
        for pattern in self.engine.price_patterns:
            price_match = re.search(pattern, text)
            if price_match:
                result["price"] = price_match.group(0)
                break
        
        # 상품명 추출 (가격 앞부분)
        if result["price"]:
            price_start = text.find(result["price"])
            product_part = text[:price_start].strip()
            result["product_name"] = product_part
        
        # 키워드 매칭으로 상품명 보완
        for keyword in self.engine.market_keywords:
            if keyword in text and not result["product_name"]:
                result["product_name"] = keyword
                break
        
        # 단위 정보 추출
        unit_patterns = [r'(\d+)\s*개', r'(\d+)\s*kg', r'(\d+)\s*근', r'(\d+)\s*봉']
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
            # 1. 이미지 전처리
            processed_image = self.preprocess_image(image_path)
            
            # 2. 텍스트 영역 추출
            text_regions = self.extract_text_regions(processed_image)
            
            # 3. 각 영역별 텍스트 인식
            all_texts = []
            for region in text_regions:
                # TrOCR 시도
                trocr_text = self.recognize_with_trocr(region)
                if trocr_text:
                    all_texts.append(trocr_text)
                else:
                    # Tesseract 백업
                    tesseract_text = self.recognize_with_tesseract(region)
                    if tesseract_text:
                        all_texts.append(tesseract_text)
            
            # 4. 전체 텍스트 결합
            full_text = " ".join(all_texts)
            
            # 5. 후처리
            structured_result = self.post_process_text(full_text)
            
            return {
                "success": True,
                "engine": "Sibang OCR",
                "text": full_text,
                "structured": structured_result,
                "regions_count": len(text_regions)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "engine": "Sibang OCR"
            }

# 데이터 수집 및 학습을 위한 유틸리티 클래스
class SibangDataCollector:
    """
    Sibang OCR용 데이터 수집 도구
    """
    
    def __init__(self):
        self.collected_data = []
    
    def collect_from_web(self, search_terms: List[str], max_images: int = 100):
        """
        웹에서 전통시장 이미지 수집
        
        Args:
            search_terms: 검색어 리스트
            max_images: 최대 수집 이미지 수
        """
        # 실제 구현에서는 Selenium, BeautifulSoup 등을 사용
        print(f"🔍 웹에서 전통시장 이미지 수집 중... (최대 {max_images}개)")
        print(f"검색어: {', '.join(search_terms)}")
        
        # TODO: 실제 웹 스크래핑 구현
        pass
    
    def create_synthetic_data(self, base_images: List[str], text_overlays: List[str]):
        """
        합성 데이터 생성
        
        Args:
            base_images: 기본 이미지 리스트
            text_overlays: 오버레이할 텍스트 리스트
        """
        print("🎨 합성 데이터 생성 중...")
        
        # TODO: 이미지에 텍스트 오버레이 구현
        pass
    
    def validate_data(self, image_path: str, expected_text: str) -> bool:
        """
        데이터 검증
        
        Args:
            image_path: 이미지 경로
            expected_text: 예상 텍스트
            
        Returns:
            검증 결과
        """
        # TODO: 데이터 품질 검증 구현
        return True

# 학습을 위한 유틸리티 클래스
class SibangTrainer:
    """
    Sibang OCR 모델 학습 도구
    """
    
    def __init__(self):
        self.model = None
        self.optimizer = None
        self.criterion = None
    
    def prepare_dataset(self, data_dir: str) -> Tuple[DataLoader, DataLoader]:
        """
        데이터셋 준비
        
        Args:
            data_dir: 데이터 디렉토리
            
        Returns:
            학습용, 검증용 DataLoader
        """
        # TODO: 데이터셋 로더 구현
        pass
    
    def train_model(self, train_loader: DataLoader, val_loader: DataLoader, epochs: int = 10):
        """
        모델 학습
        
        Args:
            train_loader: 학습용 데이터 로더
            val_loader: 검증용 데이터 로더
            epochs: 학습 에포크 수
        """
        print(f"🚀 모델 학습 시작 (에포크: {epochs})")
        
        # TODO: 실제 학습 루프 구현
        pass
    
    def save_model(self, model_path: str):
        """
        모델 저장
        
        Args:
            model_path: 저장할 모델 경로
        """
        # TODO: 모델 저장 구현
        pass

# 사용 예시
if __name__ == "__main__":
    # Sibang OCR 프로세서 생성
    processor = SibangOCRProcessor()
    
    # 테스트 이미지 처리
    test_image = "sample_images/test_market.jpg"
    if os.path.exists(test_image):
        result = processor.process_image(test_image)
        print("📊 Sibang OCR 결과:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("❌ 테스트 이미지를 찾을 수 없습니다.")
        print("💡 sample_images/test_market.jpg 파일을 준비해주세요.")










