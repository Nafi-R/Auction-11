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
        self.ourbots = []
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
        self.trueValue = trueValue
        self.engine.print("Auction Started!")


    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was
        
        #identify who made their first bid
        # if bid is made, check if equal to our first bid by inversing the math function
        # if not our bot, check is NPC bot
        # if not NPC bot, add to competitor list
        # identify who didn't make a bid 
        if whoMadeBid not in self.has_made_first_bid:
            temp = self.prevBid
            if howMuch == self.math_func(temp):
                self.ourbots.append(whoMadeBid)
                self.engine.print(f"Our bots are {self.ourbots}")
            else:
                self.competitor_bots.append(whoMadeBid)
                self.engine.print(f"Our competitors bots are {self.competitor_bots}")
            
            self.has_made_first_bid.append(whoMadeBid)
        self.prevBid = howMuch
        self.engine.print(f"Someone at position [{whoMadeBid}] made a bid for (${howMuch})")
        pass
    

    def math_func(self,lastBid) -> int:
        last_digit = (lastBid+8)%10
        power_digit = last_digit^2
        bid = (lastBid+8) + power_digit
        return bid
        
        #lastbid = 2000
        # minbid = 2000 + 8 = 2008
        #last_digit = 8
        #power_digit = last_digit^2 (64)
        #prevBid = (lastBid+8) + power_digit (2072)
        #prevBid = 2072

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
            pass
        ###                      ###
        # Bidding Code to be ADDED #
        ###                      ###


        #our_bid = lastBid + self.minbid + 1
        
        #if(lastBid == self.our_lastBid):
        #    return
        
        #our_min_bid = lastBid + self.minbid + 1

        #sd_025_range = range(mean - 0.25*stdv, mean + 0.25*stdv)
        #sd_05_range = range(mean - 0.5*stdv, mean + 0.5*stdv)
        #sd_075_range = range(mean -0.75*stdv, mean + 0.75*stdv)
        #if(self.trueValue != -1): #know true value
         #   if self.trueValue in sd_025_range:
          #      our_bid = random.randint(our_min_bid, range(mean-stdv,mean-0.25*stdv))
           # if self.trueValue in sd_05_range - sd_025_range:
            #    our_bid = random.randint(our_min_bid, range(mean-stdv,mean-0.5*stdv))
            #if self.trueValue in sd_075_range - sd_075_range:
             #   our_bid = random.randint(our_min_bid, range(mean-stdv,mean-0.75*stdv))

            # self.engine.makebid(our_bid)
            # self.engine.print(f"We made a bid for {our_bid} and the true value is: {self.trueValue}")
            # self.our_lastBid = our_bid

        if(self.trueValue == -1): # don't know true value
            pass

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.print(f"Auction Ended")
        self.engine.print(f"Our bots are {self.ourbots} and enemy bots are {self.competitor_bots}")
        pass