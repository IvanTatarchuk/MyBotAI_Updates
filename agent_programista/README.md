# Agent Programista (CLI)

Lekki agent programistyczny do automatyzacji prostych zadań w repozytorium:
- planowanie kroków,
- uruchamianie testów,
- wykonywanie komend powłoki,
- edycja plików według specyfikacji YAML,
- commitowanie zmian i (opcjonalne) push.

## Instalacja

```bash
cd /workspace/agent_programista
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Użycie

- Inicjalizacja pliku konfiguracyjnego:
  ```bash
  python -m agent_programista init
  ```

- Uruchomienie agenta dla zadania (z tworzeniem brancha, testami i commitami):
  ```bash
  python -m agent_programista run --task "Napraw testy w projekcie"
  ```

- Tylko plan (bez wykonywania):
  ```bash
  python -m agent_programista plan --task "Zaktualizuj zależności"
  ```

- Edycja plików przez specyfikację YAML (przykład poniżej):
  ```bash
  python -m agent_programista edit --spec edits.yml
  ```

- Ręczne uruchomienie testów przez wykryty runner:
  ```bash
  python -m agent_programista test
  ```

## Specyfikacja edycji (YAML)

```yaml
edits:
  - path: "README.md"
    action: "append"            # create | append | replace_exact
    content: "\nNowa sekcja...\n"
  - path: "app/main.py"
    action: "create"
    content: |
      def hello():
          return "world"
  - path: "app/config.py"
    action: "replace_exact"
    find: "DEBUG = True"
    replace: "DEBUG = False"
```

## Uwaga
Agent działa zachowawczo: jeżeli nie znajdzie repozytorium Git, spróbuje je zainicjalizować w katalogu roboczym. Push wykona tylko, gdy istnieje zdefiniowany `origin`.