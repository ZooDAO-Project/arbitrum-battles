#!/usr/bin/python3
import pytest

import brownie
from brownie import chain

from _utils.utils import _from, pair_all_nfts


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
	# perform a chain rewind after completing each test, to ensure proper isolation
	# https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
	pass


@pytest.fixture(scope="module")
def veBal(accounts, tokens, GaugeMock, VeBalRewardMock):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	gauge = GaugeMock.deploy(zooToken, {"from": accounts[0]})
	vebal = VeBalRewardMock.deploy(zooToken, gauge, {"from": accounts[0]})

	return (gauge, vebal)


@pytest.fixture(scope="module")
def winnersJackpot(fifth_stage, WinnersJackpot, accounts):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	#rewardAmount = 2500 * 10 ** 18
	winnersJackpot = WinnersJackpot.deploy(functions, voting, daiToken, zooToken, {"from": accounts[0]})
	arena.requestRandom()

	zooToken.transfer(winnersJackpot.address, 10e25, {"from": accounts[0]})
	daiToken.mint(winnersJackpot.address, 10e25, {"from": accounts[0]})

	return (winnersJackpot)

@pytest.fixture(scope="module")
def testnet(accounts, ZooTokenFaucet, ZooTokenMock):

	# nft = ZooNft.deploy("zNFT", "zNFT", {"from": accounts[0]}) # testnet nft contract 1
	# nft1 = ZooNft.deploy("zNFT1", "zNFT1", {"from": accounts[0]}) # testnet nft contract 2
	# nft2 = ZooNft.deploy("zNFT2", "zNFT2", {"from": accounts[0]}) # testnet nft contract 3
	# nft3 = ZooNft.deploy("zNFT3", "zNFT3", {"from": accounts[0]}) # testnet nft contract 4

	zooToken = ZooTokenMock.deploy("name", "symbol", "18", 1e26, {"from": accounts[0]})
	# daiToken = Dai.deploy(1, {"from": accounts[0]})
	faucet = ZooTokenFaucet.deploy(zooToken, 1, {"from": accounts[0]})

	# nft.transferOwnership(faucet.address)
	# nft1.transferOwnership(faucet.address)
	# nft2.transferOwnership(faucet.address)
	# nft3.transferOwnership(faucet.address)

	zooToken.transfer(faucet.address, 4e25, {"from": accounts[0]})
	# daiToken.mint(faucet.address, 4e25, {"from": accounts[0]})

	return faucet

@pytest.fixture(scope="module")
def tokens(accounts, ZooNftFaucet, ZooTokenMock, Dai):
	zooToken = ZooTokenMock.deploy("name", "symbol", "18", 2e26, {"from": accounts[0]}) # should be LP zoo-mim token
	# daiToken = ZooTokenMock.deploy("name", "symbol", "18", 1e26, {"from": accounts[0]})
	notLpZoo = ZooTokenMock.deploy("name", "symbol", "18", 2e26, {"from": accounts[0]}) # actual zoo token, not LP.
	daiToken = Dai.deploy(1, {"from": accounts[0]})
	linkToken = ZooTokenMock.deploy("name", "symbol", "18", 1e26, {"from": accounts[0]})

	zooToken.transfer(accounts[1], 4e25, {"from": accounts[0]})
	zooToken.transfer(accounts[2], 4e25, {"from": accounts[0]})

	daiToken.mint(accounts[0], 4e25, {"from": accounts[0]})
	daiToken.mint(accounts[1], 4e25, {"from": accounts[0]})
	daiToken.mint(accounts[2], 4e25, {"from": accounts[0]})

	nft = ZooNftFaucet.deploy("name", "symbol", {"from": accounts[0]})
	nft.addToWhiteList(accounts[0], {"from": accounts[0]})
	nft.batchMint([accounts[0], accounts[1], accounts[2]], 3, {"from": accounts[0]})

	return (zooToken, daiToken, linkToken, nft, notLpZoo)

# @pytest.fixture(scope="module")
# def well(accounts, ERC20PresetMinterPauser):
# 	token = ERC20PresetMinterPauser.deploy("well", "WELL", {"from": accounts[0]})
# 	token.mint(accounts[0], 4e25, {"from": accounts[0]})
# 	return token

# @pytest.fixture(scope="module")
# def wGlmr(accounts, WETH9):
# 	return WETH9.deploy({"from": accounts[0]})

# @pytest.fixture(scope="module")
# def token_controller(accounts, well, ControllerMock):
# 	controller = ControllerMock.deploy(well.address, {"from": accounts[0]})
# 	well.transfer(controller.address, 4e25)
# 	accounts[0].transfer(controller.address, 50 * 1e18)
# 	return controller

@pytest.fixture(scope="module")
def listing(accounts, tokens, ListingList):
	zooToken = tokens[0]

	listingList = ListingList.deploy(zooToken, 4, {"from": accounts[0]})

	return (listingList, zooToken)

@pytest.fixture(scope="module")
def vault(YearnMock, tokens, accounts):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	return YearnMock.deploy(daiToken.address, {"from": accounts[0]}) # dai address/mock 

