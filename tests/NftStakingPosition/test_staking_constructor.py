import brownie

def test_set_constructor_arguments(accounts, NftStakingPosition, base_zoo_functions):
	name = 'Name'
	symbol = 'NM'

	listing = '0x0000000000000000000000000000000000000001'
	zoo = '0x0000000000000000000000000000000000000002'

	staking = NftStakingPosition.deploy(name, symbol, listing, zoo, base_zoo_functions, accounts[0], {"from": accounts[0]})
	
	assert staking.name() == name
	assert staking.symbol() == symbol
	assert staking.listingList() == listing
	assert staking.zoo() == zoo


def test_owner(accounts, NftStakingPosition, base_zoo_functions):
	name = 'Name'
	symbol = 'NM'
	
	listing = '0x0000000000000000000000000000000000000001'
	zoo = '0x0000000000000000000000000000000000000002'

	staking = NftStakingPosition.deploy(name, symbol, listing, zoo, base_zoo_functions, accounts[0], {"from": accounts[9]})
	
	assert staking.owner() == accounts[9]
