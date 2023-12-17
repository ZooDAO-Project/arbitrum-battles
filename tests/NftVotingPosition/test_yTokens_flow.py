import brownie
from brownie import chain
import pytest

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


@pytest.mark.parametrize("daiNumber,daiAmountToVote2", [(100000e18, 100000e18), (100001e18, 100000e18), (100000e18, 399e18), (100001e18, 399e18)])
def test_workflow(accounts, tokens, battles, daiNumber, daiAmountToVote2):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	assert arena.currentEpoch() == 1

	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)

	daiAmountToVote1 = 10**18
	daiToken.approve(voting, daiAmountToVote1, _from(accounts[1]))
	voting.createNewVotingPosition(1, daiAmountToVote1, True, _from(accounts[1]))

	initial = daiToken.balanceOf(accounts[1])

	daiToken.approve(voting, daiAmountToVote2, _from(accounts[2]))
	voting.createNewVotingPosition(2, daiAmountToVote2, True, _from(accounts[2]))

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration()) # skip 1 stage
	# Waiting for third stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage

	arena.pairNft(1)

	# Waiting for fourth stage
	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.
	# Waiting for fifth stage
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	arena.requestRandom()
	vault.increaseMockBalance()
	tx0 = arena.chooseWinnerInPair(0)

	chain.sleep(arena.fifthStageDuration()) # skip 5 stage.

	arena.updateEpoch()

	assert arena.currentEpoch() == 2
	
	# Move to second epoch

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration() + 1) # skip 1 stage

	# Waiting for third stage
	chain.sleep(arena.secondStageDuration() + 1) # skip 2 stage

	arena.pairNft(1)

	# Waiting for fourth stage
	chain.sleep(arena.thirdStageDuration() + 1) # skip 3 stage.

	assert arena.getCurrentStage() == 2
	additionalDai = 100000e18
	daiToken.approve(voting, additionalDai, _from(accounts[1]))
	voting.addDaiToPosition(1, additionalDai, _from(accounts[1]))

	# Waiting for fifth stage
	chain.sleep(arena.fourthStageDuration() + 1) # skip 4 stage.

	arena.requestRandom()
	vault.increaseMockBalance()
	tx1 = arena.chooseWinnerInPair(0)

	chain.sleep(arena.fifthStageDuration()) # skip 5 stage.

	arena.updateEpoch()

	# Move to third epoch

	assert arena.currentEpoch() == 3

	print(tx0.events["ChosenWinner"])
	print(tx1.events["ChosenWinner"])

	pending_y_tokens = arena.pendingYTokens(1)
	shares = arena.tokensToShares.call(daiNumber)
	assert vault.balanceOf(arena) > shares # Check that balance of arena enough
	assert arena.rewardsForEpoch(1, arena.currentEpoch())["yTokens"] >= shares
	assert arena.votingPositionsValues(1)["yTokensNumber"] + pending_y_tokens >= shares

	deltaVotes = arena.votingPositionsValues(1)["daiVotes"] * daiNumber // arena.votingPositionsValues(1)["daiInvested"]
	assert arena.votingPositionsValues(1)["votes"] >= deltaVotes
	assert arena.votingPositionsValues(1)["daiVotes"] >= deltaVotes
	assert arena.rewardsForEpoch(1, arena.currentEpoch())["votes"] >= deltaVotes

	tx2 = voting.withdrawDaiFromVotingPosition(1, accounts[1], daiNumber, _from(accounts[1])) # overflow

	after = daiToken.balanceOf(accounts[1])

	eps = 10**9 # redeem eps of out mock
	assert after + 10**9 >= initial

