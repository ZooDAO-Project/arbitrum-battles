#!/usr/bin/python3

import brownie
from brownie import chain

def test_winners(winnersJackpot, accounts):
	participants = [10, 2, 31, 25, 1]
	votes = [1000000000, 100, 1000, 10000, 10]
	season = 1

	tx = winnersJackpot.chooseWinner(participants, votes, season)
	event = tx.events["WinnerChosen"]

	winner = winnersJackpot.winners(season)

	assert winner == 10
	assert event['winner'] == accounts[1]

	participants1 = [6, 5, 4, 3, 2]
	votes1 = [100 * 10 ** 18, 1000 * 10 ** 18, 1000* 10 ** 18, 10000 * 10 ** 18, 100000000000 * 10 ** 18]
	season1 = 2

	assert winnersJackpot.participants(1, 10) == 1000000000
	assert winnersJackpot.participants(1, 2) == 1000000000 + 100
	assert winnersJackpot.participants(1, 31) == 1000000000 + 100 + 1000
	assert winnersJackpot.participants(1, 25) == 1000000000 + 100 + 1000 + 10000
	assert winnersJackpot.participants(1, 1) == 1000011110

	with brownie.reverts('requestRandom has not been called'):
		tx1 = winnersJackpot.chooseWinner(participants1, votes1, season1)

	with brownie.reverts('winner has been chosen'):
		tx1 = winnersJackpot.chooseWinner(participants1, votes1, season)


def test_event(winnersJackpot, battles, tokens, accounts):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	participants = [1, 2, 6, 25, 31]
	votes = [10, 100, 1000000000, 10000, 1000]
	season = 1
	daiBalance = daiToken.balanceOf(winnersJackpot)
	zooBalance = zooToken.balanceOf(winnersJackpot)

	print("dai balance", daiBalance)
	tx = winnersJackpot.chooseWinner(participants, votes, season)
	event = tx.events["WinnerChosen"]

	winner = event['winner']
	winnerId = event["winnerId"]
	totalParticipants = event["totalParticipants"]
	totalVotes = event["totalVotes"]
	fraxReward = event["fraxReward"]
	zooReward = event["zooReward"]

	assert winner == accounts[1]
	assert winnerId == 6
	assert totalParticipants == 5
	assert totalVotes == 1000011110
	assert fraxReward == daiBalance
	assert zooReward == zooBalance


def test_balance(winnersJackpot, battles, tokens, accounts):
	(vault, functions, governance, staking, voting, arena, listing) = battles
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens

	participants1 = [6, 5, 4, 3, 2]
	votes1 = [100 * 10 ** 18, 1000 * 10 ** 18, 1000* 10 ** 18, 10000 * 10 ** 18, 100000000000 * 10 ** 18]
	season = 1

	daiBalance = daiToken.balanceOf(winnersJackpot)
	print("dai balance contract", daiBalance)
	zooBalance = zooToken.balanceOf(winnersJackpot)
	print("zoo balance contrac", zooBalance)

	daiBalanceWinner = daiToken.balanceOf(accounts[0])
	print("dai balance winner", daiBalanceWinner)
	zooBalanceWinner = zooToken.balanceOf(accounts[0])
	print("zoo balance winner", zooBalanceWinner)

	tx = winnersJackpot.chooseWinner(participants1, votes1, season)
	tx.events["WinnerChosen"]

	event = tx.events['WinnerChosen']
	winner = event['winner']
	winnerId = event["winnerId"]
	totalParticipants = event["totalParticipants"]
	totalVotes = event["totalVotes"]
	fraxReward = event["fraxReward"]
	zooReward = event["zooReward"]

	daiBalance1 = daiToken.balanceOf(winnersJackpot)
	print("dai balance contract", daiBalance1)

	zooBalance1 = zooToken.balanceOf(winnersJackpot)
	print("zoo balance contract", zooBalance1)

	assert daiBalance1 == daiBalance - fraxReward
	assert zooBalance1 == zooBalance - zooReward

	daiBalanceWinner1 = daiToken.balanceOf(accounts[0])
	print("dai balance winner", daiBalanceWinner1)
	zooBalanceWinner1 = zooToken.balanceOf(accounts[0])
	print("zoo balance winner", zooBalanceWinner1)

	assert daiBalanceWinner1 == daiBalanceWinner + fraxReward
	assert zooBalanceWinner1 == zooBalanceWinner + zooReward

	assert winner == accounts[0]
	assert winnerId == 2
	assert totalParticipants == 5
	assert totalVotes == 100000012100000000000000000000
	assert fraxReward == daiBalance
	assert zooReward == zooBalance