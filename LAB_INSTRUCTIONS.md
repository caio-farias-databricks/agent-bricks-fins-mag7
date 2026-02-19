# Agent Bricks Workshop - Lab Instructions

## Overview

This lab will guide you through creating a comprehensive multi-agent system in Databricks using Agent Bricks. You'll build a financial analysis system that can answer complex questions by combining document knowledge with structured data analysis.

## What You'll Build

By the end of this lab, you'll have created:

1. **Knowledge Assistant**: Analyzes financial documents (10-Ks, 10-Qs, annual reports, earnings materials)
2. **Genie Space**: Natural language to SQL agent for ticker/financial data queries
3. **Unity Catalog Function**: Generates Vega-Lite chart specifications for data visualization
4. **Multi-Agent Supervisor**: Orchestrates all agents to answer complex financial questions

## Architecture

```
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│   Knowledge Assistant   │    │      Genie Space        │    │  Unity Catalog Function │
│                        │    │   (NL to SQL Agent)     │    │  (Vega-Lite Charts)     │
│ - 10-K documents       │    │                        │    │                        │
│ - 10-Q filings         │    │ - Ticker data          │    │ - Chart generation     │
│ - Annual reports       │    │ - Financial tables     │    │ - Data visualization    │
│ - Earnings materials   │    │ - Market data          │    │ - Interactive graphs   │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘
             │                             │                             │
             └─────────────┐               │               ┌─────────────┘
                           │               │               │
                           ▼               ▼               ▼
                    ┌─────────────────────────────────────────────┐
                    │         Multi-Agent Supervisor              │
                    │                                           │
                    │  Orchestrates all agents to answer        │
                    │  complex financial analysis questions     │
                    └─────────────────────────────────────────────┘
```

## Prerequisites

- Access to a Databricks workspace with Unity Catalog enabled
- Permissions to create catalogs, schemas, volumes, and Agent Bricks
- Python environment with Databricks Connect (optional, for running setup scripts locally)
- Access to the Databricks UI for monitoring and testing Agent Bricks

## Setup Scripts Overview

This workshop includes automated setup scripts in the `setup_instructor/` folder:

- **`01_instructor_setup_ka.ipynb`**: Creates Knowledge Assistant with 5 knowledge sources
- **`02_instructor_setup_genie.py`**: Creates Genie space for ticker data analysis
- **`03_create_vegalite_uc_function_simple.ipynb`**: Creates Unity Catalog visualization function
- **`04_instructor_setup_sa.py`**: Creates Multi-Agent Supervisor coordinating all agents

These scripts handle the complex configuration automatically, allowing you to focus on testing and understanding the multi-agent workflows.

## Lab Structure

### Phase 1: Data Setup and Infrastructure
1. Set up Unity Catalog infrastructure (catalog, schema, volumes)
2. Upload financial documents to Unity Catalog volumes
3. Download and upload ticker data

### Phase 2: Knowledge Assistant Creation
4. Create Knowledge Assistant using setup script
5. Configure multiple document knowledge sources
6. Test document-based question answering

### Phase 3: Genie Space Setup
7. Create Genie Space for ticker data analysis
8. Configure natural language to SQL capabilities
9. Add sample questions and instructions

### Phase 4: Unity Catalog Function Creation
10. Create Vega-Lite chart generation function
11. Test visualization capabilities
12. Register function for agent use

### Phase 5: Multi-Agent Supervisor Integration
13. Create Multi-Agent Supervisor
14. Configure agent orchestration with all tools
15. Test complex multi-agent workflows

---

## Phase 1: Data Setup and Infrastructure

### Step 1.1: Review Available Data

Your repository contains the following financial document categories:

```
data/
├── 10k/                    # Annual filings (10-K forms)
├── 10Q/                    # Quarterly filings (10-Q forms)
├── annual_reports/         # Annual shareholder reports
├── earning_releases/       # Earnings press releases
└── earning_transcripts/    # Earnings call transcripts
```

### Step 1.2: Configure Your Environment

1. **Review configuration** in `config.py`:
   ```python
   catalog = "main"                             # Your catalog name
   schema = "brandon_cowen"                     # Schema for this lab (update with your name)
   table = "parsed_data"                        # Table for document metadata
   volume_name = "raw_documents"                # Volume for raw files
   ```

2. **Update the config** with your details:
   - Change the `schema` value to use your username or preferred schema name
   - Ensure you have permissions to the specified catalog

### Step 1.3: Set Up Infrastructure Using Scripts

This workshop includes automated setup scripts in the `setup_instructor/` folder:

