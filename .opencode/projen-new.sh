#!/usr/bin/env bash
set -euo pipefail
export NVM_DIR=/home/jacopo/.nvm
. /home/jacopo/.nvm/nvm.sh
export PATH=/home/jacopo/.local/bin:$PATH
cd /home/jacopo/aws-data-engineering-shenanigans
npx projen new awscdk-app-py \
  --from projen@0.104.17 \
  --name aws-data-engineering-shenanigans \
  --module-name aws_data_engineering_shenanigans \
  --uv \
  --author-name JacopoMalatesta \
  --author-email jacopomalatesta95@gmail.com
echo "--- exit: $? ---"
ls -la
