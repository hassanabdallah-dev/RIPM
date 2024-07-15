CREATE DATABASE  IF NOT EXISTS `rankingindicators` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `rankingindicators`;
-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: localhost    Database: rankingindicators
-- ------------------------------------------------------
-- Server version	8.0.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `form_kendal_teau`
--

DROP TABLE IF EXISTS `form_kendal_teau`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_kendal_teau` (
  `id` int NOT NULL AUTO_INCREMENT,
  `method` varchar(45) DEFAULT NULL,
  `profession` varchar(100) NOT NULL,
  `kendal_teau` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_kendal_teau`
--

LOCK TABLES `form_kendal_teau` WRITE;
/*!40000 ALTER TABLE `form_kendal_teau` DISABLE KEYS */;
/*!40000 ALTER TABLE `form_kendal_teau` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `results_first_method_optimized_new`
--

DROP TABLE IF EXISTS `results_first_method_optimized_new`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `results_first_method_optimized_new` (
  `id` int NOT NULL AUTO_INCREMENT,
  `target_entity_code` varchar(100) NOT NULL,
  `target_entity_type` varchar(100) DEFAULT NULL,
  `target_entity_label` varchar(200) DEFAULT NULL,
  `property` varchar(100) NOT NULL,
  `property_label` varchar(200) DEFAULT NULL,
  `class` varchar(100) NOT NULL,
  `class_label` varchar(200) DEFAULT NULL,
  `class_rank` int NOT NULL,
  `Gini` double NOT NULL,
  `proportion` float DEFAULT NULL,
  `objects_number` int DEFAULT NULL,
  `facts_number` int DEFAULT NULL,
  `Gini_times_proportion` double NOT NULL,
  `Gini_Times_proportion_times_Rank` double NOT NULL,
  `gini_calculation_method` varchar(40) DEFAULT NULL,
  `time_to_get_result` double NOT NULL,
  `sampling` tinyint DEFAULT NULL,
  `queries_number` int DEFAULT '0',
  `percentage` int DEFAULT '100',
  `queries_number_per_record` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `results_first_method_optimized_new`
--

LOCK TABLES `results_first_method_optimized_new` WRITE;
/*!40000 ALTER TABLE `results_first_method_optimized_new` DISABLE KEYS */;
/*!40000 ALTER TABLE `results_first_method_optimized_new` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `results_first_method_optimized_new_dbpedia`
--

DROP TABLE IF EXISTS `results_first_method_optimized_new_dbpedia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `results_first_method_optimized_new_dbpedia` (
  `id` int NOT NULL AUTO_INCREMENT,
  `target_entity_code` varchar(100) NOT NULL,
  `target_entity_type` varchar(100) DEFAULT NULL,
  `target_entity_label` varchar(200) DEFAULT NULL,
  `property` varchar(100) NOT NULL,
  `property_label` varchar(200) DEFAULT NULL,
  `class` varchar(100) NOT NULL,
  `class_label` varchar(200) DEFAULT NULL,
  `class_rank` int NOT NULL,
  `Gini` double NOT NULL,
  `proportion` float DEFAULT NULL,
  `objects_number` int DEFAULT NULL,
  `facts_number` int DEFAULT NULL,
  `Gini_times_proportion` double NOT NULL,
  `Gini_Times_proportion_times_Rank` double NOT NULL,
  `gini_calculation_method` varchar(40) DEFAULT NULL,
  `time_to_get_result` double NOT NULL,
  `sampling` tinyint DEFAULT NULL,
  `queries_number` int DEFAULT '0',
  `percentage` int DEFAULT '100',
  `queries_number_per_record` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_target_property_class_method` (`target_entity_code`,`property`,`class`,`gini_calculation_method`),
  KEY `classIndex` (`class`) /*!80000 INVISIBLE */,
  KEY `entityCodeIndex` (`target_entity_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `results_first_method_optimized_new_dbpedia`
--

LOCK TABLES `results_first_method_optimized_new_dbpedia` WRITE;
/*!40000 ALTER TABLE `results_first_method_optimized_new_dbpedia` DISABLE KEYS */;
/*!40000 ALTER TABLE `results_first_method_optimized_new_dbpedia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `results_first_method_optimized_new_yago`
--

DROP TABLE IF EXISTS `results_first_method_optimized_new_yago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `results_first_method_optimized_new_yago` (
  `id` int NOT NULL AUTO_INCREMENT,
  `target_entity_code` varchar(100) NOT NULL,
  `target_entity_type` varchar(100) DEFAULT NULL,
  `target_entity_label` varchar(200) DEFAULT NULL,
  `property` varchar(100) NOT NULL,
  `property_label` varchar(200) DEFAULT NULL,
  `class` varchar(100) NOT NULL,
  `class_label` varchar(200) DEFAULT NULL,
  `class_rank` int NOT NULL,
  `Gini` double NOT NULL,
  `proportion` float DEFAULT NULL,
  `objects_number` int DEFAULT NULL,
  `facts_number` int DEFAULT NULL,
  `Gini_times_proportion` double NOT NULL,
  `Gini_Times_proportion_times_Rank` double NOT NULL,
  `gini_calculation_method` varchar(40) DEFAULT NULL,
  `time_to_get_result` double NOT NULL,
  `sampling` tinyint DEFAULT NULL,
  `queries_number` int DEFAULT '0',
  `percentage` int DEFAULT '100',
  `queries_number_per_record` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `results_first_method_optimized_new_yago`
--

LOCK TABLES `results_first_method_optimized_new_yago` WRITE;
/*!40000 ALTER TABLE `results_first_method_optimized_new_yago` DISABLE KEYS */;
/*!40000 ALTER TABLE `results_first_method_optimized_new_yago` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-07-10 12:48:16
