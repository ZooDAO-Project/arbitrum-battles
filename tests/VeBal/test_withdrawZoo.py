import brownie
from brownie import chain


#
# Utility functions
#
# has _ before name because from is internal reserved word
def _from(account):
	return {"from": account}


def test_multiplie_withdraw(accounts, finished_epoch):
	(vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	team = accounts[0]
	account1 = accounts[1]
	amount = 1e19
	fee = amount * 5 // 1000
	oldBalance = zooToken.balanceOf(account1)
	oldBalanceTeam = zooToken.balanceOf(team)

	voting.withdrawZooFromVotingPosition(4, amount, account1, _from(account1))

	assert zooToken.balanceOf(account1) == oldBalance + amount - fee
	assert zooToken.balanceOf(team) == oldBalanceTeam + fee