class CompetitorInstance():
    def __init__(self):
        # initialize personal variables
        self.minbid = 0
        self.trueValue = -1
        self.should_bid = True
        self.our_lastBid = 0
        self.prevBid = 0
        self.hasBid = False 
        self.has_made_first_bid = [] 
        self.our_bots = []
        self.competitor_bots = []

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
        self.engine.print(f"Our Bot index is {index}")
        self.trueValue = trueValue
        self.our_bots = []
        self.competitor_bots = []
        self.has_made_first_bid = []
        self.our_lastBid = 0
        self.prevBid = 0
        self.should_bid = True
        self.hasBid = False 
        self.has_made_first_bid = [] 



    def is_NPC(self, currentBid) -> bool:
        bid_diff = currentBid - self.prevBid
        if bid_diff >= self.minbid and bid_diff <= 3*self.minbid:
            return True
        else:
            if bid_diff < 0:
                return True
            else:
                return False

    def onBidMade(self, whoMadeBid, howMuch):
        if (self.is_NPC(howMuch) == False):
            if whoMadeBid not in self.competitor_bots:
                self.competitor_bots.append(whoMadeBid)

        self.prevBid = howMuch
    

    def math_func(self,lastBid) -> int:
        last_digit = (lastBid+8)%10
        power_digit = last_digit^2
        bid = (lastBid+8) + power_digit
        return bid

    def onMyTurn(self,lastBid):
        # lastBid is the last bid that was made
        mean = self.gameParameters["meanTrueValue"]
        stdv = self.gameParameters["stddevTrueValue"]

        #run only on first bid to identify bots
        if self.hasBid == False:
            self.our_lastBid = self.math_func(lastBid)
            self.engine.makeBid(self.our_lastBid)
            self.hasBid = True
        else:
            if(self.trueValue == -1): # don't know true value
                pass
            else: # If we do know the true value
                pass

        ###                      ###
        # Bidding Code to be ADDED #
        ###                      ###
    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.print(f"Auction Ended")
        self.engine.print(f"Our bots are {self.our_bots} and enemy bots are {self.competitor_bots}")
        pass