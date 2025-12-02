"""
시장 이미지 OCR 테스트 스크립트
제공된 이미지들에 대해 다양한 OCR 엔진 테스트
"""

import os
import json
from ocr_processor import MarketOCRProcessor
from simple_ocr_processor import SimpleOCRProcessor

def test_market_images():
    """
    시장 이미지들에 대한 OCR 테스트
    """
    print("🏪 시장 이미지 OCR 테스트 시작")
    print("=" * 50)
    
    # 테스트할 이미지 파일들 (실제 경로로 변경 필요)
    test_images = [
        "market_image_1.jpg",  # 옻나무 가격표 이미지
        "market_image_2.jpg",  # 포도 가격표 이미지  
        "market_image_3.jpg"   # 귤 가격표 이미지
    ]
    
    # OCR 엔진들 테스트
    engines = [
        ("gpt4_vision", "GPT-4 Vision (추천)"),
        ("naver_clova", "Naver Clova OCR"),
        ("google_vision", "Google Cloud Vision")
    ]
    
    for image_path in test_images:
        if not os.path.exists(image_path):
            print(f"⚠️  이미지 파일을 찾을 수 없습니다: {image_path}")
            continue
            
        print(f"\n📷 이미지 처리: {image_path}")
        print("-" * 30)
        
        for engine_name, engine_desc in engines:
            try:
                print(f"\n🔍 {engine_desc} 테스트 중...")
                
                # OCR 프로세서 생성
                processor = MarketOCRProcessor(method=engine_name)
                
                # 이미지 처리
                result = processor.process_image(image_path)
                
                # 결과 출력
                if "error" in result:
                    print(f"❌ 오류: {result['error']}")
                else:
                    print("✅ 성공!")
                    products = result.get("products", [])
                    print(f"📦 인식된 상품 수: {len(products)}")
                    
                    for i, product in enumerate(products, 1):
                        print(f"  {i}. {product.get('product_name', 'N/A')} - {product.get('price', 'N/A')}")
                
            except Exception as e:
                print(f"❌ {engine_desc} 오류: {str(e)}")
            
            print()  # 빈 줄 추가

def test_simple_ocr():
    """
    간단한 OCR 프로세서 테스트
    """
    print("\n🚀 간단한 OCR 프로세서 테스트")
    print("=" * 50)
    
    try:
        processor = SimpleOCRProcessor()
        
        # 테스트 이미지 (실제 경로로 변경)
        test_image = "market_image_1.jpg"
        
        if os.path.exists(test_image):
            print(f"📷 테스트 이미지: {test_image}")
            result = processor.process_image(test_image)
            
            if result["success"]:
                print("✅ OCR 성공!")
                print("📊 결과:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("❌ OCR 실패:", result["error"])
        else:
            print("❌ 테스트 이미지를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 초기화 오류: {e}")

def main():
    """
    메인 실행 함수
    """
    print("🏪 시장 OCR 엔진 테스트 프로그램")
    print("=" * 50)
    
    # 환경 변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   sibangaiocr.env 파일에 API 키를 설정해주세요.")
        return
    
    # 테스트 실행
    test_market_images()
    test_simple_ocr()
    
    print("\n🎉 테스트 완료!")
    print("\n💡 추천사항:")
    print("1. GPT-4 Vision: 가장 정확한 결과")
    print("2. Naver Clova: 한국어 특화, 무료 사용량 제공")
    print("3. Google Vision: 안정적이고 빠름")

if __name__ == "__main__":
    main()










