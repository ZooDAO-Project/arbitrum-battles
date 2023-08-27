from brownie import *

def test_simple_incentive_reward(accounts, finished_epoch):
	((zooToken, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listing)) = finished_epoch
	
	tx1 = staking.claimIncentiveStakerReward(1, accounts[-1], {"from": accounts[0]})
	
	assert tx1.return_value > 0

def test_batch_incentive_reward(accounts, finished_epoch):
	((zooToken, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listing)) = finished_epoch

	reward = staking.claimIncentiveStakerReward.call(1, accounts[-1], {"from": accounts[0]})

	tx1 = staking.batchClaimIncentiveStakerReward([1, 2], accounts[-1], {"from": accounts[0]})

	assert tx1.return_value > reward