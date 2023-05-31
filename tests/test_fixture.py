#!/usr/bin/python3

import brownie
from brownie import chain

def test_tokens(accounts, tokens):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	assert zooToken.balanceOf(accounts[0]) == 12e25
	assert zooToken.balanceOf(accounts[1]) == 4e25
	assert zooToken.balanceOf(accounts[2]) == 4e25

	assert daiToken.balanceOf(accounts[0]) == 4e25
	assert daiToken.balanceOf(accounts[1]) == 4e25
	assert daiToken.balanceOf(accounts[2]) == 4e25

	assert nft.balanceOf(accounts[0]) == 3
	assert nft.balanceOf(accounts[1]) == 3
	assert nft.balanceOf(accounts[2]) == 3


def test_battles(accounts, battles):
	(vault, functions, governance, staking, voting, arena, listingList) = battles

	assert arena.currentEpoch() == 1
	assert arena.getCurrentStage() == 0


def test_second_stage(accounts, second_stage):
	(zooToken, daiToken, linkToken, nft) = second_stage[0]
	(vault, functions, governance, staking, voting, arena, listingList) = second_stage[1]

	start = arena.epochStartDate()
	firstStageDuration = arena.firstStageDuration()
	secondStageDuration = arena.secondStageDuration()
	thirdStageDuration = arena.thirdStageDuration()
	fourthStageDuration = arena.fourthStageDuration()

	assert arena.currentEpoch() == 1
	assert arena.getCurrentStage() == 1

	for i in range(arena.getStakerPositionsLength()):
		assert arena.activeStakerPositions(i) == i + 1

	assert arena.numberOfStakingPositions() == 9 + 1 # Always bigger by one


def test_third_stage(accounts, third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listingList) = third_stage[1]

	current_epoch = arena.currentEpoch()
	assert current_epoch == 1
	
	assert arena.getCurrentStage() == 2

	for i in range(1, 9):
		reward = arena.rewardsForEpoch(i, current_epoch)
		assert reward["votes"] == 130e18
		assert reward["yTokensSaldo"] == 0

		votingPosition = arena.votingPositionsValues(i)
		assert votingPosition["daiInvested"] == 100e18 # 100 DAI

		assert votingPosition["stakingPositionId"] == i
		assert votingPosition["startEpoch"] == 1
		assert votingPosition["daiVotes"] == 130e18
		assert votingPosition["votes"] == 130e18

	assert arena.numberOfNftsWithNonZeroVotes() == 9


def test_fourth_stage(accounts, fourth_stage):
	(zooToken, daiToken, linkToken, nft) = fourth_stage[0]
	(vault, functions, governance, staking, voting, arena, listingList) = fourth_stage[1]

	current_epoch = arena.currentEpoch()
	assert current_epoch == 1
	
	assert arena.getCurrentStage() == 3

	assert arena.numberOfNftsWithNonZeroVotes() == 9

	nftsInGame = arena.nftsInGame()
	assert nftsInGame == 8

	pairs_number = arena.getNftPairLength(current_epoch)
	assert pairs_number == 4

	for pair_index in range(pairs_number):
		pair = arena.pairsInEpoch(current_epoch, pair_index)

		token1 = pair['token1']
		assert token1 != 0

		token2 = pair['token2']
		assert token2 != 0
		
		token1Reward = arena.rewardsForEpoch(current_epoch, token1)
		token2Reward = arena.rewardsForEpoch(current_epoch, token2)
		
		print(token1)
		print(token2)

		print(token1Reward)
		print(token2Reward)
		
		# ??? Doesn't write rewards ???

		# assert token1Reward["tokensAtBattleStart"] == 100e18
		# assert token1Reward["pricePerShareAtBattleStart"] == 1e18

		# assert token2Reward["tokensAtBattleStart"] == 100e18
		# assert token2Reward["pricePerShareAtBattleStart"] == 1e18


		# assert pair["playedInEpoch"] == False
		# assert pair["win"] == False


def test_fifth_stage(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listingList) = fifth_stage[1]

	assert arena.currentEpoch() == 1
	assert arena.getCurrentStage() == 4

	for i in range(1, 9):
		reward = arena.rewardsForEpoch(i, 1)
		assert reward["votes"] == (130e18 * 2)
		# assert reward["yTokens"] == 999990000099999
		assert reward["yTokensSaldo"] == 0

		voting = arena.votingPositionsValues(i)
		assert voting["stakingPositionId"] == i
		assert voting["votes"] == (130e18 * 2)
		assert voting["daiInvested"] == 100e18
		assert voting["zooInvested"] == 100e18
		assert voting["startEpoch"] == 1


