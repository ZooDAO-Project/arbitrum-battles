pragma solidity 0.8.13;


// SPDX-License-Identifier: MIT

interface INftStakingPosition
{
	function setNftBattleArena(address _nftBattleArena) external;

	function stakeNft(address token, uint256 id) external;

	function unstakeNft(uint256 stakingPositionId) external;

	function claimRewardFromStaking(uint256 stakingPositionId, address beneficiary) external;

	function allowNewContractForStaking(address token) external;
}