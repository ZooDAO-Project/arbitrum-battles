import brownie

# def test_choose_winner(accounts, finished_epoch, iterable_mapping_library):
# 	(vault, functions, governance, staking, voting, arena, listing, xZoo, jackpotA, jackpotB) = finished_epoch[1]

# 	position_id = 1
# 	staking.approve(jackpotA, position_id)
# 	tx1 = jackpotA.stake(position_id, accounts[0])
# 	tx2 = jackpotA.chooseWinner(1)

# 	assert jackpotA.winners(1) == 1
# 	assert jackpotA.checkReward(1, 1) != 0

# 	tx3 = jackpotA.claimReward(1, 1, accounts[-1])

# 	assert tx3.return_value != 0