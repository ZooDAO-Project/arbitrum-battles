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

	additionalDai = 10e18

	# TODO: add error msg
	with brownie.reverts():
		voting.addDaiToPosition(1, additionalDai, _from(accounts[1]))


def test_dai_transfer(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	balance_before = daiToken.balanceOf(accounts[1], _from(accounts[1]))

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	vault_balance = daiToken.balanceOf(vault)

	daiAmount = 10e18
	create_voting_position(voting, daiToken, accounts[2], 1, daiAmount)


	# Second approve and transfer of DAI
	additionalDai = 20e18
	daiToken.approve(voting, additionalDai, _from(accounts[2]))
	voting.addDaiToPosition(1, additionalDai, _from(accounts[2]))

	assert daiToken.balanceOf(accounts[2], _from(accounts[2])) == balance_before - daiAmount - additionalDai
	assert daiToken.balanceOf(vault, _from(accounts[2])) == vault_balance + daiAmount + additionalDai


# vote at any stage #

def test_revert_in_stage_3(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())
	# Waiting for third stage
	chain.sleep(arena.secondStageDuration())

	additionalDai = 20e18
	daiToken.approve(voting, additionalDai, _from(accounts[2]))

	with brownie.reverts("Wrong stage!"):
		voting.addDaiToPosition(1, additionalDai, _from(accounts[2]))


def test_works_in_stage_1_4_5(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))
	voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))

	# Second approve and transfer of DAI
	additionalDai = 20e18
	daiToken.approve(voting, additionalDai, _from(accounts[2]))
	voting.addDaiToPosition(1, additionalDai, _from(accounts[2])) # 1 stage

	assert arena.votingPositionsValues(1)[1] == 30000000000000000000
	assert arena.pendingVotesEpoch(1) == 0
	assert arena.pendingVotes(1) == 0
	assert arena.rewardsForEpoch(1,1)[1] == 39000000000000000000 # current epoch
	assert arena.rewardsForEpoch(1,2)[1] == 0 # next epoch

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration()) # skip 1 stage
	# Waiting for third stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage
	# Waiting for fourth stage
	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.

	daiToken.approve(voting, additionalDai, _from(accounts[2]))
	voting.addDaiToPosition(1, additionalDai, _from(accounts[2])) # 4 stage

	assert arena.votingPositionsValues(1)[1] == 50000000000000000000
	assert arena.pendingVotesEpoch(1) == 1
	assert arena.pendingVotes(1) == 26000000000000000000
	assert arena.rewardsForEpoch(1,1)[1] == 39000000000000000000 # current epoch
	assert arena.rewardsForEpoch(1,2)[1] == 26000000000000000000 # next epoch

	# Waiting for fifth stage
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	daiToken.approve(voting, additionalDai, _from(accounts[2]))
	voting.addDaiToPosition(1, additionalDai, _from(accounts[2])) # 5 stage

	assert arena.votingPositionsValues(1)[1] == 70000000000000000000
	assert arena.pendingVotesEpoch(1) == 1
	assert arena.pendingVotes(1) == 52000000000000000000 # pending votes adds correct
	assert arena.rewardsForEpoch(1,1)[1] == 39000000000000000000 # current epoch
	assert arena.rewardsForEpoch(1,2)[1] == 52000000000000000000 # next epoch

