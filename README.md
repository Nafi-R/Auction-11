*Tournament*

[Official Competition details can be found here!](https://www.notion.so/READ-ME-68e95ca047c24c82b834890488e65fc2)

This competition will be a tournament consisting of a number of games. A tournament engine will automatically schedule games involving multiple teams at a time

Final Placement

![alt text](https://i.imgur.com/crS52Ya.png)

Game Details
- Games
	- Each game will have exactly 3 competitor teams. Each competitor team submits one copy of code; and their code is run on 2≤b≤3 exactly 3 **bots**.
      Each game will also have exactly 12 **bots**, with the remaining non-player bots being filled by ***NPC bots.
        *** ***NPC bots*** behave in a set manner, see below
    - The order of the bots is random and fixed. Each bot's position then serves as its ID
     - At the start of the game, bots will not know which bots belong to which teams, including their own teams. There is no private way to communicate between bots on the same team.
     - *NPC bots* make bids randomly with a bid size related to the minimum bid size. The probability at which a bid is made by a random bot decreases as the value increases. 
          The NPC bot code is visible to all competitors in the `gameEngine.py` file, see submission guidelines in:
          [Submission & Ranking](https://www.notion.so/Submission-Ranking-f235d5f93b834fa1a9f4adff48ad797c)
     - **Game parameters**
     	A number of parameters of the game, including the mean of the true value distribution, will be broadcasted at the start of the game 
        	- see [API] (https://www.notion.so/API-81ff407992ce44ae81f780a70f1bd2d5)  for more details

- **Rounds**

	During the game, a number of rounds will take place, where an item will be placed for auction

	- *At the start of a round*

		- An item will be put up for auction. The true value of the item up for auction is broadcasted to a select number of bots.
		- Each team has a [~~75~~ 100% chance] of receiving the true value, a maximum of one bot from each team will recieve the true value

		- The true value is sampled from a normal distribution truncated to:

			-1 ≤ z-score ≤ 1

		- The mean and z-score will be provided to the teams, see [API](https://www.notion.so/API-81ff407992ce44ae81f780a70f1bd2d5)
    - *During a single round*

		- Bots will be asked to bid clockwise starting from a random bot
		- Bids MUST be at least 8 more than the previous value, otherwise they will not be counted
		- If a bidding round finishes without any new bids, the last bidder will receive points = item true value - bid value. This value can be negative
		- If the winning bidder originally knew the true value, the winning bidder's team will incur a penalty of 50 points
		- *At the end of the round*

 	- A **reporting phase** will begin. Every bot in each team will be asked to report on which bots they have identified are (see below)
		- No points will be given for failing to identify bots in any of the categories below
		- The reporting score will be rounded up to 0 if it is negative
		- For your team, only one reporting score (the highest) from all your bots will be kept for each round your own team's bots
		- for each bot correctly identified, you will score +k points; for each bot wrongly identified, you will score -k points
				- k = 100 / (number of bots in team-1)
				- If a bot self-reports, it will not be counted
		- competitor teams' bots (not grouped by team)
				- for each opponent bot reported, you will score +15 points;
				- for each **NPC bot** reported, you will score -90 points
				- If you report your own bots, you will not score any points
		- bots which knew the true value at the start of the game
				- for each bot correctly identified they will score +100 points; for each bot wrongly identified, you will score -50 points
				- If the current bot knows the true value and self-reports, this is not counted
