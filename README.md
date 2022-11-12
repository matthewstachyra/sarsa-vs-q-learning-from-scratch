# From scratch - SARSA vs Q-Learning for Novelty in Gridworld

Below is a gridworld that has a shortcut. The left version has the shortcut closed; the right version has the shortcut open. SARSA is tested against Q-Learning with different learning rates to see which adapts best - i.e., identifies the more optimal path and doesn't diverge after converging.

The `s` character represents any via start position; the `f` character represents any viable finish position; `1` represents a valid part of the grid world that the agent can move to while `0` represents an invalid part of the grid world, or what is out of bounds.
	
![Alt text](/exp_grid.png)

This repo uses pipenv but all that's required is `numpy` to get this running.

`python main` or `pipenv shell` followed by `pipenv run python main`.
