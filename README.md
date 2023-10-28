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
* 2nd stage: Voting for nft with dai.
* 3rd stage: Pairing of nft for battle.
* 4th stage: Boosting\voting for nft with Zoo.
* 5th stage: Random request and Choosing winners in pair.

## Technology
ZooDAO uses several technologies to provide its services:

- **Aragon**: ZooDAO integrates Aragon to provide true autonomy and fairness to the DAO.
- **Chainlink's VRF**: This technology guarantees fair play by providing true randomness to Battle outcomes.
- **DeFi protocols**: ZooDAO builds on DeFi protocols to deliver users organic yield, which underpins their rewards.


## Deploy
Deploying with Brownie involves a few steps:

1. **Install Brownie**: You can install Brownie using pip, which is Python's package manager. You can do this by typing the following in your terminal:
```bash
pip install eth-brownie
```
If the installation fails, you can try using sudo:
```bash
sudo pip install eth-brownie
```

2. **Create a New Directory**: Create a new directory and switch to this directory using the following commands: 
```bash
cd project
```
3. **Initialize a New Brownie Project**: Run the command `brownie init` to start a new Brownie project. This will create boilerplate content that will help you carry on the subsequent steps with Brownie.

4. **Create a Deployment Script**: The simplest way to deploy is via a deployment script. Here is an example deployment script for a basic ERC20, taken from the documentation:

```python
from brownie import *

def main():
    accounts.deploy(Token, "Test Token", "TEST", 18, "1000 ether")
```
Save your deployment script within the `scripts/` folder of your project.

5. **Account Creation and Management**: All interactions on the Ethereum blockchain require interaction with accounts. You can generate a new set of 10 accounts with keys placed in a local json keystore located at `~/.brownie/accounts/dev.json` by default using the command: `brownie accounts generate dev`.

Deploying a smart contract with Brownie involves several steps:

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

- `brownie run`: This is the command to tell Brownie that you want to run a script.
- `<script>`: This is where you specify the path to the script that you want to run.
- `[function]`: This is an optional argument where you can specify a particular function within the script that you want to execute. If no function is specified, Brownie attempts to run the `main` function.

From the console, you can use the `run` method to execute a script. For example, `run('token')` would execute the `main()` function within `scripts/token.py`.

Please note that `brownie run` is designed to be run without any extra arguments besides the ones listed in `brownie run -h`. 
## Testing
To run a test script in Brownie, you can use the `brownie test` command followed by the path to your test script. For example:

```bash
brownie test tests/Example_test.py
```

If you want to run a specific test function within a test script, you can do so by appending `::` followed by the function name to the script path. For example:

```bash
brownie test tests/test_contract_abc.py::specific_test_function_name
```

This will only execute the specified test function within the given test script.

You can also use the `--coverage` flag to see the coverage of your smart contract:

```bash
brownie test tests/Example_test.py --coverage
```

This command will run the tests and also provide a coverage report.

Remember to replace `Example_test.py`, `test_contract_abc.py`, and `specific_test_function_name` with your actual test script name and function name.
## Compilet
The `brownie compile` command is used to compile your smart contracts. Each time the compiler runs, Brownie compares hashes of each contract source against hashes of the existing compiled versions. If a contract has not changed it is not recompiled⁶.
```bash
brownie compile
```
If you wish to force a recompile of the entire project, you can use `brownie compile --all`.
```bash
brownie compile --all
```
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
|Jackpot|Сontract for apply for a lottery for % of yield generated in battles.|
| Yield farming |Liquidity mining, is a way to generate passive income while holdings crypto assets. To participate in yield farming, owners of a cryptocurrency or digital asset lend their crypto assets in order to generate returns and rewards. We recommend users participate in yield farming only after understanding the associated benefits and risks.|

## License

This project is licensed under the [MIT license](LICENSE).



