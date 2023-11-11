import brownie
from brownie import ZERO_ADDRESS

def test_pool_weight_sum_in_first_epoch(accounts, fourth_stage):
	(zooToken, daiToken, linkToken, nft) = fourth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fourth_stage[1]

	assert arena.poolWeight(ZERO_ADDRESS, arena.currentEpoch()) == arena.poolWeight(nft, arena.currentEpoch())

def test_pool_weight_sum_before_and_after_update(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	assert arena.poolWeight(ZERO_ADDRESS, arena.currentEpoch()) != arena.poolWeight(nft, arena.currentEpoch())

	tx1 = arena.updateInfoAboutStakedNumber(nft)

	assert arena.poolWeight(ZERO_ADDRESS, arena.currentEpoch()) == arena.poolWeight(nft, arena.currentEpoch()) == tx1.return_value
 
def test_pool_weight_sum_in_second(account,)