from brownie import chain
import math
import pytest

def _from(account):
	return {"from": account}

@pytest.mark.skip(reason="Need to fix recompute")
def test_multiplying_y_tokens_reward_debt_before_claim(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	votings = []

	votingPositionWithReward = 0
	positionIndex = 0

	# Find voting with reward
	for i in range(arena.numberOfVotingPositions()):
		if (arena.getPendingVoterReward(i, 1, 2) != 0):
			votingPositionWithReward = arena.votingPositionsValues(i)
			positionIndex = i

	stakingPositionId = votingPositionWithReward["stakingPositionId"]

	rewardsBefore = arena.rewardsForEpoch(stakingPositionId, 2)

	assert votingPositionWithReward["yTokensRewardDebt"] == 0

	owner = 0
	for account in accounts:
		if account.address == voting.ownerOf(positionIndex):
			owner = account

	reward = arena.getPendingVoterReward(positionIndex)
	assert reward == 1999798018 or reward == 99991900727033

	chain.sleep(arena.firstStageDuration())
	chain.sleep(math.ceil(arena.secondStageDuration() / 3 * 2) + 100)

	daiToken.approve(voting, 20e18, _from(owner))
	voting.addDaiToPosition(positionIndex, 20e18, _from(owner))

	chain.sleep(math.ceil(arena.secondStageDuration()))
	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())
	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	chain.sleep(arena.firstStageDuration())
	chain.sleep(math.ceil(arena.secondStageDuration() / 3 * 2))

	daiToken.approve(voting, 20e18, _from(owner))
	voting.addDaiToPosition(positionIndex, 20e18, _from(owner))

	chain.sleep(math.ceil(arena.secondStageDuration() / 3))

	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())
	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	chain.sleep(arena.firstStageDuration())

	arena.recomputeDaiVotes(positionIndex, _from(owner))

	# Update voting position values from contract
	votingPositionWithReward = arena.votingPositionsValues(positionIndex)
	assert votingPositionWithReward["yTokensRewardDebt"] == reward  # Reward debt increased as expected

	arena.recomputeDaiVotes(positionIndex, _from(owner))

	votingPositionWithReward = arena.votingPositionsValues(positionIndex)
	assert votingPositionWithReward["yTokensRewardDebt"] == reward  # Reward debt increased as expected


def test_recompute_votes(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]

	assert arena.votingPositionsValues(10)["daiInvested"] == 100000000000000000000
	assert arena.votingPositionsValues(10)["zooInvested"] == 0
	assert arena.votingPositionsValues(10)["daiVotes"] == 70000000000000000000
	assert arena.votingPositionsValues(10)["votes"] == 70000000000000000000

	chain.sleep(arena.firstStageDuration())

	tx1 = arena.recomputeDaiVotes(10)
	tx1.events["RecomputedDaiVotes"]

	assert arena.votingPositionsValues(10)["daiInvested"] == 100000000000000000000
	assert arena.votingPositionsValues(10)["zooInvested"] == 0
	assert arena.votingPositionsValues(10)["daiVotes"] == 130000000000000000000
	assert arena.votingPositionsValues(10)["votes"] == 130000000000000000000