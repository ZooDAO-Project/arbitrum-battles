import brownie
from brownie import *

def _from(account):
	return {"from": account}


def test_pairing_and_chooseWinner_with_id0_in_different_leagues(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listingList) = battles
	approveAmount = 250000e18

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

	daiToken.approve(voting.address, approveAmount, _from(accounts[1])) # address, value, from
	voting.createNewVotingPosition(1, 200e18, True, _from(accounts[1])) # stakingPositionId, value, from // position 1 wooden league
	voting.createNewVotingPosition(2, 110000e18, True, _from(accounts[1])) # stakingPositionId, value, from // position 2 platinum league
	voting.createNewVotingPosition(3, 5500e18, True, _from(accounts[1])) # stakingPositionId, value, from // position 3 silver league

	chain.sleep(arena.secondStageDuration()) # skip 2nd(1) stage, now third stage(2)
	# stage 2, epoch 1 #

	# pairing, every position should pair to id 0.
	tx = arena.pairNft(1, _from(accounts[1])) # pair for 1 position.
	tx1 = arena.pairNft(2, _from(accounts[1])) # pair for 2 position.
	tx2 = arena.pairNft(3, _from(accounts[1])) # pair for 3 position.

	event = tx.events["PairedNft"]
	event1 = tx1.events["PairedNft"]
	event2 = tx2.events["PairedNft"]

	assert event["currentEpoch"] == arena.currentEpoch()
	assert event["fighter1"] == 1
	assert event["fighter2"] == 0
	assert event["pairIndex"] == 0

	assert event1["currentEpoch"] == arena.currentEpoch()
	assert event1["fighter1"] == 2
	assert event1["fighter2"] == 0
	assert event1["pairIndex"] == 1

	assert event2["currentEpoch"] == arena.currentEpoch()
	assert event2["fighter1"] == 3
	assert event2["fighter2"] == 0
	assert event2["pairIndex"] == 2


	chain.sleep(arena.thirdStageDuration()) # skip 3nd(2) stage, now fourth stage(3)
	# stage 3, epoch 1 #
	chain.sleep(arena.fourthStageDuration()) # skip 4th(3) stage, now fifth stage(4)
	# stage 4, epoch 1 #

	arena.requestRandom()
	tx3 = arena.chooseWinnerInPair(0, _from(accounts[1])) # pair index, from
	tx4 = arena.chooseWinnerInPair(1, _from(accounts[1])) # pair index, from
	tx5 = arena.chooseWinnerInPair(2, _from(accounts[1])) # pair index, from

	chain.sleep(arena.fifthStageDuration())
	arena.updateEpoch()

	event3 = tx3.events["ChosenWinner"]
	event4 = tx4.events["ChosenWinner"]
	event5 = tx5.events["ChosenWinner"]

	assert event3["currentEpoch"] == 1
	assert event3["fighter1"] == 1
	assert event3["fighter2"] == 0
	print(event3["winner"], "winner 1")
	assert event3["pairIndex"] == 0
	assert event3["playedPairsAmount"] == 1
	print(arena.rewardsForEpoch(1,1)["zooRewards"])
	reward = 0
	if (event3["winner"] == True):
		reward = 21e18

	assert arena.rewardsForEpoch(1,1)["zooRewards"] == reward
	print(arena.rewardsForEpoch(1,1)["zooRewards"])

	assert event4["currentEpoch"] == 1
	assert event4["fighter1"] == 2
	assert event4["fighter2"] == 0
	print(event4["winner"], "winner 2")
	assert event4["pairIndex"] == 1
	assert event4["playedPairsAmount"] == 2

	reward1 = 0
	if (event4["winner"] == True):
		reward1 = 12345e18

	assert arena.rewardsForEpoch(2,1)["zooRewards"] == reward1
	print(arena.rewardsForEpoch(2,1)["zooRewards"])

	assert event5["currentEpoch"] == 1
	assert event5["fighter1"] == 3
	assert event5["fighter2"] == 0
	print(event5["winner"], "winner 3")
	assert event5["pairIndex"] == 2
	assert event5["playedPairsAmount"] == 3

	reward2 = 0
	if (event5["winner"] == True):
		reward2 = 1818e18

	assert arena.rewardsForEpoch(3,1)["zooRewards"] == reward2
	print(arena.rewardsForEpoch(3,1)["zooRewards"])

	assert arena.currentEpoch() == 2
	assert arena.getCurrentStage() == 0


