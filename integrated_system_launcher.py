#!/usr/bin/env python3
"""
🚀 Integrated System Launcher - Maksymalne Uruchomienie
Uruchamia portal webowy z pełną integracją systemu agentów w jednym procesie
"""
import os
import sys
import time
import threading
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import signal
import atexit

# Dodaj workspace do ścieżki
sys.path.append('/workspace')

# Import komponentów systemu
try:
    from simple_master_coordinator import SimpleMasterCoordinator
    from web_framework_builder import WebFrameworkBuilder
    from security_tools_builder import SecurityToolsBuilder
    from mobile_game_builder import MobileGameBuilder
    print("✅ Wszystkie komponenty agentów zaimportowane!")
except ImportError as e:
    print(f"⚠️ Nie można zaimportować niektórych komponentów: {e}")

# Import portalu webowego
sys.path.append('/workspace/web_portal')

class IntegratedSystemLauncher:
    """Zintegrowany launcher dla całego systemu."""
    
    def __init__(self):
        self.workspace_path = Path('/workspace')
        self.coordinator = None
        self.builders = {}
        self.web_server_thread = None
        self.running = False
        self.setup_logging()
        
        # Przygotuj sygnały do czystego zamknięcia
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        atexit.register(self.cleanup)
        
        print("🚀 Integrated System Launcher zainicjalizowany")
    
    def setup_logging(self):
        """Konfiguracja logowania."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/workspace/web_portal/logs/integrated_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('IntegratedSystem')
    
    def launch_agent_system(self):
        """Uruchomienie systemu agentów."""
        print("🤖 Uruchamianie systemu agentów...")
        
        try:
            # Inicjalizuj Master Coordinator
            self.coordinator = SimpleMasterCoordinator()
            
            # Inicjalizuj wszystkie buildery
            self.builders = {
                'web': WebFrameworkBuilder(),
                'security': SecurityToolsBuilder(),
                'mobile': MobileGameBuilder()
            }
            
            print(f"✅ Master Coordinator uruchomiony z {len(self.coordinator.agents)} agentami")
            print(f"✅ {len(self.builders)} builderów zainicjalizowanych")
            
            # Uruchom koordynację
            self.coordinator.start_coordination()
            
            # Dodaj przykładowe zadania
            self.add_sample_tasks()
            
            return True
            
        except Exception as e:
            print(f"❌ Błąd uruchamiania systemu agentów: {e}")
            self.logger.error(f"Agent system launch failed: {e}")
            return False
    
    def add_sample_tasks(self):
        """Dodanie przykładowych zadań do systemu."""
        print("📋 Dodawanie przykładowych zadań...")
        
        sample_tasks = [
            ('React Dashboard', 'Stwórz nowoczesny dashboard w React', 'code_generation', ['React', 'Dashboard'], 5),
            ('Security Scan', 'Przeprowadź skanowanie bezpieczeństwa', 'security_audit', ['Security'], 4),
            ('Code Review', 'Przeanalizuj kod pod kątem jakości', 'code_analysis', ['Quality'], 3),
            ('API Tests', 'Napisz testy API endpoints', 'testing', ['API', 'Testing'], 3),
            ('User Guide', 'Stwórz przewodnik użytkownika', 'documentation', ['Documentation'], 2)
        ]
        
        for title, description, task_type, requirements, priority in sample_tasks:
            try:
                task_id = self.coordinator.create_task(title, description, task_type, requirements, priority)
                print(f"   ✅ {task_id}: {title}")
            except Exception as e:
                print(f"   ❌ Błąd tworzenia zadania '{title}': {e}")
    
    def start_web_server(self):
        """Uruchomienie serwera webowego z integracją agentów."""
        print("🌐 Uruchamianie zintegrowanego portalu webowego...")
        
        def run_web_server():
            try:
                # Import modułu aplikacji webowej
                from app import application, make_server
                
                # Zaktualizuj globalne zmienne w module app
                import app
                app.AGENT_COORDINATOR = self.coordinator
                app.BUILDERS = self.builders
                app.SYSTEM_READY = True
                
                # Uruchom serwer
                port = int(os.environ.get('PORT', 8000))
                with make_server('0.0.0.0', port, application) as httpd:
                    print(f"🌐 Zintegrowany portal webowy działa na http://0.0.0.0:{port}")
                    print("📊 Dashboard dostępny na: http://localhost:8000/dashboard")
                    print("🤖 Zarządzanie agentami: http://localhost:8000/agents")
                    print("🛠️ Buildery: http://localhost:8000/builders")
                    print("⚙️ Monitor systemu: http://localhost:8000/system")
                    
                    # Oznacz jako działający
                    self.running = True
                    
                    # Uruchom serwer
                    httpd.serve_forever()
                    
            except Exception as e:
                print(f"❌ Błąd serwera webowego: {e}")
                self.logger.error(f"Web server error: {e}")
        
        # Uruchom serwer w osobnym wątku
        self.web_server_thread = threading.Thread(target=run_web_server, daemon=True)
        self.web_server_thread.start()
        
        # Poczekaj na uruchomienie
        time.sleep(2)
        
        return self.running
    
    def display_system_status(self):
        """Wyświetlenie statusu całego systemu."""
        print("\n" + "="*80)
        print("📊 STATUS ZINTEGROWANEGO SYSTEMU AGENTÓW")
        print("="*80)
        
        if self.coordinator:
            status = self.coordinator.get_system_status()
            
            print(f"🤖 AGENTY:")
            print(f"   📊 Wszystkie agenty: {status['total_agents']}")
            print(f"   ⚡ Aktywne agenty: {status['active_agents']}")
            print(f"   🔥 Zajęte agenty: {status['busy_agents']}")
            print(f"   💤 Bezczynne agenty: {status['idle_agents']}")
            
            print(f"\n📋 ZADANIA:")
            print(f"   📊 Wszystkie zadania: {status['total_tasks']}")
            print(f"   ⏳ W kolejce: {status['pending_tasks']}")
            print(f"   ✅ Ukończone: {status['completed_tasks']}")
            
            print(f"\n🛠️ BUILDERY:")
            for name, builder in self.builders.items():
                print(f"   ✅ {name.upper()} Builder - Gotowy")
        
        print(f"\n🌐 PORTAL WEBOWY:")
        if self.running:
            print("   ✅ Portal webowy - Online")
            print("   📊 Dashboard: http://localhost:8000/dashboard")
            print("   🤖 Agents: http://localhost:8000/agents")
            print("   🛠️ Builders: http://localhost:8000/builders")
            print("   ⚙️ System: http://localhost:8000/system")
        else:
            print("   ❌ Portal webowy - Offline")
        
        print("\n🎯 MOŻLIWOŚCI SYSTEMU:")
        print("   • Zarządzanie agentami przez interfejs webowy")
        print("   • Tworzenie aplikacji webowych (React, Vue, Angular)")
        print("   • Generowanie narzędzi bezpieczeństwa")
        print("   • Rozwój gier mobilnych")
        print("   • Automatyczne przetwarzanie zadań")
        print("   • Monitoring w czasie rzeczywistym")
        print("   • API dla zewnętrznych integracji")
        
        print("\n🚀 SYSTEM GOTOWY DO MAKSYMALNEJ PRACY!")
        print("="*80)
    
    def launch_full_system(self):
        """Uruchomienie pełnego zintegrowanego systemu."""
        print("🚀 URUCHAMIANIE MAKSYMALNEGO ZINTEGROWANEGO SYSTEMU")
        print("="*80)
        
        # 1. Uruchom system agentów
        agent_success = self.launch_agent_system()
        if not agent_success:
            print("❌ Nie udało się uruchomić systemu agentów")
            return False
        
        # 2. Uruchom portal webowy z integracją
        web_success = self.start_web_server()
        if not web_success:
            print("❌ Nie udało się uruchomić portalu webowego")
            return False
        
        # 3. Wyświetl status systemu
        time.sleep(1)
        self.display_system_status()
        
        return True
    
    def signal_handler(self, signum, frame):
        """Obsługa sygnałów systemowych."""
        print(f"\n🛑 Otrzymano sygnał {signum}, zamykanie systemu...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Czyszczenie zasobów."""
        print("🧹 Zamykanie systemu...")
        
        if self.coordinator:
            self.coordinator.stop_coordination()
        
        self.running = False
        print("✅ System zamknięty")
    
    def keep_running(self):
        """Utrzymanie systemu w działaniu."""
        try:
            while self.running:
                time.sleep(10)
                
                # Wyświetl okresowy status
                if self.coordinator:
                    status = self.coordinator.get_system_status()
                    print(f"📊 Status: {status['active_agents']} aktywnych agentów, "
                          f"{status['pending_tasks']} zadań w kolejce, "
                          f"{status['completed_tasks']} ukończonych")
                
        except KeyboardInterrupt:
            print("\n🛑 Przerwano przez użytkownika")
            self.cleanup()

def main():
    """Główna funkcja uruchamiająca system."""
    launcher = IntegratedSystemLauncher()
    
    try:
        # Uruchom pełny system
        success = launcher.launch_full_system()
        
        if success:
            print("\n🎉 SYSTEM URUCHOMIONY POMYŚLNIE!")
            print("🌐 Otwórz http://localhost:8000/dashboard w przeglądarce")
            print("⌨️ Naciśnij Ctrl+C aby zatrzymać system")
            
            # Utrzymuj system w działaniu
            launcher.keep_running()
        else:
            print("❌ Nie udało się uruchomić systemu")
            return 1
            
    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")
        launcher.logger.error(f"Critical error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)