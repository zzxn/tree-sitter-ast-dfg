This code is modified from https://github.com/microsoft/CodeBERT

Some bugs is fixed:
- To use Point of tree-sitter, each line should be `bytes` instead of `str`.
- The two lists followed by `'comesFrom'` or `'computedFrom'` sometimes are not equal-sized.
