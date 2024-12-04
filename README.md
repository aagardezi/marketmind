# FISDFunctionCallingDemo

This project demonstrates using Google Cloud Functions to implement a function-calling flow with Gemini, integrating with external APIs (Finhub) and BigQuery. It uses Streamlit for a user interface and leverages the `functions-framework` for local development.

## Project Structure

* **`main.py`**: This is the main entry point for the Cloud Function. It handles user input from the Streamlit interface, interacts with the Gemini model, processes function calls, and displays responses.
* **`helperfinhub.py`**: Contains functions for interacting with the Finhub API.  Each function corresponds to a specific Finhub API endpoint.
* **`helperbqfunction.py`**: Contains functions for interacting with BigQuery.  These functions handle dataset listing, table information retrieval, and SQL query execution.
* **`geminifunctionfinhub.py`**: Defines the function declarations for Finhub API calls that Gemini can use.
* **`geminifunctionsbq.py`**: Defines the function declarations for BigQuery operations that Gemini can use.
* **`helpercode.py`**: Contains utility functions, such as fetching text content from URLs, used to support API interactions.

## Functionality

The application allows users to interact with Gemini via a Streamlit chat interface. User queries can trigger function calls to either Finhub or BigQuery, based on the function declarations provided to the model.  The results from these calls are then incorporated into Gemini's response.  The application handles both serial and parallel function calls from Gemini.

## Local Development

1. **Set up virtual environment:**  Create and activate a virtual environment to manage project dependencies.
2. **Install dependencies:** Install the required packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt

MarketMind



This demo showcases an AI-powered financial analyst built using Gemini, capable of complex financial analysis and reporting. It addresses the challenge of quickly gathering and analyzing diverse financial data, streamlining investment research and decision-making.

Business Value:

Accelerated Research: The demo automates the tedious process of collecting data from various sources (BigQuery for market data, Finnhub for company information, news sentiment APIs), enabling analysts to focus on higher-level insights.
Enhanced Decision-Making: By providing a comprehensive overview of a company's financials, news, and peer comparisons, the demo empowers users to make better-informed investment choices.
Improved Efficiency: Automating the analysis process frees up analysts' time, allowing them to handle larger volumes of research or dedicate their expertise to more complex tasks.
Data-Driven Insights: The tool leverages large datasets and AI, providing insights that might be missed by manual analysis.
Technical Value:

Gemini's Power: The demo highlights the capabilities of Gemini for complex reasoning, tool use, and function calling.
Integration with Google Cloud: It demonstrates seamless integration with various Google Cloud services, including Vertex AI, BigQuery, and Secret Manager.
Scalability: The architecture is inherently scalable, allowing for handling increasing volumes of data and requests.
Extensibility: The demo can be easily extended to incorporate additional data sources and analytical functions.
Business Challenge Solved:

The demo addresses the challenge of efficient financial analysis in a data-rich environment. Traditional research methods are time-consuming and often involve manual data aggregation from disparate sources. This demo provides a unified platform to access and analyze relevant information quickly, empowering analysts and investors with readily available insights.

The demo addresses the challenge of efficient financial analysis in a data-rich environment. Traditional research methods are time-consuming and often involve manual data aggregation from disparate sources. This demo provides a unified platform to access and analyze relevant information quickly

This demo showcases an AI-powered financial analyst built using Gemini Agents, capable of complex financial analysis and reporting. It addresses the challenge of quickly gathering and analyzing diverse financial data, streamlining investment research and decision-making. raditional research methods are time-consuming and often involve manual data aggregation from disparate sources. This demo provides a unified platform to access and analyze relevant information quickly.



Attendees will be wowed by the seamless integration of Gemini's natural language capabilities with real-time financial data analysis. Imagine asking, "What are the key financial indicators for Tesla compared to its competitors, and what has the news sentiment been around the company this week?" and getting a comprehensive, data-driven response instantly, pulling information from Finnhub, BigQuery, and news sentiment APIs – all orchestrated through a conversational interface. The speed and depth of analysis, combined with the intuitive interaction, are the key "wow" factors.

Teaching Attendees:

The demo's open-source nature, coupled with clear documentation (the README.md and potentially additional materials), will be crucial for attendee learning. The code showcases how to:

Structure a function-calling application: Attendees can examine the project structure, including how function declarations are defined and how the main.py file orchestrates the interaction between Gemini, the Streamlit UI, and the backend functions.
Integrate with external APIs and BigQuery: The code demonstrates practical examples of making API calls (Finnhub) and querying BigQuery, providing reusable templates for similar integrations.
Handle Gemini's function-calling responses: The demo shows how to process and display the structured data returned by Gemini's function calls, which is essential for building effective applications.
Call to Action:

