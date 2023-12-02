#!/usr/bin/python3

import brownie
from brownie import chain

from _utils.utils import _from

def test_balance(accounts, tokens):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	assert zooToken.balanceOf(accounts[0]) == 12e25
	assert zooToken.balanceOf(accounts[1]) == 4e25
	assert zooToken.balanceOf(accounts[2]) == 4e25

	assert daiToken.balanceOf(accounts[0]) == 4e25
	assert daiToken.balanceOf(accounts[1]) == 4e25
	assert daiToken.balanceOf(accounts[2]) == 4e25

	assert nft.balanceOf(accounts[0]) == 3 # 1,2,3 Id
	assert nft.balanceOf(accounts[1]) == 3 # 4,5,6 Id
	assert nft.balanceOf(accounts[2]) == 3 # 7,8,9 ID

def test_battles_workflow_basic(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listingList) = battles
	value = 100e18

	
	nft.approve(staking.address, 4, _from(accounts[1])) # account 1 have nft 4,5,6
	nft.approve(staking.address, 5, _from(accounts[1])) # account 1 have nft 4,5,6
	nft.approve(staking.address, 6, _from(accounts[1])) # account 1 have nft 4,5,6
	staking.stakeNft(nft.address, 4, _from(accounts[1])) # address, id, from. // position 1
	staking.stakeNft(nft.address, 5, _from(accounts[1])) # address, id, from. // position 2
	staking.stakeNft(nft.address, 6, _from(accounts[1])) # address, id, from. // position 3

	chain.sleep(arena.firstStageDuration()) # skip 1st(0) stage, now second stage(1)

	daiToken.approve(voting.address, value*3, _from(accounts[1])) # address, value, from
	voting.createNewVotingPosition(1, value, True, _from(accounts[1])) # stakingPositionId, value, from
	voting.createNewVotingPosition(2, value, True, _from(accounts[1])) # stakingPositionId, value, from
	voting.createNewVotingPosition(3, value, True, _from(accounts[1])) # stakingPositionId, value, from

	chain.sleep(arena.secondStageDuration()) # skip 2nd(1) stage, now third stage(2)

	arena.pairNft(1, _from(accounts[1])) # pair for 0 position.

	chain.sleep(arena.thirdStageDuration()) # skip 3nd(2) stage, now fourth stage(3)

	zooToken.approve(voting.address, value, _from(accounts[1])) # address, value, from
	voting.addZooToPosition(1, value, _from(accounts[1])) # stakingPositionId, value, from

	chain.sleep(arena.fourthStageDuration()) # skip 4th(3) stage, now fifth stage(4)

	arena.requestRandom()
	arena.chooseWinnerInPair(0, _from(accounts[1])) # pair index, from

	chain.sleep(arena.fifthStageDuration())
	arena.updateEpoch()

	assert arena.currentEpoch() == 2
	assert arena.getCurrentStage() == 0


