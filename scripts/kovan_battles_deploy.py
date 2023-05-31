from brownie import accounts, ZooTokenMock, ZooNftFaucet, YearnMock, BaseZooFunctions, ZooGovernance, NftStakingPosition, NftVotingPosition, NftBattleArena
account = accounts.load('kovan')

def main():
	# zooToken = ZooTokenMock.deploy("name", "symbol", "18", 1e26, {"from": account})          # zoo token Mock.
	# daiToken = ZooTokenMock.deploy("name", "symbol", "18", 1e26, {"from": account})          # dai token Mock.

	vault = YearnMock.deploy("0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa", {"from": account}, publish_source=True) # dai address/mock 
	functions = BaseZooFunctions.deploy("0xdD3782915140c8f3b190B5D67eAc6dc5760C46E9", "0xa36085F69e2889c224210F603D836748e7dC0088", {"from": account}, publish_source=True) # vrfCoordinator and link token addresses.
	governance = ZooGovernance.deploy(functions.address, account, {"from": account}, publish_source=True)         # functions address and aragon(owner) address.

	staking = NftStakingPosition.deploy("zStakerPosition", "ZSP", {"from": account}, publish_source=True)

	voting = NftVotingPosition.deploy("zVoterPosition", "ZVP",
	"0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa", # dai token/mock
	"0x19455784cc60cE5096be40669Be991d550E4742A", # zoo token/mock
	{"from": account}, publish_source=True)

	arena = NftBattleArena.deploy(
	"0x19455784cc60cE5096be40669Be991d550E4742A", # zoo token/mock
	"0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa",                                   # dai token/mock
	vault.address, 
	governance.address,
	account,                                              # treasury pool     address/mock
	account,                                              # gas fee pool      address/mock
	account,                                              # team              address/mock
	staking.address,
	voting.address, 
	{"from": account}, publish_source=True)

	staking.setNftBattleArena(arena.address, {"from": account})
	voting.setNftBattleArena(arena.address, {"from": account})
	functions.init(arena.address, {"from": account})                      # connect functions with battleStaker

	# staking.allowNewContractForStaking(nft.address, {"from": account})  # Allow contract nft.
