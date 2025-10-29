#!/usr/bin/env python3
"""
NIST Output Validator
Validates generated summaries for accuracy and compliance with requirements
"""

import re
import sys
from datetime import datetime

class NISTOutputValidator:
    def __init__(self):
        # Verified publication dates and references
        self.verified_pubs = {
            "800-218A": {"date": "2024-07-26", "title": "SSDF Community Profile for Generative AI"},
            "800-171r3": {"date": "2024-05-15", "title": "Protecting Controlled Unclassified Information"},
            "csf-2.0": {"date": "2024-02-26", "title": "Cybersecurity Framework 2.0"},
            "800-204D": {"date": "2024-02-01", "title": "Software Supply Chain Security in DevSecOps"},
            "800-218": {"date": "2022-02-04", "title": "Secure Software Development Framework"},
            "800-161r1": {"date": "2022-05-13", "title": "Cybersecurity Supply Chain Risk Management"},
            "800-215": {"date": "2022-11-17", "title": "Guide to a Secure Enterprise Network Landscape"},
            "800-53r5": {"date": "2020-09-23", "title": "Security and Privacy Controls"},
            "800-190": {"date": "2017-09-01", "title": "Application Container Security Guide"},
        }
        
        # Invalid publications that should NOT appear
        self.invalid_pubs = [
            "800-204C",  # Common error - should be 800-204D
            "800-210",   # Cloud access control - not relevant for most summaries
        ]
        
        self.errors = []
        self.warnings = []
        self.passed_checks = []
    
    def validate_file(self, filepath: str) -> dict:
        """Validate a markdown summary file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n{'='*70}")
            print(f"Validating: {filepath}")
            print(f"{'='*70}\n")
            
            self._check_required_sections(content)
            self._check_publication_dates(content)
            self._check_invalid_publications(content)
            self._check_urls(content)
            self._check_duplicate_tables(content)
            self._check_publication_coverage(content)
            
            return self._generate_report()
            
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        except Exception as e:
            print(f"Error validating file: {e}")
            sys.exit(1)
    
    def _check_required_sections(self, content: str):
        """Check for required sections."""
        required_sections = [
            "Executive Summary",
            "Latest Updates Discovered",
            "Impact on Software Development Organizations",
            "Key Actions and Checklist",
            "References and Citations",
            "Quick Reference Table"
        ]
        
        for section in required_sections:
            if section in content:
                self.passed_checks.append(f"✓ Section found: {section}")
            else:
                self.errors.append(f"✗ Missing required section: {section}")
    
    def _check_publication_dates(self, content: str):
        """Verify publication dates match verified data."""
        for pub_id, pub_info in self.verified_pubs.items():
            # Look for the publication in content
            patterns = [
                rf"800-{pub_id.split('-')[1]}",  # e.g., 800-218A
                rf"SP {pub_id.replace('-', ' ')}",  # e.g., SP 800 218A
            ]
            
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if correct date appears near this publication
                    correct_date = pub_info["date"]
                    
                    # Find all dates near this publication reference
                    pub_context = self._get_context(content, pattern, 200)
                    dates_found = re.findall(r'\d{4}-\d{2}-\d{2}', pub_context)
                    
                    if correct_date in dates_found:
                        self.passed_checks.append(
                            f"✓ Correct date for {pub_id}: {correct_date}"
                        )
                    elif dates_found:
                        self.warnings.append(
                            f"⚠ Possible incorrect date for {pub_id}. "
                            f"Expected: {correct_date}, Found: {dates_found[0]}"
                        )
    
    def _check_invalid_publications(self, content: str):
        """Check for invalid publication references."""
        for invalid_pub in self.invalid_pubs:
            if invalid_pub in content:
                self.errors.append(
                    f"✗ Invalid publication referenced: {invalid_pub}"
                )
            else:
                self.passed_checks.append(
                    f"✓ No reference to invalid publication: {invalid_pub}"
                )
    
    def _check_urls(self, content: str):
        """Validate URL formats."""
        # Find all NIST URLs
        urls = re.findall(r'https://csrc\.nist\.gov[^\s\)]+', content)
        
        correct_pattern = r'https://csrc\.nist\.gov/pubs/sp/\d+/[^/\s]+/final'
        
        for url in urls:
            if re.match(correct_pattern, url):
                self.passed_checks.append(f"✓ Correct URL format: {url}")
            else:
                self.warnings.append(f"⚠ Check URL format: {url}")
    
    def _check_duplicate_tables(self, content: str):
        """Check for duplicate tables."""
        table_headers = re.findall(r'\|.*\|.*\|', content)
        
        if len(table_headers) > 5:  # More than one table typically
            self.warnings.append(
                f"⚠ Multiple tables detected ({len(table_headers)} rows). "
                "Verify no duplicates."
            )
        else:
            self.passed_checks.append("✓ Single reference table (no duplicates)")
    
    def _check_publication_coverage(self, content: str):
        """Check if key publications are mentioned."""
        key_pubs = ["800-218A", "800-218", "800-171", "800-204D"]
        
        missing = []
        for pub in key_pubs:
            if pub not in content:
                missing.append(pub)
        
        if missing:
            self.warnings.append(
                f"⚠ Key publications not mentioned: {', '.join(missing)}"
            )
        else:
            self.passed_checks.append("✓ All key publications referenced")
    
    def _get_context(self, content: str, pattern: str, chars: int = 200) -> str:
        """Get context around a pattern match."""
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            start = max(0, match.start() - chars)
            end = min(len(content), match.end() + chars)
            return content[start:end]
        return ""
    
    def _generate_report(self) -> dict:
        """Generate validation report."""
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70 + "\n")
        
        # Passed checks
        if self.passed_checks:
            print(f"✓ PASSED CHECKS ({len(self.passed_checks)}):")
            for check in self.passed_checks[:10]:  # Show first 10
                print(f"  {check}")
            if len(self.passed_checks) > 10:
                print(f"  ... and {len(self.passed_checks) - 10} more")
            print()
        
        # Warnings
        if self.warnings:
            print(f"⚠ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        # Errors
        if self.errors:
            print(f"✗ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        # Summary
        total_checks = len(self.passed_checks) + len(self.warnings) + len(self.errors)
        pass_rate = (len(self.passed_checks) / total_checks * 100) if total_checks > 0 else 0
        
        print("="*70)
        print(f"SUMMARY: {len(self.passed_checks)}/{total_checks} checks passed ({pass_rate:.1f}%)")
        print("="*70 + "\n")
        
        if self.errors:
            print("VALIDATION FAILED - Please fix errors above\n")
            return {"status": "failed", "errors": len(self.errors)}
        elif self.warnings:
            print("⚠ VALIDATION PASSED WITH WARNINGS\n")
            return {"status": "passed_with_warnings", "warnings": len(self.warnings)}
        else:
            print("VALIDATION PASSED - All checks successful!\n")
            return {"status": "passed"}


def main():
    if len(sys.argv) < 2:
        print("Usage: python output_validator.py <path-to-summary.md>")
        print("\nExample:")
        print("  python output_validator.py outputs/nist-summary-2024-10-24-123456.md")
        sys.exit(1)
    
    validator = NISTOutputValidator()
    result = validator.validate_file(sys.argv[1])
    
    # Exit with appropriate code
    if result["status"] == "failed":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()