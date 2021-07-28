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
        self.auctionNumber = 0

    
    def onAuctionStart(self, index, trueValue):
        # index is the current player's index, that usually stays put from game to game
        # trueValue is -1 if this bot doesn't know the true value 
        # if we know the true value, let others bid.
        # If within certain range, allow us to buy
        self.engine.print(f"Our Bot index is {index} and knows value: {trueValue != -1} , {trueValue}")
        self.phase = self.gameParameters["phase"]
        self.bidOrder = self.gameParameters["bidOrder"]
        self.mean = self.gameParameters["meanTrueValue"]
        self.numPlayers = self.gameParameters["numPlayers"]
        self.thisIndex = index
        self.givenValue = trueValue
        self.value = trueValue
        self.knowsValue = True if trueValue != -1 else False
        # index : [status, bidCount]
        self.botStatus = {}
        for i in range(0, self.numPlayers):
            self.botStatus[i] = ["NPC", 0]
        self.our_bots = []
        self.other_bots = []
        self.competitor_bots = []
        self.known_bots = []
        self.has_made_first_bid = []
        self.biddersThisTurn = set()
        self.firstBidder = (self.bidOrder[self.auctionNumber] + 1)%self.numPlayers
        self.our_lastBid = 0
        self.prevBid = 1
        self.should_bid = True
        self.hasBid = False
        self.hasSecondBid = False
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
        self.botStatus[whoMadeBid][1] += 1
        self.placeBot(whoMadeBid, howMuch)
        if whoMadeBid == self.firstBidder:
            self.biddersThisTurn = set()
        self.biddersThisTurn.add(whoMadeBid)
        self.prevBid = howMuch
    
    def placeBot(self, index, howMuch):
        #OUTPUT: "Own", "Competitor", "NPC"
        # First Turn (which bots are ours)
        if self.botStatus[index][1] == 1:
            if self.math_func1(self.prevBid, index) == howMuch:
                self.botStatus[index][0] = "Own"
            elif not self.is_NPC(howMuch):
                self.botStatus[index][0] = "Competitor"
        #Second Turn (which of our bots know the true value)
        elif self.botStatus[index][1] == 2:
            if self.phase == "phase_1":
                if self.botStatus[index][0] == "Own":
                    if self.math_func2(self.prevBid, -1) != howMuch:
                        self.addKnownBot(index)
            else:
                if self.botStatus[index][0] == "Own":
                    if self.math_func2(self.prevBid, self.value) != howMuch:
                        self.addKnownBot(index)
                pass
        #Third Turn (get the true value and tell our other bots)
        elif self.botStatus[index][1] == 3:
                if self.botStatus[index][0] == "Own":
                    if self.phase == "phase_1":
                        if index in self.known_bots:
                            bid_diff = howMuch - self.prevBid
                            self.value = bid_diff**2
                    else:
                        if len(self.known_bots) >= 2:
                            self.known_bots = [self.thisIndex]
                        if index not in self.known_bots:
                            bid_diff = howMuch - self.prevBid
                            self.value = bid_diff**2

        #Every other Turn
        else:
            if self.botStatus[index][0] == "NPC":
                if not self.is_NPC(howMuch):
                    self.botStatus[index][0] = "Competitor"



    def getOurBots(self) -> list:
        output = []
        for i in self.botStatus.keys():
            if self.botStatus[i][0] == "Own":
                output.append(i)
        return output

    def getCompetitorBots(self) -> list:
        output = []
        for i in self.botStatus.keys():
            if self.botStatus[i][0] == "Competitor":
                output.append(i)
        return output


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


    #Bots that our ours do this function on the first bet
    def math_func1(self,lastBid, index) -> int:
        num = hash((lastBid,index))%100
        bid = (lastBid+self.minbid) + num
        return bid

    #Bots that know the true/fake value do thos in the second bet
    def math_func2(self,lastBid, knownValue) -> int:
        num = hash((lastBid, knownValue))%100    
        bid = (lastBid+self.minbid) + num
        return bid

    #Creates signal for other bots to find the true value (bid increase = sqrt(trueValue))
    def math_func3(self,lastBid, value) -> int:
        bid = lastBid+ self.engine.math.floor(self.engine.math.sqrt(value))
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

        # if self.phase == "phase_1":
        #     if self.knowsValue:
        #         our_bid = self.math_func1(lastBid)
        #     else:
        #         our_bid = self.math_func2(lastBid)
        # else:
        #     if self.hasBid == False:
        #         our_bid = self.math_func3(lastBid)
        #         self.hasBid = True
        #     else:
        #         our_bid = self.math_func2(lastBid)       

        if self.botStatus[self.thisIndex][1] == 0:  
            our_bid = self.math_func1(lastBid, self.thisIndex) # Finds our own bots [0,1,2]
        elif self.botStatus[self.thisIndex][1] == 1:
            if(self.phase == "phase_1"):
                if self.knowsValue:
                    our_bid = self.math_func2(lastBid, self.givenValue) # Finds true/fake value [0]
                else: 
                    our_bid = self.math_func2(lastBid, -1)
            else:
                our_bid = self.math_func2(lastBid, self.value)
        elif self.botStatus[self.thisIndex][1] == 2:
            if self.knowsValue:
                our_bid = self.math_func3(lastBid, self.value) # if knows true, create a signal for other bots [0] bid differs = 42 -> true value = 42^2
            else: 
                our_bid = lastBid + self.minbid + self.engine.random.randint(0,10)
        else:
            our_bid = lastBid + self.minbid + self.engine.random.randint(0,10)

        # if our bots have not bid
        #    bid
        # reset our biddersThisTurn list
        # = set()

        

        shouldBid = True

        if self.botStatus[self.thisIndex][1] >= 3:
            for ourBot in self.getOurBots():
                if ourBot in self.biddersThisTurn:
                    if ourBot < self.thisIndex:
                        shouldBid = False

        if(our_bid > self.value):
                shouldBid = False

        if shouldBid:
            self.engine.makeBid(our_bid)
        #run only on first bid to identify bots
        # probability = self.get_probability(our_bid, self.value, stdv)
        
        # if(self.engine.random.random() < probability):
        

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.print(f"Auction Ended")
        #self.addRemainingCompetitors()
        if len(self.getCompetitorBots()) >= 2:
            getRandomCompetitor = self.getCompetitorBots()
            getListIndex = self.engine.random.randint(0, len(getRandomCompetitor))
            self.engine.print(f"Known bot index added at {getListIndex}")
            self.known_bots.append(getRandomCompetitor[getListIndex])
            getRandomCompetitor.remove(getRandomCompetitor[getListIndex])
            getListIndex = self.engine.random.randint(0, len(getRandomCompetitor))
            self.engine.print(f"Known bot index added at {getListIndex}")
            self.known_bots.append(getRandomCompetitor[getListIndex])
        self.engine.reportTeams(self.getOurBots() , self.getCompetitorBots(), self.known_bots)
        self.engine.print(f"[{self.thisIndex}] Our bots are {self.getOurBots()} and enemy bots are {self.getCompetitorBots()} , Known: {self.known_bots}")
        self.engine.print(f"[{self.knowsValue}] = {self.value} , {self.givenValue}")
        self.engine.print(f"Order: {self.bidOrder}")
        self.auctionNumber += 1
        pass