-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: wardrobe_python
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `brand`
--

DROP TABLE IF EXISTS `brand`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brand` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brand`
--

LOCK TABLES `brand` WRITE;
/*!40000 ALTER TABLE `brand` DISABLE KEYS */;
INSERT INTO `brand` VALUES (1,'Allen Solly','2026-10-06 10:14:56'),(2,'H&M','2026-10-06 10:14:56'),(3,'Levi\'s','2026-10-06 10:14:56'),(4,'Nike','2026-10-06 10:14:56'),(5,'Adidas','2026-10-06 10:14:56'),(6,'Uniqlo','2026-10-06 10:14:56'),(7,'Woodland','2026-10-06 10:14:56');
/*!40000 ALTER TABLE `brand` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `wear_limit` int NOT NULL,
  `sort_order` int NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES (1,'Topwear','topwear',3,1,'2026-10-06 10:14:56'),(2,'Bottomwear','bottomwear',3,2,'2026-10-06 10:14:56'),(3,'Footwear','footwear',5,3,'2026-10-06 10:14:56'),(4,'Outerwear','outerwear',5,4,'2026-10-06 10:14:56'),(5,'Accessories','accessories',5,5,'2026-10-06 10:14:56');
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clothingitem`
--

DROP TABLE IF EXISTS `clothingitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clothingitem` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `category_id` int NOT NULL,
  `brand_id` int DEFAULT NULL,
  `season_id` int DEFAULT NULL,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `formality_score` int NOT NULL,
  `purchase_price` decimal(10,2) NOT NULL,
  `last_washed_at` date DEFAULT NULL,
  `sent_to_laundry_at` date DEFAULT NULL,
  `image_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `ix_clothingitem_user_category` (`user_id`,`category_id`),
  KEY `ix_clothingitem_user_season` (`user_id`,`season_id`),
  KEY `ix_clothingitem_user_brand` (`user_id`,`brand_id`),
  KEY `fk_clothingitem_brand` (`brand_id`),
  KEY `fk_clothingitem_season` (`season_id`),
  CONSTRAINT `clothingitem_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `clothingitem_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `clothingitem_ibfk_3` FOREIGN KEY (`brand_id`) REFERENCES `brand` (`id`) ON DELETE SET NULL,
  CONSTRAINT `clothingitem_ibfk_4` FOREIGN KEY (`season_id`) REFERENCES `season` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_clothingitem_brand` FOREIGN KEY (`brand_id`) REFERENCES `brand` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_clothingitem_season` FOREIGN KEY (`season_id`) REFERENCES `season` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clothingitem`
--

LOCK TABLES `clothingitem` WRITE;
/*!40000 ALTER TABLE `clothingitem` DISABLE KEYS */;
INSERT INTO `clothingitem` VALUES (1,1,1,1,4,'Navy Oxford Shirt','Navy',4,2400.00,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(2,1,1,2,1,'White Crew Tee','White',1,800.00,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(3,1,1,6,2,'Charcoal Sweater','Charcoal',3,1600.00,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(4,1,1,4,1,'Light Blue Polo','Blue',2,1200.00,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(5,1,2,1,4,'Black Chinos','Black',3,1800.00,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(6,1,2,2,4,'Beige Chinos','Beige',3,1800.00,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(7,1,2,3,1,'Blue Jeans','Blue',1,1500.00,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(8,1,3,4,1,'White Sneakers','White',1,3200.00,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(9,1,3,7,2,'Brown Leather Shoes','Brown',5,4200.00,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(10,1,3,5,2,'Black Boots','Black',3,3600.00,NULL,'2026-10-06',NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(11,2,1,2,1,'Maroon Oversized Tee','Maroon',1,900.00,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(12,2,2,7,3,'Olive Cargo Pants','Olive',2,2100.00,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(13,2,3,5,4,'Grey Running Shoes','Grey',1,2800.00,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56'),(14,2,4,6,2,'Khaki Bomber Jacket','Khaki',3,3400.00,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56','2026-10-06 10:14:56');
/*!40000 ALTER TABLE `clothingitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `colorcompatibility`
--

DROP TABLE IF EXISTS `colorcompatibility`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `colorcompatibility` (
  `id` int NOT NULL AUTO_INCREMENT,
  `color1` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color2` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `score` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_color_pair` (`color1`,`color2`),
  KEY `ix_colorcompat_color2` (`color2`)
) ENGINE=InnoDB AUTO_INCREMENT=191 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `colorcompatibility`
--

LOCK TABLES `colorcompatibility` WRITE;
/*!40000 ALTER TABLE `colorcompatibility` DISABLE KEYS */;
INSERT INTO `colorcompatibility` VALUES (1,'Black','Black',9),(2,'Black','White',8),(3,'Black','Grey',8),(4,'Black','Charcoal',8),(5,'Black','Navy',8),(6,'Beige','Black',8),(7,'Black','Khaki',8),(8,'Black','Brown',8),(9,'Black','Red',8),(10,'Black','Maroon',8),(11,'Black','Burgundy',8),(12,'Black','Pink',8),(13,'Black','Purple',8),(14,'Black','Orange',8),(15,'Black','Yellow',8),(16,'Black','Olive',8),(17,'Black','Green',8),(18,'Black','Teal',8),(19,'Black','Blue',8),(20,'White','White',9),(21,'Grey','White',8),(22,'Charcoal','White',8),(23,'Navy','White',8),(24,'Beige','White',8),(25,'Khaki','White',8),(26,'Brown','White',8),(27,'Red','White',8),(28,'Maroon','White',8),(29,'Burgundy','White',8),(30,'Pink','White',8),(31,'Purple','White',8),(32,'Orange','White',8),(33,'White','Yellow',8),(34,'Olive','White',8),(35,'Green','White',8),(36,'Teal','White',8),(37,'Blue','White',8),(38,'Grey','Grey',9),(39,'Charcoal','Grey',8),(40,'Grey','Navy',8),(41,'Beige','Grey',8),(42,'Grey','Khaki',8),(43,'Brown','Grey',8),(44,'Grey','Red',8),(45,'Grey','Maroon',8),(46,'Burgundy','Grey',8),(47,'Grey','Pink',8),(48,'Grey','Purple',8),(49,'Grey','Orange',8),(50,'Grey','Yellow',8),(51,'Grey','Olive',8),(52,'Green','Grey',8),(53,'Grey','Teal',8),(54,'Blue','Grey',8),(55,'Charcoal','Charcoal',9),(56,'Charcoal','Navy',8),(57,'Beige','Charcoal',8),(58,'Charcoal','Khaki',8),(59,'Brown','Charcoal',8),(60,'Charcoal','Red',8),(61,'Charcoal','Maroon',8),(62,'Burgundy','Charcoal',8),(63,'Charcoal','Pink',8),(64,'Charcoal','Purple',8),(65,'Charcoal','Orange',8),(66,'Charcoal','Yellow',8),(67,'Charcoal','Olive',8),(68,'Charcoal','Green',8),(69,'Charcoal','Teal',8),(70,'Blue','Charcoal',8),(71,'Navy','Navy',9),(72,'Beige','Navy',8),(73,'Khaki','Navy',8),(74,'Brown','Navy',8),(75,'Navy','Red',8),(76,'Maroon','Navy',8),(77,'Burgundy','Navy',8),(78,'Navy','Pink',8),(79,'Navy','Purple',8),(80,'Navy','Orange',8),(81,'Navy','Yellow',8),(82,'Navy','Olive',8),(83,'Green','Navy',8),(84,'Navy','Teal',8),(85,'Blue','Navy',8),(86,'Beige','Beige',9),(87,'Beige','Khaki',8),(88,'Beige','Brown',8),(89,'Beige','Red',8),(90,'Beige','Maroon',8),(91,'Beige','Burgundy',8),(92,'Beige','Pink',8),(93,'Beige','Purple',8),(94,'Beige','Orange',8),(95,'Beige','Yellow',8),(96,'Beige','Olive',8),(97,'Beige','Green',8),(98,'Beige','Teal',8),(99,'Beige','Blue',8),(100,'Khaki','Khaki',9),(101,'Brown','Khaki',8),(102,'Khaki','Red',8),(103,'Khaki','Maroon',8),(104,'Burgundy','Khaki',8),(105,'Khaki','Pink',8),(106,'Khaki','Purple',8),(107,'Khaki','Orange',8),(108,'Khaki','Yellow',8),(109,'Khaki','Olive',8),(110,'Green','Khaki',8),(111,'Khaki','Teal',8),(112,'Blue','Khaki',8),(113,'Brown','Brown',9),(114,'Brown','Red',8),(115,'Brown','Maroon',8),(116,'Brown','Burgundy',8),(117,'Brown','Pink',8),(118,'Brown','Purple',8),(119,'Brown','Orange',8),(120,'Brown','Yellow',8),(121,'Brown','Olive',8),(122,'Brown','Green',8),(123,'Brown','Teal',8),(124,'Blue','Brown',8),(125,'Red','Red',9),(126,'Maroon','Red',8),(127,'Burgundy','Red',8),(128,'Pink','Red',8),(129,'Purple','Red',7),(130,'Orange','Red',8),(131,'Red','Yellow',5),(132,'Olive','Red',5),(133,'Green','Red',7),(134,'Red','Teal',9),(135,'Blue','Red',7),(136,'Maroon','Maroon',9),(137,'Burgundy','Maroon',8),(138,'Maroon','Pink',8),(139,'Maroon','Purple',7),(140,'Maroon','Orange',8),(141,'Maroon','Yellow',5),(142,'Maroon','Olive',5),(143,'Green','Maroon',7),(144,'Maroon','Teal',9),(145,'Blue','Maroon',7),(146,'Burgundy','Burgundy',9),(147,'Burgundy','Pink',8),(148,'Burgundy','Purple',7),(149,'Burgundy','Orange',8),(150,'Burgundy','Yellow',5),(151,'Burgundy','Olive',5),(152,'Burgundy','Green',7),(153,'Burgundy','Teal',9),(154,'Blue','Burgundy',7),(155,'Pink','Pink',9),(156,'Pink','Purple',5),(157,'Orange','Pink',5),(158,'Pink','Yellow',5),(159,'Olive','Pink',5),(160,'Green','Pink',7),(161,'Pink','Teal',9),(162,'Blue','Pink',7),(163,'Purple','Purple',9),(164,'Orange','Purple',7),(165,'Purple','Yellow',7),(166,'Olive','Purple',9),(167,'Green','Purple',9),(168,'Purple','Teal',7),(169,'Blue','Purple',5),(170,'Orange','Orange',9),(171,'Orange','Yellow',8),(172,'Olive','Orange',5),(173,'Green','Orange',7),(174,'Orange','Teal',9),(175,'Blue','Orange',9),(176,'Yellow','Yellow',9),(177,'Olive','Yellow',8),(178,'Green','Yellow',5),(179,'Teal','Yellow',7),(180,'Blue','Yellow',9),(181,'Olive','Olive',9),(182,'Green','Olive',5),(183,'Olive','Teal',7),(184,'Blue','Olive',9),(185,'Green','Green',9),(186,'Green','Teal',5),(187,'Blue','Green',7),(188,'Teal','Teal',9),(189,'Blue','Teal',5),(190,'Blue','Blue',9);
/*!40000 ALTER TABLE `colorcompatibility` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `outfit`
--

DROP TABLE IF EXISTS `outfit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `outfit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `occasion` enum('CASUAL','SMART_CASUAL','WORK','FORMAL') COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `outfit_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outfit`
--

LOCK TABLES `outfit` WRITE;
/*!40000 ALTER TABLE `outfit` DISABLE KEYS */;
INSERT INTO `outfit` VALUES (1,1,'Smart Casual Blue','SMART_CASUAL','Signature everyday outfit','2026-10-06 10:14:57','2026-10-06 10:14:57');
/*!40000 ALTER TABLE `outfit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `outfititem`
--

DROP TABLE IF EXISTS `outfititem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `outfititem` (
  `id` int NOT NULL AUTO_INCREMENT,
  `outfit_id` int NOT NULL,
  `item_id` int NOT NULL,
  `position` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_outfit_item` (`outfit_id`,`item_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `outfititem_ibfk_1` FOREIGN KEY (`outfit_id`) REFERENCES `outfit` (`id`) ON DELETE CASCADE,
  CONSTRAINT `outfititem_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `clothingitem` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outfititem`
--

LOCK TABLES `outfititem` WRITE;
/*!40000 ALTER TABLE `outfititem` DISABLE KEYS */;
INSERT INTO `outfititem` VALUES (1,1,1,1),(2,1,6,2),(3,1,8,3);
/*!40000 ALTER TABLE `outfititem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `season`
--

DROP TABLE IF EXISTS `season`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `season` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_order` int NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `season`
--

LOCK TABLES `season` WRITE;
/*!40000 ALTER TABLE `season` DISABLE KEYS */;
INSERT INTO `season` VALUES (1,'Summer','summer',1,'2026-10-06 10:14:56'),(2,'Winter','winter',2,'2026-10-06 10:14:56'),(3,'Rainy','rainy',3,'2026-10-06 10:14:56'),(4,'Spring','spring',4,'2026-10-06 10:14:56');
/*!40000 ALTER TABLE `season` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'demo@atelier.local','Demo User','pbkdf2_sha256$200000$677c56c0cdcdc0f3e076559d4c99b8c2$87fe22679b53270478c6d3c0043d03a5270f68d9bd8e974b0bc718c267724232','2026-10-06 10:14:56','2026-10-06 10:14:56'),(2,'sam@atelier.local','Sam Rivera','pbkdf2_sha256$200000$de772e46c05089a137ffa8f21f81cfb0$a50a527977214ca8e7ab7cf6071a2a7db2048fd799cc99c2fb682026a2fd3ebf','2026-10-06 10:14:56','2026-10-06 10:14:56'),(3,'something@example.com','something','pbkdf2_sha256$200000$c8f1fec237cad68ac16bd65e88c045bb$ace0f400f35dbd865264f823e05219b22990fd880db6b3fd3868bef3e074a649','2026-10-06 10:15:29','2026-10-06 10:15:29');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_itemcostperwear`
--

DROP TABLE IF EXISTS `v_itemcostperwear`;
/*!50001 DROP VIEW IF EXISTS `v_itemcostperwear`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_itemcostperwear` AS SELECT 
 1 AS `id`,
 1 AS `user_id`,
 1 AS `name`,
 1 AS `category`,
 1 AS `purchase_price`,
 1 AS `wear_count`,
 1 AS `status`,
 1 AS `cost_per_wear`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `wearlog`
--

DROP TABLE IF EXISTS `wearlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wearlog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `item_id` int NOT NULL,
  `outfit_id` int DEFAULT NULL,
  `date_worn` date NOT NULL,
  `weather_temp` int DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `outfit_id` (`outfit_id`),
  KEY `ix_wearlog_user_date` (`user_id`,`date_worn`),
  KEY `ix_wearlog_item_date` (`item_id`,`date_worn`),
  CONSTRAINT `wearlog_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `wearlog_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `clothingitem` (`id`) ON DELETE CASCADE,
  CONSTRAINT `wearlog_ibfk_3` FOREIGN KEY (`outfit_id`) REFERENCES `outfit` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wearlog`
--

LOCK TABLES `wearlog` WRITE;
/*!40000 ALTER TABLE `wearlog` DISABLE KEYS */;
INSERT INTO `wearlog` VALUES (1,1,1,NULL,'2026-10-01',NULL,NULL,'2026-10-06 10:14:56'),(2,1,1,NULL,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56'),(3,1,1,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(4,1,1,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(5,1,1,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(6,1,1,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(7,1,2,NULL,'2026-09-25',NULL,NULL,'2026-10-06 10:14:56'),(8,1,2,NULL,'2026-09-26',NULL,NULL,'2026-10-06 10:14:56'),(9,1,2,NULL,'2026-09-27',NULL,NULL,'2026-10-06 10:14:56'),(10,1,2,NULL,'2026-09-28',NULL,NULL,'2026-10-06 10:14:56'),(11,1,2,NULL,'2026-09-29',NULL,NULL,'2026-10-06 10:14:56'),(12,1,2,NULL,'2026-09-30',NULL,NULL,'2026-10-06 10:14:56'),(13,1,2,NULL,'2026-10-01',NULL,NULL,'2026-10-06 10:14:56'),(14,1,2,NULL,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56'),(15,1,2,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(16,1,2,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(17,1,2,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(18,1,2,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(19,1,3,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(20,1,3,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(21,1,3,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(22,1,3,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(23,1,4,NULL,'2026-09-29',NULL,NULL,'2026-10-06 10:14:56'),(24,1,4,NULL,'2026-09-30',NULL,NULL,'2026-10-06 10:14:56'),(25,1,4,NULL,'2026-10-01',NULL,NULL,'2026-10-06 10:14:56'),(26,1,4,NULL,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56'),(27,1,4,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(28,1,4,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(29,1,4,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(30,1,4,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(31,1,5,NULL,'2026-09-27',NULL,NULL,'2026-10-06 10:14:56'),(32,1,5,NULL,'2026-09-28',NULL,NULL,'2026-10-06 10:14:56'),(33,1,5,NULL,'2026-09-29',NULL,NULL,'2026-10-06 10:14:56'),(34,1,5,NULL,'2026-09-30',NULL,NULL,'2026-10-06 10:14:56'),(35,1,5,NULL,'2026-10-01',NULL,NULL,'2026-10-06 10:14:56'),(36,1,5,NULL,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56'),(37,1,5,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(38,1,5,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(39,1,5,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(40,1,5,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(41,1,6,NULL,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56'),(42,1,6,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(43,1,6,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(44,1,6,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(45,1,6,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(46,1,7,NULL,'2026-09-22',NULL,NULL,'2026-10-06 10:14:56'),(47,1,7,NULL,'2026-09-23',NULL,NULL,'2026-10-06 10:14:56'),(48,1,7,NULL,'2026-09-24',NULL,NULL,'2026-10-06 10:14:56'),(49,1,7,NULL,'2026-09-25',NULL,NULL,'2026-10-06 10:14:56'),(50,1,7,NULL,'2026-09-26',NULL,NULL,'2026-10-06 10:14:56'),(51,1,7,NULL,'2026-09-27',NULL,NULL,'2026-10-06 10:14:56'),(52,1,7,NULL,'2026-09-28',NULL,NULL,'2026-10-06 10:14:56'),(53,1,7,NULL,'2026-09-29',NULL,NULL,'2026-10-06 10:14:56'),(54,1,7,NULL,'2026-09-30',NULL,NULL,'2026-10-06 10:14:56'),(55,1,7,NULL,'2026-10-01',NULL,NULL,'2026-10-06 10:14:56'),(56,1,7,NULL,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56'),(57,1,7,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(58,1,7,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(59,1,7,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(60,1,7,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(61,1,8,NULL,'2026-09-17',NULL,NULL,'2026-10-06 10:14:56'),(62,1,8,NULL,'2026-09-18',NULL,NULL,'2026-10-06 10:14:56'),(63,1,8,NULL,'2026-09-19',NULL,NULL,'2026-10-06 10:14:56'),(64,1,8,NULL,'2026-09-20',NULL,NULL,'2026-10-06 10:14:56'),(65,1,8,NULL,'2026-09-21',NULL,NULL,'2026-10-06 10:14:56'),(66,1,8,NULL,'2026-09-22',NULL,NULL,'2026-10-06 10:14:56'),(67,1,8,NULL,'2026-09-23',NULL,NULL,'2026-10-06 10:14:56'),(68,1,8,NULL,'2026-09-24',NULL,NULL,'2026-10-06 10:14:56'),(69,1,8,NULL,'2026-09-25',NULL,NULL,'2026-10-06 10:14:56'),(70,1,8,NULL,'2026-09-26',NULL,NULL,'2026-10-06 10:14:56'),(71,1,8,NULL,'2026-09-27',NULL,NULL,'2026-10-06 10:14:56'),(72,1,8,NULL,'2026-09-28',NULL,NULL,'2026-10-06 10:14:56'),(73,1,8,NULL,'2026-09-29',NULL,NULL,'2026-10-06 10:14:56'),(74,1,8,NULL,'2026-09-30',NULL,NULL,'2026-10-06 10:14:56'),(75,1,8,NULL,'2026-10-01',NULL,NULL,'2026-10-06 10:14:56'),(76,1,8,NULL,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56'),(77,1,8,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(78,1,8,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(79,1,8,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(80,1,8,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(81,1,9,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(82,1,9,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(83,1,9,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(84,1,10,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(85,1,10,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(86,2,11,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(87,2,11,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(88,2,11,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(89,2,12,NULL,'2026-10-01',NULL,NULL,'2026-10-06 10:14:56'),(90,2,12,NULL,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56'),(91,2,12,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(92,2,12,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(93,2,12,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(94,2,12,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(95,2,13,NULL,'2026-09-28',NULL,NULL,'2026-10-06 10:14:56'),(96,2,13,NULL,'2026-09-29',NULL,NULL,'2026-10-06 10:14:56'),(97,2,13,NULL,'2026-09-30',NULL,NULL,'2026-10-06 10:14:56'),(98,2,13,NULL,'2026-10-01',NULL,NULL,'2026-10-06 10:14:56'),(99,2,13,NULL,'2026-10-02',NULL,NULL,'2026-10-06 10:14:56'),(100,2,13,NULL,'2026-10-03',NULL,NULL,'2026-10-06 10:14:56'),(101,2,13,NULL,'2026-10-04',NULL,NULL,'2026-10-06 10:14:56'),(102,2,13,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(103,2,13,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56'),(104,2,14,NULL,'2026-10-05',NULL,NULL,'2026-10-06 10:14:56'),(105,2,14,NULL,'2026-10-06',NULL,NULL,'2026-10-06 10:14:56');
/*!40000 ALTER TABLE `wearlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'wardrobe_python'
--

--
-- Final view structure for view `v_itemcostperwear`
--

/*!50001 DROP VIEW IF EXISTS `v_itemcostperwear`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_itemcostperwear` AS select `ci`.`id` AS `id`,`ci`.`user_id` AS `user_id`,`ci`.`name` AS `name`,`cat`.`name` AS `category`,`ci`.`purchase_price` AS `purchase_price`,(select count(0) from `wearlog` `w` where (`w`.`item_id` = `ci`.`id`)) AS `wear_count`,(case when ((`ci`.`sent_to_laundry_at` is not null) or ((select count(0) from `wearlog` `w` where ((`w`.`item_id` = `ci`.`id`) and (`w`.`date_worn` >= coalesce(`ci`.`last_washed_at`,'1000-01-01')))) >= `cat`.`wear_limit`)) then 'LAUNDRY' else 'CLEAN' end) AS `status`,(`ci`.`purchase_price` / greatest((select count(0) from `wearlog` `w` where (`w`.`item_id` = `ci`.`id`)),1)) AS `cost_per_wear` from (`clothingitem` `ci` join `category` `cat` on((`cat`.`id` = `ci`.`category_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-06 15:53:58
