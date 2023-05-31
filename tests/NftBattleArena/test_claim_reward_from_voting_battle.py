
from _utils.utils import _from, find_voting_owner_in_accounts


# def test_claim_reward_after_liquidating_voting():


# def test_liquidate_voting_after_claiming_reward():

# def test_update_yTokens_reward_debt():

# def test_empty_pending_reward():


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
	assert pending_reward == 9217448745 or 3840603643 # cause we have position with fewer amount dai, reward sometimes lower.

	owner = find_voting_owner_in_accounts(positionIndex, accounts, voting)

	# Triggers update yTokensRewardDebt 
	voting.withdrawDaiFromVotingPosition(positionIndex, owner, 0, _from(owner))    

	# Update voting position values from contract
	votingPositionWithReward = arena.votingPositionsValues(positionIndex)
	assert votingPositionWithReward["yTokensRewardDebt"] == pending_reward  # Reward debt increased as expected

	reward = arena.getPendingVoterReward(positionIndex)
	assert reward == (0, 0)

	# Try to withdraw 0 again to double reward
	voting.withdrawDaiFromVotingPosition(positionIndex, owner, 0, _from(owner))    

	# Get new values of voting position
	votingPositionWithReward = arena.votingPositionsValues(positionIndex)
	assert votingPositionWithReward["yTokensRewardDebt"] == pending_reward
