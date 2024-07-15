from SPARQLWrapper import SPARQLWrapper, JSON
import mysql.connector
import pymysql
import time
import threading
import numpy as np
import traceback
from scipy import integrate
import matplotlib.pyplot as plt
from sortedcontainers import SortedDict
# Define variables used globally in the script
sampling = False
samplingDoNotWork = False
queryNumber = 0
percentage = 100
QueriesNumbers = {}
QueriesNumbersWithClasses = {}

lock = threading.Lock()
lock1 = threading.Lock()
lock2 = threading.Lock()
lock3 = threading.Lock()
classesMapPerProperty = {}
databaseQuery = "insert into results_first_method_optimized_new_dbpedia (target_entity_code, target_entity_type, property, class, class_rank, Gini, proportion, objects_number, facts_number, Gini_times_proportion, Gini_Times_proportion_times_Rank, gini_calculation_method, time_to_get_result, sampling, queries_number, percentage, queries_number_per_record) VALUES "
timePerOccupation = 0
time_per_thread = []
data_gini_calculation_cache = []
#####################################################
def sparqlQuery(query, sparql):
    elapsed_time_seconds = 0
    start_time = time.time()

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = None

    try:
        results = sparql.query().convert()
    except Exception as e:
        if hasattr(e, 'msg') and e.msg == "The endpoint returned the HTTP status code 500":
            return None
        if hasattr(e, 'code') and e.code == 429:
            #print("Back step")

            end_time = time.time()
            elapsed_time_seconds += end_time - start_time
            time.sleep(15)
            start_time = time.time()

            error = 1
            tryNumber = 0
            while error == 1 and tryNumber < 5:
                try:
                    results = sparql.query().convert()
                    error = 0
                except Exception as ex:
                    end_time = time.time()
                    elapsed_time_seconds += end_time - start_time
                    time.sleep(20)
                    start_time = time.time()
                tryNumber = tryNumber + 1
            if error == 1:
                results = None
                print("TimeOut error")

    end_time = time.time()
    elapsed_time_seconds += end_time - start_time
    returnResults = {
        "results": results,
        "time": elapsed_time_seconds
    }
    return returnResults

def process_property(property, ReferenceRelation, currentEntity, sparql):
    global classesMapPerProperty
    global time_per_thread
    global queryNumber

    elapsed_time_seconds = 0
    start_time = time.time()

    try:
        query = """SELECT ?class (COUNT(?s) AS ?count)
                    WHERE {
                      ?o """ + ReferenceRelation + """ <""" + currentEntity + """>.
                      ?s <""" + property + """> ?o.
                      ?s rdf:type ?class.
                    }
                    GROUP BY ?class
                    ORDER BY DESC(?count)
                    LIMIT 5
                """
        end_time = time.time()
        elapsed_time_seconds += end_time - start_time

        returnResult = sparqlQuery(query, sparql)
        resultsClasses = returnResult["results"]
        elapsed_time_seconds += returnResult["time"]
        queryNumber += 1

        if property in QueriesNumbers:
            QueriesNumbers[property] = int(QueriesNumbers[property]) + 1
        else:
            QueriesNumbers[property] = 3



        start_time = time.time()

        for resultClass in resultsClasses["results"]["bindings"]:
            wikiClass = resultClass["class"]["value"]
            with lock:
                if classesMapPerProperty.__contains__(str(property)):
                    classesMapPerProperty[str(property)].append(str(wikiClass))
                else:
                    classesMapPerProperty[str(property)] = []
                    classesMapPerProperty[str(property)].append(str(wikiClass))
        end_time = time.time()
        elapsed_time_seconds += end_time - start_time
        with lock2:
            time_per_thread.append(elapsed_time_seconds)
        return elapsed_time_seconds
    except Exception as timeout:
        end_time = time.time()
        elapsed_time_seconds += end_time - start_time
        with lock2:
            time_per_thread.append(elapsed_time_seconds)
        traceback.print_exc()
        return elapsed_time_seconds

