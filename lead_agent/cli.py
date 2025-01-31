import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.theme import Theme
from lead_agent import create_graph
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

app = typer.Typer(help="Lead Agent CLI - Query your sales leads database")

def display_welcome():
    welcome_md = """
    # 🎯 Lead Agent CLI
    
    Query your sales leads using natural language. Some example queries:
    
    - Show me all leads from last month
    - How many leads did we get this month?
    - What are our most valuable opportunities?
    """
    console.print(Panel(Markdown(welcome_md), title="Welcome", border_style="blue"))

@app.command()
def interactive():
    """Start an interactive session with the Lead Agent"""
    display_welcome()
    workflow = create_graph()
    
    while True:
        try:
            query = Prompt.ask("\n[blue]Query[/blue]")
            
            if query.lower() in ('exit', 'quit'):
                console.print("\n[info]Goodbye! 👋[/info]")
                break
                
            with console.status("[bold blue]Processing query...[/bold blue]"):
                state = {"messages": [HumanMessage(content=query)]}
                final_state = workflow.invoke(state)
                response = final_state["messages"][-1].content
            
            console.print(Panel(response, title="Response", border_style="green"))
            
        except Exception as e:
            console.print(f"[error]Error: {str(e)}[/error]")
            console.print("[warning]Please try again with a different query.[/warning]")

@app.command()
def query(question: str):
    """Run a single query and exit"""
    workflow = create_graph()
    
    try:
        with console.status("[bold blue]Processing query...[/bold blue]"):
            state = {"messages": [HumanMessage(content=question)]}
            final_state = workflow.invoke(state)
            response = final_state["messages"][-1].content
        
        console.print(Panel(response, title="Response", border_style="green"))
        
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/error]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app() 