pragma solidity 0.8.17;

// SPDX-License-Identifier: MIT

import "@OpenZeppelin/contracts/token/ERC721/IERC721.sol";
import "@OpenZeppelin/contracts/token/ERC20/IERC20.sol";
import "@OpenZeppelin/contracts/access/Ownable.sol";
import "./interfaces/IZooFunctions.sol";

/// @title WinnersJackpot
/// @notice contract for jackpot reward from arena.
contract WinnersJackpot is Ownable
{
	IERC721 public votingPosition;
	// Jackpot public jackpot;

	IERC20 public frax;
	IERC20 public zoo;

	IZooFunctions public zooFunctions;

	// battle season => id of position
	mapping (uint256 => uint256) public winners;

	// season => id of position => votes
	mapping (uint256 => mapping(uint256 => uint256)) public participants;

	event WinnerChosen(uint256 indexed season, address indexed winner, uint256 indexed winnerId, uint256 totalParticipants, uint256 totalVotes, uint256 fraxReward, uint256 zooReward);

	constructor (address _functions, address _votingPosition, address _frax, address _zoo)
	{
		frax = IERC20(_frax);
		zoo = IERC20(_zoo);
		zooFunctions = IZooFunctions(_functions);
		votingPosition = IERC721(_votingPosition);
	}

	/// @notice Function to choose jackpot winner in selected season.
	/// @param voterIds - array of id of voter positions, winners of season to choose from.
	/// @param votes - array of votes from voter positions of winners of season for chance to win.
	/// @param season - season to choose winner.
	function chooseWinner(uint256[] calldata voterIds, uint256[] calldata votes, uint256 season) external onlyOwner returns (address)
	{
		require(winners[season] == 0, "winner has been chosen");
		uint256 random = zooFunctions.getRandomResultByEpoch(season);
		require(random != 0, "requestRandom has not been called");
		uint256 totalParticipants;
		uint256 lotteryNumbers;                                   // total amount of votes and lottery tickets.

		for (uint256 i = 0; i < voterIds.length; i++)             // iterate through voter positions of participants.
		{
			lotteryNumbers += votes[i];                           // Add amount of votes to total.
			participants[season][voterIds[i]] = lotteryNumbers;   // Add amount of lottery numbers to participant.
			totalParticipants++;
		}

		uint256 winnerNumber = random % lotteryNumbers;           // Get number of winners ticket.

		for (uint256 i = 0; i < voterIds.length; i++)             // iterate thought voter positions again, to calculate who get winner ticket.
		{
			if (participants[season][voterIds[i]] >= winnerNumber)// If winner ticket is withing participants numbers,
			{
				winners[season] = voterIds[i];                    // Set the winner for season and stop iterate.
				break;
			}
		}

		uint256 fraxReward = frax.balanceOf(address(this));
		uint256 zooReward = zoo.balanceOf(address(this));

		address winner = votingPosition.ownerOf(winners[season]); // Get the owner of winners position.

		frax.transfer(winner, fraxReward);         // Transfer reward in frax.
		zoo.transfer(winner, zooReward);          // Transfer reward in zoo.

		emit WinnerChosen(season, winner, winners[season], totalParticipants, lotteryNumbers, fraxReward, zooReward);

		return winner;
	}

	/// @notice Function to check winner in selected season. 
	function checkWinner(uint256 season) public view returns (uint256 positionId)
	{
		return winners[season];
	}

	/// @notice Function to return tokens, in case something went wrong.
	function returnTokens(uint256 fraxAmount, uint256 zooAmount, address recipient) external onlyOwner
	{
		frax.transfer(recipient, fraxAmount);
		zoo.transfer(recipient, zooAmount);
	}
}