1. **Upload documents to Unity Catalog**:
   ```bash
   # Run the data setup script
   python resources/data_setup_functions.py
   ```
   This script will:
   - Create the catalog and schema if needed
   - Create a Unity Catalog volume for documents
   - Upload all 153 financial documents to the volume
   - Create metadata tables

2. **Download and upload ticker data**:
   ```bash
   # Run the ticker data download script
   python resources/download_ticker_data.py
   ```
   This will:
   - Download ticker data for the "Magnificent 7" companies (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA)
   - Upload the data directly to a Unity Catalog table
   - Include price, volume, and financial metrics

3. **Verify the setup**:
   ```sql
   -- Check that your catalog and schema were created
   SHOW CATALOGS LIKE 'main';
   SHOW SCHEMAS IN main LIKE 'brandon_cowen';

   -- Check the volume and uploaded files
   LIST '/Volumes/main/brandon_cowen/raw_documents/';

   -- Check ticker data table
   SELECT * FROM main.brandon_cowen.ticker_data LIMIT 10;
   ```

---

## Phase 2: Knowledge Assistant Creation

### Step 2.1: Create Knowledge Assistant Using Setup Script

1. **Run the Knowledge Assistant setup notebook**:
   ```bash
   # Upload and run the notebook in Databricks workspace
   # File: setup_instructor/01_instructor_setup_ka.ipynb
   ```

   Or run locally with Databricks Connect:
   ```bash
   cd setup_instructor
   # Upload notebook to Databricks workspace and run there
   ```

2. **What the setup script does**:
   - Creates a Knowledge Assistant named `Financial_Analysis_Assistant`
   - Configures 5 separate knowledge sources for better organization:
     - `quarterly_reports_10q`: 10-Q quarterly financial reports
     - `annual_reports_10k`: 10-K annual financial reports
     - `earnings_releases`: Quarterly earnings releases and announcements
     - `annual_reports`: Annual reports and business reviews
     - `earnings_transcripts`: Earnings call transcripts and Q&A sessions

3. **Knowledge Assistant Configuration**:
   - **Name**: `Financial_Analysis_Assistant`
   - **Description**: `A Knowledge Assistant for analyzing financial documents and providing insights on company performance, earnings, and financial metrics.`
   - **Instructions**: Specialized prompts for financial analysis with proper citation requirements

### Step 2.2: Monitor Setup Progress

1. **Wait for Knowledge Assistant creation** (this may take several minutes):
   - The setup script will create the Knowledge Assistant with all 5 knowledge sources
   - Monitor the output for the Knowledge Assistant tile ID
   - Example output: `Tile ID: 235fb299-115b-400e-85ec-15a70714213a`

2. **Verify in Databricks workspace**:
   - Navigate to Machine Learning > Knowledge Assistants
   - Look for `Financial_Analysis_Assistant`
   - Check that the status shows "ONLINE" (may take time for document indexing)

3. **Test with sample questions**:
   ```
   - "What were the key revenue trends in the most recent quarterly report?"
   - "What are the main risk factors mentioned in the 10-K filing?"
   - "How did earnings per share change compared to the previous quarter?"
   - "What guidance did management provide for the upcoming quarter or year?"
   ```

---

## Phase 3: Genie Space Setup

### Step 3.1: Create Genie Space Using Setup Script

1. **Run the Genie Space setup script**:
   ```bash
   # File: setup_instructor/02_instructor_setup_genie.py
   python setup_instructor/02_instructor_setup_genie.py
   ```

2. **What the setup script does**:
   - Creates a Genie Space named `Financial_Data_Explorer`
   - Automatically detects and uses an available SQL warehouse
   - Configures the Genie space to use the ticker data table
   - Adds comprehensive sample questions for financial analysis
   - Includes instructional notes about the data structure

3. **Genie Space Configuration**:
   - **Name**: `Financial_Data_Explorer`
   - **Description**: `A Genie space for exploring and analyzing financial ticker data through natural language queries`
   - **Data Source**: `main.brandon_cowen.ticker_data`

### Step 3.2: Monitor Genie Space Creation

1. **Wait for creation** (usually quick):
   - Monitor the script output for the Genie Space ID
   - Example output: `Genie ID: 01f1014423d410d88660959285a90eb7`

2. **Verify in Databricks workspace**:
   - Navigate to Data Intelligence > Genie
   - Look for `Financial_Data_Explorer`
   - Check that it shows your ticker data table as a source

3. **Test with sample queries**:
   ```
   - "What are the latest stock prices for all companies?"
   - "Show me the daily trading volume for Apple over the last week"
   - "Compare the closing prices of NVIDIA and Meta"
   - "Which company had the highest trading volume yesterday?"
   - "What is the average closing price for each company?"
   ```

---

