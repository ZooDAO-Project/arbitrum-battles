import brownie
from brownie import chain


def _from(account):
	return {"from": account}


def test_get_pending_voter_reward(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	nft.approve(staking.address, 1, _from(accounts[0]))
	staking.stakeNft(nft.address, 1, _from(accounts[0]))
	nft.approve(staking.address, 2, _from(accounts[0]))
	staking.stakeNft(nft.address, 2, _from(accounts[0]))

	daiToken.approve(voting, 200e18, _from(accounts[1]))
	voting.createNewVotingPosition(1, 200e18, True, _from(accounts[1]))
	daiToken.approve(voting, 100e18, _from(accounts[1]))
	voting.createNewVotingPosition(2, 100e18, True, _from(accounts[1]))

	chain.sleep(arena.firstStageDuration())
	chain.sleep(arena.secondStageDuration())

	arena.pairNft(1, _from(accounts[1])) # pair for 1 position.

	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())

	daiToken.approve(voting, 1000e18, _from(accounts[1]))
	voting.addDaiToPosition(1, 1000e18, _from(accounts[1])) # needs to create non zero saldo.

	arena.requestRandom()
	arena.chooseWinnerInPair(0, _from(accounts[1])) # pair index, from

	assert arena.getPendingVoterReward(1)[0] or arena.getPendingVoterReward(2)[0] == 1 or 2

	voting.claimRewardFromVoting(1, accounts[1], _from(accounts[1]))
	voting.claimRewardFromVoting(2, accounts[1], _from(accounts[1]))

	assert arena.getPendingVoterReward(1)[0] == 0 and arena.getPendingVoterReward(2)[0] == 0



