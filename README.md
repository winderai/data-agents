# Demo AI Agents for State of Open Con

The goal is to quickly demonstrate using AI agents as IO interfaces for a business. Agents are split by business domain.

There are three agents. Two "base" agents exposing data from parts of the organization. The first is a lead agent that exposes data from the lead database. The second is a sales engineer agent that exposes knowledge from sales engineering.

The third agent is a functional agent that uses the other two agents to generate proposals for leads.

## Setup

1. Install `uv`
2. Run `uv sync` to install dependencies
3. Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=xxxx
OPENAI_BASE_URL=https://app.tryhelix.ai/v1/
OPENAI_MODEL=llama3.1:8b-instruct-q8_0
```

## Usage

1. `uv run lead_agent/cli.py interactive`
2. `uv run sales_engineer_agent/cli.py interactive`
3. `uv run sales_agent/cli.py interactive`