## Phase 4: Unity Catalog Function Creation

### Step 4.1: Create Vega-Lite Chart Generation Function

1. **Run the Unity Catalog Function setup notebook**:
   ```bash
   # Upload and run the notebook in Databricks workspace
   # File: setup_instructor/03_create_vegalite_uc_function_simple.ipynb
   ```

2. **What the setup script does**:
   - Creates a Unity Catalog function named `generate_vega_lite_spec`
   - Supports multiple chart types: bar, line, scatter, area, pie
   - Returns valid Vega-Lite v5 specifications as JSON strings
   - Includes robust error handling and data validation
   - Provides tooltip and interactive features

3. **Function Configuration**:
   - **Name**: `main.brandon_cowen.generate_vega_lite_spec`
   - **Parameters**:
     - `chart_description` (string): Natural language description of the chart
     - `data_sample` (string): JSON data for visualization
   - **Returns**: JSON string containing Vega-Lite specification

### Step 4.2: Test the Unity Catalog Function

1. **Monitor function creation**:
   - The notebook will create and test the function automatically
   - Verify the function is registered in your catalog

2. **Test with sample data**:
   ```sql
   -- Test the function directly
   SELECT main.brandon_cowen.generate_vega_lite_spec(
     'bar chart of sales',
     '[{"category": "Jan", "value": 100}, {"category": "Feb", "value": 150}]'
   );
   ```

3. **Example chart types**:
   ```sql
   -- Line chart
   SELECT main.brandon_cowen.generate_vega_lite_spec(
     'line chart showing revenue trend',
     '[{"month": "Jan", "revenue": 10000}, {"month": "Feb", "revenue": 15000}]'
   );

   -- Scatter plot
   SELECT main.brandon_cowen.generate_vega_lite_spec(
     'scatter plot',
     '[{"x": 1, "y": 2}, {"x": 2, "y": 4}, {"x": 3, "y": 6}]'
   );
   ```

---

## Phase 5: Multi-Agent Supervisor Integration

### Step 5.1: Create Multi-Agent Supervisor Using Setup Script

1. **Run the Multi-Agent Supervisor setup script**:
   ```bash
   # File: setup_instructor/04_instructor_setup_sa.py
   python setup_instructor/04_instructor_setup_sa.py
   ```

2. **What the setup script does**:
   - Creates a Multi-Agent Supervisor named `Financial_Analysis_Supervisor`
   - Automatically configures agents for:
     - Knowledge Assistant (financial documents)
     - Unity Catalog Function (chart generation)
     - Placeholder for Genie Space (when ID is provided)
   - Includes comprehensive instructions for multi-agent coordination

3. **Supervisor Configuration**:
   - **Name**: `Financial_Analysis_Supervisor`
   - **Description**: `A multi-agent supervisor that coordinates financial analysis using Knowledge Assistant for document analysis, Genie for SQL queries, and Unity Catalog functions for data visualization`
   - **Instructions**: Specialized coordination prompts for financial workflow orchestration

### Step 5.2: Monitor Supervisor Creation and Update Configuration

1. **Monitor script output**:
   - Look for the Multi-Agent Supervisor ID in the output
   - Example output: `Multi-Agent Supervisor ID: 746700dd-f4b5-4a6b-88da-7c8a5030ea84`
   - Note any endpoint configuration requirements

2. **Update Knowledge Assistant endpoint** (if needed):
   - If the script fails due to incorrect KA endpoint name
   - Navigate to Machine Learning > Knowledge Assistants
   - Find your Financial_Analysis_Assistant and note the endpoint name
   - Update the script with the correct endpoint name

3. **Add Genie Space** (optional):
   - If you have the Genie Space ID from Phase 3, update the script
   - Find the `financial_genie_id` placeholder and replace with your actual ID
   - Re-run the script to create a new supervisor with all three agents

### Step 5.3: Test Multi-Agent Workflows

1. **Wait for supervisor to be ONLINE**:
   - Check the status in Machine Learning > Agents
   - The supervisor status should change from NOT_READY to ONLINE

2. **Test individual agent capabilities**:
   ```
   # Knowledge Assistant tests:
   - "What were Apple's key revenue highlights in their latest quarterly report?"
   - "What are the main risk factors mentioned in Meta's 10-K filing?"

   # Unity Catalog Function tests:
   - "Create a bar chart showing sample sales data"
   - "Generate a line chart visualization"
   ```

3. **Test multi-agent coordination** (when Genie is added):
   ```
   - "What risks did Tesla mention in their latest filing and create a chart showing their stock performance?"
   - "Compare NVIDIA's recent earnings performance with their guidance and create a visualization"
   - "Show me the price trends for Tesla over time and explain what their documents say about growth strategy"
   ```

