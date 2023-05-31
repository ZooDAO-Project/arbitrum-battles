import brownie

def test_one_collection_incentive_reward_of_staker(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	arena.updateInfoAboutStakedNumber(nft)
	assert arena.numberOfStakedNftsInCollection(1, nft) > 0
	assert arena.numberOfStakedNftsInCollection(2, nft) > 0

	tx = staking.claimIncentiveStakerReward(1, accounts[-1], {"from": accounts[0]})

	assert tx.return_value > 0
	assert zooToken.balanceOf(accounts[-1]) > 0