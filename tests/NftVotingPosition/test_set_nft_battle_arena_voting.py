import brownie
from brownie import ZERO_ADDRESS

# Sample addresses
arena = '0x0000000000000000000000000000000000000040'
dai = "0x0000000000000000000000000000000000000041"
zoo = "0x0000000000000000000000000000000000000042"
notLpZoo = "0x0000000000000000000000000000000000000043"


def test_set_nft_battle_arena(accounts, NftVotingPosition, base_zoo_functions):
	voting = NftVotingPosition.deploy("name", "symbol", dai, zoo, notLpZoo, base_zoo_functions, accounts[0], ZERO_ADDRESS, ZERO_ADDRESS, {"from": accounts[0]})
	voting.setNftBattleArena(arena, {"from": accounts[0]})

	assert voting.nftBattleArena() == arena


def test_owner(accounts, NftVotingPosition, base_zoo_functions):
	voting = NftVotingPosition.deploy("name", "symbol", dai, zoo, notLpZoo, base_zoo_functions, accounts[0], ZERO_ADDRESS, ZERO_ADDRESS, {"from": accounts[0]})

	with brownie.reverts("Ownable: caller is not the owner"):
		voting.setNftBattleArena(arena, {"from": accounts[1]})


def test_second_setting_of_arena_address(accounts, battles):
	(vault, functions, governance, voting, voting, arena, listing) = battles

	with brownie.reverts():
		voting.setNftBattleArena(arena, {"from": accounts[0]})


def test_emitting_event(accounts, NftVotingPosition, base_zoo_functions):
	voting = NftVotingPosition.deploy("name", "symbol", dai, zoo, notLpZoo, base_zoo_functions, accounts[0], ZERO_ADDRESS, ZERO_ADDRESS, {"from": accounts[0]})

	tx = voting.setNftBattleArena(arena, {"from": accounts[0]})

	# Checking "NftBattleArenaSetted" event
	assert len(tx.events) == 1
	assert tx.events[0]["nftBattleArena"] == arena
