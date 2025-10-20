# Setup Guide - Tech Adoption Reality Checker

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
# GitHub API Token (get from https://github.com/settings/tokens)
GITHUB_TOKEN=your_github_token_here

# Stack API Key (optional)
STACK_API_KEY=your_stack_key_here
```

### 3. Run Data Collection

```bash
# Collect data for all lists
python src/collect_all.py

# Or collect for specific list
python src/collect_all.py --list enterprise
python src/collect_all.py --list fintech
```

### 4. Run Analysis

```bash
python src/analyze_all.py
```

### 5. Generate Reports

```bash
python src/generate_reports.py
```

---

## GitHub Actions Setup (Autonomous Updates)

To enable daily automated updates:

### Step 1: Add Repository Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add these secrets:

**GITHUB_API_TOKEN:**
- Name: `GITHUB_API_TOKEN`
- Value: Your GitHub personal access token
- Get from: https://github.com/settings/tokens
- Permissions needed: `repo`, `workflow`

**STACK_API_KEY** (optional):
- Name: `STACK_API_KEY`
- Value: Your Stack API key

### Step 2: Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. Enable workflows if prompted
3. The workflow will run:
   - **Automatically**: Every day at 9 AM UTC
   - **Manually**: Click "Run workflow" button in Actions tab

### Step 3: Verify It Works

1. Go to **Actions** tab
2. Click "Daily Tech Adoption Update"
3. Click "Run workflow" → "Run workflow" (to test manually)
4. Wait ~5 minutes
5. Check if new commit appears with updated reports

---

## Configuration

### Modify Technology Lists

Edit `src/utils/config.py`:

```python
ENTERPRISE_AI = {
    "technologies": [
        {"name": "openai", "github": "openai/openai-python", ...},
        # Add more technologies here
    ]
}
```

### Change Update Schedule

Edit `.github/workflows/daily-update.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Change time here (UTC)
```

---

## Troubleshooting

**"API Rate Limit" error:**
- GitHub allows 5000 requests/hour with authentication
- Wait 1 hour or run with `--list` flag for one list at a time

**"Module not found" error:**
- Run: `pip install -r requirements.txt`

**Workflow fails in GitHub Actions:**
- Check if secrets are configured correctly
- View logs in Actions tab for specific error

---

## Project Structure

```
tech-adoption-tracker/
├── src/
│   ├── collectors/     # Data collection from APIs
│   ├── analyzers/      # Quality, velocity, insights
│   ├── reporters/      # Report generation
│   └── utils/          # Configuration & logging
├── data/
│   ├── raw/           # Collected data (not in git)
│   └── processed/     # Analysis results (not in git)
├── reports/           # Generated reports
├── .github/workflows/ # Automation configuration
└── README.md          # Project overview
```

---

## Manual Workflow

If you don't want autonomous updates, run manually:

```bash
# Full pipeline
python src/collect_all.py && \
python src/analyze_all.py && \
python src/generate_reports.py
```

Or run components individually as needed.
