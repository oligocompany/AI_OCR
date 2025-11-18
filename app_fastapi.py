"""
시장 가판대 OCR API 서버 (FastAPI)
RESTful API로 OCR 서비스 제공
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
from pathlib import Path

# 사용자 정의 OCR 프로세서
from ocr_processor import MarketOCRProcessor


# FastAPI 앱 초기화
app = FastAPI(
    title="시장 가판대 OCR API",
    description="시장 가판대 사진에서 상품명과 가격을 인식하는 AI OCR API",
    version="1.0.0"
)


# CORS 설정 (모바일 앱이나 웹에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 응답 모델 정의
class OCRResponse(BaseModel):
    """OCR 결과 응답 모델"""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """
    API 루트 엔드포인트
    서비스 상태 확인
    """
    return {
        "service": "시장 가판대 OCR API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "POST /ocr": "이미지 업로드 및 OCR 처리",
            "GET /health": "서비스 상태 확인",
            "GET /docs": "API 문서 (Swagger UI)"
        }
    }


@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    서버가 정상 동작하는지 확인
    """
    return {
        "status": "healthy",
        "message": "서비스가 정상 작동 중입니다."
    }


@app.post("/ocr", response_model=OCRResponse)
async def process_ocr(
    file: UploadFile = File(..., description="OCR 처리할 이미지 파일"),
    method: str = Form(default="gpt4_vision", description="OCR 방법: gpt4_vision, google_vision, naver_clova")
):
    """
    이미지 업로드 및 OCR 처리
    
    **Parameters:**
    - **file**: 시장 가판대 사진 (JPG, PNG, WEBP)
    - **method**: OCR 엔진 선택
        - `gpt4_vision`: OpenAI GPT-4 Vision (추천)
        - `google_vision`: Google Cloud Vision API
        - `naver_clova`: Naver Clova OCR
    
    **Returns:**
    - 인식된 상품명, 가격, 단위 정보를 JSON 형식으로 반환
    
    **Example Response:**
    ```json
    {
      "success": true,
      "message": "OCR 처리 완료",
      "data": {
        "products": [
          {
            "product_name": "계란 조개류",
            "price": "800원",
            "unit": "1개"
          }
        ],
        "metadata": {
          "method": "gpt4_vision",
          "total_items": 1
        }
      }
    }
    ```
    """
    
    # 파일 형식 검증
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {allowed_extensions}"
        )
    
    # OCR 방법 검증
    allowed_methods = ["gpt4_vision", "google_vision", "naver_clova"]
    if method not in allowed_methods:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 OCR 방법입니다. 허용: {allowed_methods}"
        )
    
    # 임시 파일로 저장
    try:
        # 임시 디렉토리 생성
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # 업로드된 파일 저장
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # OCR 프로세서 초기화
        try:
            processor = MarketOCRProcessor(method=method)
        except ValueError as e:
            # API 키 누락 등의 설정 오류
            raise HTTPException(
                status_code=500,
                detail=f"OCR 설정 오류: {str(e)}"
            )
        
        # OCR 수행
        result = processor.process_image(temp_file_path)
        
        # 임시 파일 삭제
        os.remove(temp_file_path)
        os.rmdir(temp_dir)
        
        # 오류 확인
        if "error" in result:
            return OCRResponse(
                success=False,
                message="OCR 처리 중 오류 발생",
                error=result["error"]
            )
        
        # 성공 응답
        return OCRResponse(
            success=True,
            message="OCR 처리 완료",
            data=result
        )
    
    except HTTPException:
        # FastAPI HTTPException은 그대로 전달
        raise
    
    except Exception as e:
        # 기타 예상치 못한 오류
        raise HTTPException(
            status_code=500,
            detail=f"서버 오류: {str(e)}"
        )


@app.post("/ocr/batch")
async def process_batch_ocr(
    files: list[UploadFile] = File(..., description="여러 이미지 파일"),
    method: str = Form(default="gpt4_vision")
):
    """
    여러 이미지를 한 번에 OCR 처리 (배치 처리)
    
    **Parameters:**
    - **files**: 여러 이미지 파일 (최대 10개)
    - **method**: OCR 방법
    
    **Returns:**
    - 각 이미지의 OCR 결과 리스트
    """
    
    # 최대 파일 수 제한
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="한 번에 최대 10개 파일까지 처리 가능합니다."
        )
    
    results = []
    
    # 각 파일 처리
    for idx, file in enumerate(files):
        try:
            # 개별 OCR 처리 (위의 process_ocr 로직 재사용)
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, file.filename)
            
            with open(temp_file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            processor = MarketOCRProcessor(method=method)
            result = processor.process_image(temp_file_path)
            
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
            
            results.append({
                "file_index": idx,
                "filename": file.filename,
                "success": "error" not in result,
                "result": result
            })
        
        except Exception as e:
            results.append({
                "file_index": idx,
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {
        "success": True,
        "message": f"{len(files)}개 파일 처리 완료",
        "results": results
    }


# 서버 실행 함수
def run_server(host: str = "0.0.0.0", port: int = 8000):
    """
    FastAPI 서버 실행
    
    Args:
        host: 호스트 주소 (기본: 0.0.0.0)
        port: 포트 번호 (기본: 8000)
    """
    import uvicorn
    
    print("="*50)
    print("🚀 시장 가판대 OCR API 서버 시작")
    print("="*50)
    print(f"📡 서버 주소: http://{host}:{port}")
    print(f"📖 API 문서: http://{host}:{port}/docs")
    print(f"🔍 ReDoc: http://{host}:{port}/redoc")
    print("="*50)
    
    # Uvicorn으로 서버 실행
    uvicorn.run(app, host=host, port=port)


# 직접 실행 시
if __name__ == "__main__":
    run_server()









