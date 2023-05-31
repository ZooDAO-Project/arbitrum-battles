import brownie
from brownie import chain

# Utility functions
#
# has _ before name because from is internal reserved word
def _from(account):
	return {"from": account}


def test_add_dai_to_voting_for_same_position_in_second_epoch(finished_epoch, accounts):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	chain.sleep(arena.firstStageDuration())

	voting_position_id = 1

	dai_amount = 50 * 10 ** 18

	tx = voting.addDaiToPosition(voting_position_id, dai_amount, {"from": accounts[0]})


# tests for league #
def test_league_sets_correctly(accounts, fourth_stage):
	(zooToken, daiToken, linkToken, nft) = fourth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fourth_stage[1]

	daiApprove = 400000e18
	daiToken.approve(voting, daiApprove, _from(accounts[1])) # approve a lot.
	votingPositionId = 1 # note that we can add to anyone's position
	stakingPositionId = 1

	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] == 260000000000000000000 # already have some votes.

	# since this vote in fourth stage, votes come to next epoch.
	# wooden
	voting.addDaiToPosition(votingPositionId, 180e18, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 500e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 0 # league 0
	# bronze
	voting.addDaiToPosition(votingPositionId, 1453e18, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 2500e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 1 
	# silver
	voting.addDaiToPosition(votingPositionId, 3746e18, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 7500e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 2
	# golden
	voting.addDaiToPosition(votingPositionId, 16307e18, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 30000e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 3
	# platinum
	voting.addDaiToPosition(votingPositionId, 91307e18, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 150000e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 4
	# master
	voting.addDaiToPosition(votingPositionId, 3000e18, _from(accounts[1])) # we up to limit of 150k so almost any amount.
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] > 150000e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 5