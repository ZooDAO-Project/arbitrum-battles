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

	

	stake_nft(staking, accounts[1], nft, 4)

	with brownie.reverts():
		arena.removeStakerPosition(1, accounts[1], _from(accounts[1]))

	tx = staking.unstakeNft(1, _from(accounts[1]))

	assert tx.status == 1


def test_stage_must_be_first(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	

	stake_nft(staking, accounts[1], nft, 4)

	chain.sleep(arena.firstStageDuration())

	with brownie.reverts('Wrong stage!'):
		staking.unstakeNft(1, _from(accounts[1]))

	chain.sleep(arena.secondStageDuration())

	with brownie.reverts('Wrong stage!'):
		staking.unstakeNft(1, _from(accounts[1]))

	chain.sleep(arena.thirdStageDuration())

	with brownie.reverts('Wrong stage!'):
		staking.unstakeNft(1, _from(accounts[1]))

	chain.sleep(arena.fourthStageDuration())

	with brownie.reverts('Wrong stage!'):
		staking.unstakeNft(1, _from(accounts[1]))

	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	tx = staking.unstakeNft(1, _from(accounts[1]))

	assert tx.status == 1


def test_setting_end_epoch_and_end_date(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	

	stake_nft(staking, accounts[1], nft, 4)

	staking.unstakeNft(1, _from(accounts[1]))

	position = arena.stakingPositionsValues(1)
	currentEpoch = arena.currentEpoch()

	assert position["endEpoch"] == currentEpoch
	# start date should no more that +-5 seconds away from current blockchain time
	#assert position["endDate"] >= chain.time() - 5 or position["startDate"] <= chain.time() + 5


def test_removing_already_removed_position(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	

	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	stake_nft(staking, accounts[1], nft, 6)

	chain.sleep(arena.firstStageDuration())

	daiToken.approve(voting, 20e18, _from(accounts[0]))

	# checking i > numberOfNftsWithNonZeroVotes
	voting.createNewVotingPosition(1, 10e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(3, 10e18, True, _from(accounts[0]))

	chain.sleep(arena.secondStageDuration())
	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())
	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	position_to_unstake = 2
	tx = staking.unstakeNft(position_to_unstake, _from(accounts[1]))
	assert tx.status == 1

	with brownie.reverts("E1"):
		staking.unstakeNft(position_to_unstake, _from(accounts[1]))


def test_removing_from_active_staking_positions(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens	

	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	stake_nft(staking, accounts[1], nft, 6)

	chain.sleep(arena.firstStageDuration())

	daiToken.approve(voting, 200e18, _from(accounts[0]))
	# checking i < numberOfNftsWithNonZeroVotes
	voting.createNewVotingPosition(1, 100e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(2, 100e18, True, _from(accounts[0]))

	assert arena.activeStakerPositions(0) == 1
	assert arena.activeStakerPositions(1) == 2
	assert arena.activeStakerPositions(2) == 3

	epoch = arena.currentEpoch()
	assert epoch == 1

	reward = arena.rewardsForEpoch(1, epoch)
	assert reward['votes'] == 130e18
	assert abs(arena.sharesToTokens.call(reward['yTokens']) - 100e18) < 10

	reward = arena.rewardsForEpoch(2, epoch)
	assert reward['votes'] == 130e18
	assert abs(arena.sharesToTokens.call(reward['yTokens']) - 100e18) < 10

	chain.sleep(arena.secondStageDuration())
	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())
	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	active_staker_positions_length_before = arena.getStakerPositionsLength()

	rewards = arena.rewardsForEpoch(1, arena.currentEpoch())
	# assert rewards.votes == 1

	assert arena.numberOfNftsWithNonZeroVotes() == 2

	staking.unstakeNft(1, _from(accounts[1]))

	assert arena.activeStakerPositions(0) == 2
	assert arena.activeStakerPositions(1) == 3

	assert arena.getStakerPositionsLength() == active_staker_positions_length_before - 1


def test_removing_from_active_staking_positions_without_votes(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	

	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	stake_nft(staking, accounts[1], nft, 6)

	chain.sleep(arena.firstStageDuration())

	daiToken.approve(voting, 20e18, _from(accounts[0]))

	# checking i > numberOfNftsWithNonZeroVotes
	voting.createNewVotingPosition(1, 10e18, True, _from(accounts[0]))

	chain.sleep(arena.secondStageDuration())
	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())
	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	active_staker_positions_length = arena.getStakerPositionsLength()
	last_active_staker_position = arena.activeStakerPositions(active_staker_positions_length - 1)

	position_to_unstake = 2
	staking.unstakeNft(position_to_unstake, _from(accounts[1]))

	# Unstaked position must be replaced with last element from array
	assert arena.activeStakerPositions(position_to_unstake - 1) == last_active_staker_position

	# Check that activeStakingPositions length decreased
	assert arena.getStakerPositionsLength() == active_staker_positions_length - 1


def test_array_structure_consistency(accounts, battles, tokens):
	# Array should contain firstly - tokens with votes, secondly - tokens without votes
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles

	

	stake_nft(staking, accounts[0], nft, 1)
	stake_nft(staking, accounts[0], nft, 2)
	stake_nft(staking, accounts[0], nft, 3)
	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	stake_nft(staking, accounts[1], nft, 6)
	stake_nft(staking, accounts[2], nft, 7)
	stake_nft(staking, accounts[2], nft, 8)
	stake_nft(staking, accounts[2], nft, 9)

	positions_before_voting = get_pairs_positions(arena)
	assert positions_before_voting == [1,2,3,4,5,6,7,8,9]

	chain.sleep(arena.firstStageDuration())

	daiToken.approve(voting, 40e18, _from(accounts[0]))

	voting.createNewVotingPosition(1, 10e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(4, 10e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(3, 10e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(5, 10e18, True, _from(accounts[0]))

	positions_after_voting = get_pairs_positions(arena)

	assert positions_after_voting == [1, 4, 3, 5, 2, 6, 7, 8, 9]

	chain.sleep(arena.secondStageDuration())
	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())
	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	tokens_and_owners = [
		(1, accounts[0]),
		(2, accounts[0]),
		(3, accounts[0]),
		(4, accounts[1]),
		(5, accounts[1]),
		(6, accounts[1]),
		(7, accounts[2]),
		(8, accounts[2]),
		(9, accounts[2]),
	]

	for (token, owner) in tokens_and_owners:
		staking.unstakeNft(token, _from(owner))

		positions = get_pairs_positions(arena)
		numberOfNftsWithNonZeroVotes = arena.numberOfNftsWithNonZeroVotes()

		for i in range(len(positions)):
			reward = arena.rewardsForEpoch(positions[i], 1)

			if i < numberOfNftsWithNonZeroVotes:
				assert reward["votes"] != 0

			if i >= numberOfNftsWithNonZeroVotes:
				assert reward["votes"] == 0


def get_pairs_positions(arena):
	positions = []

	for i in range(arena.getStakerPositionsLength()):
		position = arena.activeStakerPositions(i)
		positions.append(position)

	return positions


def test_removing_from_active_staking_positions_with_votes(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	
	# Some random stakes
	stake_nft(staking, accounts[1], nft, 4)
	stake_nft(staking, accounts[1], nft, 5)
	stake_nft(staking, accounts[1], nft, 6)
	stake_nft(staking, accounts[2], nft, 7)
	stake_nft(staking, accounts[2], nft, 8)
	stake_nft(staking, accounts[2], nft, 9)

	chain.sleep(arena.firstStageDuration())

	# Creating votes for first 3 stakes
	daiToken.approve(voting, 30e18, _from(accounts[0]))

	voting.createNewVotingPosition(1, 10e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(2, 10e18, True, _from(accounts[0]))
	voting.createNewVotingPosition(3, 10e18, True, _from(accounts[0]))

	# Sleep until firstStage
	chain.sleep(arena.secondStageDuration())
	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())
	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	# checking actions after in i < numberOfNftsWithNonZeroVotes condition
	active_staker_positions_length_before_unstake = arena.getStakerPositionsLength()

	last_active_staker_position = arena.activeStakerPositions(active_staker_positions_length_before_unstake - 1)


	stakes_with_votes_before_unstake = arena.numberOfNftsWithNonZeroVotes()
	last_active_staker_position_with_votes = arena.activeStakerPositions(stakes_with_votes_before_unstake - 1)

	# Unstaking element that have votes
	position_to_unstake = 2
	staking.unstakeNft(position_to_unstake, _from(accounts[1]))


	# Unstaked position must be replaced with last element with votes in array
	assert arena.activeStakerPositions(position_to_unstake - 1) == last_active_staker_position_with_votes
	# Last element with votes must be replaced with last element in array
	assert arena.activeStakerPositions(stakes_with_votes_before_unstake - 1) == last_active_staker_position

	# Check decrementing numberOfNftsWithNonZeroVotes
	assert arena.numberOfNftsWithNonZeroVotes() == stakes_with_votes_before_unstake - 1

	# Check that activeStakingPositions length decreased
	assert arena.getStakerPositionsLength() == active_staker_positions_length_before_unstake - 1


def test_emitting_event(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	

	stake_nft(staking, accounts[1], nft, 4)

	tx = staking.unstakeNft(1, _from(accounts[1]))

	event = tx.events['RemovedStakerPosition']

	assert event["currentEpoch"] == arena.currentEpoch()
	assert event["staker"] == accounts[1]
	assert event["stakingPositionId"] == 1


# TODO: unstake is very insufficient in gas :(
def _test_gas_efficiency(accounts, battles, tokens):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	

	nftsByAccount = 10
	nft.batchMint(list(accounts), nftsByAccount, _from(accounts[0]))

	# Stake all NFTs
	for i in range(len(accounts)):
		nft.setApprovalForAll(staking, True, _from(accounts[i]))

		for j in range(nftsByAccount):
			tokenId = 10 + j + i * nftsByAccount # 9 - already minted in conftest
			staking.stakeNft(nft, tokenId, _from(accounts[i]))

	# Wait for voting
	chain.sleep(arena.firstStageDuration())

	daiToken.approve(voting, 100e18, _from(accounts[1]))

	for i in range(100):
		voting.createNewVotingPosition(i, 1e18, True, _from(accounts[1]))

	# Sleep until firstStage
	chain.sleep(arena.secondStageDuration())
	chain.sleep(arena.thirdStageDuration())
	chain.sleep(arena.fourthStageDuration())
	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	tx = staking.unstakeNft(10 * nftsByAccount, _from(accounts[9]))
	assert tx.status == 1


