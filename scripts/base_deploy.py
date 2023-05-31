from brownie import *

def main():
	# zooToken = ZooTokenMock.deploy("name", "symbol", "18", 1e26, {"from": account})          # zoo token Mock.
	# daiToken = ZooTokenMock.deploy("name", "symbol", "18", 1e26, {"from": account})          # dai token Mock.
	# daiToken = DaiTokenMock.deploy # todo: fork dai
	active_network = network.show_active()
	account = accounts.load(active_network) # brownie account for deploy.

	try:
		variables = config["networks"][active_network]["variables"]
		vrfCoordinator = variables["chainlink"]["vrfCoordinator"]
		linkToken = variables["chainlink"]["linkToken"]
		daiToken = variables["tokens"]["daiToken"]
		zooToken = variables["tokens"]["zooToken"]
	except Exception as e: # for brownie console at development
		print(e)
		linkToken = ZERO_ADDRESS
		vrfCoordinator = ZERO_ADDRESS
		daiToken = "0x9dE882A68616FA96622ca5d032Cb7F7416823B0c"
		zooToken = "0x469bb20F4D2122275fB1fD715e7BaFCA1B36a50A"

	vault = YearnMock.deploy(daiToken, {"from": account}, publish_source=True) # dai address/mock 
	functions = BaseZooFunctions.deploy(vrfCoordinator, linkToken, {"from": account}, publish_source=True) # vrfCoordinator and link token addresses.
	governance = ZooGovernance.deploy(functions, account, {"from": account}, publish_source=True)         # functions address and aragon(owner) address.

	well = Token.deploy("well", "WELL", {"from": accounts[0]}, publish_source=True)
	well.mint(accounts[0], 4e25, {"from": accounts[0]})

	controller = ControllerMock.deploy(well.address, {"from": accounts[0]}, publish_source=True)
	well.transfer(controller.address, 4e25)

	duration_of_incentive_rewards = 60 * 60 * 24 * 7 * 3 # 3 weeks
	ve_zoo = ListingList.deploy(zooToken, 3000, 3000, 172800, duration_of_incentive_rewards, {"from": account}, publish_source=True) # todo: change time
	# address _zoo, uint256 _duration, uint256 _minTimelock, uint256 _maxTimelock

	staking = NftStakingPosition.deploy("zStakerPosition", "ZSP", ve_zoo, zooToken, {"from": account}, publish_source=True)

	voting = NftVotingPosition.deploy("zVoterPosition", "ZVP",
		daiToken, # dai token/mock
		zooToken, # zoo token/mock
		{"from": account}, publish_source=True)

	x_zoo = XZoo.deploy("xZoo", "XZOO", daiToken, zooToken, vault, {"from": account}, publish_source=True)

	iterable_mapping = IterableMapping.deploy({"from": account}, publish_source=True)

	jackpot_a = Jackpot.deploy(staking, vault, functions, "Jackpot A", "JKPTA", {"from": account}, publish_source=True)

	jackpot_b = Jackpot.deploy(voting, vault, functions, "Jackpot B", "JKPTB", {"from": account}, publish_source=True)

	arena = NftBattleArena.deploy(
		zooToken, # zoo token/mock
		daiToken, # dai token/mock
		vault, 
		governance,
		account,                                              # treasury pool     address/mock
		account,                                              # gas fee pool      address/mock
		account,                                              # team              address/mock
		staking,
		voting, 
		ve_zoo,
		controller,
		well,
		{"from": account}, publish_source=True)
	
	w_glmr = "0xAcc15dC74880C9944775448304B263D191c6077F" # todo: need to be moved to config
	arena.init(x_zoo, jackpot_a, jackpot_b, w_glmr)
	x_zoo.setNftBattleArena(arena)
	jackpot_a.setNftBattleArena(arena)
	jackpot_b.setNftBattleArena(arena)

	staking.setNftBattleArena(arena, {"from": account})
	voting.setNftBattleArena(arena, {"from": account})
	functions.init(arena, ve_zoo, account, {"from": account})        # connect functions with battleStaker and set owner(should be aragon in mainnet)

	ve_zoo.batchAllowNewContract(["0xF541BD5BC1D5b68080BDd408ad5903866240B813", 
		"0xC0988eaE601ffcDab49C145199F84cF2dbbd9849", 
		"0xd86EAe9B7D3ef173124F5aF299944DfD528bac19", 
		"0x3aA13120179841F09e889dbFDC70C567ED0e8094", 
		"0x9182BB660E013BB0781152c88E364351e1b7b49d"], 
		[vault, vault, vault, vault, vault], {"from": account})  # Allow contract nft.

	zoo = ZooMock.at(zooToken)

	number_of_epochs = duration_of_incentive_rewards // ve_zoo.epochDuration() + 1
	number_of_zoo_for_incentive_rewards_of_stakers = number_of_epochs * arena.baseStakerReward()
	number_of_zoo_for_incentive_rewards_of_voters = number_of_epochs * arena.baseVoterReward()
	zoo.mint(staking, number_of_zoo_for_incentive_rewards_of_stakers, {"from": account})
	zoo.mint(voting, number_of_zoo_for_incentive_rewards_of_voters, {"from": account})

	# send glmrs to controller mock:
	account.transfer(controller.address, account.balance * 9 // 10)
	# ve_zoo.allowNewContractForStaking("0x8e89A140596D73573cCF99A012E11Ccb6b89Ea3d", vault, {"from": account})  # Allow contract nft.
