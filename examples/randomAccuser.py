import random
class CompetitorInstance():
    def __init__(self):
        pass
    
    def onGameStart(self, engine, gameParameters):
        self.engine=engine
        self.gameParameters=gameParameters
    
    def onAuctionStart(self, index, trueValue):
        self.thisIndex = index
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        pass

    def onMyTurn(self,lastBid):
        if self.engine.random.randint(0,100)<80:
            self.engine.makeBid(lastBid+20)
        pass

    def onAuctionEnd(self):
        self.engine.print(f"==RandomAccuser [{self.thisIndex}]==")
        playerList = list(range(0,self.gameParameters["numPlayers"]))
        reportOwnTeam = random.sample(playerList,5)
        self.engine.reportTeams(reportOwnTeam, [], [])
        pass