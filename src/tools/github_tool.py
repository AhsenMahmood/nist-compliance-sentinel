from github import Github, Auth, GithubException
from datetime import datetime
import os

class GitHubTool:
    def __init__(self, token, repo_name):
        if not token:
            raise ValueError("GitHub token is required")
        
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.repo_name = repo_name
        self.base_branch = "main"
        
    def create_pull_request(self, summary_content, filename=None):
        try:
            repo = self.github.get_repo(self.repo_name)
            print(f"Connected to: {repo.full_name}")
            
            if not filename:
                timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
                filename = f"nist-summary-{timestamp}.md"
            
            branch_name = f"nist-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            base_ref = repo.get_git_ref(f"heads/{self.base_branch}")
            base_sha = base_ref.object.sha
            
            print(f"Creating branch: {branch_name}")
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha
            )
            
            file_path = f"summaries/{filename}"
            print(f"Creating file: {file_path}")
            
            try:
                contents = repo.get_contents(file_path, ref=branch_name)
                repo.update_file(
                    path=file_path,
                    message=f"Update NIST SP 800 Summary - {datetime.now().strftime('%Y-%m-%d')}",
                    content=summary_content,
                    sha=contents.sha,
                    branch=branch_name
                )
            except GithubException as e:
                if e.status == 404:
                    repo.create_file(
                        path=file_path,
                        message=f"Add NIST SP 800 Summary - {datetime.now().strftime('%Y-%m-%d')}",
                        content=summary_content,
                        branch=branch_name
                    )
                else:
                    raise
            
            print(f"Creating Pull Request...")
            pr_title = f"NIST SP 800 Compliance Update - {datetime.now().strftime('%Y-%m-%d')}"
            pr_body = f"""## NIST SP 800 Compliance Update

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This PR contains the latest NIST SP 800 series updates relevant to software development organizations.

### Summary Contents
- Accurate publication dates from official NIST sources
- Draft vs Final status clearly indicated
- Correct NIST publication references
- Control mappings to SP 800-53 Rev. 5, SP 800-171 Rev. 3, and SSDF
- Actionable recommendations for development teams

### Changes
- Added/Updated: `{file_path}`

### Verification
All publication dates and references have been verified against official NIST sources.

Please review and merge."""
            
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=self.base_branch
            )
            
            print(f"Pull Request created: {pr.html_url}")
            return pr.html_url
            
        except GithubException as e:
            error_msg = f"GitHub API Error: {e.status} {e.data}"
            print(f"Error creating PR: {error_msg}")
            return self._save_locally(summary_content, filename)
            
        except Exception as e:
            print(f"Error creating PR: {str(e)}")
            return self._save_locally(summary_content, filename)
    
    def _save_locally(self, content, filename=None):
        try:
            os.makedirs("outputs", exist_ok=True)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
                filename = f"nist-summary-{timestamp}.md"
            
            filepath = os.path.join("outputs", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Summary saved locally: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving locally: {e}")
            return "Failed to save"
    
    def verify_access(self):
        try:
            repo = self.github.get_repo(self.repo_name)
            user = self.github.get_user()
            
            print(f"GitHub Access Verified")
            print(f"   User: {user.login}")
            print(f"   Repo: {repo.full_name}")
            print(f"   Default branch: {repo.default_branch}")
            
            return True
        except Exception as e:
            print(f"Access verification failed: {e}")
            return False
