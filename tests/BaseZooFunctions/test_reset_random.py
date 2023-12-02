import brownie
from brownie import chain

def _from(account):
	return {"from": account}


def stake_nft(staking, account, nft, tokenId):
	nft.approve(staking.address, tokenId, _from(account))

	return staking.stakeNft(nft.address, tokenId, _from(account))


def test_only_arena_modifier(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	with brownie.reverts('Only arena contract can make call'):
		functions.resetRandom(_from(accounts[0]))
		functions.resetRandom(_from(accounts[1]))


	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	stake_nft(staking, accounts[1], nft, 6)

	chain.sleep(arena.firstStageDuration())

	daiToken.approve(voting, 300e18, _from(accounts[0]))
	# checking i < numberOfNftsWithNonZeroVotes
	voting.createNewVotingPosition(1, 10e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(2, 25e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(3, 230e18, True, _from(accounts[0]))

	chain.sleep(arena.secondStageDuration())
	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())
	chain.sleep(arena.fifthStageDuration())

	# Update epoch uses resetRandom()
	tx = arena.updateEpoch()
	assert tx.status == 1

