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
		# Using wrong
		voting.addZooToPosition(1, 10e18, _from(accounts[1]))


def test_zoo_transfer(accounts, tokens, battles, veBal):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(gauge, vebal) = veBal

	zoo_balance_before = zooToken.balanceOf(accounts[1], _from(accounts[1]))


	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	daiAmount = 10e18
	create_voting_position(voting, daiToken, accounts[2], 1, daiAmount)

	# Waiting for fourth position
	chain.sleep(arena.secondStageDuration())
	chain.sleep(arena.thirdStageDuration())

	zooAmount = 10e18

	zooToken.approve(voting, zooAmount, _from(accounts[2]))
	voting.addZooToPosition(1, zooAmount, _from(accounts[2]))

	assert zooToken.balanceOf(accounts[2], _from(accounts[2])) == zoo_balance_before - zooAmount
	assert zooToken.balanceOf(gauge, _from(accounts[2])) == zooAmount
