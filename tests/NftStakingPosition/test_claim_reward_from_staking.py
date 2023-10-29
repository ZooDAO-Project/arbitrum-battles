import brownie


def test_claim_reward_from_not_owner(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	tokenId = nft.mintNft({"from": accounts[1]}).return_value
	nft.approve(staking.address, tokenId, {"from": accounts[1]})
	
	staking.stakeNft(nft.address, tokenId, {"from": accounts[1]})
	stakingPositionId = 1

	with brownie.reverts("Not the owner of NFT"):
		staking.claimRewardFromStaking(stakingPositionId, accounts[2], {"from": accounts[2]})


def test_emitting_event(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	tokenId = nft.mintNft({"from": accounts[1]}).return_value
	nft.approve(staking.address, tokenId, {"from": accounts[1]})

	
	staking.stakeNft(nft.address, tokenId, {"from": accounts[1]})
	stakingPositionId = 1

	staking.claimRewardFromStaking(stakingPositionId, accounts[1], {"from": accounts[1]})

def test_batch_claim_reward_from_staking(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	staking.stakeNft(nft.address, tokenId, {"from": accounts[1]})
	stakingPositionId = 1

	staking.batchClaimRewardFromStaking([stakingPositionId], accounts[1], {"from": accounts[1]})
