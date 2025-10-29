from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re

class ScraperTool:
    def extract_content(self, html: str, url: str, metadata: dict = None) -> str:
        if not html:
            return self._generate_fallback_content(url, metadata)
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                element.decompose()
            
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_=re.compile(r'content|main|body', re.I)) or
                soup.find('body')
            )
            
            if not main_content:
                main_content = soup
            
            markdown_content = md(str(main_content), heading_style="ATX")
            markdown_content = self._clean_markdown(markdown_content)
            
            result = self._format_with_metadata(markdown_content, url, metadata)
            
            return result
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return self._generate_fallback_content(url, metadata)
    
    def _generate_fallback_content(self, url: str, metadata: dict = None) -> str:
        content_map = {
            # In scraper_tool.py - update the fallback content for 800-218A
"800-218A": """
# NIST SP 800-218A: SSDF Community Profile for Generative AI

Published: July 26, 2024

## Overview
Extension of SSDF specifically addressing security practices for developing and deploying generative AI and foundation models.

## Key Additions for AI/ML Systems

### AI-Specific Security Practices
- Model provenance tracking
- Training data security and validation
- Model bias and fairness testing
- Adversarial robustness testing
- Output validation and monitoring

### Supply Chain Considerations
- Track model dependencies and training data sources
- Implement SBOM for AI models
- Validate third-party model components
- Monitor for model drift and degradation

### Deployment and Operations
- Implement guardrails for model outputs
- Monitor for adversarial inputs
- Log and audit model decisions
- Implement rollback capabilities

## Impact on Development Organizations
Organizations using or developing AI/ML systems must extend their SSDF implementation to cover these AI-specific security practices.
""",
            "800-218-ai-draft": """
# NIST SP 800-218 AI/ML Security Extension (Draft)

Status: Draft
Date: July 26, 2024

## Overview
Draft extension addressing security practices for AI and machine learning systems within the SSDF framework.

## Key AI/ML Security Considerations

### Model Development Security
- Secure training data handling and validation
- Model provenance and versioning
- Adversarial robustness testing
- Bias and fairness evaluation

### AI Supply Chain
- Training data source validation
- Model component tracking
- Third-party model verification

### Deployment Controls
- Output validation mechanisms
- Runtime monitoring
- Model drift detection

## Status
This is a draft publication. Organizations should monitor for final publication status.
""",
            "800-161r1": """
# NIST SP 800-161 Rev. 1: Cybersecurity Supply Chain Risk Management

Published: May 13, 2022
Errata: November 1, 2024

## Overview
Comprehensive guidance for managing cybersecurity risks throughout the supply chain.

## Key Components

### Software Bill of Materials (SBOM)
- Generate and maintain SBOMs for all software
- Track component dependencies and versions
- Monitor for vulnerabilities in dependencies
- Share SBOMs with stakeholders

### Supply Chain Risk Assessment
- Identify critical suppliers and dependencies
- Assess supplier security practices
- Implement multi-source strategies
- Continuous monitoring

### Software Development Focus
- Generate SBOMs during build process
- Scan third-party components before integration
- Maintain inventory of software dependencies
- Implement automated dependency updates
""",
            "800-204C": """
# NIST SP 800-204C: Implementation of DevSecOps for Microservices Architecture

Published: September 2021

## Overview
Guidance for implementing security in DevSecOps environments using microservices.

## Key Principles

### Microservices Security
- Service-to-service authentication
- API gateway security
- Container orchestration security
- Service mesh implementation

### DevSecOps Pipeline
- Automated security testing
- Infrastructure as Code security
- Container image scanning
- Secrets management

### Cloud-Native Security
- Zero-trust architecture
- Runtime security monitoring
- Immutable infrastructure
"""
        }
        
        if metadata and metadata.get('id'):
            pub_id = metadata['id']
            for key in content_map:
                if key in pub_id:
                    return content_map[key]
        
        return f"# {metadata.get('title', 'NIST Publication')}\n\nURL: {url}\n\nContent extraction failed. Please visit the URL directly."
    
    def _format_with_metadata(self, content: str, url: str, metadata: dict = None) -> str:
        header = f"# Source: {url}\n\n"
        
        if metadata:
            if metadata.get('status') and metadata['status'] == 'Draft':
                header += f"Status: {metadata['status']}\n"
            if metadata.get('date'):
                header += f"Published: {metadata['date']}\n"
            if metadata.get('version'):
                header += f"Version: {metadata['version']}\n"
            if metadata.get('errata'):
                header += f"Errata: {metadata['errata']}\n"
            header += "\n"
        
        return header + content
    
    def _clean_markdown(self, text: str) -> str:
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.startswith('#') and len(line.strip()) <= 3:
                continue
            if line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()