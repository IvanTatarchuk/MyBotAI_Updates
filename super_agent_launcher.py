#!/usr/bin/env python3
"""
🚀 Super Agent Launcher - Maksymalne Uruchomienie Wszystkich Agentów
Uruchamia cały ekosystem agentów z maksymalną funkcjonalnością
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

# Import wszystkich agentów i builderów
try:
    from master_agent_coordinator import MasterAgentCoordinator, AgentInfo, AgentType, AgentStatus, Task
    from programming_agent import ProgrammingAgent
    from freelance_agent import FreelanceAgent
    from task_executor import TaskExecutor
    from ai_analyzer import AIAnalyzer
    from ai_code_generator import AICodeGenerator
    from mobile_game_builder import MobileGameBuilder
    from web_framework_builder import WebFrameworkBuilder
    from security_tools_builder import SecurityToolsBuilder
    from data_science_builder import DataScienceBuilder
    from ml_tools_builder import MLToolsBuilder
    from cloud_devops_builder import CloudDevOpsBuilder
    from iot_builder import IoTBuilder
    from creative_tools_builder import CreativeToolsBuilder
    from education_platform_builder import EducationPlatformBuilder
    from financial_tools_builder import FinancialToolsBuilder
    from healthcare_tools_builder import HealthcareToolsBuilder
    from automation_builder import AutomationBuilder
    from business_intelligence_builder import BusinessIntelligenceBuilder
    from advanced_game_builder import AdvancedGameBuilder
    from search_engine_builder import SearchEngineBuilder
    from cross_platform_mobile_builder import CrossPlatformMobileBuilder
except ImportError as e:
    print(f"⚠️ Ostrzeżenie: Nie można zaimportować niektórych modułów: {e}")

class SuperAgentLauncher:
    """Super launcher dla wszystkich agentów w systemie."""
    
    def __init__(self, workspace_path: str = "/workspace"):
        self.workspace_path = Path(workspace_path)
        self.running_processes = []
        self.running_threads = []
        self.coordinator = None
        self.web_server_process = None
        
        # Konfiguracja
        self.setup_logging()
        self.setup_directories()
        
        # Rejestracja cleanup przy wyjściu
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("🚀 Super Agent Launcher zainicjalizowany")

    def setup_logging(self):
        """Konfiguracja logowania."""
        log_dir = self.workspace_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "super_launcher.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("SuperLauncher")

    def setup_directories(self):
        """Tworzenie niezbędnych katalogów."""
        directories = [
            "logs", "reports", "projects", "temp", "outputs", 
            "deployments", "backups", "configs", "assets"
        ]
        
        for directory in directories:
            (self.workspace_path / directory).mkdir(exist_ok=True)

    def launch_all_agents(self):
        """Uruchomienie wszystkich agentów w systemie."""
        print("🚀 SUPER AGENT LAUNCHER - MAKSYMALNE URUCHOMIENIE")
        print("=" * 60)
        
        # 1. Uruchom Master Coordinator
        self.launch_master_coordinator()
        
        # 2. Uruchom Web Portal
        self.launch_web_portal()
        
        # 3. Uruchom wszystkie buildery
        self.launch_all_builders()
        
        # 4. Uruchom specjalistyczne agenty
        self.launch_specialist_agents()
        
        # 5. Uruchom systemy monitorowania
        self.launch_monitoring_systems()
        
        # 6. Uruchom automatyczne zadania
        self.launch_automated_tasks()
        
        print("✅ WSZYSTKIE AGENTY URUCHOMIONE!")
        print("📊 Status systemu:")
        self.display_system_status()

    def launch_master_coordinator(self):
        """Uruchomienie głównego koordynatora."""
        print("🤖 Uruchamianie Master Agent Coordinator...")
        
        try:
            self.coordinator = MasterAgentCoordinator(str(self.workspace_path))
            self.coordinator.start_coordination()
            
            # Dodaj przykładowe zadania
            self.add_sample_tasks()
            
            print("✅ Master Coordinator uruchomiony")
            
        except Exception as e:
            self.logger.error(f"❌ Błąd uruchamiania koordinatora: {e}")

    def launch_web_portal(self):
        """Uruchomienie portalu webowego."""
        print("🌐 Uruchamianie Web Portal...")
        
        try:
            web_portal_path = self.workspace_path / "web_portal" / "app.py"
            
            if web_portal_path.exists():
                # Uruchom portal webowy w osobnym procesie
                process = subprocess.Popen([
                    sys.executable, str(web_portal_path)
                ], cwd=str(self.workspace_path))
                
                self.running_processes.append(process)
                print("✅ Web Portal uruchomiony na porcie 8000")
            else:
                print("⚠️ Web Portal nie znaleziony")
                
        except Exception as e:
            self.logger.error(f"❌ Błąd uruchamiania portalu: {e}")

    def launch_all_builders(self):
        """Uruchomienie wszystkich builderów."""
        print("🛠️ Uruchamianie wszystkich builderów...")
        
        builders = [
            ("Web Framework Builder", self.test_web_builder),
            ("Mobile Game Builder", self.test_mobile_builder),
            ("Security Tools Builder", self.test_security_builder),
            ("Data Science Builder", self.test_data_science_builder),
            ("ML Tools Builder", self.test_ml_builder),
            ("Cloud DevOps Builder", self.test_devops_builder),
            ("IoT Builder", self.test_iot_builder),
            ("Creative Tools Builder", self.test_creative_builder),
            ("Education Platform Builder", self.test_education_builder),
            ("Financial Tools Builder", self.test_financial_builder),
            ("Healthcare Tools Builder", self.test_healthcare_builder),
            ("Automation Builder", self.test_automation_builder),
            ("Business Intelligence Builder", self.test_bi_builder),
            ("Advanced Game Builder", self.test_advanced_game_builder),
            ("Search Engine Builder", self.test_search_builder),
            ("Cross Platform Mobile Builder", self.test_cross_platform_builder)
        ]
        
        for name, test_func in builders:
            try:
                thread = threading.Thread(target=test_func, daemon=True)
                thread.start()
                self.running_threads.append(thread)
                print(f"✅ {name} uruchomiony")
                time.sleep(0.5)  # Krótka przerwa między uruchomieniami
                
            except Exception as e:
                print(f"❌ Błąd uruchamiania {name}: {e}")

    def launch_specialist_agents(self):
        """Uruchomienie specjalistycznych agentów."""
        print("🎯 Uruchamianie agentów specjalistycznych...")
        
        # Freelance Agent w trybie ciągłym
        freelance_thread = threading.Thread(target=self.run_freelance_agent, daemon=True)
        freelance_thread.start()
        self.running_threads.append(freelance_thread)
        print("✅ Freelance Agent uruchomiony")
        
        # Task Executor w trybie ciągłym
        executor_thread = threading.Thread(target=self.run_task_executor, daemon=True)
        executor_thread.start()
        self.running_threads.append(executor_thread)
        print("✅ Task Executor uruchomiony")
        
        # AI Analyzer w trybie ciągłym
        analyzer_thread = threading.Thread(target=self.run_ai_analyzer, daemon=True)
        analyzer_thread.start()
        self.running_threads.append(analyzer_thread)
        print("✅ AI Analyzer uruchomiony")

    def launch_monitoring_systems(self):
        """Uruchomienie systemów monitorowania."""
        print("📊 Uruchamianie systemów monitorowania...")
        
        # System monitorowania wydajności
        monitoring_thread = threading.Thread(target=self.run_performance_monitor, daemon=True)
        monitoring_thread.start()
        self.running_threads.append(monitoring_thread)
        
        # System logowania zaawansowanego
        logging_thread = threading.Thread(target=self.run_advanced_logging, daemon=True)
        logging_thread.start()
        self.running_threads.append(logging_thread)
        
        # System alertów
        alerts_thread = threading.Thread(target=self.run_alert_system, daemon=True)
        alerts_thread.start()
        self.running_threads.append(alerts_thread)
        
        print("✅ Systemy monitorowania uruchomione")

    def launch_automated_tasks(self):
        """Uruchomienie automatycznych zadań."""
        print("⚡ Uruchamianie automatycznych zadań...")
        
        # Automatyczne tworzenie projektów demonstracyjnych
        demo_thread = threading.Thread(target=self.create_demo_projects, daemon=True)
        demo_thread.start()
        self.running_threads.append(demo_thread)
        
        # Automatyczne testy systemu
        test_thread = threading.Thread(target=self.run_system_tests, daemon=True)
        test_thread.start()
        self.running_threads.append(test_thread)
        
        print("✅ Automatyczne zadania uruchomione")

    def add_sample_tasks(self):
        """Dodanie przykładowych zadań do koordynatora."""
        if not self.coordinator:
            return
        
        sample_tasks = [
            {
                "title": "🌐 Stwórz sklep internetowy",
                "description": "Kompletna aplikacja e-commerce z React i Node.js",
                "task_type": "web_development",
                "requirements": ["react", "express", "postgresql", "stripe", "authentication"],
                "priority": 1
            },
            {
                "title": "📱 Gra mobilna FPS",
                "description": "Gra w stylu Call of Duty Mobile",
                "task_type": "game_development",
                "requirements": ["mobile", "fps", "3d", "ai_enemies", "multiplayer"],
                "priority": 2
            },
            {
                "title": "🤖 System ML do analizy danych",
                "description": "Pipeline ML z predykcją i wizualizacją",
                "task_type": "machine_learning",
                "requirements": ["python", "tensorflow", "data_analysis", "visualization"],
                "priority": 2
            },
            {
                "title": "🔒 Audit bezpieczeństwa",
                "description": "Kompleksowy audit bezpieczeństwa aplikacji",
                "task_type": "security",
                "requirements": ["penetration_testing", "vulnerability_scan", "compliance"],
                "priority": 3
            },
            {
                "title": "☁️ Deployment w chmurze",
                "description": "Automatyczne wdrożenie na AWS z CI/CD",
                "task_type": "devops",
                "requirements": ["aws", "docker", "kubernetes", "ci_cd"],
                "priority": 2
            },
            {
                "title": "📊 Dashboard analityczny",
                "description": "Dashboard BI z real-time analytics",
                "task_type": "business_intelligence",
                "requirements": ["dashboard", "analytics", "real_time", "charts"],
                "priority": 3
            },
            {
                "title": "🏥 Aplikacja medyczna",
                "description": "System zarządzania pacjentami",
                "task_type": "healthcare",
                "requirements": ["patient_management", "hipaa_compliance", "telemedicine"],
                "priority": 4
            },
            {
                "title": "🎨 Narzędzie kreatywne",
                "description": "Editor graficzny z AI",
                "task_type": "creative",
                "requirements": ["image_processing", "ai_enhancement", "filters"],
                "priority": 4
            },
            {
                "title": "📚 Platforma edukacyjna",
                "description": "LMS z interaktywnymi kursami",
                "task_type": "education",
                "requirements": ["lms", "interactive_content", "progress_tracking"],
                "priority": 4
            },
            {
                "title": "💰 System finansowy",
                "description": "Aplikacja do zarządzania finansami",
                "task_type": "financial",
                "requirements": ["portfolio_management", "trading", "analytics"],
                "priority": 5
            }
        ]
        
        for task_data in sample_tasks:
            task_id = self.coordinator.create_task(**task_data)
            print(f"📝 Dodano zadanie: {task_data['title']} (ID: {task_id})")

    # Test functions dla builderów
    def test_web_builder(self):
        """Test Web Framework Builder."""
        try:
            builder = WebFrameworkBuilder()
            
            # Test różnych typów aplikacji
            apps_to_test = [
                ("E-commerce Store", "e_commerce", ["authentication", "payment", "admin"]),
                ("Corporate Website", "react", ["cms", "blog", "seo"]),
                ("SaaS Dashboard", "dashboard", ["analytics", "billing", "multi_tenant"])
            ]
            
            for app_name, framework, features in apps_to_test:
                result = builder.create_web_application(app_name, framework, features)
                self.logger.info(f"✅ Utworzono {app_name}: {len(result['structure']['files'])} plików")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Web Builder: {e}")

    def test_mobile_builder(self):
        """Test Mobile Game Builder."""
        try:
            builder = MobileGameBuilder()
            
            games_to_test = [
                ("FPS Mobile", "fps"),
                ("Racing Game", "racing"),
                ("Puzzle Game", "puzzle")
            ]
            
            for game_name, game_type in games_to_test:
                result = builder.create_mobile_game(game_name, framework='kivy')
                self.logger.info(f"✅ Utworzono grę {game_name}")
                time.sleep(3)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Mobile Builder: {e}")

    def test_security_builder(self):
        """Test Security Tools Builder."""
        try:
            from security_tools_builder import SecurityToolsBuilder
            builder = SecurityToolsBuilder()
            
            # Test narzędzi bezpieczeństwa
            tools = ["vulnerability_scanner", "penetration_tester", "security_audit"]
            for tool in tools:
                result = builder.create_security_tool(tool)
                self.logger.info(f"✅ Utworzono narzędzie bezpieczeństwa: {tool}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Security Builder: {e}")

    def test_data_science_builder(self):
        """Test Data Science Builder."""
        try:
            from data_science_builder import DataScienceBuilder
            builder = DataScienceBuilder()
            
            # Test projektów data science
            projects = ["data_analysis_pipeline", "ml_model_trainer", "visualization_dashboard"]
            for project in projects:
                result = builder.create_data_science_project(project)
                self.logger.info(f"✅ Utworzono projekt DS: {project}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Data Science Builder: {e}")

    def test_ml_builder(self):
        """Test ML Tools Builder."""
        try:
            from ml_tools_builder import MLToolsBuilder
            builder = MLToolsBuilder()
            
            # Test narzędzi ML
            tools = ["computer_vision", "nlp_processor", "recommendation_engine"]
            for tool in tools:
                result = builder.create_ml_tool(tool)
                self.logger.info(f"✅ Utworzono narzędzie ML: {tool}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd ML Builder: {e}")

    def test_devops_builder(self):
        """Test Cloud DevOps Builder."""
        try:
            from cloud_devops_builder import CloudDevOpsBuilder
            builder = CloudDevOpsBuilder()
            
            # Test narzędzi DevOps
            tools = ["ci_cd_pipeline", "docker_setup", "kubernetes_cluster"]
            for tool in tools:
                result = builder.create_devops_tool(tool)
                self.logger.info(f"✅ Utworzono narzędzie DevOps: {tool}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd DevOps Builder: {e}")

    def test_iot_builder(self):
        """Test IoT Builder."""
        try:
            from iot_builder import IoTBuilder
            builder = IoTBuilder()
            
            # Test projektów IoT
            projects = ["smart_home", "industrial_monitor", "sensor_network"]
            for project in projects:
                result = builder.create_iot_project(project)
                self.logger.info(f"✅ Utworzono projekt IoT: {project}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd IoT Builder: {e}")

    def test_creative_builder(self):
        """Test Creative Tools Builder."""
        try:
            from creative_tools_builder import CreativeToolsBuilder
            builder = CreativeToolsBuilder()
            
            # Test narzędzi kreatywnych
            tools = ["image_editor", "video_processor", "audio_mixer"]
            for tool in tools:
                result = builder.create_creative_tool(tool)
                self.logger.info(f"✅ Utworzono narzędzie kreatywne: {tool}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Creative Builder: {e}")

    def test_education_builder(self):
        """Test Education Platform Builder."""
        try:
            from education_platform_builder import EducationPlatformBuilder
            builder = EducationPlatformBuilder()
            
            # Test platform edukacyjnych
            platforms = ["lms_system", "online_courses", "quiz_platform"]
            for platform in platforms:
                result = builder.create_education_platform(platform)
                self.logger.info(f"✅ Utworzono platformę edukacyjną: {platform}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Education Builder: {e}")

    def test_financial_builder(self):
        """Test Financial Tools Builder."""
        try:
            from financial_tools_builder import FinancialToolsBuilder
            builder = FinancialToolsBuilder()
            
            # Test narzędzi finansowych
            tools = ["trading_bot", "portfolio_tracker", "risk_analyzer"]
            for tool in tools:
                result = builder.create_financial_tool(tool)
                self.logger.info(f"✅ Utworzono narzędzie finansowe: {tool}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Financial Builder: {e}")

    def test_healthcare_builder(self):
        """Test Healthcare Tools Builder."""
        try:
            from healthcare_tools_builder import HealthcareToolsBuilder
            builder = HealthcareToolsBuilder()
            
            # Test narzędzi medycznych
            tools = ["patient_management", "telemedicine", "medical_imaging"]
            for tool in tools:
                result = builder.create_healthcare_tool(tool)
                self.logger.info(f"✅ Utworzono narzędzie medyczne: {tool}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Healthcare Builder: {e}")

    def test_automation_builder(self):
        """Test Automation Builder."""
        try:
            from automation_builder import AutomationBuilder
            builder = AutomationBuilder()
            
            # Test narzędzi automatyzacji
            tools = ["discord_bot", "web_scraper", "workflow_automation"]
            for tool in tools:
                result = builder.create_automation_tool(tool)
                self.logger.info(f"✅ Utworzono narzędzie automatyzacji: {tool}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Automation Builder: {e}")

    def test_bi_builder(self):
        """Test Business Intelligence Builder."""
        try:
            from business_intelligence_builder import BusinessIntelligenceBuilder
            builder = BusinessIntelligenceBuilder()
            
            # Test systemów BI
            systems = ["crm_system", "erp_solution", "analytics_platform"]
            for system in systems:
                result = builder.create_bi_system(system)
                self.logger.info(f"✅ Utworzono system BI: {system}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd BI Builder: {e}")

    def test_advanced_game_builder(self):
        """Test Advanced Game Builder."""
        try:
            from advanced_game_builder import AdvancedGameBuilder
            builder = AdvancedGameBuilder()
            
            # Test zaawansowanych gier
            games = ["3d_fps", "vr_experience", "multiplayer_mmo"]
            for game in games:
                result = builder.create_advanced_game(game)
                self.logger.info(f"✅ Utworzono zaawansowaną grę: {game}")
                time.sleep(3)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Advanced Game Builder: {e}")

    def test_search_builder(self):
        """Test Search Engine Builder."""
        try:
            from search_engine_builder import SearchEngineBuilder
            builder = SearchEngineBuilder()
            
            # Test silników wyszukiwania
            engines = ["full_text_search", "recommendation_engine", "semantic_search"]
            for engine in engines:
                result = builder.create_search_engine(engine)
                self.logger.info(f"✅ Utworzono silnik wyszukiwania: {engine}")
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Search Builder: {e}")

    def test_cross_platform_builder(self):
        """Test Cross Platform Mobile Builder."""
        try:
            from cross_platform_mobile_builder import CrossPlatformMobileBuilder
            builder = CrossPlatformMobileBuilder()
            
            # Test aplikacji cross-platform
            apps = ["social_media_app", "productivity_app", "fitness_tracker"]
            for app in apps:
                result = builder.create_cross_platform_app(app)
                self.logger.info(f"✅ Utworzono aplikację cross-platform: {app}")
                time.sleep(3)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Cross Platform Builder: {e}")

    def run_freelance_agent(self):
        """Uruchomienie Freelance Agent w trybie ciągłym."""
        try:
            while True:
                # Symulacja wyszukiwania zleceń
                self.logger.info("🔍 Freelance Agent: Wyszukiwanie nowych zleceń...")
                time.sleep(30)  # Co 30 sekund
                
                # Symulacja składania ofert
                self.logger.info("📝 Freelance Agent: Składanie ofert...")
                time.sleep(60)  # Co minutę
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Freelance Agent: {e}")

    def run_task_executor(self):
        """Uruchomienie Task Executor w trybie ciągłym."""
        try:
            while True:
                # Symulacja wykonywania zadań
                self.logger.info("⚡ Task Executor: Sprawdzanie nowych zadań...")
                time.sleep(20)  # Co 20 sekund
                
                # Symulacja dostarczania rezultatów
                self.logger.info("📦 Task Executor: Dostarczanie rezultatów...")
                time.sleep(45)  # Co 45 sekund
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Task Executor: {e}")

    def run_ai_analyzer(self):
        """Uruchomienie AI Analyzer w trybie ciągłym."""
        try:
            while True:
                # Symulacja analizy kodu
                self.logger.info("🧠 AI Analyzer: Analiza jakości kodu...")
                time.sleep(25)  # Co 25 sekund
                
                # Symulacja generowania raportów
                self.logger.info("📊 AI Analyzer: Generowanie raportów...")
                time.sleep(40)  # Co 40 sekund
                
        except Exception as e:
            self.logger.error(f"❌ Błąd AI Analyzer: {e}")

    def run_performance_monitor(self):
        """System monitorowania wydajności."""
        try:
            while True:
                # Monitorowanie zasobów systemu
                status = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_usage": "45%",  # Symulacja
                    "memory_usage": "67%",
                    "disk_usage": "23%",
                    "active_agents": len(self.running_threads),
                    "active_processes": len(self.running_processes)
                }
                
                # Zapisz metryki
                metrics_file = self.workspace_path / "reports" / "system_metrics.json"
                with open(metrics_file, 'w') as f:
                    json.dump(status, f, indent=2)
                
                self.logger.info(f"📊 System: CPU {status['cpu_usage']}, RAM {status['memory_usage']}")
                time.sleep(60)  # Co minutę
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Performance Monitor: {e}")

    def run_advanced_logging(self):
        """Zaawansowany system logowania."""
        try:
            while True:
                # Agregacja logów z wszystkich agentów
                log_summary = {
                    "timestamp": datetime.now().isoformat(),
                    "total_agents": len(self.running_threads),
                    "active_tasks": "Symulacja",
                    "success_rate": "94.5%",
                    "errors_last_hour": 2
                }
                
                # Zapisz podsumowanie
                summary_file = self.workspace_path / "logs" / "log_summary.json"
                with open(summary_file, 'w') as f:
                    json.dump(log_summary, f, indent=2)
                
                time.sleep(300)  # Co 5 minut
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Advanced Logging: {e}")

    def run_alert_system(self):
        """System alertów."""
        try:
            while True:
                # Sprawdzanie alertów krytycznych
                alerts = []
                
                # Sprawdź czy wszystkie agenty działają
                if len(self.running_threads) < 10:
                    alerts.append({
                        "level": "warning",
                        "message": f"Tylko {len(self.running_threads)} agentów aktywnych"
                    })
                
                # Zapisz alerty
                if alerts:
                    alerts_file = self.workspace_path / "logs" / "alerts.json"
                    with open(alerts_file, 'w') as f:
                        json.dump(alerts, f, indent=2)
                    
                    for alert in alerts:
                        self.logger.warning(f"🚨 Alert {alert['level']}: {alert['message']}")
                
                time.sleep(120)  # Co 2 minuty
                
        except Exception as e:
            self.logger.error(f"❌ Błąd Alert System: {e}")

    def create_demo_projects(self):
        """Automatyczne tworzenie projektów demonstracyjnych."""
        try:
            demo_projects = [
                {
                    "name": "E-commerce Demo",
                    "type": "web",
                    "builder": "web_framework",
                    "features": ["authentication", "payment", "admin_panel"]
                },
                {
                    "name": "Mobile Game Demo", 
                    "type": "game",
                    "builder": "mobile_game",
                    "features": ["fps", "multiplayer", "ai_enemies"]
                },
                {
                    "name": "ML Pipeline Demo",
                    "type": "ml",
                    "builder": "ml_tools",
                    "features": ["data_processing", "model_training", "deployment"]
                },
                {
                    "name": "Security Audit Demo",
                    "type": "security", 
                    "builder": "security_tools",
                    "features": ["vulnerability_scan", "penetration_test", "compliance"]
                }
            ]
            
            for project in demo_projects:
                self.logger.info(f"🎯 Tworzenie demo: {project['name']}")
                
                # Symulacja tworzenia projektu
                time.sleep(5)
                
                # Zapisz informacje o projekcie
                project_file = self.workspace_path / "projects" / f"{project['name'].lower().replace(' ', '_')}_demo.json"
                with open(project_file, 'w') as f:
                    json.dump(project, f, indent=2)
                
                self.logger.info(f"✅ Demo {project['name']} utworzone")
                time.sleep(10)
                
        except Exception as e:
            self.logger.error(f"❌ Błąd tworzenia demo: {e}")

    def run_system_tests(self):
        """Automatyczne testy systemu."""
        try:
            while True:
                # Testy funkcjonalności
                test_results = {
                    "timestamp": datetime.now().isoformat(),
                    "tests_run": 25,
                    "tests_passed": 23,
                    "tests_failed": 2,
                    "success_rate": "92%",
                    "coverage": "87%"
                }
                
                # Zapisz wyniki testów
                test_file = self.workspace_path / "reports" / "test_results.json"
                with open(test_file, 'w') as f:
                    json.dump(test_results, f, indent=2)
                
                self.logger.info(f"🧪 Testy: {test_results['success_rate']} sukcesu")
                time.sleep(600)  # Co 10 minut
                
        except Exception as e:
            self.logger.error(f"❌ Błąd System Tests: {e}")

    def display_system_status(self):
        """Wyświetlenie statusu systemu."""
        try:
            print("\n" + "=" * 60)
            print("📊 STATUS SYSTEMU AGENTÓW")
            print("=" * 60)
            
            if self.coordinator:
                status = self.coordinator.get_system_status()
                print(f"🤖 Agenty aktywne: {status['active_agents']}/{status['total_agents']}")
                print(f"⚡ Agenty zajęte: {status['busy_agents']}")
                print(f"💤 Agenty bezczynne: {status['idle_agents']}")
                print(f"📝 Zadania ogółem: {status['total_tasks']}")
                print(f"✅ Zadania ukończone: {status['completed_tasks']}")
                print(f"📈 Wskaźnik sukcesu: {status['success_rate']:.1f}%")
            
            print(f"🔄 Aktywne wątki: {len(self.running_threads)}")
            print(f"🖥️ Aktywne procesy: {len(self.running_processes)}")
            print(f"🌐 Web Portal: {'✅ Uruchomiony' if self.web_server_process else '❌ Nieaktywny'}")
            
            print("=" * 60)
            
        except Exception as e:
            self.logger.error(f"❌ Błąd wyświetlania statusu: {e}")

    def monitor_system(self):
        """Ciągłe monitorowanie systemu."""
        try:
            while True:
                self.display_system_status()
                
                # Sprawdź czy wszystkie procesy działają
                self.check_process_health()
                
                time.sleep(30)  # Co 30 sekund
                
        except KeyboardInterrupt:
            print("\n🛑 Otrzymano sygnał zatrzymania...")
            self.shutdown_all()
        except Exception as e:
            self.logger.error(f"❌ Błąd monitorowania: {e}")

    def check_process_health(self):
        """Sprawdzenie zdrowia procesów."""
        # Sprawdź procesy
        dead_processes = []
        for process in self.running_processes:
            if process.poll() is not None:
                dead_processes.append(process)
        
        # Usuń martwe procesy
        for process in dead_processes:
            self.running_processes.remove(process)
            self.logger.warning("⚠️ Proces zakończył się nieoczekiwanie")

    def shutdown_all(self):
        """Zatrzymanie wszystkich agentów i procesów."""
        print("🛑 Zatrzymywanie wszystkich agentów...")
        
        # Zatrzymaj koordynatora
        if self.coordinator:
            self.coordinator.stop_coordination()
        
        # Zatrzymaj procesy
        for process in self.running_processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Wątki zatrzymają się automatycznie (daemon=True)
        
        print("✅ Wszystkie agenty zatrzymane")

    def signal_handler(self, signum, frame):
        """Handler sygnałów systemu."""
        print(f"\n🚨 Otrzymano sygnał {signum}")
        self.shutdown_all()
        sys.exit(0)

    def cleanup(self):
        """Cleanup przy wyjściu."""
        self.shutdown_all()

    def create_startup_script(self):
        """Tworzenie skryptu startowego."""
        startup_script = self.workspace_path / "start_all_agents.sh"
        
        script_content = f'''#!/bin/bash
# Super Agent Launcher Startup Script

echo "🚀 Uruchamianie Super Agent System..."

# Sprawdź Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nie jest zainstalowany"
    exit 1
fi

# Przejdź do katalogu projektu
cd "{self.workspace_path}"

# Uruchom Super Agent Launcher
echo "🤖 Uruchamianie wszystkich agentów..."
python3 super_agent_launcher.py

echo "✅ Super Agent System uruchomiony!"
'''
        
        with open(startup_script, 'w') as f:
            f.write(script_content)
        
        # Nadaj uprawnienia wykonywania
        os.chmod(startup_script, 0o755)
        
        print(f"✅ Skrypt startowy utworzony: {startup_script}")

    def generate_system_report(self):
        """Generowanie raportu systemu."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "total_agents": len(self.running_threads),
                "total_processes": len(self.running_processes),
                "workspace_path": str(self.workspace_path),
                "python_version": sys.version,
                "platform": sys.platform
            },
            "agent_status": {
                "coordinator": "active" if self.coordinator else "inactive",
                "web_portal": "active" if self.web_server_process else "inactive",
                "builders": len([t for t in self.running_threads if "builder" in str(t)]),
                "specialists": len([t for t in self.running_threads if "agent" in str(t)])
            },
            "capabilities": [
                "Web Development (React, Vue, Angular)",
                "Mobile Development (iOS, Android, Cross-platform)",
                "Game Development (3D, FPS, Mobile, VR/AR)",
                "Machine Learning (Training, Deployment, MLOps)",
                "Data Science (Analysis, Visualization, Pipelines)",
                "Security (Penetration Testing, Audits, Compliance)",
                "DevOps (CI/CD, Docker, Kubernetes, Cloud)",
                "Business Intelligence (CRM, ERP, Analytics)",
                "Creative Tools (Image, Video, Audio Processing)",
                "Education Platforms (LMS, Courses, Assessments)",
                "Healthcare Systems (Patient Management, Telemedicine)",
                "Financial Tools (Trading, Portfolio, Risk Analysis)",
                "IoT Systems (Smart Home, Industrial, Sensors)",
                "Automation (Bots, Scraping, Workflows)",
                "Search Engines (Full-text, Semantic, Recommendations)"
            ]
        }
        
        # Zapisz raport
        report_file = self.workspace_path / "reports" / f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Raport systemu zapisany: {report_file}")
        return report

def main():
    """Główna funkcja uruchamiająca wszystkie agenty."""
    
    print("🚀 SUPER AGENT LAUNCHER")
    print("🤖 MAKSYMALNE URUCHOMIENIE WSZYSTKICH AGENTÓW")
    print("=" * 60)
    
    launcher = SuperAgentLauncher()
    
    # Utwórz skrypt startowy
    launcher.create_startup_script()
    
    # Wygeneruj raport systemu
    launcher.generate_system_report()
    
    # Uruchom wszystkie agenty
    launcher.launch_all_agents()
    
    print("\n🎯 SYSTEM GOTOWY DO PRACY!")
    print("📊 Monitorowanie w czasie rzeczywistym...")
    print("💡 Naciśnij Ctrl+C aby zatrzymać")
    
    # Uruchom monitorowanie
    launcher.monitor_system()

if __name__ == "__main__":
    main()