4. **Example workflows included in the script**:
   - Document analysis + visualization
   - Cross-reference document insights with data analysis
   - Comprehensive analysis combining multiple sources

---

## Testing Your Complete System

### Current Setup Summary

After completing all phases, you should have:

1. **Knowledge Assistant**: `Financial_Analysis_Assistant` with 153 financial documents
2. **Genie Space**: `Financial_Data_Explorer` with ticker data for 7 major companies
3. **Unity Catalog Function**: `generate_vega_lite_spec` for chart generation
4. **Multi-Agent Supervisor**: `Financial_Analysis_Supervisor` coordinating all agents

### Comprehensive Test Questions

Try these end-to-end test questions:

1. **Document Analysis**:
   ```
   - "What were the key revenue trends in Apple's most recent quarterly report?"
   - "What are the main risk factors mentioned in Tesla's 10-K filing?"
   - "Summarize NVIDIA's guidance from their latest earnings call"
   ```

2. **Data Analysis** (via Genie):
   ```
   - "Which company had the highest trading volume yesterday?"
   - "Compare the closing prices of NVIDIA and Meta"
   - "What is the average closing price for each company?"
   ```

3. **Visualization**:
   ```
   - "Create a bar chart showing market cap comparison"
   - "Generate a line chart of revenue trends"
   - "Show me a scatter plot of price vs volume"
   ```

4. **Multi-Agent Coordination**:
   ```
   - "What risks did Tesla mention in their filing and create a chart of their stock performance?"
   - "Analyze Apple's earnings and create a visualization of their key metrics"
   ```

### Success Criteria

Your multi-agent system should be able to:

- ✅ Answer document-based questions using the Knowledge Assistant
- ✅ Perform quantitative analysis using the Genie Space
- ✅ Create interactive Vega-Lite visualizations
- ✅ Coordinate between agents for complex, multi-faceted questions
- ✅ Provide synthesized insights combining documents and data
- ✅ Generate charts alongside textual analysis
- ✅ Cite sources and explain reasoning for all conclusions

---

## Troubleshooting

### Common Issues

1. **Knowledge Assistant not ready**:
   - Wait for document indexing to complete
   - Check that volumes are accessible
   - Verify file formats are supported

2. **Genie Space queries failing**:
   - Ensure tables are properly registered
   - Check data quality and schema consistency
   - Verify warehouse permissions

3. **Multi-Agent coordination issues**:
   - Review agent descriptions and instructions
   - Test individual agents separately first
   - Refine example questions and workflows

4. **Data access errors**:
   - Verify Unity Catalog permissions
   - Check catalog/schema/volume names in config
   - Ensure proper authentication

### Getting Help

- Check Databricks documentation for Agent Bricks
- Review Unity Catalog permissions and setup
- Test individual components before integration
- Monitor agent status and error messages in the UI

---

## Next Steps and Extensions

After completing this lab, consider these enhancements:

1. **Add more data sources**:
   - Earnings estimates and analyst reports
   - Real-time news feeds
   - Economic indicators and market data

2. **Extend the Genie Space**:
   - Add the Genie Space ID to the Multi-Agent Supervisor
   - Include more complex financial calculations
   - Add additional financial metrics tables

3. **Create specialized agents**:
   - Sector-specific analysis agents
   - Risk assessment specialists
   - ESG (Environmental, Social, Governance) analysis

4. **Build automated workflows**:
   - Scheduled financial monitoring reports
   - Alert systems for significant market changes
   - Regular portfolio analysis updates

5. **Add external intelligence**:
   - MCP servers for web search capabilities
   - Real-time market data APIs
   - Social media sentiment analysis

## Workshop Scripts Reference

Your completed workshop includes these working components:

```
setup_instructor/
├── 01_instructor_setup_ka.ipynb          # ✅ Knowledge Assistant creation
├── 02_instructor_setup_genie.py          # ✅ Genie space for ticker data
├── 03_create_vegalite_uc_function_simple.ipynb  # ✅ Unity Catalog function
└── 04_instructor_setup_sa.py             # ✅ Multi-Agent Supervisor

resources/
├── data_setup_functions.py               # Infrastructure setup
├── download_ticker_data.py               # Ticker data download
├── brick_setup_functions.py              # Agent Bricks helper functions
└── generate_vega_lite_spec.py            # Visualization function code

data/
├── 10k/, 10Q/, annual_reports/           # 153 financial documents
├── earning_releases/, earning_transcripts/
```

**Congratulations!** You've built a comprehensive financial analysis multi-agent system that can analyze documents, query data, generate visualizations, and coordinate complex analytical workflows.