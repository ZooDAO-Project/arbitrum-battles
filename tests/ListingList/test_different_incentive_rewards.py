import brownie
from brownie import *

def test_incentive_rewards_are_different(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


	result = voting.claimIncentiveVoterReward.call(1, accounts[-1], {"from": accounts[0]})

	assert result > 0
	"""
	while arena.currentEpoch() < arena.endEpochOfIncentiveRewards():
		chain.sleep(arena.epochDuration() + 1)
		chain.mine(1)
		arena.updateEpoch({"from": accounts[0]})
		current_epoch = arena.currentEpoch()
		
		# check correctness of results after update epoch
		vote_reward_list = []
		for i in range(3):
			for j in range(3):
				voting_position_id = 1 + j + i * 3
				reward = voting.claimIncentiveVoterReward.call(voting_position_id, accounts[-1], {"from": accounts[i]})
				vote = arena.votingPositionsValues(voting_position_id)["daiVotes"]
				vote_reward_list.append([vote, reward])

		vote_reward_list.pop()
		for i in range(len(vote_reward_list)):
			for j in range(len(vote_reward_list)):
				if i != j:
					if vote_reward_list[i][0] != vote_reward_list[j][0]:
						assert vote_reward_list[i][1] != vote_reward_list[j][1]

		mode = arena.currentEpoch() % 5
		duration = 0
		if mode == 0:
			duration = arena.firstStageDuration()
		elif mode == 1:
			duration = arena.firstStageDuration() + arena.secondStageDuration()
		elif mode == 2:
			duration = arena.firstStageDuration() + arena.secondStageDuration() + arena.thirdStageDuration()
		elif mode == 3:
			duration = arena.firstStageDuration() + arena.secondStageDuration() + arena.thirdStageDuration() + arena.fourthStageDuration()
		else:
			duration = 0

		chain.sleep(duration)
		chain.mine(1)

		# check that results are stage-independent
		vote_reward_list = []
		for i in range(3):
			for j in range(3):
				voting_position_id = 1 + j + i * 3
				reward = voting.claimIncentiveVoterReward.call(voting_position_id, accounts[-1], {"from": accounts[i]})
				vote = arena.votingPositionsValues(voting_position_id)["daiVotes"]
				vote_reward_list.append([vote, reward])

		vote_reward_list.pop()
		for i in range(len(vote_reward_list)):
			for j in range(len(vote_reward_list)):
				if i != j:
					if vote_reward_list[i][0] != vote_reward_list[j][0]:
						assert vote_reward_list[i][1] != vote_reward_list[j][1]
		
		# add stablecoins to voting position
		selected_voting_position = arena.currentEpoch() % 8 + 1
		info_about_position = arena.votingPositionsValues(selected_voting_position)
		owner_of_selected_position = voting.ownerOf(selected_voting_position)
		amount = info_about_position["daiVotes"] // 2
		if arena.getCurrentStage() != 2:
			voting.addDaiToPosition(selected_voting_position, amount, {"from": owner_of_selected_position})"""
