from typing import Dict, Any
from langgraph.graph import Graph
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

class SalesEngineerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
    def analyze_requirements(self, query: str) -> str:
        """Break down the requirements and create a detailed project plan"""
        prompt = f"""You are an expert software engineer helping the sales team with project estimation.
        Given the following client requirements, create a detailed project plan.
        Break it down into phases and specific tasks.
        
        Requirements: {query}
        
        Format your response as:
        1. Project Overview
        2. Technical Requirements
        3. Project Phases (with subtasks)
        4. Technical Considerations
        """
        
        messages = [HumanMessage(content=prompt)]
        return self.llm.invoke(messages).content

    def estimate_effort(self, project_plan: str) -> str:
        """Estimate the effort in man-days based on the project plan"""
        prompt = f"""Based on the following project plan, estimate:
        1. Number of engineers needed
        2. Time required for each phase
        3. Total effort in man-days
        4. Any risk factors that could affect the timeline
        
        Project Plan:
        {project_plan}
        
        Provide a detailed breakdown of your estimation, explaining your reasoning.
        """
        
        messages = [HumanMessage(content=prompt)]
        return self.llm.invoke(messages).content

    def run(self, query: str) -> str:
        """Process a project requirements query and provide estimation"""
        project_plan = self.analyze_requirements(query)
        estimation = self.estimate_effort(project_plan)
        
        # Combine the plan and estimation into a complete response
        response = f"""# Project Analysis and Estimation

## Project Plan
{project_plan}

## Effort Estimation
{estimation}
"""
        return response

def create_graph() -> Graph:
    """Create the langgraph workflow"""
    sales_engineer = SalesEngineerAgent()
    
    def process_message(state: Dict[str, Any]):
        query = state["messages"][-1].content
        response = sales_engineer.run(query)
        state["messages"].append(AIMessage(content=response))
        return state
    
    workflow = Graph()
    workflow.add_node("process_message", process_message)
    workflow.set_entry_point("process_message")
    workflow.set_finish_point("process_message")
    
    return workflow.compile() 