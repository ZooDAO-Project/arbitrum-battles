import brownie
from brownie import chain

def _from(account):
	return {"from": account}

def test_updateVotingPosition_and_pendingVotes_works_correct(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	nft.approve(staking.address, 1, _from(accounts[0])) # staking
	staking.stakeNft(nft.address, 1, _from(accounts[0]))
	nft.approve(staking.address, 2, _from(accounts[0]))
	staking.stakeNft(nft.address, 2, _from(accounts[0]))

	daiToken.approve(voting, 200e18, _from(accounts[1]))
	voting.createNewVotingPosition(1, 200e18, True, _from(accounts[1])) # voting
	daiToken.approve(voting, 100e18, _from(accounts[1]))
	voting.createNewVotingPosition(2, 100e18, True, _from(accounts[1]))

	chain.sleep(arena.firstStageDuration()) # skip stages
	chain.sleep(arena.secondStageDuration())

	arena.pairNft(1, _from(accounts[1])) # pair for 1 position.
	# print("after pairing 1st epoch")

	assert arena.votingPositionsValues(1)[1] == 200000000000000000000
	assert arena.votingPositionsValues(2)[1] == 100000000000000000000
	# print("1 position, 1 epoch, votingPositionsValues", arena.votingPositionsValues(1))
	# print("2 position, 1 epoch, votingPositionsValues", arena.votingPositionsValues(2))

	assert arena.rewardsForEpoch(1,1)[1] == 260000000000000000000
	assert arena.rewardsForEpoch(2,1)[1] == 130000000000000000000
	# print("1 position, 1 epoch, rewardsForEpoch", arena.rewardsForEpoch(1,1))
	# print("2 position, 1 epoch, rewardsForEpoch", arena.rewardsForEpoch(2,1))

	chain.sleep(arena.thirdStageDuration()) # skip stages
	chain.sleep(arena.fourthStageDuration())

	assert arena.stakingPositionsValues(1)["lastUpdateEpoch"] == 1
	assert arena.computeLastEpoch(1) == 1
	# print("lastUpdateEpoch", arena.stakingPositionsValues(1)["lastUpdateEpoch"])
	# print("computeLastEpoch", arena.computeLastEpoch(1))

	daiToken.approve(voting, 100e18, _from(accounts[1]))
	voting.addDaiToPosition(1, 100e18, _from(accounts[1]))
	# print("_____________________________________________")
	# print("after addDai")

	assert arena.stakingPositionsValues(1)["lastUpdateEpoch"] == 1
	assert arena.computeLastEpoch(1) == 1

	assert arena.rewardsForEpoch(1,1)[1] == 260000000000000000000
	assert arena.rewardsForEpoch(2,1)[1] == 130000000000000000000
	assert arena.rewardsForEpoch(1,2)[1] == 130000000000000000000
	assert arena.rewardsForEpoch(2,2)[1] == 0

	# print("lastUpdateEpoch", arena.stakingPositionsValues(1)["lastUpdateEpoch"])
	# print("pending votes", arena.pendingVotes(1))
	# print("pending votes epoch", arena.pendingVotesEpoch(1))

	# print("1 position, 1 epoch, rewardsForEpoch", arena.rewardsForEpoch(1,1))
	# print("2 position, 1 epoch, rewardsForEpoch", arena.rewardsForEpoch(2,1))

	# print("1 position, 2 epoch, rewardsForEpoch", arena.rewardsForEpoch(1,2))
	# print("2 position, 2 epoch, rewardsForEpoch", arena.rewardsForEpoch(2,2))

	# print("pending reward 1 position", arena.getPendingVoterReward(1))
	# print("pending reward 2 position", arena.getPendingVoterReward(2))

	arena.requestRandom()
	arena.chooseWinnerInPair(0, _from(accounts[1])) # pair index
	# print("_____________________________________________")
	# print("after choose winner")

	assert arena.rewardsForEpoch(1,2)[1] == 390000000000000000000
	assert arena.rewardsForEpoch(2,2)[1] == 130000000000000000000

	# print("computeLastEpoch", arena.computeLastEpoch(1))
	# print("lastUpdateEpoch", arena.stakingPositionsValues(1)["lastUpdateEpoch"])
	# print("1 position, 1 epoch, rewardsForEpoch", arena.rewardsForEpoch(1,1))
	# print("2 position, 1 epoch, rewardsForEpoch", arena.rewardsForEpoch(2,1))

	# print("1 position, 2 epoch, rewardsForEpoch", arena.rewardsForEpoch(1,2))
	# print("2 position, 2 epoch, rewardsForEpoch", arena.rewardsForEpoch(2,2))

	assert arena.getPendingVoterReward(1) == (1, 0) # 1st position wins most of the times.
	assert arena.getPendingVoterReward(2) == (0, 0)
	# print("pending reward 1 position", arena.getPendingVoterReward(1))
	# print("pending reward 2 position", arena.getPendingVoterReward(2))


	voting.claimRewardFromVoting(1, accounts[1], _from(accounts[1]))
	voting.claimRewardFromVoting(2, accounts[1], _from(accounts[1]))
	# print("_____________________________________________")
	# print("after claim reward")

	assert arena.stakingPositionsValues(1)["lastUpdateEpoch"] == 2
	assert arena.computeLastEpoch(1) == 2

	assert arena.getPendingVoterReward(1) == (0, 0)
	assert arena.getPendingVoterReward(2) == (0, 0)

	assert arena.rewardsForEpoch(1,2)[1] == 390000000000000000000
	assert arena.rewardsForEpoch(2,2)[1] == 130000000000000000000

	assert arena.pendingVotesEpoch(1) == 1
	assert arena.pendingVotes(1) == 130000000000000000000

	assert arena.votingPositionsValues(1)[1] == 300000000000000000000
	assert arena.votingPositionsValues(2)[1] == 100000000000000000000

	# print("computeLastEpoch", arena.computeLastEpoch(1))
	# print("lastUpdateEpoch", arena.computeLastEpoch(1))
	# print("pending reward 1 position", arena.getPendingVoterReward(1))
	# print("pending reward 2 position", arena.getPendingVoterReward(2))

	# print("1 position, 1 epoch, rewardsForEpoch", arena.rewardsForEpoch(1,1))
	# print("2 position, 1 epoch, rewardsForEpoch", arena.rewardsForEpoch(2,1))

	# print("1 position, 2 epoch, rewardsForEpoch", arena.rewardsForEpoch(1,2))
	# print("2 position, 2 epoch, rewardsForEpoch", arena.rewardsForEpoch(2,2))

	# print("pending votes", arena.pendingVotes(1))
	# print("pending votes epoch", arena.pendingVotesEpoch(1))
	# print("1 position, 2 epoch, votingPositionsValues", arena.votingPositionsValues(1))
	# print("2 position, 2 epoch, votingPositionsValues", arena.votingPositionsValues(2))

	chain.sleep(arena.firstStageDuration())
	chain.sleep(arena.secondStageDuration())

	arena.pairNft(1, _from(accounts[1])) # pair for 1 position.

	assert arena.rewardsForEpoch(1,2)[1] == 390000000000000000000
	assert arena.rewardsForEpoch(2,2)[1] == 130000000000000000000
	# print("_____________________________________________")
	# print("after pairing")

	# print("1 position, 2 epoch, rewardsForEpoch", arena.rewardsForEpoch(1,2))
	# print("2 position, 2 epoch, rewardsForEpoch", arena.rewardsForEpoch(2,2))