def test_pairing_and_chooseWinner_in_different_leagues(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listingList) = battles
	approveAmount = 250000e18

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

	nft.approve(staking.address, 1, _from(accounts[0]))
	staking.stakeNft(nft.address, 1, _from(accounts[0])) # 4
	nft.approve(staking.address, 2, _from(accounts[0]))
	staking.stakeNft(nft.address, 2, _from(accounts[0])) # 5
	nft.approve(staking.address, 3, _from(accounts[0]))
	staking.stakeNft(nft.address, 3, _from(accounts[0])) # 6

	chain.sleep(arena.firstStageDuration()) # skip 1st(0) stage, now second stage(1)
	# stage 1, epoch 1 #

	daiToken.approve(voting.address, approveAmount, _from(accounts[1])) # address, value, from
	voting.createNewVotingPosition(1, 200e18, True, _from(accounts[1])) # stakingPositionId, value, from // position 1 wooden league
	voting.createNewVotingPosition(2, 110000e18, True, _from(accounts[1])) # stakingPositionId, value, from // position 2 platinum league
	voting.createNewVotingPosition(3, 5500e18, True, _from(accounts[1])) # stakingPositionId, value, from // position 3 silver league

	daiToken.approve(voting.address, approveAmount, _from(accounts[0])) # address, value, from
	voting.createNewVotingPosition(4, 200e18, True, _from(accounts[0])) # stakingPositionId, value, from // position 4 wooden league
	voting.createNewVotingPosition(5, 110000e18, True, _from(accounts[0])) # stakingPositionId, value, from // position 5 platinum league
	voting.createNewVotingPosition(6, 5500e18, True, _from(accounts[0])) # stakingPositionId, value, from // position 6 silver league

	chain.sleep(arena.secondStageDuration()) # skip 2nd(1) stage, now third stage(2)
	# stage 2, epoch 1 #

	# pairing, every position should pair to id 0.
	tx = arena.pairNft(1, _from(accounts[1])) # pair for 1 position.
	tx1 = arena.pairNft(2, _from(accounts[1])) # pair for 2 position.
	tx2 = arena.pairNft(3, _from(accounts[1])) # pair for 3 position.

	event = tx.events["PairedNft"]
	event1 = tx1.events["PairedNft"]
	event2 = tx2.events["PairedNft"]

	assert event["currentEpoch"] == arena.currentEpoch()
	assert event["fighter1"] == 1
	assert event["fighter2"] == 4
	assert event["pairIndex"] == 0

	assert event1["currentEpoch"] == arena.currentEpoch()
	assert event1["fighter1"] == 2
	assert event1["fighter2"] == 5
	assert event1["pairIndex"] == 1

	assert event2["currentEpoch"] == arena.currentEpoch()
	assert event2["fighter1"] == 3
	assert event2["fighter2"] == 6
	assert event2["pairIndex"] == 2


	chain.sleep(arena.thirdStageDuration()) # skip 3nd(2) stage, now fourth stage(3)
	# stage 3, epoch 1 #
	chain.sleep(arena.fourthStageDuration()) # skip 4th(3) stage, now fifth stage(4)
	# stage 4, epoch 1 #

	arena.requestRandom()
	tx3 = arena.chooseWinnerInPair(0, _from(accounts[1])) # pair index, from
	tx4 = arena.chooseWinnerInPair(1, _from(accounts[1])) # pair index, from
	tx5 = arena.chooseWinnerInPair(2, _from(accounts[1])) # pair index, from

	chain.sleep(arena.fifthStageDuration())
	arena.updateEpoch()

	event3 = tx3.events["ChosenWinner"]
	event4 = tx4.events["ChosenWinner"]
	event5 = tx5.events["ChosenWinner"]

	assert event3["currentEpoch"] == 1
	assert event3["fighter1"] == 1
	assert event3["fighter2"] == 4
	print(event3["winner"], "winner 1")
	assert event3["pairIndex"] == 0
	assert event3["playedPairsAmount"] == 1
	print(arena.rewardsForEpoch(1,1)["zooRewards"])

	assert arena.rewardsForEpoch(1,1)["zooRewards"] == 0
	print(arena.rewardsForEpoch(1,1)["zooRewards"])

	assert event4["currentEpoch"] == 1
	assert event4["fighter1"] == 2
	assert event4["fighter2"] == 5
	print(event4["winner"], "winner 2")
	assert event4["pairIndex"] == 1
	assert event4["playedPairsAmount"] == 2

	assert arena.rewardsForEpoch(2,1)["zooRewards"] == 0
	print(arena.rewardsForEpoch(2,1)["zooRewards"])

	assert event5["currentEpoch"] == 1
	assert event5["fighter1"] == 3
	assert event5["fighter2"] == 6
	print(event5["winner"], "winner 3")
	assert event5["pairIndex"] == 2
	assert event5["playedPairsAmount"] == 3

	assert arena.rewardsForEpoch(3,1)["zooRewards"] == 0
	print(arena.rewardsForEpoch(3,1)["zooRewards"])

	assert arena.currentEpoch() == 2
	assert arena.getCurrentStage() == 0