def test_battles_workflow_advanced(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listing) = battles
	value = 100e18

	# stage 0, epoch 1 #

	
	nft.approve(staking.address, 4, _from(accounts[1])) # account 1 have nft 4,5,6
	nft.approve(staking.address, 5, _from(accounts[1])) # account 1 have nft 4,5,6
	nft.approve(staking.address, 6, _from(accounts[1])) # account 1 have nft 4,5,6
	staking.stakeNft(nft.address, 4, _from(accounts[1])) # address, id, from. // position 1
	staking.stakeNft(nft.address, 5, _from(accounts[1])) # address, id, from. // position 2
	staking.stakeNft(nft.address, 6, _from(accounts[1])) # address, id, from. // position 3

	chain.sleep(arena.firstStageDuration()) # skip 1st(0) stage, now second stage(1)
	# stage 1, epoch 1 #

	daiToken.approve(voting.address, value*3, _from(accounts[1])) # address, value, from
	voting.createNewVotingPosition(1, value, True, _from(accounts[1])) # stakingPositionId, value, from // position 1
	voting.createNewVotingPosition(2, value, True, _from(accounts[1])) # stakingPositionId, value, from // position 2
	voting.createNewVotingPosition(3, value, True, _from(accounts[1])) # stakingPositionId, value, from // position 3

	daiToken.approve(voting.address, value*2, _from(accounts[1])) # address, value, from
	voting.addDaiToPosition(1, value, _from(accounts[1]))
	voting.addDaiToPosition(2, value, _from(accounts[1]))

	chain.sleep(arena.secondStageDuration()) # skip 2nd(1) stage, now third stage(2)
	# stage 2, epoch 1 #

	arena.pairNft(1, _from(accounts[1])) # pair for 1 position.

	chain.sleep(arena.thirdStageDuration()) # skip 3nd(2) stage, now fourth stage(3)
	# stage 3, epoch 1 #

	zooToken.approve(voting.address, value*2, _from(accounts[1])) # address, value, from
	voting.addZooToPosition(1, value, _from(accounts[1])) # stakingPositionId, value, from
	voting.addZooToPosition(2, value, _from(accounts[1])) # stakingPositionId, value, from

	chain.sleep(arena.fourthStageDuration()) # skip 4th(3) stage, now fifth stage(4)
	# stage 4, epoch 1 #

	arena.requestRandom()
	arena.chooseWinnerInPair(0, _from(accounts[1])) # pair index, from

	chain.sleep(arena.fifthStageDuration())
	arena.updateEpoch()

	assert arena.currentEpoch() == 2
	assert arena.getCurrentStage() == 0
	
			### stage 0, epoch 2 #

	nft.approve(staking.address, 7, _from(accounts[2])) # account 1 have nft 4,5,6
	staking.stakeNft(nft.address, 7, _from(accounts[2])) # address, id, from. // position 4

	staking.unstakeNft(1, _from(accounts[1])) # // position 1 unstaked

	voting.withdrawDaiFromVotingPosition(2, accounts[1], value/2, _from(accounts[1])) # withdraw dai from voting position 2 

	voting.withdrawZooFromVotingPosition(1, value, accounts[1], _from(accounts[1])) # withdraw zoo from voting position 1

	voting.claimRewardFromVoting(1, accounts[2], _from(accounts[1]))
	staking.claimRewardFromStaking(1, accounts[1], _from(accounts[1]))

	chain.sleep(arena.firstStageDuration()) # skip 1st(0) stage, now second stage(1)
	# stage 1, epoch 2 #

	voting.withdrawDaiFromVotingPosition(1, accounts[1], value*2, _from(accounts[1])) # liquidate voting position 1

	daiToken.approve(voting.address, value*3, _from(accounts[1])) # address, value, from
	daiToken.approve(voting.address, value*3, _from(accounts[2])) # address, value, from
	voting.createNewVotingPosition(4, value, True, _from(accounts[1])) # stakingPositionId, value, from // position 4
	voting.createNewVotingPosition(3, value, True, _from(accounts[2])) # stakingPositionId, value, from // position 5

	voting.addDaiToPosition(3, value, _from(accounts[1]))
	voting.addDaiToPosition(5, value, _from(accounts[2]))

	chain.sleep(arena.secondStageDuration()) # skip 2nd(1) stage, now third stage(2)
	# stage 2, epoch 2 #

	arena.pairNft(2, _from(accounts[1])) # pair for 1 position.

	chain.sleep(arena.thirdStageDuration()) # skip 3nd(2) stage, now fourth stage(3)
	# stage 3, epoch 2 #

	zooToken.approve(voting.address, value*2, _from(accounts[1])) # address, value, from
	zooToken.approve(voting.address, value*2, _from(accounts[2])) # address, value, from
	voting.addZooToPosition(3, value, _from(accounts[1])) # stakingPositionId, value, from
	voting.addZooToPosition(5, value, _from(accounts[2])) # stakingPositionId, value, from

	chain.sleep(arena.fourthStageDuration()) # skip 4th(3) stage, now fifth stage(4)
	# stage 4, epoch 2 #

	arena.requestRandom()
	arena.chooseWinnerInPair(0, _from(accounts[1])) # pair index, from

	chain.sleep(arena.fifthStageDuration())
	arena.updateEpoch()

	assert arena.currentEpoch() == 3
	assert arena.getCurrentStage() == 0

