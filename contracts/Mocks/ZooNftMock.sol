pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

import "@OpenZeppelin/contracts/token/ERC721/ERC721.sol";

contract NftMock is ERC721
{
	uint256 public counter;

	constructor () ERC721("Test NFT", "TEST")
	{

	}

	function mint(uint256 quantity) external
	{
		for (uint256 i = 0; i < quantity; i++) 
		{
			_safeMint(msg.sender, counter);
			counter++;
		}
	}
}

