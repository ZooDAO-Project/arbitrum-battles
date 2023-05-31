from brownie import *

def main():
	active_network = network.show_active()
	account = accounts.load(active_network) # brownie account for deploy.

	zooToken = ZooTokenMock.deploy("ZOO", "ZOO", "18", 9e26, {"from": account}, publish_source=True)
	daiToken = Dai.deploy(69, {"from": account}, publish_source=True)

	faucet = ZooTokenFaucet.deploy("zNFT", "zNFT", zooToken.address, daiToken.address, {"from": account}, publish_source=True)
	faucet.batchAddToWhiteList(["0xaB90ff4a66b9727158C3422770b450d7Ca9011B1", "0x4122691B0dd344b3CCd13F4Eb8a71ad22c8CCe5c"])
	daiToken.mint(faucet.address, 5e26)
	daiToken.mint(account, 1e26)

	daiToken.mint("0x4122691B0dd344b3CCd13F4Eb8a71ad22c8CCe5c", 1e26)
	daiToken.mint("0xaB90ff4a66b9727158C3422770b450d7Ca9011B1", 1e26)

	faucet.multiMint("0x4122691B0dd344b3CCd13F4Eb8a71ad22c8CCe5c", {"from": account})
	faucet.multiMint("0xaB90ff4a66b9727158C3422770b450d7Ca9011B1", {"from": account})
