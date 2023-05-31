import brownie 

# def test_stake(tokens, battles, accounts):
# 	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = battles
# 	value = 10 ** 18
# 	zooToken.approve(xZoo, value)
# 	index = xZoo.indexCounter()

# 	tx = xZoo.stakeZoo(value, accounts[-1])

# 	assert index == 1
# 	assert xZoo.ownerOf(index) == accounts[-1]
	
# 	x_zoo_position = xZoo.xZooPositions(index)
# 	assert x_zoo_position["amount"] == value
# 	assert xZoo.tokenOfOwnerByIndex(accounts[-1], 0) == index