import brownie
from brownie import chain

def get_first_part_of_active_staker_positions(arena, number):
	order = []
	for i in range(number):
		order.append(arena.activeStakerPositions(i))
	return order

def test_correct_order_after_voting(second_stage, accounts):
	((zooToken, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listingList)) = second_stage

	assert [1, 2, 3] == get_first_part_of_active_staker_positions(arena, 3)

	amount1 = 1e18
	amount2 = 2e18
	daiToken.approve(voting, amount1, {"from": accounts[0]})
	daiToken.approve(voting, amount2, {"from": accounts[1]})
	tx1 = voting.createNewVotingPosition(3, amount1, True, {"from": accounts[0]})

	assert arena.numberOfNftsWithNonZeroVotes() == 1
	assert 3 == get_first_part_of_active_staker_positions(arena, 3)[0]
	
	tx2 = voting.createNewVotingPosition(1, amount2, True, {"from": accounts[1]})

	assert arena.numberOfNftsWithNonZeroVotes() == 2
	assert [3, 1] == get_first_part_of_active_staker_positions(arena, 2)