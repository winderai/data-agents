from typing import Dict, Any, Optional
from langgraph.graph import Graph
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from lead_agent.lead_agent import LeadAgent
from sales_engineer_agent.sales_engineer_agent import SalesEngineerAgent

class SalesAgent:
    # Pay scale for different roles (daily rates)
    PAY_SCALE = {
        "Junior Engineer": 400,
        "Senior Engineer": 800,
        "Tech Lead": 1200,
        "Project Manager": 1000,
        "DevOps Engineer": 900,
        "QA Engineer": 600
    }
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.lead_agent = LeadAgent()
        self.sales_engineer = SalesEngineerAgent()
        
    def get_lead_details(self, lead_id: str) -> str:
        """Fetch lead details from the lead agent"""
        query = f"Give me all details for lead with id {lead_id}"
        return self.lead_agent.run(query)
        
    def generate_technical_specs(self, requirements: str) -> str:
        """Get technical specifications and estimates from sales engineer"""
        return self.sales_engineer.run(requirements)
        
    def calculate_costs(self, technical_specs: str) -> str:
        """Calculate costs based on technical specifications and pay scale"""
        prompt = f"""Based on these technical specifications, determine the team composition needed
        and calculate the total cost. Use these daily rates:
        
        - Junior Engineer: $400/day
        - Senior Engineer: $800/day
        - Tech Lead: $1200/day
        - Project Manager: $1000/day
        - DevOps Engineer: $900/day
        - QA Engineer: $600/day
        
        Technical Specifications:
        {technical_specs}
        
        Provide a detailed cost breakdown including:
        1. Required team members and duration
        2. Cost calculation for each role
        3. Total project cost
        
        Format as a clear, itemized breakdown."""
        
        messages = [HumanMessage(content=prompt)]
        return self.llm.invoke(messages).content
        
    def generate_proposal(self, technical_specs: str, lead_details: str, costs: str) -> str:
        """Generate the final proposal document"""
        prompt = f"""Create a professional proposal document with the following information:
        
        Lead Details:
        {lead_details}
        
        Technical Specifications:
        {technical_specs}
        
        Cost Breakdown:
        {costs}
        
        Format the proposal with these sections:
        1. Executive Summary
        2. Project Understanding
        3. Proposed Solution
        4. Implementation Approach
        5. Timeline
        6. Team Composition
        7. Investment
        8. Terms and Conditions
        
        Make it professional and persuasive. Use markdown formatting."""
        
        messages = [HumanMessage(content=prompt)]
        return self.llm.invoke(messages).content
        
    def run(self, query: str) -> str:
        """Process a proposal request"""
        # Extract lead ID from query
        prompt = f"Extract the lead ID from this query: {query}"
        messages = [HumanMessage(content=prompt)]
        lead_id = self.llm.invoke(messages).content.strip()
        
        # Get lead details
        lead_details = self.get_lead_details(lead_id)
        
        # Generate technical specifications
        technical_specs = self.generate_technical_specs(lead_details)
        
        # Calculate costs
        costs = self.calculate_costs(technical_specs)
        
        # Generate final proposal
        proposal = self.generate_proposal(technical_specs, lead_details, costs)
        
        return proposal

    def list_leads(self) -> str:
        """Get a formatted list of all leads"""
        query = """List all leads showing their IDs, company names, and needs.
        Format each lead on a new line starting with the ID."""
        result = self.lead_agent.run(query)
        return result
    
    def search_leads(self, search_term: str) -> str:
        """Search leads by company name or needs"""
        query = f"""Find leads where company name or needs contain '{search_term}'.
        Show the ID, company name, and needs for each match.
        Format each lead on a new line starting with the ID."""
        result = self.lead_agent.run(query)
        return result

def create_graph() -> Graph:
    """Create the langgraph workflow"""
    sales_agent = SalesAgent()
    
    def process_message(state: Dict[str, Any]):
        query = state["messages"][-1].content
        response = sales_agent.run(query)
        state["messages"].append(AIMessage(content=response))
        return state
    
    workflow = Graph()
    workflow.add_node("process_message", process_message)
    workflow.set_entry_point("process_message")
    workflow.set_finish_point("process_message")
    
    return workflow.compile() 