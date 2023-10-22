This is a great template README.


## General actions

-   rename the `modulename` folder
-   Ctrl+Shift+F -> replace `modulename` with the actual module name
-   Ctrl+Shift+F -> replace `username` with your user/org name
-   Ctrl+Shift+F -> replace `lord` with your default branch name (or not, `lord` is nice)

## GitHub Actions workflows

-   `publish.yml` publishes a new release for every version bump in `pyproject.toml` (check out `poetry version`)
    -   ***Add PYPI_TOKEN variable to repository settings*** to publish package on PyPI, otherwise you will get an error (or just remove the `Publish on PyPI` step)
    -   GitHub releases are created automatically, but you need to ***give the workflow write permissions (Settings / Actions / General / Workflow Permissions)***
-   `test.yml` runs several checks on PR and on push to main branch
    -   `Check Types` job runs mypy against the module code
        -   You may want to remove `--disallow-any-expr` if you don't want errors on `Any`
    -   `Run Tests` runs tests from `test` on several Python versions folder and pushes the coverage data to Coveralls
        -   You may want to write the actual tests
        -   If you don't want Coveralls integration, just remove the `Coveralls Update` step altogether. Otherwise, ***check out https://docs.coveralls.io/index*** to set up the integration.
        -   Check `python-version` matrix and edit if you want a different version list

## Stub module folder

- Includes an empty `__init__.py` (wow!)
- Includes an empty `py.typed` file so that typecheckers treat your package as typed ([see PEP 561](https://peps.python.org/pep-0561/#packaging-type-information))
- ***You may want to write actual code***

## `.gitignore` file

Taken from [here](https://github.com/github/gitignore/blob/main/Python.gitignore), with `poetry.lock` added (***consider removing that line if your package is not a library***)

## Simple `CONTRIBUTING.md` file

Just a bunch of recommendations for people contributing to your repository (if there are any)

## `pyproject.toml` file

- Includes several dev dependencies (used in workflows)
- ***Be sure to edit the license, author, links and other information as needed***

## `LICENSE` file:

***Be sure to replace it if needed***