import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.theme import Theme
from sales_engineer_agent import create_graph
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Rich console with custom theme
console = Console(theme=Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green",
}))

app = typer.Typer(help="Sales Engineer Agent - Project estimation assistant")

def display_welcome():
    welcome_md = """
    # 🛠️ Sales Engineer Agent
    
    Get detailed project plans and estimates for potential projects.
    
    Example queries:
    - I need a new e-commerce website with product catalog and payment integration
    - Client needs a mobile app for their restaurant delivery service
    - We need to migrate our on-premise CRM to the cloud
    - Build an AI-powered chatbot for customer service
    """
    console.print(Panel(Markdown(welcome_md), title="Welcome", border_style="blue"))

@app.command()
def interactive():
    """Start an interactive session with the Sales Engineer Agent"""
    display_welcome()
    workflow = create_graph()
    
    while True:
        try:
            query = Prompt.ask("\n[blue]Project Requirements[/blue]")
            
            if query.lower() in ('exit', 'quit'):
                console.print("\n[info]Goodbye! 👋[/info]")
                break
                
            with console.status("[bold blue]Analyzing requirements...[/bold blue]"):
                state = {"messages": [HumanMessage(content=query)]}
                final_state = workflow.invoke(state)
                response = final_state["messages"][-1].content
            
            console.print(Panel(Markdown(response), title="Analysis & Estimation", border_style="green"))
            
        except Exception as e:
            console.print(f"[error]Error: {str(e)}[/error]")
            console.print("[warning]Please try again with different requirements.[/warning]")

@app.command()
def analyze(requirements: str):
    """Analyze a single project and exit"""
    workflow = create_graph()
    
    try:
        with console.status("[bold blue]Analyzing requirements...[/bold blue]"):
            state = {"messages": [HumanMessage(content=requirements)]}
            final_state = workflow.invoke(state)
            response = final_state["messages"][-1].content
        
        console.print(Panel(Markdown(response), title="Analysis & Estimation", border_style="green"))
        
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/error]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app() 