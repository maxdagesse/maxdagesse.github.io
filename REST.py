#!/usr/bin/python
import json
from bson import json_util
from bson.json_util import dumps
import bottle
from bottle import route, run, request, abort
#imports for database
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection['market']
collection = db['stocks']


#Update
@route('/update/<TickerValue>', method='PUT')
def UpdateMyStock(TickerValue):
  jsondata = request.json #Retrieve all data passed in url
  query = { "Ticker" : TickerValue} #Query used to search for documents to update
 
  #Update collection with parameters from command
  for key in jsondata:
    update =  { "$set":{key:jsondata[key]}}
    #updating collection
    collection.update(query,update)
  updateDocs = collection.find({"Ticker":TickerValue}) #Locate documents with appropriate TickerValue
  line = "--" * 50 +"\n" #This will print a line
  result = dumps(updateDocs) #
  return line+"\n   Updated Values:  \n"+str(result)+" \n "+line


#Add
#Without Ticker
@route('/addDocument', method='POST')
def addDocumentStock():
  #get all passed data in a json object using the request.json
  jsonData = request.json
  #insert the document passed to the collection
  newDocument = collection.insert(jsonData) #returns the _id
  retriveDoc = collection.find_one({"_id":newDocument})
  line = "--" * 45 +"\n"
  return line+ "\nAdded: \n "+dumps(retriveDoc)+" \n "+line #return inserted document.

#With Ticker
@route('/addDocument/<tickerValue>', method='POST')
def addDocumentStock(tickerValue):
  #get all passed dat in a json object using the request.json
  jsonData = request.json
  jsonData.update( {'Ticker' : tickerValue} ) 
  #Lets insert the document passed to the collection
  recordId = collection.insert(jsonData) #insert data to the stocks collection
  retriveDoc = collection.find_one({"_id":recordId})
  line = "--" * 50 +"\n"
  return line+ "\nAdded: \n "+dumps(retriveDoc)+" \n "+line #return inserted document.



#Remove
@route('/remove/<TickerValue>', method='GET')
def removeStock(TickerValue):
  query = {"Ticker" :TickerValue} #Searches for matching Ticker values
  result = collection.delete_many(query) #Deletes all documents that match the query
  return "\n Document Removed \n" #return results to the user


#Request Doc
#No Search Term
@route('/search', method='GET')
def requestDocument():
  readDocument = collection.find().limit(1) #Find first document in collection
  #provided
  line = "--" * 50 +"\n"
  return line+" \n "+dumps(readDocument)

#Search By Ticker
@route('/searchTicker/<TickerValue>', method='GET')
def requestDocument(TickerValue):
  readDocument = collection.find({"Ticker":TickerValue}) #Find all documents with appropriate TickerValue
  #provided
  line = "--" * 50 +"\n"
  return line+"\nSearch Criteria [Ticker Value]: \n "+dumps(readDocument)

#Search By Sector
@route('/searchSector/<SectorValue>', method='GET')
def requestDocument(SectorValue):
  readDocument = collection.find({"Sector":SectorValue}) #Find all documents with appropriate SectorValue
  #provided
  line = "--" * 50 +"\n"
  return line+"\nSearch Criteria [Sector]: \n "+dumps(readDocument)

#Search By Industry
@route('/searchIndustry/<IndustryValue>', method='GET')
def requestDocument(IndustryValue):
  readDocument = collection.find({"Industry":IndustryValue}) #Find all documents with appropriate IndustryValue
  #provided
  line = "--" * 50 +"\n"
  return line+"\nSearch Criteria [Industry]: \n "+dumps(readDocument)


#Stock Summary
@route('/stockSummary', method='POST')
def getReport(): 
  line = "--" * 50 +"\n"
  tickerSymbols = request.json.get('list') #retrieves the value of the list key in the url data
  #Removing the curl Braces from the List 
  tickerSymbols = tickerSymbols.replace("[","")
  tickerSymbols = tickerSymbols.replace("]","")
  tickerSymbols = list(tickerSymbols.split(","))
  EmptyTickers = list()
  print(tickerSymbols)
  underline = "_" * 30;
  #This for loop uses each ticker in the list,
  #gets the summary and adds it to the items list
  for ticker in tickerSymbols:
      item = Pipeline(ticker)
      print(item)
      #Building string for display
      EmptyTickers.append(line+" \t\t\t Report for Ticker ["+ticker+"]  \n \t\t\t"+underline+" \n"+item+"\n\n "+line)
  return EmptyTickers  #return a list of items


