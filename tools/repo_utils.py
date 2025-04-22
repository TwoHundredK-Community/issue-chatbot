import os
import subprocess
from langchain.tools import BaseTool

def clone_repository(repo: str, clone_dir: str) -> None:
    """Clone the GitHub repository to the specified local directory (if not already cloned)."""
    repo_url = f"https://github.com/{repo}.git"
    if os.path.isdir(clone_dir):
        # If repo already cloned, you could pull latest changes if desired
        return
    result = subprocess.run(["git", "clone", repo_url, clone_dir], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Git clone failed: {result.stderr}")

def gather_file_list(root_dir: str) -> str:
    """Walk through the repository directory and return a string listing all files (excluding certain dirs/files)."""
    file_paths = []
    exclude_dirs = {".git", ".github", "__pycache__", "node_modules", "venv"}  # common dirs to skip
    exclude_exts = {".png", ".jpg", ".jpeg", ".gif", ".zip", ".exe", ".dll"}    # skip binary files
    for base, dirs, files in os.walk(root_dir):
        # Prune directories we don't want to traverse
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
        for filename in files:
            # Skip binary or irrelevant file types by extension
            _, ext = os.path.splitext(filename)
            if ext.lower() in exclude_exts:
                continue
            # Compute path relative to root_dir for readability
            rel_path = os.path.relpath(os.path.join(base, filename), root_dir)
            file_paths.append(rel_path)
    # Join file paths into a single string (each file on a new line)
    file_paths.sort()
    return "\n".join(file_paths)

class ListRepoFilesTool(BaseTool):
    """Tool to clone a GitHub repo (if not already) and list all text-based file paths."""
    name = "list_repo_files"
    description = (
        "List all source code file paths in a GitHub repository. "
        "Use this to find which files exist in the repo. Excludes binary files and hidden folders."
    )

    def _run(self, repo_name: str) -> str:
        # Directory to store cloned repositories
        base_dir = os.path.join(os.getcwd(), "repos")
        os.makedirs(base_dir, exist_ok=True)
        # Use repo name with owner as part of path (replace slashes with underscores)
        repo_dir = os.path.join(base_dir, repo_name.replace("/", "_"))
        # Clone the repo if not already cloned
        if not os.path.isdir(repo_dir):
            try:
                git_url = f"https://github.com/{repo_name}.git"
                # If a GitHub token is available, use it for authenticated clone
                token = os.getenv("GITHUB_TOKEN")
                if token:
                    git_url = f"https://{token}@github.com/{repo_name}.git"
                subprocess.run(
                    ["git", "clone", "--depth", "1", git_url, repo_dir],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                return f"Error: Git clone failed for {repo_name} - {e}"
        # Walk through the repo directory and collect file paths
        file_paths = []
        skip_dirs = {".git", ".github", "__pycache__", "node_modules"}
        for root, dirs, files in os.walk(repo_dir):
            # Prune hidden and skip directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in skip_dirs]
            for fname in files:
                if fname.startswith("."):  # skip hidden files
                    continue
                full_path = os.path.join(root, fname)
                # Check for binary content by looking for null byte [oai_citation_attribution:8‡stackoverflow.com](https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python#:~:text=def%20is_binary%28filename%29%3A%20,it%20contains%20a%20NULL%20byte)
                try:
                    with open(full_path, "rb") as f:
                        chunk = f.read(1024)
                        if b"\x00" in chunk:
                            continue  # skip binary file
                except Exception:
                    continue  # skip files we can't read
                # Record the path relative to the repo root
                rel_path = os.path.relpath(full_path, repo_dir)
                file_paths.append(rel_path)
        # Return the list of files as a newline-separated string
        if not file_paths:
            return "No files found in repository."
        return "\n".join(file_paths)

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("ListRepoFilesTool does not support async")