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

def skip_epoch(arena, vault, staking_position_id):
	chain.sleep(arena.firstStageDuration()) # skip 1 stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage

	arena.pairNft(staking_position_id)

	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	arena.requestRandom()
	vault.increaseMockBalance()
	tx3 = arena.chooseWinnerInPair(0)

	chain.sleep(arena.fifthStageDuration()) # skip 5 stage.

	arena.updateEpoch()


# End of utility functions

def test_wp_m5(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	zooToken.approve(listing, 10**20)
	listing.voteForNftCollection(nft, 10**20)
	chain.sleep(arena.epochDuration() + 1)
	arena.updateEpoch()
	# Now is epoch 2

	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	create_voting_position(voting, daiToken, accounts[2], 1, 100e18) # Alice's opponent.

	chain.sleep(arena.firstStageDuration())
	chain.sleep(arena.secondStageDuration() * 2 // 3 + 1)
	# Now is last 1/3 duration of stage 2 of epoch 2
	create_voting_position(voting, daiToken, accounts[1], 2, 100e18) # Alice vote with 100 stablecoins.
	chain.sleep(arena.secondStageDuration() // 3 + 1)
	chain.mine()
	
	assert arena.getCurrentStage() == 2 # Now must be stage 3
	votes = arena.votingPositionsValues(2)["votes"]
	assert votes == 70e18

	arena.pairNft(2)

	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	arena.requestRandom()
	vault.increaseMockBalance()
	tx2 = arena.chooseWinnerInPair(0)

	chain.sleep(arena.fifthStageDuration()) # skip 5 stage.

	arena.updateEpoch()
	# Now is epoch 3

	reward2 = arena.calculateIncentiveRewardForVoter.call(2, {"from": voting})

	skip_epoch(arena, vault, 2)
	# Now is epoch 4

	reward23 = arena.calculateIncentiveRewardForVoter.call(2, {"from": voting})
	assert reward23 // 2 == reward2

	chain.sleep(arena.firstStageDuration()) # skip 1 stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage

	arena.pairNft(2)

	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.
	chain.mine()
	assert arena.getCurrentStage() == 3 # stage 4 of epoch 4

	daiToken.approve(voting, 100e18)
	voting.addDaiToPosition(2, 100e18, {"from": accounts[0]})

	assert arena.pendingVotesEpoch(2) == 5 # That value was fixed.
	assert arena.votingPositionsValues(2)["lastEpochOfIncentiveReward"] == 4

	chain.sleep(arena.fourthStageDuration())

	arena.requestRandom()
	vault.increaseMockBalance()
	tx3 = arena.chooseWinnerInPair(0)

	chain.sleep(arena.fifthStageDuration()) # skip 5 stage.

	arena.updateEpoch()
	# Now is epoch 5

	reward234 = arena.calculateIncentiveRewardForVoter.call(2, {"from": voting})
	assert reward234 // 3 == reward2 == reward234 - reward23

	skip_epoch(arena, vault, 2)
	# Now is epoch 6

	reward2345 = arena.calculateIncentiveRewardForVoter.call(2, {"from": voting})
	assert reward2345 - reward234 > reward2

	skip_epoch(arena, vault, 2)
	# Now is epoch 7

	reward23456 = arena.calculateIncentiveRewardForVoter.call(2, {"from": voting})
	assert reward23456 - reward2345 == reward2345 - reward234

	skip_epoch(arena, vault, 2)
	# Now is epoch 8

	reward234567 = arena.calculateIncentiveRewardForVoter.call(2, {"from": voting})
	assert reward234567 - reward23456 == reward23456 - reward2345

	assert arena.computeLastEpoch(2) == 8
	assert arena.votingPositionsValues(2)["lastEpochOfIncentiveReward"] == 4
	arena.recomputeDaiVotes(2)
	assert arena.computeLastEpoch(2) == 8
	assert arena.votingPositionsValues(2)["votes"] == 260e18
	assert arena.votingPositionsValues(2)["lastEpochOfIncentiveReward"] == 8

	skip_epoch(arena, vault, 2)
	# Now is epoch 9

	reward2345678 = arena.calculateIncentiveRewardForVoter.call(2, {"from": voting})
	assert reward2345678 - reward234567 > reward234567 - reward23456

	skip_epoch(arena, vault, 2)
	# Now is epoch 10

	reward23456789 = arena.calculateIncentiveRewardForVoter.call(2, {"from": voting})
	assert reward23456789 - reward2345678 == reward2345678 - reward234567