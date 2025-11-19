#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 웹 OCR 서버 - Streamlit 대신 Flask 사용
ASCII 인코딩 문제 완전 회피
"""

import os
import base64
import json
import tempfile
import uuid
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv("sibangaiocr.env")

app = Flask(__name__, static_folder='fonts', static_url_path='/fonts')

# HTML 템플릿 (드래그 앤 드롭 포함)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>전통시장 AI OCR 시스템</title>
    <style>
        @font-face {
            font-family: 'Paperlogy';
            src: url('/fonts/Paperlogy-4Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        @font-face {
            font-family: 'Paperlogy';
            src: url('/fonts/Paperlogy-6SemiBold.ttf') format('truetype');
            font-weight: 600;
            font-style: normal;
        }
        body { font-family: 'Paperlogy', 'Malgun Gothic', sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .upload-area { 
            border: 3px dashed #ccc; 
            padding: 40px; 
            text-align: center; 
            margin: 20px 0; 
            border-radius: 10px;
            transition: all 0.3s ease;
            cursor: pointer;
            font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;
        }
        .upload-area:hover { border-color: #007bff; background: #f8f9ff; }
        .upload-area.dragover { border-color: #007bff; background: #e6f3ff; transform: scale(1.02); }
        .upload-area.dragover h3 { color: #007bff; }
        .result { margin: 20px 0; padding: 20px; background: #f5f5f5; border-radius: 10px; font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; }
        .error { background: #ffe6e6; color: #d00; border-left: 4px solid #d00; }
        .success { background: #e6ffe6; color: #060; border-left: 4px solid #060; }
        button { 
            padding: 12px 24px; 
            background: #007bff; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px;
            font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;
            transition: all 0.3s ease;
            margin: 5px;
        }
        .button-group {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        .camera-btn {
            background: #28a745;
        }
        .camera-btn:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        .ocr-btn {
            background: #007bff;
        }
        .ocr-btn:hover {
            background: #0056b3;
            transform: translateY(-2px);
        }
        button:disabled { background: #ccc; cursor: not-allowed; }
        img { max-width: 100%; height: auto; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        #imagePreview { 
            max-width: 400px; 
            max-height: 300px; 
            width: auto; 
            height: auto; 
            object-fit: contain; 
            display: block; 
            margin: 15px auto; 
            border-radius: 8px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
            background: #f8f9fa;
        }
        .file-info { margin: 10px 0; padding: 10px; background: #e9ecef; border-radius: 5px; font-family: 'Paypalogist', sans-serif; }
        .hidden { display: none; }
        .progress { margin: 20px 0; }
        .progress-bar { 
            width: 100%; 
            height: 20px; 
            background: #e9ecef; 
            border-radius: 10px; 
            overflow: hidden;
        }
        .progress-fill { 
            height: 100%; 
            background: #007bff; 
            width: 0%; 
            transition: width 0.3s ease;
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .container { padding: 20px; margin: 10px; }
            .button-group { flex-direction: column; align-items: center; }
            .button-group button { width: 200px; margin: 5px 0; }
            h1 { font-size: 24px; }
            .upload-area { padding: 30px 20px; }
            .upload-area h3 { font-size: 18px; }
            #engineOptions { flex-direction: column; align-items: flex-start; gap: 10px; }
            #engineOptions label { width: 100%; margin-bottom: 8px; }
            #imagePreview { max-width: 300px; max-height: 250px; }
        }
        
        @media (max-width: 480px) {
            .container { padding: 15px; margin: 5px; }
            h1 { font-size: 20px; }
            .upload-area { padding: 20px 15px; }
            .upload-area h3 { font-size: 16px; }
            button { padding: 10px 20px; font-size: 14px; }
            #engineOptions { flex-direction: column; align-items: flex-start; gap: 8px; }
            #engineOptions label { width: 100%; margin-bottom: 6px; font-size: 14px; }
            #imagePreview { max-width: 250px; max-height: 200px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align: center; color: #333; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif; font-weight: 600;">🏪 전통시장 AI OCR 시스템</h1>
        <p style="text-align: center; color: #666; margin-bottom: 30px; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">이미지를 드래그하거나 클릭해서 업로드하세요</p>
        
        <!-- OCR 엔진 선택 -->
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #007bff;">
            <h3 style="margin-top: 0; color: #333; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">🤖 OCR 엔진 선택</h3>
            <div style="display: flex; gap: 15px; flex-wrap: wrap; align-items: center;" id="engineOptions">
                <label style="display: flex; align-items: center; cursor: pointer; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">
                    <input type="radio" name="ocr_engine" value="tesseract" checked style="margin-right: 8px;">
                    <span style="font-weight: 600;">Tesseract OCR</span>
                    <span style="margin-left: 10px; font-size: 12px; color: #666;">(고급처리)</span>
                </label>
                <label style="display: flex; align-items: center; cursor: pointer; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">
                    <input type="radio" name="ocr_engine" value="naver_clova" style="margin-right: 8px;">
                    <span style="font-weight: 600;">Naver Clova OCR</span>
                    <span style="margin-left: 10px; font-size: 12px; color: #666;">(한글 최적화)</span>
                </label>
                <label style="display: flex; align-items: center; cursor: pointer; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">
                    <input type="radio" name="ocr_engine" value="gpt4_vision" style="margin-right: 8px;">
                    <span style="font-weight: 600;">GPT-4 Vision</span>
                    <span style="margin-left: 10px; font-size: 12px; color: #666;">(고정밀 텍스트 인식)</span>
                </label>
                <label style="display: flex; align-items: center; cursor: pointer; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">
                    <input type="radio" name="ocr_engine" value="pp_ocrv5" style="margin-right: 8px;">
                    <span style="font-weight: 600;">🚀 PP-OCRv5</span>
                    <span style="margin-left: 10px; font-size: 12px; color: #666;">(한국어 특화, 로컬)</span>
                </label>
                <label style="display: flex; align-items: center; cursor: pointer; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif; opacity: 0.6;">
                    <input type="radio" name="ocr_engine" value="sibang_ocr" disabled style="margin-right: 8px;">
                    <span style="font-weight: 600;">🏪 Sibang OCR</span>
                    <span style="margin-left: 10px; font-size: 12px; color: #666;">(전통시장 전용)</span>
                </label>
            </div>
            <div id="engineStatus" style="margin-top: 10px; padding: 10px; background: #f0f8ff; border-radius: 5px; font-size: 14px; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">
                <strong>현재 선택:</strong> <span id="currentEngine">Tesseract OCR</span> - 고급처리 엔진
            </div>
            
            <!-- Sibang OCR 개발 예정 안내 -->
            <div id="sibangInfo" style="margin-top: 15px; padding: 15px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107; display: none;">
                <h4 style="margin-top: 0; color: #856404; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">🚧 Sibang OCR 개발 중</h4>
                <ul style="margin: 10px 0; padding-left: 20px; color: #856404; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">
                    <li>전통시장 가격표 특화 인식</li>
                    <li>한글 필기체 최적화</li>
                    <li>상품명 및 가격 자동 추출</li>
                    <li>시장 특화 용어 사전</li>
                </ul>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #6c757d; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">
                    💡 전통시장에 최적화된 OCR 엔진으로 개발 중입니다.
                </p>
            </div>
        </div>
        
        <form id="uploadForm" method="post" enctype="multipart/form-data">
            <div class="upload-area" id="uploadArea">
                <h3>📁 이미지를 여기에 드래그하세요</h3>
                <p>또는 클릭해서 파일을 선택하세요</p>
                <input type="file" id="fileInput" name="image" accept="image/*" class="hidden" required>
                <div class="file-info hidden" id="fileInfo"></div>
            </div>
            <div style="text-align: center; margin: 20px 0;">
                <div class="button-group">
                    <button type="button" class="camera-btn" onclick="openCamera()">📷 촬영하기</button>
                    <button type="submit" class="ocr-btn" id="submitBtn">🚀 OCR 시작</button>
                </div>
            </div>
        </form>
        
        <div class="progress hidden" id="progressDiv">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <p style="text-align: center; margin: 10px 0; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">OCR 처리 중...</p>
        </div>
        
        {% if result %}
        <div class="result {{ result.type }}">
            <h3>📊 OCR 결과</h3>
            {% if result.type == 'success' %}
                {% if result.engine %}
                <div style="background: #e6f3ff; padding: 10px; border-radius: 5px; margin-bottom: 15px; border-left: 4px solid #007bff;">
                    <strong>🤖 사용된 엔진:</strong> {{ result.engine }}
                </div>
                {% endif %}
                <div style="background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin: 10px 0;">
                    <pre style="white-space: pre-wrap; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif; margin: 0;">{{ result.message or result.text }}</pre>
                </div>
            {% else %}
                <div style="background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin: 10px 0;">
                    <pre style="white-space: pre-wrap; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif; margin: 0;">{{ result.message }}</pre>
                </div>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const uploadForm = document.getElementById('uploadForm');
        const submitBtn = document.getElementById('submitBtn');
        const progressDiv = document.getElementById('progressDiv');
        const progressFill = document.getElementById('progressFill');

        // 드래그 앤 드롭 이벤트
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                showFileInfo(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                showFileInfo(e.target.files[0]);
            }
        });
        
        function showFileInfo(file) {
            fileInfo.innerHTML = `
                <strong>선택된 파일:</strong> ${file.name}<br>
                <strong>크기:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB<br>
                <strong>타입:</strong> ${file.type}
            `;
            fileInfo.classList.remove('hidden');
            submitBtn.disabled = false;
            
            // 이미지 미리보기 추가
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = document.getElementById('imagePreview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'imagePreview';
                        preview.style.cssText = 'max-width: 400px; max-height: 300px; width: auto; height: auto; object-fit: contain; display: block; margin: 15px auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); background: #f8f9fa;';
                        fileInfo.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        }

        // 카메라 기능
        function openCamera() {
            // 모바일 디바이스 감지
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            
            if (isMobile) {
                // 모바일에서는 카메라로 직접 촬영
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*';
                input.capture = 'environment'; // 후면 카메라 우선
                input.onchange = function(e) {
                    const file = e.target.files[0];
                    if (file) {
                        document.getElementById('fileInput').files = e.target.files;
                        showFileInfo(file);
                        
                        // 이미지 미리보기
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            let preview = document.getElementById('imagePreview');
                            if (!preview) {
                                preview = document.createElement('img');
                                preview.id = 'imagePreview';
                                preview.style.cssText = 'max-width: 400px; max-height: 300px; width: auto; height: auto; object-fit: contain; display: block; margin: 15px auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); background: #f8f9fa;';
                                fileInfo.appendChild(preview);
                            }
                            preview.src = e.target.result;
                        };
                        reader.readAsDataURL(file);
                    }
                };
                input.click();
            } else {
                // 데스크톱에서는 웹캠 사용
                openWebcam();
            }
        }

        // 웹캠 기능 (데스크톱용)
        function openWebcam() {
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0,0,0,0.8); z-index: 1000; display: flex; 
                align-items: center; justify-content: center;
            `;
            
            const modalContent = document.createElement('div');
            modalContent.style.cssText = `
                background: white; padding: 20px; border-radius: 10px; 
                max-width: 500px; width: 90%; text-align: center;
            `;
            
            modalContent.innerHTML = `
                <h3 style="margin-bottom: 20px; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">📷 웹캠으로 촬영하기</h3>
                <video id="webcamVideo" autoplay style="width: 100%; max-width: 400px; border-radius: 8px; margin-bottom: 15px;"></video>
                <div style="margin: 15px 0;">
                    <button onclick="capturePhoto()" style="background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px; cursor: pointer; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">📸 촬영</button>
                    <button onclick="closeWebcam()" style="background: #dc3545; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px; cursor: pointer; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif;">❌ 닫기</button>
                </div>
            `;
            
            modal.appendChild(modalContent);
            document.body.appendChild(modal);
            
            // 웹캠 시작
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    const video = document.getElementById('webcamVideo');
                    video.srcObject = stream;
                    window.webcamStream = stream;
                })
                .catch(err => {
                    alert('웹캠에 접근할 수 없습니다. 카메라 권한을 허용해주세요.');
                    closeWebcam();
                });
        }

        function capturePhoto() {
            const video = document.getElementById('webcamVideo');
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);
            
            canvas.toBlob(blob => {
                const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
                
                // 파일 입력에 설정
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                document.getElementById('fileInput').files = dataTransfer.files;
                
                // 파일 정보 표시
                showFileInfo(file);
                
                // 이미지 미리보기
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = document.getElementById('imagePreview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'imagePreview';
                        preview.style.cssText = 'max-width: 400px; max-height: 300px; width: auto; height: auto; object-fit: contain; display: block; margin: 15px auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); background: #f8f9fa;';
                        fileInfo.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
                
                closeWebcam();
            }, 'image/jpeg', 0.8);
        }

        function closeWebcam() {
            if (window.webcamStream) {
                window.webcamStream.getTracks().forEach(track => track.stop());
                window.webcamStream = null;
            }
            const modal = document.querySelector('div[style*="position: fixed"]');
            if (modal) {
                modal.remove();
            }
        }
        
        // OCR 엔진 선택 이벤트
        document.querySelectorAll('input[name="ocr_engine"]').forEach(radio => {
            radio.addEventListener('change', function() {
                const currentEngine = document.getElementById('currentEngine');
                const engineStatus = document.getElementById('engineStatus');
                
                if (this.value === 'tesseract') {
                    currentEngine.textContent = 'Tesseract OCR';
                    engineStatus.innerHTML = '<strong>현재 선택:</strong> <span id="currentEngine">Tesseract OCR</span> - 고급처리 엔진';
                    engineStatus.style.background = '#f0f8ff';
                    document.getElementById('sibangInfo').style.display = 'none';
                } else if (this.value === 'naver_clova') {
                    currentEngine.textContent = 'Naver Clova OCR';
                    engineStatus.innerHTML = '<strong>현재 선택:</strong> <span id="currentEngine">Naver Clova OCR</span> - 한글 최적화 엔진';
                    engineStatus.style.background = '#e6fff2';
                    document.getElementById('sibangInfo').style.display = 'none';
                } else if (this.value === 'gpt4_vision') {
                    currentEngine.textContent = 'GPT-4 Vision';
                    engineStatus.innerHTML = '<strong>현재 선택:</strong> <span id="currentEngine">GPT-4 Vision</span> - 고정밀 텍스트 인식 엔진';
                    engineStatus.style.background = '#e6f3ff';
                    document.getElementById('sibangInfo').style.display = 'none';
                } else if (this.value === 'pp_ocrv5') {
                    currentEngine.textContent = 'PP-OCRv5';
                    engineStatus.innerHTML = '<strong>현재 선택:</strong> <span id="currentEngine">🚀 PP-OCRv5</span> - 한국어 특화 로컬 OCR 엔진';
                    engineStatus.style.background = '#fff5e6';
                    document.getElementById('sibangInfo').style.display = 'none';
                } else if (this.value === 'sibang_ocr') {
                    currentEngine.textContent = 'Sibang OCR';
                    engineStatus.innerHTML = '<strong>현재 선택:</strong> <span id="currentEngine">🏪 Sibang OCR</span> - 전통시장 전용 엔진<br><small style="color: #dc3545;">⚠️ 아직 개발 중입니다. 다른 엔진을 선택해주세요.</small>';
                    engineStatus.style.background = '#fff3cd';
                    engineStatus.style.borderLeft = '4px solid #ffc107';
                    
                    // Sibang OCR 정보 표시
                    document.getElementById('sibangInfo').style.display = 'block';
                } else {
                    // Sibang OCR이 아닌 경우 정보 숨기기
                    document.getElementById('sibangInfo').style.display = 'none';
                }
            });
        });

        // 폼 제출 시 AJAX로 처리 (페이지 새로고침 방지)
        uploadForm.addEventListener('submit', (e) => {
            e.preventDefault(); // 페이지 새로고침 방지
            
            const formData = new FormData(uploadForm);
            const selectedEngine = document.querySelector('input[name="ocr_engine"]:checked').value;
            formData.append('ocr_engine', selectedEngine);
            
            submitBtn.disabled = true;
            submitBtn.textContent = '처리 중...';
            progressDiv.classList.remove('hidden');
            
            // 프로그레스 바 애니메이션
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                progressFill.style.width = progress + '%';
            }, 200);
            
            // AJAX 요청으로 OCR 처리
            fetch('/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(html => {
                clearInterval(interval);
                progressFill.style.width = '100%';
                
                // 새 HTML에서 결과 부분만 추출
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newResult = doc.querySelector('.result');
                
                // 기존 결과 제거
                const existingResult = document.querySelector('.result');
                if (existingResult) {
                    existingResult.remove();
                }
                
                // 새 결과 추가 (이미지 프리뷰는 유지됨)
                if (newResult) {
                    const container = document.querySelector('.container');
                    container.appendChild(newResult);
                }
                
                submitBtn.disabled = false;
                submitBtn.textContent = '🚀 OCR 시작';
                progressDiv.classList.add('hidden');
            })
            .catch(error => {
                clearInterval(interval);
                console.error('Error:', error);
                
                // 에러 결과 표시
                const errorResult = document.createElement('div');
                errorResult.className = 'result error';
                errorResult.innerHTML = `
                    <h3>📊 OCR 결과</h3>
                    <div style="background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin: 10px 0;">
                        <pre style="white-space: pre-wrap; font-family: 'Paperlogy', 'Malgun Gothic', sans-serif; margin: 0;">오류가 발생했습니다: ${error.message}</pre>
                    </div>
                `;
                
                const existingResult = document.querySelector('.result');
                if (existingResult) {
                    existingResult.remove();
                }
                
                const container = document.querySelector('.container');
                container.appendChild(errorResult);
                
                submitBtn.disabled = false;
                submitBtn.textContent = '🚀 OCR 시작';
                progressDiv.classList.add('hidden');
            });
        });
        
        // 페이지 로드 시 이미지 프리뷰 상태 확인
        window.addEventListener('load', function() {
            const fileInput = document.getElementById('fileInput');
            const imagePreview = document.getElementById('imagePreview');
            
            // 파일이 선택되어 있다면 이미지 프리뷰 유지
            if (fileInput.files.length > 0 && !imagePreview) {
                showFileInfo(fileInput.files[0]);
            }
        });
    </script>
</body>
</html>
"""

