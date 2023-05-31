from brownie import *
from brownie.network import priority_fee

def main(is_need_to_publish = True):
	priority_fee("auto")
	accounts.from_mnemonic("enter mnemonic")
	account = accounts[0]

	treasury = "0x1ada350F59ff5cFd1b0ABA004F63a0892FA93858" # DAO
	team = "0x0dd0782559a043A53D0a6662F673A9E937b6F1fa"     # team

	vault = "0xdDbdeda15C2Df67ee5F10782679dA93722d3189B"      # gmx vault
	dai = "0x5402B5F40310bDED796c7D0F3FF6683f5C0cFfdf"       # main token for vault.
	lpZooToken = "0x178E029173417b1F9C8bC16DCeC6f697bC323746" # balancer lp
	zooToken = "0x1689A6E1f09658FF37d0bB131514E701045876dA"   # zoo token

	zooVoteRate = 1 # rate for conversion lp to votes.
	veBal = "0xA0DAbEBAAd1b243BBb243f933013d560819eB66f" # balancer reward distributor
	gauge = "0x9232EE56ab3167e2d77E491fBa82baBf963cCaCE" # balancer gauge.

	collections = ["0x08f0ebffc998b104b89981a78823d486cab573b5", "0x0ab8837263f6c4f9823aaea2283bc11c9f6bbb8e", "0x1ac7a2fc7f66fa4edf2713a88cd4bad24220c86c"]
	royalty = [treasury, treasury, treasury]

	arenaFee = 10 # 275320000000000 # equal to 50 cents at the price of 1 eth at 1800$

	functions = BaseZooFunctions.deploy({"from": account}, publish_source=is_need_to_publish)
	functions.setStageDuration(0, 60 * 20, {"from": account}) # 1 stage - 20 mins
	functions.setStageDuration(1, 60 * 20, {"from": account}) # 2 stage - 20 mins
	functions.setStageDuration(2, 60 * 20, {"from": account}) # 3 stage - 20 mins
	functions.setStageDuration(3, 60 * 20, {"from": account}) # 4 stage - 20 mins
	functions.setStageDuration(4, 60 * 20, {"from": account}) # 5 stage - 20 mins
	governance = ZooGovernance.deploy(functions, account, {"from": account}, publish_source=is_need_to_publish)
	ve_zoo = ListingList.deploy(lpZooToken, 4, {"from": account}, publish_source=is_need_to_publish)

	staking = NftStakingPosition.deploy("zStakerPosition", "ZSP", ve_zoo, zooToken, functions, team, {"from": account}, publish_source=is_need_to_publish)
	voting = NftVotingPosition.deploy("zVoterPosition", "ZVP",
		dai, # frax
		zooToken, # zoo token/mock
		lpZooToken,
		functions,
		team,
		{"from": account}, publish_source=is_need_to_publish)

	arena = NftBattleArena.deploy(
		lpZooToken, # zoo token/mock
		dai, # frax
		vault, 
		governance,
		treasury,                                              # treasury pool     address/mock
		#"0x24410c1d93d1216E126b6A6cd32d79f634308b3b",                                              # gas fee pool      address/mock
		team,                                                  # team              address/mock
		staking,
		voting, 
		ve_zoo,
		{"from": account}, publish_source=is_need_to_publish)

	arena.init(veBal, gauge, zooVoteRate, lpZooToken, {"from": account})

	staking.setNftBattleArena(arena, {"from": account})
	voting.setNftBattleArena(arena, {"from": account})
	functions.init(arena, account, {"from": account})
	ve_zoo.init(arena, {"from": account})

	ve_zoo.batchAllowNewContract(collections, royalty, {"from": account})

	functions.setArenaFee(arenaFee, {"from": account})

	result = {
		"token" : dai,
		"vault" : vault,
		"zooToken" : zooToken,
		"lpZooToken" : lpZooToken,
		"collections" : collections,
		"functions" : functions,
		"governance" : governance,
		"ve_zoo" : ve_zoo,
		"staking" : staking,
		"voting" : voting,
		# "x_zoo" : x_zoo,
		# "jackpot_a" : jackpot_a,
		# "jackpot_b" : jackpot_b,
		"arena" : arena,
	}

	return result