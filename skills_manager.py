#!/usr/bin/env python3
"""
Meta Business Agent Skills Manager
Manage skills (behavioral instructions) for WhatsApp Business Agent
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Represents a Meta Business Agent skill"""
    title: str
    description: str
    skill: str
    skill_id: Optional[str] = None

    def validate(self):
        """Validate skill parameters according to Meta's limits"""
        if len(self.title) > 64:
            raise ValueError(f"Title too long: {len(self.title)} chars (max 64)")
        
        if not self.title.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Title must contain only lowercase letters, numbers, and hyphens")
        
        if self.title != self.title.lower():
            raise ValueError("Title must be lowercase")
        
        if len(self.description) > 1024:
            raise ValueError(f"Description too long: {len(self.description)} chars (max 1024)")
        
        if len(self.skill) > 20000:
            raise ValueError(f"Skill content too long: {len(self.skill)} chars (max 20000)")

    def to_api_dict(self) -> Dict[str, str]:
        """Convert to API request format"""
        return {
            "title": self.title,
            "description": self.description,
            "skill": self.skill
        }


class SkillsManager:
    """Manages Meta Business Agent skills via API"""
    
    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"https://api.facebook.com/{phone_number_id}/agent_config/skills"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-API-Version": "2.0.0"
        }

    def create_skill(self, skill: Skill) -> Dict[str, Any]:
        """Create a new skill"""
        skill.validate()
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=skill.to_api_dict(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"✓ Created skill '{skill.title}': {result.get('id')}")
            return {"success": True, "data": result}
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error creating skill '{skill.title}': {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return {"success": False, "error": str(e)}

    def list_skills(self) -> Dict[str, Any]:
        """List all skills"""
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            skills = result.get('data', [])
            logger.info(f"✓ Retrieved {len(skills)} skills")
            return {"success": True, "data": skills}
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error listing skills: {e}")
            return {"success": False, "error": str(e)}

    def get_skill(self, skill_id: str) -> Dict[str, Any]:
        """Get a specific skill by ID"""
        try:
            response = requests.get(
                f"{self.base_url}/{skill_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"✓ Retrieved skill {skill_id}")
            return {"success": True, "data": result}
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error getting skill {skill_id}: {e}")
            return {"success": False, "error": str(e)}

    def update_skill(self, skill_id: str, skill: Skill) -> Dict[str, Any]:
        """Update an existing skill"""
        skill.validate()
        
        try:
            response = requests.put(
                f"{self.base_url}/{skill_id}",
                headers=self.headers,
                json=skill.to_api_dict(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"✓ Updated skill {skill_id}")
            return {"success": True, "data": result}
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error updating skill {skill_id}: {e}")
            return {"success": False, "error": str(e)}

    def delete_skill(self, skill_id: str) -> Dict[str, Any]:
        """Delete a skill"""
        try:
            response = requests.delete(
                f"{self.base_url}/{skill_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"✓ Deleted skill {skill_id}")
            return {"success": True}
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error deleting skill {skill_id}: {e}")
            return {"success": False, "error": str(e)}

    def bulk_create_skills(self, skills: List[Skill]) -> Dict[str, Any]:
        """Create multiple skills"""
        results = {"created": [], "failed": []}
        
        for skill in skills:
            result = self.create_skill(skill)
            if result["success"]:
                results["created"].append(skill.title)
            else:
                results["failed"].append({"skill": skill.title, "error": result.get("error")})
        
        return results


# Predefined skills for RSI course (Responsabilidad Social en la Industria)
RSI_SKILLS = [
    Skill(
        title="greeting-skill",
        description="Apply when the customer first messages the agent or says hello/hi/hola",
        skill="""When a student sends their first message or greeting:
1) Respond warmly: "¡Hola! Soy el asistente del curso Responsabilidad Social en la Industria - Otoño 2026."
2) Briefly introduce yourself: "Puedo ayudarte con economía circular, sostenibilidad industrial y RSC."
3) Ask how you can help: "¿En qué puedo ayudarte hoy?"
4) Keep tone professional yet friendly
5) Use emojis sparingly (only ♻️ for circular economy, 🌱 for sustainability, 🤝 for RSC)"""
    ),
    
    Skill(
        title="circular-economy-questions",
        description="Apply when student asks about economía circular, circular economy, recycling, waste reduction, or resource optimization",
        skill="""When asked about circular economy topics:
1) Provide a clear, concise explanation (max 3 lines)
2) Focus on practical examples from industry
3) Key concepts to mention:
   - Minimizing waste and maximizing resource value
   - Closed-loop systems
   - Reduce, reuse, recycle, regenerate
   - Business models: product-as-service, sharing economy
4) If the question is too broad, ask for clarification on a specific aspect
5) Always connect to RSI/CSR principles
6) Use emoji: ♻️"""
    ),
    
    Skill(
        title="sustainability-questions",
        description="Apply when student asks about sostenibilidad, sustentabilidad, sustainability, ESG, or environmental topics",
        skill="""When asked about sustainability:
1) Explain using the three pillars: environmental, social, and economic
2) Keep responses to 3 lines maximum
3) Include industry-relevant examples
4) Key frameworks to reference when relevant:
   - Triple bottom line (people, planet, profit)
   - SDGs (Sustainable Development Goals)
   - ESG criteria (Environmental, Social, Governance)
5) Ask clarifying questions if topic is too broad
6) Use emoji: 🌱"""
    ),
    
    Skill(
        title="csr-rsc-questions",
        description="Apply when student asks about RSC, CSR, corporate social responsibility, responsabilidad social corporativa, or business ethics",
        skill="""When asked about Corporate Social Responsibility:
1) Define CSR as company commitment to society and environment beyond legal requirements
2) Mention key areas:
   - Labor practices and human rights
   - Environmental responsibility
   - Community engagement
   - Ethical business practices
   - Stakeholder management
3) Keep response to 3 lines
4) Provide practical examples from known companies
5) Connect to economic benefits (reputation, employee retention, customer loyalty)
6) Use emoji: 🤝"""
    ),
    
    Skill(
        title="assignment-help",
        description="Apply when student mentions tarea, entrega, trabajo, assignment, homework, or asks for help with coursework",
        skill="""When student asks about assignments:
1) First, request their information: "Para ayudarte mejor, necesito tu nombre completo y matrícula."
2) Ask which specific assignment: "¿Sobre qué tarea necesitas ayuda?"
3) Once you have context, provide guidance on:
   - Key concepts to address
   - Recommended structure
   - Resources to review
4) Do NOT solve the assignment for them
5) Do NOT provide complete answers
6) Guide them to think critically
7) Offer to clarify specific concepts
8) Use emoji: 📚"""
    ),
    
    Skill(
        title="course-information",
        description="Apply when student asks about syllabus, schedule, grading, course dates, profesor, or general course information",
        skill="""When asked about course information:
1) Provide the requested information clearly
2) Known course details:
   - Course: Responsabilidad Social en la Industria
   - Semester: Otoño 2026
   - Main topics: Circular economy, Industrial sustainability, CSR
3) If you don't have specific information (dates, professor details, grading rubrics):
   - Be honest: "No tengo esa información específica en este momento."
   - Suggest: "Te recomiendo revisar el syllabus o consultar directamente con el profesor."
4) Never invent dates, percentages, or policies
5) Use emoji: 📅 for dates, 📧 for contact info"""
    ),
    
    Skill(
        title="exam-preparation",
        description="Apply when student asks about examen, exam, test, quiz, evaluation, or study tips",
        skill="""When student asks about exam preparation:
1) Offer to review key concepts from the course
2) Suggest focus areas:
   - Circular economy principles and business models
   - Sustainability frameworks (triple bottom line, SDGs)
   - CSR strategies and stakeholder management
   - Industry case studies
3) Recommend study methods:
   - Create concept maps
   - Practice with real company examples
   - Form study groups
   - Review class materials systematically
4) Ask what specific topics they find challenging
5) Do NOT provide exam questions or answers
6) Use emoji: 📝"""
    ),
    
    Skill(
        title="examples-case-studies",
        description="Apply when student asks for ejemplos, examples, casos, case studies, or real company instances",
        skill="""When student requests examples or case studies:
1) Provide 2-3 specific, real-world examples
2) Well-known companies to reference:
   - Circular economy: Patagonia (repair program), Interface (carpet recycling)
   - Sustainability: Unilever (Sustainable Living Plan), IKEA (renewable materials)
   - CSR: Ben & Jerry's (social mission), Natura (B Corp certification)
3) For each example, briefly explain:
   - What they did
   - Why it matters
   - Business/social impact
4) Keep each example to 1-2 lines
5) Encourage students to research more: "Te recomiendo investigar más sobre [company] para tu tarea."
6) Use emoji: 💡"""
    ),
    
    Skill(
        title="unclear-or-offtopic",
        description="Apply when the message is unclear, off-topic, not related to the course, or you cannot understand the intent",
        skill="""When message is unclear or off-topic:
1) Politely acknowledge: "No estoy seguro de entender tu pregunta."
2) Redirect to course topics: "Puedo ayudarte con temas de economía circular, sostenibilidad o RSC."
3) Ask for clarification: "¿Puedes ser más específico sobre qué necesitas?"
4) If completely off-topic (jokes, personal chat, unrelated subjects):
   - Gently redirect: "Soy un asistente académico especializado en RSI. ¿Tienes alguna consulta sobre el curso?"
5) Maintain professional but friendly tone
6) Do NOT engage with inappropriate content - respond: "Por favor, mantengamos la conversación enfocada en temas del curso."
"""
    ),
    
    Skill(
        title="human-handoff",
        description="Apply when student explicitly asks for the professor, needs urgent help, has complaints, or issue is beyond agent capabilities",
        skill="""When human escalation is needed:
Escalate to human (professor) when:
- Student explicitly requests to speak with professor
- Complex grading disputes or complaints
- Personal/sensitive academic issues
- Technical problems with course platform
- Emergency situations

Response format:
1) Acknowledge: "Entiendo que necesitas hablar directamente con el profesor."
2) Provide action: "Te recomiendo enviar un correo a [email if known] o consultar el syllabus para información de contacto."
3) Or: "Puedo pasar tu consulta al profesor. Por favor deja tu nombre, matrícula y describe tu situación."
4) Never promise immediate professor response
5) Set expectations: "El profesor responderá lo antes posible."
6) Use emoji: 👨‍🏫"""
    )
]


def main():
    """Main function - demonstrates usage"""
    print("=" * 70)
    print("Meta Business Agent Skills Manager - RSI Course")
    print("=" * 70)
    
    # Load credentials from environment
    phone_number_id = os.getenv("PHONE_NUMBER_ID", "")
    access_token = os.getenv("WHATSAPP_TOKEN", "")
    
    if not phone_number_id or not access_token:
        print("\n⚠️  Missing credentials!")
        print("Please set environment variables:")
        print("  - PHONE_NUMBER_ID")
        print("  - WHATSAPP_TOKEN")
        print("\nOr use the interactive mode to view predefined skills.")
        print("\n" + "=" * 70)
        
        # Show predefined skills even without credentials
        print(f"\n📚 Predefined RSI Skills ({len(RSI_SKILLS)} skills):\n")
        for i, skill in enumerate(RSI_SKILLS, 1):
            print(f"{i}. {skill.title}")
            print(f"   Description: {skill.description}")
            print(f"   Skill length: {len(skill.skill)} characters")
            print()
        
        print("To upload these skills to Meta Business Agent:")
        print("1. Set environment variables (PHONE_NUMBER_ID, WHATSAPP_TOKEN)")
        print("2. Run: python skills_manager.py --upload")
        print("3. Or use the Meta Business Suite interface")
        return
    
    # Initialize manager
    manager = SkillsManager(phone_number_id, access_token)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--upload":
        print("\n📤 Uploading RSI skills to Meta Business Agent...\n")
        results = manager.bulk_create_skills(RSI_SKILLS)
        
        print(f"\n✓ Successfully created: {len(results['created'])} skills")
        for title in results['created']:
            print(f"  - {title}")
        
        if results['failed']:
            print(f"\n✗ Failed to create: {len(results['failed'])} skills")
            for failure in results['failed']:
                print(f"  - {failure['skill']}: {failure['error']}")
        
    elif len(sys.argv) > 1 and sys.argv[1] == "--list":
        print("\n📋 Listing existing skills...\n")
        result = manager.list_skills()
        if result['success']:
            skills = result['data']
            print(f"Found {len(skills)} skills:\n")
            for skill in skills:
                print(f"ID: {skill.get('id')}")
                print(f"Title: {skill.get('title')}")
                print(f"Description: {skill.get('description')}")
                print("-" * 70)
        else:
            print(f"Error: {result['error']}")
    
    else:
        print("\nUsage:")
        print("  python skills_manager.py --upload   # Upload RSI skills")
        print("  python skills_manager.py --list     # List existing skills")
        print("\nPredefined RSI Skills:")
        for skill in RSI_SKILLS:
            print(f"  - {skill.title}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    main()
