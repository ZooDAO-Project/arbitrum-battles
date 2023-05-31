import brownie
from brownie import chain

#
# Utility functions
#
# has _ before name because from is internal reserved word
def _from(account):
	return {"from": account}


# tests for league #
def test_league_changes_correctly(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listingList) = battles

	bigAmount = 400000e18
	zooToken.approve(voting, bigAmount, _from(accounts[1])) # approve a lot.
	daiToken.approve(voting, bigAmount, _from(accounts[1])) # approve a lot.
	votingPositionId = 1 # note that we can add to anyone's position
	stakingPositionId = 1
	
	nft.approve(staking.address, 4, _from(accounts[1])) # account 1 have nft 4,5,6
	nft.approve(staking.address, 5, _from(accounts[1])) # account 1 have nft 4,5,6
	staking.stakeNft(nft.address, 4, _from(accounts[1])) # address, id, from. // position 1
	staking.stakeNft(nft.address, 5, _from(accounts[1])) # address, id, from. // position 2

	chain.sleep(arena.firstStageDuration()) # skip 1st(0) stage, now second stage(1)
	# stage 1, epoch 1 #

	voting.createNewVotingPosition(1, 5000e18, True, _from(accounts[1])) # stakingPositionId, value, from // position 1
	voting.createNewVotingPosition(2, 5000e18, True, _from(accounts[1])) # stakingPositionId, value, from // position 2

	chain.sleep(arena.secondStageDuration()) # skip 2nd(1) stage, now third stage(2)
	# stage 2, epoch 1 #

	tx = arena.pairNft(1, _from(accounts[1])) # pair for 1 position.

	assert arena.rewardsForEpoch(stakingPositionId, 1)["votes"] == 6500e18
	assert arena.rewardsForEpoch(stakingPositionId, 1)["league"] == 2

	chain.sleep(arena.thirdStageDuration()) # skip third stage, now fourth stage

	# from wooden to bronze
	voting.addZooToPosition(votingPositionId, 5000e18, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 1)["votes"] == 13000e18
	assert arena.rewardsForEpoch(stakingPositionId, 1)["league"] == 3