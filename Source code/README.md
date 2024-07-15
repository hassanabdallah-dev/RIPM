# Ranking Indicator Discovery from Knowledge Graphs

## Steps to Run and Test Our Approach:

1. **Setup Materials:**
   - Download and install MySQL: [MySQL Downloads](https://www.mysql.com/downloads/)
   - Download the MySQL dump named 'Ranking-Indicators-Necessary-Tables'. Then, run it. This action will create the necessary database and tables to proceed.
   - Download and install PyCharm or any other Python IDE: [PyCharm Download](https://www.jetbrains.com/pycharm/download/)
   - Import and install the 'mysql.connector' package in your Python environment and edit the MySQL user and password along with the target schema in every python file.

2. **Automatically Discovering Counting Graph Patterns:**
   - Run the files named 'RIPM_(wikidata|yago|dbpedia).py'. This will discover and extract counting graph patterns for occupations and classes, inserting them into the database.
   - Run the file named 'SetLabels.py'. This will retrieve and insert the labels of all existing URIs into the database (for wikidata).
   - Run the file named 'curves_(wikidata|yago|dbpedia).py'. This will export the curves related to the Gini coefficient in PDF format.

3. **Users study:**
   - The file named 'Automatic Discovery of Ranking Indicators' contains the annotations we received in our form from 19 raters. You can access the form via this link: [Form Link](https://forms.office.com/e/26v4bWGJry).
   - Run the file named 'UserSurvey'. This will read the annotations of the raters, compute the Kendall Tau between users, extract the ground truth, and compute the Kendall Tau between the ground truth and the results of RIPM. All statistics will then be inserted into the database, and two JSON files are exported: one containing the ground truth and the other containing the results of RIPM.

4. **Rankings Diversity:**
   - Run the file named 'RankingsDiversity.py'. This will use the generated counting graph patterns already in the database after 'RIPM.py' finishes. It will then use them to rank entities of Wikidata, exporting a JSON file for each occupation containing statistics showing the diversity.
