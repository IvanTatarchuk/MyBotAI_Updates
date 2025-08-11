# 🤖 Agent Programista

**Inteligentny Asystent Programisty z AI** - zaawansowane narzędzie do analizy, generowania i optymalizacji kodu.

## 📋 Spis Treści

- [Funkcjonalności](#-funkcjonalności)
- [Instalacja](#-instalacja)
- [Szybki Start](#-szybki-start)
- [Szczegółowe Użycie](#-szczegółowe-użycie)
- [Konfiguracja](#-konfiguracja)
- [Przykłady](#-przykłady)
- [Obsługiwane Języki](#-obsługiwane-języki)
- [Struktura Projektu](#-struktura-projektu)

## 🚀 Funkcjonalności

### 🔍 Analiza Kodu
- **Analiza składni** - Szczegółowa analiza plików Python z AST
- **Metryki złożoności** - Obliczanie złożoności cyklomatycznej
- **Wykrywanie problemów** - Identyfikacja potencjalnych błędów i code smells
- **Statystyki projektu** - Podsumowanie całego projektu

### 🛠️ Generowanie Kodu
- **Szablony kodu** - Gotowe wzorce dla różnych języków
- **Struktury projektów** - Automatyczne tworzenie szkieletu projektu
- **Dokumentacja** - Generowanie dokumentacji i komentarzy

### 🔧 Refaktoryzacja
- **Sugestie optymalizacji** - Propozycje ulepszeń kodu
- **Wykrywanie duplikatów** - Identyfikacja powtarzającego się kodu
- **Best practices** - Wskazówki zgodne z najlepszymi praktykami

### 📊 Raportowanie
- **Raporty analizy** - Szczegółowe raporty w formacie Markdown
- **Statystyki** - Metryki jakości i złożoności kodu
- **Export danych** - Zapisywanie wyników do plików

## 🔧 Instalacja

### Automatyczna Instalacja

```bash
# Sklonuj repozytorium lub pobierz pliki
git clone <repository_url>
cd agent-programista

# Uruchom skrypt instalacyjny
./setup.sh
```

### Manualna Instalacja

```bash
# Sprawdź wersję Python (wymagany Python 3.8+)
python3 --version

# Opcjonalnie: utwórz środowisko wirtualne
python3 -m venv agent_env
source agent_env/bin/activate  # Linux/macOS
# lub
agent_env\Scripts\activate     # Windows

# Zainstaluj opcjonalne pakiety (jeśli potrzebne)
pip3 install pylint black flake8 mypy pytest

# Nadaj uprawnienia wykonywania
chmod +x programming_agent.py
```

## ⚡ Szybki Start

### 1. Analiza pojedynczego pliku
```bash
python3 programming_agent.py analyze --file moj_skrypt.py
```

### 2. Skanowanie całego projektu
```bash
python3 programming_agent.py scan --path ./moj_projekt
```

### 3. Generowanie szablonu kodu
```bash
python3 programming_agent.py generate --language python --type class
```

### 4. Tworzenie nowego projektu
```bash
python3 programming_agent.py create --name moj_nowy_projekt --type python_package
```

### 5. Generowanie raportu
```bash
python3 programming_agent.py report --output raport.md
```

## 📖 Szczegółowe Użycie

### Analiza Kodu

#### Analiza pojedynczego pliku
```bash
python3 programming_agent.py analyze --file app.py
```

**Wynik:**
- Język programowania
- Liczba linii kodu
- Lista funkcji i klas
- Metryki złożoności
- Wykryte problemy
- Sugestie poprawek

#### Skanowanie projektu
```bash
python3 programming_agent.py scan --path ./projekt
```

**Wynik:**
- Lista wszystkich plików kodu
- Statystyki dla każdego pliku
- Podsumowanie całego projektu

### Generowanie Kodu

#### Dostępne szablony Python:
```bash
# Klasa
python3 programming_agent.py generate --language python --type class

# Funkcja
python3 programming_agent.py generate --language python --type function

# Skrypt
python3 programming_agent.py generate --language python --type script

# Test jednostkowy
python3 programming_agent.py generate --language python --type test
```

#### Dostępne szablony JavaScript:
```bash
# Funkcja
python3 programming_agent.py generate --language javascript --type function

# Klasa
python3 programming_agent.py generate --language javascript --type class

# Moduł
python3 programming_agent.py generate --language javascript --type module
```

### Refaktoryzacja

```bash
# Sugestie wyodrębnienia funkcji
python3 programming_agent.py refactor --file app.py --type extract_function

# Sugestie podziału klasy
python3 programming_agent.py refactor --file models.py --type split_class

# Sugestie optymalizacji
python3 programming_agent.py refactor --file utils.py --type optimize
```

### Wykrywanie Błędów

```bash
python3 programming_agent.py bugs --file problematyczny_plik.py
```

**Agent sprawdza:**
- Puste bloki `except:`
- Pozostawione `print()` statements
- Niepotrzebne porównania z `True/False`
- Niebezpieczne użycie `eval()`
- I wiele więcej...

### Tworzenie Projektów

#### Dostępne typy projektów:

```bash
# Standardowy pakiet Python
python3 programming_agent.py create --name moj_pakiet --type python_package

# Aplikacja webowa
python3 programming_agent.py create --name moja_aplikacja --type web_project

# Projekt Data Science
python3 programming_agent.py create --name analiza_danych --type data_science

# API projekt
python3 programming_agent.py create --name moje_api --type api_project
```

### Raportowanie

```bash
# Podstawowy raport w terminalu
python3 programming_agent.py report

# Zapisanie raportu do pliku
python3 programming_agent.py report --output raport_projektu.md

# Raport konkretnego katalogu
python3 programming_agent.py report --path ./src --output raport_src.md
```

## ⚙️ Konfiguracja

Agent używa pliku `agent_config.json` do konfiguracji. Główne sekcje:

### Ustawienia Agenta
```json
{
  "agent_settings": {
    "cache_enabled": true,
    "max_cache_size": 1000,
    "analysis_timeout": 30
  }
}
```

### Obsługiwane Języki
```json
{
  "supported_languages": {
    "python": {
      "complexity_threshold": 10,
      "max_lines_warning": 500,
      "enable_ast_analysis": true
    }
  }
}
```

### Szabłony Projektów
Możesz dodać własne szablony projektów w sekcji `project_templates`.

## 📚 Przykłady

### Przykład 1: Analiza własnego kodu

```bash
# Analizuj agent programista
python3 programming_agent.py analyze --file programming_agent.py
```

### Przykład 2: Kompletna analiza projektu z raportem

```bash
# Przeskanuj projekt i wygeneruj raport
python3 programming_agent.py scan
python3 programming_agent.py report --output analiza_kompletna.md
```

### Przykład 3: Tworzenie nowego projektu Flask

```bash
# Utwórz nowy projekt webowy
python3 programming_agent.py create --name sklep_online --type web_project

# Przejdź do katalogu
cd sklep_online

# Uruchom aplikację
python3 app.py
```

### Przykład 4: Workflow dla istniejącego projektu

```bash
# 1. Przeskanuj projekt
python3 programming_agent.py scan --path ./moj_projekt

# 2. Znajdź błędy w głównym pliku
python3 programming_agent.py bugs --file ./moj_projekt/main.py

# 3. Sprawdź możliwości refaktoryzacji
python3 programming_agent.py refactor --file ./moj_projekt/main.py --type optimize

# 4. Wygeneruj szczegółowy raport
python3 programming_agent.py report --path ./moj_projekt --output raport_moj_projekt.md
```

## 🌐 Obsługiwane Języki

| Język | Rozszerzenia | Analiza AST | Złożoność |
|-------|-------------|-------------|-----------|
| Python | `.py` | ✅ | ✅ |
| JavaScript | `.js`, `.jsx` | ❌ | ❌ |
| TypeScript | `.ts`, `.tsx` | ❌ | ❌ |
| Java | `.java` | ❌ | ❌ |
| C++ | `.cpp`, `.cc`, `.cxx` | ❌ | ❌ |
| C | `.c` | ❌ | ❌ |
| C# | `.cs` | ❌ | ❌ |
| PHP | `.php` | ❌ | ❌ |
| Ruby | `.rb` | ❌ | ❌ |
| Go | `.go` | ❌ | ❌ |
| Rust | `.rs` | ❌ | ❌ |
| HTML | `.html` | ❌ | ❌ |
| CSS | `.css` | ❌ | ❌ |
| SQL | `.sql` | ❌ | ❌ |
| JSON | `.json` | ❌ | ❌ |
| XML | `.xml` | ❌ | ❌ |
| YAML | `.yaml`, `.yml` | ❌ | ❌ |

**Uwaga:** Dla języków innych niż Python dostępna jest podstawowa analiza (liczba linii, wykrywanie plików).

## 📁 Struktura Projektu

```
agent-programista/
├── programming_agent.py    # Główny skrypt agenta
├── agent_config.json      # Plik konfiguracyjny
├── requirements.txt       # Zależności Python
├── setup.sh              # Skrypt instalacyjny
├── README.md             # Ta dokumentacja
├── version.txt           # Wersja projektu
└── latest_version.txt    # Najnowsza wersja
```

## 🆘 Pomoc i Wsparcie

### Wyświetlenie pomocy
```bash
python3 programming_agent.py --help
```

### Typowe problemy

**Problem:** `Permission denied`
```bash
chmod +x programming_agent.py
```

**Problem:** Brak modułu `ast`
- Moduł `ast` jest częścią standardowej biblioteki Python 3.8+

**Problem:** Błąd dekodowania plików
- Agent automatycznie próbuje dekodować pliki w UTF-8
- Dla innych kodowań może być potrzebne ręczne przekonwertowanie

### Rozszerzanie funkcjonalności

Agent został zaprojektowany jako modularny i łatwy do rozszerzania:

1. **Dodawanie nowych języków:** Dodaj rozszerzenia do `supported_languages`
2. **Nowe szablony:** Rozszerz metodę `generate_code_template()`
3. **Dodatkowe sprawdzenia:** Dodaj reguły do `find_bugs()`
4. **Nowe typy projektów:** Rozszerz `create_project_structure()`

## 📄 Licencja

Ten projekt jest dostępny na licencji open source. Możesz go swobodnie używać, modyfikować i dystrybuować.

## 🙏 Podziękowania

Agent Programista został stworzony jako zaawansowane narzędzie AI do wspomagania programistów w codziennej pracy.

---

**Miłego kodowania! 🚀**