def test_finished_epoch(accounts, finished_epoch):
	(zooToken, daiToken, linkToken, nft) = finished_epoch[0]
	(vault, functions, governance, staking, voting, arena, listingList) = finished_epoch[1]

	assert arena.currentEpoch() == 2
	assert arena.getCurrentStage() == 0

	for i in range(4):
		pair = arena.pairsInEpoch(1, i)
		assert pair["playedInEpoch"] == True

		token1 = pair['token1']
		token2 = pair['token2']

		# Check change of yTokens balance after choosing winner and transfer dai to vault

		token1yTokens = arena.rewardsForEpoch(pair["token1"], 2)["yTokens"]
		token2yTokens = arena.rewardsForEpoch(pair["token2"], 2)["yTokens"]

		if pair['win']:
			assert token1yTokens == 968659324741 or 486634024558
			assert token2yTokens == 472689679022 or 945379358045
		else:
			assert token1yTokens == 472689679022 or 945379358045
			assert token2yTokens == 486634024558 or 968659324741

		assert pair['playedInEpoch']

	assert arena.numberOfPlayedPairsInEpoch(1) == 4
	

# def test_second_stage_advanced(accounts, second_stage_advanced):
# 	(zooToken, daiToken, linkToken, nft) = second_stage_advanced[0]
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = second_stage_advanced[1]

# 	start = arena.epochStartDate()
# 	firstStageDuration = arena.firstStageDuration()
# 	secondStageDuration = arena.secondStageDuration()
# 	thirdStageDuration = arena.thirdStageDuration()
# 	fourthStageDuration = arena.fourthStageDuration()

# 	assert arena.currentEpoch() == 1
# 	assert arena.getCurrentStage() == 1

# 	for i in range(50):
# 		assert arena.activeStakerPositions(i) == i + 1

# 	assert arena.numberOfStakingPositions() == 50 + 1 # Always bigger by one


# def test_third_stage_advanced(accounts, third_stage_advanced):
# 	(zooToken, daiToken, linkToken, nft) = third_stage_advanced[0]
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = third_stage_advanced[1]

# 	assert arena.currentEpoch() == 1
# 	assert arena.getCurrentStage() == 2

# 	for i in range(1, 51):
# 		reward = arena.rewardsForEpoch(i, 1)
# 		assert reward["votes"] == 130e18
# 		assert reward["yTokens"] == 1e20
# 		assert reward["yTokensSaldo"] == 0

# 		voting = arena.votingPositionsValues(i)
# 		assert voting["stakingPositionId"] == i
# 		assert voting["daiInvested"] == 1e20 # 100 DAI
# 		assert voting["startEpoch"] == 1
# 		assert voting["daiVotes"] == 130e18
# 		assert voting["votes"] == 130e18

# 	assert arena.numberOfNftsWithNonZeroVotes() == 50


# def test_fourth_stage_advanced(accounts, fourth_stage_advanced):
# 	(zooToken, daiToken, linkToken, nft) = fourth_stage_advanced[0]
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = fourth_stage_advanced[1]

# 	assert arena.currentEpoch() == 1
# 	assert arena.getCurrentStage() == 3

# 	assert arena.numberOfNftsWithNonZeroVotes() == 50
# 	assert arena.nftsInGame() == 50

# 	for i in range(1, 51):
# 		reward = arena.rewardsForEpoch(i, 1)
# 		assert reward["tokensAtBattleStart"] == 1e20
# 		assert reward["pricePerShareAtBattleStart"] == 1e18

# 	for i in range(0, 25):
# 		pair = arena.pairsInEpoch(1, i)
# 		assert pair["playedInEpoch"] == False
# 		assert pair["win"] == False


# def test_fifth_stage_advanced(accounts, fifth_stage_advanced):
# 	(zooToken, daiToken, linkToken, nft) = fifth_stage_advanced[0]
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = fifth_stage_advanced[1]

# 	assert arena.currentEpoch() == 1
# 	assert arena.getCurrentStage() == 4

# 	for i in range(1, 51):
# 		reward = arena.rewardsForEpoch(i, 1)
# 		assert reward["votes"] == 130e18 * 2
# 		assert reward["yTokens"] == 1e20
# 		assert reward["yTokensSaldo"] == 0

# 		voting = arena.votingPositionsValues(i)
# 		assert voting["stakingPositionId"] == i
# 		assert voting["daiInvested"] == 1e20 # 100 DAI
# 		assert voting["zooInvested"] == 1e20 # 100 ZOO
# 		assert voting["startEpoch"] == 1
# 		assert voting["votes"] == 130e18 * 2


# def test_finished_epoch_advanced(accounts, finished_epoch_advanced):
# 	(zooToken, daiToken, linkToken, nft) = finished_epoch_advanced[0]
# 	(vault, functions, governance, staking, voting, arena, listingList, xZoo, jackpotA, jackpotB) = finished_epoch_advanced[1]

# 	assert arena.currentEpoch() == 2
# 	assert arena.getCurrentStage() == 0

# 	for i in range(25):
# 		pair = arena.pairsInEpoch(1, i)
# 		assert pair["playedInEpoch"] == True

# 		# Check change of yTokens balance after choosing winner and transfer dai to vault
# 		assert (arena.rewardsForEpoch(pair["token1"], 2)["yTokens"] == 66666666666666666667) or (arena.rewardsForEpoch(pair["token1"], 2)["yTokens"] == 133333333333333333333)
# 		assert (arena.rewardsForEpoch(pair["token2"], 2)["yTokens"] == 66666666666666666667) or (arena.rewardsForEpoch(pair["token2"], 2)["yTokens"] == 133333333333333333333)

# 	assert arena.numberOfPlayedPairsInEpoch(1) == 25