import brownie 

# def test_withdraw_zoo(tokens, battles, accounts):
# 	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = battles
# 	value = 10 ** 18
# 	zooToken.approve(xZoo, value)

# 	tx = xZoo.stakeZoo(value, accounts[0])
# 	position_id = tx.return_value
# 	tx1 = xZoo.withdrawZoo(position_id, value // 2, accounts[-1])

# 	assert xZoo.xZooPositions(position_id)["amount"] == value // 2
# 	assert zooToken.balanceOf(accounts[-1]) == value // 2