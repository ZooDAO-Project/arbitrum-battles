pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

import "@OpenZeppelin/contracts/token/ERC20/IERC20.sol";

/// @notice contract to get tokens for open test of zoo dao battle arena.
contract ZooTokenFaucet {
	IERC20 public zoo;

	uint256 public attemptLimit;
	uint256 public faucetAmount;                                 // Fixed amount of tokens to get.

	mapping (address => bool) whiteList;                         // WhiteList for admin functions.
	mapping (address => uint256) public attemptAmount;

	event ZooGiven(address indexed user);

	constructor (address _zoo, uint256 attempts)
	{
		zoo = IERC20(_zoo);

		whiteList[msg.sender] = true;

		attemptLimit = attempts;
		faucetAmount = 5000 * 10 ** 18;
	}

	/// @notice Function to get test test zoo.
	function getZoo() external 
	{
		require(attemptAmount[msg.sender] < attemptLimit, "reached attempt limit");
		uint256 zooBalance = zoo.balanceOf(address(this));
		require(zooBalance >= faucetAmount, "not enough tokens");

		zoo.transfer(msg.sender, faucetAmount);
		attemptAmount[msg.sender] += 1;

		emit ZooGiven(msg.sender);
	}

	/// @notice Function for sending tokens for list of recipients.
	/// @param recipients - array of recipients.
	/// @param sendAmount - amount of zoo and dai tokens to send.
	function batchFaucet(address[] calldata recipients, uint256 sendAmount) external onlyWhiteList
	{
		uint256 totalTokensTransfered = sendAmount * recipients.length;
		uint256 zooBalance = zoo.balanceOf(address(this));
		require(zooBalance >= totalTokensTransfered, "not enough tokens");

		for (uint256 i = 0; i < recipients.length; i++)
		{
			zoo.transfer(recipients[i], sendAmount);
		}
	}

	function returnTokens(uint256 zooAmount) external onlyWhiteList
	{
		zoo.transfer(msg.sender, zooAmount);
	}

	function addToWhiteList(address user) external onlyWhiteList
	{
		whiteList[user] = true;
	}

	function batchAddToWhiteList(address[] calldata users) external onlyWhiteList
	{
		for (uint256 i = 0; i < users.length; i++) {
			whiteList[users[i]] = true;
		}
	}

	function changeAttemptLimit(uint256 amount) external onlyWhiteList
	{
		attemptLimit = amount;
	}

	function setFaucetAmount(uint256 amount) external onlyWhiteList
	{
		faucetAmount = amount;
	}

	modifier onlyWhiteList()
	{	
		require(whiteList[msg.sender] == true, "not whitelisted");
		_;
	}
}
