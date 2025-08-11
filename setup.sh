#!/bin/bash
# Setup script dla Agent Programista
# Instaluje i konfiguruje środowisko programistyczne

set -e

echo "🤖 Agent Programista - Setup Script"
echo "==================================="

# Sprawdzenie systemu
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="Windows"
else
    PLATFORM="Unknown"
fi

echo "Wykryty system: $PLATFORM"

# Sprawdzenie Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany!"
    echo "Proszę zainstalować Python 3.8 lub nowszy"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python wersja: $PYTHON_VERSION"

# Sprawdzenie pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 nie jest zainstalowany!"
    exit 1
fi

echo "✅ pip3 dostępny"

# Utworzenie środowiska wirtualnego (opcjonalne)
read -p "Czy chcesz utworzyć środowisko wirtualne? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Tworzenie środowiska wirtualnego..."
    python3 -m venv agent_env
    
    if [[ "$PLATFORM" == "Windows" ]]; then
        source agent_env/Scripts/activate
    else
        source agent_env/bin/activate
    fi
    
    echo "✅ Środowisko wirtualne aktywowane"
fi

# Instalacja opcjonalnych pakietów
read -p "Czy chcesz zainstalować dodatkowe pakiety do analizy kodu? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Instalowanie pakietów dodatkowych..."
    
    # Uncomment lines in requirements.txt and install
    sed 's/^# //' requirements.txt > requirements_install.txt
    pip3 install -r requirements_install.txt
    rm requirements_install.txt
    
    echo "✅ Pakiety dodatkowe zainstalowane"
fi

# Nadanie uprawnień wykonywania
chmod +x programming_agent.py

# Utworzenie aliasu (opcjonalne)
read -p "Czy chcesz dodać alias 'agent' do bashrc? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CURRENT_DIR=$(pwd)
    ALIAS_LINE="alias agent='python3 $CURRENT_DIR/programming_agent.py'"
    
    if [[ "$PLATFORM" == "Linux" ]] || [[ "$PLATFORM" == "macOS" ]]; then
        echo "$ALIAS_LINE" >> ~/.bashrc
        echo "✅ Alias 'agent' dodany do ~/.bashrc"
        echo "💡 Uruchom 'source ~/.bashrc' lub otwórz nowy terminal"
    fi
fi

# Test instalacji
echo ""
echo "🧪 Test instalacji..."
python3 programming_agent.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Agent Programista zainstalowany pomyślnie!"
else
    echo "❌ Wystąpił błąd podczas testowania"
    exit 1
fi

# Informacje o użytkowaniu
echo ""
echo "🎉 Setup zakończony!"
echo ""
echo "Sposób użycia:"
echo "  python3 programming_agent.py <komenda> [opcje]"
echo ""
echo "Dostępne komendy:"
echo "  analyze   - Analizuj pojedynczy plik"
echo "  scan      - Skanuj cały projekt"
echo "  generate  - Generuj szablon kodu"
echo "  refactor  - Sugestie refaktoryzacji"
echo "  bugs      - Znajdź potencjalne błędy"
echo "  create    - Utwórz nowy projekt"
echo "  report    - Wygeneruj raport projektu"
echo ""
echo "Przykłady:"
echo "  python3 programming_agent.py scan"
echo "  python3 programming_agent.py analyze --file my_script.py"
echo "  python3 programming_agent.py generate --language python --type class"
echo "  python3 programming_agent.py create --name my_project --type python_package"
echo ""
echo "Więcej informacji: python3 programming_agent.py --help"