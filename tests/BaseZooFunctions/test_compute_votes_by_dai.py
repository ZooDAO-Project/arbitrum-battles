import brownie
from brownie import chain
from fractions import Fraction

from brownie.test import given, strategy as st
from hypothesis import note

def _from(account):
	return {"from": account}


@given(val=st('uint256', max_value=3.464307406e15))
def test_returns_correct_value(accounts, second_stage, val):
	(zooToken, daiToken, linkToken, nft) = second_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = second_stage[1]

	returned = functions.computeVotesByDai(val)
	note(val)
	assert returned == int(Fraction(val) * Fraction(13,10))