The call to action will be multi-pronged:

Explore the code: Attendees should be encouraged to download the code from the repository (GitHub, etc.), experiment with it, and adapt it to their use cases.
Join the community: A call to join a Google Cloud community forum or Slack channel would allow attendees to continue learning, ask questions, and share their experiences.
Build their own applications: The ultimate goal is to inspire attendees to leverage Gemini and Google Cloud to develop their own AI-powered solutions, potentially in the financial domain or other areas that benefit from data analysis and intelligent automation. Clear documentation and community support are essential for achieving this.

This demo showcases an AI-powered financial analyst built with Gemini, enabling complex analysis and reporting through natural language. Users can query real-time financial data from Finnhub and BigQuery via a Streamlit interface, receiving comprehensive insights on companies, market trends, and news sentiment. The application demonstrates Gemini's function-calling capabilities, seamlessly integrating with external APIs and databases for streamlined investment research. The provided codebase offers a practical example of building intelligent, data-driven applications on Google Cloud. Experience the future of financial analysis with the power of Gemini.


Developers:

Learning Gemini function calling: The project serves as an educational resource for developers learning how to implement function calling with Gemini. The clear project structure and example code provide a practical template for building similar applications.
Integrating with external APIs and BigQuery: Developers can learn how to connect Gemini to external data sources like Finnhub and BigQuery, gaining experience with data integration and API interaction within a Gemini-powered application.
Building Streamlit interfaces for LLMs: The project demonstrates how to use Streamlit to create interactive user interfaces for Gemini-based applications, showcasing how to handle user input and display model responses.
Customers (Financial Industry):

Accelerated Financial Analysis: Financial analysts can use this type of application to quickly gather and analyze company information, market data, and news sentiment, enabling faster and more informed decision-making.
Investment Research: The demo provides a platform for conducting comprehensive investment research, automating the collection and analysis of relevant financial data.
Automated Reporting: The tool can be used to generate customized financial reports, saving time and resources compared to manual report creation.
Partners (Technology Consultants/Integrators):

Building custom solutions for financial clients: System integrators can leverage the project as a starting point for developing tailored financial analysis solutions for their clients, incorporating additional data sources and analytical functionalities.
Demonstrating Gemini's capabilities: The demo can be used to showcase the power and flexibility of Gemini to potential clients in the financial industry.
Expanding service offerings: Consultants can add Gemini-based solutions to their portfolio, offering new services related to AI-driven financial analysis and reporting.


Events:

Smaller industry conferences (FinTech, AI, Data Science): The demo is highly relevant to specialized audiences interested in financial technology, AI applications, or data science. It can be adapted to focus on specific aspects like Gemini's capabilities or data integration techniques.
Google Cloud events (roadshows, workshops): The demo is a great showcase of Google Cloud products (Gemini, BigQuery, Cloud Functions, etc.) and can be incorporated into broader presentations about Google Cloud's AI/ML offerings. Hands-on workshops could be developed around the demo code.
University recruiting events/hackathons: The project's clear structure and focus on cutting-edge technology make it attractive for student engagement. It can be used in hackathons or recruiting events to inspire and educate aspiring developers.
Campaigns:

Online marketing campaigns (blog posts, webinars, social media): The demo can be featured in content marketing efforts, such as blog posts, webinars, or social media posts, to demonstrate the practical applications of Gemini and Google Cloud in the financial industry. Code snippets and explanatory videos can be included to enhance engagement.
Targeted email campaigns: The demo can be used in targeted email campaigns to specific customer segments (e.g., financial institutions, investment firms) to promote Google Cloud's AI/ML solutions.
Sales Meetings:

Proof-of-concept for potential clients: The demo can be adapted as a personalized proof-of-concept for potential clients in the financial sector, showcasing how Gemini can be tailored to address their specific data analysis needs. Live demonstrations can be highly effective in sales meetings.
Technical deep dives: For clients interested in the technical details, the codebase can be used to illustrate the architecture and implementation of a Gemini-powered solution.
Other Use Cases:

Internal training: The demo project can be used to train Google Cloud sales teams and solutions architects on Gemini and related technologies.
Open-source contribution: The project can be further developed and released as a more comprehensive open-source tool for financial analysis, fostering community engagement and attracting external contributions.