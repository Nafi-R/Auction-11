class CompetitorInstance():
    def __init__(self):
        # initialize personal variables
        self.minbid = 0
        self.trueValue = -1
        self.should_bid = True
        self.our_lastBid = 0
        self.thisisatest = "hey"
        pass
    
    def onGameStart(self, engine, gameParameters):
        # engine: an instance of the game engine with functions as outlined in the documentation.
        self.engine=engine
        # gameParameters: A dictionary containing a variety of game parameters
        self.gameParameters = gameParameters
        self.minbid = gameParameters["minimumBid"]
        self.engine.print("Game Started!")

    
    def onAuctionStart(self, index, trueValue):
        # index is the current player's index, that usually stays put from game to game
        # trueValue is -1 if this bot doesn't know the true value 
        # if we know the true value, let others bid.
        # If within certain range, allow us to buy
        self.trueValue = trueValue
        self.engine.print("Auction Started!")


    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was
        self.engine.print(f"Someone at position [{whoMadeBid}] made a bid for (${howMuch})")
        pass

    def onMyTurn(self,lastBid):
        # lastBid is the last bid that was made
        mean = self.gameParameters["meanTrueValue"]
        stdv = self.gameParameters["stddevTrueValue"]
        our_bid = lastBid + self.minbid + 1
        if(lastBid == self.our_lastBid):
            return
        if(self.trueValue != -1):
            if(lastBid <= self.trueValue/2):
                self.engine.makeBid(our_bid)
                self.engine.print(f"We made a bid for {our_bid} and the true val is: {self.trueValue}")
                self.our_lastBid = our_bid
                return
        if (lastBid < mean - abs(stdv)):
            # But don't bid too high!
            self.engine.makeBid(lastBid+self.minbid + 1)
            self.engine.print(f"We made a bid for {our_bid}")
            self.our_lastBid = our_bid
        pass

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.print(f"Auction Ended")
        pass