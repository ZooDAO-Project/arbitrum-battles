import brownie 

# def test_add_zoo(tokens, battles, accounts):
# 	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = battles
# 	value = 10 ** 18
# 	zooToken.approve(xZoo, 2 * value)

# 	tx = xZoo.stakeZoo(value, accounts[0])
# 	position_id = tx.return_value
# 	tx1 = xZoo.addZoo(position_id, value)

# 	assert xZoo.xZooPositions(position_id)["amount"] == 2 * value