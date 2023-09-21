pragma solidity 0.8.17;

// SPDX-License-Identifier: MIT

import "@OpenZeppelin/contracts/token/ERC20/extensions/ERC4626.sol";

contract VeBalRewardMock
{
	ERC4626 public lpZoo;
	address public veBalGauge;

	uint256 public reward;

	constructor(ERC4626 _lpZoo, address _gauge)
	{
		lpZoo = _lpZoo;
		veBalGauge = _gauge;
	}

	function claimRewardsFromGauge(address gauge, address user) external
	{
		lpZoo.transfer(user, reward);
	}

	function setRewardAmount(uint256 amount) external
	{
		reward = amount;
	}
}