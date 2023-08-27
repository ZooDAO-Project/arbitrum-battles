import brownie
from brownie import accounts
import math

def test_setting_value(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles
	
	duration = 100
	for stage in range(5):
		base_zoo_functions.setStageDuration(stage, duration * (stage + 1))
	
	stages = base_zoo_functions.getStageDurations()

	for stage in range(5):
		assert stages[stage] == duration * (stage + 1)
	

def test_only_owner(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles

	# Range
	stage = 0
	duration = 1e18

	with brownie.reverts('Ownable: caller is not the owner'):
		base_zoo_functions.setStageDuration(stage, duration, {"from": accounts[6]})
	

def test_setting_non_existing_stage(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles
	
	non_existent_stage = 10
	duration = 1e20

	with brownie.reverts():
		base_zoo_functions.setStageDuration(non_existent_stage, duration)


def test_get_reward_for_non_existent_league(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles
	
	league = 10
	reward = base_zoo_functions.getLeagueZooRewards(league)
	assert reward == 0
	

def test_get_stage_and_epoch_durations(battles):
	(vault, base_zoo_functions, governance, staking, voting, arena, listingList) = battles
	
	duration = 100
	for stage in range(5):
		base_zoo_functions.setStageDuration(stage, duration)
	
	stages = base_zoo_functions.getStageDurations()

	for stage in range(6):
		if stage == 5: # epochDuration
			durations_sum = duration * 5
			assert stages[stage] == durations_sum
		else:
			assert stages[stage] == duration
	
