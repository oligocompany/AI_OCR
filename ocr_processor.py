"""
시장 가판대 OCR 프로세서
이미지에서 상품명과 가격을 인식하여 JSON으로 변환
"""

import os
import json
import base64
from typing import Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv("sibangaiocr.env")  # sibangaiocr.env 파일에서 환경변수 로드

# 이미지 처리 라이브러리
from PIL import Image
import cv2
import numpy as np


class MarketOCRProcessor:
    """
    시장 가판대 상품 정보 OCR 처리 클래스
    여러 OCR 엔진을 지원합니다.
    """
    
    def __init__(self, method: str = "gpt4_vision"):
        """
        초기화 함수
        
        Args:
            method: OCR 방법 선택
                - "gpt4_vision": OpenAI GPT-4 Vision (추천, 가장 정확)
                - "google_vision": Google Cloud Vision API
                - "naver_clova": Naver Clova OCR
                - "pp_ocrv5": PaddleOCR PP-OCRv5 (한국어 특화, 로컬 실행)
        """
        self.method = method
        self.api_key = None
        self.pp_ocr_ocr = None  # PP-OCRv5 OCR 객체 (지연 로딩)
        
        # 선택한 방법에 따라 API 키 확인
        if method == "gpt4_vision":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        
        elif method == "google_vision":
            self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not self.credentials_path:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS가 설정되지 않았습니다.")
        
        elif method == "naver_clova":
            self.naver_secret = os.getenv("NAVER_OCR_SECRET_KEY")
            self.naver_url = os.getenv("NAVER_OCR_API_URL")
            if not self.naver_secret or not self.naver_url:
                raise ValueError("Naver Clova OCR 설정이 완료되지 않았습니다.")
        
        elif method == "pp_ocrv5":
            # PP-OCRv5는 지연 로딩 (처음 사용할 때 모델 로드)
            # 모델 경로 설정 (선택사항, 기본값은 자동 다운로드)
            self.pp_ocrv5_model_path = os.getenv("PP_OCRV5_MODEL_PATH", None)
            # 한국어 모델 사용 여부 설정
            self.pp_ocrv5_use_korean = os.getenv("PP_OCRV5_USE_KOREAN", "True").lower() == "true"
    
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        이미지 전처리 - 인식률 향상을 위한 이미지 품질 개선
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            전처리된 이미지 (numpy array)
        """
        # 이미지 읽기
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"이미지를 불러올 수 없습니다: {image_path}")
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 노이즈 제거 (가우시안 블러)
        denoised = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 대비 향상 (CLAHE - Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 이진화 (Adaptive Thresholding)
        binary = cv2.adaptiveThreshold(
            enhanced, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary
    
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        이미지를 Base64로 인코딩 (API 전송용)
        한글 경로 및 인코딩 문제 완전 해결
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            Base64 인코딩된 문자열
        """
        import tempfile
        import shutil
        
        # 항상 임시 파일을 사용하여 안전하게 처리
        temp_fd = None
        temp_path = None
        
        try:
            # 안전한 임시 파일 생성
            temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            os.close(temp_fd)  # 파일 디스크립터 즉시 닫기
            
            # 원본 파일을 임시 파일로 복사
            shutil.copy2(image_path, temp_path)
            
            # 임시 파일에서 바이너리 데이터 읽기
            with open(temp_path, "rb") as temp_file:
                image_data = temp_file.read()
            
            # Base64 인코딩 (ASCII로 안전하게 디코딩)
            base64_encoded = base64.b64encode(image_data).decode('ascii')
            return base64_encoded
            
        except Exception as e:
            # 오류 발생 시 더 자세한 정보 제공
            error_msg = f"이미지 인코딩 실패: {str(e)}"
            if temp_path and os.path.exists(temp_path):
                error_msg += f" (임시 파일: {temp_path})"
            raise Exception(error_msg)
            
        finally:
            # 임시 파일 정리
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
    
    
    def process_with_gpt4_vision(self, image_path: str) -> Dict:
        """
        GPT-4 Vision API를 사용한 OCR 처리
        가장 정확하고 사용하기 쉬운 방법
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            인식된 상품 정보 딕셔너리
        """
        from openai import OpenAI
        
        try:
            # OpenAI 클라이언트 초기화
            client = OpenAI(api_key=self.api_key)
            
            # 이미지를 Base64로 인코딩 (안전한 방식)
            base64_image = self.encode_image_to_base64(image_path)
            
            # GPT-4 Vision에게 프롬프트 전송 (ASCII 전용으로 변경)
            prompt = """
This image shows products and price tags from a market stall.
Please identify all product names and prices from the image and organize them in JSON format.

Output format:
{
  "products": [
    {
      "product_name": "Product name in Korean",
      "price": "Price with won currency",
      "unit": "Unit (e.g., 1 piece, 1 basket, 1kg, etc.)",
      "additional_info": "Additional information if available"
    }
  ]
}

- Recognize Korean handwriting as accurately as possible
- Include won currency unit in the price
- Extract unit information if available
- Recognize all price tags without missing any
"""
            
            # API 호출
            response = client.chat.completions.create(
                model="gpt-4o",  # 또는 "gpt-4-vision-preview"
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
            
            # 응답에서 JSON 추출
            result_text = response.choices[0].message.content
            
            # JSON 파싱 (코드 블록 제거)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            # 메타데이터 추가
            result["metadata"] = {
                "method": "gpt4_vision",
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "total_items": len(result.get("products", []))
            }
            
            return result
            
        except UnicodeDecodeError as e:
            return {
                "error": f"인코딩 오류: {str(e)}",
                "message": "파일 인코딩 문제가 발생했습니다. 파일명에 한글이 포함되어 있을 수 있습니다.",
                "solution": "파일명을 영문으로 변경하거나 다른 이미지를 시도해보세요."
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": "GPT-4 Vision 처리 중 오류가 발생했습니다."
            }
    
    
    def process_with_google_vision(self, image_path: str) -> Dict:
        """
        Google Cloud Vision API를 사용한 OCR 처리
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            인식된 상품 정보 딕셔너리
        """
        from google.cloud import vision
        
        # Vision API 클라이언트 초기화
        client = vision.ImageAnnotatorClient()
        
        try:
            # 이미지 읽기
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # 텍스트 감지 수행
            response = client.text_detection(image=image)
            texts = response.text_annotations
            
            if not texts:
                return {
                    "products": [],
                    "message": "텍스트를 찾을 수 없습니다."
                }
            
            # 전체 텍스트 추출
            full_text = texts[0].description
            
            # 텍스트를 분석하여 상품 정보 파싱
            products = self._parse_text_to_products(full_text)
            
            result = {
                "products": products,
                "raw_text": full_text,
                "metadata": {
                    "method": "google_vision",
                    "timestamp": datetime.now().isoformat(),
                    "image_path": image_path,
                    "total_items": len(products)
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "message": "Google Vision 처리 중 오류가 발생했습니다."
            }
    
    
    def process_with_naver_clova(self, image_path: str) -> Dict:
        """
        Naver Clova OCR을 사용한 처리
        한국어에 특화된 OCR
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            인식된 상품 정보 딕셔너리
        """
        import requests
        
        try:
            # API 요청 준비
            url = self.naver_url
            headers = {
                'X-OCR-SECRET': self.naver_secret,
                'Content-Type': 'application/json'
            }
            
            # 이미지를 Base64로 인코딩
            base64_image = self.encode_image_to_base64(image_path)
            
            # 안전한 파일명 처리 (한글 경로 대응)
            try:
                file_name = Path(image_path).name
                file_format = Path(image_path).suffix[1:] or 'jpg'
            except:
                file_name = 'image.jpg'
                file_format = 'jpg'
            
            data = {
                'version': 'V2',
                'requestId': f'market_ocr_{datetime.now().timestamp()}',
                'timestamp': int(datetime.now().timestamp() * 1000),
                'images': [
                    {
                        'format': file_format,
                        'name': file_name,
                        'data': base64_image
                    }
                ]
            }
            
            # API 호출
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result_data = response.json()
            
            # 텍스트 추출
            full_text = ""
            for image in result_data.get('images', []):
                for field in image.get('fields', []):
                    full_text += field.get('inferText', '') + "\n"
            
            # 상품 정보 파싱
            products = self._parse_text_to_products(full_text)
            
            result = {
                "products": products,
                "raw_text": full_text,
                "metadata": {
                    "method": "naver_clova",
                    "timestamp": datetime.now().isoformat(),
                    "image_path": image_path,
                    "total_items": len(products)
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "message": "Naver Clova OCR 처리 중 오류가 발생했습니다."
            }
    
    def process_with_naver_clova_from_data(self, image_data: bytes) -> Dict:
        """
        Naver Clova OCR을 사용한 처리 (이미지 데이터 직접 전달)
        한국어에 특화된 OCR
        
        Args:
            image_data: 이미지 바이트 데이터
            
        Returns:
            인식된 텍스트 정보 딕셔너리
        """
        import requests
        
        try:
            # API 요청 준비
            url = self.naver_url
            headers = {
                'X-OCR-SECRET': self.naver_secret,
                'Content-Type': 'application/json'
            }
            
            # 이미지 데이터를 Base64로 인코딩
            import base64
            base64_image = base64.b64encode(image_data).decode('ascii')
            
            # API 요청 데이터
            data = {
                "version": "V2",
                "requestId": "ocr_request",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "images": [
                    {
                        "name": "image",
                        "format": "jpg",
                        "data": base64_image
                    }
                ]
            }
            
            # API 호출
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            # 응답 처리
            result = response.json()
            
            # 텍스트 추출
            extracted_text = ""
            if 'images' in result and len(result['images']) > 0:
                fields = result['images'][0].get('fields', [])
                for field in fields:
                    if 'inferText' in field:
                        extracted_text += field['inferText'] + " "
            
            return {
                "text": extracted_text.strip(),
                "raw_result": result
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "text": ""
            }
    
    
    def _load_pp_ocrv5_model(self):
        """
        PP-OCRv5 모델 로드 (지연 로딩)
        처음 사용할 때만 모델을 로드하여 메모리 효율성 향상
        """
        if self.pp_ocr_ocr is None:
            try:
                from paddleocr import PaddleOCR
                import paddle
                
                # GPU 사용 가능 여부 확인
                gpu_available = False
                gpu_device = "CPU"
                try:
                    # PaddlePaddle이 CUDA를 지원하는지 확인
                    if paddle.device.is_compiled_with_cuda():
                        # GPU가 사용 가능한지 확인
                        if paddle.device.cuda.device_count() > 0:
                            gpu_available = True
                            gpu_device = f"GPU (CUDA {paddle.device.cuda.device_count()}개)"
                            print(f"🚀 GPU 감지됨: {gpu_device}")
                        else:
                            print("⚠️ CUDA는 지원되지만 사용 가능한 GPU가 없습니다. CPU 사용.")
                    else:
                        print("ℹ️ CUDA가 지원되지 않는 빌드입니다. CPU 사용.")
                except Exception as e:
                    print(f"⚠️ GPU 확인 중 오류: {e}. CPU 사용.")
                
                # 한국어 모델 사용 여부에 따라 설정
                if self.pp_ocrv5_use_korean:
                    # 한국어 특화 모델 사용
                    # lang='korean': 한국어 모델 사용 (korean_PP-OCRv5_mobile_rec)
                    # use_doc_orientation_classify: 문서 방향 분류 사용 (성능 향상)
                    # use_textline_orientation: 텍스트 라인 방향 감지 사용 (성능 향상)
                    # text_rec_score_thresh: 텍스트 인식 신뢰도 임계값 (낮을수록 더 많은 텍스트 인식)
                    self.pp_ocr_ocr = PaddleOCR(
                        lang='korean',  # 한국어 모델
                        use_doc_orientation_classify=True,  # 문서 방향 분류 활성화 (성능 향상)
                        use_textline_orientation=True,  # 텍스트 라인 방향 감지 활성화 (성능 향상)
                        text_rec_score_thresh=0.5,  # 텍스트 인식 신뢰도 임계값 (0.5 = 50% 이상)
                        ocr_version='PP-OCRv5'  # PP-OCRv5 버전 명시
                    )
                else:
                    # 기본 다국어 모델 사용
                    self.pp_ocr_ocr = PaddleOCR(
                        lang='ch',  # 중국어/영어 기본 모델 (한국어도 지원)
                        use_doc_orientation_classify=True,
                        use_textline_orientation=True,
                        text_rec_score_thresh=0.5,
                        ocr_version='PP-OCRv5'
                    )
                
                # GPU 사용 정보 저장 (결과에 포함하기 위해)
                self.pp_ocr_gpu_info = {
                    "gpu_available": gpu_available,
                    "gpu_device": gpu_device,
                    "using_gpu": gpu_available  # PaddleOCR은 자동으로 GPU 사용
                }
                
                print(f"✅ PP-OCRv5 모델 로드 완료 ({gpu_device})")
                
            except ImportError:
                raise ImportError(
                    "PaddleOCR이 설치되지 않았습니다. "
                    "설치하려면: pip install paddleocr paddlepaddle"
                )
            except Exception as e:
                raise Exception(f"PP-OCRv5 모델 로드 실패: {str(e)}")
        
        return self.pp_ocr_ocr
    
    
    def process_with_pp_ocrv5(self, image_path: str) -> Dict:
        """
        PP-OCRv5 모델을 사용한 OCR 처리
        한국어에 특화된 PaddleOCR의 최신 모델 사용
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            인식된 상품 정보 딕셔너리
        """
        try:
            # PP-OCRv5 모델 로드 (지연 로딩)
            ocr = self._load_pp_ocrv5_model()
            
            # 이미지 파일 읽기 (한글 경로 대응)
            # PaddleOCR은 파일 경로를 직접 받을 수 있지만, 
            # 한글 경로 문제를 방지하기 위해 numpy array로 변환
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"이미지를 불러올 수 없습니다: {image_path}")
            
            # OCR 수행
            # PaddleOCR 3.3.2에서는 result[0]이 OCRResult 객체
            result = ocr.ocr(image)
            
            # 결과 파싱
            full_text = ""
            text_lines = []
            
            if result and len(result) > 0:
                ocr_result = result[0]
                
                # OCRResult 객체는 딕셔너리처럼 동작
                # rec_texts: 인식된 텍스트 리스트
                # rec_scores: 각 텍스트의 신뢰도 리스트
                # get() 메서드를 사용하여 안전하게 접근
                texts = ocr_result.get('rec_texts', []) or []
                scores = ocr_result.get('rec_scores', []) or []
                
                # 텍스트와 신뢰도를 매칭
                if texts:
                    for i, text in enumerate(texts):
                        if text and isinstance(text, str):
                            confidence = scores[i] if i < len(scores) else 0.0
                            full_text += text + "\n"
                            text_lines.append({
                                "text": text,
                                "confidence": float(confidence)
                            })
            
            # 텍스트가 없으면 오류 반환
            if not full_text.strip():
                return {
                    "products": [],
                    "raw_text": "",
                    "error": "텍스트를 인식할 수 없습니다.",
                    "message": "이미지에서 텍스트를 찾을 수 없습니다."
                }
            
            # 상품 정보 파싱
            products = self._parse_text_to_products(full_text)
            
            # GPU 사용 정보 가져오기 (모델이 로드된 경우)
            gpu_info = getattr(self, 'pp_ocr_gpu_info', {
                "gpu_available": False,
                "gpu_device": "CPU",
                "using_gpu": False
            })
            
            # 결과 구성
            result_dict = {
                "products": products,
                "raw_text": full_text.strip(),
                "text_lines": text_lines,  # 각 라인별 상세 정보
                "metadata": {
                    "method": "pp_ocrv5",
                    "timestamp": datetime.now().isoformat(),
                    "image_path": image_path,
                    "total_items": len(products),
                    "total_text_lines": len(text_lines),
                    "korean_model": self.pp_ocrv5_use_korean,
                    "gpu_info": gpu_info  # GPU 사용 정보 추가
                }
            }
            
            return result_dict
            
        except ImportError as e:
            return {
                "error": f"PaddleOCR 라이브러리 오류: {str(e)}",
                "message": "PaddleOCR이 설치되지 않았습니다. pip install paddleocr paddlepaddle로 설치하세요."
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": "PP-OCRv5 처리 중 오류가 발생했습니다."
            }
    
    
    def _parse_text_to_products(self, text: str) -> List[Dict]:
        """
        추출된 텍스트에서 상품명과 가격 파싱
        간단한 규칙 기반 파싱 (개선 가능)
        
        Args:
            text: OCR로 추출된 텍스트
            
        Returns:
            상품 정보 리스트
        """
        import re
        
        products = []
        lines = text.strip().split('\n')
        
        # 가격 패턴 (예: 800원, 5000원, 10,000원, 1만원)
        price_pattern = r'(\d[\d,]*)\s*원|(\d+)\s*만\s*원'
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 가격을 찾음
            price_match = re.search(price_pattern, line)
            if price_match:
                # 가격이 있는 경우, 이전 라인이나 같은 라인에서 상품명 찾기
                product_name = ""
                price = price_match.group(0)
                
                # 가격 앞부분을 상품명으로 추정
                product_name = line[:price_match.start()].strip()
                
                # 상품명이 비어있으면 이전 라인 확인
                if not product_name and i > 0:
                    product_name = lines[i-1].strip()
                
                if product_name:
                    products.append({
                        "product_name": product_name,
                        "price": price,
                        "unit": "",
                        "confidence": 0.7
                    })
        
        return products
    
    
    def process_image(self, image_path: str) -> Dict:
        """
        이미지 처리 메인 함수
        설정된 방법으로 OCR 수행
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            인식된 상품 정보 (JSON 형태)
        """
        # 이미지 파일 존재 확인
        if not os.path.exists(image_path):
            return {
                "error": "파일을 찾을 수 없습니다.",
                "image_path": image_path
            }
        
        # 선택한 방법으로 처리
        if self.method == "gpt4_vision":
            return self.process_with_gpt4_vision(image_path)
        elif self.method == "google_vision":
            return self.process_with_google_vision(image_path)
        elif self.method == "naver_clova":
            return self.process_with_naver_clova(image_path)
        elif self.method == "pp_ocrv5":
            return self.process_with_pp_ocrv5(image_path)
        else:
            return {
                "error": f"지원하지 않는 OCR 방법: {self.method}",
                "supported_methods": ["gpt4_vision", "google_vision", "naver_clova", "pp_ocrv5"]
            }
    
    
    def save_result(self, result: Dict, output_path: str = "result.json"):
        """
        결과를 JSON 파일로 저장
        
        Args:
            result: 인식 결과 딕셔너리
            output_path: 저장할 파일 경로
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 결과가 저장되었습니다: {output_path}")
        except Exception as e:
            print(f"❌ 저장 실패: {e}")


# 커맨드라인에서 직접 실행할 때
if __name__ == "__main__":
    import argparse
    
    # 커맨드라인 인자 파싱
    parser = argparse.ArgumentParser(description="시장 가판대 상품 OCR")
    parser.add_argument("--image", "-i", required=True, help="이미지 파일 경로")
    parser.add_argument(
        "--method", "-m", 
        default="gpt4_vision",
        choices=["gpt4_vision", "google_vision", "naver_clova", "pp_ocrv5"],
        help="OCR 방법 선택 (gpt4_vision, google_vision, naver_clova, pp_ocrv5)"
    )
    parser.add_argument("--output", "-o", default="result.json", help="결과 저장 경로")
    
    args = parser.parse_args()
    
    # 프로세서 생성 및 실행
    print(f"🚀 OCR 처리 시작... (방법: {args.method})")
    print(f"📷 이미지: {args.image}")
    
    processor = MarketOCRProcessor(method=args.method)
    result = processor.process_image(args.image)
    
    # 결과 출력
    print("\n" + "="*50)
    print("📊 인식 결과")
    print("="*50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 결과 저장
    processor.save_result(result, args.output)

