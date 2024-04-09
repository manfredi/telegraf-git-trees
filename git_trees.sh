#!/usr/bin/env bash
set -e

function usage() {
    printf "Usage: %s -o owner -r repo -p path -t type -m measurement [-b branch] \n" "$(basename $0)"
}

function git_trees() {
    local pwd=$(pwd)
    local temp=$(mktemp -d)
    cd $temp
    git clone --depth 1 -b $branch https://github.com/${owner}/${repo}.git &>/dev/null
    cd $repo
    count=$(find $path -type f -name "*.$type" | wc -l)
    cd $pwd
    rm -rf $temp
    echo "${measurement},owner=${owner},repo=${repo},branch=${branch},path=${path},type=${type} count=${count}i"
}

while getopts :o:r:p:t:m:b: name
do
    case $name in
        o) owner="$OPTARG";;
        r) repo="$OPTARG";;
        p) path="$OPTARG";;
        t) type="$OPTARG";;
        m) measurement="$OPTARG";;
        b) branch="$OPTARG";;
        ?) usage; exit 1;;
    esac
done

if [[ -z "$owner" || -z "$repo" || -z  "$path" || -z  "$type" || -z "$measurement" ]]; then
    usage; exit 1;
fi

branch="${branch:-master}"

git_trees
