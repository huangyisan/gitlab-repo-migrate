#!/bin/bash
workdir=$(pwd)
repo_list=()

for r in "${repo_list[@]}"
    do
cd repo/${r} && git push --tags && cd ${workdir}
done
