from openai import OpenAI
from typing import List, Dict
import json

class NISTAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # VERIFIED NIST PUBLICATION REFERENCE MAP
        self.publication_reference = {
            "800-218A": {
                "title": "SP 800-218A: SSDF Community Profile for Generative AI",
                "date": "2024-07-26",
                "status": "Final",
                "url": "https://csrc.nist.gov/pubs/sp/800/218/a/final"
            },
            "800-171r3": {
                "title": "SP 800-171 Rev. 3: Protecting Controlled Unclassified Information",
                "date": "2024-05-15",
                "status": "Final",
                "url": "https://csrc.nist.gov/pubs/sp/800/171/r3/final"
            },
            "csf-2.0": {
                "title": "NIST Cybersecurity Framework 2.0",
                "date": "2024-02-26",
                "status": "Final",
                "url": "https://csrc.nist.gov/pubs/sp/800/221/final"
            },
            "800-204D": {
                "title": "SP 800-204D: Software Supply Chain Security in DevSecOps CI/CD",
                "date": "2024-02-01",
                "status": "Final",
                "url": "https://csrc.nist.gov/pubs/sp/800/204/d/final"
            },
            "800-218": {
                "title": "SP 800-218: Secure Software Development Framework v1.1",
                "date": "2022-02-04",
                "status": "Final",
                "url": "https://csrc.nist.gov/pubs/sp/800/218/final"
            },
            "800-161r1": {
                "title": "SP 800-161 Rev. 1: Cybersecurity Supply Chain Risk Management",
                "date": "2022-05-13",
                "status": "Final",
                "errata": "2024-11-01",
                "url": "https://csrc.nist.gov/pubs/sp/800/161/r1/final"
            },
            "800-215": {
                "title": "SP 800-215: Guide to a Secure Enterprise Network Landscape",
                "date": "2022-11-17",
                "status": "Final",
                "url": "https://csrc.nist.gov/pubs/sp/800/215/final"
            },
            "800-53r5": {
                "title": "SP 800-53 Rev. 5: Security and Privacy Controls",
                "date": "2020-09-23",
                "status": "Final",
                "url": "https://csrc.nist.gov/pubs/sp/800/53/r5/final"
            },
            "800-190": {
                "title": "SP 800-190: Application Container Security Guide",
                "date": "2017-09-01",
                "status": "Final",
                "url": "https://csrc.nist.gov/pubs/sp/800/190/final"
            }
        }
    
    def filter_for_software_dev(self, articles: List[Dict]) -> str:
        """Filter content for software development relevance with accurate metadata."""
        print("Filtering content for software development relevance...")
        
        combined_content = "\n\n---\n\n".join([
            f"# {article.get('title', 'Unknown')}\n"
            f"Publication ID: {article.get('id', 'N/A')}\n"
            f"URL: {article.get('url', 'N/A')}\n"
            f"Status: {article.get('status', 'Final')}\n"
            f"Published: {article.get('date', 'N/A')}\n"
            f"Version: {article.get('version', 'N/A')}\n"
            f"{('Errata: ' + article.get('errata')) if article.get('errata') else ''}\n\n"
            f"{article.get('content', article.get('snippet', ''))}"
            for article in articles
        ])
        
        prompt = f"""Analyze the following NIST SP 800 series content and extract ONLY sections relevant to IT software development organizations.

CRITICAL: Preserve ALL metadata EXACTLY as provided (dates, status, versions, publication IDs).

Focus on software development practices:
1. Secure Software Development Lifecycle (SDLC) and SSDF practices
2. CI/CD pipeline security and DevSecOps
3. SAST/DAST and security testing automation
4. Software Bill of Materials (SBOM) and dependency management
5. Software supply chain security
6. Cloud-native and container security
7. Source code security and version control
8. API security and microservices
9. AI/ML system security (from SP 800-218A)
10. Control mappings to SP 800-53, 800-171, and SSDF

EXCLUDE:
- Physical security unrelated to software/cloud infrastructure
- Hardware procurement (unless software supply chain related)
- General organizational policies not affecting developers

Content to analyze:
{combined_content[:20000]}

Return filtered content in markdown with:
- Exact publication dates from source
- Correct status (Final/Draft)
- Accurate version numbers
- Proper publication IDs
- Source URLs"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a cybersecurity expert specializing in NIST frameworks for software development. CRITICAL: Never modify publication dates, status, or version numbers from source material. Use exact metadata provided."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=5000
            )
            
            filtered_content = response.choices[0].message.content
            print(f"Filtered content: {len(filtered_content)} characters")
            return filtered_content
            
        except Exception as e:
            print(f"Error filtering content: {e}")
            return combined_content[:8000]
    
    def map_to_controls(self, filtered_content: str) -> Dict:
        """Map content to NIST controls with verified publication references."""
        print("Mapping content to NIST controls...")
        
        # Create reference guide from our verified publication map
        pub_guide = "\n".join([
            f"- {pub_id}: {info['title']} ({info['date']})"
            for pub_id, info in self.publication_reference.items()
        ])
        
        prompt = f"""Analyze the NIST content and create explicit mappings to controls and frameworks.

