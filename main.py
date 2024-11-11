import gitlab
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

gitlab_url = os.getenv("GITLAB_URL", "")
print(gitlab_url)
gitlab_token = os.getenv("GITLAB_TOKEN")
print(gitlab_token)
gl = gitlab.Gitlab(url=gitlab_url, private_token=gitlab_token,keep_base_url=True)
gl.auth()

def clone_repo(repo_url):
    repo_url = repo_url.strip()
    project_name = repo_url.split(':')[-1]
    subprocess.run(["git","clone","--bare",repo_url,f"repo/{project_name}"])

def clone():
    with open('repo.txt','r') as f:
        repos = f.readlines()
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(clone_repo, repos)

def get_projects_list():
    projects = gl.projects.list(iterator=True)
    count = 0 
    for project in projects:
        with open("repo.txt", 'a') as f:
            f.write(project.ssh_url_to_repo + '\n')
        count += 1
    print(count)

def is_dir_exist(repo_url):
    repo_url = repo_url.strip()
    project_name = repo_url.split(':')[-1]
    project_path = f"repo/{project_name}"
    if not os.path.exists(project_path):
        print(repo_url)
    else:
        print("exist")

def diff_missing_project():
    with open('repo.txt','r') as f:
        repos = f.readlines()
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(is_dir_exist, repos)

def main():
    get_projects_list()
    clone()
    diff_missing_project()
    
main()