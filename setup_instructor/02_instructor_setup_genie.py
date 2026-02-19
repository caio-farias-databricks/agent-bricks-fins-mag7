#!/usr/bin/env python3
"""
Create Genie Space for Financial Analysis

This script demonstrates how to create a Genie space using the AgentBricksManager class.
The Genie space will use the ticker data table for SQL-based financial data analysis.
"""

# Import configuration and helper functions
import sys
import os
sys.path.append('..')

# Import configuration
exec(open('../config.py').read())

import logging
from databricks.sdk import WorkspaceClient
from resources.brick_setup_functions import AgentBricksManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main function to create Genie space for financial data analysis."""

    print("🚀 Starting Genie space creation...")

    # Initialize Workspace Client and AgentBricksManager
    w = WorkspaceClient()
    brick_manager = AgentBricksManager(w)

    print(f"Using catalog: {catalog}")
    print(f"Using schema: {schema}")
    print(f"Ticker data table: {catalog}.{schema}.ticker_data")

    # Get available warehouses
    print("\n🔍 Getting available SQL warehouses...")
    try:
        warehouses = list(w.warehouses.list())

        if not warehouses:
            print("❌ No warehouses found. Genie spaces require a SQL warehouse.")
            print("Please create a SQL warehouse in your Databricks workspace first.")
            return

        # Find a running warehouse or use the first available one
        running_warehouses = [wh for wh in warehouses if wh.state.value == 'RUNNING']
        if running_warehouses:
            warehouse = running_warehouses[0]
            print(f"✅ Found running warehouse: {warehouse.name} (ID: {warehouse.id})")
        else:
            warehouse = warehouses[0]
            print(f"⚠️  Using first available warehouse: {warehouse.name} (ID: {warehouse.id}) - State: {warehouse.state}")

        warehouse_id = warehouse.id

    except Exception as e:
        print(f"❌ Error accessing warehouses: {e}")
        return

    # Define the Genie space configuration
    genie_name = "Financial_Data_Explorer"
    genie_description = "A Genie space for exploring and analyzing financial ticker data through natural language queries."

    # Define table identifiers for the Genie space
    table_identifiers = [f"{catalog}.{schema}.ticker_data"]

    print(f"\n📊 Creating Genie space...")
    print(f"  Name: {genie_name}")
    print(f"  Description: {genie_description}")
    print(f"  Warehouse ID: {warehouse_id}")
    print(f"  Table: {table_identifiers[0]}")

    # Create the Genie space
    try:
        result = brick_manager.genie_create(
            display_name=genie_name,
            warehouse_id=warehouse_id,
            table_identifiers=table_identifiers,
            description=genie_description
        )

        print("\n✅ Genie space created successfully!")

        # Extract key information from the result
        genie_id = result.get('id')

        print(f"  Genie ID: {genie_id}")
        print(f"  Name: {result.get('display_name', genie_name)}")
        print(f"  Description: {result.get('description', 'No description')}")

        # Display table identifiers
        tables = result.get('table_identifiers', [])
        print(f"\n📋 Table Sources ({len(tables)}):")
        for i, table in enumerate(tables):
            print(f"  {i+1}. {table}")

    except Exception as e:
        print(f"❌ Error creating Genie space: {e}")
        return

    # Add sample questions
    sample_questions = [
        "What are the latest stock prices for all companies?",
        "Show me the daily trading volume for Apple over the last week",
        "Compare the closing prices of NVIDIA and Meta",
        "Which company had the highest trading volume yesterday?",
        "Show me the price trends for Tesla over time",
        "What is the average closing price for each company?",
        "Which stocks have increased in price over the last 5 days?"
    ]

    print(f"\n📚 Adding {len(sample_questions)} sample questions...")

    try:
        # Add sample questions in batch for efficiency
        created_questions = brick_manager.genie_add_sample_questions_batch(genie_id, sample_questions)
        print(f"✅ Successfully added {len(created_questions)} sample questions")

        for i, question in enumerate(sample_questions):
            print(f"  {i+1}. {question}")

    except Exception as e:
        print(f"⚠️ Warning: Could not add sample questions: {e}")
        print("The Genie space was created successfully, but sample questions failed to add.")

    # Add text instructions
    text_instructions = [
        "The ticker_data table contains financial market data for major technology companies including Apple (AAPL), Microsoft (MSFT), Google (GOOGL), Amazon (AMZN), Meta (META), NVIDIA (NVDA), and Tesla (TSLA).",
        "Available columns: date, symbol, company_name, price_open, price_close, volume, pe_trailing, pe_forward, peg, ev_ebitda, market_cap, beta",
        "Use 'symbol' to filter by specific companies (e.g., 'AAPL' for Apple, 'MSFT' for Microsoft)",
        "Price data includes daily open and close prices. Volume represents the number of shares traded.",
        "Financial metrics like PE ratios, market cap, and beta are available for fundamental analysis."
    ]

    print(f"\n📝 Adding {len(text_instructions)} instructional notes...")

    try:
        for instruction in text_instructions:
            brick_manager.genie_add_text_instruction(genie_id, instruction)

        print(f"✅ Successfully added instructional notes")

        for i, instruction in enumerate(text_instructions):
            print(f"  {i+1}. {instruction[:80]}{'...' if len(instruction) > 80 else ''}")

    except Exception as e:
        print(f"⚠️ Warning: Could not add text instructions: {e}")

    # Add SQL examples
    sql_examples = [
        {
            "description": "Get latest stock prices for all companies",
            "sql": f"SELECT symbol, company_name, date, price_close FROM {catalog}.{schema}.ticker_data WHERE date = (SELECT MAX(date) FROM {catalog}.{schema}.ticker_data) ORDER BY symbol"
        },
        {
            "description": "Calculate average trading volume by company",
            "sql": f"SELECT symbol, company_name, AVG(volume) as avg_volume FROM {catalog}.{schema}.ticker_data GROUP BY symbol, company_name ORDER BY avg_volume DESC"
        },
        {
            "description": "Show price performance over time for Apple",
            "sql": f"SELECT date, price_open, price_close, volume FROM {catalog}.{schema}.ticker_data WHERE symbol = 'AAPL' ORDER BY date DESC LIMIT 10"
        },
        {
            "description": "Compare market cap across companies",
            "sql": f"SELECT symbol, company_name, market_cap FROM {catalog}.{schema}.ticker_data WHERE market_cap IS NOT NULL GROUP BY symbol, company_name, market_cap ORDER BY market_cap DESC"
        }
    ]

    print(f"\n🔍 Adding {len(sql_examples)} SQL example queries...")

    try:
        # Add SQL examples in batch for efficiency
        created_examples = brick_manager.genie_add_sql_instructions_batch(genie_id, sql_examples)
        print(f"✅ Successfully added {len(created_examples)} SQL examples")

        for i, example in enumerate(sql_examples):
            print(f"  {i+1}. {example['description']}")

    except Exception as e:
        print(f"⚠️ Warning: Could not add SQL examples: {e}")

    # Summary
    print("\n🎉 Genie Space Setup Complete!")
    print("\n📋 Summary:")
    print(f"  • Name: {genie_name}")
    print(f"  • Genie ID: {genie_id}")
    print(f"  • Data Source: {catalog}.{schema}.ticker_data")
    print(f"  • Sample Questions: {len(sample_questions)} added")
    print(f"  • Instructions: {len(text_instructions)} notes added")
    print(f"  • SQL Examples: {len(sql_examples)} queries added")

    print("\n🚀 Next Steps:")
    print("1. Access the Genie space in the Databricks workspace")
    print("2. Try asking natural language questions about the financial data")
    print("3. Use the sample questions as starting points for analysis")
    print("4. Explore SQL patterns with the provided examples")

    print(f"\n🔗 Access your Genie Space:")
    print(f"   Navigate to Data Intelligence > Genie in your Databricks workspace")
    print(f"   Look for: {genie_name}")
    print(f"\n💡 Example queries to try:")
    for question in sample_questions[:3]:
        print(f"   • {question}")

if __name__ == "__main__":
    main()