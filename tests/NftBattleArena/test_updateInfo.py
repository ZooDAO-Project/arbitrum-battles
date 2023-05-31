import brownie
from brownie import *

def _from(account):
	return {"from": account}


def test_updateInfo_should_skip_rewriting(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	currentEpoch = arena.currentEpoch() # current epoch 2

	pairIndex = 0
	pair = arena.pairsInEpoch(currentEpoch -1, pairIndex) # get pairs from 1st epoch.

	token1 = pair["token1"] # get id
	token2 = pair["token2"] # get id

	tokensAtStartEpoch1 = arena.rewardsForEpoch(token1, currentEpoch)["yTokens"] # get amount of yTokens
	tokensAtStartEpoch2 = arena.rewardsForEpoch(token2, currentEpoch)["yTokens"] # get amount of yTokens
	lastUpdateEpoch1 = arena.stakingPositionsValues(token1)["lastUpdateEpoch"]
	lastUpdateEpoch2 = arena.stakingPositionsValues(token2)["lastUpdateEpoch"]

	assert lastUpdateEpoch1 == currentEpoch # it sets in chooseWinner to next epoch.
	assert lastUpdateEpoch2 == currentEpoch

	print(token1, "token1")
	print(token2, "token2")
	print("tokensAtStartEpoch1: ", tokensAtStartEpoch1)
	print("tokensAtStartEpoch2: ", tokensAtStartEpoch2)

	arena.updateInfo(token1) # update info should skip rewriting if lastUpdateEpoch is current,
	arena.updateInfo(token2)

	###
	tokensAfterUpdate1 = arena.rewardsForEpoch(token1, currentEpoch)["yTokens"]
	tokensAfterUpdate2 = arena.rewardsForEpoch(token2, currentEpoch)["yTokens"]
	print("tokensAfterUpdate1: ", tokensAfterUpdate1)
	print("tokensAfterUpdate2: ", tokensAfterUpdate2)
	print("lastUpdateEpoch1: ", lastUpdateEpoch1)
	print("lastUpdateEpoch2: ", lastUpdateEpoch2)
	
	assert tokensAtStartEpoch1 == tokensAfterUpdate1 # so, it should not be changed by updateInfo
	assert tokensAtStartEpoch2 == tokensAfterUpdate2
