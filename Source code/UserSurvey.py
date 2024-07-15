import copy
from SPARQLWrapper import SPARQLWrapper, JSON
import mysql.connector
import pymysql
import time
import threading
import numpy as np
import random as rd
import pandas as pd
import traceback
import math
import csv
import pandas as pd
import re
from sklearn.metrics import cohen_kappa_score
import scipy.stats as stats
import json

class Combinations:
    def __init__(self):
        self.p1p2 = ""
        self.p1p3 = ""
        self.p2p3 = ""
        self.p2p1 = ""
        self.p3p1 = ""
        self.p3p2 = ""


def read_excel_file(file_path):
    return pd.read_excel(file_path)

def manipulate_data(data):
    print(data.head())

def clean_string(s):
    return re.sub(r'\s+', ' ', s).strip()

def getAnswSet(set):
    comb = []
    for i in range(len(set)):
        comb.append(set[i].split(';'))
    flatList = []
    ok = 0
    while ok == 0:
        for j in range(1,len(comb)):
            if comb[0][1] == comb[j][0]:
                temp = comb[1]
                comb[1] = comb[j]
                comb[j] = temp
                ok = 1
        if ok == 0:
            combTemp = copy.deepcopy(comb)
            for i in range(len(comb)):
                comb[(i + 1) % len(comb)] = combTemp[i]

    for i in range(len(comb)):
        for j in range(len(comb[i])):
            flatList.append(comb[i][j])

    for i in range(len(flatList)):
        for j in range(i+1,len(flatList)):
            if(j >= len(flatList)):
                break
            if flatList[i] == flatList[j]:
                flatList.pop(j)
                j -= 1

    return flatList


