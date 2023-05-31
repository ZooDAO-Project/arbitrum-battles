import brownie
from brownie import chain, ZERO_ADDRESS

day = 24 * 60 * 60

def test_unlock(accounts, second_stage):
	((zoo_token, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listingList)) = second_stage
	collection = accounts[-4]
	recipient = accounts[-5]
	listingList.allowNewContractForStaking(collection, recipient)
	balance = zoo_token.balanceOf(accounts[0])

	chain.time()

	value = 1e21
	zoo_token.approve(listingList, value)

	balance_of_ve_zoo = zoo_token.balanceOf(listingList)
	tx1 = listingList.voteForNftCollection(collection, value)

	ve_position_id = tx1.events["Transfer"][1]["tokenId"]
	ve_position = listingList.vePositions(ve_position_id)

	assert ve_position["zooLocked"] == value
	assert balance_of_ve_zoo + value == zoo_token.balanceOf(listingList)
	assert balance - value == zoo_token.balanceOf(accounts[0])
	assert tx1.events["Transfer"][0]["value"] == value

	chain.sleep(arena.epochDuration() - 1)
	arena.updateEpoch()
	tx2 = listingList.unlockZoo(ve_position_id)

	assert tx2.events["Transfer"][0]["value"] == value
	assert balance == zoo_token.balanceOf(accounts[0])

