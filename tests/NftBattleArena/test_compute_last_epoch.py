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


def test_inactive_staking_and_inactive_voting(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)

	chain.sleep(arena.firstStageDuration())

	create_voting_position(voting, daiToken, accounts[2], 1, 10e18)
	create_voting_position(voting, daiToken, accounts[2], 2, 10e18)

	additionalDai = 10e18

	# TODO: add error msg
	with brownie.reverts():
		voting.addDaiToPosition(1, additionalDai, _from(accounts[1]))


def test_inactive_staking_and_active_voting(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	chain.sleep(arena.firstStageDuration())

	create_voting_position(voting, daiToken, accounts[2], 1, 10e18)

	additionalDai = 10e18

	# TODO: add error msg
	with brownie.reverts():
		voting.addDaiToPosition(1, additionalDai, _from(accounts[1]))


def test_active_staking_and_inactive_voting(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	chain.sleep(arena.firstStageDuration())

	create_voting_position(voting, daiToken, accounts[2], 1, 10e18)

	additionalDai = 10e18

	# TODO: add error msg
	with brownie.reverts():
		voting.addDaiToPosition(1, additionalDai, _from(accounts[1]))


def test_active_staking_and_active_voting(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	chain.sleep(arena.firstStageDuration())

	create_voting_position(voting, daiToken, accounts[2], 1, 10e18)

	additionalDai = 10e18

	# TODO: add error msg
	with brownie.reverts():
		voting.addDaiToPosition(1, additionalDai, _from(accounts[1]))