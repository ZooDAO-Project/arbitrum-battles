import brownie
from brownie import accounts

def test_setting_value(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles
	
	base_rewards = 100e18
	for league in range(6):
		base_zoo_functions.setZooRewards(league, base_rewards * (league + 1))
		assert base_zoo_functions.getLeagueZooRewards(league) == base_rewards * (league + 1)
	

def test_only_owner(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles

	# Range
	league = 0
	reward = 10000000000e18

	with brownie.reverts('Ownable: caller is not the owner'):
		base_zoo_functions.setZooRewards(league, reward, {"from": accounts[5]})
	

def test_setting_non_existing_league(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles
	
	default_rewards = []
	for league in range(6):
		reward = base_zoo_functions.getLeagueZooRewards(league)
		default_rewards.append(reward)

	# Range
	league = 10 # Non existent
	reward = 100e18

	base_zoo_functions.setZooRewards(league, reward)

	# Rewards stayed the same
	for league in range(6):
		reward = base_zoo_functions.getLeagueZooRewards(league)
		assert reward == default_rewards[league]


def test_get_reward_for_non_existent_league(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles
	
	league = 10
	reward = base_zoo_functions.getLeagueZooRewards(league)
	assert reward == 0
	
