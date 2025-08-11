#!/usr/bin/env python3
"""
🤖 Master Agent Coordinator - Główny Koordynator Wszystkich Agentów
Zarządza i koordynuje działania wszystkich specjalistycznych agentów w systemie
"""

import json
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import concurrent.futures

# Import wszystkich agentów
from programming_agent import ProgrammingAgent
from freelance_agent import FreelanceAgent
from task_executor import TaskExecutor
from ai_analyzer import AIAnalyzer
from ai_code_generator import AICodeGenerator

class AgentType(Enum):
    """Typy agentów w systemie."""
    PROGRAMMING = "programming"
    FREELANCE = "freelance" 
    TASK_EXECUTOR = "task_executor"
    AI_ANALYZER = "ai_analyzer"
    CODE_GENERATOR = "code_generator"
    WEB_BUILDER = "web_builder"
    MOBILE_BUILDER = "mobile_builder"
    GAME_BUILDER = "game_builder"
    SECURITY_SPECIALIST = "security_specialist"
    DATA_SCIENTIST = "data_scientist"
    DEVOPS_ENGINEER = "devops_engineer"
    ML_ENGINEER = "ml_engineer"
    BUSINESS_ANALYST = "business_analyst"

class AgentStatus(Enum):
    """Status agenta."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class AgentInfo:
    """Informacje o agencie."""
    agent_id: str
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[str]
    status: AgentStatus
    current_task: Optional[str] = None
    last_activity: Optional[datetime] = None
    performance_score: float = 100.0
    completed_tasks: int = 0
    success_rate: float = 100.0

@dataclass
class Task:
    """Zadanie do wykonania."""
    task_id: str
    title: str
    description: str
    task_type: str
    priority: int
    requirements: List[str]
    assigned_agent: Optional[str] = None
    status: str = "pending"
    created_at: datetime = None
    deadline: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

class MasterAgentCoordinator:
    """Główny koordynator wszystkich agentów w systemie."""
    
    def __init__(self, workspace_path: str = "/workspace"):
        self.workspace_path = Path(workspace_path)
        self.agents: Dict[str, AgentInfo] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.PriorityQueue()
        self.results_queue = queue.Queue()
        
        # Konfiguracja logowania
        self.setup_logging()
        
        # Inicjalizacja agentów
        self.initialize_agents()
        
        # Wątki dla przetwarzania
        self.running = False
        self.coordinator_thread = None
        self.monitor_thread = None
        
        self.logger.info("🤖 Master Agent Coordinator zainicjalizowany")

    def setup_logging(self):
        """Konfiguracja systemu logowania."""
        log_dir = self.workspace_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "master_coordinator.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("MasterCoordinator")

    def initialize_agents(self):
        """Inicjalizacja wszystkich agentów w systemie."""
        
        # Agent programistyczny
        self.register_agent(AgentInfo(
            agent_id="prog_001",
            agent_type=AgentType.PROGRAMMING,
            name="Programming Agent",
            description="Główny agent do analizy i generowania kodu",
            capabilities=[
                "code_analysis", "code_generation", "debugging", 
                "refactoring", "testing", "documentation"
            ],
            status=AgentStatus.IDLE
        ))
        
        # Agent freelance
        self.register_agent(AgentInfo(
            agent_id="freelance_001", 
            agent_type=AgentType.FREELANCE,
            name="Freelance Agent",
            description="Automatyczne wyszukiwanie i składanie ofert",
            capabilities=[
                "job_search", "proposal_writing", "client_communication",
                "project_management", "bid_optimization"
            ],
            status=AgentStatus.IDLE
        ))
        
        # Executor zadań
        self.register_agent(AgentInfo(
            agent_id="executor_001",
            agent_type=AgentType.TASK_EXECUTOR, 
            name="Task Executor",
            description="Autonomiczne wykonywanie zadań programistycznych",
            capabilities=[
                "task_execution", "project_delivery", "quality_assurance",
                "testing", "deployment", "client_delivery"
            ],
            status=AgentStatus.IDLE
        ))
        
        # AI Analyzer
        self.register_agent(AgentInfo(
            agent_id="ai_analyzer_001",
            agent_type=AgentType.AI_ANALYZER,
            name="AI Code Analyzer", 
            description="Zaawansowana analiza kodu z wykorzystaniem AI",
            capabilities=[
                "ai_code_analysis", "quality_scoring", "security_audit",
                "performance_analysis", "refactoring_suggestions"
            ],
            status=AgentStatus.IDLE
        ))
        
        # Code Generator
        self.register_agent(AgentInfo(
            agent_id="code_gen_001",
            agent_type=AgentType.CODE_GENERATOR,
            name="AI Code Generator",
            description="Generowanie kodu z języka naturalnego",
            capabilities=[
                "natural_language_to_code", "template_generation",
                "best_practices", "multi_language_support"
            ],
            status=AgentStatus.IDLE
        ))
        
        # Dodanie specjalistycznych agentów
        self.add_specialist_agents()

    def add_specialist_agents(self):
        """Dodanie specjalistycznych agentów."""
        
        specialist_agents = [
            {
                "id": "web_builder_001",
                "type": AgentType.WEB_BUILDER,
                "name": "Web Framework Builder",
                "description": "Specjalista od aplikacji webowych",
                "capabilities": ["react_apps", "vue_apps", "angular_apps", "full_stack", "e_commerce", "cms_systems"]
            },
            {
                "id": "mobile_builder_001", 
                "type": AgentType.MOBILE_BUILDER,
                "name": "Mobile App Builder",
                "description": "Specjalista od aplikacji mobilnych",
                "capabilities": ["react_native", "flutter", "native_ios", "native_android", "pwa", "hybrid_apps"]
            },
            {
                "id": "game_builder_001",
                "type": AgentType.GAME_BUILDER, 
                "name": "Game Development Agent",
                "description": "Specjalista od tworzenia gier",
                "capabilities": ["mobile_games", "3d_games", "fps_games", "game_engines", "vr_ar", "multiplayer"]
            },
            {
                "id": "security_001",
                "type": AgentType.SECURITY_SPECIALIST,
                "name": "Security Specialist Agent", 
                "description": "Specjalista od cyberbezpieczeństwa",
                "capabilities": ["penetration_testing", "vulnerability_scanning", "security_audit", "encryption", "compliance"]
            },
            {
                "id": "data_scientist_001",
                "type": AgentType.DATA_SCIENTIST,
                "name": "Data Science Agent",
                "description": "Specjalista od analizy danych i ML",
                "capabilities": ["data_analysis", "machine_learning", "deep_learning", "data_visualization", "predictive_analytics"]
            },
            {
                "id": "devops_001", 
                "type": AgentType.DEVOPS_ENGINEER,
                "name": "DevOps Engineer Agent",
                "description": "Specjalista od automatyzacji i wdrożeń",
                "capabilities": ["ci_cd", "docker", "kubernetes", "cloud_deployment", "monitoring", "infrastructure"]
            },
            {
                "id": "ml_engineer_001",
                "type": AgentType.ML_ENGINEER,
                "name": "ML Engineering Agent", 
                "description": "Specjalista od systemów ML w produkcji",
                "capabilities": ["ml_pipelines", "model_deployment", "ml_ops", "feature_engineering", "model_monitoring"]
            },
            {
                "id": "business_analyst_001",
                "type": AgentType.BUSINESS_ANALYST,
                "name": "Business Analyst Agent",
                "description": "Specjalista od analizy biznesowej",
                "capabilities": ["requirements_analysis", "business_intelligence", "process_optimization", "reporting", "stakeholder_management"]
            }
        ]
        
        for agent_data in specialist_agents:
            self.register_agent(AgentInfo(
                agent_id=agent_data["id"],
                agent_type=agent_data["type"], 
                name=agent_data["name"],
                description=agent_data["description"],
                capabilities=agent_data["capabilities"],
                status=AgentStatus.IDLE
            ))

    def register_agent(self, agent_info: AgentInfo):
        """Rejestracja agenta w systemie."""
        self.agents[agent_info.agent_id] = agent_info
        self.logger.info(f"✅ Zarejestrowano agenta: {agent_info.name} ({agent_info.agent_id})")

    def start_coordination(self):
        """Uruchomienie systemu koordynacji agentów."""
        if self.running:
            self.logger.warning("⚠️ Koordynator już działa")
            return
            
        self.running = True
        
        # Uruchomienie wątków
        self.coordinator_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        
        self.coordinator_thread.start()
        self.monitor_thread.start()
        
        self.logger.info("🚀 Master Agent Coordinator uruchomiony!")

    def stop_coordination(self):
        """Zatrzymanie systemu koordynacji."""
        self.running = False
        self.logger.info("🛑 Master Agent Coordinator zatrzymany")

    def _coordination_loop(self):
        """Główna pętla koordynacji zadań."""
        while self.running:
            try:
                # Sprawdzenie nowych zadań
                self._process_pending_tasks()
                
                # Sprawdzenie statusu agentów
                self._check_agent_status()
                
                # Optymalizacja obciążenia
                self._optimize_workload()
                
                time.sleep(5)  # Sprawdzanie co 5 sekund
                
            except Exception as e:
                self.logger.error(f"❌ Błąd w pętli koordynacji: {e}")
                time.sleep(10)

    def _monitoring_loop(self):
        """Pętla monitorowania wydajności agentów."""
        while self.running:
            try:
                # Monitorowanie wydajności
                self._monitor_performance()
                
                # Generowanie raportów
                self._generate_reports()
                
                # Aktualizacja metryk
                self._update_metrics()
                
                time.sleep(30)  # Monitorowanie co 30 sekund
                
            except Exception as e:
                self.logger.error(f"❌ Błąd w monitorowaniu: {e}")
                time.sleep(60)

    def assign_task(self, task: Task) -> bool:
        """Przypisanie zadania do najlepszego agenta."""
        
        # Znajdź najlepszego agenta dla zadania
        best_agent = self._find_best_agent_for_task(task)
        
        if not best_agent:
            self.logger.warning(f"⚠️ Brak dostępnego agenta dla zadania: {task.title}")
            return False
        
        # Przypisz zadanie
        task.assigned_agent = best_agent.agent_id
        task.status = "assigned"
        self.tasks[task.task_id] = task
        
        # Aktualizuj status agenta
        best_agent.status = AgentStatus.BUSY
        best_agent.current_task = task.task_id
        best_agent.last_activity = datetime.now()
        
        self.logger.info(f"✅ Zadanie '{task.title}' przypisane do {best_agent.name}")
        
        # Uruchom wykonanie zadania w osobnym wątku
        threading.Thread(target=self._execute_task, args=(task, best_agent), daemon=True).start()
        
        return True

    def _find_best_agent_for_task(self, task: Task) -> Optional[AgentInfo]:
        """Znajdź najlepszego agenta dla zadania."""
        
        available_agents = [
            agent for agent in self.agents.values() 
            if agent.status == AgentStatus.IDLE
        ]
        
        if not available_agents:
            return None
        
        # Scoring system dla dopasowania agenta do zadania
        best_agent = None
        best_score = 0
        
        for agent in available_agents:
            score = self._calculate_agent_task_score(agent, task)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent

    def _calculate_agent_task_score(self, agent: AgentInfo, task: Task) -> float:
        """Oblicz score dopasowania agenta do zadania."""
        score = 0.0
        
        # Dopasowanie typu zadania do możliwości agenta
        task_keywords = task.description.lower().split()
        for capability in agent.capabilities:
            for keyword in task_keywords:
                if keyword in capability.lower():
                    score += 10
        
        # Wydajność agenta
        score += agent.performance_score * 0.5
        
        # Wskaźnik sukcesu
        score += agent.success_rate * 0.3
        
        # Bonus za brak obecnego zadania
        if agent.current_task is None:
            score += 20
        
        return score

    def _execute_task(self, task: Task, agent: AgentInfo):
        """Wykonaj zadanie przez agenta."""
        try:
            self.logger.info(f"🔄 Rozpoczęcie zadania '{task.title}' przez {agent.name}")
            
            # Symulacja wykonania zadania (w rzeczywistości wywołanie odpowiedniego agenta)
            result = self._delegate_to_agent(task, agent)
            
            # Aktualizacja rezultatu
            task.result = result
            task.status = "completed"
            
            # Aktualizacja agenta
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.completed_tasks += 1
            agent.last_activity = datetime.now()
            
            if result.get("success", False):
                agent.success_rate = min(100.0, agent.success_rate + 0.5)
                agent.performance_score = min(100.0, agent.performance_score + 0.2)
            else:
                agent.success_rate = max(0.0, agent.success_rate - 2.0)
                agent.performance_score = max(0.0, agent.performance_score - 1.0)
            
            self.logger.info(f"✅ Zadanie '{task.title}' zakończone przez {agent.name}")
            
        except Exception as e:
            self.logger.error(f"❌ Błąd wykonania zadania '{task.title}': {e}")
            task.status = "failed"
            agent.status = AgentStatus.ERROR
            agent.current_task = None

    def _delegate_to_agent(self, task: Task, agent: AgentInfo) -> Dict[str, Any]:
        """Deleguj zadanie do odpowiedniego agenta."""
        
        try:
            if agent.agent_type == AgentType.PROGRAMMING:
                return self._execute_programming_task(task)
            elif agent.agent_type == AgentType.FREELANCE:
                return self._execute_freelance_task(task)
            elif agent.agent_type == AgentType.TASK_EXECUTOR:
                return self._execute_general_task(task)
            elif agent.agent_type == AgentType.AI_ANALYZER:
                return self._execute_analysis_task(task)
            elif agent.agent_type == AgentType.CODE_GENERATOR:
                return self._execute_generation_task(task)
            elif agent.agent_type == AgentType.WEB_BUILDER:
                return self._execute_web_building_task(task)
            elif agent.agent_type == AgentType.MOBILE_BUILDER:
                return self._execute_mobile_building_task(task)
            elif agent.agent_type == AgentType.GAME_BUILDER:
                return self._execute_game_building_task(task)
            else:
                return self._execute_specialist_task(task, agent)
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_programming_task(self, task: Task) -> Dict[str, Any]:
        """Wykonaj zadanie programistyczne."""
        try:
            agent = ProgrammingAgent()
            
            if "analyze" in task.description.lower():
                result = agent.analyze_project_structure()
                return {"success": True, "type": "analysis", "data": result}
                
            elif "generate" in task.description.lower():
                # Parsowanie wymagań do generowania kodu
                language = "python"  # domyślny
                for req in task.requirements:
                    if any(lang in req.lower() for lang in ["python", "javascript", "java"]):
                        language = req.lower()
                        break
                
                code = agent.generate_code(language, task.title, task.requirements)
                return {"success": True, "type": "code_generation", "code": code}
                
            elif "debug" in task.description.lower():
                # Znajdź plik do debugowania w requirements
                file_path = next((req for req in task.requirements if req.endswith('.py')), None)
                if file_path:
                    debug_info = agent.debug_code(file_path, task.description)
                    return {"success": True, "type": "debugging", "debug_info": debug_info}
            
            return {"success": True, "type": "general", "message": "Zadanie wykonane"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_freelance_task(self, task: Task) -> Dict[str, Any]:
        """Wykonaj zadanie freelance."""
        try:
            # Symulacja działania freelance agenta
            time.sleep(2)  # Symulacja pracy
            
            return {
                "success": True, 
                "type": "freelance",
                "jobs_found": 5,
                "proposals_sent": 3,
                "responses": 1
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_general_task(self, task: Task) -> Dict[str, Any]:
        """Wykonaj ogólne zadanie."""
        try:
            # Symulacja wykonania zadania
            time.sleep(3)
            
            return {
                "success": True,
                "type": "general_execution", 
                "deliverables": ["code", "documentation", "tests"],
                "quality_score": 95.0
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_analysis_task(self, task: Task) -> Dict[str, Any]:
        """Wykonaj zadanie analizy AI."""
        try:
            # Symulacja analizy AI
            time.sleep(1)
            
            return {
                "success": True,
                "type": "ai_analysis",
                "quality_score": 87.5,
                "security_score": 92.0,
                "performance_score": 89.0,
                "recommendations": ["Improve error handling", "Add unit tests", "Optimize database queries"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_generation_task(self, task: Task) -> Dict[str, Any]:
        """Wykonaj zadanie generowania kodu."""
        try:
            # Symulacja generowania kodu
            time.sleep(2)
            
            return {
                "success": True,
                "type": "code_generation",
                "generated_files": ["main.py", "utils.py", "tests.py"],
                "lines_generated": 450,
                "language": "python"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_web_building_task(self, task: Task) -> Dict[str, Any]:
        """Wykonaj zadanie budowania aplikacji webowej."""
        try:
            time.sleep(4)  # Symulacja tworzenia aplikacji web
            
            return {
                "success": True,
                "type": "web_application",
                "framework": "React",
                "components": ["Frontend", "Backend", "Database", "API"],
                "features": ["Authentication", "CRUD operations", "Responsive design"],
                "deployment_ready": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_mobile_building_task(self, task: Task) -> Dict[str, Any]:
        """Wykonaj zadanie budowania aplikacji mobilnej."""
        try:
            time.sleep(5)  # Symulacja tworzenia aplikacji mobilnej
            
            return {
                "success": True,
                "type": "mobile_application",
                "platform": ["Android", "iOS"],
                "framework": "React Native",
                "features": ["Cross-platform", "Push notifications", "Offline support"],
                "store_ready": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_game_building_task(self, task: Task) -> Dict[str, Any]:
        """Wykonaj zadanie tworzenia gry."""
        try:
            time.sleep(6)  # Symulacja tworzenia gry
            
            return {
                "success": True,
                "type": "game_development",
                "game_type": "FPS Mobile Game",
                "engine": "Custom 3D Engine",
                "features": ["3D Graphics", "AI Enemies", "Multiplayer", "Mobile Controls"],
                "platforms": ["Android", "iOS"],
                "playable": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_specialist_task(self, task: Task, agent: AgentInfo) -> Dict[str, Any]:
        """Wykonaj zadanie specjalistyczne."""
        try:
            # Symulacja pracy specjalistycznego agenta
            execution_time = 3 + len(agent.capabilities)  # Czas zależny od złożoności
            time.sleep(execution_time)
            
            return {
                "success": True,
                "type": f"specialist_{agent.agent_type.value}",
                "specialist": agent.name,
                "capabilities_used": agent.capabilities,
                "quality_score": 90.0 + (agent.performance_score * 0.1)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_task(self, title: str, description: str, task_type: str, 
                   requirements: List[str], priority: int = 5) -> str:
        """Utwórz nowe zadanie."""
        
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            requirements=requirements,
            created_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        
        # Dodaj do kolejki z priorytetem
        self.task_queue.put((priority, task_id))
        
        self.logger.info(f"📝 Utworzono zadanie: {title} (ID: {task_id})")
        
        return task_id

    def _process_pending_tasks(self):
        """Przetwarzanie oczekujących zadań."""
        try:
            while not self.task_queue.empty():
                priority, task_id = self.task_queue.get_nowait()
                
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    if task.status == "pending":
                        self.assign_task(task)
                        
        except queue.Empty:
            pass

    def _check_agent_status(self):
        """Sprawdzenie statusu wszystkich agentów."""
        for agent in self.agents.values():
            if agent.status == AgentStatus.BUSY and agent.current_task:
                # Sprawdź czy zadanie nie trwa zbyt długo
                if agent.last_activity:
                    time_diff = datetime.now() - agent.last_activity
                    if time_diff > timedelta(minutes=30):  # Timeout 30 minut
                        self.logger.warning(f"⚠️ Agent {agent.name} przekroczył timeout")
                        agent.status = AgentStatus.ERROR

    def _optimize_workload(self):
        """Optymalizacja obciążenia agentów."""
        # Sprawdź czy są przeciążeni agenci
        busy_agents = [a for a in self.agents.values() if a.status == AgentStatus.BUSY]
        idle_agents = [a for a in self.agents.values() if a.status == AgentStatus.IDLE]
        
        if len(busy_agents) > len(idle_agents) * 2:
            self.logger.info("⚖️ Optymalizacja obciążenia - równoważenie zadań")

    def _monitor_performance(self):
        """Monitorowanie wydajności agentów."""
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a.status != AgentStatus.OFFLINE])
        busy_agents = len([a for a in self.agents.values() if a.status == AgentStatus.BUSY])
        
        utilization = (busy_agents / active_agents * 100) if active_agents > 0 else 0
        
        self.logger.info(f"📊 Wydajność systemu: {utilization:.1f}% wykorzystania agentów")

    def _generate_reports(self):
        """Generowanie raportów wydajności."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status != AgentStatus.OFFLINE]),
            "total_tasks": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == "completed"]),
            "success_rate": self._calculate_overall_success_rate()
        }
        
        # Zapisz raport
        reports_dir = self.workspace_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

    def _calculate_overall_success_rate(self) -> float:
        """Oblicz ogólny wskaźnik sukcesu."""
        if not self.agents:
            return 0.0
        
        total_success_rate = sum(agent.success_rate for agent in self.agents.values())
        return total_success_rate / len(self.agents)

    def _update_metrics(self):
        """Aktualizacja metryk systemu."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "agents": {agent_id: asdict(agent) for agent_id, agent in self.agents.items()},
            "tasks": {task_id: asdict(task) for task_id, task in self.tasks.items()}
        }
        
        # Zapisz metryki
        metrics_file = self.workspace_path / "metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)

    def get_system_status(self) -> Dict[str, Any]:
        """Pobierz status całego systemu."""
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status != AgentStatus.OFFLINE]),
            "busy_agents": len([a for a in self.agents.values() if a.status == AgentStatus.BUSY]),
            "idle_agents": len([a for a in self.agents.values() if a.status == AgentStatus.IDLE]),
            "total_tasks": len(self.tasks),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == "pending"]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == "completed"]),
            "success_rate": self._calculate_overall_success_rate(),
            "uptime": datetime.now().isoformat() if self.running else "Not running"
        }

    def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Pobierz szczegóły agenta."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            return asdict(agent)
        return None

    def get_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Pobierz szczegóły zadania."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return asdict(task)
        return None

    def emergency_stop(self):
        """Awaryjne zatrzymanie wszystkich agentów."""
        self.logger.warning("🚨 AWARYJNE ZATRZYMANIE SYSTEMU")
        
        # Zatrzymaj wszystkie agenty
        for agent in self.agents.values():
            agent.status = AgentStatus.OFFLINE
            agent.current_task = None
        
        # Zatrzymaj koordynację
        self.stop_coordination()
        
        self.logger.warning("🛑 System zatrzymany awaryjnie")

    def restart_agent(self, agent_id: str) -> bool:
        """Restart konkretnego agenta."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.last_activity = datetime.now()
            
            self.logger.info(f"🔄 Agent {agent.name} zrestartowany")
            return True
        
        return False

    def add_custom_agent(self, agent_info: AgentInfo):
        """Dodaj niestandardowego agenta."""
        self.register_agent(agent_info)
        self.logger.info(f"➕ Dodano niestandardowego agenta: {agent_info.name}")

    def remove_agent(self, agent_id: str) -> bool:
        """Usuń agenta z systemu."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            
            # Sprawdź czy agent nie ma aktywnego zadania
            if agent.current_task:
                self.logger.warning(f"⚠️ Nie można usunąć agenta {agent.name} - ma aktywne zadanie")
                return False
            
            del self.agents[agent_id]
            self.logger.info(f"➖ Usunięto agenta: {agent.name}")
            return True
        
        return False

def main():
    """Główna funkcja uruchamiająca koordynatora."""
    print("🤖 Uruchamianie Master Agent Coordinator...")
    
    coordinator = MasterAgentCoordinator()
    
    # Uruchom koordynację
    coordinator.start_coordination()
    
    # Przykładowe zadania testowe
    test_tasks = [
        {
            "title": "Analiza projektu Python",
            "description": "Przeanalizuj strukturę projektu i jakość kodu",
            "task_type": "analysis",
            "requirements": ["python", "code_quality", "structure_analysis"],
            "priority": 1
        },
        {
            "title": "Generowanie API REST",
            "description": "Wygeneruj kod dla API REST w Python",
            "task_type": "code_generation", 
            "requirements": ["python", "flask", "rest_api", "authentication"],
            "priority": 2
        },
        {
            "title": "Tworzenie gry mobilnej",
            "description": "Stwórz grę mobilną w stylu FPS",
            "task_type": "game_development",
            "requirements": ["mobile", "fps", "3d_graphics", "android"],
            "priority": 3
        },
        {
            "title": "Aplikacja webowa e-commerce",
            "description": "Stwórz kompletną aplikację e-commerce",
            "task_type": "web_development",
            "requirements": ["react", "node.js", "database", "payment_integration"],
            "priority": 2
        }
    ]
    
    # Dodaj zadania testowe
    for task_data in test_tasks:
        coordinator.create_task(**task_data)
    
    print("✅ Koordynator uruchomiony z przykładowymi zadaniami")
    print("📊 Status systemu:")
    
    try:
        while True:
            status = coordinator.get_system_status()
            print(f"\r🤖 Agenty: {status['active_agents']}/{status['total_agents']} | "
                  f"Zadania: {status['completed_tasks']}/{status['total_tasks']} | "
                  f"Sukces: {status['success_rate']:.1f}%", end="")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Zatrzymywanie koordynatora...")
        coordinator.stop_coordination()
        print("✅ Koordynator zatrzymany")

if __name__ == "__main__":
    main()