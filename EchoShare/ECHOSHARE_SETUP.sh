#!/bin/bash

# EchoShare Complete Setup Script
# This script sets up the complete EchoShare development environment

echo "🚀 EchoShare Complete Setup Script"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Node.js is installed
if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'.' -f1 | sed 's/v//')
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version $NODE_VERSION detected. Please upgrade to Node.js 16+"
    exit 1
fi

echo "✅ Node.js version $(node -v) detected"

# Install project dependencies
echo "📦 Installing project dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create Android SDK setup instructions
echo ""
echo "📱 Setting up Android build environment..."
echo ""
echo "🔧 To build the Android APK, you have several options:"
echo ""
echo "Option 1 - Android Studio (Recommended):"
echo "1. Download Android Studio: https://developer.android.com/studio"
echo "2. Install and open Android Studio"
echo "3. Set ANDROID_HOME to your SDK path (usually ~/Android/Sdk)"
echo "4. Run: ./build-apk.sh"
echo ""
echo "Option 2 - Command Line Tools:"
echo "1. Install Android SDK command line tools"
echo "2. Set ANDROID_HOME environment variable"
echo "3. Run: ./build-apk.sh"
echo ""
echo "Option 3 - Use React Native CLI:"
echo "1. Install React Native CLI: npm install -g @react-native-community/cli"
echo "2. Run: npx react-native run-android"
echo ""

# Create environment setup script
cat > setup-environment.sh << 'EOF'
#!/bin/bash
# Environment Setup Script for EchoShare

echo "Setting up EchoShare development environment..."

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    export ANDROID_HOME=$HOME/Library/Android/sdk
    export JAVA_HOME=/Applications/Android\ Studio.app/Contents/jre/jdk/Contents/Home
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    export ANDROID_HOME=$HOME/Android/Sdk
    export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    export ANDROID_HOME=C:/Users/$USER/AppData/Local/Android/Sdk
    export JAVA_HOME=C:/Program\ Files/Java/jdk-11
fi

export PATH=$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$PATH

echo "Environment variables set:"
echo "ANDROID_HOME=$ANDROID_HOME"
echo "JAVA_HOME=$JAVA_HOME"
echo "PATH includes Android tools"
EOF

chmod +x setup-environment.sh

echo "✅ Setup script created!"
echo "📋 Next steps:"
echo "1. Set up Android development environment"
echo "2. Run: source setup-environment.sh"
echo "3. Run: ./build-apk.sh"
echo "4. Install the generated APK on your device"
echo ""
echo "📖 For detailed instructions, see ANDROID_INSTALLATION.md"
echo "🎯 Happy coding!"

# Show current project status
echo ""
echo "📊 Project Status:"
echo "✅ React Native project created"
echo "✅ Dependencies installed"
echo "✅ Build scripts configured"
echo "⏳ Android SDK setup needed"
echo "⏳ APK generation ready"
echo ""
echo "🔗 Useful links:"
echo "   - Android Studio: https://developer.android.com/studio"
echo "   - React Native docs: https://reactnative.dev/docs/environment-setup"
echo "   - EchoShare GitHub: [Repository Link]"