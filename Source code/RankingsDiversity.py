from SPARQLWrapper import SPARQLWrapper, JSON
import mysql.connector
import pymysql
import time
import threading
import numpy as np
import traceback
import json
import scipy.stats as stats
import math
entitiesPrefix = "http://www.wikidata.org/entity/"

def sparqlQuery(query, sparql):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = None
    try:
        results = sparql.query().convert()
    except Exception as e:
        print("Back step")
        time.sleep(10)
        error = 1
        tryNumber = 0
        while error == 1 and tryNumber < 5:
            try:
                results = sparql.query().convert()
                error = 0
            except Exception as ex:
                time.sleep(20)
            tryNumber = tryNumber + 1
        if error == 1:
            results = None
            print("TimeOut error")
    return results

def choosenRankingContains(choosenRankingList, rankingObject):
    for ranking in choosenRankingList:
        if ranking.equal(rankingObject):
            return True
    return False

class rankingCharacteristics:
    def __init__(self, Property, Class):
        self.Property = Property
        self.Class = Class

    def equal(self, rankingObject):
        #rankingObject.Class == self.Class or
        if rankingObject.Property == self.Property:
            return True
        else:
            return False

if __name__ == '__main__':
    mydb = pymysql.connect(user='root', password='hsn123', host='localhost', database='rankingindicators')
    mycursor = mydb.cursor()
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    numberOfRankings = 4
    maxNumberOfEntities = 500

    outputPath = ""

    for occupationName, OccupationCode in [("writer","Q36180"), ("university teacher","Q1622272"),("singer","Q177220"),("journalist","Q1930187"),("poet","Q49757"),("actor","Q33999"),("painter","Q1028181"),("composer","Q36834")]:
        print(occupationName+": "+OccupationCode)
        databaseQuery = """ SELECT property, class 
                    FROM results_first_method_optimized_new
                    WHERE target_entity_label = '"""+occupationName+"""' AND gini_calculation_method = 'model'
                    ORDER BY Gini_times_proportion DESC;"""
        mycursor.execute(databaseQuery)
        resultsCharacteristics = mycursor.fetchall()

        choosenRankingsCount = 0
        choosenRankings = []
        for record in resultsCharacteristics:
            rankingObject = rankingCharacteristics(record[0], record[1])
            if choosenRankingContains(choosenRankings, rankingObject):
                continue
            else:
                choosenRankingsCount += 1
                choosenRankings.append(rankingObject)
            if choosenRankingsCount > numberOfRankings:
                break

        ResultDictionary = {}
        ResultDictionary[occupationName] = {}
        ResultDictionary[occupationName]["Ranking"] = {}
        ResultDictionary[occupationName]["RankingIntersection"] = {}

        maxPerOccupation = 0
        proportionSum = 0
        kendalSum = 0
        count = 0
        count1 = 0
        maxRanking = ""
        for ranking1Index in range(len(choosenRankings)):
            for ranking2Index in range(ranking1Index+1,len(choosenRankings)):

                Query = """SELECT ?o (COUNT(DISTINCT ?s) AS ?Count)
                                    WHERE {
                                      ?o wdt:P106 wd:"""+OccupationCode+""".
                                      ?s wdt:P31 wd:"""+choosenRankings[ranking1Index].Class+""".
                                      ?s wdt:"""+choosenRankings[ranking1Index].Property+""" ?o.
                                    }
                                    GROUP BY ?o
                                    ORDER BY DESC(?Count)
                                    LIMIT """+str(maxNumberOfEntities)
                results1 = sparqlQuery(Query, sparql)

                RankingListOne = []
                for result in results1["results"]["bindings"]:
                    entityCode = result["o"]["value"][len(entitiesPrefix):]
                    RankingListOne.append(entityCode)


                ResultDictionary[occupationName]["Ranking"][str(choosenRankings[ranking1Index].Property) + ";" + str(choosenRankings[ranking1Index].Class)] = RankingListOne

                Query = """SELECT ?o (COUNT(DISTINCT ?s) AS ?Count)
                                    WHERE {
                                      ?o wdt:P106 wd:"""+OccupationCode+""".
                                      ?s wdt:P31 wd:"""+choosenRankings[ranking2Index].Class+""".
                                      ?s wdt:"""+choosenRankings[ranking2Index].Property+""" ?o.
                                    }
                                    GROUP BY ?o
                                    ORDER BY DESC(?Count)
                                    LIMIT """+str(maxNumberOfEntities)
                results2 = sparqlQuery(Query, sparql)

                RankingListTwo = []
                for result in results2["results"]["bindings"]:
                    entityCode = result["o"]["value"][len(entitiesPrefix):]
                    RankingListTwo.append(entityCode)


                #ResultDictionary[occupationName]["Ranking"][str(choosenRankings[ranking2Index].Property) + ";" + str(choosenRankings[ranking2Index].Class)] = RankingListTwo

                intersectionRankingOne = {}
                intersectionRankingTwo = {}

                kendalSet1 = []
                kendalSet2 = []

                intersectionCount = 0
                for i in range(len(RankingListOne)):
                    if RankingListTwo.__contains__(RankingListOne[i]):
                        intersectionRankingOne[str(i+1)] = RankingListOne[i]
                        intersectionRankingTwo[str(RankingListTwo.index(RankingListOne[i])+1)] = RankingListOne[i]
                        intersectionCount += 1
                        kendalSet1.append(i+1)
                        kendalSet2.append(RankingListTwo.index(RankingListOne[i])+1)

                if len(kendalSet1) != 0 and len(kendalSet2) != 0:
                    kendal, p_value = stats.kendalltau(kendalSet1, kendalSet2)
                else:
                    kendal = None

                if kendal is not None and math.isnan(kendal):
                    kendal = None



                key1 = str(choosenRankings[ranking1Index].Property) + ";" + str(choosenRankings[ranking1Index].Class) + ";" + str(choosenRankings[ranking2Index].Property) + ";" + str(choosenRankings[ranking2Index].Class)
                key2 = str(choosenRankings[ranking2Index].Property) + ";" + str(choosenRankings[ranking2Index].Class) +";"+ str(choosenRankings[ranking1Index].Property) + ";" + str(choosenRankings[ranking1Index].Class)

                if intersectionCount > maxPerOccupation:
                    maxPerOccupation = intersectionCount
                    maxRanking = key1

                ResultDictionary[occupationName]["RankingIntersection"][key1] = {}
                ResultDictionary[occupationName]["RankingIntersection"][key2] = {}
                ResultDictionary[occupationName]["RankingIntersection"][key1]["Ranks"] = intersectionRankingOne
                ResultDictionary[occupationName]["RankingIntersection"][key1]["IntersectionCount"] = intersectionCount
                ResultDictionary[occupationName]["RankingIntersection"][key1]["kendal"] = kendal
                ResultDictionary[occupationName]["RankingIntersection"][key2]["Ranks"] = intersectionRankingTwo
                ResultDictionary[occupationName]["RankingIntersection"][key2]["IntersectionCount"] = intersectionCount
                ResultDictionary[occupationName]["RankingIntersection"][key2]["kendal"] = kendal

                proportion = intersectionCount/maxNumberOfEntities
                proportionSum += proportion
                if kendal is not None:
                    kendalSum += kendal
                    count1 += 1
                count += 1


        ResultDictionary[occupationName]["MaxInfo"] = {}
        ResultDictionary[occupationName]["MaxInfo"]["MaxIntersectionCount"] = maxPerOccupation
        ResultDictionary[occupationName]["MaxInfo"]["MaxRankingCombination"] = maxRanking
        ResultDictionary[occupationName]["MaxInfo"]["proportionsSum"] = proportionSum
        ResultDictionary[occupationName]["MaxInfo"]["count"] = count
        ResultDictionary[occupationName]["MaxInfo"]["averageProportion"] = proportionSum/count
        ResultDictionary[occupationName]["MaxInfo"]["averageKendal"] = kendalSum/count1

        output_file_path = outputPath+''+str(occupationName)+'Diversity.json'
        with open(output_file_path, 'w') as json_file:
            json.dump(ResultDictionary, json_file, indent=4)
        print("Data exported to", output_file_path)