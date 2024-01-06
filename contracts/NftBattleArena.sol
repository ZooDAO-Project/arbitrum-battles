pragma solidity 0.8.17;

// SPDX-License-Identifier: MIT

import "./interfaces/IVault.sol";
import "./interfaces/IZooFunctions.sol";
import "./ZooGovernance.sol";
import "./ListingList.sol";
import "@OpenZeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import "@OpenZeppelin/contracts/utils/math/Math.sol";
import "@OpenZeppelin/contracts/token/ERC20/extensions/ERC4626.sol";

/// @notice Struct with stages of arena.
enum Stage
{
	FirstStage,
	SecondStage,
	ThirdStage,
	FourthStage,
	FifthStage
}

/// @title NftBattleArena contract.
/// @notice Contract for staking ZOO-Nft for participate in battle votes.
contract NftBattleArena
{
	using Math for uint256;
	using Math for int256;

	ERC4626 public immutable lpZoo;                                            // lp zoo interface.
	IERC20Metadata public immutable dai;                                       // stablecoin token interface
	IERC20Metadata public zoo;                                       // Zoo token interface
	VaultAPI public immutable vault;                                           // Vault interface.
	ZooGovernance public zooGovernance;                              // zooGovernance contract.
	IZooFunctions public zooFunctions;                               // zooFunctions contract.
	ListingList public immutable veZoo;

	/// @notice Struct with info about rewards, records for epoch.
	struct BattleRewardForEpoch
	{
		uint256 yTokensSaldo;                                         // Saldo from deposit in yearn in yTokens.
		uint256 votes;                                               // Total amount of votes for nft in this battle in this epoch.
		uint256 yTokens;                                             // Amount of yTokens.
		uint256 tokensAtBattleStart;                                 // Amount of yTokens at battle start.
		uint256 pricePerShareAtBattleStart;                          // pps at battle start.
		uint256 pricePerShareCoef;                                   // pps1*pps2/pps2-pps1
		uint256 zooRewards;                                          // Reward from arena 50-50 battle
		uint8 league;                                                // League of NFT
		bool isWinnerChose;											 // Choose winner was called for that position.
	}

	/// @notice Struct with info about staker positions.
	struct StakerPosition
	{
		uint256 startEpoch;                                          // Epoch when started to stake.
		uint256 endEpoch;                                            // Epoch when unstaked.
		uint256 lastRewardedEpoch;                                   // Epoch when last reward were claimed.
		uint256 lastUpdateEpoch;                                     // Epoch when last updateInfo called.
		address collection;                                          // Address of nft collection contract.
		uint256 lastEpochOfIncentiveReward;
	}

	/// @notice struct with info about voter positions.
	struct VotingPosition
	{
		uint256 stakingPositionId;                                   // Id of staker position voted for.
		uint256 daiInvested;                                         // Amount of dai invested in voting position.
		uint256 yTokensNumber;                                       // Amount of yTokens got for dai.
		uint256 zooInvested;                                         // Amount of Zoo used to boost votes.
		uint256 daiVotes;                                            // Amount of votes got from voting with dai.
		uint256 votes;                                               // Amount of total votes from dai, zoo and multiplier.
		uint256 startEpoch;                                          // Epoch when created voting position.
		uint256 endEpoch;                                            // Epoch when liquidated voting position.
		uint256 lastRewardedEpoch;                                   // Epoch when last battle reward was claimed.
		uint256 lastEpochYTokensWereDeductedForRewards;              // Last epoch when yTokens used for rewards in battles were deducted from all voting position's yTokens
		uint256 yTokensRewardDebt;                                   // Amount of yTokens which voter can claim for previous epochs before add/withdraw votes.
		uint256 lastEpochOfIncentiveReward;
	}

	/// @notice Struct for records about pairs of Nfts for battle.
	struct NftPair
	{
		uint256 token1;                                              // Id of staker position of 1st candidate.
		uint256 token2;                                              // Id of staker position of 2nd candidate.
		bool playedInEpoch;                                          // Returns true if winner chosen.
		bool win;                                                    // Boolean, where true is when 1st candidate wins, and false for 2nd.
	}

	/// @notice Event about staked nft.                         FirstStage
	event CreatedStakerPosition(uint256 indexed currentEpoch, address indexed staker, uint256 indexed stakingPositionId);

	/// @notice Event about withdrawed nft from arena.          FirstStage
	event RemovedStakerPosition(uint256 indexed currentEpoch, address indexed staker, uint256 indexed stakingPositionId);


	/// @notice Event about created voting position.            SecondStage
	event CreatedVotingPosition(uint256 indexed currentEpoch, address indexed voter, uint256 indexed stakingPositionId, uint256 daiAmount, uint256 votes, uint256 votingPositionId);

	/// @notice Event about liquidated voting position.         FirstStage
	event LiquidatedVotingPosition(uint256 indexed currentEpoch, address indexed voter, uint256 indexed stakingPositionId, address beneficiary, uint256 votingPositionId, uint256 zooReturned, uint256 daiReceived);

	/// @notice Event about recomputing votes from dai.         SecondStage
	event RecomputedDaiVotes(uint256 indexed currentEpoch, address indexed voter, uint256 indexed stakingPositionId, uint256 votingPositionId, uint256 newVotes, uint256 oldVotes);

	/// @notice Event about recomputing votes from zoo.         FourthStage
	event RecomputedZooVotes(uint256 indexed currentEpoch, address indexed voter, uint256 indexed stakingPositionId, uint256 votingPositionId, uint256 newVotes, uint256 oldVotes);


	/// @notice Event about adding dai to voter position.       SecondStage
	event AddedDaiToVoting(uint256 indexed currentEpoch, address indexed voter, uint256 indexed stakingPositionId, uint256 votingPositionId, uint256 amount, uint256 votes);

	/// @notice Event about adding zoo to voter position.       FourthStage
	event AddedZooToVoting(uint256 indexed currentEpoch, address indexed voter, uint256 indexed stakingPositionId, uint256 votingPositionId, uint256 amount, uint256 votes);


	/// @notice Event about withdraw dai from voter position.   FirstStage
	event WithdrawedDaiFromVoting(uint256 indexed currentEpoch, address indexed voter, uint256 indexed stakingPositionId, address beneficiary, uint256 votingPositionId, uint256 daiNumber);

	/// @notice Event about withdraw zoo from voter position.   FirstStage
	event WithdrawedZooFromVoting(uint256 indexed currentEpoch, address indexed voter, uint256 indexed stakingPositionId, uint256 votingPositionId, uint256 zooNumber, address beneficiary);


	/// @notice Event about claimed reward from voting.         FirstStage
	event ClaimedRewardFromVoting(uint256 indexed currentEpoch, address indexed voter, uint256 indexed stakingPositionId, address beneficiary, uint256 daiReward, uint256 votingPositionId);

	/// @notice Event about claimed reward from staking.        FirstStage
	event ClaimedRewardFromStaking(uint256 indexed currentEpoch, address indexed staker, uint256 indexed stakingPositionId, address beneficiary, uint256 yTokenReward, uint256 daiReward);


	/// @notice Event about paired nfts.                        ThirdStage
	event PairedNft(uint256 indexed currentEpoch, uint256 indexed fighter1, uint256 indexed fighter2, uint256 pairIndex);

	/// @notice Event about winners in battles.                 FifthStage
	event ChosenWinner(uint256 indexed currentEpoch, uint256 indexed fighter1, uint256 indexed fighter2, bool winner, uint256 pairIndex, uint256 playedPairsAmount);

	/// @notice Event about changing epochs.
	event EpochUpdated(uint256 date, uint256 newEpoch);

	uint256 public epochStartDate;                                                 // Start date of battle epoch.
	uint256 public currentEpoch = 1;                                               // Counter for battle epochs.

	uint256 public firstStageDuration;                                             // Duration of first stage(stake).
	uint256 public secondStageDuration;                                            // Duration of second stage(DAI)'.
	uint256 public thirdStageDuration;                                             // Duration of third stage(Pair).
	uint256 public fourthStageDuration;                                            // Duration fourth stage(ZOO).
	uint256 public fifthStageDuration;                                             // Duration of fifth stage(Winner).
	uint256 public epochDuration;                                                  // Total duration of battle epoch.

	uint256[] public activeStakerPositions;                                        // Array of ZooBattle nfts, which are StakerPositions.
	uint256 public numberOfNftsWithNonZeroVotes;                                   // Staker positions with votes for, eligible to pair and battle.
	uint256 public numberOfNftsWithNonZeroVotesPending; // positions eligible for paring from next epoch.
	uint256 public nftsInGame;                                                     // Amount of Paired nfts in current epoch.

	uint256 public numberOfStakingPositions = 1;
	uint256 public numberOfVotingPositions = 1;

	address public immutable treasury;                                                       // Address of ZooDao insurance pool.
	// address public team;                                                           // Address of ZooDao team reward pool.
	address public immutable nftStakingPosition; // address of staking positions contract.
	address public immutable nftVotingPosition;  // address of voting positions contract.

	uint256 public constant baseStakerReward = 140_000 * 10 ** 18 * 15 / 100; // amount of incentives for staker.
	uint256 public constant baseVoterReward = 140_000 * 10 ** 18 * 85 / 100; // amount of incentives for voter.

	uint256 public zooVoteRateNominator; // amount of votes for 1 LP with zoo.
	uint256 public zooVoteRateDenominator;

	uint256 public constant endEpochOfIncentiveRewards = 18;

	mapping (address => mapping (uint256 => uint256)) public poolWeight;

	// epoch number => index => NftPair struct.
	mapping (uint256 => NftPair[]) public pairsInEpoch;                            // Records info of pair in struct per battle epoch.

	// number of played pairs in epoch.
	uint256 public numberOfPlayedPairsInEpoch = 0;                // Records amount of pairs with chosen winner in current epoch.

	// position id => StakerPosition struct.
	mapping (uint256 => StakerPosition) public stakingPositionsValues;             // Records info about staker position.

	// position id => VotingPosition struct.
	mapping (uint256 => VotingPosition) public votingPositionsValues;              // Records info about voter position.

	// epoch index => collection => number of staked nfts.
	mapping (uint256 => mapping (address => uint256)) public numberOfStakedNftsInCollection;

	// collection => last epoch when info about numberOfStakedNftsInCollection was updated.
	mapping (address => uint256) public lastUpdatesOfStakedNumbers;

	// staker position id => epoch = > rewards struct.
	mapping (uint256 => mapping (uint256 => BattleRewardForEpoch)) public rewardsForEpoch;

	// epoch number => timestamp of epoch start
	mapping (uint256 => uint256) public epochsStarts;

	// epoch collection => epoch number => votes from collection played in this epoch.
	mapping (address => mapping (uint256 => uint256)) public playedVotes;

	// id voting position => pendingVotes
	mapping (uint256 => uint256) public pendingVotes;      // Votes amount for next epoch.

	// id voting position => pendingVotesEpoch
	mapping (uint256 => uint256) public pendingVotesEpoch; // Epoch when voted for next epoch.

	// voting position id => pendingYTokens
	mapping (uint256 => uint256) public pendingYTokens;

	// id voting position => zooTokenRewardDebt
	mapping (uint256 => uint256) public zooTokensRewardDebt; // This needs for correct distributing of zoo reward for 50-50 arena battle case.

	// voting position id => zoo debt
	mapping (uint256 => uint256) public voterIncentiveDebt;

	modifier only(address who)
	{
		require(msg.sender == who);
		_;
	}

	/// @notice Contract constructor.
	/// @param _lpZoo - address of LP token with zoo.
	/// @param _dai - address of stable token contract.
	/// @param _vault - address of yearn.
	/// @param _zooGovernance - address of ZooDao Governance contract.
	/// @param _treasuryPool - address of ZooDao treasury pool.
	///  _teamAddress - address of ZooDao team reward pool.
	constructor (
		ERC4626 _lpZoo,
		IERC20Metadata _dai,
		address _vault,
		address _zooGovernance,
		address _treasuryPool,
		// address _teamAddress,
		address _nftStakingPosition,
		address _nftVotingPosition,
		address _veZoo)
	{
		lpZoo = _lpZoo;
		dai = _dai;
		vault = VaultAPI(_vault);
		zooGovernance = ZooGovernance(_zooGovernance);
		zooFunctions = IZooFunctions(zooGovernance.zooFunctions());
		veZoo = ListingList(_veZoo);

		treasury = _treasuryPool;
		// team = _teamAddress;
		nftStakingPosition = _nftStakingPosition;
		nftVotingPosition = _nftVotingPosition;

		epochStartDate = block.timestamp; // Start date of 1st battle.
		epochsStarts[currentEpoch] = block.timestamp;
		(firstStageDuration, secondStageDuration, thirdStageDuration, fourthStageDuration, fifthStageDuration, epochDuration) = zooFunctions.getStageDurations();
	}

	/// @param _zooVoteRateNominator - amount of votes for 1 LP with zoo.
	/// @param _zooVoteRateDenomibator - divider for amount of votes for 1 LP with zoo.
	/// @param _zoo actual zoo token(not LP).
	function init(uint256 _zooVoteRateNominator, uint256 _zooVoteRateDenomibator, IERC20Metadata _zoo) external
	{
		require(zooVoteRateNominator == 0);

		zooVoteRateNominator = _zooVoteRateNominator;
		zooVoteRateDenominator = _zooVoteRateDenomibator;
		zoo = _zoo;
	}

	/// @notice Function to get amount of nft in array StakerPositions/staked in battles.
	/// @return amount - amount of ZooBattles nft.
	function getStakerPositionsLength() public view returns (uint256 amount)
	{
		return activeStakerPositions.length;
	}

	/// @notice Function to get amount of nft pairs in epoch.
	/// @param epoch - number of epoch.
	/// @return length - amount of nft pairs.
	function getNftPairLength(uint256 epoch) public view returns(uint256 length)
	{
		return pairsInEpoch[epoch].length;
	}

	/// @notice Function to calculate amount of tokens from shares.
	/// @param sharesAmount - amount of shares.
	/// @return tokens - calculated amount tokens from shares.
	function sharesToTokens(uint256 sharesAmount) public returns (uint256 tokens)
	{
		return sharesAmount * vault.exchangeRateCurrent() / (10 ** 18);
	}

	/// @notice Function for calculating tokens to shares.
	/// @param tokens - amount of tokens to calculate.
	/// @return shares - calculated amount of shares.
	function tokensToShares(uint256 tokens) public returns (uint256 shares)
	{
		return tokens * (10 ** 18) / vault.exchangeRateCurrent();
	}

	/// @notice Function for staking NFT in this pool.
	/// @param staker address of staker
	/// @param token NFT collection address
	function createStakerPosition(address staker, address token) public only(nftStakingPosition) returns (uint256)
	{
		//require(getCurrentStage() == Stage.FirstStage, "Wrong stage!"); // Require turned off cause its moved to staker position contract due to lack of space for bytecode. // Requires to be at first stage in battle epoch.

		StakerPosition storage position = stakingPositionsValues[numberOfStakingPositions];
		position.startEpoch = currentEpoch;                                                     // Records startEpoch.
		position.lastRewardedEpoch = currentEpoch;                                              // Records lastRewardedEpoch
		position.collection = token;                                                            // Address of nft collection.
		position.lastEpochOfIncentiveReward = currentEpoch;
		position.lastUpdateEpoch = currentEpoch;

		numberOfStakedNftsInCollection[currentEpoch][token]++;                                  // Increments amount of nft collection.

		activeStakerPositions.push(numberOfStakingPositions);                                   // Records this position to stakers positions array.

		emit CreatedStakerPosition(currentEpoch, staker, numberOfStakingPositions);             // Emits StakedNft event.

		return numberOfStakingPositions++;                                                      // Increments amount and id of future positions.
	}

	/// @notice Function for withdrawing staked nft.
	/// @param stakingPositionId - id of staker position.
	function removeStakerPosition(uint256 stakingPositionId, address staker) external only(nftStakingPosition)
	{
		//require(getCurrentStage() == Stage.FirstStage, "Wrong stage!"); // Require turned off cause its moved to staker position contract due to lack of space for bytecode. // Requires to be at first stage in battle epoch.
		StakerPosition storage position = stakingPositionsValues[stakingPositionId];
		require(position.endEpoch == 0, "E1");                                        // Requires token to be staked.

		position.endEpoch = currentEpoch;                                                       // Records epoch when unstaked.
		updateInfo(stakingPositionId);                                                          // Updates staking position params from previous epochs.

		if (rewardsForEpoch[stakingPositionId][currentEpoch].votes > 0 || rewardsForEpoch[stakingPositionId][currentEpoch + 1].votes > 0)                         // If votes for position in current or next epoch more than zero.
		{
			for(uint256 i = 0; i < numberOfNftsWithNonZeroVotes; ++i)                           // Iterates for non-zero positions.
			{
				if (activeStakerPositions[i] == stakingPositionId)                              // Finds this position in array of active positions.
				{
					// Replace this position with another position from end of array. Then shift zero positions for one point.
					activeStakerPositions[i] = activeStakerPositions[numberOfNftsWithNonZeroVotes - 1];
					activeStakerPositions[--numberOfNftsWithNonZeroVotes] = activeStakerPositions[activeStakerPositions.length - 1];
					break;
				}
			}
		}
		else // If votes for position in current epoch are zero, does the same, but without decrement numberOfNftsWithNonZeroVotes.
		{
			for(uint256 i = numberOfNftsWithNonZeroVotes; i < activeStakerPositions.length; ++i)
			{
				if (activeStakerPositions[i] == stakingPositionId)                                     // Finds this position in array.
				{
					activeStakerPositions[i] = activeStakerPositions[activeStakerPositions.length - 1];// Swaps to end of array.
					break;
				}
			}
		}

		updateInfoAboutStakedNumber(position.collection);
		numberOfStakedNftsInCollection[currentEpoch][position.collection]--;
		activeStakerPositions.pop();                                                            // Removes staker position from array.

		emit RemovedStakerPosition(currentEpoch, staker, stakingPositionId);                    // Emits UnstakedNft event.
	}

	/// @notice Function for vote for nft in battle.
	/// @param stakingPositionId - id of staker position.
	/// @param amount - amount of dai to vote.
	/// @return votes - computed amount of votes.
	function createVotingPosition(uint256 stakingPositionId, address voter, uint256 amount) external only(nftVotingPosition) returns (uint256 votes, uint256 votingPositionId)
	{
		//require(getCurrentStage() == Stage.SecondStage, "Wrong stage!"); // Require turned off cause its moved to voting position contract due to lack of space for bytecode. // Requires to be at second stage of battle epoch.

		updateInfo(stakingPositionId);                                                          // Updates staking position params from previous epochs.

		if (dai.allowance(address(this), address(vault)) < amount)
			dai.approve(address(vault), type(uint256).max);                                         // Approves Dai for yearn.
		uint256 yTokensNumber = vault.balanceOf(address(this));
		require(vault.mint(amount) == 0);                                                       // Deposits dai to yearn vault and get yTokens.

		(votes, votingPositionId) = _createVotingPosition(stakingPositionId, voter, vault.balanceOf(address(this)) - yTokensNumber, amount);// Calls internal create voting position.
	}

	/// @dev internal function to modify voting position params without vault deposit, making swap votes possible.
	/// @param stakingPositionId ID of staking to create voting for
	/// @param voter address of voter
	/// @param yTokens amount of yTokens got from Yearn from deposit
	/// @param amount daiVotes amount
	function _createVotingPosition(uint256 stakingPositionId, address voter, uint256 yTokens, uint256 amount) public only(nftVotingPosition) returns (uint256 votes, uint256 votingPositionId)
	{
		StakerPosition storage stakingPosition = stakingPositionsValues[stakingPositionId];
		require(stakingPosition.startEpoch != 0 && stakingPosition.endEpoch == 0, "E1"); // Requires for staking position to be staked.

		VotingPosition storage position = votingPositionsValues[numberOfVotingPositions];
		votes = zooFunctions.computeVotesByDai(amount);                                         // Calculates amount of votes.

		uint256 epoch = currentEpoch;
		if (getCurrentStage() > Stage.ThirdStage)
		{
			epoch += 1;
			pendingVotes[numberOfVotingPositions] = votes;
			pendingVotesEpoch[numberOfVotingPositions] = epoch;
		}
		else
		{
			position.daiVotes = votes;                     			// Records computed amount of votes to daiVotes.
			position.votes = votes;                        			// Records computed amount of votes to total votes.
		}

		position.stakingPositionId = stakingPositionId;    			// Records staker position Id voted for.
		position.yTokensNumber = yTokens;                  			// Records amount of yTokens got from yearn vault.
		position.daiInvested = amount;                     			// Records amount of dai invested.
		position.startEpoch = epoch;                       			// Records epoch when position created.
		position.lastRewardedEpoch = epoch;                			// Sets starting point for reward to current epoch.
		position.lastEpochYTokensWereDeductedForRewards = epoch;	// Sets starting point for deducted reward to current epoch.
		position.lastEpochOfIncentiveReward = epoch;       			// Sets starting point for incentive rewards calculation.

		BattleRewardForEpoch storage battleReward = rewardsForEpoch[stakingPositionId][currentEpoch];
		BattleRewardForEpoch storage battleReward1 = rewardsForEpoch[stakingPositionId][epoch];

		if (battleReward.votes == 0)                                                            // If staker position had zero votes before,
		{
			if (epoch == currentEpoch) // if vote for this epoch
			{
				_swapActiveStakerPositions(stakingPositionId);
				numberOfNftsWithNonZeroVotes++;
			}
			else if (battleReward1.votes == 0) // if vote for next epoch and position have zero votes in both epochs.
			{
				_swapActiveStakerPositions(stakingPositionId);
				numberOfNftsWithNonZeroVotesPending++;
			}
		}
		battleReward1.votes += votes;                                                            // Adds votes for staker position for this epoch.
		battleReward1.yTokens += yTokens;                                                        // Adds yTokens for this staker position for this epoch.

		battleReward1.league = zooFunctions.getNftLeague(battleReward1.votes);

		votingPositionId = numberOfVotingPositions;
		numberOfVotingPositions++;

		emit CreatedVotingPosition(epoch, voter, stakingPositionId, amount, votes, votingPositionId);
	}


	function _swapActiveStakerPositions(uint256 stakingPositionId) internal
	{
		for(uint256 i = 0; i < activeStakerPositions.length; ++i)                           // Iterate for active staker positions.
		{
			if (activeStakerPositions[i] == stakingPositionId)                              // Finds this position.
			{
				uint256 endIndex = numberOfNftsWithNonZeroVotes + numberOfNftsWithNonZeroVotesPending;
				if (i > endIndex)                                       // if equal, then its already in needed place in array.
				{
					(activeStakerPositions[i], activeStakerPositions[endIndex]) = (activeStakerPositions[endIndex], activeStakerPositions[i]);                                              // Swaps this position in array, moving it to last point of non-zero positions.
					break;
				}
			}
		}
	}

	/// @notice Function to recompute votes from dai.
	/// @notice Reasonable to call at start of new epoch for better multiplier rate, if voted with low rate before.
	/// @param votingPositionId - id of voting position.
	function recomputeDaiVotes(uint256 votingPositionId) public
	{
		require(getCurrentStage() <= Stage.SecondStage, "Wrong stage!");              // Requires to be at second stage of battle epoch.

		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		_updateVotingPosition(votingPositionId);
		// _updateVotingRewardDebt(votingPositionId);

		uint256 stakingPositionId = votingPosition.stakingPositionId;
		updateInfo(stakingPositionId);                                                // Updates staking position params from previous epochs.

		uint256 daiNumber = votingPosition.daiInvested;                               // Gets amount of dai from voting position.
		uint256 newVotes = zooFunctions.computeVotesByDai(daiNumber);                 // Recomputes dai to votes.
		uint256 oldVotes = votingPosition.daiVotes;                                   // Gets amount of votes from voting position.

		require(newVotes > oldVotes, "E1");                     // Requires for new votes amount to be bigger than before.

		votingPosition.daiVotes = newVotes;                                           // Records new votes amount from dai.
		votingPosition.votes += newVotes - oldVotes;                                  // Records new votes amount total.
		rewardsForEpoch[stakingPositionId][currentEpoch].votes += newVotes - oldVotes;// Increases rewards for staker position for added amount of votes in this epoch.
		emit RecomputedDaiVotes(currentEpoch, msg.sender, stakingPositionId, votingPositionId, newVotes, oldVotes);
	}

	// todo: check for correct work with change for zoo-mim
	/// @notice Function to recompute votes from zoo.
	/// @param votingPositionId - id of voting position.
	function recomputeZooVotes(uint256 votingPositionId) public
	{
		require(getCurrentStage() == Stage.FourthStage, "Wrong stage!");              // Requires to be at 4th stage.

		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		_updateVotingPosition(votingPositionId);
		// _updateVotingRewardDebt(votingPositionId);

		uint256 stakingPositionId = votingPosition.stakingPositionId;
		updateInfo(stakingPositionId);

		uint256 zooNumber = votingPosition.zooInvested * zooVoteRateNominator / zooVoteRateDenominator;                 // Gets amount of zoo invested from voting position.
		uint256 newZooVotes = zooFunctions.computeVotesByZoo(zooNumber);              // Recomputes zoo to votes.
		uint256 oldZooVotes = votingPosition.votes - votingPosition.daiVotes;         // Get amount of votes from zoo.

		require(newZooVotes > oldZooVotes, "E1");               // Requires for new votes amount to be bigger than before.

		votingPosition.votes += newZooVotes - oldZooVotes;                            // Add amount of recently added votes to total votes in voting position.
		rewardsForEpoch[stakingPositionId][currentEpoch].votes += newZooVotes - oldZooVotes; // Adds amount of recently added votes to reward for staker position for current epoch.

		emit RecomputedZooVotes(currentEpoch, msg.sender, stakingPositionId, votingPositionId, newZooVotes, oldZooVotes);
	}

	/// @notice Function to add dai tokens to voting position.
	/// @param votingPositionId - id of voting position.
	/// @param voter - address of voter.
	/// @param amount - amount of dai tokens to add.
	/// @param _yTokens - amount of yTokens from previous position when called with swap.
	function addDaiToVoting(uint256 votingPositionId, address voter, uint256 amount, uint256 _yTokens) public only(nftVotingPosition) returns (uint256 votes)
	{
		require(getCurrentStage() != Stage.ThirdStage, "Wrong stage!");

		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		uint256 stakingPositionId = votingPosition.stakingPositionId;                 // Gets id of staker position.
		require(stakingPositionsValues[stakingPositionId].endEpoch == 0, "E1");       // Requires to be staked.

		_updateVotingPosition(votingPositionId);
		// _updateVotingRewardDebt(votingPositionId);

		votes = zooFunctions.computeVotesByDai(amount);                               // Gets computed amount of votes from multiplier of dai.
		// case for NOT swap.
		if (_yTokens == 0)                                                            // if no _yTokens from another position with swap.
		{
			_yTokens = vault.balanceOf(address(this));
			require(vault.mint(amount) == 0);                                         // Deposits dai to yearn and gets yTokens.
			_yTokens = vault.balanceOf(address(this)) - _yTokens;
		}

		uint256 epoch = currentEpoch;
		if (getCurrentStage() > Stage.SecondStage)
		{
			epoch += 1;
			pendingVotes[votingPositionId] += votes;
			pendingVotesEpoch[votingPositionId] = epoch;
			pendingYTokens[votingPositionId] += _yTokens;
		}
		else
		{
			votingPosition.daiVotes += votes;                                             // Adds computed daiVotes amount from to voting position.
			votingPosition.votes += votes;                                                // Adds computed votes amount to totalVotes amount for voting position.
			votingPosition.yTokensNumber += _yTokens; // Adds yTokens to voting position.
		}

		_subtractYTokensUserForRewardsFromVotingPosition(votingPositionId);
		votingPosition.daiInvested += amount;                                         // Adds amount of dai to voting position.

		updateInfo(stakingPositionId);
		BattleRewardForEpoch storage battleReward = rewardsForEpoch[stakingPositionId][epoch];

		battleReward.votes += votes;              // Adds votes to staker position for current epoch.
		battleReward.yTokens += _yTokens;         // Adds yTokens to rewards from staker position for current epoch.

		battleReward.league = zooFunctions.getNftLeague(battleReward.votes);

		emit AddedDaiToVoting(currentEpoch, voter, stakingPositionId, votingPositionId, amount, votes);
	}

	/// @notice Function to add zoo tokens to voting position.
	/// @param votingPositionId - id of voting position.
	/// @param amount - amount of zoo LP tokens to add.
	function addZooToVoting(uint256 votingPositionId, address voter, uint256 amount) external only(nftVotingPosition) returns (uint256 votes)
	{
		//require(getCurrentStage() == Stage.FourthStage, "Wrong stage!"); // Require turned off cause its moved to voting position contract due to lack of space for bytecode. // Requires to be at 3rd stage.

		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		_updateVotingPosition(votingPositionId);
		// _updateVotingRewardDebt(votingPositionId);                                    // Records current reward for voting position to reward debt.

		uint256 zooVotesFromLP = amount * zooVoteRateNominator / zooVoteRateDenominator; // Gets amount of zoo votes from LP.
		votes = zooFunctions.computeVotesByZoo(zooVotesFromLP);                               // Gets computed amount of votes from multiplier of zoo.
		require(votingPosition.zooInvested + amount <= votingPosition.daiInvested, "E1");// Requires for votes from zoo to be less than votes from dai.

		uint256 stakingPositionId = votingPosition.stakingPositionId;                 // Gets id of staker position.
		updateInfo(stakingPositionId);                                                // Updates staking position params from previous epochs.
		BattleRewardForEpoch storage battleReward = rewardsForEpoch[stakingPositionId][currentEpoch];

		poolWeight[address(0)][currentEpoch] += votes;
		poolWeight[stakingPositionsValues[stakingPositionId].collection][currentEpoch] += votes;

		battleReward.votes += votes;              // Adds votes for staker position.
		votingPositionsValues[votingPositionId].votes += votes;                       // Adds votes to voting position.
		votingPosition.zooInvested += amount;                                         // Adds amount of zoo tokens to voting position.

		battleReward.league = zooFunctions.getNftLeague(battleReward.votes);

		emit AddedZooToVoting(currentEpoch, voter, stakingPositionId, votingPositionId, amount, votes);
	}

	/// @notice Functions to withdraw dai from voting position.
	/// @param votingPositionId - id of voting position.
	/// @param daiNumber - amount of dai to withdraw.
	/// @param beneficiary - address of recipient.
	function withdrawDaiFromVoting(uint256 votingPositionId, address voter, address beneficiary, uint256 daiNumber, bool toSwap) public only(nftVotingPosition)
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		uint256 stakingPositionId = votingPosition.stakingPositionId;               // Gets id of staker position.
		updateInfo(stakingPositionId);                                              // Updates staking position params from previous epochs.

		require(getCurrentStage() == Stage.FirstStage || stakingPositionsValues[stakingPositionId].endEpoch != 0, "Wrong stage!"); // Requires correct stage or nft to be unstaked.
		require(votingPosition.endEpoch == 0, "E1");                  // Requires to be not liquidated yet.

		_updateVotingPosition(votingPositionId);
		// _updateVotingRewardDebt(votingPositionId);
		_subtractYTokensUserForRewardsFromVotingPosition(votingPositionId);

		if (daiNumber >= votingPosition.daiInvested)                                // If withdraw amount more or equal of maximum invested.
		{
			_liquidateVotingPosition(votingPositionId, voter, beneficiary, stakingPositionId, toSwap);// Calls liquidate and ends call.
			return;
		}

		uint256 shares = tokensToShares(daiNumber);                                 // If withdraw amount don't require liquidating, get amount of shares and continue.

		if (toSwap == false)                                                        // If called not through swap.
		{
			require(vault.redeem(shares) == 0);
			_stablecoinTransfer(voter, dai.balanceOf(address(this)));
		}
		BattleRewardForEpoch storage battleReward = rewardsForEpoch[stakingPositionId][currentEpoch];

		uint256 deltaVotes = votingPosition.daiVotes * daiNumber / votingPosition.daiInvested;// Gets average amount of votes withdrawed, cause vote price could be different.
		battleReward.yTokens -= shares;                                          // Decreases amount of shares for epoch.
		battleReward.votes -= deltaVotes;                                        // Decreases amount of votes for epoch for average votes.

		votingPosition.yTokensNumber -= shares;                                     // Decreases amount of shares.
		votingPosition.daiVotes -= deltaVotes;
		votingPosition.votes -= deltaVotes;                                         // Decreases amount of votes for position.
		votingPosition.daiInvested -= daiNumber;                                    // Decreases daiInvested amount of position.

		if (votingPosition.zooInvested > votingPosition.daiInvested)                // If zooInvested more than daiInvested left in position.
		{
			_rebalanceExceedZoo(votingPositionId, stakingPositionId, beneficiary);  // Withdraws excess zoo to save 1-1 dai-zoo proportion.
		}

		battleReward.league = zooFunctions.getNftLeague(battleReward.votes);

		emit WithdrawedDaiFromVoting(currentEpoch, voter, stakingPositionId, beneficiary, votingPositionId, daiNumber);
	}

	function addVotesToVeZoo(address collection, uint256 amount) external only(address(veZoo))
	{
		require(getCurrentStage() != Stage.FifthStage, "Wrong stage!");

		poolWeight[collection][currentEpoch] += amount * zooVoteRateNominator / zooVoteRateDenominator;
		poolWeight[address(0)][currentEpoch] += amount * zooVoteRateNominator / zooVoteRateDenominator;
	}

	function removeVotesFromVeZoo(address collection, uint256 amount) external only(address(veZoo))
	{
		require(getCurrentStage() == Stage.FifthStage, "Wrong stage!");

		updateInfoAboutStakedNumber(collection);
		poolWeight[collection][currentEpoch] -= amount * zooVoteRateNominator / zooVoteRateDenominator;
		poolWeight[address(0)][currentEpoch] -= amount * zooVoteRateNominator / zooVoteRateDenominator;
	}

	/// @dev Function to liquidate voting position and claim reward.
	/// @param votingPositionId - id of position.
	/// @param voter - address of position owner.
	/// @param beneficiary - address of recipient.
	/// @param stakingPositionId - id of staking position.
	/// @param toSwap - boolean for swap votes, True if called from swapVotes function.
	function _liquidateVotingPosition(uint256 votingPositionId, address voter, address beneficiary, uint256 stakingPositionId, bool toSwap) internal
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];

		uint256 yTokens = votingPosition.yTokensNumber;

		if (toSwap == false)                                         // If false, withdraws tokens from vault
		{
			require(vault.redeem(yTokens) == 0);
			_stablecoinTransfer(beneficiary, dai.balanceOf(address(this))); // True when called from swapVotes, ignores withdrawal to re-assign them for another position.
		}

		_withdrawZoo(votingPosition.zooInvested, beneficiary);                      // Even if it is swap, withdraws all zoo.

		votingPosition.endEpoch = currentEpoch;                      // Sets endEpoch to currentEpoch.

		BattleRewardForEpoch storage battleReward = rewardsForEpoch[stakingPositionId][currentEpoch];
		battleReward.votes -= votingPosition.votes;                  // Decreases votes for staking position in current epoch.

		if (battleReward.yTokens >= yTokens)                         // If withdraws less than in staking position.
		{
			battleReward.yTokens -= yTokens;                         // Decreases yTokens for this staking position.
		}
		else
		{
			battleReward.yTokens = 0;                                // Or nullify it if trying to withdraw more yTokens than left in position(because of yTokens current rate)
		}

		// IF there is votes on position AND staking position is active
		if (battleReward.votes == 0 && stakingPositionsValues[stakingPositionId].endEpoch == 0)
		{
			// Move staking position to part, where staked without votes.
			for(uint256 i = 0; i < activeStakerPositions.length; ++i)
			{
				if (activeStakerPositions[i] == stakingPositionId)
				{
					(activeStakerPositions[i], activeStakerPositions[numberOfNftsWithNonZeroVotes - 1]) = (activeStakerPositions[numberOfNftsWithNonZeroVotes - 1], activeStakerPositions[i]);      // Swaps position to end of array
					numberOfNftsWithNonZeroVotes--;                                    // Decrements amount of non-zero positions.
					break;
				}
			}
		}

		battleReward.league = zooFunctions.getNftLeague(battleReward.votes);

		emit LiquidatedVotingPosition(currentEpoch, voter, stakingPositionId, beneficiary, votingPositionId, votingPosition.zooInvested * 995 / 1000, votingPosition.daiInvested);
	}

	function _subtractYTokensUserForRewardsFromVotingPosition(uint256 votingPositionId) internal
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];

		votingPosition.yTokensNumber = _calculateVotersYTokensExcludingRewards(votingPositionId);
		votingPosition.lastEpochYTokensWereDeductedForRewards = currentEpoch;
	}

	/// @dev Calculates voting position's own yTokens - excludes yTokens that was used for rewards
	/// @dev yTokens must be substracted even if voting won in battle (they go to the voting's pending reward)
	/// @param votingPositionId ID of voting to calculate yTokens
	function _calculateVotersYTokensExcludingRewards(uint256 votingPositionId) public view returns(uint256 yTokens)
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		uint256 stakingPositionId = votingPosition.stakingPositionId;

		yTokens = votingPosition.yTokensNumber;
		uint256 endEpoch = computeLastEpoch(votingPositionId);

		// From user yTokens subtract all tokens that go to the rewards
		// This way allows to withdraw exact same amount of DAI user invested at the start
		for (uint256 i = votingPosition.lastEpochYTokensWereDeductedForRewards; i < endEpoch; ++i)
		{
			if (rewardsForEpoch[stakingPositionId][i].pricePerShareCoef != 0)
			{
				yTokens -= rewardsForEpoch[stakingPositionId][i].pricePerShareAtBattleStart * yTokens / rewardsForEpoch[stakingPositionId][i].pricePerShareCoef;
			}
		}
	}

	/// @dev function to withdraw Zoo number greater than Dai number to save 1-1 dai-zoo proportion.
	/// @param votingPositionId ID of voting to reduce Zoo number
	/// @param stakingPositionId ID of staking to reduce number of votes
	/// @param beneficiary address to withdraw Zoo
	function _rebalanceExceedZoo(uint256 votingPositionId, uint256 stakingPositionId, address beneficiary) internal
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		uint256 zooDelta = votingPosition.zooInvested - votingPosition.daiInvested;    // Get amount of zoo exceeding.

		_withdrawZoo(zooDelta, beneficiary);                                           // Withdraws exceed zoo.
		_reduceZooVotes(votingPositionId, stakingPositionId, zooDelta);
	}

	/// @dev function to calculate votes from zoo using average price and withdraw it.
	function _reduceZooVotes(uint256 votingPositionId, uint256 stakingPositionId, uint256 zooNumber) internal
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		StakerPosition storage stakerPosition = stakingPositionsValues[stakingPositionId];
		updateInfoAboutStakedNumber(stakerPosition.collection);

		uint256 zooVotes = votingPosition.votes - votingPosition.daiVotes;             // Calculates amount of votes got from zoo.
		uint256 deltaVotes = zooVotes * zooNumber * zooVoteRateDenominator / zooVoteRateNominator / votingPosition.zooInvested; // Calculates average amount of votes from this amount of zoo.

		votingPosition.votes -= deltaVotes;                                            // Decreases amount of votes.
		votingPosition.zooInvested -= zooNumber;                                       // Decreases amount of zoo invested.
		poolWeight[address(0)][currentEpoch] -= deltaVotes;
		poolWeight[stakerPosition.collection][currentEpoch] -= deltaVotes;

		updateInfo(stakingPositionId);                                                 // Updates staking position params from previous epochs.
		BattleRewardForEpoch storage battleReward = rewardsForEpoch[stakingPositionId][currentEpoch];
		battleReward.votes -= deltaVotes;          // Decreases amount of votes for staking position in current epoch.

		battleReward.league = zooFunctions.getNftLeague(battleReward.votes);
	}

	/// @notice Functions to withdraw zoo from voting position.
	/// @param votingPositionId - id of voting position.
	/// @param zooNumber - amount of zoo to withdraw.
	/// @param beneficiary - address of recipient.
	function withdrawZooFromVoting(uint256 votingPositionId, address voter, uint256 zooNumber, address beneficiary) external only(nftVotingPosition)
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		_updateVotingPosition(votingPositionId);
		// _updateVotingRewardDebt(votingPositionId);

		uint256 stakingPositionId = votingPosition.stakingPositionId;                  // Gets id of staker position from this voting position.
		StakerPosition storage stakingPosition = stakingPositionsValues[stakingPositionId];

		require(getCurrentStage() == Stage.FirstStage || stakingPosition.endEpoch != 0, "Wrong stage!"); // Requires correct stage or nft to be unstaked.
		require(votingPosition.endEpoch == 0, "E1");                     // Requires to be not liquidated yet.

		if (zooNumber > votingPosition.zooInvested)                                                   // If trying to withdraw more than invested, withdraws maximum.
		{
			zooNumber = votingPosition.zooInvested;
		}

		_withdrawZoo(zooNumber, beneficiary);
		_reduceZooVotes(votingPositionId, stakingPositionId, zooNumber);

		emit WithdrawedZooFromVoting(currentEpoch, voter, stakingPositionId, votingPositionId, zooNumber, beneficiary);
	}


	/// @notice Function to claim reward in yTokens from voting.
	/// @param votingPositionId - id of voting position.
	/// @param beneficiary - address of recipient of reward.
	function claimRewardFromVoting(uint256 votingPositionId, address voter, address beneficiary) external only(nftVotingPosition) returns (uint256 daiReward)
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];

		require(getCurrentStage() == Stage.FirstStage || stakingPositionsValues[votingPosition.stakingPositionId].endEpoch != 0, "Wrong stage!"); // Requires to be at first stage or position should be liquidated.

		updateInfo(votingPosition.stakingPositionId);

		(uint256 yTokenReward, uint256 zooRewards) = getPendingVoterReward(votingPositionId); // Calculates amount of reward in yTokens.

		yTokenReward += votingPosition.yTokensRewardDebt;                                // Adds reward debt, from previous epochs.
		zooRewards += zooTokensRewardDebt[votingPositionId];
		votingPosition.yTokensRewardDebt = 0;                                            // Nullify reward debt.
		zooTokensRewardDebt[votingPositionId] = 0;

		yTokenReward = yTokenReward * 95 / 96; // 95% of income to voter.

		require(vault.redeem(yTokenReward) == 0);                                                      // Withdraws dai from vault for yTokens, minus staker %.
		daiReward = dai.balanceOf(address(this));

		_stablecoinTransfer(beneficiary, daiReward);                             // Transfers voter part of reward.
		/*
		BattleRewardForEpoch storage battleReward = rewardsForEpoch[votingPosition.stakingPositionId][currentEpoch];
		if (battleReward.yTokens >= yTokenReward)
		{
			battleReward.yTokens -= yTokenReward;                                        // Subtracts yTokens for this position.
		}
		else
		{
			battleReward.yTokens = 0;
		}*/

		zoo.transfer(beneficiary, zooRewards);

		votingPosition.lastRewardedEpoch = computeLastEpoch(votingPositionId);           // Records epoch of last reward claimed.

		emit ClaimedRewardFromVoting(currentEpoch, voter, votingPosition.stakingPositionId, beneficiary, daiReward, votingPositionId);
	}

	// /// @dev Updates yTokensRewardDebt of voting.
	// /// @dev Called before every action with voting to prevent increasing share % in battle reward.
	// /// @param votingPositionId ID of voting to be updated.
	// function _updateVotingRewardDebt(uint256 votingPositionId) internal {
	// 	(uint256 reward,uint256 zooRewards) = getPendingVoterReward(votingPositionId);

	// 	if (reward != 0)
	// 	{
	// 		votingPositionsValues[votingPositionId].yTokensRewardDebt += reward;
	// 	}
	// 	if (zooRewards != 0)
	// 	{
	// 		zooTokensRewardDebt[votingPositionId] += zooRewards;
	// 	}

	// 	votingPositionsValues[votingPositionId].lastRewardedEpoch = currentEpoch;
	// }

	/// @notice Function to calculate pending reward from voting for position with this id.
	/// @param votingPositionId - id of voter position in battles.
	/// @return yTokens - amount of pending reward and 2 technical numbers, which must me always equal 0.
	function getPendingVoterReward(uint256 votingPositionId) public view returns (uint256 yTokens, uint256 zooRewards)
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];

		uint256 endEpoch = computeLastEpoch(votingPositionId);

		uint256 stakingPositionId = votingPosition.stakingPositionId;                  // Gets staker position id from voter position.

		uint256 pendingVotes = pendingVotes[votingPositionId];
		uint256 pendingVotesEpoch = pendingVotesEpoch[votingPositionId];
		uint256 votes = votingPosition.votes;
		for (uint256 i = votingPosition.lastRewardedEpoch; i < endEpoch; ++i)
		{
			if (i == pendingVotesEpoch && pendingVotes > 0)
			{
				votes += pendingVotes;
			}

			BattleRewardForEpoch storage leagueRewards = rewardsForEpoch[stakingPositionId][i];

			if (rewardsForEpoch[stakingPositionId][i].votes > 0) // Voting position participated in battle.
			{
				yTokens += rewardsForEpoch[stakingPositionId][i].yTokensSaldo * votes / rewardsForEpoch[stakingPositionId][i].votes;         // Calculates yTokens amount for voter.
				zooRewards += leagueRewards.zooRewards * votes / rewardsForEpoch[stakingPositionId][i].votes;         // Calculates yTokens amount for voter.
			}
		}

		return (yTokens, zooRewards);
	}

	/// @notice Function to claim reward for staker.
	/// @param stakingPositionId - id of staker position.
	/// @param beneficiary - address of recipient.
	function claimRewardFromStaking(uint256 stakingPositionId, address staker, address beneficiary) public only(nftStakingPosition) returns (uint256 daiReward)
	{
		StakerPosition storage stakerPosition = stakingPositionsValues[stakingPositionId];
		require(getCurrentStage() == Stage.FirstStage || stakerPosition.endEpoch != 0, "Wrong stage!"); // Requires to be at first stage in battle epoch.

		updateInfo(stakingPositionId);
		(uint256 yTokenReward, uint256 end) = getPendingStakerReward(stakingPositionId);
		stakerPosition.lastRewardedEpoch = end;                                               // Records epoch of last reward claim.

		require(vault.redeem(yTokenReward) == 0);                                                           // Gets reward from yearn.
		daiReward = dai.balanceOf(address(this));
		_stablecoinTransfer(beneficiary, daiReward);

		emit ClaimedRewardFromStaking(currentEpoch, staker, stakingPositionId, beneficiary, yTokenReward, daiReward);
	}

	/// @notice Function to get pending reward fo staker for this position id.
	/// @param stakingPositionId - id of staker position.
	/// @return stakerReward - reward amount for staker of this nft.
	function getPendingStakerReward(uint256 stakingPositionId) public view returns (uint256 stakerReward, uint256 end)
	{
		StakerPosition storage stakerPosition = stakingPositionsValues[stakingPositionId];
		uint256 endEpoch = stakerPosition.endEpoch;                                           // Gets endEpoch from position.

		end = endEpoch == 0 ? currentEpoch : endEpoch;                                        // Sets end variable to endEpoch if it non-zero, otherwise to currentEpoch.

		for (uint256 i = stakerPosition.lastRewardedEpoch; i < end; ++i)
		{
			stakerReward += rewardsForEpoch[stakingPositionId][i].yTokensSaldo / 96;                                          // Calculates reward for staker: 1% = 1 / 96
		}
	}

	/// @notice Function for pair nft for battles.
	/// @param stakingPositionId - id of staker position.
	function pairNft(uint256 stakingPositionId) external
	{
		require(getCurrentStage() == Stage.ThirdStage, "Wrong stage!");                       // Requires to be at 3 stage of battle epoch.

		updateInfo(stakingPositionId);
		BattleRewardForEpoch storage battleReward1 = rewardsForEpoch[stakingPositionId][currentEpoch];

		// this require makes impossible to pair if there are no available pair. // require(numberOfNftsWithNonZeroVotes / 2 > nftsInGame / 2, "E1");            // Requires enough nft for pairing.
		uint256 index1;                                                                       // Index of nft paired for.
		uint256[] memory leagueList = new uint256[](numberOfNftsWithNonZeroVotes);
		uint256 nftsInSameLeague = 0;
		bool idFound;

		// Find first staking position and get list of opponents from league for index2
		for (uint256 i = nftsInGame; i < numberOfNftsWithNonZeroVotes; ++i)
		{
			updateInfo(activeStakerPositions[i]);
			if (activeStakerPositions[i] == stakingPositionId)
			{
				index1 = i;
				idFound = true;
				continue;
				// break;
			}
			// In the same league
			else if (battleReward1.league == rewardsForEpoch[activeStakerPositions[i]][currentEpoch].league)
			{
				leagueList[nftsInSameLeague] = activeStakerPositions[i];
				nftsInSameLeague++;
			}
		}
		require(idFound, "E1");

		(activeStakerPositions[index1], activeStakerPositions[nftsInGame]) = (activeStakerPositions[nftsInGame], activeStakerPositions[index1]);// Swaps nftsInGame with index.
		nftsInGame++;                                                                         // Increases amount of paired nft.

		uint256 stakingPosition2;
		battleReward1.tokensAtBattleStart = sharesToTokens(battleReward1.yTokens);            // Records amount of yTokens on the moment of pairing for candidate.
		battleReward1.pricePerShareAtBattleStart = vault.exchangeRateCurrent();

		if (nftsInSameLeague != 0)
		{
			uint256 index2;
			stakingPosition2 = leagueList[0];
			if (nftsInSameLeague > 1)
			{
				stakingPosition2 = leagueList[zooFunctions.computePseudoRandom() % nftsInSameLeague];
			}

			for (uint256 i = nftsInGame; i < numberOfNftsWithNonZeroVotes; ++i)
			{
				if (activeStakerPositions[i] == stakingPosition2)
				{
					index2 = i;
				}
			}

			//updateInfo(stakingPosition2);
			BattleRewardForEpoch storage battleReward2 = rewardsForEpoch[stakingPosition2][currentEpoch];
			battleReward2.tokensAtBattleStart = sharesToTokens(battleReward2.yTokens);            // Records amount of yTokens on the moment of pairing for opponent.
			battleReward2.pricePerShareAtBattleStart = vault.exchangeRateCurrent();

			(activeStakerPositions[index2], activeStakerPositions[nftsInGame]) = (activeStakerPositions[nftsInGame], activeStakerPositions[index2]); // Swaps nftsInGame with index of opponent.
			nftsInGame++;                                                                         // Increases amount of paired nft.
		}
		else
		{
			stakingPosition2 = 0;
		}

		pairsInEpoch[currentEpoch].push(NftPair(stakingPositionId, stakingPosition2, false, false));// Pushes nft pair to array of pairs.
		uint256 pairIndex = getNftPairLength(currentEpoch) - 1;

		emit PairedNft(currentEpoch, stakingPositionId, stakingPosition2, pairIndex);
	}

	/// @notice Function to request random once per epoch.
	function requestRandom() public
	{
		require(getCurrentStage() == Stage.FifthStage, "Wrong stage!");                       // Requires to be at 5th stage.

		zooFunctions.requestRandomNumber();                                                 // Calls generate random number from chainlink or blockhash.
	}

	/// @notice Function for chosing winner for pair by its index in array.
	/// @notice returns error if random number for deciding winner is NOT requested OR fulfilled in ZooFunctions contract
	/// @param pairIndex - index of nft pair.
	function chooseWinnerInPair(uint256 pairIndex) external
	{
		require(getCurrentStage() == Stage.FifthStage, "Wrong stage!");                     // Requires to be at 5th stage.
		NftPair storage pair = pairsInEpoch[currentEpoch][pairIndex];
		require(pair.playedInEpoch == false, "E1");                      // Requires to be not paired before.

		uint256 randomNumber = zooFunctions.getRandomResult();
		uint256 votes1 = rewardsForEpoch[pair.token1][currentEpoch].votes;
		uint256 votes2 = rewardsForEpoch[pair.token2][currentEpoch].votes;

		playedVotes[stakingPositionsValues[pair.token1].collection][currentEpoch] += votes1;

		if (pair.token2 == 0)
		{
			votes2 = votes1;
		}
		else
		{
			playedVotes[stakingPositionsValues[pair.token2].collection][currentEpoch] += votes2;
		}

		pair.win = zooFunctions.decideWins(votes1, votes2, randomNumber);                   // Calculates winner and records it, 50/50 result
		// Getting winner and loser to calculate rewards
		(uint256 winner, uint256 loser) = pair.win? (pair.token1, pair.token2) : (pair.token2, pair.token1);
		_calculateBattleRewards(winner, loser);

		pair.playedInEpoch = true;

		emit ChosenWinner(currentEpoch, pair.token1, pair.token2, pair.win, pairIndex, ++numberOfPlayedPairsInEpoch); // Emits ChosenWinner event.
	}

	/// @dev Contains calculation logic of battle rewards
	/// @param winner stakingPositionId of NFT that WON in battle
	/// @param loser stakingPositionId of NFT that LOST in battle
	function _calculateBattleRewards(uint256 winner, uint256 loser) internal
	{
		BattleRewardForEpoch storage winnerRewards = rewardsForEpoch[winner][currentEpoch];

		uint256 income2;

		if (winner == 0 || loser == 0) // arena 50-50 case
		{
			if (winner == 0) // Battle Arena won
			{
				// Take yield
				income2 = _processBattleRecords(loser);
				require(vault.redeem(income2) == 0);
				_stablecoinTransfer(treasury, dai.balanceOf(address(this)));
			}
			else
			{
				// Grant Zoo
				winnerRewards.zooRewards += zooFunctions.getLeagueZooRewards(winnerRewards.league);
				winnerRewards.isWinnerChose = true;
			}
			return;
		}

		uint256 income1 = _processBattleRecords(winner);

		if (income1 == 0)
			return; // Skip all if price per share didn't change since pairing

		income2 = _processBattleRecords(loser);
		require(vault.redeem(((income1 + income2) / 25)) == 0);           // Withdraws stablecoins from vault for yTokens, minus staker %.

		uint256 daiReward = dai.balanceOf(address(this));
		_stablecoinTransfer(treasury, daiReward);                                       // Transfers treasury part. 4 / 100 == 4%

		winnerRewards.yTokensSaldo += (income1 + income2) * 96 / 100;
	}

	function _processBattleRecords(uint256 stakingPositionId) internal returns (uint256 income)
	{
		BattleRewardForEpoch storage currentEpochRecord = rewardsForEpoch[stakingPositionId][currentEpoch];
		BattleRewardForEpoch storage nextEpochRecord = rewardsForEpoch[stakingPositionId][currentEpoch + 1];

		uint256 currentPps = vault.exchangeRateCurrent();
		if (currentEpochRecord.pricePerShareAtBattleStart == currentPps)
			return 0; // Skip all and return 0 if price per share didn't change since pairing
		else
			income = currentEpochRecord.yTokens - tokensToShares(currentEpochRecord.tokensAtBattleStart);

		currentEpochRecord.pricePerShareCoef = currentPps * currentEpochRecord.pricePerShareAtBattleStart / (currentPps - currentEpochRecord.pricePerShareAtBattleStart);
		nextEpochRecord.yTokens += (currentEpochRecord.yTokens - income); // Deduct reward value.
		stakingPositionsValues[stakingPositionId].lastUpdateEpoch = currentEpoch + 1;           // Update lastUpdateEpoch to next epoch.
		nextEpochRecord.votes += currentEpochRecord.votes;                                   			// Update votes for next epoch.
		nextEpochRecord.league = zooFunctions.getNftLeague(nextEpochRecord.votes);	// Update league for next epoch.

		currentEpochRecord.isWinnerChose = true;
	}

	/// @notice Function for updating position from lastUpdateEpoch, in case there was no battle with position for a while.
	function updateInfo(uint256 stakingPositionId) public
	{
		StakerPosition storage position = stakingPositionsValues[stakingPositionId];
		uint256 lastUpdateEpoch = position.lastUpdateEpoch;                         // Get lastUpdateEpoch for position.
		if (lastUpdateEpoch == currentEpoch)                                        // If already updated in this epoch - skip.
			return;

		for (; lastUpdateEpoch < currentEpoch; ++lastUpdateEpoch)
		{
			BattleRewardForEpoch storage rewardOfCurrentEpoch = rewardsForEpoch[stakingPositionId][lastUpdateEpoch + 1];
			BattleRewardForEpoch storage rewardOflastUpdateEpoch = rewardsForEpoch[stakingPositionId][lastUpdateEpoch];

			rewardOfCurrentEpoch.votes += rewardOflastUpdateEpoch.votes;             // Get votes from lastUpdateEpoch.
			rewardOfCurrentEpoch.yTokens += rewardOflastUpdateEpoch.yTokens;         // Get yTokens from lastUpdateEpoch.

			rewardOfCurrentEpoch.league = zooFunctions.getNftLeague(rewardOfCurrentEpoch.votes);
		}

		position.lastUpdateEpoch = currentEpoch;                                    // Set lastUpdateEpoch to currentEpoch.
	}

	function _updateVotingPosition(uint256 votingPositionId) internal
	{
		VotingPosition storage position = votingPositionsValues[votingPositionId];

		(uint256 reward, uint256 zooRewards) = getPendingVoterReward(votingPositionId);
		voterIncentiveDebt[votingPositionId] += computeInvenctiveRewardForVoter(votingPositionId);

		if (reward != 0)
		{
			position.yTokensRewardDebt += reward;
		}
		if (zooRewards != 0)
		{
			zooTokensRewardDebt[votingPositionId] += zooRewards;
		}

		position.lastRewardedEpoch = currentEpoch;

		if (pendingVotesEpoch[votingPositionId] == 0 || pendingVotesEpoch[votingPositionId] == currentEpoch + 1) // If already updated in this epoch - skip.
			return;

		uint256 votes = pendingVotes[votingPositionId];
		position.daiVotes += votes;
		position.votes += votes;
		position.yTokensNumber += pendingYTokens[votingPositionId];

		pendingVotes[votingPositionId] = 0;
		pendingVotesEpoch[votingPositionId] = 0;
		pendingYTokens[votingPositionId] = 0;
	}

	/// @notice Function to increment epoch.
	function updateEpoch() public {
		require(getCurrentStage() == Stage.FifthStage, "Wrong stage!");             // Requires to be at fourth stage.
		require(block.timestamp >= epochStartDate + epochDuration); // Requires end of fifth stage to end.

		zooFunctions = IZooFunctions(zooGovernance.zooFunctions());                 // Sets ZooFunctions to contract specified in zooGovernance.

		epochStartDate = block.timestamp;                                           // Sets start date of new epoch.
		currentEpoch++;                                                             // Increments currentEpoch.
		epochsStarts[currentEpoch] = block.timestamp;                               // Records timestamp of new epoch start for ve-Zoo.
		nftsInGame = 0;                                                             // Nullifies amount of paired nfts.
		poolWeight[address(0)][currentEpoch] += poolWeight[address(0)][currentEpoch - 1];

		numberOfNftsWithNonZeroVotes += numberOfNftsWithNonZeroVotesPending;
		numberOfNftsWithNonZeroVotesPending = 0;
		numberOfPlayedPairsInEpoch = 0;

		zooFunctions.resetRandom();     // Resets random in zoo functions.

		(firstStageDuration, secondStageDuration, thirdStageDuration, fourthStageDuration, fifthStageDuration, epochDuration) = zooFunctions.getStageDurations();

		emit EpochUpdated(block.timestamp, currentEpoch);
	}

	/// @notice Function to calculate incentive reward from ve-Zoo for voter.
	function calculateIncentiveRewardForVoter(uint256 votingPositionId) external only(nftVotingPosition) returns (uint256 reward)
	{
		_updateVotingPosition(votingPositionId);
		reward = computeInvenctiveRewardForVoter(votingPositionId) + voterIncentiveDebt[votingPositionId];
		voterIncentiveDebt[votingPositionId] = 0;
	}

	function computeInvenctiveRewardForVoter(uint256 votingPositionId) internal returns (uint256 reward)
	{
		VotingPosition storage votingPosition = votingPositionsValues[votingPositionId];
		uint256 stakingPositionId = votingPosition.stakingPositionId;

		address collection = stakingPositionsValues[stakingPositionId].collection;
		updateInfo(stakingPositionId);
		updateInfoAboutStakedNumber(collection);                                      // Updates info about collection.
		
		uint256 lastEpoch = computeLastEpoch(votingPositionId); // Last epoch
		if (votingPosition.lastEpochOfIncentiveReward > lastEpoch)
			return 0;

		if (lastEpoch > endEpochOfIncentiveRewards)
			lastEpoch = endEpochOfIncentiveRewards;

		uint256 votes = votingPosition.votes;
		for (uint256 i = votingPosition.lastEpochOfIncentiveReward; i < lastEpoch; ++i)
		{
			if (i == pendingVotesEpoch[votingPositionId])
				votes += pendingVotes[votingPositionId];

			if (poolWeight[address(0)][i] != 0 && rewardsForEpoch[stakingPositionId][i].isWinnerChose) // Check that collection has non-zero weight in veZoo and nft played in battle.
				reward += baseVoterReward * votes * poolWeight[collection][i] / (poolWeight[address(0)][i] * playedVotes[collection][i]);
		}

		votingPosition.lastEpochOfIncentiveReward = lastEpoch;
	}

	/// @notice Function to calculate incentive reward from ve-Zoo for staker.
	function calculateIncentiveRewardForStaker(uint256 stakingPositionId) external only(nftStakingPosition) returns (uint256 reward)
	{
		StakerPosition storage stakingPosition = stakingPositionsValues[stakingPositionId];

		address collection = stakingPosition.collection;                              // Gets nft collection.
		updateInfo(stakingPositionId);                                                // Updates staking position params from previous epochs.
		updateInfoAboutStakedNumber(collection);                                      // Updates info about collection.

		uint256 end = stakingPosition.endEpoch == 0 ? currentEpoch : stakingPosition.endEpoch;// Get recorded end epoch if it's not 0, or current epoch.
		if (end > endEpochOfIncentiveRewards)
			end = endEpochOfIncentiveRewards;

		for (uint256 i = stakingPosition.lastEpochOfIncentiveReward; i < end; ++i)
		{
			if (poolWeight[address(0)][i] != 0)
				reward += baseStakerReward * poolWeight[collection][i] / (poolWeight[address(0)][i] * numberOfStakedNftsInCollection[i][collection]);
		}

		stakingPosition.lastEpochOfIncentiveReward = currentEpoch;

		return reward;
	}

	/// @notice Function to get last epoch.
	function computeLastEpoch(uint256 votingPositionId) public view returns (uint256 lastEpochNumber)
	{
		VotingPosition storage votingposition = votingPositionsValues[votingPositionId];
		//uint256 stakingPositionId = votingposition.stakingPositionId;  // Gets staker position id from voter position.
		uint256 lastEpochOfStaking = stakingPositionsValues[votingposition.stakingPositionId].endEpoch;        // Gets endEpoch from staking position.

		// Staking - finished, Voting - finished
		if (lastEpochOfStaking != 0 && votingposition.endEpoch != 0)
		{
			lastEpochNumber = Math.min(lastEpochOfStaking, votingposition.endEpoch);
		}
		// Staking - finished, Voting - existing
		else if (lastEpochOfStaking != 0)
		{
			lastEpochNumber = lastEpochOfStaking;
		}
		// Staking - exists, Voting - finished
		else if (votingposition.endEpoch != 0)
		{
			lastEpochNumber = votingposition.endEpoch;
		}
		// Staking - exists, Voting - exists
		else
		{
			lastEpochNumber = currentEpoch;
		}
	}

	function updateInfoAboutStakedNumber(address collection) public returns (uint256 actualWeight)
	{
		uint256 lastUpdateEpoch = lastUpdatesOfStakedNumbers[collection];
		if (lastUpdateEpoch == currentEpoch || collection == address(0))
			return poolWeight[collection][currentEpoch];

		uint256 i = lastUpdateEpoch + 1;
		for (; i <= currentEpoch; ++i)
		{
			numberOfStakedNftsInCollection[i][collection] += numberOfStakedNftsInCollection[i - 1][collection];
			poolWeight[collection][i] += poolWeight[collection][i - 1];
		}

		lastUpdatesOfStakedNumbers[collection] = currentEpoch;
		return poolWeight[collection][currentEpoch];
	}

	/// @notice Internal function to calculate amount of zoo to burn and withdraw.
	function _withdrawZoo(uint256 zooAmount, address beneficiary) internal
	{
		uint256 zooWithdraw = zooAmount * 995 / 1000; // Calculates amount of zoo to withdraw.

		lpZoo.transfer(beneficiary, zooWithdraw);                                           // Transfers lp to beneficiary.
		lpZoo.transfer(treasury, zooAmount * 5 / 1000);
	}

	function _stablecoinTransfer(address who, uint256 value) internal
	{
		if (value > 0)
			dai.transfer(who, value);
	}

	/// @notice Function to view current stage in battle epoch.
	/// @return stage - current stage.
	function getCurrentStage() public view returns (Stage)
	{
		uint256 time = epochStartDate + firstStageDuration;
		if (block.timestamp < time)
		{
			return Stage.FirstStage; // Staking stage
		}

		time += secondStageDuration;
		if (block.timestamp < time)
		{
			return Stage.SecondStage; // Dai vote stage.
		}

		time += thirdStageDuration;
		if (block.timestamp < time)
		{
			return Stage.ThirdStage; // Pair stage.
		}

		time += fourthStageDuration;
		if (block.timestamp < time)
		{
			return Stage.FourthStage; // Zoo vote stage.
		}
		else
		{
			return Stage.FifthStage; // Choose winner stage.
		}
	}
}