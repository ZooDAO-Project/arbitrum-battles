pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

interface INftBattleArena {

	/* STAKER */
	function createNewStakerPosition() external returns (uint);
	function unstakeNft(uint256 stakingPositionId) external;
	
	function claimRewardFromStaking(uint256 stakingPositionId, address beneficiary) external;
	function getPendingStakerReward(uint256 stakingPositionId) external view returns (uint256 stakerReward, uint256 end);


	/* VOTER */
	function createNewVotingPosition(uint256 stakingPositionId, uint256 amount) external returns (uint256 votes, uint256 votingPositionId);
	function liquidateVotingPosition(uint256 votingPositionId, address beneficiary) external;

	function claimRewardFromVoting(uint256 votingPositionId, address beneficiary) external returns (uint256 rewardDaiAmount);
	function getPendingVoterReward(uint256 votingPositionId, uint256 startEpoch, uint256 endEpoch) external view returns (uint256 rewardAmount);

	function recomputeDaiVotes(uint256 votingPositionId) external;
	function recomputeZooVotes(uint256 votingPositionId) external;

	function addDaiToPosition(uint256 votingPositionId, uint256 amount) external returns (uint256 votes);
	function addZooToPosition(uint256 votingPositionId, uint256 amount) external  returns (uint256 votes);

	function withdrawZooFromVotingPosition(uint256 votingPositionId, uint256 zooNumber, address beneficiary) external;
	function withdrawDaiFromVotingPosition(uint256 votingPositionId, uint256 daiNumber, address beneficiary) external;


	/* BATTLE */
	function getBattleReward(uint256 stakingPositionId, uint256 epoch) external;

	function getStakerPositionsLength() external view returns (uint256 amount);
	function getNftPairLength(uint256 epoch) external view returns(uint256 length) ;

	function sharesToTokens(uint256 sharesAmount) external view returns (uint256 tokens);
	function tokensToShares(int256 tokens) external view returns (int256 shares);

	function pairNft(uint256 stakingPositionId) external;

	function requestRandom() external;
	function chooseWinnerInPair(uint256 pairIndex) external;

	function updateInfo(uint256 stakingPositionId) external;

	function updateEpoch() external;

	function computeLastEpoch(uint256 votingPositionId) external view returns (uint256 lastEpochNumber);

	function calculateWithdrawForZoo(uint256 zooAmount, address beneficiary) external;

	function getCurrentStage() external;
}