VERIFIED PUBLICATIONS (USE ONLY THESE):
{pub_guide}

CRITICAL RULES:
1. ONLY reference publications from the verified list above
2. Use SP 800-204D for software supply chain security (NOT 800-204C)
3. Use SP 800-190 for container security
4. Use SP 800-218 for baseline SSDF practices
5. Use SP 800-218A for AI/ML-specific security
6. Include both SP 800-218 and 800-218A where relevant
7. Never invent publication numbers

For each relevant section, map to:
- NIST SP 800-53 Rev. 5 control families (SA-*, SI-*, CM-*, SC-*, AC-*)
- NIST SP 800-171 Rev. 3 requirements (3.X.X format)
- SSDF practices from SP 800-218 (PO.*, PS.*, PW.*, RV.*)

Content:
{filtered_content[:15000]}

Return valid JSON:
{{
  "mappings": [
    {{
      "section": "Brief description",
      "source_publication": "SP 800-XXX [Rev. X]",
      "publication_id": "800-XXX",
      "controls": {{
        "sp_800_53": ["SA-11", "SI-7"],
        "sp_800_171": ["3.13.1", "3.14.1"],
        "ssdf": ["PO.1", "PS.2", "PW.5"]
      }},
      "priority": "High/Medium/Low",
      "action": "Specific actionable requirement"
    }}
  ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at mapping security requirements to NIST controls. CRITICAL: Only use verified NIST publication numbers. SP 800-204D is for supply chain, SP 800-218 is baseline SSDF, SP 800-218A is for AI/ML. Respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            mappings_text = response.choices[0].message.content.strip()
            
            # Clean JSON formatting
            if mappings_text.startswith("```json"):
                mappings_text = mappings_text[7:]
            elif mappings_text.startswith("```"):
                mappings_text = mappings_text[3:]
            if mappings_text.endswith("```"):
                mappings_text = mappings_text[:-3]
            
            mappings = json.loads(mappings_text.strip())
            
            # Validate mappings reference only verified publications
            valid_mappings = []
            for mapping in mappings.get('mappings', []):
                pub_id = mapping.get('publication_id', '')
                if pub_id in self.publication_reference or not pub_id:
                    valid_mappings.append(mapping)
                else:
                    print(f"Warning: Removed invalid publication reference: {pub_id}")
            
            mappings['mappings'] = valid_mappings
            print(f"Generated {len(valid_mappings)} validated control mappings")
            return mappings
            
        except Exception as e:
            print(f"Error mapping controls: {e}")
            return {"mappings": []}
    
    def generate_summary(self, filtered_content: str, mappings: Dict, articles: List[Dict]) -> str:
        """Generate comprehensive summary with verified publication data."""
        print("Generating comprehensive summary...")
        
        # Sort articles by date and get recent ones
        recent_articles = sorted(articles, key=lambda x: x.get('date', ''), reverse=True)[:8]
        
        # Create verified articles list with exact metadata
        articles_info = "\n".join([
            f"- **{art.get('title')}**\n"
            f"  Published: {art.get('date')}\n"
            f"  Version: {art.get('version')}\n"
            f"  Status: {art.get('status', 'Final')}\n"
            f"  URL: {art.get('url')}\n"
            f"  {('Errata: ' + art.get('errata')) if art.get('errata') else ''}"
            for art in recent_articles
        ])
        
        # Create publication reference guide
        pub_guide = "\n".join([
            f"- {pub_id}: {info['title']} ({info['date']}) - {info['url']}"
            for pub_id, info in self.publication_reference.items()
        ])
        
        mappings_json = json.dumps(mappings, indent=2)
        
        prompt = f"""Create a comprehensive executive summary for software development leadership.

VERIFIED PUBLICATIONS (USE EXACT DATES AND URLS):
{articles_info}

PUBLICATION REFERENCE GUIDE:
{pub_guide}

Filtered Content:
{filtered_content[:12000]}

Control Mappings:
{mappings_json}

CRITICAL REQUIREMENTS:
1. Use EXACT publication dates from verified data above
2. Use CORRECT URLs in format: https://csrc.nist.gov/pubs/sp/XXX/[revision]/final
3. Mark Draft publications clearly (currently all are Final)
4. ONLY reference verified publications:
   - SP 800-218A (AI/ML) - 2024-07-26
   - SP 800-171 Rev. 3 - 2024-05-15
   - CSF 2.0 - 2024-02-26
   - SP 800-204D (Supply Chain) - 2024-02-01
   - SP 800-218 (SSDF baseline) - 2022-02-04
   - SP 800-161 Rev. 1 (C-SCRM) - 2022-05-13
   - SP 800-215 - 2022-11-17
   - SP 800-53 Rev. 5 - 2020-09-23
   - SP 800-190 (Containers) - 2017-09-01
5. Include BOTH SP 800-218 and 800-218A in latest updates
6. Use SP 800-204D (not 204C) for supply chain security
7. Single table only - no duplicates

Generate markdown summary with these sections:

## Executive Summary
2-3 sentences on concrete impacts to software development organizations.

## Latest Updates Discovered
List 6-8 most recent/relevant publications with:
- Full title
- EXACT publication date
- Status (Final/Draft)
- Version
- Specific relevance to software development
- Include both SP 800-218 and 800-218A

## Impact on Software Development Organizations
Clear takeaways on how updates affect development teams:
- SDLC integration requirements
- Supply chain security mandates
- Compliance requirements (CMMC, FedRAMP, etc.)
- AI/ML security considerations

## Key Actions and Checklist
5-6 specific actionable items with:
- Mapped controls (SP 800-53, SP 800-171, SSDF)
- Priority (High/Medium)
- Clear action description

## References and Citations
List all referenced publications with correct URLs.
Format: [NIST SP XXX](https://csrc.nist.gov/pubs/sp/XXX/.../final)

## Quick Reference Table
Single table with columns:
| Control/Practice | NIST Reference | Action Required | Priority |

Use professional language. Be specific and actionable."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a senior technical writer specializing in cybersecurity compliance. CRITICAL: Use exact publication dates from verified data. Never guess or invent dates. SP 800-204D is for supply chain (not 204C). Include both SP 800-218 and 800-218A. Use correct URL format: https://csrc.nist.gov/pubs/sp/XXX/[revision]/final"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            summary = response.choices[0].message.content
            
            # Validate summary has correct publication references
            summary = self._validate_and_fix_summary(summary)
            
            print(f"Summary generated: {len(summary)} characters")
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return self._generate_fallback_summary(articles)
    
    def _validate_and_fix_summary(self, summary: str) -> str:
        """Validate and fix common issues in generated summary."""
        
        # Fix incorrect publication numbers
        replacements = {
            "SP 800-204C": "SP 800-204D",
            "800-204C": "800-204D",
            "/pubs/sp/800/210/": "/pubs/sp/800/210/final",
            # Add more common errors as needed
        }
        
        for old, new in replacements.items():
            if old in summary:
                print(f"Fixed incorrect reference: {old} -> {new}")
                summary = summary.replace(old, new)
        
        return summary
    
    def _generate_fallback_summary(self, articles: List[Dict]) -> str:
        """Generate basic summary if main generation fails."""
        
        articles_list = "\n".join([
            f"- {art.get('title')} ({art.get('date')})"
            for art in sorted(articles, key=lambda x: x.get('date', ''), reverse=True)[:6]
        ])
        
        return f"""# NIST SP 800 Compliance Update

## Executive Summary
Recent NIST publications enhance security requirements for software development organizations.

## Latest Updates Discovered
{articles_list}

## Impact
Organizations must align SDLC practices with latest NIST guidance.

## References
See verified publications in source data.

Note: This is a fallback summary. Full generation encountered errors.
"""