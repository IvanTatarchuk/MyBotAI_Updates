#!/bin/bash
# Super Agent Launcher Startup Script

echo "🚀 Uruchamianie Super Agent System..."

# Sprawdź Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nie jest zainstalowany"
    exit 1
fi

# Przejdź do katalogu projektu
cd "/workspace"

# Uruchom Super Agent Launcher
echo "🤖 Uruchamianie wszystkich agentów..."
python3 super_agent_launcher.py

echo "✅ Super Agent System uruchomiony!"