#Get Industry Report
#Most URLs replace spaces with +, so for any industry with spaces in the name, we replace spaces with + signs
@route('/getIndustryReport/<industryName>', method='GET')
def getReport(industryName):
  industry = industryName.replace("+"," ") 
  #Stage 1
  print("\n\n\n "+industry+"\n\n")
  result2 = IndustryPipeline(industry)
  firstStage = { '$project': {'Industry':1, 'Ticker':1,'Float Short':1,'Relative Volume':1,'Volume':1,'Performance (Year)':1 } }
  #Stage 2
  secondStage = { '$match': { "Industry": industry } }
  print("\n\n\n "+str(secondStage)+"\n\n")
  #Stage 3
  thirdStage = { '$group': { '_id': "$Industry", 'Total Float Short': {'$sum': "$Float Short" },
                           'Average Relative Volume':{'$avg':"$Relative Volume"},
                           'Average Volume':{'$avg':'$Volume'},
                           'Maximum Performance (Year)':{'$max':'$Performance (Year)'},
			   'Minimum Performance (Year)':{'$min':'$Performance (Year)'},
			   'Maximum Volume':{'$max':'$Volume'},
			   'Minimum Volume':{'$min':'$Volume'},
                           'Total Volume':{'$sum':'$Volume'} } }
  #Stage 4, adding limit
  fourthStage = { '$limit' : 5 }
  query = [firstStage,secondStage,thirdStage,fourthStage]
  print(str(query))
  result=collection.aggregate(query)
  result = dumps(result)
  #print results to user
  return "-------- \n \t\t\t Portfolio Report For "+industry+" Industries \n\n "+result+" \n-------- \n"+result2+"\n"

#Get Sector Report
#Most URLs replace spaces with +, so for any sector with spaces in the name, we replace spaces with + signs
@route('/getSectorReport/<sectorName>', method='GET')
def getReport(sectorName):
  sector = sectorName.replace("+"," ") 
  #Stage 1
  print("\n\n\n "+sector+"\n\n")
  result2 = SectorPipeline(sector)
  firstStage = { '$project': {'Sector':1, 'Ticker':1,'Float Short':1,'Relative Volume':1,'Volume':1,'Performance (Year)':1 } }
  #Stage 2
  secondStage = { '$match': { "Sector": sector } }
  print("\n\n\n "+str(secondStage)+"\n\n")
  #Stage 3
  thirdStage = { '$group': { '_id': "$Sector", 'Total Float Short': {'$sum': "$Float Short" },
                           'Average Relative Volume':{'$avg':"$Relative Volume"},
                           'Average Volume':{'$avg':'$Volume'},
                           'Maximum Performance (Year)':{'$max':'$Performance (Year)'},
			   'Minimum Performance (Year)':{'$min':'$Performance (Year)'},
			   'Maximum Volume':{'$max':'$Volume'},
			   'Minimum Volume':{'$min':'$Volume'},
                           'Total Volume':{'$sum':'$Volume'} } }
  #Stage 4, adding limit
  fourthStage = { '$limit' : 5 }
  query = [firstStage,secondStage,thirdStage,fourthStage]
  print(str(query))
  result=collection.aggregate(query)
  result = dumps(result)
  #print results to user
  return "-------- \n \t\t\t Portfolio Report For "+sector+" Sector \n\n "+result+" \n-------- \n"+result2+"\n"

#Pipeline

