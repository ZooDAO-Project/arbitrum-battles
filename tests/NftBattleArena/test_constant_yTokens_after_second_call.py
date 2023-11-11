import brownie
from brownie import chain

def test_constant_yTokens_after_second_withdraw_dai(accounts, fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	chain.sleep(arena.fifthStageDuration())

	arena.updateEpoch()

	position_index = 1
	owner = accounts[0]
	voting_position = arena.votingPositionsValues(position_index)
	dai_number = voting_position["daiInvested"] - voting_position["zooInvested"]
	tx1 = voting.withdrawDaiFromVotingPosition(position_index, owner, dai_number // 2, {"from": owner})

	y_tokens = arena.votingPositionsValues(position_index)["yTokensNumber"]

	tx2 = voting.withdrawDaiFromVotingPosition(position_index, owner, 0, {"from": owner})

	assert y_tokens == arena.votingPositionsValues(position_index)["yTokensNumber"]
