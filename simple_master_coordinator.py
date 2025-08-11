#!/usr/bin/env python3
"""
🤖 Simple Master Agent Coordinator - Bez Zewnętrznych Zależności
Zarządza wszystkimi agentami używając tylko standardowej biblioteki Python
"""

import json
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import queue

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
class SimpleAgentInfo:
    """Informacje o agencie."""
    agent_id: str
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[str]
    status: AgentStatus
    current_task: Optional[str] = None
    completed_tasks: int = 0
    success_rate: float = 100.0

@dataclass
class SimpleTask:
    """Zadanie do wykonania."""
    task_id: str
    title: str
    description: str
    task_type: str
    priority: int
    requirements: List[str]
    assigned_agent: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None

class SimpleMasterCoordinator:
    """Uproszczony koordynator agentów bez zewnętrznych zależności."""
    
    def __init__(self, workspace_path: str = "/workspace"):
        self.workspace_path = Path(workspace_path)
        self.agents: Dict[str, SimpleAgentInfo] = {}
        self.tasks: Dict[str, SimpleTask] = {}
        self.task_queue = queue.Queue()
        
        # Inicjalizacja
        self.setup_logging()
        self.initialize_agents()
        
        # Status systemu
        self.running = False
        self.start_time = datetime.now()
        
        print("🤖 Simple Master Coordinator zainicjalizowany")

    def setup_logging(self):
        """Konfiguracja logowania."""
        log_dir = self.workspace_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "simple_coordinator.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("SimpleCoordinator")

    def initialize_agents(self):
        """Inicjalizacja wszystkich agentów."""
        
        agents_config = [
            {
                "id": "prog_001",
                "type": AgentType.PROGRAMMING,
                "name": "Programming Agent",
                "description": "Główny agent do analizy i generowania kodu",
                "capabilities": ["code_analysis", "code_generation", "debugging", "refactoring", "testing"]
            },
            {
                "id": "freelance_001", 
                "type": AgentType.FREELANCE,
                "name": "Freelance Agent",
                "description": "Automatyczne wyszukiwanie i składanie ofert",
                "capabilities": ["job_search", "proposal_writing", "client_communication", "bid_optimization"]
            },
            {
                "id": "executor_001",
                "type": AgentType.TASK_EXECUTOR, 
                "name": "Task Executor",
                "description": "Autonomiczne wykonywanie zadań programistycznych",
                "capabilities": ["task_execution", "project_delivery", "quality_assurance", "deployment"]
            },
            {
                "id": "ai_analyzer_001",
                "type": AgentType.AI_ANALYZER,
                "name": "AI Code Analyzer", 
                "description": "Zaawansowana analiza kodu z wykorzystaniem AI",
                "capabilities": ["ai_code_analysis", "quality_scoring", "security_audit", "performance_analysis"]
            },
            {
                "id": "code_gen_001",
                "type": AgentType.CODE_GENERATOR,
                "name": "AI Code Generator",
                "description": "Generowanie kodu z języka naturalnego",
                "capabilities": ["natural_language_to_code", "template_generation", "best_practices"]
            },
            {
                "id": "web_builder_001",
                "type": AgentType.WEB_BUILDER,
                "name": "Web Framework Builder",
                "description": "Specjalista od aplikacji webowych",
                "capabilities": ["react_apps", "vue_apps", "angular_apps", "full_stack", "e_commerce"]
            },
            {
                "id": "mobile_builder_001", 
                "type": AgentType.MOBILE_BUILDER,
                "name": "Mobile App Builder",
                "description": "Specjalista od aplikacji mobilnych",
                "capabilities": ["react_native", "flutter", "native_ios", "native_android", "games"]
            },
            {
                "id": "game_builder_001",
                "type": AgentType.GAME_BUILDER, 
                "name": "Game Development Agent",
                "description": "Specjalista od tworzenia gier",
                "capabilities": ["mobile_games", "3d_games", "fps_games", "multiplayer", "ai_enemies"]
            },
            {
                "id": "security_001",
                "type": AgentType.SECURITY_SPECIALIST,
                "name": "Security Specialist Agent", 
                "description": "Specjalista od cyberbezpieczeństwa",
                "capabilities": ["penetration_testing", "vulnerability_scanning", "security_audit", "compliance"]
            },
            {
                "id": "data_scientist_001",
                "type": AgentType.DATA_SCIENTIST,
                "name": "Data Science Agent",
                "description": "Specjalista od analizy danych i ML",
                "capabilities": ["data_analysis", "machine_learning", "visualization", "predictive_analytics"]
            },
            {
                "id": "devops_001", 
                "type": AgentType.DEVOPS_ENGINEER,
                "name": "DevOps Engineer Agent",
                "description": "Specjalista od automatyzacji i wdrożeń",
                "capabilities": ["ci_cd", "docker", "kubernetes", "cloud_deployment", "monitoring"]
            },
            {
                "id": "ml_engineer_001",
                "type": AgentType.ML_ENGINEER,
                "name": "ML Engineering Agent", 
                "description": "Specjalista od systemów ML w produkcji",
                "capabilities": ["ml_pipelines", "model_deployment", "ml_ops", "feature_engineering"]
            },
            {
                "id": "business_analyst_001",
                "type": AgentType.BUSINESS_ANALYST,
                "name": "Business Analyst Agent",
                "description": "Specjalista od analizy biznesowej",
                "capabilities": ["requirements_analysis", "business_intelligence", "process_optimization"]
            }
        ]
        
        for agent_config in agents_config:
            agent_info = SimpleAgentInfo(
                agent_id=agent_config["id"],
                agent_type=agent_config["type"],
                name=agent_config["name"],
                description=agent_config["description"],
                capabilities=agent_config["capabilities"],
                status=AgentStatus.IDLE
            )
            self.register_agent(agent_info)

    def register_agent(self, agent_info: SimpleAgentInfo):
        """Rejestracja agenta w systemie."""
        self.agents[agent_info.agent_id] = agent_info
        print(f"   ✅ Zarejestrowano: {agent_info.name}")

    def start_coordination(self):
        """Uruchomienie koordynacji."""
        if self.running:
            print("⚠️ Koordynator już działa")
            return
        
        self.running = True
        
        # Uruchom wątek koordynacji
        coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        coordination_thread.start()
        
        print("🚀 Simple Master Coordinator uruchomiony!")

    def stop_coordination(self):
        """Zatrzymanie koordynacji."""
        self.running = False
        print("🛑 Simple Master Coordinator zatrzymany")

    def _coordination_loop(self):
        """Główna pętla koordynacji."""
        while self.running:
            try:
                # Przetwarzaj zadania z kolejki
                self._process_task_queue()
                
                # Aktualizuj status agentów
                self._update_agent_status()
                
                time.sleep(2)  # Sprawdzanie co 2 sekundy
                
            except Exception as e:
                self.logger.error(f"Błąd w koordynacji: {e}")
                time.sleep(5)

    def _process_task_queue(self):
        """Przetwarzanie kolejki zadań."""
        try:
            while not self.task_queue.empty():
                task = self.task_queue.get_nowait()
                self._assign_task_to_agent(task)
        except queue.Empty:
            pass

    def _assign_task_to_agent(self, task: SimpleTask):
        """Przypisanie zadania do agenta."""
        
        # Znajdź najlepszego agenta
        best_agent = self._find_best_agent_for_task(task)
        
        if best_agent:
            task.assigned_agent = best_agent.agent_id
            task.status = "assigned"
            best_agent.status = AgentStatus.BUSY
            best_agent.current_task = task.task_id
            
            print(f"📋 Zadanie '{task.title}' przypisane do {best_agent.name}")
            
            # Symuluj wykonanie zadania
            threading.Thread(target=self._execute_task, args=(task, best_agent), daemon=True).start()
        else:
            print(f"⚠️ Brak dostępnego agenta dla zadania: {task.title}")

    def _find_best_agent_for_task(self, task: SimpleTask) -> Optional[SimpleAgentInfo]:
        """Znajdź najlepszego agenta dla zadania."""
        
        available_agents = [
            agent for agent in self.agents.values() 
            if agent.status == AgentStatus.IDLE
        ]
        
        if not available_agents:
            return None
        
        # Prosty scoring
        best_agent = None
        best_score = 0
        
        for agent in available_agents:
            score = 0
            
            # Sprawdź dopasowanie capabilities
            for capability in agent.capabilities:
                for requirement in task.requirements:
                    if requirement.lower() in capability.lower():
                        score += 10
            
            # Dodaj bonus za wydajność
            score += agent.success_rate * 0.1
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent

    def _execute_task(self, task: SimpleTask, agent: SimpleAgentInfo):
        """Wykonanie zadania przez agenta."""
        try:
            print(f"🔄 {agent.name} rozpoczyna zadanie: {task.title}")
            
            # Symulacja wykonania zadania
            execution_time = len(task.requirements) * 2  # 2 sekundy na requirement
            time.sleep(execution_time)
            
            # Symulacja rezultatu
            result = {
                "success": True,
                "agent": agent.name,
                "execution_time": execution_time,
                "deliverables": task.requirements,
                "quality_score": 85 + (agent.success_rate * 0.1)
            }
            
            # Aktualizuj zadanie i agenta
            task.result = result
            task.status = "completed"
            
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.completed_tasks += 1
            agent.success_rate = min(100.0, agent.success_rate + 0.5)
            
            print(f"✅ {agent.name} ukończył zadanie: {task.title}")
            
        except Exception as e:
            print(f"❌ Błąd wykonania zadania {task.title}: {e}")
            task.status = "failed"
            agent.status = AgentStatus.ERROR

    def _update_agent_status(self):
        """Aktualizacja statusu agentów."""
        for agent in self.agents.values():
            if agent.status == AgentStatus.ERROR:
                # Auto-recovery po 30 sekundach
                agent.status = AgentStatus.IDLE
                agent.current_task = None

    def create_task(self, title: str, description: str, task_type: str, 
                   requirements: List[str], priority: int = 5) -> str:
        """Utworzenie nowego zadania."""
        
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        
        task = SimpleTask(
            task_id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            requirements=requirements
        )
        
        self.tasks[task_id] = task
        self.task_queue.put(task)
        
        print(f"📝 Utworzono zadanie: {title}")
        return task_id

    def get_system_status(self) -> Dict[str, Any]:
        """Status całego systemu."""
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status != AgentStatus.OFFLINE]),
            "busy_agents": len([a for a in self.agents.values() if a.status == AgentStatus.BUSY]),
            "idle_agents": len([a for a in self.agents.values() if a.status == AgentStatus.IDLE]),
            "total_tasks": len(self.tasks),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == "pending"]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == "completed"]),
            "success_rate": self._calculate_success_rate(),
            "uptime": str(datetime.now() - self.start_time) if self.running else "Not running"
        }

    def _calculate_success_rate(self) -> float:
        """Oblicz wskaźnik sukcesu."""
        if not self.agents:
            return 0.0
        
        total_success = sum(agent.success_rate for agent in self.agents.values())
        return total_success / len(self.agents)

    def list_agents(self):
        """Wylistuj wszystkich agentów."""
        print("\n🤖 LISTA AGENTÓW:")
        print("=" * 50)
        
        for agent in self.agents.values():
            status_emoji = {
                AgentStatus.IDLE: "💤",
                AgentStatus.BUSY: "⚡", 
                AgentStatus.ERROR: "❌",
                AgentStatus.OFFLINE: "🔴"
            }
            
            print(f"{status_emoji[agent.status]} {agent.name}")
            print(f"   ID: {agent.agent_id}")
            print(f"   Typ: {agent.agent_type.value}")
            print(f"   Status: {agent.status.value}")
            print(f"   Ukończone zadania: {agent.completed_tasks}")
            print(f"   Wskaźnik sukcesu: {agent.success_rate:.1f}%")
            print(f"   Możliwości: {', '.join(agent.capabilities[:3])}...")
            print()

    def list_tasks(self):
        """Wylistuj wszystkie zadania."""
        print("\n📋 LISTA ZADAŃ:")
        print("=" * 50)
        
        for task in self.tasks.values():
            status_emoji = {
                "pending": "⏳",
                "assigned": "📋",
                "completed": "✅",
                "failed": "❌"
            }
            
            print(f"{status_emoji.get(task.status, '❓')} {task.title}")
            print(f"   ID: {task.task_id}")
            print(f"   Typ: {task.task_type}")
            print(f"   Status: {task.status}")
            print(f"   Priorytet: {task.priority}")
            print(f"   Wymagania: {', '.join(task.requirements)}")
            if task.assigned_agent:
                agent = self.agents.get(task.assigned_agent)
                print(f"   Przypisany agent: {agent.name if agent else 'Nieznany'}")
            print()

    def add_sample_tasks(self):
        """Dodanie przykładowych zadań."""
        
        sample_tasks = [
            {
                "title": "🌐 Sklep internetowy",
                "description": "Kompletna aplikacja e-commerce",
                "task_type": "web_development",
                "requirements": ["react", "express", "database", "payment"],
                "priority": 1
            },
            {
                "title": "📱 Gra mobilna FPS",
                "description": "Gra w stylu Call of Duty Mobile",
                "task_type": "game_development",
                "requirements": ["mobile", "fps", "3d", "multiplayer"],
                "priority": 2
            },
            {
                "title": "🤖 Analiza kodu AI",
                "description": "Zaawansowana analiza jakości kodu",
                "task_type": "code_analysis",
                "requirements": ["python", "ai_analysis", "quality_metrics"],
                "priority": 3
            },
            {
                "title": "🔒 Audit bezpieczeństwa",
                "description": "Kompleksowy audit aplikacji",
                "task_type": "security",
                "requirements": ["vulnerability_scan", "penetration_test"],
                "priority": 2
            },
            {
                "title": "☁️ Deployment automatyczny",
                "description": "CI/CD pipeline na AWS",
                "task_type": "devops",
                "requirements": ["docker", "kubernetes", "ci_cd"],
                "priority": 3
            }
        ]
        
        for task_data in sample_tasks:
            self.create_task(**task_data)

    def run_demo(self):
        """Uruchomienie demonstracji systemu."""
        print("🎯 DEMONSTRACJA SIMPLE MASTER COORDINATOR")
        print("=" * 60)
        
        # Wylistuj agentów
        self.list_agents()
        
        # Uruchom koordynację
        self.start_coordination()
        
        # Dodaj przykładowe zadania
        print("📝 Dodawanie przykładowych zadań...")
        self.add_sample_tasks()
        
        # Wylistuj zadania
        self.list_tasks()
        
        # Monitoruj przez chwilę
        print("📊 Monitorowanie systemu przez 30 sekund...")
        
        for i in range(6):  # 6 x 5 sekund = 30 sekund
            time.sleep(5)
            status = self.get_system_status()
            print(f"🤖 Status: {status['busy_agents']}/{status['active_agents']} agentów zajętych | "
                  f"Zadania: {status['completed_tasks']}/{status['total_tasks']} ukończonych")
        
        # Pokaż finalne wyniki
        print("\n📊 FINALNE WYNIKI:")
        print("=" * 50)
        
        final_status = self.get_system_status()
        print(f"✅ Ukończone zadania: {final_status['completed_tasks']}")
        print(f"📈 Wskaźnik sukcesu: {final_status['success_rate']:.1f}%")
        print(f"⏱️ Czas działania: {final_status['uptime']}")
        
        # Zatrzymaj system
        self.stop_coordination()

def main():
    """Główna funkcja demonstracyjna."""
    coordinator = SimpleMasterCoordinator()
    coordinator.run_demo()

if __name__ == "__main__":
    main()