@pytest.fixture(scope="module")
def staking(NftStakingPosition, listing, tokens, accounts, base_zoo_functions):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	listingList = listing[0]

	return NftStakingPosition.deploy("zStakerPosition", "ZSP", listingList.address, zooToken.address, base_zoo_functions.address, accounts[0], {"from": accounts[0]})

@pytest.fixture(scope="module")
def voting(NftVotingPosition, tokens, accounts, base_zoo_functions):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	# note what zooToken now LP zoo for arbitrum.
	return NftVotingPosition.deploy("zVoterPosition", "ZVP", daiToken.address, notLpZoo.address, zooToken.address, base_zoo_functions.address, accounts[0], {"from": accounts[0]})

# @pytest.fixture(scope="module")
# def xZoo(XZoo, tokens, vault, accounts):
# 	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

# 	return XZoo.deploy("xZoo", "XZOO", daiToken.address, zooToken.address, vault.address, {"from": accounts[0]})

@pytest.fixture(scope="module")
def iterable_mapping_library(IterableMapping, accounts):
	return IterableMapping.deploy({"from": accounts[0]})

@pytest.fixture(scope="module")
def base_zoo_functions(accounts, tokens, BaseZooFunctions):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens

	# return BaseZooFunctions.deploy(accounts[0], linkToken.address, {"from": accounts[0]}) # vrfCoordinator and link token addresses.
	return BaseZooFunctions.deploy({"from": accounts[0]}) # vrfCoordinator and link token addresses.

# @pytest.fixture(scope="module")
# def jackpotA(Jackpot, staking, vault, iterable_mapping_library, base_zoo_functions, accounts):

# 	return Jackpot.deploy(staking.address, vault.address, base_zoo_functions, "Jackpot A", "JKPTA", {"from": accounts[0]})

# @pytest.fixture(scope="module")
# def jackpotB(Jackpot, voting, vault, iterable_mapping_library, base_zoo_functions, accounts):

# 	return Jackpot.deploy(voting.address, vault.address, base_zoo_functions, "Jackpot B", "JKPTB", {"from": accounts[0]})

@pytest.fixture(scope="module")
def battles(accounts, tokens, vault, listing, staking, voting, base_zoo_functions, ZooGovernance, NftBattleArena, veBal):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(gauge, veBal) = veBal

	listingList = listing[0]
	zooVoteRate = 1

	#functions = BaseZooFunctions.deploy(accounts[0], linkToken.address, {"from": accounts[0]}) # vrfCoordinator and link token addresses.
	governance = ZooGovernance.deploy(base_zoo_functions.address, accounts[0], {"from": accounts[0]})         # functions address and aragon(owner) address.

	daiToken.mint(vault, 1e25, _from(accounts[0]))

	arena = NftBattleArena.deploy(
		zooToken.address,# now it should be new LpZoo, but instead new token mock will be in incentives for easier refactoring tests.
		daiToken.address,
		vault.address,
		governance.address,
		accounts[0],
		#accounts[0],
		# accounts[0],# team address
		staking.address,
		voting.address,
		listingList.address,
		{"from": accounts[0]})

	arena.init(veBal, gauge, zooVoteRate, notLpZoo)

	# xZoo.setNftBattleArena(arena.address)
	# jackpotA.setNftBattleArena(arena.address)
	# jackpotB.setNftBattleArena(arena.address)
	staking.setNftBattleArena(arena.address, {"from": accounts[0]})
	voting.setNftBattleArena(arena.address, {"from": accounts[0]})
	base_zoo_functions.init(arena.address, accounts[0], {"from": accounts[0]})                      # connect functions with battleStaker
	listingList.init(arena.address)
	# vault.transferOwnership(arena.address, {"from": accounts[0]})                           # only arena can deposit and withdraw directly.

	royalty_receiver = accounts[9]
	listingList.allowNewContractForStaking(nft.address, royalty_receiver, {"from": accounts[0]})

	zooToken.transfer(staking, arena.baseStakerReward() * 100)

	return (vault, base_zoo_functions, governance, staking, voting, arena, listingList)

# @pytest.fixture(scope="module")
# def tokens_advanced(accounts, ZooNftFaucet, ZooTokenMock, Dai):
# 	zooSupply = 1e26 
# 	zooToken = ZooTokenMock.deploy("name", "symbol", "18", zooSupply, {"from": accounts[0]})
# 	daiToken = Dai.deploy(1, {"from": accounts[0]})
# 	linkToken = ZooTokenMock.deploy("name", "symbol", "18", 1e26, {"from": accounts[0]})

# 	for i in range(1, 10):
# 		zooToken.transfer(accounts[i], 1e26 / 10, {"from": accounts[0]})

# 	for i in range(10):
# 		daiToken.mint(accounts[i], 1e25, {"from": accounts[0]})

# 	nft = ZooNftFaucet.deploy("name", "symbol", {"from": accounts[0]})
# 	nft.addToWhiteList(accounts[0], {"from": accounts[0]})
# 	nft.batchMint(list(accounts), 10, {"from": accounts[0]})

