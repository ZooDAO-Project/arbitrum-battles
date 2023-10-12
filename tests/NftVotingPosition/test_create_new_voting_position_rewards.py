import brownie
from brownie import chain


#
# Utility functions
#
# has _ before name because from is internal reserved word
def _from(account):
	return {"from": account}


def stake_nft(staking, account, nft, tokenId):
	nft.approve(staking.address, tokenId, _from(account))

	staking.stakeNft(nft.address, tokenId, _from(account))


def create_voting_position(voting, daiToken, account, stakingPositionId, daiAmount):
	daiToken.approve(voting, daiAmount, _from(account))

	return voting.createNewVotingPosition(stakingPositionId, daiAmount, True, _from(account))

# End of utility functions

def test_numberOfNftsWithNonZeroVotes(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	
	tokenId = nft.mintNft({"from": accounts[1]}).return_value
	nft.approve(staking.address, tokenId, {"from": accounts[1]})

	staking.stakeNft(nft.address, tokenId, {"from": accounts[1]})
	
	
	tokenId = nft.mintNft({"from": accounts[2]}).return_value
	nft.approve(staking.address, tokenId, {"from": accounts[2]})

	staking.stakeNft(nft.address, tokenId, {"from": accounts[2]})

	
	tokenId = nft.mintNft({"from": accounts[3]}).return_value
	nft.approve(staking.address, tokenId, {"from": accounts[3]})

	staking.stakeNft(nft.address, tokenId, {"from": accounts[3]})

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))
	voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))
	voting.createNewVotingPosition(2, daiAmountToVote, True, _from(accounts[1]))

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))
	voting.createNewVotingPosition(3, daiAmountToVote, True, _from(accounts[1]))

	assert arena.numberOfNftsWithNonZeroVotes() == 3

	staking.unstakeNft(1, _from(accounts[1]))

	assert arena.numberOfNftsWithNonZeroVotes() == 2
	assert arena.getStakerPositionsLength() == 2



