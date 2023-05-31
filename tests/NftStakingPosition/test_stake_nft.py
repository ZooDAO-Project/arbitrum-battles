import brownie


def test_allowed_collection_requirement(accounts, battles, ZooNftFaucet):
	(vault, functions, governance, staking, voting, arena, listing) = battles

	nft = ZooNftFaucet.deploy('', '', {"from": accounts[1]})
	tokenId = nft.mintNft({"from": accounts[1]}).return_value

	with brownie.reverts("NFT collection is not allowed"):
		staking.stakeNft(nft.address, tokenId)


def test_staking_nft_mint(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	account = accounts[8]
	fromAccount = {"from": account}

	tokenId = nft.mintNft(fromAccount).return_value
	nft.approve(staking.address, tokenId, fromAccount)

	print(tokenId)
	print(nft.ownerOf(tokenId))
	print(accounts[1].address)

	staking.stakeNft(nft.address, tokenId, fromAccount)

	assert nft.balanceOf(account) == 0
	assert staking.balanceOf(account) == 1


def test_non_nft_contract_address(accounts, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles

	address = "0x0000000000000000000000000000000000000042"

	with brownie.reverts():
		staking.stakeNft(address, 0, {"from": accounts[1]})


def test_setting_position(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	tokenId = nft.mintNft({"from": accounts[1]}).return_value
	nft.approve(staking.address, tokenId, {"from": accounts[1]})

	staking.stakeNft(nft.address, tokenId, {"from": accounts[1]})
	stakingPositionId = 1
	assert staking.positions(stakingPositionId) == (nft.address, tokenId)
