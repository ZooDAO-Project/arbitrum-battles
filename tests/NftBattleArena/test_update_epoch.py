import brownie
from brownie import chain

def test_stage_requirement(accounts, battles, tokens):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	with brownie.reverts("Wrong stage!"):
		arena.updateEpoch()

	chain.sleep(arena.firstStageDuration())

	with brownie.reverts("Wrong stage!"):
		arena.updateEpoch()

	chain.sleep(arena.secondStageDuration())

	with brownie. reverts("Wrong stage!"):
		arena.updateEpoch()

	chain.sleep(arena.thirdStageDuration())

	with brownie.reverts("Wrong stage!"):
		arena.updateEpoch()

	chain.sleep(arena.fourthStageDuration())

	with brownie.reverts(""):
		arena.updateEpoch()

	chain.sleep(arena.fifthStageDuration())

	tx = arena.updateEpoch()
	assert tx.status == 1


def test_all_pairs_played_requirement(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	epoch = arena.currentEpoch()
	arena.requestRandom()
	
	# Reverted until all pairs finished battles
	for i in range(arena.getNftPairLength(epoch)):
		with brownie.reverts():
			arena.updateEpoch()

		arena.chooseWinnerInPair(i)


	chain.sleep(arena.fifthStageDuration())
	arena.updateEpoch()

	assert arena.currentEpoch() == epoch + 1


def test_ended_stage_requirement(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	epoch = arena.currentEpoch()

	with brownie.reverts():
		arena.updateEpoch()

	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	assert arena.currentEpoch() == epoch + 1


def test_contract_info_update(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	epoch = arena.currentEpoch()

	chain.sleep(arena.fifthStageDuration())

	for i in range(5):
		functions.setStageDuration(i, 100 * i)

	arena.updateEpoch()

	# Start epoch date updated
	epochStartDate = arena.epochStartDate()
	assert epochStartDate < (chain.time() + 7) and epochStartDate > (chain.time() - 7)

	# Epoch updated
	newEpoch = arena.currentEpoch()
	assert newEpoch == epoch + 1

	# Nfts in game updated
	assert arena.nftsInGame() == 0

	# Nfts in game updated
	assert arena.nftsInGame() == 0

	# Stages duration updates
	assert arena.firstStageDuration() == 0
	assert arena.secondStageDuration() == 100
	assert arena.thirdStageDuration() == 200
	assert arena.fourthStageDuration() == 300
	assert arena.fifthStageDuration() == 400

	assert arena.epochDuration() == 100 + 200 + 300 + 400


def test_event_emitting(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	epoch = arena.currentEpoch()

	chain.sleep(arena.fifthStageDuration())

	tx = arena.updateEpoch()
	event = tx.events["EpochUpdated"]

	assert event["date"] == arena.epochStartDate()
	assert event["newEpoch"] == epoch + 1


