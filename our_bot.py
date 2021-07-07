class CompetitorInstance():
    def __init__(self):
        # initialize personal variables
        self.minbid = 0
        self.trueValue = -1
        self.should_bid = True
        self.our_lastBid = 0
        self.penalty = 50
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
        #our_bid = lastBid + self.minbid + 1
        if(lastBid == self.our_lastBid):
            return
        
        our_min_bid = last_bid + self.minbid + 1

        sd_025_range = range(mean - 0.25*stdv, mean + 0.25*stdv)
        sd_05_range = range(mean - 0.5*stdv, mean + 0.5*stdv)
        sd_075_range = range(mean -0.75*stdv, mean + 0.75*stdv)
        if(self.trueValue != -1): #know true value
            if self.trueValue in sd_025_range:
                our_bid = random.randint(our_min_bid, range(mean-stdv,mean-0.25*stdv))
            if self.trueValue in sd_05_range - sd_025_range:
                our_bid = random.randint(our_min_bid, range(mean-stdv,mean-0.5*stdv))
            if self.trueValue in sd_075_range - sd_075_range:
                our_bid = random.randint(our_min_bid, range(mean-stdv,mean-0.75*stdv))

            self.engine.makebid(our_bid)
            self.engine.print(f"We made a bid for {our_bid} and the true value is: {self.trueValue}")
            self.our_lastBid = our_bid

        if(self.trueValue == -1): # don't know true value
            pass

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.print(f"Auction Ended")
        pass