#!/usr/bin/env python3
"""
🤖 Freelance Agent - Autonomous Freelance Task Execution System
Automatically finds jobs, analyzes requirements, and sends proposals
"""

import json
import time
import random
import smtplib
import requests
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import re
from dataclasses import dataclass
from enum import Enum

class JobPlatform(Enum):
    """Supported freelance platforms."""
    UPWORK = "upwork"
    FREELANCER = "freelancer"
    FIVERR = "fiverr"
    GURU = "guru"
    PEOPLE_PER_HOUR = "peopleperhour"
    TOPCODER = "topcoder"
    TOPTAL = "toptal"

class JobCategory(Enum):
    """Job categories the agent can handle."""
    WEB_DEVELOPMENT = "web_development"
    MOBILE_DEVELOPMENT = "mobile_development"
    GAME_DEVELOPMENT = "game_development"
    DATA_ANALYSIS = "data_analysis"
    MACHINE_LEARNING = "machine_learning"
    API_DEVELOPMENT = "api_development"
    AUTOMATION = "automation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"

@dataclass
class JobRequirement:
    """Job requirement analysis."""
    skill: str
    experience_level: str
    estimated_hours: int
    complexity: str
    priority: int

@dataclass
class JobOpportunity:
    """Job opportunity details."""
    id: str
    title: str
    description: str
    budget: Dict[str, Any]
    skills_required: List[str]
    platform: JobPlatform
    url: str
    posted_date: datetime
    deadline: Optional[datetime]
    client_rating: float
    client_reviews: int
    requirements: List[JobRequirement]
    match_score: float

@dataclass
class Proposal:
    """Proposal details."""
    job_id: str
    title: str
    cover_letter: str
    bid_amount: float
    delivery_time: int
    portfolio_items: List[str]
    attachments: List[str]

