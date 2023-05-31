from brownie import chain


def test_random_numbers(battles):
	(vault, functions, governance, staking, voting, arena, listing) = battles

	for i in range(50):
		random_number = functions.computePseudoRandom()
		print(random_number)

		chain.mine(1)
