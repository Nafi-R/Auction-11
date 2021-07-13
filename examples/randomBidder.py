import random
class CompetitorInstance():
    def __init__(self):
        # initialize personal variables
        pass
    
    def onGameStart(self, engine, gameParameters):
        # engine: an instance of the game engine with functions as outlined in the documentation.
        self.engine=engine
    
    def onAuctionStart(self, index, trueValue):
        self.engine.print(f"I am a random bidder at {index}")
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        pass

    def onMyTurn(self,lastBid):
        if self.engine.random.randint(0,100)<20:
            self.engine.makeBid(lastBid+40)
        pass

    def onAuctionEnd(self):
        pass