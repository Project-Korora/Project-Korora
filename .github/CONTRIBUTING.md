# Project Kororā's Contributing Guidelines

## Contributing Code

We use Conventional Commits with ALL CAPS for merge commits.

### Format:
- **Fix**: A commit of the type `fix` patches a bug in the codebase.
- **Feat**: A commit of the type `feat` introduces a new feature to the codebase.
- **BREAKING CHANGE**: A commit that has a footer `BREAKING CHANGE:`, or appends a `!` after the type/scope, introduces a breaking API change.
    - A BREAKING CHANGE can be part of commits of any type.
- **Commit Types**: Types other than `fix:` and `feat:` are allowed:
    - `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others.
- **Merge Types**:
    - `API`, `BENCH`, `BLD`, `BUG`, `DEP`, `DEV`, `DOC`, `ENH`, `MAINT`, `MNT`, `REL`, `REV`, `STY`, `TST`, `TYP`, `WIP`
- **Scope**: A scope may be provided to a commit’s type, to provide additional contextual information and is contained within parentheses.
    - e.g., `feat(parser): add ability to parse arrays`.

## Setting Up the Project

Before you begin contributing, please make sure to set up the project environment:

1. **Download Miniconda** and install it by following the instructions for your platform [here](https://docs.conda.io/en/latest/miniconda.html).

2. **Initialize Conda**:
    After installing Miniconda, run:

    - For bash
    ```bash
    conda init
    ```

    - For fish
    ```fish
    conda init fish
    ```

    This will configure your shell for Conda, so it works properly with your environment.

3. **Create and activate the Conda environment**:
    From the root of the project, run:
    ```bash
    conda env create -f environment.yml
    conda activate Project-Korora
    ```
    Conda will automatically install all the necessary dependencies as specified in `environment.yml`.

### Running Pre-commit Hooks

After setting up your environment, **ensure to run the pre-commit hooks** to check your code style and ensure that everything is correctly formatted before you commit:

1. **Run the pre-commit hooks manually** to check your code:
    ```bash
    pre-commit run --all-files
    ```

This ensures that your code is linted and formatted according to the project's standards. If any issues are found, resolve them before committing your changes.

Thank you for contributing!
