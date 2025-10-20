# Navigation Guide - For Non-Technical Users

## Quick Start - Running the System

### Collect Fresh Data
```bash
python src/main.py --collect
```
**What it does:** Fetches latest data from GitHub, npm, and PyPI for all tracked technologies
**Time:** ~5-10 minutes
**Output:** New files in `/data/raw/enterprise_ai/` and `/data/raw/fintech_ai/`

### Generate Analysis Report
```bash
python src/main.py --analyze
```
**What it does:** Analyzes collected data, creates insights
**Time:** ~2 minutes
**Output:** Processed data in `/data/processed/`

### Create Reports
```bash
python src/main.py --report
```
**What it does:** Generates 3 PDF reports (Enterprise AI, Fintech AI, Comparative)
**Time:** ~1 minute
**Output:** Reports in `/reports/` folder

### Run Everything
```bash
python src/main.py --all
```
**What it does:** Complete end-to-end: collect → analyze → report
**Time:** ~10 minutes total

### Analyze Specific List
```bash
python src/main.py --list enterprise
python src/main.py --list fintech
```
**What it does:** Focus on one strategic list only

## Understanding the Output

### Report Sections

**1. Executive Summary:** Top 3 insights from analysis
**2. Adoption Leaders:** Technologies with fastest growth
**3. Quality Signals:** Multi-source validation results
**4. Trends:** Month-over-month changes
**5. Comparative Insights:** Cross-market patterns (Comparative Report only)

### Key Metrics Explained

- **Velocity:** Rate of growth (% per month)
- **Quality Score:** How many sources confirm trend (1-5 scale)
- **Hype Flag:** Warning when signals diverge (⚠️)
- **Confidence:** Data reliability (High/Medium/Low)

### The Three Reports

**1. Enterprise AI Report** (`enterprise_ai_report.pdf`)
- AI platform adoption trends
- Infrastructure and tooling patterns
- Platform wars (AWS vs Azure vs OpenAI)

**2. Fintech AI Report** (`fintech_ai_report.pdf`)
- Financial services AI adoption
- Trading and payments tools
- Risk/compliance technology trends

**3. Comparative Insights Report** (`comparative_insights_report.pdf`) ⭐ **Most Valuable**
- Cross-market patterns between enterprise and fintech
- Leading indicators (what predicts what)
- Adoption lag analysis
- Unique insights from dual-dimensional analysis

## Troubleshooting

### "API Rate Limit Error"
**Cause:** GitHub API limits (5000 requests/hour for authenticated)
**Solution:** Wait 1 hour, or run with `--list` flag to analyze one list at a time

### "No data found"
**Cause:** Need to collect data first
**Solution:** Run `python src/main.py --collect` before analyzing

### "Module not found"
**Cause:** Python dependencies not installed
**Solution:** Run `pip install -r requirements.txt`

### "Authentication failed"
**Cause:** GitHub token not configured or expired
**Solution:** Check `.env` file has correct `GITHUB_TOKEN` value

## File Locations

**Latest reports:** `/reports/` folder
**Raw data:** `/data/raw/enterprise_ai/` and `/data/raw/fintech_ai/`
**Processed data:** `/data/processed/`
**Technology lists:** `src/utils/config.py` (ENTERPRISE_AI and FINTECH_AI dictionaries)
**Logs:** `/logs/system.log`

## Project Status

Check `CLAUDE.md` for:
- Current phase
- Recent changes
- Known issues
- Next steps
