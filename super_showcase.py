#!/usr/bin/env python3
"""
🚀 Super Showcase - runs demos for all builders
"""

from web_framework_builder import WebFrameworkBuilder
from cross_platform_mobile_builder import CrossPlatformMobileBuilder
from cloud_devops_builder import CloudDevOpsBuilder
from ml_tools_builder import MLToolsBuilder
from security_tools_builder import SecurityToolsBuilder
from data_science_builder import DataScienceBuilder
from advanced_game_builder import AdvancedGameBuilder
from automation_builder import AutomationBuilder
from business_intelligence_builder import BusinessIntelligenceBuilder
from search_engine_builder import SearchEngineBuilder
from creative_tools_builder import CreativeToolsBuilder
from education_platform_builder import EducationPlatformBuilder
from healthcare_tools_builder import HealthcareToolsBuilder
from financial_tools_builder import FinancialToolsBuilder
from iot_builder import IoTBuilder


def main():
    print("\n🚀 Running Super Showcase (all modules)\n" + "="*60)

    print("\n🌐 Web Framework Builder")
    print(WebFrameworkBuilder().demo())

    print("\n📱 Cross-Platform Mobile Builder")
    print(CrossPlatformMobileBuilder().demo())

    print("\n☁️ Cloud & DevOps Builder")
    print(CloudDevOpsBuilder().demo())

    print("\n🎯 ML Tools Builder")
    print(MLToolsBuilder().demo())

    print("\n🔒 Security Tools Builder")
    print(SecurityToolsBuilder().demo())

    print("\n📊 Data Science Builder")
    print(DataScienceBuilder().demo())

    print("\n🎮 Advanced Game Builder")
    print(AdvancedGameBuilder().demo())

    print("\n🤖 Automation Builder")
    print(AutomationBuilder().demo())

    print("\n📈 Business Intelligence Builder")
    print(BusinessIntelligenceBuilder().demo())

    print("\n🔍 Search Engine Builder")
    print(SearchEngineBuilder().demo())

    print("\n🎨 Creative Tools Builder")
    print(CreativeToolsBuilder().demo())

    print("\n📚 Education Platform Builder")
    print(EducationPlatformBuilder().demo())

    print("\n🏥 Healthcare Tools Builder")
    print(HealthcareToolsBuilder().demo())

    print("\n🏦 Financial Tools Builder")
    print(FinancialToolsBuilder().demo())

    print("\n🏭 IoT Builder")
    print(IoTBuilder().demo())

    print("\n✅ Super Showcase completed.")


if __name__ == "__main__":
    main()