pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

interface INftVotingPosition
{
	function setNftBattleArena(address _nftBattleArena) external;

	function createNewVotingPosition(uint256 stakingPositionId, uint256 amount) external;

	function addDaiToPosition(uint256 votingPositionId, uint256 amount) external returns (uint256 votes);

	function addZooToPosition(uint256 votingPositionId, uint256 amount) external returns (uint256 votes);

	function withdrawDaiFromVotingPosition(uint256 votingPositionId, uint256 daiNumber, address beneficiary) external;

	function withdrawZooFromVotingPosition(uint256 votingPositionId, uint256 zooNumber, address beneficiary) external;

	function claimRewardFromVoting(uint256 votingPositionId, address beneficiary) external;
}