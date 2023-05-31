pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

import "@OpenZeppelin/contracts/token/ERC721/ERC721.sol";
import "@OpenZeppelin/contracts/access/Ownable.sol";

contract ZooNft is ERC721, Ownable
{
	uint256 public counter;

	constructor (string memory name, string memory symbol) ERC721(name, symbol)
	{

	}

	function mint(address recipient) external onlyOwner
	{
		_mint(recipient, counter);
		counter++;
	}
}
