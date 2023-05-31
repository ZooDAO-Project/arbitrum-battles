pragma solidity 0.8.13;
// SPDX-License-Identifier: MIT

import "@OpenZeppelin/contracts/utils/Counters.sol";
import "@OpenZeppelin/contracts/token/ERC721/ERC721.sol";

/// @notice Contract for minting nfts for open test of zoo dao battle arena.
contract ZooNftFaucet is ERC721 {

	using Counters for Counters.Counter;

	Counters.Counter private _tokenIdTracker;                   // Token id tracker.

	uint256 public delayTime;

	mapping (address => bool) whiteList;                        // WhiteList for admin functions.
	mapping (address => uint256) lastAttempt;

	constructor(string memory name, string memory symbol) ERC721(name, symbol) 
	{
		whiteList[msg.sender] = true;
		delayTime = 1 days;
	}

	/// @notice Function to mint test nft for msg.sender.
	/// @notice allowed to everyone to mint nft eligible in arena for test purposes once per day.
	function mintNft() external returns (uint256 newId)
	{
		require(block.timestamp > lastAttempt[msg.sender] + delayTime, "mint allowed once per a day");
		_tokenIdTracker.increment();
		newId = _tokenIdTracker.current();
		_safeMint(msg.sender, newId);

		lastAttempt[msg.sender] = block.timestamp;
	}

	/// @notice Function to mint 30 nft for recipient.
	/// @notice admin only function.
	/// @param recipient - address receiver.
	function multiMint(address recipient, string memory batchUri) external onlyWhiteList
	{
		uint256 currentId = _tokenIdTracker.current();
		while (_tokenIdTracker.current() < currentId + 30)
		{
			string memory imageUri = batchUri;
			_tokenIdTracker.increment();
			uint256 newId = _tokenIdTracker.current();
			_safeMint(recipient, newId);
		}
	}

	/// @notice Function to mint nfts for list of users.
	/// @notice admin only function.
	/// @param recipients - array of address to send nft.
	/// @param nftAmount - amount of nft to mint for every recipient.
	function batchMint(address[] calldata recipients, uint256 nftAmount) external onlyWhiteList
	{
		string memory imageUri = "zoo testnet release";
		for (uint256 i = 0; i < recipients.length; i++) 
		{
			uint256 currentId = _tokenIdTracker.current();
			while (_tokenIdTracker.current() < currentId + nftAmount)
			{
				_tokenIdTracker.increment();
				uint256 newId = _tokenIdTracker.current();
				_safeMint(recipients[i], newId);
				// _setTokenURI(newId, imageUri);
			}
		}
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

	function changeDelayTime(uint256 time) external onlyWhiteList
	{
		delayTime = time;
	}

	modifier onlyWhiteList()
	{	
		require(whiteList[msg.sender] == true, "not whitelisted");
		_;
	}
}
