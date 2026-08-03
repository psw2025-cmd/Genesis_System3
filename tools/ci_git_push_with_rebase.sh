#!/usr/bin/env bash
# Retry git push with rebase to survive concurrent [skip ci] bot commits.
set -euo pipefail
BRANCH="${1:-main}"
REMOTE="${2:-origin}"
MAX_ATTEMPTS="${CI_GIT_PUSH_ATTEMPTS:-8}"

git fetch "$REMOTE" "$BRANCH" || true
for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  if git push "$REMOTE" "HEAD:${BRANCH}"; then
    echo "ci_git_push=PASS attempt=${attempt}"
    exit 0
  fi
  echo "ci_git_push=RETRY attempt=${attempt}"
  git pull --rebase "$REMOTE" "$BRANCH" || git rebase --abort || true
  sleep $((attempt))
done
echo "ci_git_push=FAIL after ${MAX_ATTEMPTS} attempts"
exit 1
