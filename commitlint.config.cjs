/**
 * Commitlint - enforce Conventional Commits.
 * Install: npm install -D @commitlint/cli @commitlint/config-conventional
 * Hook: npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
 */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'perf', 'ci', 'build', 'revert']
    ],
    'type-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'header-max-length': [2, 'always', 100]
  }
};