if __name__ == "__main__":
    mydb = pymysql.connect(user='root', password='hsn123', host='localhost', database='rankingindicators')
    mycursor = mydb.cursor()

    query = "delete FROM form_kendal_teau;"
    mycursor.execute(query)

    output_file_path_TrueAnswers = 'trueAnswers.json'
    output_file_path_groundTruth = 'groundTruth.json'

    input_file_path = """Automatic Discovery of Ranking Indicators.xlsx"""

    excel_data = read_excel_file(input_file_path)

    necessary_data = excel_data.iloc[:,6:14]
    columns = necessary_data.columns.tolist()

    ranking = dict()
    combination_dict = dict()
    flag = 0

    for i in range(len(columns)):
        profession = re.search(r'\"(.*?)\"', columns[i]).group(1)
        flag = 0
        answers = necessary_data.iloc[:,i].tolist()

        for j in range(len(answers)):

            question_answers = answers[j].split(';')
            list_answers = question_answers[0:len(question_answers)-1]
            list_answers = [answer.strip() for answer in list_answers]

            ranking.setdefault(str(profession), {})
            ranking[str(profession)].setdefault("user:"+str(j), {})


            ranking[profession]["user:"+str(j)]["answers"] = []
            ranking[profession]["user:"+str(j)]["sortedAnswers"] = copy.deepcopy(list_answers)


            temp_list_answers = copy.deepcopy(list_answers)
            temp_list_answers.pop(2)
            ranking[profession]["user:"+str(j)]["answers"].append(';'.join(temp_list_answers))

            temp_list_answers = copy.deepcopy(list_answers)
            temp_list_answers.pop(1)
            ranking[profession]["user:"+str(j)]["answers"].append(';'.join(temp_list_answers))

            temp_list_answers = copy.deepcopy(list_answers)
            temp_list_answers.pop(0)
            ranking[profession]["user:"+str(j)]["answers"].append(';'.join(temp_list_answers))

            if flag == 0:
                comb = Combinations()

                temp_list_answers = copy.deepcopy(list_answers)
                temp_list_answers.pop(2)
                comb.p1p2 = ';'.join(temp_list_answers)

                temp_list_answers = copy.deepcopy(list_answers)
                temp_list_answers.pop(1)
                comb.p1p3 = ';'.join(temp_list_answers)

                temp_list_answers = copy.deepcopy(list_answers)
                temp_list_answers.pop(0)
                comb.p2p3 = ';'.join(temp_list_answers)

                temp_list_answers = copy.deepcopy(list_answers)
                temp_list_answers.pop(2)
                comb.p2p1 = ';'.join(temp_list_answers[::-1])

                temp_list_answers = copy.deepcopy(list_answers)
                temp_list_answers.pop(1)
                comb.p3p1 = ';'.join(temp_list_answers[::-1])

                temp_list_answers = copy.deepcopy(list_answers)
                temp_list_answers.pop(0)
                comb.p3p2 = ';'.join(temp_list_answers[::-1])

                combination_dict[profession] = {}
                combination_dict[profession]["Combinations"] = comb

                combination_dict[profession]["p1p2"] = 0
                combination_dict[profession]["p1p3"] = 0
                combination_dict[profession]["p2p3"] = 0
                combination_dict[profession]["p2p1"] = 0
                combination_dict[profession]["p3p1"] = 0
                combination_dict[profession]["p3p2"] = 0

                flag = 1

    cohenSum=0
    total = 0

    cohenSumPerProfession=0
    totalPerProfession = 0

    for profession, users in ranking.items():

        cohenSumPerProfession = 0
        totalPerProfession = 0

        comClass = combination_dict[profession]["Combinations"]

        for i in range(len(users)):

            y1 = []
            set1 = ranking[profession]["user:" + str(i)]["answers"]
            user1SortedAnswers = ranking[profession]["user:" + str(i)]["sortedAnswers"]
            kendalSet1 = [1, 2, 3]

            if set1.__contains__(comClass.p1p2):
                y1.append(1)
                combination_dict[profession]["p1p2"] += 1
            else:
                y1.append(0)

            if set1.__contains__(comClass.p1p3):
                y1.append(1)
                combination_dict[profession]["p1p3"] += 1
            else:
                y1.append(0)

            if set1.__contains__(comClass.p2p3):
                y1.append(1)
                combination_dict[profession]["p2p3"] += 1
            else:
                y1.append(0)

            if set1.__contains__(comClass.p2p1):
                y1.append(1)
                combination_dict[profession]["p2p1"] += 1
            else:
                y1.append(0)

            if set1.__contains__(comClass.p3p1):
                y1.append(1)
                combination_dict[profession]["p3p1"] += 1
            else:
                y1.append(0)

            if set1.__contains__(comClass.p3p2):
                y1.append(1)
                combination_dict[profession]["p3p2"] += 1
            else:
                y1.append(0)

            startIndex = (i+1)%len(users)
            if startIndex == 0:
                continue
            stopIndex = len(users)

            for j in range(startIndex,stopIndex):
              y2=[]
              set2 = ranking[profession]["user:"+str(j)]["answers"]
              user2SortedAnswers = ranking[profession]["user:"+str(j)]["sortedAnswers"]
              kendalSet2 = [user2SortedAnswers.index(user1SortedAnswers[0])+1,user2SortedAnswers.index(user1SortedAnswers[1])+1,user2SortedAnswers.index(user1SortedAnswers[2])+1]


              if set2.__contains__(comClass.p1p2):
                  y2.append(1)
              else:
                  y2.append(0)

              if set2.__contains__(comClass.p1p3):
                  y2.append(1)
              else:
                  y2.append(0)

              if set2.__contains__(comClass.p2p3):
                  y2.append(1)
              else:
                  y2.append(0)

              if set2.__contains__(comClass.p2p1):
                  y2.append(1)
              else:
                  y2.append(0)

              if set2.__contains__(comClass.p3p1):
                  y2.append(1)
              else:
                  y2.append(0)

              if set2.__contains__(comClass.p3p2):
                  y2.append(1)
              else:
                  y2.append(0)

              cohen =  cohen_kappa_score(y1,y2)
              kendal, p_value = stats.kendalltau(kendalSet1, kendalSet2)
              if abs(cohen - kendal) > 10**-8:
                  print('')
              print(profession)
              print("user: "+ str(i+1) + "_" + str(j+1))
              print(y1)
              print(y2)
              print("cohen="+str(cohen))
              print("kendal="+str(kendal))
              print("-------------------------------------------------------------------------------------------")
              cohenSum+= cohen
              total += 1

              cohenSumPerProfession+= cohen
              totalPerProfession += 1

        averagePerProfession = cohenSumPerProfession / totalPerProfession
        query = """insert 
                    into  form_kendal_teau (method, profession, kendal_teau) 
                    VALUES ('betweenUsers','"""+str(profession)+"""',"""+str(averagePerProfession)+""");"""
        mycursor.execute(query)
        mydb.commit()

        print("-------------------------------------------------------------------------------------------")
        print("-------------------------------------------------------------------------------------------")
        print("average cohen total for:" + str(profession) + " = " + str(averagePerProfession))
        print("-------------------------------------------------------------------------------------------")
        print("-------------------------------------------------------------------------------------------")
    # total = len(necessary_data.iloc[:, i].tolist())*(len(necessary_data.iloc[:, i].tolist()))
    average = cohenSum/total
    query = """insert 
                into  form_kendal_teau (method,profession, kendal_teau) 
                VALUES ('betweenUsers','All',""" + str(average) + """);"""
    mycursor.execute(query)
    mydb.commit()
    print("-------------------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------------------")
    print("average cohen total:" + str(average))
    print("-------------------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------------------")
    groundTruth = {}
    for profession, value in combination_dict.items():
        combCounts = copy.deepcopy(value)
        combCounts.pop("Combinations")

        sortedCount = sorted(combCounts.items(), key= lambda x : x[1], reverse = True)
        sortedCount = sortedCount[:3]

        groundTruth[profession] = []

        if sortedCount[0][0] == "p1p2":
            groundTruth[profession].append(value["Combinations"].p1p2)
        elif sortedCount[0][0] == "p1p3":
            groundTruth[profession].append(value["Combinations"].p1p3)
        elif sortedCount[0][0] == "p2p3":
            groundTruth[profession].append(value["Combinations"].p2p3)
        elif sortedCount[0][0] == "p2p1":
            groundTruth[profession].append(value["Combinations"].p2p1)
        elif sortedCount[0][0] == "p3p1":
            groundTruth[profession].append(value["Combinations"].p3p1)
        elif sortedCount[0][0] == "p3p2":
            groundTruth[profession].append(value["Combinations"].p3p2)

        if sortedCount[1][0] == "p1p2":
            groundTruth[profession].append(value["Combinations"].p1p2)
        elif sortedCount[1][0] == "p1p3":
            groundTruth[profession].append(value["Combinations"].p1p3)
        elif sortedCount[1][0] == "p2p3":
            groundTruth[profession].append(value["Combinations"].p2p3)
        elif sortedCount[1][0] == "p2p1":
            groundTruth[profession].append(value["Combinations"].p2p1)
        elif sortedCount[1][0] == "p3p1":
            groundTruth[profession].append(value["Combinations"].p3p1)
        elif sortedCount[1][0] == "p3p2":
            groundTruth[profession].append(value["Combinations"].p3p2)

        if sortedCount[2][0] == "p1p2":
            groundTruth[profession].append(value["Combinations"].p1p2)
        elif sortedCount[2][0] == "p1p3":
            groundTruth[profession].append(value["Combinations"].p1p3)
        elif sortedCount[2][0] == "p2p3":
            groundTruth[profession].append(value["Combinations"].p2p3)
        elif sortedCount[2][0] == "p2p1":
            groundTruth[profession].append(value["Combinations"].p2p1)
        elif sortedCount[2][0] == "p3p1":
            groundTruth[profession].append(value["Combinations"].p3p1)
        elif sortedCount[2][0] == "p3p2":
            groundTruth[profession].append(value["Combinations"].p3p2)

    print("------------------------------------------------------------------------------------------------------------")

    ourMethodRanking = {
        'writer': ["versions, editions, or translations authored;events where she/he served as an exhibited creator","versions, editions, or translations authored;television series presented","events where she/he served as an exhibited creator;television series presented"],
        'university teacher': ["humans advised by her/him as a doctoral advisor;written works for which she/he served as a thesis committee member","humans advised by her/him as a doctoral advisor;the number of awards named after her/him","written works for which she/he served as a thesis committee member;the number of awards named after her/him"],
        'singer': ["albums performed by her/him;music tracks with vocals produced by her/him","albums performed by her/him;eurovision Song Contest entries featuring her/him as a contributor to a creative work or subject","music tracks with vocals produced by her/him;eurovision Song Contest entries featuring her/him as a contributor to a creative work or subject"],
        'journalist': ["versions, editions, or translations authored her/him;events where she/he served as an exhibited creator","versions, editions, or translations authored her/him;prints depicting her/him","events where she/he served as an exhibited creator;prints depicting her/him"],
        'poet': ["literary works authored by her/him;singles performed by her/him","literary works authored by her/him;television films for which she/he served as a screenwriter","singles performed by her/him;television films for which she/he served as a screenwriter"],
        'actor': ["films in which she/he served as a cast member;musical works or compositions with lyrics by her/him","films in which she/he served as a cast member;singles composed by her/him","musical works or compositions with lyrics by her/him;singles composed by her/him"],
        'painter': ["paintings created by her/him;prints created after a work by her/him","paintings created by her/him;art museums named after her/him","prints created after a work by her/him;art museums named after her/him"],
        'composer': ["musical works or compositions composed by her/him;Christian hymns with lyrics written by her/him","musical works or compositions composed by her/him;obituaries featuring a composer as the main subject","Christian hymns with lyrics written by her/him;obituaries featuring a composer as the main subject"],
    }

    # giniMethodRanking = {
    #     'writer': ["events where she/he served as an exhibited creator;versions, editions, or translations authored", "versions, editions, or translations authored;television series presented","events where she/he served as an exhibited creator;television series presented"],
    #     'university teacher': ["humans advised by her/him as a doctoral advisor;written works for which she/he served as a thesis committee member","humans advised by her/him as a doctoral advisor;the number of awards named after her/him","written works for which she/he served as a thesis committee member;the number of awards named after her/him"],
    #     'singer': ["albums performed by her/him;music tracks with vocals produced by her/him","albums performed by her/him;eurovision Song Contest entries featuring her/him as a contributor to a creative work or subject","music tracks with vocals produced by her/him;eurovision Song Contest entries featuring her/him as a contributor to a creative work or subject"],
    #     'journalist': ["versions, editions, or translations authored her/him;events where she/he served as an exhibited creator","versions, editions, or translations authored her/him;prints depicting her/him","events where she/he served as an exhibited creator;prints depicting her/him"],
    #     'poet': ["singles performed by her/him;literary works authored by her/him","literary works authored by her/him;television films for which she/he served as a screenwriter","singles performed by her/him;television films for which she/he served as a screenwriter"],
    #     'actor': ["films in which she/he served as a cast member;musical works or compositions with lyrics by her/him","films in which she/he served as a cast member;singles composed by her/him","musical works or compositions with lyrics by her/him;singles composed by her/him"],
    #     'painter': ["prints created after a work by her/him;paintings created by her/him","paintings created by her/him;art museums named after her/him","prints created after a work by her/him;art museums named after her/him"],
    #     'composer': ["musical works or compositions composed by her/him;Christian hymns with lyrics written by her/him","musical works or compositions composed by her/him;obituaries featuring a composer as the main subject","Christian hymns with lyrics written by her/him;obituaries featuring a composer as the main subject"],
    # }
    #
    # proportionMethodRanking = {
    #     'writer': ["versions, editions, or translations authored;events where she/he served as an exhibited creator","versions, editions, or translations authored;television series presented","events where she/he served as an exhibited creator;television series presented"],
    #     'university teacher': ["humans advised by her/him as a doctoral advisor;written works for which she/he served as a thesis committee member","humans advised by her/him as a doctoral advisor;the number of awards named after her/him","the number of awards named after her/him;written works for which she/he served as a thesis committee member"],
    #     'singer': ["albums performed by her/him;music tracks with vocals produced by her/him","albums performed by her/him;eurovision Song Contest entries featuring her/him as a contributor to a creative work or subject","music tracks with vocals produced by her/him;eurovision Song Contest entries featuring her/him as a contributor to a creative work or subject"],
    #     'journalist': ["versions, editions, or translations authored her/him;events where she/he served as an exhibited creator","versions, editions, or translations authored her/him;prints depicting her/him","events where she/he served as an exhibited creator;prints depicting her/him"],
    #     'poet': ["literary works authored by her/him;singles performed by her/him","literary works authored by her/him;television films for which she/he served as a screenwriter","singles performed by her/him;television films for which she/he served as a screenwriter"],
    #     'actor': ["films in which she/he served as a cast member;musical works or compositions with lyrics by her/him","films in which she/he served as a cast member;singles composed by her/him","musical works or compositions with lyrics by her/him;singles composed by her/him"],
    #     'painter': ["paintings created by her/him;prints created after a work by her/him","paintings created by her/him;art museums named after her/him","prints created after a work by her/him;art museums named after her/him"],
    #     'composer': ["musical works or compositions composed by her/him;Christian hymns with lyrics written by her/him","musical works or compositions composed by her/him;obituaries featuring a composer as the main subject","obituaries featuring a composer as the main subject;Christian hymns with lyrics written by her/him"],
    # }

    normalTotalCohen = 0
    giniTotalCohen = 0
    proportionTotalCohen = 0

    for profession, results in ourMethodRanking.items():

        # if profession == "university teacher":
        #     print('')

        comClass = combination_dict[profession]["Combinations"]
        kendalSet1 = [1, 2, 3]

        set1OurMethod = ourMethodRanking[profession]
        ansSetOneOurMethod = getAnswSet(set1OurMethod)

        #set1Gini = giniMethodRanking[profession]
        #ansSetOneGini = getAnswSet(set1Gini)

        #set1Proportion = proportionMethodRanking[profession]
        #ansSetOneProportion = getAnswSet(set1Proportion)


        set2GroundTruth = groundTruth[profession]
        ansSetTwoGroundTruth = getAnswSet(set2GroundTruth)
        temp = []
        for s in ansSetTwoGroundTruth:
            temp.append(clean_string(s))
        ansSetTwoGroundTruth = temp

        kendalSet2 = [ansSetTwoGroundTruth.index(clean_string(ansSetOneOurMethod[0]))+1, ansSetTwoGroundTruth.index(clean_string(ansSetOneOurMethod[1]))+1, ansSetTwoGroundTruth.index(clean_string(ansSetOneOurMethod[2]))+1]
        #kendalSet2Gini = [ansSetTwoGroundTruth.index(clean_string(ansSetOneGini[0]))+1, ansSetTwoGroundTruth.index(clean_string(ansSetOneGini[1]))+1, ansSetTwoGroundTruth.index(clean_string(ansSetOneGini[2]))+1]
        #kendalSet2Proportion = [ansSetTwoGroundTruth.index(clean_string(ansSetOneProportion[0]))+1, ansSetTwoGroundTruth.index(clean_string(ansSetOneProportion[1]))+1, ansSetTwoGroundTruth.index(clean_string(ansSetOneProportion[2]))+1]

        y1OurMethod = []
        y2OurMethod = []

        y1Gini = []
        y2Gini = []

        y1Proportion = []
        y2Proportion = []


        for message, set1, y1, set2, y2, kendalset  in [('gini*prop', set1OurMethod, y1OurMethod, set2GroundTruth, y2OurMethod, kendalSet2)]:#, ('gini', set1Gini, y1Gini, set2GroundTruth, y2Gini, kendalSet2Gini), ('prop', set1Proportion, y1Proportion, set2GroundTruth, y2Proportion, kendalSet2Proportion)]:

            if set1.__contains__(clean_string(comClass.p1p2)):
                y1.append(1)
            else:
                y1.append(0)

            if set1.__contains__(clean_string(comClass.p1p3)):
                y1.append(1)
            else:
                y1.append(0)

            if set1.__contains__(clean_string(comClass.p2p3)):
                y1.append(1)
            else:
                y1.append(0)

            if set1.__contains__(clean_string(comClass.p2p1)):
                y1.append(1)
            else:
                y1.append(0)

            if set1.__contains__(clean_string(comClass.p3p1)):
                y1.append(1)
            else:
                y1.append(0)

            if set1.__contains__(clean_string(comClass.p3p2)):
                y1.append(1)
            else:
                y1.append(0)
        #-------------------------------------------------------------------------------
        #-------------------------------------------------------------------------------
        #-------------------------------------------------------------------------------
            if set2.__contains__(comClass.p1p2):
                y2.append(1)
            else:
                y2.append(0)

            if set2.__contains__(comClass.p1p3):
                y2.append(1)
            else:
                y2.append(0)

            if set2.__contains__(comClass.p2p3):
                y2.append(1)
            else:
                y2.append(0)

            if set2.__contains__(comClass.p2p1):
                y2.append(1)
            else:
                y2.append(0)

            if set2.__contains__(comClass.p3p1):
                y2.append(1)
            else:
                y2.append(0)

            if set2.__contains__(comClass.p3p2):
                y2.append(1)
            else:
                y2.append(0)
            print(message)

            cohen = cohen_kappa_score(y1, y2)
            kendal, p_value = stats.kendalltau(kendalSet1, kendalset)


            if abs(cohen - kendal) > 0:
                print('')

            if message == 'gini*prop':
                normalTotalCohen += cohen
            elif message == 'gini':
                giniTotalCohen += cohen
            else:
                proportionTotalCohen += cohen


            print("profession:"+str(profession)+" \ncohen: "+ str(cohen))
            print("kendal: "+ str(kendal))

            query = """insert 
                        into  form_kendal_teau (method, profession, kendal_teau) 
                        VALUES ('"""+str(message)+"""','groundTruth-"""+str(profession)+"""',""" + str(cohen) + """);"""
            mycursor.execute(query)
            mydb.commit()

    cohenAverage = normalTotalCohen/8
    print("Cohen Average: "+ str(cohenAverage))
    query = """insert 
                into  form_kendal_teau (method, profession, kendal_teau) 
                VALUES ('gini*prop','groundTruth-All',""" + str(cohenAverage) + """);"""
    mycursor.execute(query)
    mydb.commit()

    # cohenAverage = giniTotalCohen/8
    # print("Cohen Average: "+ str(cohenAverage))
    # query = """insert
    #             into  form_kendal_teau (method, profession, kendal_teau)
    #             VALUES ('gini','groundTruth-All',""" + str(cohenAverage) + """);"""
    # mycursor.execute(query)
    # mydb.commit()
    #
    # cohenAverage = proportionTotalCohen/8
    # print("Cohen Average: "+ str(cohenAverage))
    # query = """insert
    #             into  form_kendal_teau (method, profession, kendal_teau)
    #             VALUES ('prop','groundTruth-All',""" + str(cohenAverage) + """);"""
    # mycursor.execute(query)
    # mydb.commit()





    with open(output_file_path_groundTruth, 'w') as json_file:
        json.dump(groundTruth, json_file, indent=4)

    print("Data exported to", output_file_path_groundTruth)



    with open(output_file_path_TrueAnswers, 'w') as json_file:
        json.dump(ourMethodRanking, json_file, indent=4)

    print("Data exported to", output_file_path_TrueAnswers)