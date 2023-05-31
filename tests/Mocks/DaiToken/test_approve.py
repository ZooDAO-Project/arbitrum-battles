def _from(account):
	return {"from": account}

def test_approve(accounts, Dai):
	daiToken = Dai.deploy(1, {"from": accounts[0]})
	daiToken.mint(accounts[0], 1e20, {"from": accounts[0]})

	daiToken.approve(accounts[1], 1e20, _from(accounts[0]))

	tx = daiToken.transferFrom(accounts[0], accounts[2], 1e20, _from(accounts[1]))

	assert tx.status == 1
	assert daiToken.balanceOf(accounts[2]) == 1e20