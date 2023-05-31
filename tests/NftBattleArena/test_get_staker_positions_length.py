
#
# Utility functions
#
# has _ before name because from is internal reserved word
def _from(account):
	return {"from": account}


def stake_nft(staking, account, nft, tokenId):
	nft.approve(staking.address, tokenId, _from(account))

	return staking.stakeNft(nft.address, tokenId, _from(account))


def test_getting_length__while_staking(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	assert arena.getStakerPositionsLength() == 0

	for i in range(3):
		for j in range(3):
			stake_nft(staking, accounts[i], nft, j + 1 + i * 3)
			assert arena.getStakerPositionsLength() == j + 1 + 3 * i

	for i in range(3):
		for j in range(3):
			staking.unstakeNft(j + 1 + i * 3, _from(accounts[i]))
			assert arena.getStakerPositionsLength() == 9 - (j + 1 + 3 * i)

	assert arena.getStakerPositionsLength() == 0
