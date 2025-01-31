import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.theme import Theme
from rich.table import Table
from sales_agent import create_graph, SalesAgent
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

app = typer.Typer(help="Proposal Agent - Generate professional sales proposals")

def display_welcome():
    welcome_md = """
    # 📄 Proposal Agent
    
    Generate professional proposals by combining lead information and technical specifications.
    
    Commands:
    - list    : Show all available leads
    - search  : Search for specific leads
    - gen     : Generate a proposal for a lead ID
    - quit    : Exit the application
    """
    console.print(Panel(Markdown(welcome_md), title="Welcome", border_style="blue"))

def handle_list_leads():
    """Display all available leads"""
    agent = SalesAgent()
    with console.status("[bold blue]Fetching leads...[/bold blue]"):
        leads = agent.list_leads()
    console.print(Panel(Markdown(leads), title="Available Leads", border_style="cyan"))

def handle_search_leads(search_term: str):
    """Search for leads matching the search term"""
    agent = SalesAgent()
    with console.status(f"[bold blue]Searching leads for '{search_term}'...[/bold blue]"):
        results = agent.search_leads(search_term)
    console.print(Panel(Markdown(results), title="Search Results", border_style="cyan"))

@app.command()
def interactive():
    """Start an interactive session with the Proposal Agent"""
    display_welcome()
    workflow = create_graph()
    
    while True:
        try:
            command = Prompt.ask("\n[blue]Command[/blue]", 
                               choices=["list", "search", "gen", "quit"],
                               show_choices=True)
            
            if command == "quit":
                console.print("\n[info]Goodbye! 👋[/info]")
                break
            
            elif command == "list":
                handle_list_leads()
                
            elif command == "search":
                search_term = Prompt.ask("[blue]Enter search term[/blue]")
                handle_search_leads(search_term)
                
            elif command == "gen":
                lead_id = Prompt.ask("[blue]Enter lead ID[/blue]")
                with console.status("[bold blue]Generating proposal...[/bold blue]"):
                    state = {"messages": [HumanMessage(content=f"Generate a proposal for lead {lead_id}")]}
                    final_state = workflow.invoke(state)
                    response = final_state["messages"][-1].content
                console.print(Panel(Markdown(response), title="Generated Proposal", border_style="green"))
            
        except Exception as e:
            console.print(f"[error]Error: {str(e)}[/error]")
            console.print("[warning]Please try again.[/warning]")

@app.command()
def list_leads():
    """Display all available leads"""
    handle_list_leads()

@app.command()
def search(term: str):
    """Search for leads by company name or needs"""
    handle_search_leads(term)

@app.command()
def generate(lead_id: str):
    """Generate a proposal for a specific lead"""
    workflow = create_graph()
    
    try:
        with console.status("[bold blue]Generating proposal...[/bold blue]"):
            query = f"Generate a proposal for lead {lead_id}"
            state = {"messages": [HumanMessage(content=query)]}
            final_state = workflow.invoke(state)
            response = final_state["messages"][-1].content
        
        console.print(Panel(Markdown(response), title="Generated Proposal", border_style="green"))
        
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/error]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app() 