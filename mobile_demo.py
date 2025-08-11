#!/usr/bin/env python3
"""
📱 Mobile App Demo - Freelance Agent Monitor
Simple demonstration of mobile app features
"""

import time
import random
from datetime import datetime

class MobileAppDemo:
    """Simple mobile app demo."""
    
    def __init__(self):
        self.earnings = random.uniform(8000, 15000)
        self.proposals = random.randint(5, 12)
        self.tasks = random.randint(2, 6)
        self.performance = random.uniform(85, 98)
        self.success_rate = random.uniform(75, 95)
        self.platform = random.choice(["Upwork", "Freelancer", "Fiverr"])
        self.skills = random.sample(["Python", "React", "Node.js", "Mobile Dev", "AI/ML"], 3)
        
        self.goals = [
            {"name": "Daily Earnings", "target": 500, "current": random.uniform(300, 600)},
            {"name": "Weekly Earnings", "target": 3000, "current": random.uniform(2000, 4000)},
            {"name": "Proposals Sent", "target": 10, "current": random.randint(5, 15)}
        ]
        
        self.projects = [
            {"name": "Mobile Game", "client": "GameStudio", "budget": 8000, "progress": random.uniform(20, 80)},
            {"name": "AI System", "client": "TechCorp", "budget": 5000, "progress": random.uniform(10, 60)},
            {"name": "Web App", "client": "StartupXYZ", "budget": 3000, "progress": random.uniform(40, 90)}
        ]
        
        self.notifications = [
            "💰 Payment received: $2,500",
            "📝 Proposal accepted!",
            "🎯 Goal achieved: Daily earnings",
            "📱 New high-paying job found",
            "✅ Project completed successfully"
        ]

    def show_dashboard(self):
        """Show mobile app dashboard."""
        print("📱 FREELANCE AGENT MOBILE APP")
        print("=" * 50)
        print(f"💰 Current Earnings: ${self.earnings:,.2f}")
        print(f"📝 Active Proposals: {self.proposals}")
        print(f"🛠️ Pending Tasks: {self.tasks}")
        print(f"📈 Agent Performance: {self.performance:.1f}%")
        print(f"✅ Success Rate: {self.success_rate:.1f}%")
        print(f"🏆 Best Platform: {self.platform}")
        print(f"🎯 Top Skills: {', '.join(self.skills)}")
        
        print(f"\n🎯 GOALS:")
        for goal in self.goals:
            progress = (goal['current'] / goal['target']) * 100
            status = "✅" if goal['current'] >= goal['target'] else "⏳"
            print(f"   {status} {goal['name']}: ${goal['current']:,.0f}/${goal['target']:,.0f} ({progress:.1f}%)")
        
        print(f"\n📋 PROJECTS:")
        for project in self.projects:
            status = "✅" if project['progress'] >= 100 else "🔄"
            print(f"   {status} {project['name']} ({project['client']}) - ${project['budget']:,.0f} - {project['progress']:.1f}%")
        
        print(f"\n📱 RECENT NOTIFICATIONS:")
        for i, notification in enumerate(self.notifications[-3:], 1):
            print(f"   {i}. {notification}")
        
        print(f"\n📊 ANALYTICS:")
        daily_avg = self.earnings / 30
        weekly_avg = self.earnings / 4
        print(f"   💰 Daily Average: ${daily_avg:,.2f}")
        print(f"   💰 Weekly Average: ${weekly_avg:,.2f}")
        print(f"   📊 Project Success: {self.success_rate:.1f}%")
        print(f"   🎯 Proposal Rate: {self.proposals * 10}%")
        
        print(f"\n🎉 MOBILE APP FEATURES:")
        print(f"   📱 Real-time monitoring")
        print(f"   🔔 Push notifications")
        print(f"   📊 Live analytics")
        print(f"   🎯 Goal tracking")
        print(f"   📋 Project management")
        print(f"   💰 Financial tracking")
        print(f"   📈 Performance metrics")
        print(f"   🏆 Platform insights")

    def simulate_updates(self, duration=30):
        """Simulate real-time updates."""
        print(f"\n🔄 Simulating real-time updates for {duration} seconds...")
        print("Press Ctrl+C to stop")
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                # Update values
                self.earnings += random.uniform(-100, 200)
                self.proposals = max(0, self.proposals + random.randint(-1, 1))
                self.tasks = max(0, self.tasks + random.randint(-1, 1))
                self.performance = max(50, min(100, self.performance + random.uniform(-2, 2)))
                
                # Update project progress
                for project in self.projects:
                    if project['progress'] < 100:
                        project['progress'] = min(100, project['progress'] + random.uniform(0, 5))
                
                # Show current status
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] 💰${self.earnings:,.0f} 📝{self.proposals} 🛠️{self.tasks} 📈{self.performance:.0f}%")
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Simulation stopped")

def main():
    """Main function."""
    app = MobileAppDemo()
    app.show_dashboard()
    app.simulate_updates(20)

if __name__ == "__main__":
    main()