def process_classes(property, Class, ReferenceRelation, currentEntity, sparql, rank, totalObjectsNumberPerEntity, entityTargetType, gini_calculation_method):
    global databaseQuery
    global time_per_thread
    global queryNumber

    elapsed_time_seconds = 0
    start_time = time.time()

    try:
        if gini_calculation_method == "model":
            query = """SELECT (COUNT(DISTINCT ?o) AS ?distinctObjectCount)
                        (COUNT(*) AS ?totalFactCount)
                        WHERE {
                          ?o """ + ReferenceRelation + """ <""" + currentEntity + """>.
                          ?s rdf:type <""" + Class + """>.
                          ?s <""" + property + """> ?o.
                        }
                        """

            end_time = time.time()
            elapsed_time_seconds += end_time - start_time

            returnResult = sparqlQuery(query, sparql)
            resultsRestrictedCounts = returnResult["results"]
            elapsed_time_seconds += returnResult["time"]

            queryNumber += 1
            QueriesNumbersWithClasses[property] = {}
            QueriesNumbersWithClasses[property][Class] = int(QueriesNumbers[property]) + 1


            start_time = time.time()

            FactCount = resultsRestrictedCounts["results"]["bindings"][0]["totalFactCount"]["value"]
            ObjectCount = resultsRestrictedCounts["results"]["bindings"][0]["distinctObjectCount"]["value"]

            if int(FactCount) == int(ObjectCount):
                if int(ObjectCount) >= 100 or int(FactCount) >= 100:
                    FactCount = str(int(FactCount) + 1)
                else:
                    print("continue, facts=objs")
                    print(ObjectCount + " " + FactCount + " " + currentEntity + " " + property + " " + Class)
                    return

            try:
                powerLawExponent = 1 + (1 / (1 - (int(ObjectCount) / int(FactCount))))
            except Exception as e:
                print("continue, facts=objs")
                print(ObjectCount+" "+FactCount+" "+currentEntity+" "+property+" "+Class)
                return

            GiniCoefficient = 1 / (2 * powerLawExponent - 3)
            proportion = (int(ObjectCount) / int(totalObjectsNumberPerEntity))
            GinitimesProportion = GiniCoefficient * proportion
            GinitimesProportiontimesRank = GinitimesProportion * 1/(rank+1)
        elif gini_calculation_method == "data":
            query = """SELECT ?o (COUNT(?s) AS ?count)
                       WHERE {
                          ?o """ + ReferenceRelation + """ <""" + currentEntity + """>.
                          ?s rdf:type <""" + Class + """>.
                          ?s <""" + property + """> ?o.
                       }
                       GROUP BY ?o
                       ORDER BY ASC(?count)"""
            end_time = time.time()
            elapsed_time_seconds += end_time - start_time

            returnResult = sparqlQuery(query, sparql)
            resultsRestrictedCounts = returnResult["results"]
            elapsed_time_seconds += returnResult["time"]

            queryNumber += 1
            QueriesNumbersWithClasses[property] = {}
            QueriesNumbersWithClasses[property][Class] = int(QueriesNumbers[property]) + 1

            start_time = time.time()

            i = 0
            timesSum = 0
            normalSum = 0

            ObjectCount = 0
            FactCount = 0

            for singleProperty in resultsRestrictedCounts["results"]["bindings"]:
                i += 1
                timesSum += i * int(singleProperty["count"]["value"])
                normalSum += int(singleProperty["count"]["value"])

                ObjectCount += 1
                FactCount += int(singleProperty["count"]["value"])

            GiniCoefficient = ((2 * timesSum) / (i * normalSum)) - (i + 1) / i

            #arnaud method
            # summ = 0
            # for entity in resultsRestrictedCounts["results"]["bindings"]:
            #     summ += int(entity["count"]["value"])
            # currentCumX = 0
            # currentCumY = 0
            # area = 0
            # x = 1. / len(resultsRestrictedCounts["results"]["bindings"])
            # for entity in resultsRestrictedCounts["results"]["bindings"]:
            #     y = (1. * int(entity["count"]["value"])) / summ
            #     currentCumX += x
            #     area += currentCumY * x + y * x * 0.5
            #     currentCumY += y
            #
            #     ObjectCount += 1
            #     FactCount += int(entity["count"]["value"])
            # GiniCoefficient = (0.5 - area) / 0.5
            #arnaud method
            #my method
            # GiniCoefficient = 0
            # arrayX = []
            # arrayY = []
            # summ = 0
            # for entity in resultsRestrictedCounts["results"]["bindings"]:
            #     summ += int(entity["count"]["value"])
            # currentCumX = 0
            # currentCumY = 0
            # area = 0
            # arrayX.append(currentCumX)
            # arrayY.append(currentCumY)
            # x = 1. / len(resultsRestrictedCounts["results"]["bindings"])
            # for entity in resultsRestrictedCounts["results"]["bindings"]:
            #     y = (1. * int(entity["count"]["value"])) / summ
            #     currentCumX += x
            #     currentCumY += y
            #     arrayX.append(currentCumX)
            #     arrayY.append(currentCumY)
            #
            # plt.figure(figsize=(8, 6))
            # plt.plot(arrayX, arrayY)  # , alpha=0.5
            # min_val = min(min(arrayX), min(arrayY))
            # max_val = max(max(arrayX), max(arrayY))
            # x_identity = np.linspace(min_val, max_val, 100)
            # plt.plot(x_identity, x_identity, color='black', linestyle='--', label='Equality Line')
            # plt.xscale('log')
            # plt.yscale('log')
            # plt.savefig('curves/lorenz/LorenzCurve'+str(property)+' '+str(Class)+'.pdf')
            #
            # data = np.column_stack((arrayX, arrayY))
            # np.savetxt('curves/data/{}_{}_data.txt'.format(property, Class), data,
            #            header='property: {}, class: {}'.format(property, Class))
            #
            # area = integrate.trapezoid(arrayY, arrayX)
            # GiniCoefficientMe = (0.5 - area) / 0.5
            #my method


            proportion = (int(len(resultsRestrictedCounts["results"]["bindings"])) / int(totalObjectsNumberPerEntity))
            GinitimesProportion = GiniCoefficient * proportion

            # #my method
            # trapezoidGiniTimesProportion =  GiniCoefficientMe * proportion
            # #my method

            GinitimesProportiontimesRank = GinitimesProportion * 1/(rank+1)
        # print("property code " + str(property))
        # print("Gini Coefecient" + str(GiniCoefficient))
        # print("Gini times proportion " + str(GinitimesProportion))
        # print("Class " + str(Class))
        # print("objects " + str(ObjectCount))
        # print("facts " + str(FactCount))
        # print("total profession count  " + str(totalObjectsNumberPerProfession))

        with lock1:
            # if proportion >= 0.05:
            currentEntity = currentEntity.replace("'", " ")
            entityTargetType = entityTargetType.replace("'", " ")
            property = property.replace("'", " ")
            Class = Class.replace("'", " ")

            queryCount = 0
            if gini_calculation_method == "model":
                queryCount = 4
            else:
                queryCount = 5

            databaseQuery += "('" + str(currentEntity) + "', '"+entityTargetType+"', '" + str(property) + "', '" + str(Class) + "', " + str(rank) + ", " + str(GiniCoefficient) + ","+str(proportion)+","+str(ObjectCount)+","+str(FactCount)+" ," + str(GinitimesProportion) + ", "+str(GinitimesProportiontimesRank)+",'"+gini_calculation_method+"', " + "tempNull" + ", "+str(sampling)+", "+"QueriesTempNull"+", "+str(percentage)+", "+str(queryCount)+"),"
            # if gini_calculation_method == "data":
            #     databaseQuery += "('" + str(currentEntity) + "', '"+entityTargetType+"', '" + str(property) + "', '" + str(Class) + "', " + str(rank) + ", " + str(GiniCoefficientMe) + ","+str(proportion)+","+str(ObjectCount)+","+str(FactCount)+" ," + str(trapezoidGiniTimesProportion) + ", "+str(GinitimesProportiontimesRank)+",'trapezoidGini', " + "tempNull" + "),"
        end_time = time.time()
        elapsed_time_seconds += end_time - start_time
        with lock2:
            time_per_thread.append(elapsed_time_seconds)
        return elapsed_time_seconds
    except Exception as timeout:
        end_time = time.time()
        elapsed_time_seconds += end_time - start_time
        with lock2:
            time_per_thread.append(elapsed_time_seconds)
        traceback.print_exc()
        with open("Errors.txt", "a", encoding="utf-8") as file:
            file.write(databaseQuery + "\n\n\n\n")
        return elapsed_time_seconds

