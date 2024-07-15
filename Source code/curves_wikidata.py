from SPARQLWrapper import SPARQLWrapper, JSON
import mysql.connector
import pymysql
import time
import numpy as np
import threading
from sortedcontainers import SortedDict
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4), sharey=False)
    mydb = pymysql.connect(user='root', password='hsn123', host='localhost', database='rankingindicators')
    mycursor = mydb.cursor()
    type = 'occupations'

    databaseQuery = """
                    SELECT model.target_entity_code, model.time_to_get_result * 60 as modelTime, datav.time_to_get_result * 60 as dataTime
                    FROM
                    (SELECT distinct target_entity_code, target_entity_type, gini_calculation_method, time_to_get_result
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "model") model,
                    (SELECT distinct target_entity_code,target_entity_type, gini_calculation_method, time_to_get_result
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "data") datav
                    WHERE model.target_entity_code = datav.target_entity_code
                    AND model.target_entity_type = 'classes';
                    """

    mycursor.execute(databaseQuery)
    results = mycursor.fetchall()
    col = [des[0] for des in mycursor.description]
    df = pd.DataFrame(results, columns=col)

    distinctEntities = np.array(df.iloc[:,0])
    modelValues = np.array(df.iloc[:,1])
    dataValues = np.array(df.iloc[:,2])

    ax2.scatter(modelValues, dataValues, color='Red', alpha=0.7)#, alpha=0.5

    databaseQuery = """
                    SELECT model.target_entity_code, model.time_to_get_result * 60 as modelTime, datav.time_to_get_result * 60 as dataTime
                    FROM
                    (SELECT distinct target_entity_code, target_entity_type, gini_calculation_method, time_to_get_result
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "model") model,
                    (SELECT distinct target_entity_code,target_entity_type, gini_calculation_method, time_to_get_result
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "data") datav
                    WHERE model.target_entity_code = datav.target_entity_code
                    AND model.target_entity_type = 'occupations';
                    """

    mycursor.execute(databaseQuery)
    results = mycursor.fetchall()
    col = [des[0] for des in mycursor.description]
    df = pd.DataFrame(results, columns=col)

    distinctEntities = np.array(df.iloc[:,0])
    modelValues = np.array(df.iloc[:,1])
    dataValues = np.array(df.iloc[:,2])

    ax2.scatter(modelValues, dataValues, color='Blue', alpha=0.6)#, alpha=0.5

    databaseQuery = """
                    SELECT model.target_entity_code, model.time_to_get_result * 60 as modelTime, datav.time_to_get_result * 60 as dataTime
                    FROM
                    (SELECT distinct target_entity_code, target_entity_type, gini_calculation_method, time_to_get_result
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "model") model,
                    (SELECT distinct target_entity_code,target_entity_type, gini_calculation_method, time_to_get_result
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "data") datav
                    WHERE model.target_entity_code = datav.target_entity_code;
                    """

    mycursor.execute(databaseQuery)
    results = mycursor.fetchall()
    col = [des[0] for des in mycursor.description]
    df = pd.DataFrame(results, columns=col)

    distinctEntities = np.array(df.iloc[:,0])
    modelValues = np.array(df.iloc[:,1])
    dataValues = np.array(df.iloc[:,2])


    ax2.plot([min(min(modelValues), min(dataValues)), max(max(modelValues), max(dataValues))],
             [min(min(modelValues), min(dataValues)), max(max(modelValues), max(dataValues))],
             color='black', linestyle='--', linewidth=3)
    # plt.title('dataBasedGiniTime vs modelBasedGiniTime')
    ax2.set_xlabel('Gini approximation (seconds)')
    ax2.set_ylabel('Gini (seconds)')
    ax2.set_title('(b) Gini coefficient computation time (seconds)', fontsize=14)
    ax2.set_xscale('log')
    ax2.set_yscale('log')

    legend_handles = [
        plt.Line2D([0], [0], marker='o', color='Blue', markersize=5, linestyle='', alpha=0.6, label='Occupations'),
        plt.Line2D([0], [0], marker='o', color='Red', markersize=5, linestyle='', alpha=0.6, label='Classes')
    ]

    ax2.legend(handles=legend_handles)

    ax2.grid(True)


    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################


    databaseQuery = """
            SELECT model.target_entity_code, model.property, model.class, model.Gini as modelGini, datav.Gini as dataGini, (model.objects_number/model.facts_number) as modelRapport, (datav.objects_number/datav.facts_number) as dataRapport
            FROM
            
            (SELECT target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number
            FROM results_first_method_optimized_new
            WHERE   gini_calculation_method = "model"
            and objects_number >= 500
            GROUP BY target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number) model,
            
            (SELECT target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number
            FROM results_first_method_optimized_new
            WHERE   gini_calculation_method = "data"
            and objects_number >= 500
            GROUP BY target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number) datav
            
            WHERE model.target_entity_code = datav.target_entity_code
            AND model.property = datav.property
            AND model.class = datav.class
            AND model.target_entity_type = 'occupations';
    """
    mycursor.execute(databaseQuery)
    results = mycursor.fetchall()
    col = [des[0] for des in mycursor.description]
    df = pd.DataFrame(results, columns=col)

    modelValues = np.array(df.iloc[:, 3])
    dataValues = np.array(df.iloc[:, 4])

    ax1.scatter(modelValues, dataValues, color='Blue', label="Occupations", alpha=0.6)

    databaseQuery = """
            SELECT model.target_entity_code, model.property, model.class, model.Gini as modelGini, datav.Gini as dataGini, (model.objects_number/model.facts_number) as modelRapport, (datav.objects_number/datav.facts_number) as dataRapport
            FROM

            (SELECT target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number
            FROM results_first_method_optimized_new
            WHERE   gini_calculation_method = "model"
            and objects_number > 500
            GROUP BY target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number) model,

            (SELECT target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number
            FROM results_first_method_optimized_new
            WHERE   gini_calculation_method = "data"
            and objects_number > 500
            GROUP BY target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number) datav

            WHERE model.target_entity_code = datav.target_entity_code
            AND model.property = datav.property
            AND model.class = datav.class
            AND model.target_entity_type = 'classes';
    """
    mycursor.execute(databaseQuery)
    results = mycursor.fetchall()
    col = [des[0] for des in mycursor.description]
    df = pd.DataFrame(results, columns=col)

    modelValues = np.array(df.iloc[:, 3])
    dataValues = np.array(df.iloc[:, 4])

    ax1.scatter(modelValues, dataValues, color='Red', label="Classes", alpha=0.5)

    ax1.grid(True)

    databaseQuery = """
            SELECT model.target_entity_code, model.property, model.class, model.Gini as modelGini, datav.Gini as dataGini, (model.objects_number/model.facts_number) as modelRapport, (datav.objects_number/datav.facts_number) as dataRapport
            FROM

            (SELECT target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number
            FROM results_first_method_optimized_new
            WHERE   gini_calculation_method = "model"
            and objects_number > 500
            GROUP BY target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number) model,

            (SELECT target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number
            FROM results_first_method_optimized_new
            WHERE   gini_calculation_method = "data"
            and objects_number > 500
            GROUP BY target_entity_code, target_entity_type, property, class, Gini, objects_number, facts_number) datav

            WHERE model.target_entity_code = datav.target_entity_code
            AND model.property = datav.property
            AND model.class = datav.class;
    """
    mycursor.execute(databaseQuery)
    results = mycursor.fetchall()
    col = [des[0] for des in mycursor.description]
    df = pd.DataFrame(results, columns=col)

    modelValues = np.array(df.iloc[:, 3])
    dataValues = np.array(df.iloc[:, 4])

    mae = np.mean(np.abs(dataValues - modelValues))
    mse = np.mean((dataValues - modelValues) ** 2)
    print("mae " + str(mae))
    print("mse " + str(mse))

    ax1.plot([min(min(modelValues), min(dataValues)), max(max(modelValues), max(dataValues))],
             [min(min(modelValues), min(dataValues)), max(max(modelValues), max(dataValues))],
             color='black', linestyle='--', linewidth=3)
    # plt.title('dataBasedGiniTime vs modelBasedGiniTime')
    ax1.set_xlabel('Gini approximation')
    ax1.set_ylabel('Gini')
    ax1.set_title('(a) Gini coefficient values', fontsize=14)
    # plt.xscale('log')
    # plt.yscale('log')
    # Saving the second plot as a .png file in the 'curves' directory
    plt.tight_layout()

    # legend_handles = [
    #     plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='$n_o/n_f > 0.7$'),
    #     plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10,
    #            label='$0.2 \leq n_o/n_f \leq 0.7$'),
    #     plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='$n_o/n_f < 0.2$'),
    # ]

    legend_handles = [
        plt.Line2D([0], [0], marker='o', color='Blue', markersize=5, linestyle='', alpha=0.6, label='Occupations'),
        plt.Line2D([0], [0], marker='o', color='Red', markersize=5, linestyle='', alpha=0.6, label='Classes')
    ]

    ax1.legend(handles=legend_handles)

    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################
    ##################################################################################################################################################
    databaseQuery = """
                    SELECT model.target_entity_code, model.queries_number as modelQueries, datav.queries_number as dataQueries
                    FROM
                    (SELECT distinct target_entity_code, target_entity_type, gini_calculation_method, queries_number
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "model") model,
                    (SELECT distinct target_entity_code,target_entity_type, gini_calculation_method, queries_number
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "data") datav
                    WHERE model.target_entity_code = datav.target_entity_code
                    AND model.target_entity_type = 'classes';
                    """

    mycursor.execute(databaseQuery)
    results = mycursor.fetchall()
    col = [des[0] for des in mycursor.description]
    df = pd.DataFrame(results, columns=col)

    distinctEntities = np.array(df.iloc[:,0])
    modelValues = np.array(df.iloc[:,1])
    dataValues = np.array(df.iloc[:,2])


    ax3.scatter(modelValues, dataValues, color='Red', alpha=0.7)#, alpha=0.5

    databaseQuery = """
                    SELECT model.target_entity_code, model.queries_number as modelQueries, datav.queries_number as dataQueries
                    FROM
                    (SELECT distinct target_entity_code, target_entity_type, gini_calculation_method, queries_number
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "model") model,
                    (SELECT distinct target_entity_code,target_entity_type, gini_calculation_method, queries_number
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "data") datav
                    WHERE model.target_entity_code = datav.target_entity_code
                    AND model.target_entity_type = 'occupations';
                    """

    mycursor.execute(databaseQuery)
    results = mycursor.fetchall()
    col = [des[0] for des in mycursor.description]
    df = pd.DataFrame(results, columns=col)

    distinctEntities = np.array(df.iloc[:,0])
    modelValues = np.array(df.iloc[:,1])
    dataValues = np.array(df.iloc[:,2])

    ax3.scatter(modelValues, dataValues, color='Blue', alpha=0.6)#, alpha=0.5

    databaseQuery = """
                    SELECT model.target_entity_code, model.queries_number as modelQueries, datav.queries_number as dataQueries
                    FROM
                    (SELECT distinct target_entity_code, target_entity_type, gini_calculation_method, queries_number
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "model") model,
                    (SELECT distinct target_entity_code,target_entity_type, gini_calculation_method, queries_number
                    FROM results_first_method_optimized_new
                    WHERE  gini_calculation_method = "data") datav
                    WHERE model.target_entity_code = datav.target_entity_code;
                    """

    mycursor.execute(databaseQuery)
    results = mycursor.fetchall()
    col = [des[0] for des in mycursor.description]
    df = pd.DataFrame(results, columns=col)

    distinctEntities = np.array(df.iloc[:,0])
    modelValues = np.array(df.iloc[:,1])
    dataValues = np.array(df.iloc[:,2])


    ax3.plot([min(min(modelValues), min(dataValues)), max(max(modelValues), max(dataValues))],
             [min(min(modelValues), min(dataValues)), max(max(modelValues), max(dataValues))],
             color='black', linestyle='--', linewidth=3)
    # plt.title('dataBasedGiniTime vs modelBasedGiniTime')
    ax3.set_xlabel('Gini approximation (#Queries)')
    ax3.set_ylabel('Gini (#Queries)')
    ax3.set_title('(c) Queries\' number', fontsize=14)
    ax3.set_xscale('log')
    ax3.set_yscale('log')

    legend_handles = [
        plt.Line2D([0], [0], marker='o', color='Blue', markersize=5, linestyle='', alpha=0.6, label='Occupations'),
        plt.Line2D([0], [0], marker='o', color='Red', markersize=5, linestyle='', alpha=0.6, label='Classes')
    ]

    ax3.legend(handles=legend_handles)

    ax3.grid(True)
    fig.suptitle('Experimentation made on Wikidata', fontsize=16)
    fig.subplots_adjust(top=0.8)  # Adjust the value as needed
    plt.savefig('curves/new_gini_combined_wikidata.pdf')
    plt.close()