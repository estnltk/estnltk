#!/usr/bin/env bash



export GIT_DESCRIBE_NUMBER=$TRAVIS_BUILD_NUMBER
export GIT_BUILD_STR=$TRAVIS_COMMIT
export PYTHON_TARGET=3.5

export PATH="$HOME/miniconda/bin:$PATH"

travis-build-scripts/install.sh
travis-build-scripts/script.sh
travis-build-scripts/after_success.sh
deploy.sh
