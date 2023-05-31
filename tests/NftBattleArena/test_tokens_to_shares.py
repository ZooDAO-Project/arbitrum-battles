import brownie
from brownie import chain


def _from(account):
	return {"from": account}


def test_return_shares_according_to_vault(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]
	
	tokensAmount = 1e8
	pps = vault.exchangeRateCurrent.call()
	tokensDecimals = 16

	expectedValue = tokensAmount * (10 ** 18) // pps
	assert arena.tokensToShares.call(tokensAmount) == expectedValue


def test_stress(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	for i in range(8):
		sharesAmount = 10 ** (8 + i)
		pps = vault.exchangeRateCurrent.call()

		expectedValue = sharesAmount * (10 ** 18) // pps
		assert arena.tokensToShares.call(sharesAmount) == expectedValue
