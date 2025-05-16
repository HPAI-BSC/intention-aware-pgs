# Policy graphs and Intention
Supplementary material and code for Policy graphs and Intention, submitted to AAMAS 25'.

Included in it is a code for reproducing paper results, as well as more experimental results for other layouts, more 
analysed trajectories, etc.

## Setup
For basic reproduction of results, installation requires a pip install of requirements. Instructions for MAC below.

Two auxiliary codes (extract_trajectories, generate_pgs) are included to illustrate how those two artefacts are
generated, but require further requirements than those in requirements.txt ; and are not necessary to reproduce
paper results

## Paper reproduction and experiments

`src/eval/reproduce.py` contains the code for reproducing all experiments in the paper in order. Run from root-level
working directory (not src).

In addition to reproducing results, the setup allows to test in 3 more layouts:

![layouts](docs/assets/layouts.png)
From left to right: simple, random1, random3, unident_s, and random0. Only simple and random0 are used in the
paper due to space constraints exclusively.

When analysing results, we remark that unident_s for the HPPO agent does NOT work.

### Agent internal naming

Agents in this repository are referenced in the following manner:
HPPO:D14
PPO1:D24
HAg: D34
PPO2:D44
RAg: DR4

## Mac install

```bash
brew install graphviz
pip install --no-cache-dir --use-pep517 \ 
  --config-settings="--global-option=build_ext" \
  --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
  --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
  pygraphviz
```