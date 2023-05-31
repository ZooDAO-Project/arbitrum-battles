import brownie

def test_allowing_new_contract_for_staking(accounts, listing):
	lisintList = listing[0]
	nft = '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D'
	tx = lisintList.allowNewContractForStaking(nft, accounts[-4], {"from": accounts[0]})

	# Was contract added to mapping?
	assert lisintList.eligibleCollections(nft)


def test_only_owner(accounts, listing):
	lisintList = listing[0]
	nft = '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D'

	with brownie.reverts("Ownable: caller is not the owner"):
		lisintList.allowNewContractForStaking(nft, accounts[-4], {"from": accounts[1] })


def test_emitting_event(accounts, listing):
	lisintList = listing[0]
	nft = '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D'
	tx = lisintList.allowNewContractForStaking(nft, accounts[-4], {"from": accounts[0]})

	# Checking "NewContractAllowed" event
	assert len(tx.events) == 1
	assert tx.events[0]["collection"] == nft
