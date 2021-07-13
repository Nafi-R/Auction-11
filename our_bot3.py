class CompetitorInstance():
    def __init__(self):
        # initialize personal variables
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
        self.engine.print(f"Our Bot index is {index}")
        self.thisIndex = index
        self.value = trueValue if trueValue != -1 else self.gameParameters["meanTrueValue"]
        self.our_bots = []
        self.other_bots = []
        self.competitor_bots = []
        self.known_bots = []
        self.has_made_first_bid = []
        self.our_lastBid = 0
        self.prevBid = 1
        self.should_bid = True
        self.hasBid = False
        self.bid_diff = {}
        for i in range(0,self.gameParameters["numPlayers"]):
            self.bid_diff[i] = set()


    def is_NPC(self, currentBid) -> bool:
        bid_diff = currentBid - self.prevBid
        if bid_diff <= 3*self.minbid:
            return True
        else:
            return False

    def onBidMade(self, whoMadeBid, howMuch):
        self.placeBot(whoMadeBid, howMuch)
        self.prevBid = howMuch
    
    def placeBot(self, index, howMuch):
        #OUTPUT: "Own", "Competitor", "NPC"
        if self.math_func(self.prevBid) == howMuch:
            if index not in self.other_bots:
                self.addOwnBot(index)
                return
        else:
            if index not in self.other_bots:
                self.other_bots.append(index)
        if self.isCompetitor(index,howMuch) == True:
            self.addCompetitor(index)

    def isCompetitor(self, index, howMuch) -> bool:
        if(self.is_NPC(howMuch) == False):
            return True
        else:
            self.bid_diff[index].add(howMuch - self.prevBid)
            return False

    def removeOwnBot(self, index):
        if index in self.our_bots:
            self.our_bots.remove(index)

    def addOwnBot(self, index):
        if index in self.competitor_bots:
            return
        if index not in self.our_bots:
            self.our_bots.append(index)

    def addCompetitor(self, index):
        self.removeOwnBot(index)
        if index not in self.competitor_bots:
            self.competitor_bots.append(index)
    
    def addRemainingCompetitors(self):
        for index in self.bid_diff:
            if index not in self.our_bots:
                if index not in self.competitor_bots:
                    size = len(self.bid_diff[index])
                    if size >=1 and size <= 3:
                        self.competitor_bots.append(index)

    def addKnownBot(self, index):
        if index not in self.known_bots:
            self.known_bots.append(index)


    def math_func(self,lastBid) -> int:
        last_digit = (lastBid+ self.minbid + 1)%10
        power_digit = last_digit**2
        bid = (lastBid+8) + power_digit
        return bid

    def normal_func(self,lastBid, mean, stdv) -> float:
        e = self.engine.math.e
        pi = self.engine.math.pi

        exp = -(lastBid - mean)*(lastBid - mean)/(2*stdv*stdv)
        ans = 1/(stdv*(self.engine.math.sqrt(2*pi))) * self.engine.math.pow(e,exp)
        return ans

    def get_probability(self,lastBid, mean, stdv) -> float:
        return 1 - 0.90*self.normal_func(lastBid, mean, stdv)/self.normal_func(mean, mean,stdv)


    def onMyTurn(self,lastBid):
        # lastBid is the last bid that was made
        mean = self.gameParameters["meanTrueValue"]
        stdv = self.gameParameters["stddevTrueValue"]

        #run only on first bid to identify bots
        our_bid = self.math_func(lastBid)
        if(our_bid > self.value - stdv/3):
            return

        probability = self.get_probability(our_bid, self.value, stdv)
        
        if(self.engine.random.random() < probability):
            self.engine.makeBid(our_bid)

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.print(f"Auction Ended")
        self.addRemainingCompetitors()
        self.engine.reportTeams(self.our_bots, self.competitor_bots, [])
        self.engine.print(f"Our bots are {self.our_bots} and enemy bots are {self.competitor_bots}")
        pass