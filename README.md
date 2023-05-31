# ZooDAO 
## Nft battles arena

#### This repository contains system of contracts associated with Nft battles of the ZooDAO project.

| contract | description |
| --- | --- |
| NftBattleArena| main battle system logics|
| NftStakingPosition| staking position nft minter and user functions|
| NftVotingPosition| voter position nft minter and user functions|
| BaseZooFunctions | external battles logics|
| ZooGovernance | connects battles with Functions|
| ListingList | ve-Model zoo contract. List of eligible projects for battles |
| xZoo | Contract for staking Zoo tokens for % of yield generated in battles. |
| Jackpot | Сontract for apply for a lottery for % of yield generated in battles. |


##### NftBattleArena is time-based cyclic contracts with five stages in each epoch.
* 1st stage: Staking and unstaking of nfts, claiming rewards from previous epochs.
* 2nd stage: Voting for nft with dai.
* 3rd stage: Pairing of nft for battle.
* 4th stage: Boosting\voting for nft with Zoo.
* 5th stage: Random request and Choosing winners in pair.

#### ListingList contract associated with ve-model and list of eligible projects for battles.
* This contract contains logics about adding and removing from eligible projects, also sets royalte recipient address,
* And contains voting for ve-model weight functions.

##### NftStakingPosition contract associated with staker user functions.
* Also holds zoo tokens for incentive rewards for staker.

##### NftVotingPosition contract associated with voter user functions.
* Also holds zoo tokens for incentive rewards for voter.

##### BaseZooFunctions additional contract with some functions for battles. 
* This contract holds link tokens for chainlinkVRF and implement random for battles with\or without chainlinkVRF.

##### ZooGovernance connects battles with functions contract.
* Allows to connect battles with new functions contract to change some play rules if needed.

##### xZoo Contract for staking Zoo tokens for % of yield generated in battles.

##### JackPot contract for apply for a lottery for % of yield generated in battles.
* Voting and staking positions in battles can be staked to apply for a lottery.


##### Dai from votes are staked for % in Yearn, and rewards for winners are generated from this income.


#### Mock folder.
| contract | description |
| --- | --- |
| DaiTokenMock| dai token fork with changed strings name and symbol |
| YearnMock | contract imitating yearn dai vault |
| ZooNftMock | simple nft contract used in tests |
| ZooTokenMock | simple erc20 token from brownie |
| ZooTokenMockMintable | erc20 OZ preset |
| TokenMock |
| ControllerMock |

#### testnet folder.
| contract | description |
| --- | --- |
| ZooNft| simple single mint erc721 contract. Used to deploy multiple times and random mint in faucet from different contracts.|
| ZooNftFaucet | outdated nft faucet contract, currently unused |
| ZooTokenFaucet | Actual faucet for testnet, contains function to mint random nft and give dai\zoo for testnet |