def safe_process_image(image_data):
    """
    안전한 이미지 처리 - ASCII 인코딩 완전 회피
    """
    try:
        # OpenAI 클라이언트 생성
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Base64 인코딩 (완전 안전한 방법)
        base64_bytes = base64.b64encode(image_data)
        base64_image = base64_bytes.decode('ascii')
        
        # 영어 프롬프트 (ASCII 안전)
        prompt = """Analyze this image and extract all text content. 
        Focus on Korean text recognition for traditional market products.
        
        Please return the result in the following format:
        - Product names and prices
        - Any handwritten text
        - Market information
        
        Return the extracted text in Korean language."""
        
        # API 호출
        response = client.chat.completions.create(
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
        
        result_text = response.choices[0].message.content
        
        # 디버깅을 위한 로그
        print(f"OCR 결과: {result_text}")
        
        return {
            "type": "success",
            "message": result_text
        }
        
    except Exception as e:
        return {
            "type": "error",
            "message": f"OCR 처리 중 오류가 발생했습니다: {str(e)}"
        }

def safe_process_image_from_file(file_path):
    """파일 경로에서 안전하게 이미지 처리"""
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
        return safe_process_image(image_data)
    except Exception as e:
        return {
            "type": "error",
            "message": f"파일 처리 중 오류가 발생했습니다: {str(e)}"
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template_string(HTML_TEMPLATE, result={
                "type": "error",
                "message": "No image uploaded"
            })
        
        file = request.files['image']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, result={
                "type": "error",
                "message": "No image selected"
            })
        
        try:
            # 선택된 OCR 엔진 확인
            selected_engine = request.form.get('ocr_engine', 'naver_clova')
            
            # 안전한 이미지 처리
            try:
                # 이미지 데이터 직접 읽기 (메모리에서 처리)
                image_data = file.read()
                
                # 선택된 엔진에 따라 처리
                if selected_engine == 'tesseract':
                    try:
                        # Tesseract OCR 처리 (고급 이미지 전처리)
                        import pytesseract
                        from PIL import Image, ImageFilter, ImageOps
                        import io
                        import numpy as np
                        import cv2
                        
                        # 이미지 데이터를 PIL Image로 변환
                        image = Image.open(io.BytesIO(image_data))
                        
                        # 고급 이미지 전처리
                        # 1. 이미지를 OpenCV 형식으로 변환
                        img_array = np.array(image)
                        
                        # 2. 그레이스케일 변환
                        if len(img_array.shape) == 3:
                            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                        else:
                            gray = img_array
                        
                        # 3. 노이즈 제거 (가우시안 블러)
                        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
                        
                        # 4. 적응적 임계값 처리 (Adaptive Threshold)
                        # 텍스트 영역을 더 명확하게 분리
                        thresh = cv2.adaptiveThreshold(
                            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                            cv2.THRESH_BINARY, 11, 2
                        )
                        
                        # 5. 모폴로지 연산으로 노이즈 제거
                        kernel = np.ones((1, 1), np.uint8)
                        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                        
                        # 6. 이미지 크기 확대 (3배로 증가)
                        height, width = cleaned.shape
                        enlarged = cv2.resize(cleaned, (width * 3, height * 3), interpolation=cv2.INTER_CUBIC)
                        
                        # 7. PIL Image로 다시 변환
                        processed_image = Image.fromarray(enlarged)
                        
                        # 8. 추가 선명도 향상
                        from PIL import ImageEnhance
                        enhancer = ImageEnhance.Sharpness(processed_image)
                        processed_image = enhancer.enhance(1.5)
                        
                        # 9. 다중 OCR 설정으로 시도
                        results = []
                        
                        # 설정 1: 기본 한국어 설정
                        config1 = r'--oem 3 --psm 6 -l kor'
                        text1 = pytesseract.image_to_string(processed_image, config=config1).strip()
                        if text1:
                            results.append(('기본한국어', text1))
                        
                        # 설정 2: 한국어+영어 설정
                        config2 = r'--oem 3 --psm 6 -l kor+eng'
                        text2 = pytesseract.image_to_string(processed_image, config=config2).strip()
                        if text2:
                            results.append(('한국어+영어', text2))
                        
                        # 설정 3: 단일 텍스트 라인 설정
                        config3 = r'--oem 3 --psm 7 -l kor+eng'
                        text3 = pytesseract.image_to_string(processed_image, config=config3).strip()
                        if text3:
                            results.append(('단일라인', text3))
                        
                        # 설정 4: 단일 단어 설정
                        config4 = r'--oem 3 --psm 8 -l kor+eng'
                        text4 = pytesseract.image_to_string(processed_image, config=config4).strip()
                        if text4:
                            results.append(('단일단어', text4))
                        
                        # 설정 5: 원본 이미지로도 시도
                        config5 = r'--oem 3 --psm 6 -l kor+eng'
                        text5 = pytesseract.image_to_string(image, config=config5).strip()
                        if text5:
                            results.append(('원본이미지', text5))
                        
                        # 가장 긴 결과를 선택 (일반적으로 더 정확함)
                        if results:
                            # 결과들을 길이순으로 정렬
                            results.sort(key=lambda x: len(x[1]), reverse=True)
                            best_result = results[0]
                            text = best_result[1]
                            
                            # 디버그 정보 추가
                            debug_info = f"[{best_result[0]}] "
                        else:
                            text = "텍스트를 인식할 수 없습니다."
                            debug_info = "[실패] "
                        
                        # 결과 정리
                        import re
                        # 연속된 공백 제거
                        text = re.sub(r'\s+', ' ', text.strip())
                        # 특수문자 정리
                        text = re.sub(r'[^\w\s가-힣]', '', text)
                        
                        final_text = debug_info + text if text != "텍스트를 인식할 수 없습니다." else text
                        
                        engine_used = 'Tesseract OCR (고급처리)'
                        result = {
                            "type": "success",
                            "message": final_text,
                            "engine": engine_used
                        }
                    except ImportError:
                        result = {
                            "type": "error",
                            "message": "Tesseract OCR이 설치되지 않았습니다. 설치하려면: pip install pytesseract"
                        }
                    except Exception as e:
                        result = {
                            "type": "error",
                            "message": f"Tesseract OCR 오류: {str(e)}"
                        }
                elif selected_engine == 'naver_clova':
                    try:
                        from ocr_processor import MarketOCRProcessor
                        processor = MarketOCRProcessor(method="naver_clova")  # naver_clova 방법으로 초기화
                        # Naver Clova OCR 처리 - 이미지 데이터를 직접 전달
                        result_dict = processor.process_with_naver_clova_from_data(image_data)
                        text = result_dict.get('text', '') if isinstance(result_dict, dict) else str(result_dict)
                        engine_used = 'Naver Clova OCR'
                        result = {
                            "type": "success",
                            "message": text,
                            "engine": engine_used
                        }
                    except Exception as e:
                        # Naver Clova 실패 시 GPT-4 Vision으로 fallback
                        result = safe_process_image(image_data)
                        if result and result.get('type') == 'success':
                            result['engine'] = 'GPT-4 Vision (fallback)'
                        else:
                            result = {
                                "type": "error",
                                "message": f"Naver Clova OCR 오류: {str(e)}"
                            }
                elif selected_engine == 'pp_ocrv5':
                    try:
                        from ocr_processor import MarketOCRProcessor
                        processor = MarketOCRProcessor(method="pp_ocrv5")
                        # 이미지 데이터를 임시 파일로 저장
                        import tempfile
                        temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
                        os.close(temp_fd)
                        with open(temp_path, 'wb') as f:
                            f.write(image_data)
                        
                        # OCR 처리
                        result_dict = processor.process_image(temp_path)
                        
                        # 임시 파일 삭제
                        os.unlink(temp_path)
                        
                        # 결과 형식 통일
                        if "error" in result_dict:
                            result = {
                                "type": "error",
                                "message": result_dict.get("error", "PP-OCRv5 처리 중 오류 발생")
                            }
                        else:
                            text = result_dict.get("raw_text", "")
                            result = {
                                "type": "success",
                                "message": text,
                                "engine": "PP-OCRv5"
                            }
                    except ImportError:
                        result = {
                            "type": "error",
                            "message": "PaddleOCR이 설치되지 않았습니다.\n\n설치 방법: pip install paddleocr paddlepaddle"
                        }
                    except Exception as e:
                        result = {
                            "type": "error",
                            "message": f"PP-OCRv5 처리 오류: {str(e)}"
                        }
                elif selected_engine == 'sibang_ocr':
                    # Sibang OCR (개발 예정)
                    result = {
                        "type": "error",
                        "message": "🏪 Sibang OCR은 아직 개발 중입니다.\n\n전통시장 특화 OCR 엔진으로 향후 개발 예정입니다.\n\n현재는 GPT-4 Vision 또는 Naver Clova OCR을 사용해주세요."
                    }
                else:
                    # GPT-4 Vision (기본값)
                    result = safe_process_image(image_data)
                    if result and result.get('type') == 'success':
                        result['engine'] = 'GPT-4 Vision'
                        
            except Exception as e:
                result = {
                    "type": "error",
                    "message": f"이미지 처리 중 오류가 발생했습니다: {str(e)}"
                }
            
            return render_template_string(HTML_TEMPLATE, result=result)
            
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, result={
                "type": "error",
                "message": f"Processing error: {str(e)}"
            })
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("🚀 간단한 OCR 웹 서버 시작...")
    print("📱 접속: http://localhost:8081")
    app.run(debug=True, host='0.0.0.0', port=8081)

