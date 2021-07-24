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
        self.bidRange = {"Low": [[],1], "Mid": [[],1], "High": [[],1]}
        self.totalTurns = 1
        self.known_bots = []
        self.firstBidder = (self.bidOrder[self.auctionNumber] + 1)%self.numPlayers
        self.prevBid = 1
        self.prevBidder = 0
        self.bidRatios = {}


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
        #self.engine.print(f"[{self.botStatus[whoMadeBid]}] [{whoMadeBid}] made a bid of {howMuch} with bid difference of: {howMuch - self.prevBid}")
        self.prevBid = howMuch
        self.prevBidder = whoMadeBid
        if(howMuch < self.mean/4):
            self.bidRange["Low"][0].append(whoMadeBid)
        elif howMuch > self.mean/4 and howMuch < self.mean*3/4:
            self.bidRange["Mid"][0].append(whoMadeBid)
        elif howMuch > self.mean*3/4:
            self.bidRange["High"][0].append(whoMadeBid)
        
    
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
                            self.value = self.engine.math.pow((bid_diff + bid_diff + 1)/2,1.45)
                    else:
                        if len(self.known_bots) >= 2:
                            self.known_bots = [self.thisIndex]
                            self.knowsValue = False
                        if index not in self.known_bots:
                            bid_diff = howMuch - self.prevBid
                            self.value = self.engine.math.pow((bid_diff + bid_diff + 1)/2,1.45)

        #Every other Turn
        else:
            if self.botStatus[index] == "NPC":
                if howMuch > self.value:
                    self.knowledgeStatus[index] = False
                if not self.is_NPC(howMuch):
                    self.botStatus[index] = "Competitor"
            elif self.botStatus[index] == "Own":
                bid_diff = howMuch - self.prevBid
                if bid_diff != self.minbid:
                    self.botStatus[index] = "NPC"



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
        bid = lastBid+ self.engine.math.floor(self.engine.math.pow(value,1/1.45))
        return bid


    def onMyTurn(self,lastBid):
        # lastBid is the last bid that was made
        mean = self.gameParameters["meanTrueValue"]
        stdv = self.gameParameters["stddevTrueValue"]
        self.totalTurns += 1
        if lastBid < mean/4:
            self.bidRange["Low"][1] += 1
        elif lastBid > mean/4 and lastBid < mean*3/4:
            self.bidRange["Mid"][1] += 1
        elif lastBid > mean*3/4:
            self.bidRange["High"][1] += 1

        if self.botBidCount[self.thisIndex] == 0:
          if lastBid < mean:
            self.engine.makeBid(self.math_func1(lastBid, self.thisIndex)) # Finds our own bots [0,1,2]
        elif self.botBidCount[self.thisIndex]== 1:
          if lastBid < mean:
              if(self.phase == "phase_1"):
                  if self.knowsValue:
                    self.engine.makeBid(self.math_func2(lastBid, self.givenValue)) # Finds true/fake value [0]
                  else: 
                    self.engine.makeBid(self.math_func2(lastBid, -1))
              else:
                  self.engine.makeBid(self.math_func2(lastBid, self.value))
        elif self.botBidCount[self.thisIndex] == 2:
          if lastBid < mean:
              if self.knowsValue:
                  self.engine.makeBid(self.math_func3(lastBid, self.value)) # if knows true, create a signal for other bots [0] bid differs = 42 -> true value = 42^2
              else: 
                  self.engine.makeBid(lastBid + self.minbid)
        else:
          	if self.botStatus[self.prevBidder] != "Own":
                    our_bid = lastBid + self.minbid
                    if our_bid < self.value and self.knowsValue == False:
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

            for index in self.botStatus.keys():
                if self.botStatus[index] == "NPC":
                    ratio = self.botBidCount[index] / self.totalTurns
                    if ratio > 0:
                        if ratio >= 0.64 or ratio <= 0.04:
                            self.bidRatios[index] = ratio
                            self.botStatus[index] = "Competitor"

            for index in range(0, self.numPlayers):
                if self.botStatus[index] == "Own":
                    continue
                countLow = self.bidRange["Low"][0].count(index)
                turnLow = self.bidRange["Low"][1]
                ratioLow = countLow/turnLow
                countMid = self.bidRange["Mid"][0].count(index)
                turnMid = self.bidRange["Mid"][1]
                ratioMid = countMid/turnMid
                countHigh = self.bidRange["High"][0].count(index)
                turnHigh = self.bidRange["High"][1]
                ratioHigh = countHigh/turnHigh

                avg = (ratioLow + ratioMid + ratioHigh)/3
                self.engine.print(f"Bot [{index}] ratios are: {ratioLow},{ratioMid},{ratioHigh}, avg: {avg}")
                threshold = (self.engine.math.ceil(0.28*self.totalTurns)/self.totalTurns)
                if avg > 0:
                    if avg > threshold:
                        self.botStatus[index] = "Competitor"

    def addRandomFakeBots(self, ourBots, competitors):
        pass
        '''
        Fake/True bot -> Report 2 rand bots
        Other bot1 -> Report our fake and 1 rand bot (with max/min prob depending on phase)
        Other bot2 -> Only report our bot
        '''
        playerNum = len(competitors)
        
        if playerNum <= 0:
            return

        #If we only have 1 competitor, only add it to known list for 1 of our bots (bot with max index)
        if(playerNum == 1):
            if self.thisIndex == max(ourBots):
                self.addKnownBot(competitors[0])
                return

        #Remove known from ourBot list
        for ourBot in ourBots:
            for known in self.known_bots:
                if ourBot == known:
                    ourBots.remove(known)

        #Phase 1 -> Bot that know the value (True)
        #Phase 2 -> Bot that doesn't the value (False)
        if(self.knowsValue == (self.phase == "phase_1")):
            #Add two random bots to known list
            if playerNum >= 2:
                self.engine.random.shuffle(competitors)
                self.addKnownBot(competitors.pop())
                self.addKnownBot(competitors.pop())
        elif self.thisIndex == max(ourBots):
            #Add 1 bot (bot with max/min prob of bidding)
            if self.phase == "phase_1":
                self.addKnownBot(min(self.bidRatios, key=(lambda x: self.bidRatios[x])))
            else:
                self.addKnownBot(max(self.bidRatios, key=(lambda x: self.bidRatios[x])))
            

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.print(f"========== Auction Ended Round [{self.auctionNumber}] ==========")
        #self.addRemainingCompetitors()
        self.findCompetitorBots()
        ourBots = self.getOurBots()
        compBots = self.getCompetitorBots()
        self.addRandomFakeBots(ourBots.copy(),compBots.copy())
        for index in self.botStatus.keys():
            ratio = self.botBidCount[index] / self.totalTurns
            self.engine.print(f"Ratio {ratio} for bot at index {index} [{self.botStatus[index]}] for {self.totalTurns} turns")

        self.engine.reportTeams(ourBots , compBots, self.known_bots)
        self.engine.print(f"[{self.thisIndex}] Our bots are {ourBots} and enemy bots are {compBots} , Known: {self.known_bots}")
        self.engine.print(f"[{self.knowsValue}] = {self.value} , {self.givenValue}")
        self.auctionNumber += 1
        pass
    