#!/bin/bash

set -ex

remove_env=""
update_deploy="update"
stage="dev"

while getopts ":fds:" arg; do
  case $arg in
    f ) remove_env="rm -rf docker_env &&";;
    d ) update_deploy="deploy";;
    s ) stage=${OPTARG};;
    * ) exit 0;;
  esac
done

main () {
  docker run -ti \
    -e AWS_SECRET_ACCESS_KEY \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_DEFAULT_REGION \
    -v $(pwd):/var/ask-auth --rm zappa \
    bash -c " \
      $remove_env \
      virtualenv docker_env && \
      source docker_env/bin/activate && \
      cd /var/ask-auth/ && \
      pip install -r requirements.txt && \
      zappa $update_deploy $stage
    "
}

main
