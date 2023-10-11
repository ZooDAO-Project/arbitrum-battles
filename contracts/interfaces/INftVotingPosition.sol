pragma solidity 0.8.17;

// SPDX-License-Identifier: MIT

interface INftVotingPosition
{
	function setNftBattleArena(address _nftBattleArena) external;

	function createNewVotingPosition(uint256 stakingPositionId, uint256 amount) payable external returns (uint256 votes);

	function createNewVotingPositionStable(uint256 stakingPositionId, uint256 amount, bool allowToSwapVotes, address token, uint256 minUsdg, uint256 minGlp) payable external returns (uint256 votes);

	function addDaiToPosition(uint256 votingPositionId, uint256 amount) payable external returns (uint256 votes);

	function addDaiToPositionStable(uint256 votingPositionId, uint256 amount, address token, uint256 minUsdg, uint256 minGlp) payable external returns (uint256 votes);

	function addZooToPosition(uint256 votingPositionId, uint256 amount) external returns (uint256 votes);

	function withdrawDaiFromVotingPosition(uint256 votingPositionId, uint256 daiNumber, address beneficiary) external;

	function withdrawDaiFromVotingPositionStable(uint256 votingPositionId, address beneficiary, uint256 daiNumber, uint256 minOut, address tokenToReceive) external;

	function withdrawZooFromVotingPosition(uint256 votingPositionId, uint256 zooNumber, address beneficiary) external;

	function claimRewardFromVoting(uint256 votingPositionId, address beneficiary) external;
}