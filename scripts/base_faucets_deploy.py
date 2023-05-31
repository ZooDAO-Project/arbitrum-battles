from brownie import *

def main():
	active_network = network.show_active()
	account = accounts.load(active_network) # brownie account for deploy.

	# zooToken = ZooTokenMock.deploy("ZOO", "ZOO", "18", 9e26, {"from": account}, publish_source=True)
	zooToken = ZooMock.deploy("ZOO", "ZOO", {"from": account}, publish_source=True) # OZ mintable preset
	daiToken = Dai.deploy(69, {"from": account}, publish_source=True)

	nft = ZooNft.deploy("zBored Ape Yacht Club", "zBAYC", {"from": accounts[0]}, publish_source=True) # testnet nft contract 1
	nft1 = ZooNft.deploy("zCryptokitties", "zCK", {"from": accounts[0]}, publish_source=True) # testnet nft contract 2
	nft2 = ZooNft.deploy("zAzuki", "zAZUKI", {"from": accounts[0]}, publish_source=True) # testnet nft contract 3
	nft3 = ZooNft.deploy("zDoodles", "zDOODLE", {"from": accounts[0]}, publish_source=True) # testnet nft contract 4

	faucet = ZooTokenFaucet.deploy("zNFT0", "zNFT0", zooToken.address, daiToken.address, [nft, nft1, nft2, nft3], {"from": account}, publish_source=True) # faucet
	faucet.batchAddToWhiteList(["0xaB90ff4a66b9727158C3422770b450d7Ca9011B1", "0x4122691B0dd344b3CCd13F4Eb8a71ad22c8CCe5c"])

	nft.transferOwnership(faucet.address)
	nft1.transferOwnership(faucet.address)
	nft2.transferOwnership(faucet.address)
	nft3.transferOwnership(faucet.address)

	daiToken.mint(faucet.address, 5e26)
	daiToken.mint(account, 1e26)
	daiToken.mint("0x4122691B0dd344b3CCd13F4Eb8a71ad22c8CCe5c", 1e26)
	daiToken.mint("0xaB90ff4a66b9727158C3422770b450d7Ca9011B1", 1e26)

	zooToken.mint(faucet.address, 5e26)
	zooToken.mint(account, 1e26)
	zooToken.mint("0x4122691B0dd344b3CCd13F4Eb8a71ad22c8CCe5c", 5e26)
	zooToken.mint("0xaB90ff4a66b9727158C3422770b450d7Ca9011B1", 5e26)

	faucet.multiMint("0x4122691B0dd344b3CCd13F4Eb8a71ad22c8CCe5c", {"from": account})
	faucet.multiMint("0xaB90ff4a66b9727158C3422770b450d7Ca9011B1", {"from": account})
