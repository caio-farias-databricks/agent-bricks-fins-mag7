#!/usr/bin/env python3
"""
Create Multi-Agent Supervisor with Knowledge Assistant, Genie Space, and UC Function Tools

This script demonstrates how to create a Supervisor Agent using the AgentBricksManager class.
The Supervisor Agent will orchestrate the Knowledge Assistant, Genie space, and UC function
that we created in the previous steps.
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
    """Main function to create Supervisor Agent with all our bricks as tools."""

    print("🚀 Starting Supervisor Agent creation...")

    # Initialize Workspace Client and AgentBricksManager
    w = WorkspaceClient()
    brick_manager = AgentBricksManager(w)

    print(f"Using catalog: {catalog}")
    print(f"Using schema: {schema}")

    # Define the Supervisor Agent configuration
    sa_name = "Financial_Analysis_Supervisor"
    sa_description = "A multi-agent supervisor that coordinates financial analysis using Knowledge Assistant for document analysis, Genie for SQL queries, and Unity Catalog functions for data visualization."

    sa_instructions = """You are a financial analysis supervisor agent that coordinates multiple specialized tools to provide comprehensive financial insights.

Your available tools:
1. Knowledge Assistant: Use for analyzing financial documents, earnings reports, 10-K/10-Q filings, and extracting insights
2. Genie Space: Use for querying ticker data with natural language SQL queries
3. Unity Catalog Function: Use for creating data visualizations in Vega-Lite format

Workflow guidelines:
- For document-based questions, use the Knowledge Assistant
- For data queries about stock prices, volumes, or financial metrics, use the Genie space
- When users request charts or visualizations, use the UC function to generate Vega-Lite specs
- Combine insights from multiple tools when providing comprehensive analysis
- Always cite sources and provide specific data points when available

