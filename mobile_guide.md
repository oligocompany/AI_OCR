# 📱 모바일 앱 구현 가이드

시장 가판대 OCR 기능을 모바일 앱에 통합하는 방법을 안내합니다.

## 🎯 선택 가능한 방법

### 방법 1: 웹뷰 사용 (가장 간단) ⭐ 추천
Streamlit 웹앱을 모바일 WebView로 감싸기
- **장점**: 빠른 개발, 유지보수 쉬움
- **단점**: 네이티브 기능 제한적

### 방법 2: React Native
크로스 플랫폼 네이티브 앱
- **장점**: iOS + Android 동시 지원, 네이티브 성능
- **단점**: React/JavaScript 지식 필요

### 방법 3: Flutter
Google의 크로스 플랫폼 프레임워크
- **장점**: 빠른 성능, 아름다운 UI
- **단점**: Dart 언어 학습 필요

### 방법 4: 네이티브 개발
Swift (iOS) / Kotlin (Android)
- **장점**: 최고 성능, 모든 기능 활용
- **단점**: 플랫폼별 개발 필요, 시간 소요

---

## 🚀 React Native 예제

### 1. 프로젝트 생성
```bash
npx react-native init MarketOCRApp
cd MarketOCRApp
```

### 2. 필요한 패키지 설치
```bash
npm install axios react-native-image-picker
npm install @react-native-community/camera
```

### 3. 권한 설정

#### iOS (`ios/MarketOCRApp/Info.plist`)
```xml
<key>NSCameraUsageDescription</key>
<string>상품 사진을 촬영하기 위해 카메라 권한이 필요합니다</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>사진을 선택하기 위해 갤러리 권한이 필요합니다</string>
```

#### Android (`android/app/src/main/AndroidManifest.xml`)
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

### 4. React Native 컴포넌트 코드

파일: `App.tsx`
```typescript
import React, { useState } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import axios from 'axios';

// FastAPI 서버 주소 (실제 서버 주소로 변경)
const API_URL = 'http://your-server-ip:8000/ocr';

interface Product {
  product_name: string;
  price: string;
  unit?: string;
}

interface OCRResult {
  products: Product[];
  metadata: {
    method: string;
    total_items: number;
  };
}

const App = () => {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OCRResult | null>(null);

  // 카메라로 사진 촬영
  const handleTakePhoto = () => {
    launchCamera(
      {
        mediaType: 'photo',
        quality: 0.8,
        saveToPhotos: true,
      },
      response => {
        if (response.didCancel) {
          console.log('사용자가 촬영을 취소했습니다.');
        } else if (response.errorCode) {
          Alert.alert('오류', '카메라 실행 실패: ' + response.errorMessage);
        } else if (response.assets && response.assets[0].uri) {
          setImageUri(response.assets[0].uri);
          processOCR(response.assets[0]);
        }
      }
    );
  };

  // 갤러리에서 사진 선택
  const handleSelectPhoto = () => {
    launchImageLibrary(
      {
        mediaType: 'photo',
        quality: 0.8,
      },
      response => {
        if (response.didCancel) {
          console.log('사용자가 선택을 취소했습니다.');
        } else if (response.errorCode) {
          Alert.alert('오류', '갤러리 열기 실패: ' + response.errorMessage);
        } else if (response.assets && response.assets[0].uri) {
          setImageUri(response.assets[0].uri);
          processOCR(response.assets[0]);
        }
      }
    );
  };

  // OCR 처리
  const processOCR = async (asset: any) => {
    setLoading(true);
    setResult(null);

    try {
      // FormData 생성
      const formData = new FormData();
      formData.append('file', {
        uri: asset.uri,
        type: asset.type || 'image/jpeg',
        name: asset.fileName || 'photo.jpg',
      } as any);
      formData.append('method', 'gpt4_vision');

      // API 요청
      const response = await axios.post(API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30초 타임아웃
      });

      if (response.data.success) {
        setResult(response.data.data);
        Alert.alert('성공', `${response.data.data.metadata.total_items}개 상품이 인식되었습니다!`);
      } else {
        Alert.alert('오류', response.data.error || 'OCR 처리 실패');
      }
    } catch (error: any) {
      console.error('OCR 오류:', error);
      Alert.alert('오류', '서버와 통신 중 문제가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🏪 시장 가판대 OCR</Text>
        <Text style={styles.subtitle}>상품 사진을 촬영하세요</Text>
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity 
          style={styles.button} 
          onPress={handleTakePhoto}
          disabled={loading}
        >
          <Text style={styles.buttonText}>📸 사진 촬영</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.button} 
          onPress={handleSelectPhoto}
          disabled={loading}
        >
          <Text style={styles.buttonText}>🖼️ 갤러리</Text>
        </TouchableOpacity>
      </View>

      {imageUri && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: imageUri }} style={styles.image} />
        </View>
      )}

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>분석 중... (약 5-10초 소요)</Text>
        </View>
      )}

      {result && !loading && (
        <ScrollView style={styles.resultContainer}>
          <Text style={styles.resultTitle}>📊 인식 결과</Text>
          
          {result.products.map((product, index) => (
            <View key={index} style={styles.productCard}>
              <Text style={styles.productName}>{product.product_name}</Text>
              <Text style={styles.productPrice}>{product.price}</Text>
              {product.unit && (
                <Text style={styles.productUnit}>단위: {product.unit}</Text>
              )}
            </View>
          ))}

          <View style={styles.summary}>
            <Text style={styles.summaryText}>
              총 {result.metadata.total_items}개 상품
            </Text>
          </View>
        </ScrollView>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    padding: 20,
    backgroundColor: '#007AFF',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  subtitle: {
    fontSize: 14,
    color: 'white',
    marginTop: 5,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 10,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  imageContainer: {
    padding: 20,
    alignItems: 'center',
  },
  image: {
    width: '100%',
    height: 300,
    borderRadius: 10,
    resizeMode: 'contain',
  },
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  resultContainer: {
    flex: 1,
    padding: 20,
  },
  resultTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  productCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },
  productName: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 5,
  },
  productPrice: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  productUnit: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  summary: {
    backgroundColor: '#E8F4FD',
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
    alignItems: 'center',
  },
  summaryText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#007AFF',
  },
});

export default App;
```

