import brownie
from brownie import chain

#
# Utility functions
#
# has _ before name because from is internal reserved word
def _from(account):
	return {"from": account}


# tests for league #
def test_league_updates_from_previous_epochs(accounts, fourth_stage):
	(zooToken, daiToken, linkToken, nft) = fourth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fourth_stage[1]

	daiApprove = 400000e18
	daiToken.approve(voting, daiApprove, _from(accounts[1])) # approve a lot.
	stakingPositionId = 1
	stakingPositionId1 = 2
	stakingPositionId2 = 3

	# note that position already have 130 votes.
	assert arena.rewardsForEpoch(stakingPositionId, 1)["votes"] == 130000000000000000000 # votes epoch 1 before
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] == 0 # votes epoch 2 before

	# since this vote in fourth stage, votes come to next epoch.
	# wooden
	voting.createNewVotingPosition(stakingPositionId, 370e18, True, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 1)["votes"] == 130000000000000000000 # same
	# note that votes from previous epochs will be updated only in next epoch.
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] == 481e18 # 370 * 1.3
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 0 # league 0

	# platinum
	voting.createNewVotingPosition(stakingPositionId1, 100000e18, True, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId1, 2)["votes"] == 130000e18
	assert arena.rewardsForEpoch(stakingPositionId1, 2)["league"] == 4
	# master
	voting.createNewVotingPosition(stakingPositionId2, 150000e18, True, _from(accounts[1])) # we up to limit of 150k so almost any amount.
	assert arena.rewardsForEpoch(stakingPositionId2, 2)["votes"] > 150000e18
	assert arena.rewardsForEpoch(stakingPositionId2, 2)["league"] == 5

	# skip this and next epoch.
	chain.sleep(arena.fourthStageDuration() * 5)
	arena.updateEpoch() # now 2nd epoch.
	chain.sleep(arena.fourthStageDuration() * 5)
	arena.updateEpoch() # now 3rd epoch.
	chain.sleep(arena.fourthStageDuration() * 5)
	arena.updateEpoch() # now 4th epoch.

	arena.updateInfo(stakingPositionId)
	arena.updateInfo(stakingPositionId1)
	arena.updateInfo(stakingPositionId2)

	# wooden
	assert arena.rewardsForEpoch(stakingPositionId, 4)["votes"] == 611e18 # 481e18 + 130e18, cause old votes updated.
	assert arena.rewardsForEpoch(stakingPositionId, 4)["league"] == 1 # should update league.
	# platinum
	assert arena.rewardsForEpoch(stakingPositionId1, 4)["votes"] == 130130e18
	assert arena.rewardsForEpoch(stakingPositionId1, 4)["league"] == 4 # should update league.
	# master
	assert arena.rewardsForEpoch(stakingPositionId2, 4)["votes"] > 150130e18
	assert arena.rewardsForEpoch(stakingPositionId2, 4)["league"] == 5 # should update league.