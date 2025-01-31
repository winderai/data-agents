import duckdb
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker for generating realistic data
fake = Faker()

# Connect to DuckDB (creates a new database if it doesn't exist)
conn = duckdb.connect('lead_agent/leads.db')

# Create sequence for auto-incrementing ID
conn.execute("""
    CREATE SEQUENCE IF NOT EXISTS sales_leads_id_seq;
""")

# Create the sales_leads table
conn.execute("""
    CREATE TABLE IF NOT EXISTS sales_leads (
        id INTEGER PRIMARY KEY DEFAULT(nextval('sales_leads_id_seq')),
        customer_name VARCHAR,
        company VARCHAR,
        needs VARCHAR,
        budget DECIMAL,
        timeline_start DATE,
        timeline_end DATE,
        created_at TIMESTAMP
    )
""")

# Common business needs
business_needs = [
    "Website redesign",
    "Mobile app development",
    "Cloud migration",
    "Digital marketing campaign",
    "E-commerce platform",
    "CRM implementation",
    "Data analytics solution",
    "Security assessment",
    "IT infrastructure upgrade",
    "AI/ML integration"
]

# Generate 50 dummy leads
leads = []
for _ in range(50):
    # Generate random dates within a reasonable range
    created_at = fake.date_time_between(start_date='-3M', end_date='now')
    timeline_start = fake.date_time_between(start_date='now', end_date='+6y')
    timeline_end = timeline_start + timedelta(days=random.randint(30, 365))
    
    # Generate random budget between 10k and 500k
    budget = round(random.uniform(10000, 500000), 2)
    
    lead = (
        fake.name(),
        fake.company(),
        random.choice(business_needs),
        budget,
        timeline_start,
        timeline_end,
        created_at
    )
    leads.append(lead)

# Insert the dummy data into the table
conn.executemany("""
    INSERT INTO sales_leads (
        customer_name, company, needs, budget, 
        timeline_start, timeline_end, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""", leads)

# Verify the data
result = conn.execute("SELECT COUNT(*) FROM sales_leads").fetchone()
print(f"Successfully inserted {result[0]} leads into the database.")

# Close the connection
conn.close()
