import brownie
from brownie import accounts

def test_setting_value(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles
	
	amounts = [1e18, 10e18, 100e18, 1000e18, 10000e18]
	
	base_zoo_functions.setLeagueRange(amounts)

	assert base_zoo_functions.woodenLeague() == amounts[0]
	assert base_zoo_functions.bronzeLeague() == amounts[1]
	assert base_zoo_functions.silverLeague() == amounts[2]
	assert base_zoo_functions.goldLeague() == amounts[3]
	assert base_zoo_functions.platinumLeague() == amounts[4]

	
def test_only_owner(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles

	amounts = [1e18, 10e18, 100e18, 1000e18, 10000e18]
	
	with brownie.reverts('Ownable: caller is not the owner'):
		base_zoo_functions.setLeagueRange(amounts, {"from": accounts[5]})
	

def test_getting_nft_league_by_votes(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles
	
	amounts = [1e18, 10e18, 100e18, 1000e18, 10000e18]
	
	base_zoo_functions.setLeagueRange(amounts)

	for i in range(5):
		league = base_zoo_functions.getNftLeague(amounts[i])
		assert league == i

	for i in range(5):
		league = base_zoo_functions.getNftLeague(amounts[i] + 1e18)
		assert league == i + 1