import os
from src.gitlab_handler.gitlab_class import CurrentGItlab,MigrateGitlab

def main():
    current_gitlab_url = os.getenv("GITLAB_URL", "")
    current_gitlab_token = os.getenv("GITLAB_TOKEN")

    migrate_gitlab_url = os.getenv("MG_GITLAB_URL","")
    migrate_gitlab_token = os.getenv("MG_GITLAB_TOKEN")

    repo_file = "repo.txt"
    repo_store_dir = "repo"

    # 迁移后的gitlab，存放repo的group id
    parent_group_id = "98"
    parent_group_name = "migrate"



    '''
    # 初始化老的gitlab，并且拉取全量代码
    CG = CurrentGItlab(current_gitlab_url, current_gitlab_token, repo_file, repo_store_dir)
    CG.Gen_Gitlab()
    # 执行拉取老gitlab全量代码库
    CG.exec()
    '''

    # 初始化新的gitlab，并且将代码都推送上去。
    MG = MigrateGitlab(migrate_gitlab_url, migrate_gitlab_token, repo_file, repo_store_dir, parent_group_id, parent_group_name)
    MG.Gen_Gitlab()
    # 生成待推送的repo数组
    MG.find_git_repos()
    # 先创建subgroup
    # MG.create_subgroup_recursive()
    # print
    # MG.print()
    # 推送repo
    MG.push_repos()

main()