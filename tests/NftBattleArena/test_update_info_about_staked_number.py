
from _utils.utils import _from, stake_nft
from brownie import ZERO_ADDRESS, chain

def test_integer_overflow(accounts, battles, tokens):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	token_id = 1
	stake_nft(staking, accounts[0], nft, token_id)

	staking_position_id = 1
	staking.unstakeNft(staking_position_id, _from(accounts[0]))

def test_weight_and_number_update(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	tx1 = arena.updateInfoAboutStakedNumber(nft)

	assert arena.poolWeight(ZERO_ADDRESS, 2) == arena.poolWeight(nft, 2) == tx1.return_value
	assert arena.numberOfStakedNftsInCollection(2, nft) == 9

	chain.sleep(arena.epochDuration())
	arena.updateEpoch()

	assert arena.currentEpoch() == 3

	tx2 = arena.updateInfoAboutStakedNumber(nft)

	assert arena.poolWeight(ZERO_ADDRESS, 2) == arena.poolWeight(nft, 2) == tx1.return_value
	assert arena.numberOfStakedNftsInCollection(2, nft) == 9

	assert arena.poolWeight(ZERO_ADDRESS, 3) == arena.poolWeight(nft, 3) == tx1.return_value == tx2.return_value
	assert arena.numberOfStakedNftsInCollection(3, nft) == 9