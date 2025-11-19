"""
시장 가판대 OCR 웹 애플리케이션 (Streamlit)
브라우저에서 이미지를 업로드하고 OCR 결과를 확인할 수 있습니다.
"""

import streamlit as st
import json
import os
from pathlib import Path
from PIL import Image
import tempfile

# 사용자 정의 OCR 프로세서 임포트
try:
    from ultra_safe_ocr import UltraSafeOCR
    USE_ULTRA_SAFE_OCR = True
except ImportError:
    USE_ULTRA_SAFE_OCR = False

try:
    from simple_ocr_processor import SimpleOCRProcessor
    USE_SIMPLE_PROCESSOR = True
except ImportError:
    USE_SIMPLE_PROCESSOR = False

# 기존 OCR 프로세서 임포트 (항상 시도)
try:
    from ocr_processor import MarketOCRProcessor
    MARKET_OCR_AVAILABLE = True
except ImportError as e:
    MARKET_OCR_AVAILABLE = False


# 페이지 설정
st.set_page_config(
    page_title="시장 가판대 OCR 시스템",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """
    메인 애플리케이션 함수
    """
    # 타이틀
    st.title("🏪 시장 가판대 상품정보 OCR 시스템")
    st.markdown("---")
    st.markdown("""
    📸 **시장 가판대 사진을 업로드하면 상품명과 가격을 자동으로 인식합니다!**
    
    - 한글 손글씨 가격표 인식
    - JSON 형식으로 결과 제공
    - 여러 OCR 엔진 지원
    """)
    
    # 사이드바 - 설정
    st.sidebar.header("⚙️ 설정")
    
    # OCR 방법 선택 (GPT-4 Vision을 기본값으로 설정)
    ocr_method = st.sidebar.selectbox(
        "OCR 엔진 선택",
        options=["gpt4_vision", "naver_clova", "google_vision", "pp_ocrv5"],
        index=0,
        help="GPT-4 Vision이 가장 높은 인식률을 제공합니다."
    )
    
    # 방법별 설명
    method_info = {
        "gpt4_vision": "✨ **GPT-4 Vision** (기본, 추천) ✅\n- 가장 높은 인식률\n- 한글 손글씨 특화\n- 상품명과 가격 정확 분류\n- OpenAI API 키 필요",
        "naver_clova": "🇰🇷 **Naver Clova OCR**\n- 한국어 및 한글 손글씨에 특화\n- 월 1,000건 무료 제공\n- 국내 서버로 빠른 응답\n- ASCII 인코딩 문제 없음",
        "google_vision": "🔍 **Google Cloud Vision**\n- 높은 정확도\n- 월 1,000건 무료\n- GCP 인증 필요",
        "pp_ocrv5": "🚀 **PP-OCRv5** (다섯 번째 엔진) ✅\n- 한국어 특화 모델 (88% 정확도)\n- 로컬 실행 (API 비용 없음)\n- 오프라인 사용 가능\n- PaddleOCR 라이브러리 필요"
    }
    
    st.sidebar.info(method_info[ocr_method])
    
    # API 키 확인
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 API 키 상태")
    
    # 선택한 OCR 방법에 따라 API 키 상태 확인
    if ocr_method == "naver_clova":
        naver_secret = os.getenv("NAVER_OCR_SECRET_KEY")
        naver_url = os.getenv("NAVER_OCR_API_URL")
        if naver_secret and naver_url and "여기에" not in naver_secret:
            st.sidebar.success("✅ Naver Clova OCR 설정 완료")
        else:
            st.sidebar.error("❌ Naver Clova OCR 키가 설정되지 않았습니다.")
            st.sidebar.info("`.env` 파일에 네이버 클라우드 정보를 입력하세요.")
            st.sidebar.markdown("""
            **설정 방법:**
            1. [네이버 클라우드](https://www.ncloud.com) 가입
            2. Clova OCR 서비스 신청
            3. Secret Key와 API URL 복사
            4. `.env` 파일에 입력
            """)
    
    elif ocr_method == "gpt4_vision":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.sidebar.success("✅ OpenAI API 키 확인됨")
        else:
            st.sidebar.error("❌ OpenAI API 키가 설정되지 않았습니다.")
            st.sidebar.info("`.env` 파일에 `OPENAI_API_KEY`를 추가하세요.")
    
    elif ocr_method == "google_vision":
        credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials:
            st.sidebar.success("✅ Google Cloud 인증 확인됨")
        else:
            st.sidebar.error("❌ Google Cloud 인증이 설정되지 않았습니다.")
            st.sidebar.info("`.env` 파일에 `GOOGLE_APPLICATION_CREDENTIALS`를 추가하세요.")
    
    elif ocr_method == "pp_ocrv5":
        # PP-OCRv5는 라이브러리 설치만 확인
        try:
            import paddleocr
            st.sidebar.success("✅ PP-OCRv5 라이브러리 확인됨")
        except ImportError:
            st.sidebar.warning("⚠️ PaddleOCR이 설치되지 않았습니다.")
            st.sidebar.info("설치 방법: `pip install paddleocr paddlepaddle`")
            st.sidebar.markdown("""
            **설정 방법:**
            1. 터미널에서 `pip install paddleocr paddlepaddle` 실행
            2. 첫 실행 시 모델이 자동으로 다운로드됩니다
            3. 한국어 모델 사용 (기본값)
            """)
    
    # 메인 영역 - 이미지 업로드
    st.header("1️⃣ 이미지 업로드")
    
    # 파일 업로더
    uploaded_file = st.file_uploader(
        "시장 가판대 사진을 선택하세요",
        type=["jpg", "jpeg", "png", "webp"],
        help="가격표가 선명하게 보이는 사진을 선택하세요."
    )
    
    # 샘플 이미지 사용 옵션
    use_sample = st.checkbox("샘플 이미지 사용 (테스트용)")
    
    if uploaded_file or use_sample:
        # 2열 레이아웃
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 업로드된 이미지")
            
            # 이미지 표시 및 임시 저장
            if uploaded_file:
                # 업로드된 파일 표시
                image = Image.open(uploaded_file)
                st.image(image, use_container_width=True)
                
                # 임시 파일로 저장 (파일명 강제 ASCII화)
                import uuid
                temp_filename = f"uploaded_image_{uuid.uuid4().hex}.jpg"
                temp_image_path = os.path.join(tempfile.gettempdir(), temp_filename)
                image.save(temp_image_path)
            
            else:
                # 샘플 이미지 (실제로는 사용자가 제공한 이미지를 사용)
                st.info("샘플 이미지를 사용하려면 `sample_images/` 폴더에 이미지를 넣으세요.")
                temp_image_path = None
        
        with col2:
            st.subheader("🔍 OCR 결과")
            
            # OCR 처리 버튼
            if st.button("🚀 OCR 시작", type="primary", use_container_width=True):
                if temp_image_path and os.path.exists(temp_image_path):
                    # 프로그레스 표시
                    with st.spinner(f"🤖 {ocr_method}로 이미지 분석 중... (약 5-10초 소요)"):
                        try:
                            # OCR 프로세서 생성 (초안전 프로세서 우선 사용)
                            if USE_ULTRA_SAFE_OCR and ocr_method == "gpt4_vision":
                                processor = UltraSafeOCR()
                                result = processor.process_image(temp_image_path)
                                
                                # 결과 형식 통일
                                if result.get("success"):
                                    products = result.get("products", [])
                                    result = {
                                        "products": products,
                                        "metadata": {
                                            "method": "ultra_safe_gpt4_vision",
                                            "total_items": len(products)
                                        }
                                    }
                                else:
                                    result = {"error": result.get("error", "Unknown error")}
                            elif USE_SIMPLE_PROCESSOR and ocr_method == "gpt4_vision":
                                processor = SimpleOCRProcessor()
                                result = processor.process_image(temp_image_path)
                                
                                # 결과 형식 통일
                                if result.get("success"):
                                    products = result.get("products", [])
                                    result = {
                                        "products": products,
                                        "metadata": {
                                            "method": "simple_gpt4_vision",
                                            "total_items": len(products)
                                        }
                                    }
                                else:
                                    result = {"error": result.get("error", "Unknown error")}
                            else:
                                # 기존 프로세서 사용 (가용성 확인)
                                if MARKET_OCR_AVAILABLE:
                                    processor = MarketOCRProcessor(method=ocr_method)
                                    result = processor.process_image(temp_image_path)
                                else:
                                    result = {"error": "MarketOCRProcessor not available", "message": "OCR processor could not be loaded"}
                            
                            # 에러 확인
                            if "error" in result:
                                st.error(f"❌ Error: {result['error']}")
                                st.info(result.get('message', ''))
                            else:
                                # 성공 메시지
                                st.success("✅ OCR 처리 완료!")
                                
                                # 결과 표시
                                st.markdown("### 📊 인식된 상품 정보")
                                
                                products = result.get("products", [])
                                
                                if products:
                                    # 상품 정보를 표 형식으로 표시
                                    for idx, product in enumerate(products, 1):
                                        with st.expander(f"**{idx}. {product.get('product_name', '이름 없음')}**"):
                                            col_a, col_b = st.columns(2)
                                            with col_a:
                                                st.write("**가격:**", product.get('price', 'N/A'))
                                            with col_b:
                                                st.write("**단위:**", product.get('unit', 'N/A') or '-')
                                            
                                            if 'additional_info' in product and product['additional_info']:
                                                st.write("**추가정보:**", product['additional_info'])
                                    
                                    # 통계
                                    st.markdown("---")
                                    st.info(f"📦 총 **{len(products)}개** 상품이 인식되었습니다.")
                                else:
                                    st.warning("⚠️ 상품을 찾을 수 없습니다. 이미지를 다시 확인해주세요.")
                                
                                # JSON 결과 표시
                                st.markdown("### 📄 JSON 결과")
                                st.json(result)
                                
                                # 다운로드 버튼
                                json_str = json.dumps(result, ensure_ascii=False, indent=2)
                                st.download_button(
                                    label="💾 JSON 다운로드",
                                    data=json_str,
                                    file_name="ocr_result.json",
                                    mime="application/json",
                                    use_container_width=True
                                )
                        
                        except ValueError as e:
                            st.error(f"❌ Configuration Error: {e}")
                            st.info("Please check your API key and `.env` file settings.")
                        
                        except Exception as e:
                            st.error(f"❌ Unexpected Error: {e}")
                    
                    # 임시 파일 삭제
                    try:
                        os.unlink(temp_image_path)
                    except:
                        pass
                else:
                    st.error("Image file not found.")
    
    # 하단 - 사용 방법
    st.markdown("---")
    with st.expander("📖 사용 방법"):
        st.markdown("""
        ### 시작하기
        
        1. **API 키 설정**
           - 프로젝트 폴더에 `.env` 파일 생성
           - API 키 입력 (예: `OPENAI_API_KEY=sk-...`)
        
        2. **이미지 준비**
           - 가격표가 선명한 사진 사용
           - 조명이 밝은 환경에서 촬영
           - 가능한 정면에서 촬영
        
        3. **OCR 실행**
           - 이미지 업로드
           - OCR 엔진 선택
           - '🚀 OCR 시작' 버튼 클릭
        
        ### 팁
        - **인식률이 낮을 때**: GPT-4 Vision 사용 권장
        - **가격표가 작을 때**: 이미지를 크롭하여 가격표만 촬영
        - **손글씨가 흐릿할 때**: 조명을 개선하거나 고화질로 촬영
        
        ### 예상 처리 시간
        - GPT-4 Vision: 5-10초
        - Google Vision: 2-5초
        - Naver Clova: 3-7초
        - PP-OCRv5: 2-5초 (첫 실행 시 모델 로드 시간 추가)
        """)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>🏪 시장 가판대 OCR 시스템 v1.0 | Made with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


# 애플리케이션 실행
if __name__ == "__main__":
    main()

