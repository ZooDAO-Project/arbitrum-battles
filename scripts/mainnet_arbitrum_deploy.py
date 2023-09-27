from brownie import *


def main():
	active_network = network.show_active()
	account = accounts.load(active_network)

	treasury = "0x1ada350F59ff5cFd1b0ABA004F63a0892FA93858" # DAO
	team = "0x0dd0782559a043A53D0a6662F673A9E937b6F1fa"     # team
	glpRewardRouter = "0xB95DB5B167D75e6d04227CfFFA61069348d271F5"
	glpManager = "0x3963FfC9dff443c2A94f21b129D429891E32ec18"

	vault = ""    # gmx vault
	dai = ""       # main token for vault.
	lpZooToken = "" # balancer lp
	zooToken = ""   # zoo token

	zooVoteRate = 1 # rate for conversion lp to votes.
	veBal = "" # balancer reward distributor
	gauge = "" # balancer gauge.
	
	timeLock = [1814400, 1814400, 7257600, 7257600]

	functions = BaseZooFunctions.deploy(ZERO_ADDRESS, ZERO_ADDRESS, {"from": account}, publish_source=True)
	governance = ZooGovernance.deploy(functions, account, {"from": account}, publish_source=True)
	ve_zoo = ListingList.deploy(zooToken, timeLock[0], timeLock[1], timeLock[2], timeLock[3], {"from": account}, publish_source=True)

	staking = NftStakingPosition.deploy("zStakerPosition", "ZSP", ve_zoo, zooToken, {"from": account}, publish_source=True)
	voting = NftVotingPosition.deploy("zVoterPosition", "ZVP",
		dai, # dai
		zooToken, # zoo token/mock
		lpZooToken,
		functions,
		treasury,
		glpRewardRouter,
		glpManager,
		{"from": account}, publish_source=True)

	x_zoo = XZoo.deploy("xZoo", "XZOO", dai, zooToken, vault, {"from": account}, publish_source=True)
	iterable_mapping = IterableMapping.deploy({"from": account}, publish_source=True)
	jackpot_a = Jackpot.deploy(staking, vault, functions, "Jackpot A", "JKPTA", {"from": account}, publish_source=True)
	jackpot_b = Jackpot.deploy(voting, vault, functions, "Jackpot B", "JKPTB", {"from": account}, publish_source=True)

	arena = NftBattleArena.deploy(
		lpZooToken, # zoo token/mock
		dai, # dai
		vault, 
		governance,
		treasury,                                              # treasury pool     address/mock
		#"0x24410c1d93d1216E126b6A6cd32d79f634308b3b",                                              # gas fee pool      address/mock
		# team,                                              # team              address/mock
		staking,
		voting, 
		ve_zoo,
		{"from": account}, publish_source=True)

	arena.init(x_zoo, jackpot_a, jackpot_b, veBal, gauge, zooVoteRate, {"from": account})
	x_zoo.setNftBattleArena(arena, {"from": account})
	jackpot_a.setNftBattleArena(arena, {"from": account})
	jackpot_b.setNftBattleArena(arena, {"from": account})

	staking.setNftBattleArena(arena, {"from": account})
	voting.setNftBattleArena(arena, {"from": account})
	functions.init(arena, account, {"from": account})

	result = {
		"token" : dai,
		"vault" : vault,
		"zooToken" : zooToken,
		"lpZooToken" : lpZooToken,
		"functions" : functions,
		"governance" : governance,
		"ve_zoo" : ve_zoo,
		"staking" : staking,
		"voting" : voting,
		"x_zoo" : x_zoo,
		"jackpot_a" : jackpot_a,
		"jackpot_b" : jackpot_b,
		"arena" : arena
	}

	return result