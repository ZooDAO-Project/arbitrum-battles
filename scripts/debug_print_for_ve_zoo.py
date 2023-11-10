from brownie import *

def main(arena, voting, ve_zoo):
	voting_position_ids = arena.numberOfVotingPositions()
	positions = range(1, voting_position_ids)
	voting_values = []
	current_rewards = []
	staking_values = []
	for i in positions:
		voting_value = arena.votingPositionsValues(i)
		voting_values.append(voting_value)
		reward = arena.calculateIncentiveRewardForVoter.call(i, {"from": voting})
		current_rewards.append(reward)
		staking_value = arena.stakingPositionsValues(voting_value["stakingPositionId"])
		staking_values.append(staking_value)
		print(i, "\t", reward, "\t", voting_value, "\t", staking_value, "\t", arena.voterIncentiveDebt(i))
