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

def test_wp_h1(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	zooToken.approve(listing, 10**20)
	listing.voteForNftCollection(nft, 10**20)
	chain.sleep(arena.epochDuration() + 1)
	arena.updateEpoch()
	# Now is epoch 2

	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	create_voting_position(voting, daiToken, accounts[1], 1, 10**20)
	create_voting_position(voting, daiToken, accounts[1], 2, 10**20)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration()) # skip 1 stage
	# Waiting for third stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage

	arena.pairNft(1)

	# Waiting for fourth stage
	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.
	# Waiting for fifth stage
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	assert arena.getCurrentStage() == 2
	additionalDai = 10**20
	daiToken.approve(voting, additionalDai, _from(accounts[1]))
	voting.addDaiToPosition(1, additionalDai, _from(accounts[1]))

	arena.requestRandom()
	vault.increaseMockBalance()
	tx2 = arena.chooseWinnerInPair(0)

	chain.sleep(arena.fifthStageDuration()) # skip 5 stage.

	arena.updateEpoch()
	# Now is epoch 3

	reward2 = arena.calculateIncentiveRewardForVoter.call(1, {"from": voting})
	assert reward2 > 0
	assert arena.baseVoterReward() // 2 == reward2

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration()) # skip 1 stage
	# Waiting for third stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage

	arena.pairNft(1)

	# Waiting for fourth stage
	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.
	# Waiting for fifth stage
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	arena.requestRandom()
	vault.increaseMockBalance()
	tx3 = arena.chooseWinnerInPair(0)

	chain.sleep(arena.fifthStageDuration()) # skip 5 stage.

	arena.updateEpoch()
	# Now is epoch 4
	reward23 = arena.calculateIncentiveRewardForVoter.call(1, {"from": voting})
	assert reward23 > reward2
	assert arena.baseVoterReward() / (reward23 - reward2) == 1.5

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration()) # skip 1 stage
	# Waiting for third stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage

	arena.pairNft(1)

	# Waiting for fourth stage
	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.
	# Waiting for fifth stage
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	arena.requestRandom()
	vault.increaseMockBalance()
	tx4 = arena.chooseWinnerInPair(0)

	chain.sleep(arena.fifthStageDuration()) # skip 5 stage.

	arena.updateEpoch()
	# Now is epoch 5

	reward234 = arena.calculateIncentiveRewardForVoter.call(1, {"from": voting})

	assert reward234 > reward23
	assert reward234 - reward23 == reward23 - reward2 # Rewards for epoch 3 and 4 must be equal.
