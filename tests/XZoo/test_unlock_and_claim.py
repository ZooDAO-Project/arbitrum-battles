import brownie 

# def test_unlock_and_claim_zoo(tokens, battles, accounts):
# 	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = battles
# 	value = 10 ** 18
# 	zooToken.approve(xZoo, value)

# 	tx = xZoo.stakeZoo(value, accounts[0])
# 	position_id = tx.return_value
# 	tx1 = xZoo.unlockAndClaim(position_id, accounts[-1])

# 	assert zooToken.balanceOf(accounts[-1]) == value
# 	assert tx1.return_value == (value, 0)

# 	id = tx.events["ZooStaked"]["positionId"]
# 	position = xZoo.xZooPositions(id)
# 	assert position["endEpoch"] >= position["startEpoch"]