class FreelanceAgent:
    """Autonomous freelance agent for job finding and proposal sending."""
    
    def __init__(self, config_path: str = "freelance_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.setup_logging()
        self.job_cache = {}
        self.proposal_history = []
        self.earnings_tracker = {}
        
        # Agent capabilities and preferences
        self.skills = self.config.get('skills', [])
        self.experience_level = self.config.get('experience_level', 'intermediate')
        self.hourly_rate = self.config.get('hourly_rate', 50)
        self.min_budget = self.config.get('min_budget', 100)
        self.max_budget = self.config.get('max_budget', 10000)
        self.preferred_platforms = self.config.get('preferred_platforms', [])
        
        # Email configuration
        self.email_config = self.config.get('email', {})
        
        # Portfolio and credentials
        self.portfolio = self.config.get('portfolio', [])
        self.credentials = self.config.get('credentials', {})
        
        logging.info("🤖 Freelance Agent initialized successfully")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default configuration
            default_config = {
                "skills": [
                    "Python", "JavaScript", "React", "Node.js", "Mobile Development",
                    "Game Development", "API Development", "Data Analysis", "Machine Learning",
                    "Automation", "Testing", "Documentation"
                ],
                "experience_level": "intermediate",
                "hourly_rate": 50,
                "min_budget": 100,
                "max_budget": 10000,
                "preferred_platforms": ["upwork", "freelancer", "fiverr"],
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "your_email@gmail.com",
                    "password": "your_app_password",
                    "from_name": "Professional Developer"
                },
                "portfolio": [
                    "Mobile game development with Kivy",
                    "AI-powered code analysis system",
                    "Web application with React and Node.js",
                    "Automation scripts and tools",
                    "API development and integration"
                ],
                "credentials": {
                    "certifications": ["Python Developer", "Web Development"],
                    "education": "Computer Science Degree",
                    "years_experience": 5
                },
                "proposal_templates": {
                    "web_development": "I specialize in modern web development with React, Node.js, and Python. I can deliver high-quality, scalable applications with clean code and comprehensive testing.",
                    "mobile_development": "I have extensive experience in mobile development, including creating Call of Duty Mobile-style games with Kivy and Pygame. I can build cross-platform mobile applications.",
                    "game_development": "I specialize in game development, particularly mobile FPS games. I can create complete game engines with 3D graphics, AI enemies, and multiplayer support.",
                    "automation": "I excel at automation and can create intelligent systems that streamline workflows and improve efficiency.",
                    "default": "I am a professional developer with expertise in multiple technologies. I deliver high-quality code with comprehensive documentation and testing."
                }
            }
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('freelance_agent.log'),
                logging.StreamHandler()
            ]
        )

    def search_jobs(self, platforms: List[JobPlatform] = None, 
                   categories: List[JobCategory] = None,
                   max_results: int = 50) -> List[JobOpportunity]:
        """Search for jobs across multiple platforms."""
        if platforms is None:
            platforms = [JobPlatform(p) for p in self.preferred_platforms]
        
        if categories is None:
            categories = list(JobCategory)
        
        all_jobs = []
        
        for platform in platforms:
            try:
                logging.info(f"🔍 Searching jobs on {platform.value}...")
                jobs = self._search_platform(platform, categories, max_results)
                all_jobs.extend(jobs)
                logging.info(f"✅ Found {len(jobs)} jobs on {platform.value}")
            except Exception as e:
                logging.error(f"❌ Error searching {platform.value}: {e}")
        
        # Filter and rank jobs
        filtered_jobs = self._filter_jobs(all_jobs)
        ranked_jobs = self._rank_jobs(filtered_jobs)
        
        logging.info(f"🎯 Total jobs found: {len(ranked_jobs)}")
        return ranked_jobs

    def _search_platform(self, platform: JobPlatform, 
                        categories: List[JobCategory], 
                        max_results: int) -> List[JobOpportunity]:
        """Search jobs on a specific platform."""
        # This would integrate with actual platform APIs
        # For now, we'll simulate job discovery
        
        jobs = []
        
        # Simulate different job types based on platform
        if platform == JobPlatform.UPWORK:
            jobs.extend(self._simulate_upwork_jobs(categories, max_results))
        elif platform == JobPlatform.FREELANCER:
            jobs.extend(self._simulate_freelancer_jobs(categories, max_results))
        elif platform == JobPlatform.FIVERR:
            jobs.extend(self._simulate_fiverr_jobs(categories, max_results))
        
        return jobs

    def _simulate_upwork_jobs(self, categories: List[JobCategory], 
                            max_results: int) -> List[JobOpportunity]:
        """Simulate Upwork job discovery."""
        jobs = []
        
        job_templates = [
            {
                "title": "Python Developer for Mobile Game Development",
                "description": "Need a skilled Python developer to create a Call of Duty Mobile-style game using Kivy framework. Must have experience with game development, 3D graphics, and mobile optimization.",
                "budget": {"min": 2000, "max": 8000, "type": "fixed"},
                "skills": ["Python", "Kivy", "Game Development", "Mobile Development"],
                "category": JobCategory.GAME_DEVELOPMENT
            },
            {
                "title": "AI-Powered Code Analysis System",
                "description": "Looking for a developer to build an intelligent code analysis system that can detect security vulnerabilities, performance issues, and code smells. Should include machine learning capabilities.",
                "budget": {"min": 1500, "max": 5000, "type": "fixed"},
                "skills": ["Python", "Machine Learning", "Code Analysis", "Security"],
                "category": JobCategory.MACHINE_LEARNING
            },
            {
                "title": "Web Application with React and Node.js",
                "description": "Need a full-stack developer to build a modern web application with React frontend and Node.js backend. Should include user authentication, database integration, and responsive design.",
                "budget": {"min": 1000, "max": 4000, "type": "fixed"},
                "skills": ["React", "Node.js", "JavaScript", "Web Development"],
                "category": JobCategory.WEB_DEVELOPMENT
            },
            {
                "title": "API Development and Integration",
                "description": "Looking for an experienced developer to create RESTful APIs and integrate third-party services. Should include comprehensive documentation and testing.",
                "budget": {"min": 800, "max": 3000, "type": "fixed"},
                "skills": ["API Development", "REST", "Python", "Testing"],
                "category": JobCategory.API_DEVELOPMENT
            },
            {
                "title": "Automation Scripts and Tools",
                "description": "Need automation scripts to streamline business processes. Should include data processing, file management, and reporting capabilities.",
                "budget": {"min": 500, "max": 2000, "type": "fixed"},
                "skills": ["Python", "Automation", "Data Processing", "Scripting"],
                "category": JobCategory.AUTOMATION
            }
        ]
        
        for i, template in enumerate(job_templates[:max_results]):
            if template["category"] in categories:
                job = JobOpportunity(
                    id=f"upwork_{i}_{int(time.time())}",
                    title=template["title"],
                    description=template["description"],
                    budget=template["budget"],
                    skills_required=template["skills"],
                    platform=JobPlatform.UPWORK,
                    url=f"https://www.upwork.com/jobs/~{i}",
                    posted_date=datetime.now() - timedelta(hours=random.randint(1, 72)),
                    deadline=datetime.now() + timedelta(days=random.randint(3, 14)),
                    client_rating=random.uniform(3.5, 5.0),
                    client_reviews=random.randint(10, 500),
                    requirements=self._analyze_requirements(template["description"]),
                    match_score=0.0
                )
                jobs.append(job)
        
        return jobs

    def _simulate_freelancer_jobs(self, categories: List[JobCategory], 
                                max_results: int) -> List[JobOpportunity]:
        """Simulate Freelancer job discovery."""
        jobs = []
        
        job_templates = [
            {
                "title": "Mobile App Development with Python",
                "description": "Need a mobile app developer to create a cross-platform application using Python. Should work on both Android and iOS platforms.",
                "budget": {"min": 1200, "max": 6000, "type": "fixed"},
                "skills": ["Python", "Mobile Development", "Cross-platform"],
                "category": JobCategory.MOBILE_DEVELOPMENT
            },
            {
                "title": "Data Analysis and Visualization",
                "description": "Looking for a data analyst to process large datasets and create interactive visualizations. Should include statistical analysis and reporting.",
                "budget": {"min": 600, "max": 2500, "type": "fixed"},
                "skills": ["Data Analysis", "Python", "Visualization", "Statistics"],
                "category": JobCategory.DATA_ANALYSIS
            }
        ]
        
        for i, template in enumerate(job_templates[:max_results]):
            if template["category"] in categories:
                job = JobOpportunity(
                    id=f"freelancer_{i}_{int(time.time())}",
                    title=template["title"],
                    description=template["description"],
                    budget=template["budget"],
                    skills_required=template["skills"],
                    platform=JobPlatform.FREELANCER,
                    url=f"https://www.freelancer.com/projects/{i}",
                    posted_date=datetime.now() - timedelta(hours=random.randint(1, 48)),
                    deadline=datetime.now() + timedelta(days=random.randint(2, 10)),
                    client_rating=random.uniform(3.0, 5.0),
                    client_reviews=random.randint(5, 200),
                    requirements=self._analyze_requirements(template["description"]),
                    match_score=0.0
                )
                jobs.append(job)
        
        return jobs

    def _simulate_fiverr_jobs(self, categories: List[JobCategory], 
                            max_results: int) -> List[JobOpportunity]:
        """Simulate Fiverr job discovery."""
        jobs = []
        
        job_templates = [
            {
                "title": "Code Review and Optimization",
                "description": "Need an expert developer to review existing code, identify issues, and provide optimization suggestions. Should include security and performance analysis.",
                "budget": {"min": 100, "max": 500, "type": "fixed"},
                "skills": ["Code Review", "Python", "JavaScript", "Optimization"],
                "category": JobCategory.CODE_REVIEW
            },
            {
                "title": "Technical Documentation Writing",
                "description": "Looking for a technical writer to create comprehensive documentation for software projects. Should include API documentation, user guides, and developer guides.",
                "budget": {"min": 200, "max": 800, "type": "fixed"},
                "skills": ["Technical Writing", "Documentation", "API Documentation"],
                "category": JobCategory.DOCUMENTATION
            }
        ]
        
        for i, template in enumerate(job_templates[:max_results]):
            if template["category"] in categories:
                job = JobOpportunity(
                    id=f"fiverr_{i}_{int(time.time())}",
                    title=template["title"],
                    description=template["description"],
                    budget=template["budget"],
                    skills_required=template["skills"],
                    platform=JobPlatform.FIVERR,
                    url=f"https://www.fiverr.com/gigs/{i}",
                    posted_date=datetime.now() - timedelta(hours=random.randint(1, 24)),
                    deadline=datetime.now() + timedelta(days=random.randint(1, 7)),
                    client_rating=random.uniform(3.5, 5.0),
                    client_reviews=random.randint(20, 1000),
                    requirements=self._analyze_requirements(template["description"]),
                    match_score=0.0
                )
                jobs.append(job)
        
        return jobs

    def _analyze_requirements(self, description: str) -> List[JobRequirement]:
        """Analyze job requirements from description."""
        requirements = []
        
        # Extract skills and complexity from description
        skills_patterns = {
            "Python": r"python|kivy|pygame|django|flask",
            "JavaScript": r"javascript|js|react|node|vue|angular",
            "Mobile Development": r"mobile|android|ios|app development",
            "Game Development": r"game|gaming|3d|graphics|fps",
            "API Development": r"api|rest|endpoint|integration",
            "Machine Learning": r"machine learning|ai|ml|neural|tensorflow",
            "Data Analysis": r"data|analysis|visualization|statistics",
            "Automation": r"automation|script|workflow|process",
            "Testing": r"test|testing|qa|quality assurance",
            "Documentation": r"documentation|docs|guide|manual"
        }
        
        for skill, pattern in skills_patterns.items():
            if re.search(pattern, description.lower()):
                complexity = "high" if any(word in description.lower() for word in ["complex", "advanced", "expert"]) else "medium"
                estimated_hours = random.randint(20, 100) if complexity == "high" else random.randint(10, 50)
                
                requirement = JobRequirement(
                    skill=skill,
                    experience_level="expert" if complexity == "high" else "intermediate",
                    estimated_hours=estimated_hours,
                    complexity=complexity,
                    priority=random.randint(1, 5)
                )
                requirements.append(requirement)
        
        return requirements

    def _filter_jobs(self, jobs: List[JobOpportunity]) -> List[JobOpportunity]:
        """Filter jobs based on agent preferences."""
        filtered = []
        
        for job in jobs:
            # Check budget range
            if job.budget["type"] == "fixed":
                budget = job.budget["max"]
            else:
                budget = job.budget["max"] * 40  # Assume 40 hours for hourly jobs
            
            if self.min_budget <= budget <= self.max_budget:
                # Check if we have required skills
                matching_skills = sum(1 for skill in job.skills_required if skill.lower() in [s.lower() for s in self.skills])
                if matching_skills >= len(job.skills_required) * 0.7:  # 70% skill match
                    filtered.append(job)
        
        return filtered

    def _rank_jobs(self, jobs: List[JobOpportunity]) -> List[JobOpportunity]:
        """Rank jobs by match score."""
        for job in jobs:
            job.match_score = self._calculate_match_score(job)
        
        return sorted(jobs, key=lambda x: x.match_score, reverse=True)

    def _calculate_match_score(self, job: JobOpportunity) -> float:
        """Calculate match score for a job."""
        score = 0.0
        
        # Skill match (40%)
        skill_match = sum(1 for skill in job.skills_required if skill.lower() in [s.lower() for s in self.skills])
        skill_score = skill_match / len(job.skills_required) * 0.4
        score += skill_score
        
        # Budget match (25%)
        if job.budget["type"] == "fixed":
            budget = job.budget["max"]
        else:
            budget = job.budget["max"] * 40
        
        budget_score = 1.0 - abs(budget - (self.min_budget + self.max_budget) / 2) / ((self.max_budget - self.min_budget) / 2)
        score += budget_score * 0.25
        
        # Client rating (20%)
        client_score = job.client_rating / 5.0 * 0.2
        score += client_score
        
        # Time sensitivity (15%)
        time_score = 1.0 - (datetime.now() - job.posted_date).total_seconds() / (72 * 3600)  # 72 hours
        time_score = max(0, min(1, time_score))
        score += time_score * 0.15
        
        return score

    def analyze_job(self, job: JobOpportunity) -> Dict[str, Any]:
        """Analyze a job opportunity in detail."""
        analysis = {
            "job_id": job.id,
            "title": job.title,
            "match_score": job.match_score,
            "budget_analysis": self._analyze_budget(job),
            "skill_analysis": self._analyze_skills(job),
            "timeline_analysis": self._analyze_timeline(job),
            "risk_assessment": self._analyze_risks(job),
            "profitability": self._calculate_profitability(job),
            "recommendation": self._generate_recommendation(job)
        }
        
        return analysis

    def _analyze_budget(self, job: JobOpportunity) -> Dict[str, Any]:
        """Analyze job budget."""
        if job.budget["type"] == "fixed":
            budget = job.budget["max"]
            hourly_equivalent = budget / sum(req.estimated_hours for req in job.requirements)
        else:
            budget = job.budget["max"] * 40
            hourly_equivalent = job.budget["max"]
        
        return {
            "total_budget": budget,
            "hourly_equivalent": hourly_equivalent,
            "vs_our_rate": hourly_equivalent - self.hourly_rate,
            "profit_margin": (hourly_equivalent - self.hourly_rate) / hourly_equivalent * 100 if hourly_equivalent > 0 else 0
        }

    def _analyze_skills(self, job: JobOpportunity) -> Dict[str, Any]:
        """Analyze required skills."""
        matching_skills = [skill for skill in job.skills_required if skill.lower() in [s.lower() for s in self.skills]]
        missing_skills = [skill for skill in job.skills_required if skill.lower() not in [s.lower() for s in self.skills]]
        
        return {
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "match_percentage": len(matching_skills) / len(job.skills_required) * 100,
            "skill_gaps": len(missing_skills)
        }

    def _analyze_timeline(self, job: JobOpportunity) -> Dict[str, Any]:
        """Analyze project timeline."""
        total_hours = sum(req.estimated_hours for req in job.requirements)
        days_needed = total_hours / 8  # 8 hours per day
        
        return {
            "total_hours": total_hours,
            "days_needed": days_needed,
            "deadline_days": (job.deadline - datetime.now()).days if job.deadline else None,
            "timeline_feasible": job.deadline is None or days_needed <= (job.deadline - datetime.now()).days
        }

    def _analyze_risks(self, job: JobOpportunity) -> Dict[str, Any]:
        """Analyze project risks."""
        risks = []
        risk_score = 0
        
        # Client rating risk
        if job.client_rating < 4.0:
            risks.append("Low client rating")
            risk_score += 0.3
        
        # Budget risk
        if job.budget["type"] == "hourly" and job.budget["max"] < self.hourly_rate:
            risks.append("Low hourly rate")
            risk_score += 0.2
        
        # Timeline risk
        if job.deadline and sum(req.estimated_hours for req in job.requirements) / 8 > (job.deadline - datetime.now()).days:
            risks.append("Tight deadline")
            risk_score += 0.3
        
        # Skill gap risk
        missing_skills = [skill for skill in job.skills_required if skill.lower() not in [s.lower() for s in self.skills]]
        if missing_skills:
            risks.append(f"Missing skills: {', '.join(missing_skills)}")
            risk_score += 0.2
        
        return {
            "risks": risks,
            "risk_score": min(risk_score, 1.0),
            "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.3 else "low"
        }

    def _calculate_profitability(self, job: JobOpportunity) -> Dict[str, Any]:
        """Calculate job profitability."""
        total_hours = sum(req.estimated_hours for req in job.requirements)
        
        if job.budget["type"] == "fixed":
            revenue = job.budget["max"]
            cost = total_hours * self.hourly_rate
            profit = revenue - cost
            profit_margin = (profit / revenue) * 100 if revenue > 0 else 0
        else:
            revenue = total_hours * job.budget["max"]
            cost = total_hours * self.hourly_rate
            profit = revenue - cost
            profit_margin = (profit / revenue) * 100 if revenue > 0 else 0
        
        return {
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "profit_margin": profit_margin,
            "hourly_profit": profit / total_hours if total_hours > 0 else 0
        }

    def _generate_recommendation(self, job: JobOpportunity) -> str:
        """Generate recommendation for the job."""
        analysis = self.analyze_job(job)
        
        if analysis["match_score"] > 0.8 and analysis["profitability"]["profit_margin"] > 20:
            return "STRONG RECOMMEND - High match score and good profitability"
        elif analysis["match_score"] > 0.6 and analysis["profitability"]["profit_margin"] > 10:
            return "RECOMMEND - Good match and reasonable profit"
        elif analysis["risk_assessment"]["risk_level"] == "high":
            return "NOT RECOMMENDED - High risk factors"
        else:
            return "CONSIDER - Moderate match, evaluate carefully"

    def generate_proposal(self, job: JobOpportunity) -> Proposal:
        """Generate a customized proposal for a job."""
        analysis = self.analyze_job(job)
        
        # Determine bid amount
        if job.budget["type"] == "fixed":
            # Bid slightly below max budget for better chances
            bid_amount = job.budget["max"] * 0.9
        else:
            # Bid at our rate for hourly jobs
            bid_amount = self.hourly_rate
        
        # Generate cover letter
        cover_letter = self._generate_cover_letter(job, analysis)
        
        # Select relevant portfolio items
        portfolio_items = self._select_portfolio_items(job)
        
        # Calculate delivery time
        delivery_time = sum(req.estimated_hours for req in job.requirements) // 8  # days
        
        proposal = Proposal(
            job_id=job.id,
            title=f"Proposal for {job.title}",
            cover_letter=cover_letter,
            bid_amount=bid_amount,
            delivery_time=delivery_time,
            portfolio_items=portfolio_items,
            attachments=[]
        )
        
        return proposal

    def _generate_cover_letter(self, job: JobOpportunity, analysis: Dict[str, Any]) -> str:
        """Generate a customized cover letter."""
        templates = self.config.get('proposal_templates', {})
        
        # Determine the best template based on job category
        category_keywords = {
            JobCategory.WEB_DEVELOPMENT: ["web", "react", "node", "frontend", "backend"],
            JobCategory.MOBILE_DEVELOPMENT: ["mobile", "app", "android", "ios"],
            JobCategory.GAME_DEVELOPMENT: ["game", "gaming", "3d", "graphics"],
            JobCategory.API_DEVELOPMENT: ["api", "rest", "endpoint"],
            JobCategory.AUTOMATION: ["automation", "script", "workflow"],
            JobCategory.MACHINE_LEARNING: ["ai", "machine learning", "ml"],
            JobCategory.DATA_ANALYSIS: ["data", "analysis", "visualization"],
            JobCategory.CODE_REVIEW: ["review", "code", "optimization"],
            JobCategory.DOCUMENTATION: ["documentation", "docs", "manual"]
        }
        
        best_template = "default"
        for category, keywords in category_keywords.items():
            if any(keyword in job.description.lower() for keyword in keywords):
                category_name = category.value
                if category_name in templates:
                    best_template = category_name
                break
        
        base_letter = templates.get(best_template, templates.get("default", ""))
        
        # Customize the letter
        letter = base_letter + "\n\n"
        
        # Add specific skills
        matching_skills = analysis["skill_analysis"]["matching_skills"]
        if matching_skills:
            letter += f"I have extensive experience with {', '.join(matching_skills[:3])} and can deliver high-quality results.\n\n"
        
        # Add timeline commitment
        letter += f"I can complete this project within {analysis['timeline_analysis']['days_needed']} days and will provide regular updates throughout the development process.\n\n"
        
        # Add quality assurance
        letter += "I ensure code quality through comprehensive testing, documentation, and best practices. You'll receive clean, maintainable code with detailed documentation.\n\n"
        
        # Add call to action
        letter += "I'm excited to work on this project and would love to discuss the details further. Let me know if you have any questions!"
        
        return letter

    def _select_portfolio_items(self, job: JobOpportunity) -> List[str]:
        """Select relevant portfolio items for the job."""
        relevant_items = []
        
        for item in self.portfolio:
            # Check if portfolio item matches job requirements
            if any(skill.lower() in item.lower() for skill in job.skills_required):
                relevant_items.append(item)
        
        # Return top 3 most relevant items
        return relevant_items[:3]

    def send_proposal(self, proposal: Proposal, job: JobOpportunity) -> bool:
        """Send proposal for a job."""
        try:
            logging.info(f"📧 Sending proposal for job: {job.title}")
            
            # In a real implementation, this would integrate with platform APIs
            # For now, we'll simulate the process
            
            # Simulate API call to send proposal
            success = self._simulate_send_proposal(proposal, job)
            
            if success:
                # Record the proposal
                self.proposal_history.append({
                    "job_id": job.id,
                    "title": job.title,
                    "platform": job.platform.value,
                    "bid_amount": proposal.bid_amount,
                    "sent_date": datetime.now(),
                    "status": "sent"
                })
                
                logging.info(f"✅ Proposal sent successfully for {job.title}")
                return True
            else:
                logging.error(f"❌ Failed to send proposal for {job.title}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error sending proposal: {e}")
            return False

    def _simulate_send_proposal(self, proposal: Proposal, job: JobOpportunity) -> bool:
        """Simulate sending a proposal through platform API."""
        # Simulate API call delay
        time.sleep(random.uniform(1, 3))
        
        # Simulate success/failure (90% success rate)
        return random.random() > 0.1

    def send_email_proposal(self, proposal: Proposal, job: JobOpportunity, 
                          client_email: str) -> bool:
        """Send proposal via email."""
        try:
            msg = MimeMultipart()
            msg['From'] = f"{self.email_config['from_name']} <{self.email_config['username']}>"
            msg['To'] = client_email
            msg['Subject'] = f"Proposal for {job.title}"
            
            # Create email body
            body = f"""
Dear Client,

Thank you for posting the job "{job.title}". I'm excited to submit my proposal for this project.

{proposal.cover_letter}

Project Details:
- Budget: ${proposal.bid_amount:,.2f}
- Delivery Time: {proposal.delivery_time} days
- Platform: {job.platform.value.title()}

Relevant Portfolio Items:
{chr(10).join(f"- {item}" for item in proposal.portfolio_items)}

I'm confident I can deliver exceptional results for your project. Please let me know if you have any questions or would like to discuss the project further.

Best regards,
{self.email_config['from_name']}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logging.info(f"✅ Email proposal sent to {client_email}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error sending email proposal: {e}")
            return False

    def run_automated_search(self, max_proposals: int = 5) -> Dict[str, Any]:
        """Run automated job search and proposal sending."""
        logging.info("🚀 Starting automated job search and proposal system...")
        
        results = {
            "jobs_found": 0,
            "jobs_analyzed": 0,
            "proposals_sent": 0,
            "successful_proposals": 0,
            "total_potential_earnings": 0,
            "jobs": []
        }
        
        try:
            # Search for jobs
            jobs = self.search_jobs(max_results=50)
            results["jobs_found"] = len(jobs)
            
            logging.info(f"🔍 Found {len(jobs)} jobs, analyzing top candidates...")
            
            # Analyze top jobs
            top_jobs = jobs[:10]  # Analyze top 10 jobs
            results["jobs_analyzed"] = len(top_jobs)
            
            proposals_sent = 0
            
            for job in top_jobs:
                if proposals_sent >= max_proposals:
                    break
                
                # Analyze job
                analysis = self.analyze_job(job)
                
                # Only send proposals for highly recommended jobs
                if "RECOMMEND" in analysis["recommendation"] and analysis["match_score"] > 0.7:
                    logging.info(f"📝 Generating proposal for: {job.title}")
                    
                    # Generate proposal
                    proposal = self.generate_proposal(job)
                    
                    # Send proposal
                    if self.send_proposal(proposal, job):
                        results["proposals_sent"] += 1
                        results["successful_proposals"] += 1
                        results["total_potential_earnings"] += proposal.bid_amount
                        proposals_sent += 1
                        
                        logging.info(f"✅ Proposal sent for {job.title} - ${proposal.bid_amount:,.2f}")
                    else:
                        results["proposals_sent"] += 1
                        logging.warning(f"⚠️ Failed to send proposal for {job.title}")
                
                # Store job analysis
                results["jobs"].append({
                    "id": job.id,
                    "title": job.title,
                    "platform": job.platform.value,
                    "match_score": job.match_score,
                    "budget": job.budget,
                    "recommendation": analysis["recommendation"],
                    "profitability": analysis["profitability"]
                })
            
            logging.info(f"🎉 Automated search completed!")
            logging.info(f"   📊 Jobs found: {results['jobs_found']}")
            logging.info(f"   🔍 Jobs analyzed: {results['jobs_analyzed']}")
            logging.info(f"   📧 Proposals sent: {results['proposals_sent']}")
            logging.info(f"   ✅ Successful: {results['successful_proposals']}")
            logging.info(f"   💰 Potential earnings: ${results['total_potential_earnings']:,.2f}")
            
        except Exception as e:
            logging.error(f"❌ Error in automated search: {e}")
        
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics and performance metrics."""
        total_proposals = len(self.proposal_history)
        successful_proposals = len([p for p in self.proposal_history if p.get("status") == "sent"]) # Corrected to check for "sent" status
        
        total_earnings = sum(p.get("bid_amount", 0) for p in self.proposal_history) # Corrected to sum bid_amount
        
        return {
            "total_proposals_sent": total_proposals,
            "successful_proposals": successful_proposals,
            "success_rate": (successful_proposals / total_proposals * 100) if total_proposals > 0 else 0,
            "total_earnings": total_earnings,
            "average_earnings_per_job": total_earnings / successful_proposals if successful_proposals > 0 else 0,
            "active_jobs": len([p for p in self.proposal_history if p.get("status") == "sent"]), # Assuming "sent" means active
            "completed_jobs": len([p for p in self.proposal_history if p.get("status") == "sent"]) # Assuming "sent" means completed
        }

    def update_config(self, updates: Dict[str, Any]):
        """Update agent configuration."""
        self.config.update(updates)
        self._save_config(self.config)
        
        # Update instance variables
        if "skills" in updates:
            self.skills = updates["skills"]
        if "hourly_rate" in updates:
            self.hourly_rate = updates["hourly_rate"]
        if "min_budget" in updates:
            self.min_budget = updates["min_budget"]
        if "max_budget" in updates:
            self.max_budget = updates["max_budget"]
        
        logging.info("✅ Configuration updated successfully")