### 5. 앱 실행

```bash
# iOS
npx react-native run-ios

# Android
npx react-native run-android
```

---

## 🌐 웹뷰 방법 (가장 간단)

### React Native WebView
```bash
npm install react-native-webview
```

```typescript
import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { WebView } from 'react-native-webview';

const App = () => {
  return (
    <SafeAreaView style={styles.container}>
      <WebView 
        source={{ uri: 'http://your-streamlit-server:8501' }}
        style={styles.webview}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  webview: {
    flex: 1,
  },
});

export default App;
```

---

## 💡 개발 팁

### 1. 서버 배포
- **로컬 테스트**: ngrok 사용 (`ngrok http 8000`)
- **실제 배포**: AWS EC2, Google Cloud Run, Heroku 등

### 2. 이미지 최적화
```javascript
// 이미지 크기 줄이기 (빠른 업로드)
const optimizedImage = await ImageResizer.createResizedImage(
  imageUri,
  1024,  // 최대 너비
  1024,  // 최대 높이
  'JPEG',
  80,    // 품질
);
```

### 3. 오프라인 모드
- 이미지를 로컬에 저장
- 네트워크 연결 시 자동 업로드

### 4. 보안
- HTTPS 사용
- API 키 암호화
- 인증 토큰 추가

---

## 📦 배포 가이드

### iOS App Store
1. Apple Developer 계정 필요 ($99/년)
2. Xcode로 아카이브
3. App Store Connect에 업로드

### Google Play Store
1. Google Play Developer 계정 ($25 일회성)
2. Android Studio로 APK/AAB 빌드
3. Play Console에 업로드

---

## 🆘 문제 해결

### 카메라/갤러리 권한 오류
```bash
# iOS: Podfile 업데이트
cd ios && pod install

# Android: Gradle 동기화
cd android && ./gradlew clean
```

### 네트워크 오류
- 서버 주소 확인 (localhost는 안됨, 실제 IP 사용)
- 방화벽 설정 확인
- CORS 설정 확인

### 빌드 오류
```bash
# 캐시 삭제
rm -rf node_modules
npm install

# iOS 캐시 삭제
cd ios && rm -rf Pods && pod install

# Android 캐시 삭제
cd android && ./gradlew clean
```

---

더 자세한 내용은 공식 문서를 참고하세요:
- [React Native](https://reactnative.dev/)
- [Flutter](https://flutter.dev/)
- [Expo](https://expo.dev/)









