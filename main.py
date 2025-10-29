#!/usr/bin/env python3

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.config import Config
from tools.search_tool import SearchTool
from tools.scraper_tool import ScraperTool
from tools.github_tool import GitHubTool
from agents.nist_agent import NISTAgent

def print_banner():
    print("\n" + "="*70)
    print("  NIST SP 800 Compliance Agent")
    print("  Automated Compliance Monitoring System")
    print("="*70 + "\n")

def main():
    print_banner()
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("Step 0: Validating configuration...")
    try:
        Config.validate()
        print("Configuration validated\n")
    except Exception as e:
        print(f"Configuration error: {e}")
        print("\nPlease create a .env file with your OPENAI_API_KEY")
        print("Copy .env.example to .env and add your keys\n")
        return
    
    search_tool = SearchTool()
    scraper_tool = ScraperTool()
    agent = NISTAgent(api_key=Config.OPENAI_API_KEY, model=Config.MODEL)
    github_tool = GitHubTool(token=Config.GITHUB_TOKEN, repo_name=Config.GITHUB_REPO) if Config.GITHUB_TOKEN else None
    
    print("="*70)
    print("Step 1: Searching for latest NIST SP 800 updates...")
    print("="*70)
    articles = search_tool.search_nist_updates(max_results=Config.MAX_ARTICLES)
    print(f"Found {len(articles)} publications\n")
    
    for i, article in enumerate(articles, 1):
        status_label = f" [{article['status']}]" if article.get('status') == 'Draft' else ""
        print(f"   {i}. {article['title']}{status_label}")
        print(f"      Published: {article['date']} | Version: {article['version']}")
    print()
    
    print("="*70)
    print("Step 2: Extracting content from publications...")
    print("="*70)
    
    for i, article in enumerate(articles, 1):
        print(f"   Processing {i}/{len(articles)}: {article['title'][:60]}...")
        html_content = search_tool.get_article_content(article['url'])
        markdown_content = scraper_tool.extract_content(
            html_content, 
            article['url'],
            metadata={
                'title': article['title'],
                'date': article['date'],
                'version': article['version'],
                'id': article['id'],
                'errata': article.get('errata'),
                'status': article.get('status', 'Final')
            }
        )
        article['content'] = markdown_content
    
    print(f"Extracted content from {len(articles)} publications\n")
    
    print("="*70)
    print("Step 3: Filtering for software development relevance...")
    print("="*70)
    filtered_content = agent.filter_for_software_dev(articles)
    print(f"Content filtered ({len(filtered_content)} chars)\n")
    
    print("="*70)
    print("Step 4: Mapping to NIST controls...")
    print("="*70)
    mappings = agent.map_to_controls(filtered_content)
    print(f"Generated {len(mappings.get('mappings', []))} control mappings\n")
    
    print("="*70)
    print("Step 5: Generating executive summary...")
    print("="*70)
    summary = agent.generate_summary(filtered_content, mappings, articles)
    print(f"Summary generated ({len(summary)} chars)\n")
    
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    local_file = os.path.join("outputs", f"nist-summary-{timestamp}.md")
    
    with open(local_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Saved locally: {local_file}\n")
    
    if github_tool:
        print("="*70)
        print("Step 6: Publishing to GitHub...")
        print("="*70)
        result = github_tool.create_pull_request(summary)
        print(f"Published: {result}\n")
    else:
        print("="*70)
        print("Step 6: Skipping GitHub publishing (no token configured)")
        print("="*70 + "\n")
        result = local_file
    
    print("="*70)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*70)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Processed: {len(articles)} publications")
    print(f"Output: {result}")
    print(f"\nCheck the {local_file} for your summary\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)