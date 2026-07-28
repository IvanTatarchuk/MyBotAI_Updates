#!/bin/bash

# EchoShare APK Build Script
# This script builds the EchoShare Android application

echo "🚀 EchoShare APK Build Script"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the EchoShare project root directory"
    exit 1
fi

echo "📱 Setting up Android build environment..."

# Check if Android SDK is available
if [ -z "$ANDROID_HOME" ]; then
    echo "⚠️  Warning: ANDROID_HOME not set. Please ensure Android SDK is installed."
    echo "   You can install it via Android Studio or command line tools."
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
cd android
./gradlew clean

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to clean project. Please check your Android SDK installation."
    echo "   Make sure you have Android SDK installed and ANDROID_HOME set correctly."
    exit 1
fi

echo "🔨 Building APK..."

# Build debug APK first
echo "📦 Building debug APK..."
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo "✅ Debug APK built successfully!"
    echo "📍 Location: android/app/build/outputs/apk/debug/app-debug.apk"

    # Build release APK
    echo "📦 Building release APK..."
    ./gradlew assembleRelease

    if [ $? -eq 0 ]; then
        echo "✅ Release APK built successfully!"
        echo "📍 Location: android/app/build/outputs/apk/release/app-release.apk"
        echo ""
        echo "🎉 Build completed successfully!"
        echo ""
        echo "📋 Installation Instructions:"
        echo "1. Transfer the APK file to your Android device"
        echo "2. Enable 'Install from Unknown Sources' in Settings > Security"
        echo "3. Use a file manager to locate and tap the APK file"
        echo "4. Follow the installation prompts"
        echo ""
        echo "🔧 For development:"
        echo "- Debug APK: Allows debugging with Android Studio"
        echo "- Release APK: Optimized for production, smaller size"
    else
        echo "⚠️  Release build failed, but debug APK was built successfully."
        echo "📍 Debug APK location: android/app/build/outputs/apk/debug/app-debug.apk"
    fi
else
    echo "❌ Build failed. Please check the following:"
    echo "   1. Android SDK is installed"
    echo "   2. ANDROID_HOME environment variable is set"
    echo "   3. All dependencies are installed (npm install)"
    echo "   4. Android Studio or Android SDK command line tools are available"
    echo ""
    echo "🔧 Quick setup guide:"
    echo "   1. Install Android Studio: https://developer.android.com/studio"
    echo "   2. Set ANDROID_HOME to your Android SDK path"
    echo "   3. Run: export ANDROID_HOME=/path/to/android/sdk"
    exit 1
fi

cd ..
echo "✅ Build script completed!"