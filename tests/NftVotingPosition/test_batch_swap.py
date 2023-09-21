import brownie
from brownie import chain

def test_batch_swap(accounts, finished_epoch):
	((zooToken, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listing)) = finished_epoch

	assert arena.getCurrentStage() == 0 # Check that now first stage

	staking.unstakeNft(1, {"from": accounts[0]})
	staking.batchUnstakeNft([2, 3], {"from": accounts[0]})

	tx1 = voting.batchSwapVotesFromPrositionsForUnstakedNft([1, 2, 3], {"from": accounts[0]})

	assert len(tx1.events["LiquidatedVotingPosition"]) == 3
	assert len(tx1.events["CreatedVotingPosition"]) == 3
