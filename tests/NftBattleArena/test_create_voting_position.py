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


def test_only_voting_can_call(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	staking_position_id = 1
	dai_amount = 10e18

	with brownie.reverts():
		arena.createVotingPosition(staking_position_id, accounts[0], dai_amount, _from(accounts[0]))

	tx = create_voting_position(voting, daiToken, accounts[2], staking_position_id, dai_amount)
	assert tx.status == 1


def test_creating_new_position(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	tx = create_voting_position(voting, daiToken, accounts[2], 1, 10e18)
	assert tx.status == 1


def test_dai_transfer(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	balance_before = daiToken.balanceOf(accounts[1], _from(accounts[1]))

	stake_nft(staking, accounts[1], nft, 4)

	vault_balance = daiToken.balanceOf(vault)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	daiAmountToVote = 10e18
	create_voting_position(voting, daiToken, accounts[2], 1, daiAmountToVote)

	assert daiToken.balanceOf(accounts[2], _from(accounts[2])) == balance_before - daiAmountToVote
	assert daiToken.balanceOf(vault, _from(accounts[2])) == vault_balance + daiAmountToVote


def test_insufficient_funds(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	# More than account have
	daiAmountToVote = 5e25
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	with brownie.reverts("Dai/insufficient-balance"):
		voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))


def test_nft_mint(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	create_voting_position(voting, daiToken, accounts[2], 1, 10e18)

	assert voting.balanceOf(accounts[2], _from(accounts[2])) == 1
	assert voting.ownerOf(1, _from(accounts[2])) == accounts[2]


def test_non_existing_staking_id(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	with brownie.reverts("E1"):
		voting.createNewVotingPosition(123, daiAmountToVote, True, _from(accounts[1]))


def test_unstaked_nft(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	staking.unstakeNft(1, _from(accounts[1]))

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	with brownie.reverts("E1"):
		voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))


# test for numberOfNftsWithNonZeroVotesPending
def test_numberOfNftsWithNonZeroVotesPending_case_1(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	# two nft
	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	# voted in current epoch
	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))
	voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))
	voting.createNewVotingPosition(2, daiAmountToVote, True, _from(accounts[1]))

	assert arena.votingPositionsValues(1)[1] == 10e18
	assert arena.pendingVotesEpoch(1) == 0
	assert arena.pendingVotes(1) == 0
	assert arena.rewardsForEpoch(1,1)[1] == 13e18 # current epoch
	assert arena.rewardsForEpoch(1,2)[1] == 0 # next epoch

	assert arena.numberOfNftsWithNonZeroVotes() == 2
	assert arena.numberOfNftsWithNonZeroVotesPending() == 0

	# Waiting for third stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage
	arena.pairNft(1)
	# Waiting for fourth stage
	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.
	# Waiting for fifth stage
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	# voted for next epoch
	additionalDai = 20e18
	daiToken.approve(voting, additionalDai, _from(accounts[1]))
	voting.createNewVotingPosition(1, daiAmountToVote, True, _from(accounts[1]))
	daiToken.approve(voting, additionalDai, _from(accounts[1]))
	voting.createNewVotingPosition(2, daiAmountToVote, True, _from(accounts[1]))

	assert arena.numberOfNftsWithNonZeroVotes() == 2 # still the same
	assert arena.numberOfNftsWithNonZeroVotesPending() == 0 # still zero.