def test_battles_workflow_complex_multi_pairing(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listingList) = battles
	value = 100e18

	# stage 0, epoch 1 #
	# daiToken.transfer(vault.address, value*10, _from(accounts[0]))
	print("dai balance...", daiToken.balanceOf(vault))
	print("mockBalance...", vault.mockBalance())
	print("1______________________1")
	
	
	nft.approve(staking.address, 4, _from(accounts[1])) # account 1 have nft 4,5,6
	nft.approve(staking.address, 5, _from(accounts[1])) # account 1 have nft 4,5,6
	nft.approve(staking.address, 6, _from(accounts[1])) # account 1 have nft 4,5,6
	staking.stakeNft(nft.address, 4, _from(accounts[1])) # address, id, from. // position 1
	staking.stakeNft(nft.address, 5, _from(accounts[1])) # address, id, from. // position 2
	staking.stakeNft(nft.address, 6, _from(accounts[1])) # address, id, from. // position 3

	chain.sleep(arena.firstStageDuration()) # skip 1st(0) stage, now second stage(1)
	# stage 1, epoch 1 #

	daiToken.approve(voting.address, value*3, _from(accounts[1])) # address, value, from
	voting.createNewVotingPosition(1, value, True, _from(accounts[1])) # stakingPositionId, value, from // position 1
	voting.createNewVotingPosition(2, value, True, _from(accounts[1])) # stakingPositionId, value, from // position 2
	voting.createNewVotingPosition(3, value, True, _from(accounts[1])) # stakingPositionId, value, from // position 3

	daiToken.approve(voting.address, value*2, _from(accounts[1])) # address, value, from
	voting.addDaiToPosition(1, value, _from(accounts[1]))
	voting.addDaiToPosition(2, value, _from(accounts[1]))

	chain.sleep(arena.secondStageDuration()) # skip 2nd(1) stage, now third stage(2)
	# stage 2, epoch 1 #
	arena.pairNft(1, _from(accounts[1])) # pair for 1 position.
	chain.sleep(arena.thirdStageDuration()) # skip 3nd(2) stage, now fourth stage(3)
	# stage 3, epoch 1 #

	zooToken.approve(voting.address, value*2, _from(accounts[1])) # address, value, from
	voting.addZooToPosition(1, value, _from(accounts[1])) # stakingPositionId, value, from
	voting.addZooToPosition(2, value, _from(accounts[1])) # stakingPositionId, value, from
	chain.sleep(arena.fourthStageDuration()) # skip 4th(3) stage, now fifth stage(4)
	# stage 4, epoch 1 #

	arena.requestRandom()
	arena.chooseWinnerInPair(0, _from(accounts[1])) # pair index, from

	chain.sleep(arena.fifthStageDuration())
	arena.updateEpoch()

	assert arena.currentEpoch() == 2
	assert arena.getCurrentStage() == 0
			### stage 0, epoch 2 #

	nft.approve(staking.address, 7, _from(accounts[2])) # account 1 have nft 4,5,6
	staking.stakeNft(nft.address, 7, _from(accounts[2])) # address, id, from. // position 4
	
	nft.approve(staking.address, 1, _from(accounts[0])) # account 0 have nft 1,2,3
	nft.approve(staking.address, 2, _from(accounts[0])) # account 0 have nft 1,2,3
	nft.approve(staking.address, 3, _from(accounts[0])) # account 0 have nft 1,2,3
	staking.stakeNft(nft.address, 1, _from(accounts[0])) # address, id, from. // position 5
	staking.stakeNft(nft.address, 2, _from(accounts[0])) # address, id, from. // position 6
	staking.stakeNft(nft.address, 3, _from(accounts[0])) # address, id, from. // position 7

	staking.unstakeNft(1, _from(accounts[1])) # // position 1 unstaked
	voting.withdrawDaiFromVotingPosition(2, accounts[1], value/2, _from(accounts[1])) # withdraw dai from voting position 2

	# TODO: fix overflow in withdraw zoo("todo:" in arena withdrawzoo)
	# voting.withdrawZooFromVotingPosition(1, value, accounts[2], _from(accounts[1])) # withdraw zoo from voting position 1

	voting.claimRewardFromVoting(1, accounts[2], _from(accounts[1]))
	staking.claimRewardFromStaking(1, accounts[1], _from(accounts[1]))
	chain.sleep(arena.firstStageDuration()) # skip 1st(0) stage, now second stage(1)
	# stage 1, epoch 2 #
	voting.withdrawDaiFromVotingPosition(1, accounts[1], value*2, _from(accounts[1])) # liquidate voting position 1

	daiToken.approve(voting.address, value*3, _from(accounts[1])) # address, value, from
	daiToken.approve(voting.address, value*3, _from(accounts[2])) # address, value, from
	voting.createNewVotingPosition(4, value, True, _from(accounts[1])) # stakingPositionId, value, from // position 4
	voting.createNewVotingPosition(3, value, True, _from(accounts[2])) # stakingPositionId, value, from // position 5

	voting.addDaiToPosition(3, value, _from(accounts[1]))
	voting.addDaiToPosition(5, value, _from(accounts[2]))

	chain.sleep(arena.secondStageDuration()) # skip 2nd(1) stage, now third stage(2)
	# stage 2, epoch 2 #

	print("dai balance...", daiToken.balanceOf(vault))
	print("mockBalance...", vault.mockBalance())
	print("2______________________2")

	################## pair loop #################
	# # assert arena.numberOfNftsWithNonZeroVotes() == 8

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

		if stakerPositionId not in alreadyPaired and stakerPositionId in participants: # and len(participants) >= 2:  # if not in array of paired, in array of eligible for pairing, and 2 or more positions left.

			arena.pairNft(stakerPositionId)        # pair this position
			alreadyPaired.append(stakerPositionId) # add position to already paired
			pairs = arena.pairsInEpoch(2, n)       # epoch, index to get pair struct
			pairNew = pairs[1]                     # id of 2nd token in pair
			if (pairNew != 0):
				alreadyPaired.append(pairNew)          # add opponent to already paired
				participants.remove(pairNew)
			n+=1                                   # increment index
			participants.remove(stakerPositionId)

	chain.sleep(arena.thirdStageDuration()) # skip 3nd(2) stage, now fourth stage(3)
	# stage 3, epoch 2 #

	# daiToken.transfer(vault.address, value*10, _from(accounts[0]))
	daiToken.approve(vault.address, 10e18, _from(accounts[0]))
	vault.increaseMockBalance()

	zooToken.approve(voting.address, value*2, _from(accounts[1])) # address, value, from
	zooToken.approve(voting.address, value*2, _from(accounts[2])) # address, value, from
	voting.addZooToPosition(3, value, _from(accounts[1])) # stakingPositionId, value, from
	voting.addZooToPosition(5, value, _from(accounts[2])) # stakingPositionId, value, from

	chain.sleep(arena.fourthStageDuration()) # skip 4th(3) stage, now fifth stage(4)
	# stage 4, epoch 2 #
	# loop for choosing winner in every pair by pair index
	arena.requestRandom()
	for i in range(0, arena.getNftPairLength('2')): # epoch
		arena.chooseWinnerInPair(i, _from(accounts[1]))

	chain.sleep(arena.fifthStageDuration())
	arena.updateEpoch()

	assert arena.currentEpoch() == 3
	assert arena.getCurrentStage() == 0

	shares = 19696969696969696981 # tokensToShares and sharesForValue generate both that number from 20e18 dai
	pps = vault.exchangeRateCurrent.call()
	print("______________________")
	print("pricePerShare.", pps)
	print("totalSupply...", vault.totalSupply())
	print("3______________________3")
	# tokens = 20e18

	# _shareValue = vault._shareValue(shares)       # shares to tokens 1
	# sharesToTokens = arena.sharesToTokens(shares) # shares to tokens 2

	# tokensToShares = arena.tokensToShares(tokens) # dai to shares 3
	# sharesForValue = vault._sharesForValue(tokens)# dai to shares 4

	# print("dai balance...", daiToken.balanceOf(vault))
	# print("mockBalance...", vault.mockBalance())
	# print("______________________")

	# print("_shareValue...", _shareValue)   # gives 20000000000000000011
	# print("sharesToTokens", sharesToTokens)# gives 19999999999999999999
	# print("______________________")

	# print("tokensToShares", tokensToShares)#
	# print("sharesForValue", sharesForValue)#

	# assert _shareValue == sharesToTokens
############### # stage 0, epoch 3 ####################
