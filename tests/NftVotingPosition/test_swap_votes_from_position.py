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

def test_multiplie_swaps(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account0 = accounts[0]
	account1 = accounts[1]

	swapAmount = 1e19
	initialAmount = 1e20

	assert arena.votingPositionsValues(1)["daiInvested"] == initialAmount
	assert arena.votingPositionsValues(1)["endEpoch"] == 0
	assert arena.votingPositionsValues(1)["zooInvested"] == initialAmount
	daiBalance = daiToken.balanceOf(account0)
	zoobalance = zooToken.balanceOf(account0)

	assert arena.votingPositionsValues(4)["daiInvested"] == initialAmount
	assert arena.votingPositionsValues(4)["endEpoch"] == 0
	assert arena.votingPositionsValues(4)["zooInvested"] == initialAmount
	assert daiToken.balanceOf(account1) == 39999600000000000000000000
	assert zooToken.balanceOf(account1) == 39999700000000000000000000

	assert arena.votingPositionsValues(2)["daiInvested"] == initialAmount

	# swapVotesFromPosition(uint256 voting_position_id, uint256 daiNumber, uint256 newStakingPositionId, address beneficiary, uint256 newVotingPosition)
	tx = voting.swapVotesFromPositionForOwner(1, swapAmount, 0, account0, 2, False, _from(account0)) # swap to voting position 2, should swap to existing, withdraw and add
	# tx.events["SwappedPositionVotes"]
	tx.events["WithdrawedDaiFromVoting"]
	tx.events["AddedDaiToVoting"]

	tx1 = voting.swapVotesFromPositionForOwner(4, swapAmount, 2, account1, 0, False, _from(account1)) # swap to staking position 2, should create new and withdraw
	# tx1.events["SwappedPositionVotes"]
	tx1.events["WithdrawedDaiFromVoting"]
	tx1.events["CreatedVotingPosition"] # mint 11 position.

	tx2 = voting.swapVotesFromPositionForOwner(5, initialAmount, 2, account1, 0, False, _from(account1)) # swap to staking position 2, should create new and liquidate
	# tx2.events["SwappedPositionVotes"]
	tx2.events["LiquidatedVotingPosition"]
	tx2.events["CreatedVotingPosition"] # mint 12 position.

	assert arena.votingPositionsValues(1)["daiInvested"] == (initialAmount - swapAmount)
	assert arena.votingPositionsValues(1)["endEpoch"] == 0
	assert arena.votingPositionsValues(1)["zooInvested"] == (initialAmount - swapAmount)
	assert daiToken.balanceOf(account0) == daiBalance
	assert zooToken.balanceOf(account0) == zoobalance + 10550000000000000000 # part of zoo were unstacked

	assert arena.votingPositionsValues(4)["daiInvested"] == (initialAmount - swapAmount) # dai withdrawed
	assert arena.votingPositionsValues(4)["endEpoch"] == 0
	assert arena.votingPositionsValues(4)["zooInvested"] == (initialAmount - swapAmount)

	assert arena.votingPositionsValues(5)["daiInvested"] == initialAmount # position liquidated with old values left for history.
	assert arena.votingPositionsValues(5)["endEpoch"] == 2
	assert arena.votingPositionsValues(5)["zooInvested"] == initialAmount
	assert daiToken.balanceOf(account1) == 39999600000000000000000000
	assert zooToken.balanceOf(account1) == 39999809450000000000000000

	assert arena.votingPositionsValues(2)["daiInvested"] == (initialAmount + swapAmount) # dai added

	assert tx1.events['CreatedVotingPosition']['votingPositionId'] == 11 # new minted position exists.
	assert arena.votingPositionsValues(11)["daiInvested"] == swapAmount  # new minted position got dai swapped.
	assert arena.votingPositionsValues(11)["zooInvested"] == 0

	assert tx2.events['CreatedVotingPosition']['votingPositionId'] == 12
	assert arena.votingPositionsValues(12)["daiInvested"] == initialAmount # new minted position got dai swapped.
	assert arena.votingPositionsValues(12)["zooInvested"] == 0


def test_nft_mint_on_swap_to_new_voting(finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]

	voting_position_id = 4
	owner = voting.ownerOf(voting_position_id)
	voting_position = arena.votingPositionsValues(voting_position_id)
	old_staking_position_id = voting_position['stakingPositionId']

	staking_positions_IDs = list(range(1, 10))
	staking_positions_IDs.remove(old_staking_position_id)

	new_staking_position_ID = choice(staking_positions_IDs)
	daiNumber = voting_position['daiInvested']

	balance = voting.balanceOf(owner) # record it for future assert

	new_voting_position_ID = 0 # 0 means that votingPosition doesn't exist and that it must be created
	tx = voting.swapVotesFromPositionForOwner(voting_position_id, daiNumber, new_staking_position_ID, owner, new_voting_position_ID, False, _from(owner))
	
	new_balance = voting.balanceOf(owner)
	# New NFT must be minted
	assert new_balance == balance + 1

	event = tx.events['CreatedVotingPosition']
	new_voting_position_ID = event['votingPositionId']
	dai_amount = event['daiAmount']

	tx = voting.withdrawDaiFromVotingPosition(new_voting_position_ID, owner, dai_amount, _from(owner))
	assert tx.status == 1
	
	
