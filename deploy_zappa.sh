#!/bin/bash

set -ex

if [[ $1 == -f ]]; then
  remove_env="rm -rf docker_env &&"
elif [ $1 == -d ]; then
  update_deploy="deploy"
else
  remove_env=""
  update_deploy="update"
fi

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
      zappa $update_deploy dev
    "
}

main
