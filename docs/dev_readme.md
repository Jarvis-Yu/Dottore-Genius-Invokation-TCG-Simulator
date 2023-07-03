# Dev README

- [Dev README](#dev-readme)
  - [Run the Project Locally](#run-the-project-locally)
    - [For unix based systems (MacOS, Linux...): _(up-to-date)_](#for-unix-based-systems-macos-linux-up-to-date)
    - [For Windows based systems: _(out-dated now, needs contribution)_](#for-windows-based-systems-out-dated-now-needs-contribution)
  - [Where to Start Reading the Code](#where-to-start-reading-the-code)
  - [QA](#qa)

## Run the Project Locally

### For unix based systems (MacOS, Linux...): _(up-to-date)_

1. Clone the project
2. Make sure your Python version >= 3.10.11
3. Set up the environment with `venv` or otherwise
4. If you don't know how to setup `venv`, google it or run the following
   commands under the project directory

```sh
source ./scripts/venv.sh
```

5. With the environment set up, you may have a try with CLI by running:

```sh
./scripts/cli.sh
```

### For Windows based systems: _(out-dated now, needs contribution)_

Sorry the `.ps1` scripts last contributer wrote is not out-dated.

But given you use `wsl` or you are a Powershell user with some knowledge of
bash scripts, then have a read of the `.sh` scripts in `scripts/` to setup
the project.

## Where to Start Reading the Code

I suggest you start reading the code from `src/tests/test_game_state_machine.py`,
which contains tests for the whole game flow.

A read through other test files are also recommanded to get familiar with the state-machine design.

If you have trouble understanding the repo, please don't hesitate to raise an issue asking for help.
I may consider adding some design documentations to go over the game model structure of this project.

## QA

Do you want people to join you?

- Well, collaborators are warmly welcomed. If you have the intention to join, please contact me.

How to contact you?

- I assume you can find my email somewhere ~~(hint: `git log`)~~
