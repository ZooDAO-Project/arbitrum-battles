import brownie

def _from(account):
	return {"from": account}

def test_zoo_rewards(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

    # check initial state
	assert functions.getLeagueZooRewards(0) == 21 * 10 ** 18
	assert functions.getLeagueZooRewards(1) == 123 * 10 ** 18
	assert functions.getLeagueZooRewards(2) == 420 * 10 ** 18
	assert functions.getLeagueZooRewards(3) == 1818 * 10 ** 18
	assert functions.getLeagueZooRewards(4) == 6969 * 10 ** 18
	assert functions.getLeagueZooRewards(5) == 12345 * 10 ** 18
	assert functions.getLeagueZooRewards(6) == 0

	# reset leagues zoo rewards for league and check

	# only owner can reset
	with brownie.reverts('Ownable: caller is not the owner'):
		functions.setZooRewards(0, 1111111, _from(accounts[1]))

	# Wooden League
	functions.setZooRewards(0, 101 * 10 ** 18, _from(accounts[0]))
	assert functions.getLeagueZooRewards(0) == 101 * 10 ** 18

	# Bronze League
	functions.setZooRewards(1, 501 * 10 ** 18, _from(accounts[0]))
	assert functions.getLeagueZooRewards(1) == 501 * 10 ** 18

	# Silver League
	functions.setZooRewards(2, 1001 * 10 ** 18, _from(accounts[0]))
	assert functions.getLeagueZooRewards(2) == 1001 * 10 ** 18

	# Gold League
	functions.setZooRewards(3, 3001 * 10 ** 18, _from(accounts[0]))
	assert functions.getLeagueZooRewards(3) == 3001 * 10 ** 18

	# Platinum League
	functions.setZooRewards(4, 12501 * 10 ** 18, _from(accounts[0]))
	assert functions.getLeagueZooRewards(4) == 12501 * 10 ** 18

	# Master League
	functions.setZooRewards(5, 30001 * 10 ** 18, _from(accounts[0]))
	assert functions.getLeagueZooRewards(5) == 30001 * 10 ** 18

	# League that does not exist, nothing will change
	functions.setZooRewards(6, 30001 * 10 ** 18, _from(accounts[0]))
	assert functions.getLeagueZooRewards(6) == 0