Be helpful, accurate, and ensure all responses are well-sourced from the appropriate tools."""

    # Define the agents that the Supervisor will coordinate
    # NOTE: We'll try to find the correct Knowledge Assistant endpoint name
    # KA Tile ID from our creation: 235fb299-115b-400e-85ec-15a70714213a

    # Use the provided Knowledge Assistant endpoint ID
    ka_endpoint_name = "ka-f4a4ff5f-endpoint"
    print(f"Using KA endpoint: {ka_endpoint_name}")

    # Try to find the Financial_Data_Explorer Genie space using Databricks SDK
    print("🔍 Looking for Financial_Data_Explorer Genie space...")
    financial_genie_id = None

    try:
        # Try the correct Genie spaces API endpoint
        print("Trying /api/2.0/genie/spaces endpoint...")
        print(f"Using workspace: {w.config.host}")
        response = w.api_client.do('GET', '/api/2.0/genie/spaces')

        if 'spaces' in response:
            print(f"Found {len(response['spaces'])} Genie space(s)")
            for space in response['spaces']:
                space_title = space.get('title', 'Unknown')
                space_id = space.get('space_id', 'Unknown')
                print(f"  - {space_title} (ID: {space_id})")

                # Look for Financial_Data_Explorer by title
                if space_title == 'Financial_Data_Explorer':
                    financial_genie_id = space_id
                    print(f"✅ Found Financial_Data_Explorer with ID: {financial_genie_id}")
                    break
        else:
            print("⚠️ No 'spaces' key in API response")
            print(f"Response: {response}")

        if not financial_genie_id:
            print("\n⚠️ Could not find Financial_Data_Explorer Genie space")
            if 'spaces' in response and len(response['spaces']) > 0:
                print("Available Genie spaces:")
                for space in response['spaces']:
                    print(f"  - {space.get('title', 'Unknown')} (ID: {space.get('space_id', 'Unknown')})")
            else:
                print("No Genie spaces found. Make sure you've run 02_instructor_setup_genie.py first.")

    except Exception as e:
        print(f"⚠️ Error calling Genie spaces API: {e}")
        print("This might be a permissions issue or the Genie space hasn't been created yet.")
        print("Make sure you've run 02_instructor_setup_genie.py to create the Financial_Data_Explorer space.")

    if not financial_genie_id:
        print("\n⚠️ Financial_Data_Explorer Genie space not found.")
        print("This could mean:")
        print("1. The Genie space wasn't created yet - run 02_instructor_setup_genie.py first")
        print("2. Different workspace being used")
        print("3. Permissions issue accessing the Genie API")
        print("\nCreating supervisor with KA and UC Function only...")
        print("The Genie space can be added later by recreating the supervisor.")

    # Create agents list - starting with KA and UC Function
    agents = [
        {
            "name": "Financial_Documents_Assistant",
            "description": "Access to financial documents including 10-K/10-Q reports, earnings releases, and transcripts for comprehensive document analysis",
            "agent_type": "ka",
            "serving_endpoint": {"name": ka_endpoint_name}
        },
        {
            "name": "Chart_Generator",
            "description": "Generate Vega-Lite chart specifications for data visualization",
            "agent_type": "function",
            "unity_catalog_function": {
                "uc_path": {
                    "catalog": catalog,
                    "schema": schema,
                    "name": "generate_vega_lite_spec"
                }
            }
        }
    ]

    # Add Genie space agent if we found the ID
    if financial_genie_id:
        genie_agent = {
            "name": "Ticker_Data_Explorer",
            "description": "Natural language SQL interface for querying financial ticker data including prices, volumes, and market metrics",
            "agent_type": "genie",
            "genie_space": {"id": financial_genie_id}
        }
        agents.append(genie_agent)
        print(f"✅ Added Genie space agent with ID: {financial_genie_id}")
    else:
        print("⚠️ Genie space not found - creating MAS with KA and UC Function only")

    print(f"\n🤖 Creating Supervisor Agent...")
    print(f"  Name: {sa_name}")
    print(f"  Description: {sa_description}")
    print(f"\n🔧 Configured Agents ({len(agents)}):")
    for i, agent in enumerate(agents):
        print(f"  {i+1}. {agent['name']} ({agent['agent_type']})")
        if 'serving_endpoint' in agent:
            print(f"      Endpoint: {agent['serving_endpoint']['name']}")
        elif 'genie_space' in agent:
            print(f"      Genie ID: {agent['genie_space']['id']}")
        elif 'unity_catalog_function' in agent:
            uc_path = agent['unity_catalog_function']['uc_path']
            print(f"      Function: {uc_path['catalog']}.{uc_path['schema']}.{uc_path['name']}")

    # Create the Multi-Agent Supervisor
    try:
        result = brick_manager.mas_create(
            name=sa_name,
            agents=agents,
            description=sa_description,
            instructions=sa_instructions
        )

        print("\n✅ Supervisor Agent created successfully!")

        # Extract key information from the result
        mas_info = result.get('multi_agent_supervisor', {})
        tile_info = mas_info.get('tile', {})
        sa_id = tile_info.get('tile_id')
        sa_name_created = tile_info.get('name', sa_name)

        print(f"  Multi-Agent Supervisor ID: {sa_id}")
        print(f"  Name: {sa_name_created}")
        print(f"  Description: {mas_info.get('description', 'No description')}")

        # Display configured agents
        configured_agents = mas_info.get('agents', [])
        print(f"\n🔧 Configured Agents ({len(configured_agents)}):")
        for i, agent in enumerate(configured_agents):
            agent_name = agent.get('name', 'Unknown')
            agent_type = agent.get('agent_type', 'Unknown')
            print(f"  {i+1}. {agent_name} ({agent_type})")

    except Exception as e:
        print(f"❌ Error creating Multi-Agent Supervisor: {e}")
        return

    # Check the status of the Multi-Agent Supervisor
    print(f"\n🔍 Checking Multi-Agent Supervisor status...")
    try:
        status = brick_manager.mas_get_endpoint_status(sa_id)
        print(f"Status: {status}")

        if status in ['PROVISIONING', 'NOT_READY']:
            print("Multi-Agent Supervisor is still provisioning. You can check its status in the Databricks workspace.")
        elif status == 'ONLINE':
            print("✅ Multi-Agent Supervisor is ready to use!")
        else:
            print(f"Multi-Agent Supervisor status: {status}")

    except Exception as e:
        print(f"⚠️ Warning: Could not check status: {e}")

    # Add sample conversation starters
    sample_conversations = [
        {
            "query": "What were Apple's key revenue highlights in their latest quarterly report?",
            "expected_flow": "Knowledge Assistant → Document analysis"
        },
        {
            "query": "Show me a chart of Tesla's stock price trends over the last week",
            "expected_flow": "Genie → Data query → UC Function → Visualization"
        },
        {
            "query": "Compare NVIDIA's recent earnings performance with their guidance and create a visualization",
            "expected_flow": "Knowledge Assistant → Genie → UC Function → Comprehensive analysis"
        },
        {
            "query": "What are the main risk factors mentioned in Meta's 10-K filing?",
            "expected_flow": "Knowledge Assistant → Document analysis"
        },
        {
            "query": "Create a bar chart showing the average trading volume for each company in our dataset",
            "expected_flow": "Genie → Data query → UC Function → Visualization"
        }
    ]

    print(f"\n📚 Sample Conversation Starters ({len(sample_conversations)}):")
    for i, example in enumerate(sample_conversations):
        print(f"  {i+1}. \"{example['query']}\"")
        print(f"      Expected flow: {example['expected_flow']}")

    # Summary
    print("\n🎉 Multi-Agent Supervisor Setup Complete!")
    print("\n📋 Summary:")
    print(f"  • Name: {sa_name}")
    print(f"  • Multi-Agent Supervisor ID: {sa_id}")
    print(f"  • Agents Configured: {len(agents)}")
    print(f"    - Knowledge Assistant (Financial Documents)")
    print(f"    - Genie Space (Ticker Data)")
    print(f"    - Unity Catalog Function (Visualization)")

    print("\n🚀 Next Steps:")
    print("1. Wait for the Multi-Agent Supervisor to be ONLINE if it's still provisioning")
    print("2. Test the supervisor in the Databricks workspace (Machine Learning > Agents)")
    print("3. Try the sample conversation starters to test multi-agent coordination")
    print("4. Experiment with complex queries that require multiple agents")

    print(f"\n🔗 Access your Multi-Agent Supervisor:")
    print(f"   Navigate to Machine Learning > Agents in your Databricks workspace")
    print(f"   Look for: {sa_name}")

    print(f"\n💡 Example multi-tool queries to try:")
    for example in sample_conversations[:3]:
        print(f"   • \"{example['query']}\"")

    print(f"\n🏗️ Architecture Overview:")
    print(f"   📄 Knowledge Assistant ← Financial documents (10-K, 10-Q, earnings)")
    print(f"   📊 Genie Space ← Ticker data ({catalog}.{schema}.ticker_data)")
    print(f"   📈 UC Function ← Chart generation ({catalog}.{schema}.generate_vega_lite_spec)")
    print(f"   🤖 Multi-Agent Supervisor ← Coordinates all agents for comprehensive analysis")

if __name__ == "__main__":
    main()