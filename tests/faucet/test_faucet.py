#!/usr/bin/python3

import brownie
from brownie import chain

# def test_mint(accounts, tokens, testnet):
# 	(zooToken, daiToken, linkToken, nft) = tokens
# 	(nft, nft1, nft2, nft3, faucet) = testnet

# 	faucet.getNfts({"from": accounts[0]})
	
# 	print(faucet.balanceOf(accounts[0]), "faucet")
# 	print(nft.balanceOf(accounts[0]), "nft")
# 	print(nft1.balanceOf(accounts[0]), "nft1")
# 	print(nft2.balanceOf(accounts[0]), "nft2")
# 	print(nft3.balanceOf(accounts[0]), "nft3")
# 	print("_______________")
# 	print(faucet.balanceOf(faucet), "faucet")
# 	print(nft.balanceOf(faucet), "nft")
# 	print(nft1.balanceOf(faucet), "nft1")
# 	print(nft2.balanceOf(faucet), "nft2")
# 	print(nft3.balanceOf(faucet), "nft3")

# 	with brownie.reverts("reached attempt limit"):
# 		faucet.getNfts({"from": accounts[0]})
	
# 	assert faucet.attemptAmountNft(accounts[0]) == 1
# 	assert nft.balanceOf(faucet) == 0
# 	assert nft1.balanceOf(faucet) == 0
# 	assert nft2.balanceOf(faucet) == 0
# 	assert nft3.balanceOf(faucet) == 0
# 	assert nft.balanceOf(accounts[0]) == 2 or nft1.balanceOf(accounts[0]) == 2 or nft2.balanceOf(accounts[0]) == 2 or nft3.balanceOf(accounts[0]) == 2

def test_getTokens(accounts, tokens, testnet):
	(zooToken, daiToken, linkToken, nft, lpZoo) = tokens
	(faucet) = testnet

	print(faucet.attemptLimit(), "attemptLimit")
	print(faucet.attemptAmount(accounts[0]), "attemptAmount")

	faucet.getZoo({"from": accounts[0]})
	print(faucet.attemptAmount(accounts[0]), "attemptAmount")

	with brownie.reverts("reached attempt limit"):
		faucet.getZoo({"from": accounts[0]})

	assert faucet.attemptAmount(accounts[0]) == 1



