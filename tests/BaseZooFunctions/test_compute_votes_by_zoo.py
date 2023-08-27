import brownie
from brownie import chain
from fractions import Fraction
import math

from brownie.test import given, strategy as st
from hypothesis import note

def _from(account):
	return {"from": account}


def test_returns_correct_values(accounts, fourth_stage):
	(zooToken, daiToken, linkToken, nft) = fourth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fourth_stage[1]

	zoo = 100e18
	votes = functions.computeVotesByZoo(zoo)
	assert votes == zoo * 1.3

	stages = functions.getStageDurations()
	
	chain.sleep(math.ceil(stages[3] / 3))
	chain.mine(1)
	
	print(arena.getCurrentStage())

	votes = functions.computeVotesByZoo(zoo)
	assert votes == zoo

	chain.sleep(math.ceil(stages[3] / 3))
	chain.mine(1)

	votes = functions.computeVotesByZoo(zoo)
	assert votes == (zoo * 7 / 10)
	