# NIST SP 800 Compliance Agent

Automated AI workflow for monitoring NIST SP 800 series updates and generating applicability summaries for software development organizations.

## Overview

This agent searches NIST CSRC publications, extracts and converts content to Markdown, filters for software-development relevance using an LLM, maps findings to NIST control sets (800-53 Rev.5, 800-171 Rev.3, SSDF), generates executive summaries and checklists, and can publish results via GitHub pull requests.

This README provides complete, step-by-step instructions to set up, run, test, and deploy the application locally and in Docker.

## Prerequisites

- Git
- Python 3.11+ (recommended 3.11)
- pip
- virtualenv or venv
- Docker 24+ and Docker Compose v2 (optional, for container deployment)
- Optional: GitHub Personal Access Token (repo scope) to enable PR creation
- Required: OpenAI API Key

Supported OS: Windows, macOS, Linux. Windows examples use PowerShell syntax.

## Repository layout

```
nist-agent/
├── src/
│   ├── agents/
│   │   └── nist_agent.py
│   ├── tools/
│   │   ├── search_tool.py
│   │   ├── scraper_tool.py
│   │   └── github_tool.py
│   └── utils/
│       └── config.py
├── outputs/
├── main.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### Local Setup
```bash
git clone <your-repo-url>
cd nist-agent

pip install -r requirements.txt

cp .env.example .env
```

Edit `.env` with your credentials:
```
OPENAI_API_KEY=sk-your-key-here
GITHUB_TOKEN=ghp_your-token-here
GITHUB_REPO=username/repo-name
```

### Run the Agent
```bash
python main.py
```

## Docker Deployment

### Build
```bash
docker build -t nist-agent .
```

### Run
```bash
docker run --env-file .env nist-agent
```

### With Volume Mount
```bash
docker run --env-file .env -v $(pwd)/outputs:/app/outputs nist-agent
```

## Project Structure
```
nist-agent/
├── src/
│   ├── agents/
│   │   └── nist_agent.py
│   ├── tools/
│   │   ├── search_tool.py
│   │   ├── scraper_tool.py
│   │   └── github_tool.py
│   └── utils/
│       └── config.py
├── outputs/
├── main.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## How It Works

1. Search: Queries NIST CSRC for latest SP 800 series publications with accurate metadata
2. Extract: Downloads and converts content to Markdown with publication dates and status
3. Filter: AI identifies software development relevant sections while preserving source metadata
4. Map: Creates explicit mappings to NIST controls (800-53 Rev. 5, 800-171 Rev. 3, SSDF)
5. Summarize: Generates comprehensive executive summary with verified publication information
6. Publish: Creates GitHub PR or saves locally

## Output Format

Generated summaries include:

- Executive summary with specific impact analysis
- Latest updates with accurate publication dates and status (Final/Draft)
- Impact on software development organizations
- Actionable checklists mapped to specific controls
- NIST SP 800-53 Rev. 5 control families
- NIST SP 800-171 Rev. 3 requirements
- SSDF task references from SP 800-218
- Source citations with official NIST URLs
- Single consolidated quick reference table

## Key Improvements

### Accuracy Enhancements

- Removed non-existent SP 800-218A reference
- Corrected SP 800-215 publication date to November 17, 2023
- Replaced incorrect SP 800-210 references with correct SP 800-204C
- Added proper Draft status labeling for preliminary publications
- Included errata dates where applicable
- Eliminated duplicate tables in output

### Verified Publication Data

- SP 800-218 (SSDF v1.1): February 4, 2022
- SP 800-161 Rev. 1: May 13, 2022 (Errata: November 1, 2024)
- SP 800-53 Rev. 5: September 23, 2020
- SP 800-171 Rev. 3: May 15, 2024
- SP 800-204C: September 2021
- SP 800-204D: February 1, 2024
- SP 800-215: November 17, 2023
- CSF 2.0: February 26, 2024

## Configuration

Edit `src/utils/config.py`:
```python
MAX_ARTICLES = 10
MODEL = "gpt-4o-mini"
```

## Security

- Never commit `.env` file
- Keep API keys secure
- Use environment variables in production
- GitHub token requires `repo` scope for PR creation

## Troubleshooting

### OpenAI API Errors

Ensure your API key is valid and has sufficient credits:
```bash
echo $OPENAI_API_KEY
```

### GitHub Authentication

Verify token permissions include:
- repo (full control)
- workflow (if using GitHub Actions)

### Content Extraction Issues

The agent includes accurate fallback content for NIST publications if web scraping fails.

## Output Accuracy

The agent ensures:
- All publication dates match official NIST sources
- Draft vs Final status is clearly indicated
- Correct NIST publication numbers are used
- Full publication titles include proper context
- URLs follow official NIST format
- No duplicate content in summaries

## API Rate Limits

- OpenAI: Monitor token usage in API dashboard
- GitHub: 5000 requests/hour for authenticated users

## Contributing

Contributions welcome. Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## License

MIT License

## Support

For issues or questions, please open a GitHub issue with detailed information.