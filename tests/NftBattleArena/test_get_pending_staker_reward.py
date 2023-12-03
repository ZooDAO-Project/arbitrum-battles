import brownie
from brownie import chain

from _utils.utils import play_all_pairs


#
# Utility functions
#
# has _ before name because from is internal reserved word
def _from(account):
	return {"from": account}


def stake_nft(staking, account, nft, tokenId):
	nft.approve(staking.address, tokenId, _from(account))

	return staking.stakeNft(nft.address, tokenId, _from(account))


def test_null_reward_if_no_votes(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	stake_nft(staking, accounts[1], nft, 6)

	(reward, end) = arena.getPendingStakerReward(1)
	assert reward == 0
	assert end == 1

	(reward, end) = arena.getPendingStakerReward(2)
	assert reward == 0
	assert end == 1

	(reward, end) = arena.getPendingStakerReward(3)
	assert reward == 0
	assert end == 1


def test_reward_calculation_after_votes(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	stake_nft(staking, accounts[1], nft, 6)

	chain.sleep(arena.firstStageDuration())

	daiToken.approve(voting, 300e18, _from(accounts[0]))
	# checking i < numberOfNftsWithNonZeroVotes
	voting.createNewVotingPosition(1, 10e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(2, 25e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(3, 230e18, True, _from(accounts[0]))

	(reward, end) = arena.getPendingStakerReward(1)
	assert reward == 0

	(reward, end) = arena.getPendingStakerReward(2)
	assert reward == 0

	(reward, end) = arena.getPendingStakerReward(3)
	assert reward == 0


def test_reward_calculation_after_choosing_winner(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	current_epoch = arena.currentEpoch()
	next_epoch = current_epoch + 1

	pair_index = 0
	pair = arena.pairsInEpoch(current_epoch, pair_index)

	fighter1 = pair['token1']
	fighter2 = pair['token2']

	reward1 = arena.rewardsForEpoch(fighter1, current_epoch)
	reward2 = arena.rewardsForEpoch(fighter2, current_epoch)

	assert abs(arena.sharesToTokens.call(reward1['yTokens']) - 100e18) < 10
	assert abs(arena.sharesToTokens.call(reward2['yTokens']) - 100e18) < 10


	arena.requestRandom()
	vault.increaseMockBalance()
	arena.chooseWinnerInPair(pair_index)


	play_all_pairs(arena)

	chain.sleep(arena.fifthStageDuration())
	arena.updateEpoch()


	# Update pair after playing a game
	pair = arena.pairsInEpoch(current_epoch, pair_index)

	winner = fighter1 if pair['win'] else fighter2
	loser = fighter2 if pair['win'] else fighter1 # Opposite condition of winner

	# Winner rewards
	reward = arena.rewardsForEpoch(winner, current_epoch)
	assert reward["yTokensSaldo"] == 9075641838

	reward = arena.rewardsForEpoch(winner, next_epoch)
	assert reward["yTokensSaldo"] == 0

	staking = arena.stakingPositionsValues(winner)
	print(staking['lastRewardedEpoch'])

	(reward, end) = arena.getPendingStakerReward(winner)
	assert reward == 94537935

	# Loser rewards
	reward = arena.rewardsForEpoch(loser, current_epoch)
	assert reward["yTokensSaldo"] == 0

	reward = arena.rewardsForEpoch(loser, next_epoch)
	assert reward["yTokensSaldo"] == 0

	(reward, end) = arena.getPendingStakerReward(loser)
	assert reward == 0



# def test_token_income_calculation(accounts, battles, tokens):
#     (vault, functions, governance, staking, voting, arena, listing) = battles
#     (zooToken, daiToken, linkToken, nft) = tokens

#

#     stake_nft(staking, accounts[1], nft, 4)
#     stake_nft(staking, accounts[1], nft, 5)
#     stake_nft(staking, accounts[1], nft, 6)

#     chain.sleep(arena.firstStageDuration())

#     daiToken.approve(voting, 300e18, _from(accounts[0]))
#     # checking i < numberOfNftsWithNonZeroVotes
#     voting.createNewVotingPosition(1, 10e18, _from(accounts[0]))
#     voting.createNewVotingPosition(2, 25e18, _from(accounts[0]))
#     voting.createNewVotingPosition(3, 230e18, _from(accounts[0]))

#     chain.sleep(arena.secondStageDuration())

#     tx = arena.pairNft(1)
#     pairIndex = tx.events["PairedNft"]["pairIndex"]

#     chain.sleep(arena.thirdStageDuration())
#     chain.sleep(arena.fourthStageDuration())

#     # Transfer to vault to make rewards from battle
#     vault.IncreaseMockBalance(_from(accounts[0]))

#     assert arena.rewardsForEpoch(1, 1)["yTokens"] == 10e18
#     assert arena.rewardsForEpoch(2, 1)["yTokens"] == 25e18

#     tx = arena.chooseWinnerInPair(pairIndex)
#     event = tx.events["ChosenWinner"]
#     assert event != None

#     event = tx.events["EpochUpdated"]
#     assert event != None
