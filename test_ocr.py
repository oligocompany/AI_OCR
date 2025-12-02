"""
OCR 시스템 테스트 스크립트
API 키 확인 및 간단한 테스트 수행
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


def check_api_keys():
    """
    API 키 설정 확인
    각 OCR 방법에 필요한 키가 있는지 체크
    """
    print("="*50)
    print("🔑 API 키 설정 확인")
    print("="*50)
    
    results = {}
    
    # OpenAI API 키 확인
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-"):
        print("✅ OpenAI API 키: 설정됨")
        results["gpt4_vision"] = True
    else:
        print("❌ OpenAI API 키: 미설정")
        print("   → .env 파일에 OPENAI_API_KEY 추가 필요")
        results["gpt4_vision"] = False
    
    # Google Cloud Vision 확인
    google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if google_creds and os.path.exists(google_creds):
        print("✅ Google Cloud Vision: 설정됨")
        results["google_vision"] = True
    else:
        print("❌ Google Cloud Vision: 미설정")
        print("   → .env 파일에 GOOGLE_APPLICATION_CREDENTIALS 추가 필요")
        results["google_vision"] = False
    
    # Naver Clova OCR 확인
    naver_secret = os.getenv("NAVER_OCR_SECRET_KEY")
    naver_url = os.getenv("NAVER_OCR_API_URL")
    if naver_secret and naver_url:
        print("✅ Naver Clova OCR: 설정됨")
        results["naver_clova"] = True
    else:
        print("❌ Naver Clova OCR: 미설정")
        print("   → .env 파일에 NAVER_OCR_SECRET_KEY, NAVER_OCR_API_URL 추가 필요")
        results["naver_clova"] = False
    
    print("="*50)
    
    return results


def check_dependencies():
    """
    필요한 Python 패키지 설치 확인
    """
    print("\n" + "="*50)
    print("📦 필수 패키지 확인")
    print("="*50)
    
    required_packages = [
        "openai",
        "google-cloud-vision",
        "pillow",
        "opencv-python",
        "numpy",
        "streamlit",
        "fastapi",
        "uvicorn",
        "python-dotenv",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # 패키지명 변환 (설치명 -> 임포트명)
            import_name = package.replace("-", "_")
            if import_name == "opencv_python":
                import_name = "cv2"
            elif import_name == "pillow":
                import_name = "PIL"
            
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}: 미설치")
            missing_packages.append(package)
    
    print("="*50)
    
    if missing_packages:
        print(f"\n⚠️  누락된 패키지: {', '.join(missing_packages)}")
        print("다음 명령으로 설치하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("\n✅ 모든 패키지가 설치되어 있습니다!")
        return True


def test_sample_images():
    """
    샘플 이미지 확인
    """
    print("\n" + "="*50)
    print("📸 샘플 이미지 확인")
    print("="*50)
    
    sample_dir = Path("sample_images")
    
    if not sample_dir.exists():
        print("❌ sample_images/ 폴더가 없습니다.")
        print("   → 폴더를 생성하고 테스트 이미지를 넣으세요.")
        return []
    
    # 이미지 파일 찾기
    image_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    images = []
    
    for ext in image_extensions:
        images.extend(list(sample_dir.glob(f"*{ext}")))
        images.extend(list(sample_dir.glob(f"*{ext.upper()}")))
    
    if images:
        print(f"✅ {len(images)}개 이미지 발견:")
        for img in images:
            print(f"   - {img.name}")
    else:
        print("❌ 이미지가 없습니다.")
        print("   → sample_images/ 폴더에 테스트 이미지를 넣으세요.")
    
    print("="*50)
    
    return images


def run_quick_test(images, api_keys):
    """
    빠른 OCR 테스트 실행
    """
    if not images:
        print("\n⚠️  테스트할 이미지가 없습니다.")
        return
    
    # 사용 가능한 OCR 방법 찾기
    available_methods = [method for method, available in api_keys.items() if available]
    
    if not available_methods:
        print("\n⚠️  사용 가능한 OCR 방법이 없습니다.")
        print("API 키를 설정하고 다시 시도하세요.")
        return
    
    print("\n" + "="*50)
    print("🚀 OCR 테스트 시작")
    print("="*50)
    
    # 첫 번째 이미지로 테스트
    test_image = images[0]
    test_method = available_methods[0]
    
    print(f"📷 테스트 이미지: {test_image.name}")
    print(f"🔍 OCR 방법: {test_method}")
    print("⏱️  예상 시간: 5-10초")
    print("\n처리 중...")
    
    try:
        from ocr_processor import MarketOCRProcessor
        import json
        
        # OCR 프로세서 생성 및 실행
        processor = MarketOCRProcessor(method=test_method)
        result = processor.process_image(str(test_image))
        
        # 결과 출력
        if "error" in result:
            print(f"\n❌ 오류 발생: {result['error']}")
            print(f"   메시지: {result.get('message', '')}")
        else:
            print("\n✅ OCR 처리 완료!")
            print("\n📊 결과:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 간단한 통계
            total_items = len(result.get("products", []))
            print(f"\n📦 인식된 상품: {total_items}개")
    
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        print("상세 오류:")
        import traceback
        traceback.print_exc()
    
    print("="*50)


def main():
    """
    메인 테스트 함수
    """
    print("\n" + "="*60)
    print("🏪 시장 가판대 OCR 시스템 - 테스트 스크립트")
    print("="*60)
    
    # 1. API 키 확인
    api_keys = check_api_keys()
    
    # 2. 패키지 확인
    packages_ok = check_dependencies()
    
    if not packages_ok:
        print("\n❌ 필수 패키지를 먼저 설치하세요.")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # 3. 샘플 이미지 확인
    images = test_sample_images()
    
    # 4. 사용자 입력
    print("\n" + "="*50)
    print("🎯 다음 단계 선택")
    print("="*50)
    print("1. 빠른 OCR 테스트 실행 (샘플 이미지)")
    print("2. 특정 이미지 경로 입력하여 테스트")
    print("3. 웹 인터페이스 실행 (Streamlit)")
    print("4. API 서버 실행 (FastAPI)")
    print("5. 종료")
    
    choice = input("\n선택 (1-5): ").strip()
    
    if choice == "1":
        # 빠른 테스트
        run_quick_test(images, api_keys)
    
    elif choice == "2":
        # 사용자 지정 이미지
        image_path = input("이미지 경로 입력: ").strip()
        
        if not os.path.exists(image_path):
            print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        else:
            # 방법 선택
            available_methods = [m for m, ok in api_keys.items() if ok]
            if not available_methods:
                print("❌ 사용 가능한 OCR 방법이 없습니다.")
                return
            
            print("\nOCR 방법 선택:")
            for i, method in enumerate(available_methods, 1):
                print(f"{i}. {method}")
            
            method_choice = input(f"선택 (1-{len(available_methods)}): ").strip()
            try:
                method_idx = int(method_choice) - 1
                selected_method = available_methods[method_idx]
                
                from ocr_processor import MarketOCRProcessor
                import json
                
                print(f"\n🚀 OCR 처리 시작... (방법: {selected_method})")
                processor = MarketOCRProcessor(method=selected_method)
                result = processor.process_image(image_path)
                
                print("\n📊 결과:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
            except (ValueError, IndexError):
                print("❌ 잘못된 선택입니다.")
    
    elif choice == "3":
        # Streamlit 실행
        print("\n🌐 Streamlit 웹 인터페이스 실행 중...")
        print("브라우저에서 http://localhost:8501 을 열어주세요.")
        print("종료하려면 Ctrl+C를 누르세요.\n")
        os.system("streamlit run app_streamlit.py")
    
    elif choice == "4":
        # FastAPI 실행
        print("\n🚀 FastAPI 서버 실행 중...")
        print("브라우저에서 http://localhost:8000/docs 를 열어주세요.")
        print("종료하려면 Ctrl+C를 누르세요.\n")
        os.system("python app_fastapi.py")
    
    elif choice == "5":
        print("\n👋 종료합니다.")
    
    else:
        print("\n❌ 잘못된 선택입니다.")
    
    print("\n" + "="*60)
    print("테스트 완료!")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 사용자가 중단했습니다.")
        sys.exit(0)