def Pipeline(ticker):
  firstStage = { '$project': { 'Ticker':1,'Float Short':1,'Relative Volume':1,'Volume':1,'Performance (Year)':1,'Profit Margin':1 } }
  secondStage = { '$match': { "Ticker": ticker } }
  thirdStage = { '$group': { '_id': "$Ticker", 'Total Float Short': {'$sum': "$Float Short" },
                           'Average Relative Volume':{'$avg':"$Relative Volume"},
			   'Average Volume':{'$avg':'$Volume'},
			   'Maximum Volume':{'$max':'$Volume'},
			   'Minimum Volume':{'$min':'$Volume'},
                           'Total Volume':{'$sum':'$Volume'},
			   'Minimum Performance (Year)':{'$min':'$Performance (Year)'},
                           'Maximum Performance (Year)':{'$max':'$Performance (Year)'},
                           'Minimum Volume Used':{'$min':'$Volume'},
			   'Maximum Volume Used':{'$max':'$Volume'},
			   'Average Profit Margin':{'$avg':'$Profit Margin'} } }
  myQuery = [firstStage,secondStage,thirdStage]
  result=collection.aggregate(myQuery) 
  result = dumps(result)
  return result



def IndustryPipeline(industry):
  firstStage = { '$project': { 'Industry':1,'Float Short':1,'Price':1,'Average True Range':1,'50-Day Simple Moving Average':1,'Change':1,'Profit Margin':1 } }
  secondStage = { '$match': { "Industry": industry } }
  thirdStage = { '$group': { '_id': "$Industry", 'Total Float Short': {'$sum': "$Float Short" },
                           'Average Average True Range':{'$avg':"$Average True Range"},
                           'Total Price':{'$sum':'$Price'},
                           'Average Price':{'$avg':'$Price'},
			   'Minimum Price':{'$min':'$Price'},
			   'Maximum Price':{'$max':'$Price'},
			   'Average 50-Day Simple Moving Average (Year)':{'$avg':'$50-Day Simple Moving Average'},
			   'Minimum 50-Day Simple Moving Average (Year)':{'$min':'$50-Day Simple Moving Average'},
                           'Maximum 50-Day Simple Moving Average (Year)':{'$max':'$50-Day Simple Moving Average'},
			   'Average Change':{'$avg':'$Change'},
                           'Minimum Change':{'$min':'$Change'},
			   'Maximum Change':{'$max':'$Change'},
			   'Average Profit Margin':{'$avg':'$Profit Margin'} } }
  fourthStage = { '$limit' : 5 }
  myQuery = [firstStage,secondStage,thirdStage,fourthStage]
  result=collection.aggregate(myQuery) 
  result = dumps(result)
  return "-------- \n More Information: \n"+result+"\n"

def SectorPipeline(sector):
  firstStage = { '$project': { 'Sector':1,'Float Short':1,'Price':1,'Average True Range':1,'50-Day Simple Moving Average':1,'Change':1,'Profit Margin':1 } }
  secondStage = { '$match': { "Sector": sector } }
  thirdStage = { '$group': { '_id': "$Sector", 'Total Float Short': {'$sum': "$Float Short" },
                           'Average Average True Range':{'$avg':"$Average True Range"},
                           'Total Price':{'$sum':'$Price'},
                           'Average Price':{'$avg':'$Price'},
			   'Minimum Price':{'$min':'$Price'},
			   'Maximum Price':{'$max':'$Price'},
			   'Average 50-Day Simple Moving Average (Year)':{'$avg':'$50-Day Simple Moving Average'},
			   'Minimum 50-Day Simple Moving Average (Year)':{'$min':'$50-Day Simple Moving Average'},
                           'Maximum 50-Day Simple Moving Average (Year)':{'$max':'$50-Day Simple Moving Average'},
			   'Average Change':{'$avg':'$Change'},
                           'Minimum Change':{'$min':'$Change'},
			   'Maximum Change':{'$max':'$Change'},
			   'Average Profit Margin':{'$avg':'$Profit Margin'} } }
  fourthStage = { '$limit' : 5 }
  myQuery = [firstStage,secondStage,thirdStage,fourthStage]
  result=collection.aggregate(myQuery) 
  result = dumps(result)
  return "-------- \n More Information: \n"+result+"\n"

#Main program
  
if __name__ == '__main__':
  run(debug=True,reloader = True)
  #run(host='localhost', port=8080)