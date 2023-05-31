import brownie 

# def test_unlock_zoo(tokens, battles, accounts):
# 	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = battles
# 	value = 10 ** 18
# 	zooToken.approve(xZoo, value)

# 	tx = xZoo.stakeZoo(value, accounts[0])
# 	position_id = tx.return_value
# 	tx1 = xZoo.unlockZoo(position_id, accounts[-1])

# 	assert zooToken.balanceOf(accounts[-1]) == value