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
        self.engine.print(f"Our Bot index is {index} and knows value: {trueValue != -1} , {trueValue}")
        self.phase = self.gameParameters["phase"]
        self.bidOrder = self.gameParameters["bidOrder"]
        self.thisIndex = index
        self.value = trueValue if trueValue != -1 else self.gameParameters["meanTrueValue"]
        self.knowsValue = True if trueValue != -1 else False
        self.our_bots = []
        self.other_bots = []
        self.competitor_bots = []
        self.known_bots = []
        self.has_made_first_bid = []
        self.knowsTrue = []
        self.our_lastBid = 0
        self.prevBid = 1
        self.should_bid = True
        self.hasBid = False
        self.bid_diff = {}
        for i in range(0,self.gameParameters["numPlayers"]):
            self.bid_diff[i] = set()


    def is_NPC(self, currentBid) -> bool:
        bid_diff = currentBid - self.prevBid
        mult = 3 if self.phase == "phase_1" else 30
        if bid_diff < mult*self.minbid:
            return True
        else:
            return False

    def onBidMade(self, whoMadeBid, howMuch):
        self.placeBot(whoMadeBid, howMuch)
        self.prevBid = howMuch
    
    def placeBot(self, index, howMuch):
        #OUTPUT: "Own", "Competitor", "NPC"
        if self.phase == "phase_1":
            if self.math_func1(self.prevBid) == howMuch:
                if index not in self.other_bots:
                    self.addOwnBot(index)
                    if index not in self.known_bots:
                        self.known_bots.append(index)
                    return
            elif self.math_func2(self.prevBid) == howMuch:
                if index not in self.other_bots:
                    self.addOwnBot(index)
                    return
            else:
                if index not in self.other_bots:
                    self.other_bots.append(index)
                if self.isCompetitor(index,howMuch) == True:
                    self.addCompetitor(index)
        else:
            if index not in self.has_made_first_bid:
                if self.math_func3(self.prevBid) == howMuch:
                    self.knowsTrue.append(index)
                self.has_made_first_bid.append(index)
            else:
                if self.math_func2(self.prevBid) == howMuch:
                    if index not in self.other_bots:
                        self.addOwnBot(index)
                else:
                    if index not in self.other_bots:
                        self.other_bots.append(index)
                    if self.isCompetitor(index,howMuch) == True:
                        self.addCompetitor(index)
            pass
           

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


    def math_func1(self,lastBid) -> int:
        last_digit = (lastBid+ self.minbid + 1)%10
        power_digit = last_digit**2
        bid = (lastBid+8) + power_digit
        return bid

    def math_func2(self,lastBid) -> int:
        last_digit = (lastBid+ self.minbid + 5)%10
        power_digit = last_digit**2 + 1
        bid = (lastBid+8) + power_digit
        return bid

    def math_func3(self,lastBid) -> int:
        last_digit = (lastBid + self.value)%10
        power_digit = last_digit**3 + 1
        bid = (lastBid+8) + power_digit
        return bid


    def normal_func(self,lastBid, mean, stdv) -> float:
        e = self.engine.math.e
        pi = self.engine.math.pi

        exp = -(lastBid - mean)*(lastBid - mean)/(2*stdv*stdv)
        ans = 1/(stdv*(self.engine.math.sqrt(2*pi))) * self.engine.math.pow(e,exp)
        return ans

    def get_probability(self,lastBid, mean, stdv) -> float:
        return 1 - 0.75*self.normal_func(lastBid, mean, stdv)/self.normal_func(mean, mean,stdv)


    def onMyTurn(self,lastBid):
        # lastBid is the last bid that was made
        mean = self.gameParameters["meanTrueValue"]
        stdv = self.gameParameters["stddevTrueValue"]

        if self.phase == "phase_1":
            if self.knowsValue:
                our_bid = self.math_func1(lastBid)
            else:
                our_bid = self.math_func2(lastBid)
        else:
            if self.hasBid == False:
                our_bid = self.math_func3(lastBid)
                self.hasBid = True
            else:
                our_bid = self.math_func2(lastBid)       

        if(our_bid > self.value*0.95):
                return

        #run only on first bid to identify bots
        probability = self.get_probability(our_bid, self.value, stdv)
        
        if(self.engine.random.random() < probability):
            self.engine.makeBid(our_bid)

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.print(f"Auction Ended")
        #self.addRemainingCompetitors()
        if self.phase == "phase_2":
            fakeBots = []
            for i in self.our_bots:
                if i not in self.knowsTrue:
                    fakeBots.append(i)
            self.engine.reportTeams(self.our_bots, self.competitor_bots, fakeBots)
            self.engine.print(f"Our bots are {self.our_bots} and enemy bots are {self.competitor_bots} , Known: {fakeBots}")  
            self.engine.print(f"Bid order: {self.bidOrder}")      
        else:
            self.engine.reportTeams(self.our_bots, self.competitor_bots, self.known_bots)
            self.engine.print(f"Our bots are {self.our_bots} and enemy bots are {self.competitor_bots} , Known: {self.known_bots}")
        pass