def calculate_gini_based_on_data(ReferenceRelation, currentEntity, propertyCode, sparql):
    global queryNumber
    global QueriesNumbers

    elapsed_time_seconds = 0
    start_time = time.time()
    try:
        query = """SELECT ?o (COUNT(?s) AS ?count)
                     WHERE {
                       ?o """ + ReferenceRelation + """ <""" + currentEntity + """>.
                       ?s <""" + propertyCode + """> ?o.
                     }
                     GROUP BY ?o
                     ORDER BY ASC(?count)"""
        end_time = time.time()
        elapsed_time_seconds += end_time - start_time

        returnResult = sparqlQuery(query, sparql)

        resultsSingleProperty = returnResult["results"]
        elapsed_time_seconds += returnResult["time"]
        queryNumber += 1

        if propertyCode in QueriesNumbers:
            QueriesNumbers[propertyCode] = int(QueriesNumbers[propertyCode]) + 1
        else:
            QueriesNumbers[propertyCode] = 3

        start_time = time.time()

        i = 0
        timesSum = 0
        normalSum = 0
        for singleProperty in resultsSingleProperty["results"]["bindings"]:
            i += 1
            timesSum += i * int(singleProperty["count"]["value"])
            normalSum += int(singleProperty["count"]["value"])

        dataGini = ((2 * timesSum) / (i * normalSum)) - (i + 1) / i

        end_time = time.time()
        elapsed_time_seconds += end_time - start_time
        with lock3:
            data_gini_calculation_cache.append(GiniAndTime(propertyCode, dataGini, elapsed_time_seconds))
    except Exception as e:
        traceback.print_exc()
        return

