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


def test_owner_requirement(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	chain.sleep(arena.firstStageDuration())

	create_voting_position(voting, daiToken, accounts[2], 1, 10e18)
	
	# TODO: add error msg
	with brownie.reverts():
		voting.withdrawDaiFromVotingPosition(1, accounts[1], 10e18, _from(accounts[1]))


def test_multiplie_withdraw(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account0 = accounts[0]
	account1 = accounts[1]
	amount = 1e19
	amountMAX = 1e21

	assert arena.votingPositionsValues(1)["daiInvested"] == 100000000000000000000
	assert arena.votingPositionsValues(1)["endEpoch"] == 0
	assert arena.votingPositionsValues(1)["zooInvested"] == 100000000000000000000

	balanceZoo = zooToken.balanceOf(account0)# == 113749600000000000000000000
	balanceDai = daiToken.balanceOf(account0)# == 39999700000000000000000000

	assert arena.votingPositionsValues(4)["daiInvested"] == 100000000000000000000
	assert arena.votingPositionsValues(4)["endEpoch"] == 0
	assert arena.votingPositionsValues(4)["zooInvested"] == 100000000000000000000
	assert zooToken.balanceOf(account1) == 39999700000000000000000000

	# withdrawDaiFromVotingPosition(uint256 votingPositionId, address beneficiary, uint256 daiNumber) external onlyVotingOwner(votingPositionId)
	tx = voting.withdrawDaiFromVotingPosition(1, account0, amount, _from(account0))
	tx.events["WithdrawedDaiFromVoting"]

	tx1 = voting.withdrawDaiFromVotingPosition(4, account1, amountMAX, _from(account1))
	tx1.events["LiquidatedVotingPosition"]

	daiInvested = arena.votingPositionsValues(1)["daiInvested"]
	assert daiInvested == 90000000000000000000
	assert arena.votingPositionsValues(1)["endEpoch"] == 0
	assert arena.votingPositionsValues(1)["zooInvested"] == 90000000000000000000 # zoo withdraws
	assert zooToken.balanceOf(account0) == 119642610500000000000000000

	assert arena.votingPositionsValues(4)["daiInvested"] == 100000000000000000000 # liquidate doesn't reduce daiInvested
	assert arena.votingPositionsValues(4)["endEpoch"] == 2
	assert arena.votingPositionsValues(4)["zooInvested"] == 100000000000000000000 # liquidate doesn't reduce zooInvested
	assert zooToken.balanceOf(account1) == 39999799500000000000000000 # liquidate withdraws zoo.

	##
	tx2 = voting.withdrawDaiFromVotingPosition(1, account0, amountMAX, _from(account0))
	tx2.events["LiquidatedVotingPosition"]

	assert arena.votingPositionsValues(1)["daiInvested"] == 90000000000000000000 # liquidate doesn't reduce daiInvested
	assert arena.votingPositionsValues(1)["endEpoch"] == 2
	assert arena.votingPositionsValues(1)["zooInvested"] == 90000000000000000000 # liquidate doesn't reduce zooInvested
	assert zooToken.balanceOf(account0) == 119642700500000000000000000
	assert daiToken.balanceOf(account0) - (balanceDai + amount + daiInvested) < 1e18

def test_withdraw_votes_recompute(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account0 = accounts[0]
	account1 = accounts[1]
	amount = 30e18
	amountMAX = 1e21

	assert arena.votingPositionsValues(1)["daiInvested"] == 100000000000000000000
	assert arena.votingPositionsValues(1)["zooInvested"] == 100000000000000000000
	assert arena.votingPositionsValues(1)["daiVotes"] == 130000000000000000000
	assert arena.votingPositionsValues(1)["votes"] == 260000000000000000000


	assert arena.votingPositionsValues(10)["daiInvested"] == 100000000000000000000
	assert arena.votingPositionsValues(10)["zooInvested"] == 0
	assert arena.votingPositionsValues(10)["daiVotes"] == 70000000000000000000
	assert arena.votingPositionsValues(10)["votes"] == 70000000000000000000

	# withdrawDaiFromVotingPosition(uint256 votingPositionId, address beneficiary, uint256 daiNumber) external onlyVotingOwner(votingPositionId)
	tx = voting.withdrawDaiFromVotingPosition(1, account0, amount, _from(account0))
	tx.events["WithdrawedDaiFromVoting"]
	tx1 = voting.withdrawDaiFromVotingPosition(10, account0, amount, _from(account1))
	tx1.events["WithdrawedDaiFromVoting"]

	assert arena.votingPositionsValues(1)["daiInvested"] == 70000000000000000000
	assert arena.votingPositionsValues(1)["zooInvested"] == 70000000000000000000
	assert arena.votingPositionsValues(1)["daiVotes"] == 91000000000000000000 # saves 1.3 rate
	assert arena.votingPositionsValues(1)["votes"] == 182000000000000000000 # saves 1.3 rate for both dai and zoo.

	assert arena.votingPositionsValues(10)["daiInvested"] == 70000000000000000000
	assert arena.votingPositionsValues(10)["zooInvested"] == 0
	assert arena.votingPositionsValues(10)["daiVotes"] == 49000000000000000000 # saves 1.0 rate for dai.
	assert arena.votingPositionsValues(10)["votes"] == 49000000000000000000

	chain.sleep(arena.firstStageDuration())

	tx1 = arena.recomputeDaiVotes(10)
	tx1.events["RecomputedDaiVotes"]

	assert arena.votingPositionsValues(10)["daiInvested"] == 70000000000000000000
	assert arena.votingPositionsValues(10)["zooInvested"] == 0
	assert arena.votingPositionsValues(10)["daiVotes"] == 91000000000000000000 # recomputes to correct amount.
	assert arena.votingPositionsValues(10)["votes"] == 91000000000000000000

# tests for league #
def test_withdraw_league_change(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account1 = accounts[1]
	votingPositionId = 10
	stakingPositionId = 9

	daiApprove = 400000e18
	daiToken.approve(voting, daiApprove, _from(accounts[1])) # approve a lot.
	voting.addDaiToPosition(votingPositionId, 150000e18, _from(accounts[1]))

	# to golden
	voting.withdrawDaiFromVotingPosition(10, account1, 145000e18, _from(account1))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 7500e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 3

	# to silver
	voting.withdrawDaiFromVotingPosition(10, account1, 3400e18, _from(account1)) # overflow

	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 2500e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 2

	# wooden
	voting.withdrawDaiFromVotingPosition(10, account1, 10000e18, _from(account1)) # withdraw all and liquidate
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 500e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 0 # league 0

def test_withdraw_league_change_gold(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	account1 = accounts[1]
	votingPositionId = 10
	stakingPositionId = 9

	daiApprove = 400000e18
	daiToken.approve(voting, daiApprove, _from(accounts[1])) # approve a lot.
	voting.addDaiToPosition(votingPositionId, 150000e18, _from(accounts[1]))

	# from master to platinum
	voting.withdrawDaiFromVotingPosition(10, account1, 90000e18, _from(account1))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 150000e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 4

	# from master to platinem
	voting.withdrawDaiFromVotingPosition(10, account1, 40000e18, _from(account1))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 30000e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 4