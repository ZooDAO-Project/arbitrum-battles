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

	return staking.stakeNft(nft.address, tokenId, _from(account))


def test_only_staking_contract_can_call(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	with brownie.reverts():
		arena.createStakerPosition(accounts[1], nft.address, _from(accounts[1]))

	tx = stake_nft(staking, accounts[1], nft, 4)

	assert tx.status == 1


def test_stage_must_be_first(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	chain.sleep(arena.firstStageDuration())

	with brownie.reverts('Wrong stage!'):
		tx = stake_nft(staking, accounts[1], nft, 4)


def test_creating_of_staking_position(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	position = arena.stakingPositionsValues(1)
	currentEpoch = arena.currentEpoch()

	assert position["startEpoch"] == currentEpoch
	# start date should no more that +-5 seconds away from current blockchain time
	#assert position["startDate"] >= chain.time() - 5 or position["startDate"] <= chain.time() + 5
	assert position["lastRewardedEpoch"] == currentEpoch


def test_push_to_active_staking_positions(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	stake_nft(staking, accounts[1], nft, 4)

	activePosition = arena.activeStakerPositions(0)

	assert activePosition == 1


def test_emitting_event(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	tx = stake_nft(staking, accounts[1], nft, 4)

	event = tx.events['CreatedStakerPosition']

	assert len(tx.events) == 3
	assert event["currentEpoch"] == arena.currentEpoch()
	assert event["staker"] == accounts[1]
	assert event["stakingPositionId"] == 1


def test_incrementing_and_returning_number_of_staking_positions(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	number_of_staking_positions_before = arena.numberOfStakingPositions()

	tx = stake_nft(staking, accounts[1], nft, 4)

	number_of_staking_positions_after = arena.numberOfStakingPositions()

	# Checking correctness of returning index by index of minted staking token
	assert staking.ownerOf(number_of_staking_positions_before) == accounts[1]
	# Should increment numberOfStakingPosition for future stakes
	assert number_of_staking_positions_before + 1 == number_of_staking_positions_after
