
from _utils.utils import _from, stake_nft


def test_integer_overflow(accounts, battles, tokens):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	token_id = 1
	stake_nft(staking, accounts[0], nft, token_id)

	staking_position_id = 1
	staking.unstakeNft(staking_position_id, _from(accounts[0]))
