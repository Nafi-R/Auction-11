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
            self.botStatus[i] = "NPC"
        self.botBidCount = {}
        for i in range(0, self.numPlayers):
            self.botBidCount[i] = 0
        self.knowledgeStatus = {}
        for i in range(0, self.numPlayers):
            self.knowledgeStatus[i] = True
        self.totalTurns = 0
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
        if bid_diff >= self.minbid and bid_diff <= mult*self.minbid:
            return True
        else:
            return False

    def onBidMade(self, whoMadeBid, howMuch):
        self.botBidCount[whoMadeBid] += 1
        self.placeBot(whoMadeBid, howMuch)
        if whoMadeBid == self.firstBidder or whoMadeBid in self.biddersThisTurn:
            self.biddersThisTurn = set()
        self.biddersThisTurn.add(whoMadeBid)
        self.prevBid = howMuch
    
    def placeBot(self, index, howMuch):
        #OUTPUT: "Own", "Competitor", "NPC"
        # First Turn (which bots are ours)
        if self.botBidCount[index] == 1:
            if self.math_func1(self.prevBid, index) == howMuch:
                self.botStatus[index] = "Own"
            elif not self.is_NPC(howMuch):
                self.botStatus[index] = "Competitor"
        #Second Turn (which of our bots know the true value)
        elif self.botBidCount[index] == 2:
            if self.phase == "phase_1":
                if self.botStatus[index] == "Own":
                    if self.math_func2(self.prevBid, -1) != howMuch:
                        self.addKnownBot(index)
            else:
                if self.botStatus[index] == "Own":
                    if self.math_func2(self.prevBid, self.value) != howMuch:
                        self.addKnownBot(index)
                pass
        #Third Turn (get the true value and tell our other bots)
        elif self.botBidCount[index] == 3:
                if self.botStatus[index] == "Own":
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
            if self.botStatus[index] == "NPC":
                if howMuch > self.value:
                    self.knowledgeStatus[index] = False
                if not self.is_NPC(howMuch):
                    self.botStatus[index] = "Competitor"



    def getOurBots(self) -> list:
        output = []
        for i in self.botStatus.keys():
            if self.botStatus[i] == "Own":
                output.append(i)
        return output

    def getCompetitorBots(self) -> list:
        output = []
        for i in self.botStatus.keys():
            if self.botStatus[i] == "Competitor":
                output.append(i)
        return output
    

    def addKnownBot(self, index):
        if index not in self.known_bots:
            self.engine.print(f"Added to known: {index}")
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
        self.totalTurns += 1     

        if self.botBidCount[self.thisIndex] == 0:  
            our_bid = self.math_func1(lastBid, self.thisIndex) # Finds our own bots [0,1,2]
        elif self.botBidCount[self.thisIndex]== 1:
            if(self.phase == "phase_1"):
                if self.knowsValue:
                    our_bid = self.math_func2(lastBid, self.givenValue) # Finds true/fake value [0]
                else: 
                    our_bid = self.math_func2(lastBid, -1)
            else:
                our_bid = self.math_func2(lastBid, self.value)
        elif self.botBidCount[self.thisIndex] == 2:
            if self.knowsValue:
                our_bid = self.math_func3(lastBid, self.value) # if knows true, create a signal for other bots [0] bid differs = 42 -> true value = 42^2
            else: 
                our_bid = lastBid + self.minbid
        else:
            our_bid = lastBid + self.minbid

        shouldBid = True

        if self.botBidCount[self.thisIndex] >= 3:
            for ourBot in self.getOurBots():
                if ourBot in self.biddersThisTurn:
                    if ourBot != self.thisIndex:
                        shouldBid = False

        if(our_bid > self.value):
                shouldBid = False

        if shouldBid:
            self.engine.makeBid(our_bid)
        #run only on first bid to identify bots
        # probability = self.get_probability(our_bid, self.value, stdv)
        
        # if(self.engine.random.random() < probability):
    
    def isFakeBot(self):
        pass
        #if bid difference is the same -> two bots on same team that know true value

        #if bot makes bid over the true value -> fake bot
        
        #if ratio of total turns < closer to true value -> bot knows true value
       

    def findCompetitorBots(self):
        if self.totalTurns < 4:
            return
        for index in self.botStatus.keys():
            if self.botStatus[index] == "NPC":
                ratio = self.botBidCount[index] / self.totalTurns
                if ratio >= 0.64 or ratio <= 0.04:
                    self.botStatus[index] = "Competitor"

    def addRandomFakeBots(self):
        pass
        #Phase 1 : Report bots that know the true value (i.e bots that don't go over the true value)
        #Phase 2 : Report bots that know the fake value (i.e bots that do go over the true value)
        #knowLedgeStatus -> Shows whether the bot knows the true value (True), or doesnt (False)
        # filteredList = []
        # for comp in competitors:
        #     if self.knowledgeStatus[comp] == (self.phase == "phase_1"):
        #         filteredList.append(comp)

        competitors = self.getCompetitorBots()  
        if len(competitors) >= 2:
            randInt = self.engine.random.randint(0, len(competitors)- 1)
            randInt2 = self.engine.random.randint(0, len(competitors) - 1)
            while(randInt == randInt2):
                randInt2 = self.engine.random.randint(0, len(competitors) - 1)
            self.engine.print(f"Rands:{randInt}, {randInt2} Length: {len(competitors)}")
            self.addKnownBot(competitors[randInt])
            self.engine.print(f"Added to known: {competitors[randInt]}")
            self.addKnownBot(competitors[randInt2])
            self.engine.print(f"Added to known: {competitors[randInt2]}")

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.print(f"Auction Ended")
        #self.addRemainingCompetitors()
        for index in self.botStatus.keys():
            ratio = self.botBidCount[index] / self.totalTurns
            self.engine.print(f"Ratio {ratio} for bot at index {index} [{self.botStatus[index]}] for {self.totalTurns} turns")
        self.findCompetitorBots()
        self.addRandomFakeBots()
        self.engine.reportTeams(self.getOurBots() , self.getCompetitorBots(), self.known_bots)
        self.engine.print(f"[{self.thisIndex}] Our bots are {self.getOurBots()} and enemy bots are {self.getCompetitorBots()} , Known: {self.known_bots}")
        self.engine.print(f"[{self.knowsValue}] = {self.value} , {self.givenValue}")
        self.engine.print(f"Order: {self.bidOrder} , Round: {self.auctionNumber}, First Bidder: {self.firstBidder}")
        self.auctionNumber += 1
        pass
    