import brownie
from brownie import chain

#
# Utility functions
#
# has _ before name because from is internal reserved word
def _from(account):
	return {"from": account}


# tests for league #
def test_rebalance_votes(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listingList) = battles

	bigAmount = 400000e18
	zooToken.approve(voting, bigAmount, _from(accounts[2])) # approve a lot.
	daiToken.approve(voting, bigAmount, _from(accounts[2])) # approve a lot.
	votingPositionId = 1 # note that we can add to anyone's position
	stakingPositionId = 1
	
	# accounts[1] - owner of NFt's
	# accounts[2] - voter
	# accounts[3] - some guy

	# stage 1, epoch 1 #
	nft.approve(staking.address, 4, _from(accounts[1])) # account 1 have nft 4,5,6
	nft.approve(staking.address, 5, _from(accounts[1])) # account 1 have nft 4,5,6
	nft.approve(staking.address, 6, _from(accounts[1])) # account 1 have nft 4,5,6
	staking.stakeNft(nft.address, 4, _from(accounts[1])) # address, id, from. // position 1
	staking.stakeNft(nft.address, 5, _from(accounts[1])) # address, id, from. // position 2
	staking.stakeNft(nft.address, 6, _from(accounts[1])) # address, id, from. // position 3

	voting.createNewVotingPosition(1, 5000e18, True, _from(accounts[2])) # stakingPositionId, value, from // voting position 1
	voting.createNewVotingPosition(2, 5000e18, False, _from(accounts[2])) # stakingPositionId, value, from // voting position 2
	voting.createNewVotingPosition(3, 5000e18, False, _from(accounts[2])) # stakingPositionId, value, from // voting position 3

	staking.unstakeNft(1, _from(accounts[1])) # unstake nft in 1 stage for account1
	staking.unstakeNft(2, _from(accounts[1])) # unstake nft in 1 stage for account1

	# (uint256 votingPositionId, uint256 daiNumber)
	voting.swapVotesFromPositionForUnstackedNft(1, _from(accounts[3]))  # unstake nft in 1 stage for account1

	with brownie.reverts("Owner of voting position didn't allow to swap votes"):
		voting.swapVotesFromPositionForUnstackedNft(2, _from(accounts[3])) 
