"""
Configuration for Tech Adoption Reality Checker
Strategic technology lists for dual-dimensional analysis
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
STACK_API_KEY = os.getenv('STACK_API_KEY')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
REPORTS_DIR = PROJECT_ROOT / 'reports'
LOGS_DIR = PROJECT_ROOT / 'logs'

# Ensure directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Strategic List 1: ENTERPRISE AI ADOPTION
# Focus: AI platforms, infrastructure, and ML tools that enterprises adopt
ENTERPRISE_AI = {
    "name": "Enterprise AI Platforms",
    "description": "AI platforms, infrastructure, and enterprise ML tools",
    "focus": "What enterprises choose for AI implementation",
    "technologies": [
        # Major AI Platforms
        {
            "name": "openai",
            "display_name": "OpenAI API",
            "github": "openai/openai-python",
            "npm": "openai",
            "pypi": "openai",
            "category": "ai_platform"
        },
        {
            "name": "anthropic-claude",
            "display_name": "Anthropic Claude",
            "github": "anthropics/anthropic-sdk-python",
            "pypi": "anthropic",
            "category": "ai_platform"
        },
        {
            "name": "google-gemini",
            "display_name": "Google Gemini",
            "github": "google/generative-ai-python",
            "pypi": "google-generativeai",
            "category": "ai_platform"
        },
        {
            "name": "aws-bedrock",
            "display_name": "AWS Bedrock",
            "github": "awslabs/amazon-bedrock-samples",
            "pypi": "boto3",  # Bedrock accessed via boto3
            "category": "ai_platform"
        },
        {
            "name": "azure-openai",
            "display_name": "Azure OpenAI",
            "github": "Azure/azure-sdk-for-python",
            "pypi": "azure-ai-openai",
            "category": "ai_platform"
        },
        {
            "name": "cohere",
            "display_name": "Cohere",
            "github": "cohere-ai/cohere-python",
            "npm": "cohere-ai",
            "pypi": "cohere",
            "category": "ai_platform"
        },

        # Enterprise AI Infrastructure
        {
            "name": "langchain",
            "display_name": "LangChain",
            "github": "langchain-ai/langchain",
            "npm": "langchain",
            "pypi": "langchain",
            "category": "ai_infrastructure"
        },
        {
            "name": "llamaindex",
            "display_name": "LlamaIndex",
            "github": "run-llama/llama_index",
            "pypi": "llama-index",
            "category": "ai_infrastructure"
        },
        {
            "name": "pinecone",
            "display_name": "Pinecone",
            "github": "pinecone-io/pinecone-python-client",
            "pypi": "pinecone-client",
            "category": "vector_db"
        },
        {
            "name": "weaviate",
            "display_name": "Weaviate",
            "github": "weaviate/weaviate",
            "pypi": "weaviate-client",
            "category": "vector_db"
        },
        {
            "name": "chromadb",
            "display_name": "ChromaDB",
            "github": "chroma-core/chroma",
            "pypi": "chromadb",
            "category": "vector_db"
        },
        {
            "name": "qdrant",
            "display_name": "Qdrant",
            "github": "qdrant/qdrant",
            "pypi": "qdrant-client",
            "category": "vector_db"
        },

        # Enterprise ML Platforms
        {
            "name": "databricks-ai",
            "display_name": "Databricks AI",
            "github": "databricks/databricks-sdk-py",
            "pypi": "databricks-sdk",
            "category": "ml_platform"
        },
        {
            "name": "huggingface",
            "display_name": "Hugging Face",
            "github": "huggingface/transformers",
            "pypi": "transformers",
            "category": "ml_platform"
        },
        {
            "name": "mlflow",
            "display_name": "MLflow",
            "github": "mlflow/mlflow",
            "pypi": "mlflow",
            "category": "ml_platform"
        },
    ]
}

# Strategic List 2: FINTECH + TRADING AI
# Focus: AI in financial services - domain expertise edge
FINTECH_AI = {
    "name": "Fintech & Trading AI",
    "description": "AI in financial services, trading tools, and risk/compliance",
    "focus": "AI adoption in financial services and trading",
    "technologies": [
        # Fintech Infrastructure
        {
            "name": "plaid",
            "display_name": "Plaid",
            "github": "plaid/plaid-python",
            "pypi": "plaid-python",
            "category": "fintech_infrastructure"
        },
        {
            "name": "stripe",
            "display_name": "Stripe",
            "github": "stripe/stripe-python",
            "pypi": "stripe",
            "npm": "stripe",
            "category": "fintech_infrastructure"
        },
        {
            "name": "alpaca",
            "display_name": "Alpaca Trading",
            "github": "alpacahq/alpaca-trade-api-python",
            "pypi": "alpaca-trade-api",
            "category": "trading_platform"
        },

        # Quantitative/Trading Tools
        {
            "name": "quantlib",
            "display_name": "QuantLib",
            "github": "lballabio/QuantLib",
            "pypi": "QuantLib",
            "category": "quant_tools"
        },
        {
            "name": "zipline",
            "display_name": "Zipline",
            "github": "quantopian/zipline",
            "pypi": "zipline-reloaded",
            "category": "trading_backtesting"
        },
        {
            "name": "backtrader",
            "display_name": "Backtrader",
            "github": "mementum/backtrader",
            "pypi": "backtrader",
            "category": "trading_backtesting"
        },
        {
            "name": "vectorbt",
            "display_name": "VectorBT",
            "github": "polakowo/vectorbt",
            "pypi": "vectorbt",
            "category": "trading_backtesting"
        },

        # Financial Data/AI
        {
            "name": "yfinance",
            "display_name": "yfinance",
            "github": "ranaroussi/yfinance",
            "pypi": "yfinance",
            "category": "financial_data"
        },
        {
            "name": "prophet",
            "display_name": "Prophet (Meta)",
            "github": "facebook/prophet",
            "pypi": "prophet",
            "category": "financial_ai"
        },
        {
            "name": "numerai",
            "display_name": "Numerai",
            "github": "numerai/numerapi",
            "pypi": "numerapi",
            "category": "trading_ai"
        },

        # Risk/Compliance AI
        {
            "name": "great-expectations",
            "display_name": "Great Expectations",
            "github": "great-expectations/great_expectations",
            "pypi": "great_expectations",
            "category": "risk_compliance"
        },
        {
            "name": "evidently",
            "display_name": "Evidently AI",
            "github": "evidentlyai/evidently",
            "pypi": "evidently",
            "category": "risk_compliance"
        },
    ]
}

# Configuration for which lists to analyze
ACTIVE_LISTS = {
    "enterprise": ENTERPRISE_AI,
    "fintech": FINTECH_AI
}

# API Rate Limits
GITHUB_RATE_LIMIT = 5000  # per hour for authenticated requests
GITHUB_DELAY = 0.5  # seconds between requests to be respectful

# Data Quality Thresholds
MIN_SOURCES_FOR_HIGH_CONFIDENCE = 2
DIVERGENCE_THRESHOLD = 0.5  # 50% difference between sources = hype flag
VELOCITY_SPIKE_THRESHOLD = 5.0  # 500% growth in one period = anomaly

# Report Configuration
REPORT_FORMATS = ['markdown', 'pdf']
TOP_N_INSIGHTS = 5  # Number of top insights to highlight
