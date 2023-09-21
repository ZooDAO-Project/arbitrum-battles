pragma solidity 0.8.17;

// SPDX-License-Identifier: MIT

import "@OpenZeppelin/contracts/token/ERC20/extensions/ERC4626.sol";

contract GaugeMock
{
	ERC4626 public lpZoo;
	
	mapping (address => uint256) balances;

	constructor(ERC4626 _lpZoo)
	{
		lpZoo = _lpZoo;
	}

	function deposit(uint256 value) external 
	{
		lpZoo.transferFrom(msg.sender, address(this), value);
		balances[msg.sender] += value;
	}

	function withdraw(uint256 value) external
	{
		require(balances[msg.sender] >= value, "exceed user balance");
		lpZoo.transfer(msg.sender, value);
		balances[msg.sender] -= value;
	}
}