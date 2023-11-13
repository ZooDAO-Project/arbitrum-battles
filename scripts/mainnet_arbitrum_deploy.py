from brownie import *
from brownie.network import priority_fee

def main(account = accounts[0], is_need_to_publish = True):
	priority_fee("auto")

	treasury = "0x1ada350F59ff5cFd1b0ABA004F63a0892FA93858" # DAO
	team = "0x0dd0782559a043A53D0a6662F673A9E937b6F1fa"     # team
	glpRewardRouter = "0xB95DB5B167D75e6d04227CfFFA61069348d271F5"
	glpManager = "0x3963FfC9dff443c2A94f21b129D429891E32ec18"

	vault = "0x9d284e037c20f029c8C56bbE4ff7C0F8de0FA4A9"    # gmx vault
	dai = "0x5402B5F40310bDED796c7D0F3FF6683f5C0cFfdf"       # main token for vault.
	lpZooToken = "0x2517cd42eE966862e8EcaAc9Abd1CcD272d897b6" # Camelot lp
	zooToken = "0x1689A6E1f09658FF37d0bB131514E701045876dA"   # zoo token

	zoo_vote_rate_nominator = 20 # rate for conversion lp to votes.
	zoo_vote_rate_denominator = 1

	arenaFee = 250000000000000  # equal to 50 cents at the price of 1 eth at 2000$

	functions = BaseZooFunctions.deploy({"from": account}, publish_source=is_need_to_publish)

	governance = ZooGovernance.deploy(functions, account, {"from": account}, publish_source=is_need_to_publish)
	ve_zoo = ListingList.deploy(lpZooToken, 13, {"from": account}, publish_source=is_need_to_publish)
	

	staking = NftStakingPosition.deploy("zStakerPosition", "ZSP", 
		ve_zoo, 
		zooToken, 
		functions, 
		team, 
		{"from": account}, publish_source=is_need_to_publish)
	
	voting = NftVotingPosition.deploy("zVoterPosition", "ZVP",
		dai, # sGLP
		zooToken,
		lpZooToken,
		functions,
		team,
		glpRewardRouter,
		glpManager,
		{"from": account}, publish_source=is_need_to_publish)

	arena = NftBattleArena.deploy(
		lpZooToken, # lpZoo
		dai, # sGLP
		vault, 
		governance,
		treasury,
		staking,
		voting, 
		ve_zoo,
		{"from": account}, publish_source=is_need_to_publish)

	arena.init(zoo_vote_rate_nominator, zoo_vote_rate_denominator, zooToken, {"from": account})	

	staking.setNftBattleArena(arena, {"from": account})
	voting.setNftBattleArena(arena, {"from": account})
	functions.init(arena, account, {"from": account})
	ve_zoo.init(arena, {"from": account})

	functions.setArenaFee(arenaFee, {"from": account})

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
		"arena" : arena
	}

	return result

# After you need to call batchAllowColenctions allow_collections.py for prod