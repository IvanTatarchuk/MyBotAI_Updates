# 📱 EchoShare Android Installation Guide

This guide explains how to build and install the EchoShare app on Android devices.

## 🚀 Quick Start

### Option 1: Using the Build Script (Recommended)

1. **Open terminal** in the EchoShare project directory
2. **Run the build script**:
   ```bash
   ./build-apk.sh
   ```
3. **Find the APK** in the generated location
4. **Install on your Android device**

### Option 2: Manual Build

If you prefer to build manually or have issues with the script:

```bash
# 1. Install dependencies
npm install

# 2. Clean previous builds
cd android
./gradlew clean

# 3. Build debug APK (for development)
./gradlew assembleDebug

# 4. Build release APK (for production)
./gradlew assembleRelease
```

## 📋 Prerequisites

### Required Software

1. **Node.js** (v16 or higher)
   - Download: https://nodejs.org/

2. **Android SDK**
   - Install via **Android Studio** (recommended)
   - Or install **command line tools** only

3. **Java Development Kit (JDK)**
   - JDK 11 or higher
   - Set `JAVA_HOME` environment variable

### Environment Setup

#### Windows
```bash
# Set Android SDK path (adjust to your installation)
set ANDROID_HOME=C:\Users\YourUserName\AppData\Local\Android\Sdk
set JAVA_HOME=C:\Program Files\Java\jdk-11

# Add to PATH
set PATH=%ANDROID_HOME%\tools;%ANDROID_HOME%\platform-tools;%PATH%
```

#### macOS/Linux
```bash
# Set Android SDK path (adjust to your installation)
export ANDROID_HOME=/Users/yourusername/Library/Android/sdk
export JAVA_HOME=/Applications/Android\ Studio.app/Contents/jre/jdk/Contents/Home

# Add to PATH
export PATH=$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$PATH
```

## 🔧 Installation on Android Device

### Step 1: Enable Unknown Sources

1. **Go to Settings** on your Android device
2. **Navigate to Security** (or Privacy & Security)
3. **Enable "Install from Unknown Sources"**
   - This allows installation of apps not from Google Play Store

### Step 2: Transfer APK to Device

**Method 1: USB Transfer**
1. Connect your Android device to computer via USB
2. Enable **File Transfer** mode on your device
3. Copy the APK file to your device's Downloads folder

**Method 2: Email/Download**
1. Email the APK file to yourself
2. Download it directly on your Android device

**Method 3: Cloud Storage**
1. Upload APK to Google Drive, Dropbox, etc.
2. Download from your Android device

### Step 3: Install the App

1. **Open File Manager** on your Android device
2. **Navigate to Downloads** folder (or where you saved the APK)
3. **Tap the APK file** (`app-release.apk` or `app-debug.apk`)
4. **Follow installation prompts**
5. **Tap "Install"** when prompted
6. **Wait for installation** to complete

### Step 4: Launch the App

1. **Find EchoShare** in your app drawer
2. **Tap the EchoShare icon** to launch
3. **Grant permissions** if prompted
4. **Start using the app!**

## 🛠 Troubleshooting

### Build Issues

**Problem**: "SDK location not found"
```
Solution: Set ANDROID_HOME environment variable
- Windows: set ANDROID_HOME=C:\path\to\android\sdk
- macOS/Linux: export ANDROID_HOME=/path/to/android/sdk
```

**Problem**: "Java JDK not found"
```
Solution: Install JDK 11+ and set JAVA_HOME
- Download: https://adoptium.net/
- Set JAVA_HOME to JDK installation path
```

**Problem**: Permission denied errors
```
Solution: Make sure build script is executable
chmod +x build-apk.sh
```

### Installation Issues

**Problem**: "App not installed"
```
Solution:
1. Check if "Unknown Sources" is enabled
2. Ensure you have enough storage space
3. Try restarting your device
4. Clear Google Play Store cache
```

**Problem**: "Parse error"
```
Solution:
1. APK file may be corrupted - rebuild
2. Check if your device supports the APK version
3. Ensure minimum Android version is met (Android 7.0+)
```

**Problem**: App crashes on launch
```
Solution:
1. Check device compatibility
2. Ensure all permissions are granted
3. Try clearing app data (Settings > Apps > EchoShare > Storage > Clear Data)
4. Reinstall the app
```

## 📊 APK Information

### Debug APK (Development)
- **File name**: `app-debug.apk`
- **Size**: ~50-100MB
- **Features**: Includes debugging capabilities
- **Use for**: Development and testing

### Release APK (Production)
- **File name**: `app-release.apk`
- **Size**: ~20-50MB (optimized)
- **Features**: Optimized, minified, signed
- **Use for**: Final distribution

## 🔒 Security Notes

- **Only install APK files** from trusted sources
- **Verify file integrity** before installation
- **Keep "Unknown Sources" disabled** when not installing apps
- **The provided APK is signed** with EchoShare's release certificate

## 📱 Device Compatibility

### Minimum Requirements
- **Android Version**: 7.0 (API 24) or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB free space
- **Screen**: Any resolution supported

### Recommended Devices
- Samsung Galaxy S8+
- Google Pixel 2+
- OnePlus 6+
- Huawei P20+
- Any modern Android device

## 🚨 Important Notes

1. **First Launch**: The app may take longer to start on first launch as it initializes
2. **Internet Required**: EchoShare requires internet connection for real-time data
3. **Permissions**: Grant all requested permissions for full functionality
4. **Updates**: Check for updates regularly for new features and bug fixes

## 📞 Support

If you encounter issues:
1. Check this installation guide
2. Verify your Android SDK setup
3. Ensure all prerequisites are met
4. Contact development team if issues persist

---

**Happy investing with EchoShare!** 🚀📈