import brownie
from brownie import *

def test_one_collection_incentive_reward_of_staker(accounts, finished_epoch: tuple[tuple, tuple]):
    (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
    (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

    arena.updateInfoAboutStakedNumber(nft)
    assert arena.numberOfStakedNftsInCollection(1, nft) > 0
    assert arena.numberOfStakedNftsInCollection(2, nft) > 0

    tx = staking.claimIncentiveStakerReward(1, accounts[-1], {"from": accounts[0]})

    assert tx.return_value > 0
    assert zooToken.balanceOf(accounts[-1]) > 0

def test_no_rewards_after_finish_epoch(accounts, finished_epoch: tuple[tuple, tuple]):
    (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
    (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
    
    tx = staking.claimIncentiveStakerReward(1, accounts[-1], {"from": accounts[0]})

    assert tx.return_value > 0
    assert zooToken.balanceOf(accounts[-1]) > 0
    
    while arena.currentEpoch() < arena.endEpochOfIncentiveRewards():
        chain.sleep(arena.epochDuration() + 1)
        chain.mine(1)
        arena.updateEpoch({"from": accounts[0]})
        tx = staking.claimIncentiveStakerReward(1, accounts[-1], {"from": accounts[0]})
        assert tx.return_value > 0
        
    chain.sleep(arena.epochDuration() + 1)
    chain.mine(1)
    arena.updateEpoch({"from": accounts[0]})    

    tx = staking.claimIncentiveStakerReward(1, accounts[-1], {"from": accounts[0]})
    assert tx.return_value == 0
    
def test_one_collection_incentive_reward_of_voter(accounts, finished_epoch: tuple[tuple, tuple]):
    (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
    (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]

    arena.updateInfoAboutStakedNumber(nft)
    assert arena.numberOfStakedNftsInCollection(1, nft) > 0
    assert arena.numberOfStakedNftsInCollection(2, nft) > 0

    tx = voting.claimIncentiveVoterReward(1, accounts[-1], {"from": accounts[0]})

    assert tx.return_value > 0

def test_incentive_reward_in_new_epoch(accounts, finished_epoch: tuple[tuple, tuple]):
    (zooToken, daiToken, linkToken, nft) = finished_epoch[0]
    (vault, functions, governance, staking, voting, arena, listing) = finished_epoch[1]
    
    tx1 = voting.claimIncentiveVoterReward(1, accounts[-1], {"from": accounts[0]})

    assert tx1.return_value > 0
    
    while arena.currentEpoch() < arena.endEpochOfIncentiveRewards():
        chain.sleep(arena.firstStageDuration() + arena.secondStageDuration() + 1)
        chain.mine(1)
        arena.pairNft(1)
        chain.sleep(arena.thirdStageDuration() + 1)
        chain.mine(1)
        chain.sleep(arena.fourthStageDuration() + arena.fifthStageDuration() + 1)
        arena.requestRandom()
        vault.increaseMockBalance() # Generate yield.
        arena.chooseWinnerInPair(0)
        lastEpochOfIncentiveReward = arena.votingPositionsValues(1)["lastEpochOfIncentiveReward"]
        tx2 = voting.claimIncentiveVoterReward(1, accounts[-1], {"from": accounts[0]})
        assert arena.votingPositionsValues(1)["lastEpochOfIncentiveReward"] > lastEpochOfIncentiveReward
        assert tx2.return_value > 0
        
    chain.sleep(arena.epochDuration() + 1)
    chain.mine(1)
    arena.updateEpoch({"from": accounts[0]})    

    tx3 = voting.claimIncentiveVoterReward(1, accounts[-1], {"from": accounts[0]})
    assert tx3.return_value == 0
