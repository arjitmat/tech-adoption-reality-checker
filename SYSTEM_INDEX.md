# System Index - Tech Adoption Reality Checker

## Project Structure

```
/tech-adoption-tracker
├── /data                    # Raw and processed data
│   ├── /raw                # API responses
│   │   ├── /enterprise_ai  # Enterprise platform data
│   │   └── /fintech_ai     # Fintech tool data
│   └── /processed          # Analyzed data
├── /src                     # Source code
│   ├── /collectors         # Data collection modules
│   │   ├── github.py      # GitHub API calls
│   │   ├── npm.py         # npm download stats
│   │   └── pypi.py        # PyPI download stats
│   ├── /analyzers          # Analysis modules
│   │   ├── velocity.py    # Growth rate calculations
│   │   ├── quality.py     # Data quality checks
│   │   ├── insights.py    # Pattern detection
│   │   └── comparative.py # Cross-list analysis
│   ├── /reporters          # Report generation
│   │   ├── generate.py    # Markdown → PDF
│   │   └── charts.py      # Visualizations
│   └── /utils              # Helper functions
│       ├── config.py      # API keys, settings, tech lists
│       └── logger.py      # Logging utilities
├── /reports                # Generated reports
│   ├── enterprise_ai_report.pdf
│   ├── fintech_ai_report.pdf
│   └── comparative_insights_report.pdf
├── /notebooks              # Jupyter analysis
├── /logs                   # System logs
├── /.github/workflows      # Automation (Phase 2)
├── requirements.txt        # Python dependencies
├── .env                    # Secrets (never commit)
├── .gitignore             # Git ignore patterns
├── CLAUDE.md              # Claude Code context
├── DEV_LOG.md             # Development journal
├── NAVIGATION.md          # Non-technical user guide
└── README.md              # Public documentation
```

## Key Files & Purpose

**Data Collection:**
- `collectors/github.py`: Fetches stars, forks, commits, issues for repositories
- `collectors/npm.py`: Gets npm package download counts
- `collectors/pypi.py`: Retrieves Python package statistics

**Analysis:**
- `analyzers/velocity.py`: Calculates growth rates and momentum
- `analyzers/quality.py`: Cross-validates signals across sources
- `analyzers/insights.py`: Detects patterns (hype vs real adoption)
- `analyzers/comparative.py`: Cross-list analysis for unique insights

**Reporting:**
- `reporters/generate.py`: Creates markdown and PDF reports
- `reporters/charts.py`: Generates visualizations

**Configuration:**
- `utils/config.py`: API keys, tracked technologies lists (ENTERPRISE_AI, FINTECH_AI)
- `utils/logger.py`: Centralized logging
- `.env`: Secrets (never commit to git)

## Data Flow

1. **Collection** → Collectors fetch raw data → `/data/raw/{list_name}/`
2. **Processing** → Analyzers process data → `/data/processed/`
3. **Insights** → Detect patterns → findings
4. **Reports** → Generate 3 reports → `/reports/`

## Strategic Lists

**ENTERPRISE_AI (15 technologies):**
Focus: AI platforms, infrastructure, and ML tools that enterprises adopt

**FINTECH_AI (12 technologies):**
Focus: Financial services AI, trading tools, risk/compliance solutions

**Total: 27 strategically-selected technologies**

## Module Dependencies

```
config.py (base)
    ↓
collectors/*.py → raw data
    ↓
analyzers/quality.py → validated data
    ↓
analyzers/velocity.py → growth metrics
    ↓
analyzers/insights.py → within-list patterns
    ↓
analyzers/comparative.py → cross-list insights
    ↓
reporters/*.py → final reports
```

## API Integrations

- **GitHub API**: Repository metrics (stars, forks, commits, issues)
- **npm API**: Package download statistics
- **PyPI API**: Python package download stats via pypistats

## Report Types

1. **Enterprise AI Report**: Platform wars, infrastructure trends
2. **Fintech AI Report**: Domain-specific adoption patterns
3. **Comparative Insights Report**: Cross-market synthesis (key differentiator)
