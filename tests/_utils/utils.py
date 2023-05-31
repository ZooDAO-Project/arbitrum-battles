from typing import List
from brownie import chain
import brownie

NULL_ADDRESS = '0x0000000000000000000000000000000000000001'

def _from(account):
	return {"from": account}


def stake_nft(staking, account, nft, tokenId):
	nft.approve(staking.address, tokenId, _from(account))
	
	return staking.stakeNft(nft.address, tokenId, _from(account))


def create_voting_position(voting, daiToken, account, stakingPositionId, daiAmount):
	daiToken.approve(voting, daiAmount, _from(account))

	return voting.createNewVotingPosition(stakingPositionId, daiAmount, _from(account))


def add_dai_to_voting(voting, daiToken, voting_position_id, dai_amount):
	voting_owner = voting.ownerOf(voting_position_id)

	daiToken.approve(voting, dai_amount, _from(voting_owner))

	return voting.addDaiToPosition(voting_position_id, dai_amount, _from(voting_owner))


def get_active_staking_positions_array(arena) -> List[int]:
	length = arena.getStakerPositionsLength()
	arr = []

	for i in range(length):
			arr.append(arena.activeStakerPositions(i))

	return arr


def skip_epoch(arena):
	chain.sleep(arena.epochDuration())
	arena.updateEpoch()


def is_in_active_staking_array_part_with_votes(arena, stakingPositionId) -> bool:
	activePositions = get_active_staking_positions_array(arena)
	index = activePositions.index(stakingPositionId)
	return index < arena.numberOfNftsWithNonZeroVotes()


def play_some_epochs(tokens, battles, number_of_epochs: int, interest: int):
	(zooToken, daiToken, linkToken, nft) = tokens
	(vault, functions, governance, staking, voting, arena) = battles

	for i in range(number_of_epochs):
		print('Playing epoch')

		current_stage = arena.getCurrentStage()

		chain.sleep(arena.firstStageDuration() * (2 - current_stage))
		chain.mine(1)

		print('Skipped to stage ', arena.getCurrentStage())
		print('Active staked NFTs', arena.getStakerPositionsLength())

		pair_all_nfts(arena)
		print('Created ', arena.getNftPairLength(arena.currentEpoch()), ' pairs')

		chain.sleep(arena.thirdStageDuration())

		daiToken.approve(vault, interest)
		vault.increaseMockBalance(interest)
		print('Increase Vault balance on ', interest / 1e18, ' DAI')

		chain.sleep(arena.fourthStageDuration())

		current_epoch = arena.currentEpoch()
		pairs_number = arena.getNftPairLength(current_epoch)

		for pair in range(pairs_number):
				arena.chooseWinnerInPair(pair)
				print('Played pair №', pair + 1)

		print('Update epoch')


def pair_all_nfts(arena):
	################## pair loop #################
	# # assert arena.numberOfNftsWithNonZeroVotes() == 8
	assert arena.getCurrentStage() == 2

	current_epoch = arena.currentEpoch()

	stakers = [] # all staking positions
	participants = [] # staking positions with votes == eligible for pairing
	alreadyPaired = [] # list for already paired positions
	n = 0 # pair index
	
	activeStakingPositionLength = arena.getStakerPositionsLength()

	# loop to create list of positions:
	for l in range(activeStakingPositionLength):

		stakerPositionId = arena.activeStakerPositions(l)		  # get position id
		stakers.append(stakerPositionId)										   # push into list id of staker.

		getBattleReward = arena.rewardsForEpoch(stakerPositionId, current_epoch);  # id, epoch, get rewards struct
		if getBattleReward[1] != 0: # [1] - votes
				participants.append(stakerPositionId) # add eligible for pairing in list

	# loop to actually pair:
	for i in range(0, arena.getStakerPositionsLength()):
		stakerPositionId = arena.activeStakerPositions(i)				   # set id from index

		if stakerPositionId not in alreadyPaired and stakerPositionId in participants and len(participants) >= 2:  # if not in array of paired, in array of eligible for pairing, and 2 or more positions left.

			arena.pairNft(stakerPositionId)				# pair this position
			alreadyPaired.append(stakerPositionId) # add position to already paired
			pairs = arena.pairsInEpoch(current_epoch, n)		   # epoch, index to get pair struct
			pairNew = pairs[1]										 # id of 2nd token in pair
			alreadyPaired.append(pairNew)				  # add opponent to already paired
			n+=1																   # increment index

			participants.remove(stakerPositionId)
			participants.remove(pairNew)


def play_all_pairs(arena):
	current_epoch = arena.currentEpoch()
	
	try:
		arena.requestRandom()
	except:
		pass

	pairs_number = arena.getNftPairLength(current_epoch)

	for pair_index in range(pairs_number):
		pair = arena.pairsInEpoch(current_epoch, pair_index)

		if pair['playedInEpoch']:
			continue
		
		arena.chooseWinnerInPair(pair_index)


def equals_with_calculation_error(value, target, error_percentage) -> bool:
		return target - (target / 100 * error_percentage) <= value and value <= target + (target / 100 * error_percentage)

def find_voting_owner_in_accounts(voting_position_id, accounts, voting):
	for account in accounts:
		if account.address == voting.ownerOf(voting_position_id):
			return account