def test_numberOfNftsWithNonZeroVotesPending_case_2(accounts, tokens, battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	# two nft
	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)

	# no votes in current epoch.

	# Waiting for second stage
	chain.sleep(arena.firstStageDuration())

	assert arena.numberOfNftsWithNonZeroVotes() == 0
	assert arena.numberOfNftsWithNonZeroVotesPending() == 0

	# Waiting for third stage
	chain.sleep(arena.secondStageDuration()) # skip 2 stage
	# Waiting for fourth stage
	chain.sleep(arena.thirdStageDuration()) # skip 3 stage.
	# Waiting for fifth stage
	chain.sleep(arena.fourthStageDuration()) # skip 4 stage.

	# vote for next epoch
	additionalDai = 20e18
	daiToken.approve(voting, additionalDai, _from(accounts[1]))
	voting.createNewVotingPosition(1, additionalDai, True, _from(accounts[1]))

	# twice for one position
	daiToken.approve(voting, additionalDai, _from(accounts[2]))
	voting.createNewVotingPosition(2, additionalDai, True, _from(accounts[2]))
	daiToken.approve(voting, additionalDai, _from(accounts[2]))
	voting.createNewVotingPosition(2, additionalDai, True, _from(accounts[2]))

	assert arena.votingPositionsValues(1)[1] == additionalDai
	assert arena.pendingVotesEpoch(1) == 1
	assert arena.pendingVotes(1) == 26000000000000000000
	assert arena.rewardsForEpoch(1,1)[1] == 0 # current epoch
	assert arena.rewardsForEpoch(1,2)[1] == 26000000000000000000 # next epoch

	assert arena.numberOfNftsWithNonZeroVotes() == 0 # zero cause its for next epoch.
	assert arena.numberOfNftsWithNonZeroVotesPending() == 2 # pending for next epoch.

	chain.sleep(arena.fifthStageDuration()) # skip 4 stage.
	arena.updateEpoch() # update epoch increases numberOfNftsWithNonZeroVotes from pending.
	# now epoch 2.

	assert arena.numberOfNftsWithNonZeroVotes() == 2 # number == actual amount of non zero positions
	assert arena.numberOfNftsWithNonZeroVotesPending() == 0


def test_recording_new_voting_values(accounts, second_stage):
	(zooToken, daiToken, linkToken, nft) = second_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = second_stage[1]

	daiAmountToVote = 20e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	stakingPositionId = 1
	daiVoted = daiAmountToVote / 2
	voting.createNewVotingPosition(stakingPositionId, daiVoted, True, _from(accounts[1]))
	votingValues = arena.votingPositionsValues(1)

	assert votingValues["stakingPositionId"] == stakingPositionId
	#assert votingValues["startDate"] < chain.time() + 5 and votingValues["startDate"] > chain.time() - 5
	assert votingValues["daiInvested"] == daiVoted
	assert abs(arena.sharesToTokens.call(votingValues["yTokensNumber"]) - daiVoted) < 10
	assert votingValues["daiVotes"] == functions.computeVotesByDai(daiVoted)
	assert votingValues["votes"] == functions.computeVotesByDai(daiVoted)
	assert votingValues["startEpoch"] == arena.currentEpoch()
	assert votingValues["lastRewardedEpoch"] == arena.currentEpoch()


	stakingPositionId = 2
	voting.createNewVotingPosition(stakingPositionId, daiVoted, True, _from(accounts[1]))

	votingValues = arena.votingPositionsValues(2)

	assert votingValues["stakingPositionId"] == stakingPositionId
	#assert votingValues["startDate"] < chain.time() + 5 and votingValues["startDate"] > chain.time() - 5
	assert votingValues["daiInvested"] == daiVoted
	assert votingValues["yTokensNumber"] == arena.tokensToShares.call(daiVoted)
	assert votingValues["daiVotes"] == functions.computeVotesByDai(daiVoted)
	assert votingValues["votes"] == functions.computeVotesByDai(daiVoted)
	assert votingValues["startEpoch"] == arena.currentEpoch()
	assert votingValues["lastRewardedEpoch"] == arena.currentEpoch()


def test_recording_battle_reward(accounts, second_stage):
	(zooToken, daiToken, linkToken, nft) = second_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = second_stage[1]

	daiAmountToVote = 20e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	stakingPositionId = 1
	daiVoted = daiAmountToVote / 2
	voting.createNewVotingPosition(stakingPositionId, daiVoted, True, _from(accounts[1]))
	votingValues = arena.votingPositionsValues(1)

	epoch = arena.currentEpoch()
	reward = arena.rewardsForEpoch(stakingPositionId, epoch)

	assert abs(arena.sharesToTokens.call(reward["yTokens"]) - daiVoted) < 10
	assert reward["votes"] == functions.computeVotesByDai(daiVoted)

	stakingPositionId = 2
	voting.createNewVotingPosition(stakingPositionId, daiVoted, True, _from(accounts[1]))

	epoch = arena.currentEpoch()
	reward = arena.rewardsForEpoch(stakingPositionId, epoch)

	assert reward["yTokens"] == arena.tokensToShares.call(daiVoted)
	assert reward["votes"] == functions.computeVotesByDai(daiVoted)


