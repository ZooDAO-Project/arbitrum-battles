import brownie
from brownie import chain


def _from(account):
	return {"from": account}


def test_return_shares_according_to_vault(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]
	
	sharesAmount = 1e8
	pps = vault.exchangeRateCurrent.call()

	expectedValue = sharesAmount * pps // (10 ** 18)
	assert abs(arena.sharesToTokens.call(sharesAmount) - expectedValue) < 10


def test_stress(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]
	
	print(daiToken.balanceOf(vault))
	for i in range(37):
		sharesAmount = 10 ** (8 + i)
		print(i, sharesAmount)
		pps = vault.exchangeRateCurrent.call()
		
		expectedValue = sharesAmount * pps // (10 ** 18)
		assert arena.sharesToTokens.call(sharesAmount) == expectedValue
