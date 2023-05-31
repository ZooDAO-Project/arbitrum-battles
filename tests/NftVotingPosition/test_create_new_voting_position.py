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


def test_creating_new_position(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	tx = create_voting_position(voting, daiToken, accounts[2], 1, 10e18)
	assert tx.status == 1


def test_dai_transfer(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	balance_before = daiToken.balanceOf(accounts[1], _from(accounts[1]))

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	vault_balance = daiToken.balanceOf(vault)

	daiAmountToVote = 10e18
	create_voting_position(voting, daiToken, accounts[2], 1, daiAmountToVote)

	assert daiToken.balanceOf(accounts[2], _from(accounts[2])) == balance_before - daiAmountToVote
	assert daiToken.balanceOf(vault, _from(accounts[2])) == vault_balance + daiAmountToVote


def test_insufficient_funds(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	# More than account have
	daiAmountToVote = 5e25
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	with brownie.reverts("Dai/insufficient-balance"):
		voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))


def test_nft_mint(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	create_voting_position(voting, daiToken, accounts[2], 1, 10e18)

	assert voting.balanceOf(accounts[2], _from(accounts[2])) == 1
	assert voting.ownerOf(1, _from(accounts[2])) == accounts[2]


def test_non_existing_staking_id(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	with brownie.reverts("E1"):
		voting.createNewVotingPosition(123, daiAmountToVote, True, _from(accounts[1]))


def test_unstaked_nft(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	staking.unstakeNft(1, _from(accounts[1]))

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))


	with brownie.reverts("E1"):
		voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))

# vote at any stage #

def test_revert_in_stage_3(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())
	# Waiting for third stage
	chain.sleep(arena.secondStageDuration())

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))


	with brownie.reverts("Wrong stage!"):
		voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))


def test_works_in_stage_1_4_5(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))
	voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))


	# Waiting for second stage
	chain.sleep(arena.firstStageDuration()) # skip 1 stage
	# Waiting for third stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage
	# Waiting for fourth stage
	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.

	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))
	voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1])) # vote again in stage 4

	# Waiting for fifth stage
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))
	voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1])) # vote again in stage 5


