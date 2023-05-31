from brownie import *

def get_votes_for_positions(arena, position_array):
	votes = []
	for id in position_array:
		r = arena.votingPositionsValues(id)
		votes.append(r["votes"])

	return votes

def main(jackpot):
	active_network = network.show_active()
	account = accounts.load(active_network)

	return 0