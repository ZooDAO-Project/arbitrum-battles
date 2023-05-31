import brownie
from brownie import chain


def test_init(vault, tokens, accounts):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	defaultExchangeRate = 209460678715639526810127788

	assert vault.exchangeRateCurrent.call() == defaultExchangeRate # current exchange rate
	assert vault._shareValue.call(1e8) == 20946067871563952
	assert vault._sharesForValue.call(1e18) == 4774165758

def test_after_first_mint(vault, tokens, accounts):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	defaultExchangeRate = 209460678715639526810127788

	#daiToken.transfer(vault, 1e21)

	daiToken.approve(vault, 2**256 - 1)
	tx = vault.mint(1e18)

	assert vault.exchangeRateCurrent.call() != defaultExchangeRate
	assert vault.exchangeRateCurrent.call() == 209460678721578648631411846
	assert vault._shareValue.call(1e8) == 20946067872157864
	assert vault._sharesForValue.call(1e18) == 4774165758

def test_after_increase_balance(vault, tokens, accounts):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	defaultExchangeRate = 209460678715639526810127788

	#daiToken.transfer(vault, 1e21)

	daiToken.approve(vault, 2**256 - 1)
	tx = vault.mint(1e18)

	daiToken.transfer(vault, 1e21) # transfer isn't changing rate or share value

	assert vault.exchangeRateCurrent.call() != defaultExchangeRate
	assert vault.exchangeRateCurrent.call() == 209460678721578648631411846
	assert vault._shareValue.call(1e8) == 20946067872157864
	assert vault._sharesForValue.call(1e18) == 4774165758

	vault.increaseMockBalance()

	assert vault.exchangeRateCurrent.call() // 209460678721578648631411846 > 0
	assert vault._shareValue.call(1e8) // 20946067872157864 > 0
	assert vault._sharesForValue.call(1e18) // 4774165758 == 0

# copied from test_shares_to_tokens.py
# def test_return_shares_according_to_vault(accounts, fifth_stage):
# 	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
# 	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]
	
# 	sharesAmount = 1e18
# 	pps = vault.pricePerShare()
# 	tokensDecimals = daiToken.decimals()

# 	expectedValue = sharesAmount * pps / (10 ** tokensDecimals)
# 	assert arena.sharesToTokens(sharesAmount) == expectedValue


# def test_stress(accounts, fifth_stage):
# 	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
# 	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]
	
# 	print(daiToken.balanceOf(vault))
# 	for i in range(37):
# 		sharesAmount = 10 ** (18 + i)
# 		print(i, sharesAmount)
# 		pps = vault.pricePerShare()
# 		tokensDecimals = daiToken.decimals()

# 		expectedValue = sharesAmount * pps / (10 ** tokensDecimals)
# 		assert arena.sharesToTokens(sharesAmount) == expectedValue

# new tests below.

# def test_shareValue_equal_to_sharesToTokens(accounts, fifth_stage):
# 	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
# 	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]
# 	amount = 100e18
# 	amount1 = 20e18
# 	amount2 = 8e18

# 	daiToken.approve(vault.address, amount*2)
# 	vault.mint(amount)
# 	vault.redeemUnderlying(amount1, accounts[1])

# 	shares = 20000000000000000000
# 	pps = vault.exchangeRateStored()
	

# 	assert True