class ChoosenProperties:
    def __init__(self, propertycode, GiniCoefficient):
        self.propertycode = propertycode
        self.GiniCoefficient = GiniCoefficient

class GiniAndTime:
    def __init__(self, propertyCode, gini, time):
        self.gini = gini
        self.time = time
        self.propertyCode = propertyCode

if __name__ == '__main__':
    #DataBase declarations################################################################################
    mydb = pymysql.connect(user='root', password='hsn123', host='localhost', database='rankingindicators')
    mycursor = mydb.cursor()
    # sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql = SPARQLWrapper("https://dbpedia.org/sparql", agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    #DataBase declarations###############################################################################


    for entityTargetType in ["classes"]:
        for gini_calculation_method in ["data","model"]:
            #entityTargetType = "occupations"
            #entityTargetType = "classes"
            #gini_calculation_method = "model"
            #gini_calculation_method = "data"
            # Variables initialization###########################################################################
            if entityTargetType == "occupations":
                ReferenceRelation = "dbo:occupation"
            elif entityTargetType == "classes":
                ReferenceRelation = "rdf:type"

            existed_entities = []
            list_of_entities = []
            gini_threshold_for_first_selection = 1/10
            #Variables initialization###########################################################################


            #Checking existing professions in the database for bypassing them####################################
            databaseQuery = """ SELECT distinct target_entity_code
                                FROM results_first_method_optimized_new_dbpedia
                                WHERE target_entity_type = '"""+entityTargetType+"""' and gini_calculation_method = '"""+gini_calculation_method+"""'"""
            mycursor.execute(databaseQuery)
            temp = np.array(mycursor.fetchall())
            existed_entities = temp.reshape((len(temp), 1))[:, 0]
            #Checking existing professions in the database for bypassing them####################################

            #Querying the top 100 biggest occupations###########################################################
            if entityTargetType == "occupations":
                query = """	PREFIX dbo: <http://dbpedia.org/ontology/>
                            PREFIX dbr: <http://dbpedia.org/resource/>
                            PREFIX dbp: <http://dbpedia.org/property/>

                            SELECT ?entity (COUNT(?o) AS ?count)
                            WHERE{
                              ?o """ + ReferenceRelation + """ ?entity  
                            }
                            group by ?entity
                            ORDER BY DESC(?count)
                            Limit 100"""
                returnResult = sparqlQuery(query, sparql)
                resultsEntities = returnResult["results"]

                for resultEntity in resultsEntities["results"]["bindings"]:
                    wikiEntity = resultEntity["entity"]["value"]
                    list_of_entities.append(wikiEntity)

            elif entityTargetType == "classes":
                databaseQuery = """ SELECT distinct class
                                    FROM results_first_method_optimized_new_dbpedia
                                    WHERE target_entity_type = 'occupations' and gini_calculation_method = '"""+gini_calculation_method+"""'"""
                mycursor.execute(databaseQuery)
                temp = np.array(mycursor.fetchall())
                list_of_entities = temp.reshape((temp.shape[0],))
            #Querying the top 100 biggest occupations###########################################################
            #walking with the occupation list to find good ranking properties for each occupation
            #list_of_entities = ["Q16521", "Q4164871", "Q5633421", "Q484170", "Q101352", "Q4830453", "Q215380", "Q4022", "Q13442814", "Q476028", "Q7187", "Q34442", "Q21014462", "Q43229", "Q618779", "Q27020041", "Q34770", "Q747074", "Q3918"]
            print(list_of_entities)
            for currentEntity in list_of_entities:
                try:
                    QueriesNumbers = {}
                    QueriesNumbersWithClasses = {}
                    queryNumber = 0
                    percentage = 100
                    print(str(currentEntity) + " " + str(gini_calculation_method) + " " + str(entityTargetType))
                    sampling = False
                    samplingDoNotWork = False
                    currentEntity = currentEntity.replace("'", " ")
                    #Pass already existing occupations##############################################################
                    if existed_entities.__contains__(currentEntity):
                        continue
                    #Pass already existing occupations##############################################################

                    #Re-initialize variables for each new occupation################################################
                    databaseQuery = "insert into results_first_method_optimized_new_dbpedia (target_entity_code, target_entity_type, property, class, class_rank, Gini, proportion, objects_number, facts_number, Gini_times_proportion, Gini_Times_proportion_times_Rank, gini_calculation_method, time_to_get_result, sampling, queries_number, percentage, queries_number_per_record) VALUES "
                    classesMapPerProperty = {}
                    all_GiniCoefficient_properties = []
                    #starting measure time per occupation
                    start_time = time.time()
                    timePerOccupation = 0
                    time_per_thread = []
                    data_gini_calculation_cache = []
                    #Re-initialize variables for each new occupation################################################


                    # Checking the total number of entities for an occupation to calculate the proportion later
                    query = """SELECT (COUNT(*) AS ?count)
                                WHERE {
                                  ?o """+ReferenceRelation+"""  <"""+currentEntity+""">.
                                }"""

                    end_time = time.time()
                    timePerOccupation += end_time - start_time

                    returnResult = sparqlQuery(query, sparql)
                    #here an error for Q5
                    resultsEntityObjectsNumber = returnResult["results"]
                    timePerOccupation += returnResult["time"]
                    queryNumber += 1

                    start_time = time.time()

                    totalObjectsNumberPerEntity = resultsEntityObjectsNumber["results"]["bindings"][0]["count"]["value"]
                    # Checking the total number of entities for an occupation to calculate the proportion later

                    #For each occupation, querying all possible properties of its instances, with the objects and facts number
                    #Pass properties with object or fact number less than 100
                    #Calulcate the gini coeffecient with the law exponent formula
                    #Choose the properties with a high gini coeffecient for future treatment
                    if gini_calculation_method == "model":
                        query = """SELECT ?property
                                        (COUNT(DISTINCT ?o) AS ?distinctObjectCount)
                                        (COUNT(*) AS ?totalFactCount)
                                        WHERE {
                                          ?o """+ReferenceRelation+""" <"""+currentEntity+""">.
                                          ?s ?property ?o.

                                        }
                                        GROUP BY ?property
                                """
                        end_time = time.time()
                        timePerOccupation += end_time - start_time

                        samplingError = 0
                        returnResult = sparqlQuery(query, sparql)
                        results = returnResult["results"]
                        timePerOccupation += returnResult["time"]
                        queryNumber += 1


                        start_time = time.time()

                        for result in results["results"]["bindings"]:
                            propertyCode = result["property"]["value"]
                            wikiQueryObjectsCount = result["distinctObjectCount"]["value"]
                            wikiQueryFactsCount = result["totalFactCount"]["value"]

                            # if int(wikiQueryObjectsCount) <= 100 or int(wikiQueryFactsCount) <= 100:
                            #     continue

                            if int(wikiQueryObjectsCount) == int(wikiQueryFactsCount):
                                if int(wikiQueryObjectsCount) >= 100 or int(wikiQueryFactsCount) >= 100:
                                    wikiQueryFactsCount = str(int(wikiQueryFactsCount) + 1)
                                else:
                                    print("continue, facts=objs " + str(currentEntity))
                                    print(str(wikiQueryObjectsCount) + " " + str(wikiQueryFactsCount) + " " + currentEntity + " " + propertyCode)
                                    continue

                            try:
                                powerLawExponent = 1 + (1 / (1 - (int(wikiQueryObjectsCount)/int(wikiQueryFactsCount))))
                            except Exception as e:
                                continue

                            GiniCoefficient = 1 / (2*powerLawExponent - 3)

                            #To remove in the future
                            # print("property code" + str(propertyCode))
                            # print("Gini Coefecient" + str(GiniCoefficient))
                            # print("Gini bigger than threshold" + str(GiniCoefficient >= gini_threshold_for_first_selection))

                            if GiniCoefficient >= gini_threshold_for_first_selection:
                                all_GiniCoefficient_properties.append(ChoosenProperties(propertyCode, float(GiniCoefficient)))
                    elif gini_calculation_method == "data":
                        query = """SELECT distinct ?property
                                           WHERE {
                                             ?o """+ReferenceRelation+""" <"""+currentEntity+""">.
                                             ?s ?property ?o. 

                                           }
                                           """
                        end_time = time.time()
                        timePerOccupation += end_time - start_time

                        #print(query)

                        samplingError = 0
                        returnResult = sparqlQuery(query, sparql)
                        results = returnResult["results"]
                        timePerOccupation += returnResult["time"]
                        queryNumber += 1


                        threads = []
                        data_gini_calculation_cache = []
                        for result in results["results"]["bindings"]:
                            # sparqlInstance = SPARQLWrapper("https://query.wikidata.org/sparql")
                            sparqlInstance = SPARQLWrapper("https://dbpedia.org/sparql",
                                                           agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
                            thread = threading.Thread(target=calculate_gini_based_on_data, args=(ReferenceRelation, currentEntity, result["property"]["value"], sparqlInstance))
                            thread.start()
                            threads.append(thread)
                        for thread in threads:
                            thread.join()

                        for cache in data_gini_calculation_cache:
                            timePerOccupation += cache.time
                            if cache.gini >= gini_threshold_for_first_selection:
                                all_GiniCoefficient_properties.append(ChoosenProperties(cache.propertyCode, float(cache.gini)))

                        start_time = time.time()
                    #######################################################################################################
                    #Sorting elements inside a list in descending order based on the Gini Coefficient attribute, and keeping only the first 25 properties
                    # top_25_properties = sorted(all_GiniCoefficient_properties, key=lambda x: x.GiniCoefficient, reverse=True)[:25]
                    # all_GiniCoefficient_properties = top_25_properties
                    ###############################################################################################################################
                    threads = []
                    time_per_thread = []
                    end_time = time.time()
                    timePerOccupation += end_time - start_time

                    for element in all_GiniCoefficient_properties:
                        # sparqlInstance = SPARQLWrapper("https://query.wikidata.org/sparql")
                        sparqlInstance = SPARQLWrapper("https://dbpedia.org/sparql",
                                               agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
                        thread = threading.Thread(target=process_property, args=(element.propertycode, ReferenceRelation, currentEntity, sparqlInstance))
                        thread.start()
                        threads.append(thread)
                    for thread in threads:
                        thread.join()

                    timePerOccupation += np.array(time_per_thread).max()
                    time_per_thread = []

                    threads = []
                    for property, classes in classesMapPerProperty.items():
                        for i in range(len(classes)):
                            # sparqlInstance = SPARQLWrapper("https://query.wikidata.org/sparql")
                            sparqlInstance = SPARQLWrapper("https://dbpedia.org/sparql",
                                                           agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
                            thread = threading.Thread(target=process_classes, args=(property, classes[i], ReferenceRelation, currentEntity, sparqlInstance, i, totalObjectsNumberPerEntity, entityTargetType, gini_calculation_method))
                            thread.start()
                            threads.append(thread)
                    for thread in threads:
                        thread.join()

                    timePerOccupation += np.array(time_per_thread).max()
                    time_per_thread = []

                    elapsed_time_minutes = timePerOccupation / 60
                    databaseQuery = databaseQuery.replace("tempNull", str(elapsed_time_minutes))
                    databaseQuery = databaseQuery.replace("QueriesTempNull", str(queryNumber))

                    try:
                        mycursor.execute(databaseQuery[:len(databaseQuery)-1] + ";")
                        mydb.commit()
                    except Exception as e:
                        print("Error while inserting property results")
                        with open("Errors.txt", "a", encoding="utf-8") as file:
                            file.write(databaseQuery + "\n")

                except Exception as timeout:
                    traceback.print_exc()
                    continue
