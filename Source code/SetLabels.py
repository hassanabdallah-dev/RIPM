from SPARQLWrapper import SPARQLWrapper, JSON
import mysql.connector
import pymysql
import time
import threading
from sortedcontainers import SortedDict
def sparqlQuery(query, sparql):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = None
    try:
        results = sparql.query().convert()
    except Exception as e:
        print("Back step")
        time.sleep(15)
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


if __name__ == '__main__':
    mydb = pymysql.connect(user='root', password='hsn123', host='localhost', database='rankingindicators')
    mycursor = mydb.cursor()
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    databaseQuery = """SELECT distinct property 
                       FROM results_first_method_optimized_new;
                    """
    mycursor.execute(databaseQuery)
    resultsProperties = mycursor.fetchall()

    for property in resultsProperties:
        propertyCode = property[0]
        query = """SELECT ?label
                    WHERE {
                      wd:"""+propertyCode+""" rdfs:label ?label.
                      FILTER (LANG(?label) = "en")
                    }
                """
        results = sparqlQuery(query, sparql)
        for result in results["results"]["bindings"]:
            propertyLabel = result["label"]["value"]
            databaseQuery = """UPDATE results_first_method_optimized_new 
                                set property_label = '"""+propertyLabel+"""'
                                where property = '"""+propertyCode+"""';"""

            print(propertyCode +": "+propertyLabel)
            try:
                mycursor.execute(databaseQuery)
                mydb.commit()
            except Exception as e:
                print("Error while updating")
                continue

    databaseQuery = """SELECT distinct class 
                       FROM results_first_method_optimized_new;
                    """
    mycursor.execute(databaseQuery)
    resultsClasses = mycursor.fetchall()

    for classs in resultsClasses:
        classCode = classs[0]
        query = """SELECT ?label
                    WHERE {
                      wd:"""+classCode+""" rdfs:label ?label.
                      FILTER (LANG(?label) = "en")
                    }
                """
        results = sparqlQuery(query, sparql)
        for result in results["results"]["bindings"]:
            classLabel = result["label"]["value"]
            databaseQuery = """UPDATE results_first_method_optimized_new 
                                set class_label = '"""+classLabel+"""'
                                where class = '"""+classCode+"""';"""

            print(classCode +": "+classLabel)
            try:
                mycursor.execute(databaseQuery)
                mydb.commit()
            except Exception as e:
                print("Error while updating")
                continue

    databaseQuery = """SELECT distinct target_entity_code 
                        FROM results_first_method_optimized_new;
                        """
    mycursor.execute(databaseQuery)
    resultsClasses = mycursor.fetchall()

    for classs in resultsClasses:
        classCode = classs[0]
        query = """SELECT ?label
                        WHERE {
                          wd:""" + classCode + """ rdfs:label ?label.
                          FILTER (LANG(?label) = "en")
                        }
                    """
        results = sparqlQuery(query, sparql)
        for result in results["results"]["bindings"]:
            classLabel = result["label"]["value"]
            databaseQuery = """UPDATE results_first_method_optimized_new 
                                    set target_entity_label = '""" + classLabel + """'
                                    where target_entity_code = '""" + classCode + """';"""

            print(classCode + ": " + classLabel)
            try:
                mycursor.execute(databaseQuery)
                mydb.commit()
            except Exception as e:
                print("Error while updating")
                continue