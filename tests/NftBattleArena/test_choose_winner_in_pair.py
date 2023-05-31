import brownie
from brownie import chain
import pytest

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


def test_stage_requirement(accounts, fourth_stage):
	(zooToken, daiToken, linkToken, nft) = fourth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fourth_stage[1]

	with brownie.reverts("Wrong stage!"):
		arena.chooseWinnerInPair(0)


def test_winner_already_chosen_requirement(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	pairIndex = 0
	arena.requestRandom()
	tx = arena.chooseWinnerInPair(pairIndex)
	assert tx.status == 1

	with brownie.reverts("E1"):
		arena.chooseWinnerInPair(pairIndex)


def test_should_update_staking_info(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	pairIndex = 0
	arena.requestRandom()
	arena.chooseWinnerInPair(pairIndex)

	currentEpoch = arena.currentEpoch()
	pair = arena.pairsInEpoch(currentEpoch, pairIndex)

	staking1 = arena.stakingPositionsValues(pair["token1"])
	staking2 = arena.stakingPositionsValues(pair["token2"])

	assert staking1["lastUpdateEpoch"] == currentEpoch
	assert staking2["lastUpdateEpoch"] == currentEpoch


def test_should_finish_battle_and_choose_winner(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	pairIndex = 0
	arena.requestRandom()
	tx = arena.chooseWinnerInPair(pairIndex)

	currentEpoch = arena.currentEpoch()
	pair = arena.pairsInEpoch(currentEpoch, pairIndex)

	assert pair["playedInEpoch"] == True


def test_increasing_of_number_of_played_pairs_in_epoch(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	currentEpoch = arena.currentEpoch()
	assert arena.numberOfPlayedPairsInEpoch(currentEpoch) == 0

	pairIndex = 0
	arena.requestRandom()
	arena.chooseWinnerInPair(pairIndex)

	pair = arena.pairsInEpoch(currentEpoch, pairIndex)

	assert arena.numberOfPlayedPairsInEpoch(currentEpoch) == 1


def test_rewards_calculations(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	arena.requestRandom()
	vault.increaseMockBalance()

	currentEpoch = arena.currentEpoch()

	pairIndex = 0
	pair = arena.pairsInEpoch(currentEpoch, pairIndex)

	battleRewardOfToken1 = arena.rewardsForEpoch(pair["token1"], currentEpoch)
	battleRewardOfToken2 = arena.rewardsForEpoch(pair["token2"], currentEpoch)

	print("battleRewardOfToken1: ", battleRewardOfToken1)
	print("battleRewardOfToken2: ", battleRewardOfToken2, "\n")

	tokensAtBattleEnd1 = arena.sharesToTokens.call(battleRewardOfToken1["yTokens"])
	tokensAtBattleEnd2 = arena.sharesToTokens.call(battleRewardOfToken2["yTokens"])

	print("tokensAtBattleEnd1: ", tokensAtBattleEnd1)
	print("tokensAtBattleEnd2: ", tokensAtBattleEnd2, "\n")

	pps1 = battleRewardOfToken1["pricePerShareAtBattleStart"]

	price_per_share_at_vault = vault.exchangeRateCurrent.call()

	ppsc1 = 0
	ppsc2 = 0

	# Must go through ELSE statement
	assert pps1 != price_per_share_at_vault

	print("pps1 IS NOT equal to pps in vault")
	ppsc1 = price_per_share_at_vault * pps1 // (price_per_share_at_vault - pps1)
	ppsc2 = price_per_share_at_vault * pps1 // (price_per_share_at_vault - pps1)

	assert ppsc1 != 2 ** 256 - 1
	print("pricePerShareCoef: ", ppsc1, "\n")

	print("tokensAtBattleStart1: ", battleRewardOfToken1["tokensAtBattleStart"])
	print("tokensAtBattleStart2: ", battleRewardOfToken2["tokensAtBattleStart"], "\n")

	income1 = arena.tokensToShares.call(tokensAtBattleEnd1 - battleRewardOfToken1["tokensAtBattleStart"])
	income2 = arena.tokensToShares.call(tokensAtBattleEnd2 - battleRewardOfToken2["tokensAtBattleStart"])

	# x_rewards = (income1 + income2) * 5 // 1000
	# jackpot_rewards = (income1 + income2) * 1 // 100

	print(f"yvTokens income of first position in pair: {income1}")
	print(f"yvTokens income of second position in pair: {income2}")

	# Get battle results from SC
	tx = arena.chooseWinnerInPair(pairIndex)
	firstWon = tx.events["ChosenWinner"]["winner"]

	reward1current = arena.rewardsForEpoch(pair["token1"], currentEpoch)
	reward2current = arena.rewardsForEpoch(pair["token2"], currentEpoch)

	reward1next = arena.rewardsForEpoch(pair["token1"], currentEpoch + 1)
	reward2next = arena.rewardsForEpoch(pair["token2"], currentEpoch + 1)

	assert reward1current['pricePerShareCoef'] == ppsc1
	assert reward2current['pricePerShareCoef'] == ppsc2

	# jackpots and xZoo were removed, so test outdated and need to rework

	# eps = 100 
	# if firstWon:
	# 	assert abs(reward1current["yTokensSaldo"] - (battleRewardOfToken1["yTokensSaldo"] + income1 + income2)) < eps # - x_rewards - 2 * jackpot_rewards)) < eps
	# 	assert abs(reward2current["yTokensSaldo"] - (battleRewardOfToken2["yTokensSaldo"] - income2)) < eps

	# 	assert abs(reward1next["yTokens"] - (battleRewardOfToken1["yTokens"] + income2)) < eps # - x_rewards - 2 * jackpot_rewards)) < eps
	# 	assert abs(reward2next["yTokens"] - (battleRewardOfToken2["yTokens"] - income2)) < eps

	# else:
	# 	assert abs(reward1current["yTokensSaldo"] - (battleRewardOfToken1["yTokensSaldo"] - income1)) < eps
	# 	assert abs(reward2current["yTokensSaldo"] - (battleRewardOfToken2["yTokensSaldo"] + income1 + income2 )) < eps # - x_rewards - 2 * jackpot_rewards)) < eps

	# 	assert abs(reward1next["yTokens"] - (battleRewardOfToken1["yTokens"] - income1)) < eps
	# 	assert abs(reward2next["yTokens"] - (battleRewardOfToken2["yTokens"] + income1)) < eps #x_rewards - 2 * jackpot_rewards)) < eps


def test_ending_of_epoch_if_all_pairs_played(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	arena.requestRandom()
	for pairIndex in range(4):
		arena.chooseWinnerInPair(pairIndex)

	assert arena.currentEpoch() == 2
	assert arena.getCurrentStage() == 0


# @pytest.mark.skip(reason="Time-consuming test that rarely needed to run. Also all battles have same result")
# def test_fair_win_chances(accounts, tokens_advanced, battles_advanced):
# 	(zooToken, daiToken, linkToken, nft) = tokens_advanced
# 	(vault, functions, governance, staking, voting, arena, listing) = battles_advanced

# 	attempts = 1
# 	participants = 3

#

# 	for i in range(participants):
# 		for j in range(participants):
# 			position = j + i * 10 + 1
# 			nft.approve(staking, position, _from(accounts[i]))
# 			staking.stakeNft(nft, position, _from(accounts[i]))



# 	# One iteration is one epoch of games with 50/50 chances of winning in every game
# 	for attempt in range(attempts):
# 		print(attempt)

# 		chain.sleep(arena.firstStageDuration())

# 		# Every account votes for his NFTs
# 		for i in range(participants):
# 			daiToken.approve(voting, 1e21, _from(accounts[i]))

# 			for j in range(participants):
# 				staking_position = 1 + j + i * participants
# 				voting.createNewVotingPosition(staking_position, 1e20, _from(accounts[i]))

# 		chain.sleep(arena.secondStageDuration())

# 		epoch = arena.currentEpoch()

# 		stakers = [] # all staking positions
# 		participants = [] # staking positions with votes == eligible for pairing
# 		alreadyPaired = [] # list for already paired positions
# 		n = 0 # pair index

# 		# loop to create list of positions:
# 		for l in range(0, arena.getStakerPositionsLength()):
# 			stakerPositionId = arena.activeStakerPositions(l)      # get position id
# 			stakers.append(stakerPositionId)                       # push into list id of staker.
# 			arena.updateInfo(stakerPositionId)                     # updateInfo for every index in array

# 			getBattleReward = arena.rewardsForEpoch(stakerPositionId, epoch);  # id, epoch, get rewards struct
# 			if getBattleReward[1] != 0: # [1] - votes
# 					participants.append(stakerPositionId) # add eligible for pairing in list

# 		# loop to actually pair:
# 		for i in range(0, arena.getStakerPositionsLength()):
# 			stakerPositionId = arena.activeStakerPositions(i)           # set id from index

# 			if stakerPositionId not in alreadyPaired and stakerPositionId in participants and len(participants) >= 2:  # if not in array of paired, in array of eligible for pairing, and 2 or more positions left.

# 				arena.pairNft(stakerPositionId)        # pair this position
# 				alreadyPaired.append(stakerPositionId) # add position to already paired
# 				pairs = arena.pairsInEpoch(epoch, n)       # epoch, index to get pair struct
# 				pairNew = pairs[1]                     # id of 2nd token in pair
# 				alreadyPaired.append(pairNew)          # add opponent to already paired
# 				n+=1                                   # increment index

# 				participants.remove(stakerPositionId)
# 				participants.remove(pairNew)

# 		chain.sleep(arena.thirdStageDuration())
# 		chain.sleep(arena.fourthStageDuration())

# 		for i in range(len(participants) // 2):
# 			arena.chooseWinnerInPair(i)


# 	# gathering results
# 	winsOf1Token = 0
# 	winsOf2Token = 0

# 	for epoch in range(1, attempts + 1):
# 		for pairIndex in range(len(participants) // 2):
# 			pair = arena.pairsInEpoch(epoch, pairIndex)

# 			if pair["win"]:
# 				winsOf1Token += 1
# 			else:
# 				winsOf2Token += 1

# 	# Checking fights results
# 	assert winsOf1Token < winsOf2Token * 1.1 and winsOf1Token > winsOf2Token * 0.9


def test_should_emit_event(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	pairIndex = 0
	arena.requestRandom()
	tx = arena.chooseWinnerInPair(pairIndex)

	currentEpoch = arena.currentEpoch()
	pair = arena.pairsInEpoch(currentEpoch, pairIndex)

	event = tx.events["ChosenWinner"]

	assert event["currentEpoch"] == currentEpoch
	assert event["fighter1"] == pair["token1"]
	assert event["fighter2"] == pair["token2"]
	assert event["winner"] == True or event["winner"] == False
	assert event["pairIndex"] == pairIndex
	assert event["playedPairsAmount"] == 1