import brownie
from brownie import chain

def test_getting_nft_pair_length(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	assert arena.getNftPairLength(0) == 0
	assert arena.getNftPairLength(1) == 4
	assert arena.getNftPairLength(2) == 0

	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	chain.sleep(arena.firstStageDuration())
	chain.sleep(arena.secondStageDuration())

	stakers = [] # all staking positions
	participants = [] # staking positions with votes == eligible for pairing
	alreadyPaired = [] # list for already paired positions
	n = 0 # pair index

	# loop to create list of positions:
	for l in range(0, arena.getStakerPositionsLength()):
		stakerPositionId = arena.activeStakerPositions(l)      # get position id
		stakers.append(stakerPositionId)                       # push into list id of staker.
		arena.updateInfo(stakerPositionId)                     # updateInfo for every index in array

		getBattleReward = arena.rewardsForEpoch(stakerPositionId, 2);  # id, epoch, get rewards struct
		
		if getBattleReward[1] != 0: # [1] - votes
			participants.append(stakerPositionId) # add eligible for pairing in list

	# loop to actually pair:
	for i in range(0, arena.getStakerPositionsLength()):
		stakerPositionId = arena.activeStakerPositions(i)           # set id from index

		if stakerPositionId not in alreadyPaired and stakerPositionId in participants and len(participants) >= 2:  # if not in array of paired, in array of eligible for pairing, and 2 or more positions left.

			arena.pairNft(stakerPositionId)        # pair this position
			alreadyPaired.append(stakerPositionId) # add position to already paired
			pairs = arena.pairsInEpoch(2, n)       # epoch, index to get pair struct
			pairNew = pairs[1]                     # id of 2nd token in pair
			alreadyPaired.append(pairNew)          # add opponent to already paired 
			n+=1                                   # increment index

			participants.remove(stakerPositionId)
			participants.remove(pairNew)

	assert arena.getNftPairLength(2) == 4


