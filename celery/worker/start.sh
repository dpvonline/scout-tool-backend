#!/bin/sh

set -o errexit
set -o nounset

celery -A backend worker -l info
