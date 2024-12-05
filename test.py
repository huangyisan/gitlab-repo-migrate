import os

def list_files_and_dirs(root_dir):
    for dirpath, _, _ in os.walk(root_dir):
        if dirpath.endswith(".git") :
            print(dirpath)
            continue  # 不再遍历 .git 目录
def main():
    root_directory = 'repo'  # 替换为要遍历的目录
    list_files_and_dirs(root_directory)

if __name__ == '__main__':
    main()