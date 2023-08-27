from random import choice
import brownie
from brownie import chain

#
# Utility functions
#
# has _ before name because from is internal reserved word
def _from(account):
	return {"from": account}

def stake_nft(staking, account, nft, tokenId):
	nft.approve(staking.address, tokenId, _from(account))
	
	staking.stakeNft(nft.address, tokenId, _from(account))

def create_voting_position(voting, daiToken, account, stakingPositionId, daiAmount):
	daiToken.approve(voting, daiAmount, _from(account))

	return voting.createNewVotingPosition(stakingPositionId, daiAmount, True, _from(account))

# End of utility functions


def test_swap_for_unstaked_works(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account0 = accounts[0]
	account1 = accounts[1]

	swapAmount = 100e18

	staking.unstakeNft(1, _from(account0))

	tx = voting.swapVotesFromPositionForUnstackedNft(1, _from(account0)) # swap to voting position 2, should swap to existing, withdraw and add
	event = tx.events["CreatedVotingPosition"]
	tx.events["LiquidatedVotingPosition"]

	assert event["currentEpoch"] == arena.currentEpoch()
	assert event["voter"] == account0
	assert event["stakingPositionId"] != 1 # random
	assert event["daiAmount"] == swapAmount
	assert event["votes"] == swapAmount * 1.3
	assert event["votingPositionId"] == 11

def test_multiplie_swaps(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account0 = accounts[0]
	account1 = accounts[1]

	swapAmount = 100e18

	staking.unstakeNft(1, _from(account0))
	staking.unstakeNft(2, _from(account0))

	tx = voting.swapVotesFromPositionForUnstackedNft(1, _from(account0)) # swap to voting position 2, should swap to existing, withdraw and create
	event = tx.events["CreatedVotingPosition"]
	tx.events["LiquidatedVotingPosition"]

	assert event["currentEpoch"] == arena.currentEpoch()
	assert event["voter"] == account0
	assert event["stakingPositionId"] != 1 # random
	assert event["daiAmount"] == swapAmount
	assert event["votes"] == swapAmount * 1.3
	assert event["votingPositionId"] == 11

	tx1 = voting.swapVotesFromPositionForUnstackedNft(2, _from(account0)) # swap to voting position 2, should swap to existing, withdraw and create
	event1 = tx1.events["CreatedVotingPosition"]
	tx1.events["LiquidatedVotingPosition"]

	assert event1["currentEpoch"] == arena.currentEpoch()
	assert event1["voter"] == account0
	assert event1["stakingPositionId"] > 2 # random
	assert event1["daiAmount"] == swapAmount
	assert event1["votes"] == swapAmount * 1.3
	assert event1["votingPositionId"] == 12

	with brownie.reverts("E1"): # coz position liquidated, it reverts in withdrawDai as inactive position.
		tx2 = voting.swapVotesFromPositionForUnstackedNft(2, _from(account0)) # swap to voting position 2, should swap to existing, withdraw and create

def test_swap_for_staked_fails(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account0 = accounts[0]
	account1 = accounts[1]

	with brownie.reverts("Nft is not unstacked"):
		voting.swapVotesFromPositionForUnstackedNft(1, _from(account0))

def test_swap_for_zero_fails(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account0 = accounts[0]

	staking.unstakeNft(1, _from(account0))
	voting.withdrawDaiFromVotingPosition(1, account0, 1e20, _from(account0))

	with brownie.reverts("E1"): # coz position liquidated, it reverts in withdrawDai as inactive position.
		voting.swapVotesFromPositionForUnstackedNft(1, _from(account0))

def test_swap_with_no_staked_fails(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account0 = accounts[0]
	account1 = accounts[1]
	account2 = accounts[2]

	staking.unstakeNft(1, _from(account0))
	staking.unstakeNft(2, _from(account0))
	staking.unstakeNft(3, _from(account0))

	staking.unstakeNft(4, _from(account1))
	staking.unstakeNft(5, _from(account1))
	staking.unstakeNft(6, _from(account1))

	staking.unstakeNft(7, _from(account2))
	staking.unstakeNft(8, _from(account2))
	staking.unstakeNft(9, _from(account2))

	with brownie.reverts("There is no opponent for Nft"):
		voting.swapVotesFromPositionForUnstackedNft(1, _from(account0))