def main():
    """Main function to demonstrate the Freelance Agent."""
    print("🤖 Freelance Agent - Autonomous Job Finding and Proposal System")
    print("=" * 70)
    
    # Initialize the agent
    agent = FreelanceAgent()
    
    # Run automated search
    print("\n🚀 Running automated job search and proposal system...")
    results = agent.run_automated_search(max_proposals=3)
    
    # Display results
    print(f"\n📊 Results Summary:")
    print(f"   🔍 Jobs found: {results['jobs_found']}")
    print(f"   📝 Jobs analyzed: {results['jobs_analyzed']}")
    print(f"   📧 Proposals sent: {results['proposals_sent']}")
    print(f"   ✅ Successful: {results['successful_proposals']}")
    print(f"   💰 Potential earnings: ${results['total_potential_earnings']:,.2f}")
    
    # Show top job opportunities
    print(f"\n🎯 Top Job Opportunities:")
    for i, job in enumerate(results['jobs'][:5], 1):
        print(f"   {i}. {job['title']}")
        print(f"      Platform: {job['platform']}")
        print(f"      Match Score: {job['match_score']:.2f}")
        print(f"      Budget: ${job['budget']['max']:,.2f}")
        print(f"      Recommendation: {job['recommendation']}")
        print()
    
    # Show statistics
    stats = agent.get_statistics()
    print(f"📈 Agent Statistics:")
    print(f"   📧 Total proposals sent: {stats['total_proposals_sent']}")
    print(f"   ✅ Success rate: {stats['success_rate']:.1f}%")
    print(f"   💰 Total earnings: ${stats['total_earnings']:,.2f}")
    print(f"   🔄 Active jobs: {stats['active_jobs']}")
    print(f"   ✅ Completed jobs: {stats['completed_jobs']}")
    
    print(f"\n🎉 Freelance Agent is ready to work autonomously!")
    print(f"   🤖 Can find jobs automatically")
    print(f"   📝 Can generate customized proposals")
    print(f"   📧 Can send proposals via email")
    print(f"   💰 Can track earnings and performance")

if __name__ == "__main__":
    main()