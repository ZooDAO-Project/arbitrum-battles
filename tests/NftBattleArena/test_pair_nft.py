import brownie
from brownie import chain
import random

from _utils.utils import pair_all_nfts


def test_stage_requirement(accounts, second_stage):
	(zooToken, daiToken, linkToken, nft) = second_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = second_stage[1]

	with brownie.reverts("Wrong stage!"):
		arena.pairNft(1)

	daiToken.approve(voting, 20e18)

	voting.createNewVotingPosition(1, 10e18, True)
	voting.createNewVotingPosition(2, 10e18, True)

	chain.sleep(arena.secondStageDuration())

	tx = arena.pairNft(1)
	assert tx.status == 1

	chain.sleep(arena.thirdStageDuration())

	with brownie.reverts("Wrong stage!"):
		arena.pairNft(1)


def test_cant_pair_paired_nft(accounts, third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = third_stage[1]

	arena.pairNft(1)

	with brownie.reverts("E1"):
		arena.pairNft(1)


def test_pairing_non_existing_staking(accounts, third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = third_stage[1]

	with brownie.reverts("E1"):
		arena.pairNft(25)
		arena.pairNft(0)
		arena.pairNft(100)


def test_recording_pair(accounts, third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = third_stage[1]

	currentEpoch = arena.currentEpoch()

	tx = arena.pairNft(1)
	pair_index = 0
	event = tx.events["PairedNft"]

	pair = arena.pairsInEpoch(currentEpoch, pair_index)
	assert pair["token1"] == 1 
	assert pair["token2"] == event["fighter2"]
	assert pair["token2"] != 0
	assert pair["playedInEpoch"] == False
	assert pair["win"] == False


def test_updating_staking(accounts, third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = third_stage[1]

	currentEpoch = arena.currentEpoch()

	tx = arena.pairNft(1)
	event = tx.events["PairedNft"]

	# Actually they are already updated after last voting
	assert arena.stakingPositionsValues(1)["lastUpdateEpoch"] == currentEpoch
	assert arena.stakingPositionsValues(event["fighter2"])["lastUpdateEpoch"] == currentEpoch


def test_recording_rewards(accounts, third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = third_stage[1]

	currentEpoch = arena.currentEpoch()

	fighter1 = 1
	tx = arena.pairNft(fighter1)

	event = tx.events["PairedNft"]
	fighter2 = event['fighter2']

	reward1 = arena.rewardsForEpoch(fighter1, currentEpoch)
	reward2 = arena.rewardsForEpoch(fighter2, currentEpoch)

	print(reward1)
	print(reward2)

	tokensAtBattleStart1 = arena.sharesToTokens.call(reward1["yTokens"])
	tokensAtBattleStart2 = arena.sharesToTokens.call(reward2["yTokens"])

	assert reward1["tokensAtBattleStart"] == tokensAtBattleStart1
	assert reward2["tokensAtBattleStart"] == tokensAtBattleStart2

	pps = vault.exchangeRateCurrent.call()
	assert reward1["pricePerShareAtBattleStart"] == pps
	assert reward1["pricePerShareAtBattleStart"] == pps


def test_pairing_all_nfts(third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = third_stage[1]

	current_epoch = arena.currentEpoch()

	pair_all_nfts(arena)

	assert arena.getNftPairLength(current_epoch) == 4


def test_elements_movements_in_array(accounts, third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = third_stage[1]

	currentEpoch = arena.currentEpoch()

	tokens = get_pairs_positions(arena)

	positions_before_pairing = get_pairs_positions(arena)
	expected_positions = positions_before_pairing

	# Pair NFTs
	for i in range(4):
		positions_before_pairing = get_pairs_positions(arena)

		token1 = random.choice(tokens)

		nftsInGame = arena.nftsInGame()
		print("NftsInGame: ", nftsInGame)

		tx = arena.pairNft(token1)
		event = tx.events["PairedNft"]

		token2 = event["fighter2"]

		print("Tokens:  ", token1, token2)
		tokens.remove(token1)
		tokens.remove(token2)

		positions_after_pairing = get_pairs_positions(arena)

		expected_positions = emulate_pair_moving(arena, expected_positions, nftsInGame, token1, token2)

		print("Before:   ", positions_before_pairing)
		print("After:    ", positions_after_pairing)
		print("Expected: ", expected_positions, "\n")

		assert expected_positions == positions_after_pairing


def get_pairs_positions(arena):
	positions = []

	for i in range(arena.getStakerPositionsLength()):
		position = arena.activeStakerPositions(i)
		positions.append(position)

	return positions


def emulate_pair_moving(arena, positions, nftsInGame, stakingPositionId1, stakingPositionId2):
	index1 = 0
	index2 = 0

	for i in range(len(positions)):
		if positions[i] == stakingPositionId1:
			index1 = i
			break

	positions[index1], positions[nftsInGame] = positions[nftsInGame], positions[index1]

	for i in range(len(positions)):
		if positions[i] == stakingPositionId2:
			index2 = i
			break

	print("Indexes: ", index1, index2, "\n")

	nftsInGame += 1

	positions[index2], positions[nftsInGame] = positions[nftsInGame], positions[index2]

	return positions 



def test_emitting_event(accounts, third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = third_stage[1]

	currentEpoch = arena.currentEpoch()

	tx = arena.pairNft(1)
	event = tx.events["PairedNft"]

	assert event["currentEpoch"] == currentEpoch
	assert event["fighter1"] == 1
	assert event["fighter2"] != 1
	assert event["pairIndex"] == 0
