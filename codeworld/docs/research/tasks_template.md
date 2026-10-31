# Task templates (write concrete versions per repository, with gold answers)

1. **Locate** - "Which file/function validates <X>?" (gold: path + symbol)
2. **Callers** - "List every function that calls <Y>." (gold: set; score by F1)
3. **Flow** - "What happens, step by step, when <endpoint/CLI command> is executed? Name the main functions in order."
4. **Impact** - "If you change the signature of <Z>, which modules and tests are affected?" (gold from graph + manual check)
5. **Test selection** - "Which existing tests exercise <W>? Is anything untested?"
6. **Review** - "This diff was written by an AI assistant. Find the problems." (seed 2-3 defects: invented import, duplicated helper, layer violation)
