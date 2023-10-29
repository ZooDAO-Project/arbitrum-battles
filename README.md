![](https://i.ibb.co/ZGh8c9T/1500x500.jpg)

![License](https://img.shields.io/badge/License-MIT-blue?logo=zoodao) ![License](https://img.shields.io/badge/Solidity-0.8.17-green?logo=zoodao)

# [ZooDAO - NFT battles arena](https://zoodao.com/)
 This repository contains system of contracts associated with NFT battles of the ZooDAO project. 
 ## Table of Contents

* [About](#about)
* [NFT Battles](#nft-battles)
* [Technology](#technology)
* [Testing](#testing)
* [Deploy](#deploy)
* [Compilet](#compilet)
* [Documentation](#documentation)
* [License](#license)
## About
We set out to answer the question what if we could generate additional returns from the NFTs we already own?
ZooDAO responds directly to this question, by creating an ecosystem in which NFTs may be used to work for users, generating returns on existing investments passively.
### Greater purposes for NFTs

* Cross-community interaction in a gamified environment
* A user-friendly on-ramp to DeFi for an ever growing community of 205'000 NFT holders
* The capability to leverage digital assets to earn additional income without the possibility of liquidation or loss


## NFT Battles
##### NftBattleArena is time-based cyclic contracts with five stages in each epoch.


* 1st stage: Staking and unstaking of nfts, claiming rewards from previous epochs.
* 2nd stage: Voting for nft with stablecoins
* 3rd stage: Pairing of nft for battle.
* 4th stage: Boosting\voting for nft with LPs, which contain Zoo
* 5th stage: Random request and Choosing winners in pair.

## Technology
ZooDAO uses several technologies to provide its services:

- **Aragon**: ZooDAO integrates Aragon to provide true autonomy and fairness to the DAO.
- **DeFi protocols**: ZooDAO builds on DeFi protocols to deliver users organic yield, which underpins their rewards.


## Deploy
Deploying with Brownie involves a few steps:

1. **Install Brownie**: You can install Brownie using pip, which is Python's package manager. You can do this by typing the following in your terminal:
```bash
pip install eth-brownie
```
Here are some steps to deploy ZooDAO based on the information available:

2. **Import necessary modules**: Import the required modules from brownie.
```python
import brownie
from brownie import*
```

3. **Define your test functions**: Define your test functions with the necessary parameters. These functions will test various aspects of your contract.
```python
def test_one_collection_incentive_reward_of_staker(accounts, finished_epoch):
    ...
```

4. **Update Information**: Update information about staked number or voting number depending on the function.
```python
arena.updateInfoAboutStakedNumber(nft)
```

5. **Claim Rewards**: Claim incentive rewards using the `claimIncentiveStakerReward` or `claimIncentiveVotingReward` function.
```python
tx = staking.claimIncentiveStakerReward(1, accounts[-1], {"from": accounts[0]})
```

6. **Assert Statements**: Use assert statements to check if the return value is greater than 0 and if the balance of the account is greater than 0.
```python
assert tx.return_value > 0
assert zooToken.balanceOf(accounts[-1]) > 0
```

7. **Update Epoch**: Update the epoch while the current epoch is less than the end epoch of incentive rewards.
```python
while arena.currentEpoch() < arena.endEpochOfIncentiveRewards():
    chain.sleep(arena.epochDuration() + 1)
    chain.mine(1)
    arena.updateEpoch({"from": accounts[0]})
```

6. **Deploy Your Contracts**: You can deploy your contracts in a controlled environment using the `brownie deploy` command. If you want to deploy to a testnet or a real net, you can use the `--network` flag followed by the name of the network:
```bash
brownie deploy --network <name of the network>
```
You can also use this flag when testing your contracts:
```bash
brownie test --network <name of the network>
```
7. **Running Scripts**: The `brownie run <script> [function]` command is used to execute a script from the command line in the Brownie Python development environment. Here's a breakdown of the command:
```bash
brownie run <script> [function]
```
## Testing
To run a test script in Brownie, you can use the `brownie test` command followed by the path to your test script. For example:

```bash
brownie test tests/test_simple_incentive_rewards.py
```

If you want to run a specific test function within a test script, you can do so by appending `::` followed by the function name to the script path. For example:

```bash
brownie test tests/test_simple_incentive_rewards.py::test_no_rewards_after_finish_epoch
```

This will only execute the specified test function within the given test script.

You can also use the `--coverage` flag to see the coverage of your smart contract:

```bash
brownie test tests/test_simple_incentive_rewards.py --coverage
```

This command will run the tests and also provide a coverage report.


## Compilet
To compile a ZooDAO project, you can follow these steps:

1. **Install Brownie**: If you haven't installed Brownie yet, you can do so by running the following command in your terminal:
```bash
pip install eth-brownie
```

2. **Clone the ZooDAO repository**: Clone the ZooDAO repository from GitHub to your local machine. You can do this by running the following command in your terminal:
```bash
git clone <ZooDAO GitHub repository URL>
```
Please replace `<ZooDAO GitHub repository URL>` with the actual URL of the ZooDAO repository.

3. **Navigate to your project directory**: Open a terminal and navigate to the root directory of your ZooDAO project.

4. **Install dependencies**: Install any dependencies that are required for the project. This is typically done by running `npm install` in your project directory.

5. **Compile the project**: The `brownie compile` command is used to compile your smart contracts. Each time the compiler runs, Brownie compares hashes of each contract source against hashes of the existing compiled versions. If a contract has not changed it is not recompiled.
```bash
brownie compile
```
If you wish to force a recompile of the entire project, you can use `brownie compile --all`.
```bash
brownie compile --all
```
6. **Review the results**: If the compilation is successful, you should see a message indicating that the compilation was successful. If there are any errors, they will be displayed in the terminal.


## Documentation
| contract | description |
| --- | --- |
| NftBattleArena| Main battle system logics. Within the ZooDAO ecosystem, NFT Stakers can pitch their own eligible NFT assets against competitors, battling for supremacy and earning rewards in the form of yield and ZOO tokens. NFT Stakers are rewarded for their participation with a percentage of their Voters DeFi yields plus $ZOO incentives in a fully transparent fair play system |
| NftStakingPosition| Staking position nft minter and user functions. Staking is possible at any time during the 3-day window. ZooDAO incentivises NFT stakers to participate with $ZOO token rewards, that are claimable at the end of the Season These Incentive Rewards are distributed according to      veZOO model.|
| NftVotingPosition| Voter position nft minter and user functions.To ensure fairness and prevent lastminute sniping, the earlier a user votes, the more valuable their votes. are deposited by voters to Yearn in one ZAP . ZooDAO incentivises NFT voters to participate with ZOO token rewards, that are claimable at the end of the Season. Incentive Rewards are distributed according to       veZOO model. To ensure fairness and prevent lastminute sniping, the earlier a user votes, the more valuable their votes.  is deposited by voters to Moonwell. ZooDAO incentivises NFT voters to participate with ZOO token rewards, that are claimable at the end of the Season. Incentive Rewards are distributed according to       veZOO model.|
| BaseZooFunctions | External battles logics. Stablecoins staked in STAGE 2 determine the number of votes, and the odds of the competing NFTs of winning the battle Voters can increase their chances of winning by staking ZOO, capped at a 1:1 ratio with their stablecoin votes on any given NFT in STAGE 2.|
| ZooGovernance | Connects battles with Functions. |
| ListingList | ve-Model zoo contract. List of eligible projects for battles |
| veZOO| The mechanism of time locking tokens for a set period. The longer you elect to lock up your tokens, the more weight your tokens may get.|
|WinnersJackpot|Сontract for apply for a lottery for % of yield generated in battles.|
| Yield farming |Liquidity mining, is a way to generate passive income while holdings crypto assets. To participate in yield farming, owners of a cryptocurrency or digital asset lend their crypto assets in order to generate returns and rewards. We recommend users participate in yield farming only after understanding the associated benefits and risks.|

## License

This project is licensed under the [MIT license](LICENSE).



