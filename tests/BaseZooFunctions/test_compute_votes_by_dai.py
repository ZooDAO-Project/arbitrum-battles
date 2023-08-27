import brownie
from brownie import chain
from fractions import Fraction
import math

from brownie.test import given, strategy as st
from hypothesis import note

def _from(account):
	return {"from": account}


def test_returns_correct_values(accounts, second_stage):
	(zooToken, daiToken, linkToken, nft) = second_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = second_stage[1]

	dai = 100e18
	votes = functions.computeVotesByDai(dai)
	assert votes == dai * 1.3

	stages = functions.getStageDurations()
	second_stage_duration = stages[1]
	
	chain.sleep(math.ceil(second_stage_duration / 3))
	chain.mine(1)
	
	print(arena.getCurrentStage())

	votes = functions.computeVotesByDai(dai)
	assert votes == dai

	chain.sleep(math.ceil(second_stage_duration / 3))
	chain.mine(1)

	votes = functions.computeVotesByDai(dai)
	assert votes == dai * 7 / 10

	chain.sleep(math.ceil(second_stage_duration))
	chain.mine(1)

	votes = functions.computeVotesByDai(dai)
	assert votes == dai * 13 / 10

	