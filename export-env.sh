#!/bin/sh

## Usage:
## . ./export-env.sh


# https://stackoverflow.com/a/30969768
set -o allexport
source .env
set +o allexport

