# Projec Kororā's Contributing guidelines

## Contributing code

We use [Conventional Commits](https://www.conventionalcommits.org/) with **ALL CAPS** for merge commits.

**Format:**
- **Fix**: a commit of the type fix patches a bug in the codebase.
- **Feat**: a commit of the type feat introduces a new feature to the codebase.
- **BREAKING CHANGE**: a commit that has a footer BREAKING CHANGE:, or appends a ! after the type/scope, introduces a breaking API change.
    - A BREAKING CHANGE can be part of commits of any type.
- **Commit Types**: types other than fix: and feat: are allowed:
    - `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others.
- **Merge Types**: 
    - `API`, `BENCH`, `BLD`, `BUG`, `DEP`, `DEV`, `DOC`, `ENH`, `MAINT`, `MNT`, `REL`, `REV`, `STY`, `TST`, `TYP`, `WIP`
- **Scope** A scope may be provided to a commit’s type, to provide additional contextual information and is contained within parenthesis.
    - e.g., feat(parser): add ability to parse arrays.
