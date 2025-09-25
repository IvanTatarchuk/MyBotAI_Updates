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