import random
class CompetitorInstance():
    def __init__(self):
        pass
    
    def onGameStart(self, engine, gameParameters):
        self.engine=engine
        self.gameParameters=gameParameters
    
    def onAuctionStart(self, index, trueValue):
        self.engine.print(f"I am a random accuser at {index}")
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        pass

    def onMyTurn(self,lastBid):
        if self.engine.random.randint(0,100)<20:
            self.engine.makeBid(lastBid+12)
        pass

    def onAuctionEnd(self):
        playerList = list(range(0,self.gameParameters["numPlayers"]))
        reportOwnTeam = random.sample(playerList,5)
        self.engine.reportTeams(reportOwnTeam, [], [])
        pass