def test_incrementing_number_of_nfts_with_non_zero_votes(accounts, second_stage):
	(zooToken, daiToken, linkToken, nft) = second_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = second_stage[1]

	numberOfNftsWithNonZeroVotes = arena.numberOfNftsWithNonZeroVotes()

	daiAmountToVote = 20e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	stakingPositionId = 1
	daiVoted = daiAmountToVote / 2
	voting.createNewVotingPosition(stakingPositionId, daiVoted, True, _from(accounts[1]))

	assert arena.numberOfNftsWithNonZeroVotes() == numberOfNftsWithNonZeroVotes + 1

	stakingPositionId = 2
	voting.createNewVotingPosition(stakingPositionId, daiVoted, True, _from(accounts[1]))

	assert arena.numberOfNftsWithNonZeroVotes() == numberOfNftsWithNonZeroVotes + 2


def test_emitting_event(accounts, second_stage):
	(zooToken, daiToken, linkToken, nft) = second_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = second_stage[1]

	daiAmountToVote = 10e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	stakingPositionId = 1
	tx = voting.createNewVotingPosition(stakingPositionId, daiAmountToVote, True, _from(accounts[1]))

	event = tx.events["CreatedVotingPosition"]
	assert event["currentEpoch"] == arena.currentEpoch()
	assert event["voter"] == accounts[1]
	assert event["stakingPositionId"] == stakingPositionId
	assert event["daiAmount"] == daiAmountToVote
	assert event["votes"] == daiAmountToVote * 1.3
	assert event["votingPositionId"] == 1

# vote for next season new mapping tests #
def test_new_mappings_and_values(accounts, fourth_stage):
	(zooToken, daiToken, linkToken, nft) = fourth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fourth_stage[1]

	daiAmountToVote = 20e18
	daiToken.approve(voting, daiAmountToVote, _from(accounts[1]))

	stakingPositionId = 1
	daiVoted = 10e18

	voting.createNewVotingPosition(stakingPositionId, daiVoted, True, _from(accounts[1]))

	votingValues = arena.votingPositionsValues(11)

	assert votingValues["stakingPositionId"] == stakingPositionId
	assert votingValues["daiInvested"] == daiVoted
	assert votingValues["daiVotes"] == 0
	assert votingValues["votes"] == 0
	assert votingValues["startEpoch"] == arena.currentEpoch() + 1
	assert votingValues["lastRewardedEpoch"] == arena.currentEpoch() + 1

	assert arena.pendingVotesEpoch(11) == arena.currentEpoch()
	assert arena.pendingVotes(11) == daiVoted * 1.3


# tests for league #
def test_league_sets_correctly(accounts, fourth_stage):
	(zooToken, daiToken, linkToken, nft) = fourth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fourth_stage[1]

	daiApprove = 400000e18
	daiToken.approve(voting, daiApprove, _from(accounts[1])) # approve a lot.
	stakingPositionId = 1

	# note that position already have 130 votes.
	assert arena.rewardsForEpoch(stakingPositionId, 1)["votes"] == 130000000000000000000 # votes epoch 1 before
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] == 0 # votes epoch 2 before

	# since this vote in fourth stage, votes come to next epoch.
	# wooden
	voting.createNewVotingPosition(stakingPositionId, 370e18, True, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 1)["votes"] == 130000000000000000000 # same
	# note that votes from previous epochs will be updated only in next epoch. So its only from this voting.
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] == 481e18 # 370 * 1.3
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 1 # league 1

	# bronze
	voting.createNewVotingPosition(stakingPositionId, 1553e18, True, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 2500e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 2
	# silver
	voting.createNewVotingPosition(stakingPositionId, 3846e18, True, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 7500e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 3
	# golden
	voting.createNewVotingPosition(stakingPositionId, 17307e18, True, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 30000e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 4
	# platinum
	voting.createNewVotingPosition(stakingPositionId, 92307e18, True, _from(accounts[1]))
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] <= 150000e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 5
	# master
	voting.createNewVotingPosition(stakingPositionId, 1000e18, True, _from(accounts[1])) # we up to limit of 150k so almost any amount.
	assert arena.rewardsForEpoch(stakingPositionId, 2)["votes"] > 150000e18
	assert arena.rewardsForEpoch(stakingPositionId, 2)["league"] == 5