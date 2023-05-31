import brownie

def _from(account):
	return {"from": account}


def test_owner_requirement(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	tokenId = nft.mintNft(_from(accounts[1])).return_value
	nft.approve(staking.address, tokenId, _from(accounts[1]))
	
	staking.stakeNft(nft.address, tokenId, _from(accounts[1]))
	
	with brownie.reverts("Not the owner of NFT"):
		staking.unstakeNft(1, {"from": accounts[2]})


def test_nft_unstake(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles
	
	account = accounts[8]

	tokenId = nft.mintNft(_from(account)).return_value
	nft.approve(staking.address, tokenId, _from(account))
	
	staking.stakeNft(nft.address, tokenId, _from(account))
	
	assert nft.balanceOf(account) == 0
	assert nft.balanceOf(staking) == 1

	staking.unstakeNft(1, _from(account))

	assert nft.balanceOf(account) == 1
	assert nft.balanceOf(staking) == 0
