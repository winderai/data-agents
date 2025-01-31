from typing import Dict, Any
from langgraph.graph import Graph
import duckdb
import pandas as pd
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

class LeadAgent:
    def __init__(self, db_path: str = "lead_agent/leads.db"):
        self.conn = duckdb.connect(db_path)
        # Verify database connection and table existence
        tables = self.conn.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'sales_leads'").fetchall()
        if not tables:
            raise ValueError(f"Table 'sales_leads' not found in database '{db_path}'. Available tables: " + 
                            str(self.conn.execute("SELECT table_name FROM information_schema.tables").fetchall()))
        
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
    def query_leads(self, query: str) -> pd.DataFrame:
        """Execute a SQL query against the leads database"""
        # Clean and validate the SQL query
        query = query.strip()
        if query.endswith(';'):
            query = query[:-1]  # Remove trailing semicolon
        return self.conn.execute(query).df()

    def process_query(self, query: str) -> str:
        """Convert natural language query to SQL"""
        prompt = f"""You are a SQL expert. Convert the following natural language query into SQL.
        The sales_leads table has columns: 
        - id INTEGER
        - customer_name VARCHAR
        - company VARCHAR
        - needs VARCHAR
        - budget DECIMAL
        - timeline_start DATE
        - timeline_end DATE
        - created_at TIMESTAMP
        
        Query: {query}
        
        For listing or searching leads, always include id, customer_name, company, and needs in the output.
        Sort results by id for consistency.
        If searching, use ILIKE for case-insensitive matching.
        
        Important: Return only a valid SQL query. Do not include backticks, markdown formatting, or any explanation.
        The query should be a simple SELECT statement that can be executed directly against the sales_leads table."""
        
        messages = [HumanMessage(content=prompt)]
        sql = self.llm.invoke(messages).content.strip()
        
        # Remove any markdown code block indicators if present
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        return sql

    def format_response(self, df: pd.DataFrame, query: str) -> str:
        """Format the query results into a natural response"""
        if "id" in df.columns:  # If this is a listing or search query
            prompt = f"""Format this lead data into a clear list with IDs.
            Original query: {query}
            Data:
            {df.to_string()}
            
            Format each lead as:
            #ID: [company name] - [needs]
            
            Make sure the ID is clearly visible at the start of each line.
            If this is a search result, mention the total count at the top."""
        else:
            prompt = f"""Given this data about leads and the original query, provide a natural language summary.
            Original query: {query}
            Data:
            {df.to_string()}
            
            Format the response in a clear, business-friendly way."""
        
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages).content
        
        return response

    def run(self, query: str) -> str:
        """Process a natural language query about leads"""
        sql = self.process_query(query)
        results = self.query_leads(sql)
        response = self.format_response(results, query)
        return response

def create_graph() -> Graph:
    """Create the langgraph workflow"""
    lead_agent = LeadAgent()
    
    def process_message(state: Dict[str, Any]):
        query = state["messages"][-1].content
        response = lead_agent.run(query)
        state["messages"].append(AIMessage(content=response))
        return state
    
    workflow = Graph()
    workflow.add_node("process_message", process_message)
    workflow.set_entry_point("process_message")
    workflow.set_finish_point("process_message")

    return workflow.compile() 