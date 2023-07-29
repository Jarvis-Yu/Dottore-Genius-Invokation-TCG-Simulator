# Dev README

- [Dev README](#dev-readme)
  - [Setup Environment](#setup-environment)
    - [Setup Manually](#setup-manually)
    - [Setup By Running Script](#setup-by-running-script)
  - [Code Style](#code-style)
  - [Relative Files](#relative-files)

## Setup Environment

First make sure your Python version >= 3.10.

### Setup Manually

Create a `venv`, activate it and install packages in `requirements.txt`.

### Setup By Running Script

Run the code below in Shell or Terminal.

```
source ./scripts/sh/venv.sh
```

(If you use Powershell, then `./scripts/ps1/` contains corresponding `.ps1` scripts)

After `venv` is setup, you may run `./scripts/sh/cli.sh` and play a game to
see if the project is running correctly.
(or simply run `./scripts/sh/test.sh` to unittest the whole project)

## Code Style

Generally follow autopep8

- Line length limit is 100
- Use `snake_case` for methods, functions or variables
- Use `PascalCase` for class names
- Use `ALL_CAPITAL` for constants or enums
- Always type hint any functions/methods you wrote
- Commits naming should briefly describe what is done in the commit
  - e.g. `implements the card Starsigns` or `updates README on changes in root-level api`
  - don't give empty commits or commits merely stating which files are changed

## Relative Files

- [**Design Doc**](state_machine_design.md)
