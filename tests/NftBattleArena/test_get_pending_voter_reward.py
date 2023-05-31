import brownie
from brownie import chain


def _from(account):
	return {"from": account}


# def test_return_value(accounts, tokens, battles):
	# (vault, functions, governance, staking, voting, arena, listing) = battles
	# (zooToken, daiToken, linkToken, nft) = tokens

	# assert arena.getPendingVoterReward(0, 1, 2) != 0

# Test doen't work correctly because of fixture. FIX PAIRING IN FIXTURE !
def _test_return_value(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

	daiToken.approve(vault.address, 10e18, {"from": accounts[0]})
	vault.increaseMockBalance()

	assert (
		arena.getPendingVoterReward(1) or 
		arena.getPendingVoterReward(2) or 
		arena.getPendingVoterReward(3)
		) == 99991900727035