# 	return (zooToken, daiToken, linkToken, nft)


# @pytest.fixture(scope="module")
# def battles_advanced(accounts, tokens_advanced, vault, BaseZooFunctions, ZooGovernance, NftBattleArena, NftStakingPosition, NftVotingPosition):
# 	(zooToken, daiToken, linkToken, nft) = tokens_advanced

# 	functions = BaseZooFunctions.deploy(accounts[0], linkToken.address, {"from": accounts[0]}) # vrfCoordinator and link token addresses.
# 	governance = ZooGovernance.deploy(functions.address, accounts[0], {"from": accounts[0]})         # functions address and aragon(owner) address.

# 	daiToken.mint(vault, 1e25, _from(accounts[0]))

# 	staking = NftStakingPosition.deploy("zStakerPosition", "ZSP", {"from": accounts[0]})
# 	voting = NftVotingPosition.deploy("zVoterPosition", "ZVP", daiToken.address, zooToken.address, {"from": accounts[0]})
# 	arena = NftBattleArena.deploy(zooToken.address, daiToken.address, vault.address, governance.address, accounts[0], accounts[0], accounts[0], staking.address, voting.address, {"from": accounts[0]})

# 	staking.setNftBattleArena(arena.address, {"from": accounts[0]})
# 	voting.setNftBattleArena(arena.address, {"from": accounts[0]})
# 	functions.init(arena.address, accounts[0], {"from": accounts[0]})                      # connect functions with battleStaker
# 	# vault.transferOwnership(arena.address, {"from": accounts[0]})                           # only arena can deposit and withdraw directly.

# 	# staker.allowNewContractForStaking(nft.address, {"from": account}) # Allow contract nft.
# 	return (vault, functions, governance, staking, voting, arena, listing)


# Ready different stages
@pytest.fixture(scope="module")
def second_stage(accounts, tokens, battles):
	(zooToken, daiToken, linkToken, nft, notLpZoo) = tokens
	(vault, functions, governance, staking, voting, arena, listingList) = battles

	participant_number = 3
	stakes_by_participant = 3

	for i in range(participant_number):
		for j in range(stakes_by_participant):
			
			position = j + i * 3 + 1
			nft.approve(staking, position, _from(accounts[i]))
			staking.stakeNft(nft, position, _from(accounts[i]))

	chain.sleep(arena.firstStageDuration())
	
	# mine new block to move to next stage
	chain.mine(1)

	zooToken.approve(listingList, 1e20)
	listingList.voteForNftCollection(nft.address, 1e20)

	return ((zooToken, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listingList))


@pytest.fixture(scope="module")
def third_stage(accounts, second_stage):
	(zooToken, daiToken, linkToken, nft) = second_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = second_stage[1]

	# Every account votes for his NFTs
	for i in range(3):
		daiToken.approve(voting, 1e21, _from(accounts[i]))
		
		for j in range(3):
			staking_position = 1 + j + i * 3
			voting.createNewVotingPosition(staking_position, 1e20, True, _from(accounts[i]))

	secondStage = arena.secondStageDuration()
	secondStagePart = secondStage // 10
	chain.sleep(secondStagePart * 8)

	voting.createNewVotingPosition(9, 1e20, True, _from(accounts[1])) # position with lower than 1.3 votes rate.

	chain.sleep(secondStagePart * 2)
	
	# mine new block to move to next stage
	chain.mine(1)

	return ((zooToken, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listing))


@pytest.fixture(scope="module")
def fourth_stage(accounts, third_stage):
	(zooToken, daiToken, linkToken, nft) = third_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = third_stage[1]
	
	epoch = arena.currentEpoch()

	pair_all_nfts(arena)

	chain.sleep(arena.thirdStageDuration())

	# mine new block to move to next stage
	chain.mine(1)

	return ((zooToken, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listing))


@pytest.fixture(scope="module")
def fifth_stage(accounts, fourth_stage):
	(zooToken, daiToken, linkToken, nft) = fourth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fourth_stage[1]

	# Every account votes for his NFTs
	amount = 1e21

	for i in reversed(range(3)):
		zooToken.approve(voting, amount, _from(accounts[i]))

		for j in range(3):
			voting.addZooToPosition(j + i * 3 + 1, amount / 10, _from(accounts[i]))

	chain.sleep(arena.fourthStageDuration())

	# mine new block to move to next stage
	chain.mine(1)

	return ((zooToken, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listing))


@pytest.fixture(scope="module")
def finished_epoch(fifth_stage):
	(zooToken, daiToken, linkToken, nft) = fifth_stage[0]
	(vault, functions, governance, staking, voting, arena, listing) = fifth_stage[1]

	arena.requestRandom()
	vault.increaseMockBalance()

	# Choosing winner in every pair
	for i in range(4):
		arena.chooseWinnerInPair(i)

	chain.mine(1)

	return ((zooToken, daiToken, linkToken, nft), (vault, functions, governance, staking, voting, arena, listing))
