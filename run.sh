#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

cd $DIR
docker run -ti --network=host -v $PWD/data:/data poseidon:0.0.1
