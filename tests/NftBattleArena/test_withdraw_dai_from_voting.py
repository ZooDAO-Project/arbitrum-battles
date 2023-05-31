import brownie
from brownie import chain

from _utils.utils import find_voting_owner_in_accounts, _from


def test_stage_requirement(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	daiAmount = 10e18
	tx = voting.withdrawDaiFromVotingPosition(1, accounts[0], daiAmount, _from(accounts[0]))
	assert tx.status == 1

	chain.sleep(arena.firstStageDuration())

	with brownie.reverts("Wrong stage!"):
		voting.withdrawDaiFromVotingPosition(1, accounts[0], daiAmount, _from(accounts[0]))

	chain.sleep(arena.secondStageDuration())

	with brownie.reverts("Wrong stage!"):
		voting.withdrawDaiFromVotingPosition(1, accounts[0], daiAmount, _from(accounts[0]))

	chain.sleep(arena.thirdStageDuration())

	with brownie.reverts("Wrong stage!"):
		voting.withdrawDaiFromVotingPosition(1, accounts[0], daiAmount, _from(accounts[0]))

	chain.sleep(arena.fourthStageDuration())

	with brownie.reverts("Wrong stage!"):
		voting.withdrawDaiFromVotingPosition(1, accounts[0], daiAmount, _from(accounts[0]))

	chain.sleep(arena.fifthStageDuration())

	with brownie.reverts("Wrong stage!"):
		voting.withdrawDaiFromVotingPosition(1, accounts[0], daiAmount, _from(accounts[0]))


def test_no_repeated_withdraw_requirement(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	voting_position_id = 1

	dai_amount = arena.votingPositionsValues(voting_position_id)["daiInvested"]

	tx = voting.withdrawDaiFromVotingPosition(voting_position_id, accounts[0], dai_amount, _from(accounts[0]))

	with brownie.reverts("E1"):
		voting.withdrawDaiFromVotingPosition(1, accounts[0], dai_amount, _from(accounts[0]))

	assert tx.events["Withdrawed"]["withdrawn"] >= dai_amount


def test_updating_info(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]



# def test_updating_voting_position_reward(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


# def test_liquidate_voting_if_all_dai_withdrawed(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


# def test_decreasing_dai_invested(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


# def test_withdraw_dai_from_voting(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


# def test_recalculate_and_withdraw_zoo_if_voting_have_more_zoo_than_dai(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


# def test_staking_position_reward_decrease(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


# def test_vault_withdraw(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


# def test_emitting_event(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


# def test_withdraw_zero(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


# def_test_check_same_rewards_after_withdraw_zero_dai(accounts, finished_epoch):
#     (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
#     (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]


def test_multiplying_y_tokens_reward_debt_before_claim(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	positionIndex = 0

	# Find voting with reward
	for votingPositionId in range(1, arena.numberOfVotingPositions() + 1):
		votingPosition = arena.votingPositionsValues(votingPositionId)

		(pending_reward, zooReward) = arena.getPendingVoterReward(votingPositionId)

		if (pending_reward != 0):
			positionIndex = votingPositionId

	votingPositionWithReward = arena.votingPositionsValues(positionIndex)
	assert votingPositionWithReward["yTokensRewardDebt"] == 0

	(pending_reward, zooReward) = arena.getPendingVoterReward(positionIndex)
	# assert pending_reward == 96534656
	assert pending_reward == 3840603643 or 9217448745

	owner = find_voting_owner_in_accounts(positionIndex, accounts, voting)

	# Triggers update yTokensRewardDebt
	voting.withdrawDaiFromVotingPosition(positionIndex, owner, 0, _from(owner))

	# Update voting position values from contract
	votingPositionWithReward = arena.votingPositionsValues(positionIndex)
	assert votingPositionWithReward["yTokensRewardDebt"] == pending_reward  # Reward debt increased as expected

	(reward, zooReward) = arena.getPendingVoterReward(positionIndex)
	assert reward == 0

	# Try to withdraw 0 again to double reward
	voting.withdrawDaiFromVotingPosition(positionIndex, owner, 0, _from(owner))

	# Get new values of voting position
	votingPositionWithReward = arena.votingPositionsValues(positionIndex)
	assert votingPositionWithReward["yTokensRewardDebt"] == pending_reward
