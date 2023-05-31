import brownie 

# def test_stake_and_claim(tokens, battles, accounts):
# 	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = battles
# 	value = 10 ** 18
# 	zooToken.approve(xZoo, value)

# 	tx = xZoo.stakeZoo(value, accounts[0])

# 	position_id = tx.return_value

# 	tx2 = xZoo.claimRewards(position_id, accounts[-1])
# 	assert tx2.return_value == 0