import gitlab
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

class BaseGitlab(object):
    def __init__(self, url, token, repo_file, repo_store_dir) -> None:
        self.url = url
        self.token = token
        self.gl = None
        self.repo_file = repo_file
        self.repo_store_dir = repo_store_dir

    def Gen_Gitlab(self):
        self.gl = gitlab.Gitlab(url=self.url, private_token=self.token)
    
    def gitlab_auth(self):
        self.gl.auth()




class CurrentGItlab(BaseGitlab):
    def __init__(self, url, token, repo_file, repo_store_dir) -> None:
        super().__init__(url, token, repo_file, repo_store_dir)
    
    def clone_repo(self, repo_url):
        repo_url = repo_url.strip()
        project_name = repo_url.split(':')[-1]
        subprocess.run(["git","clone","--bare",repo_url,f"{self.repo_store_dir}/{project_name}"])

    def clone_repos(self):
        with open(self.repo_file,'r') as f:
            repos = f.readlines()
            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.clone_repo, repos)

    def get_projects_list(self):
        projects = self.gl.projects.list(iterator=True)
        count = 0 
        for project in projects:
            with open(self.repo_file, 'a') as f:
                f.write(project.ssh_url_to_repo + '\n')
            count += 1
        
    def is_dir_exist(self, repo_url):
        repo_url = repo_url.strip()
        project_name = repo_url.split(':')[-1]
        project_path = f"{self.repo_store_dir}/{project_name}"
        if not os.path.exists(project_path):
            print(repo_url)
        
    def diff_missing_project(self):
        with open(self.repo_file,'r') as f:
            repos = f.readlines()
            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.is_dir_exist, repos)

    def exec(self):
        # 获取project列表
        self.get_projects_list()

        # 克隆repos
        self.clone_repos()

        # 对比缺少克隆的repo
        self.diff_missing_project()



class MigrateGitlab(BaseGitlab):
    def __init__(self, url, token, repo_file, repo_store_dir, parent_group_id, parent_group_name) -> None:
        super().__init__(url, token, repo_file, repo_store_dir)
        self.git_repos = []
        self.parent_group_id = parent_group_id
        self.parent_group_name = parent_group_name
        self.gitlab_hostname = self.get_hostname(self.url)

    def get_hostname(self,url):
        parsed_url = urlparse(url)
        return parsed_url.hostname
    
    def find_git_repos(self):
        tmp_repos = []
        for dirpath, _, _ in os.walk(self.repo_store_dir):
            if dirpath.endswith(".git"):
                tmp_repos.append(dirpath[len(self.repo_store_dir)+1 :])
                continue
        self.git_repos = tmp_repos

    def create_subgroup_recursive(self):
        # 分割路径
        for subgroup_path in self.git_repo:
            subgroups = subgroup_path.split('/')[:-1]
            current_parent_id = self.parent_group_id

            for subgroup_name in subgroups:
                # 检查当前 subgroup 是否存在
                try:
                    subgroup = self.gl.groups.get(current_parent_id, include_subgroups=True)
                    found_subgroup = next((sg for sg in subgroup.subgroups.list(get_all=True) if sg.name == subgroup_name), None)

                    if found_subgroup:
                        current_parent_id = found_subgroup.id  # 更新父级 ID
                    else:
                        # 创建新的 subgroup
                        new_subgroup = self.gl.groups.create({'name': subgroup_name, 'path': subgroup_name, 'parent_id': current_parent_id})
                        current_parent_id = new_subgroup.id  # 更新父级 ID
                except Exception as e:
                    print(f"创建 subgroup {subgroup_name} 时出错: {e}")

    def push_repo(self, repo_url):
        wordir = f"./{self.repo_store_dir}/{repo_url}"
        print(f"Working directory: {wordir}")
        commands = [
            ["git","remote","rm","origin"],
            ["git", "remote", "add", "origin", f"git@{self.gitlab_hostname}:{self.parent_group_name}/{repo_url}"],
            ["git", "push", "--mirror", "origin"]
            ["git", "push", "--tags"]
        ]
        try:
            for command in commands:
                print(f"Executing command: {command}")
                result = subprocess.run(command, cwd=wordir, capture_output=True, text=True, check=True)
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Command '{e.cmd}' failed with exit code {e.returncode}. Output: {e.output}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print("Finished executing push_repo.")

    def push_repos(self):
        # for i in self.git_repos:
        #     self.push_repo(i)
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.push_repo, self.git_repos)


    def print(self):
        print(self.git_repos)
    def exec(self):
        # 获取待创建的repo列表
        self.find_git_repos()

