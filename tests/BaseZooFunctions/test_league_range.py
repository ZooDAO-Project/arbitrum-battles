import brownie

def _from(account):
	return {"from": account}

def test_zoo_rewards(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	# check initial state
	assert functions.woodenLeague() == 400 * 10 ** 18
	assert functions.bronzeLeague() == 1500 * 10 ** 18
	assert functions.silverLeague() == 5000 * 10 ** 18
	assert functions.goldLeague() == 20000 * 10 ** 18
	assert functions.platinumLeague() == 100000 * 10 ** 18

	# reset leagues ranges for league and check

	# only owner can reset
	with brownie.reverts('Ownable: caller is not the owner'):
		functions.setLeagueRange(
			[
			550* 10 ** 18, 
			2550* 10 ** 18, 
			7550* 10 ** 18, 
			30050* 10 ** 18, 
			150050* 10 ** 18
			], _from(accounts[1]))
		
	# # amount of ranges is smaller than reqired
	# with brownie.reverts('Sequence has incorrect length'):
	# 	functions.setLeagueRange(
	# 		[
	# 		2550* 10 ** 18, 
	# 		7550* 10 ** 18, 
	# 		30050* 10 ** 18, 
	# 		150050* 10 ** 18
	# 		], _from(accounts[0]))

	# # amount of ranges is bigger than reqired
	# with brownie.reverts('Sequence has incorrect length'):
	# 	functions.setLeagueRange(
	# 		[
	# 		550* 10 ** 18, 
	# 		2550* 10 ** 18, 
	# 		7550* 10 ** 18, 
	# 		30050* 10 ** 18, 
	# 		150050* 10 ** 18,
	# 		250050* 10 ** 18
	# 		], _from(accounts[0]))

	# reset ranges
	functions.setLeagueRange(
			[
			550* 10 ** 18, 
			2550* 10 ** 18, 
			7550* 10 ** 18, 
			30050* 10 ** 18, 
			150050* 10 ** 18
			], _from(accounts[0]))
	
	# check state after reset
	assert functions.woodenLeague() == 550 * 10 ** 18
	assert functions.bronzeLeague() == 2550 * 10 ** 18
	assert functions.silverLeague() == 7550 * 10 ** 18
	assert functions.goldLeague() == 30050 * 10 ** 18
	assert functions.platinumLeague() == 150050 * 10 ** 18



