-- MySQL dump 10.13  Distrib 8.0.33, for Linux (x86_64)
--
-- Host: localhost    Database: nurojilu_knowledgehub
-- ------------------------------------------------------
-- Server version	8.0.33-cll-lve

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
-- Table structure for table `account_emailaddress`
--

DROP TABLE IF EXISTS `account_emailaddress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_emailaddress` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `verified` tinyint(1) NOT NULL,
  `primary` tinyint(1) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_emailaddress_user_id_email_987c8728_uniq` (`user_id`,`email`),
  KEY `account_emailaddress_email_03be32b2` (`email`),
  CONSTRAINT `account_emailaddress_user_id_2c513194_fk_people_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_emailaddress`
--

LOCK TABLES `account_emailaddress` WRITE;
/*!40000 ALTER TABLE `account_emailaddress` DISABLE KEYS */;
INSERT INTO `account_emailaddress` VALUES (1,'dev.csis.id@gmail.com',1,1,2),(2,'nurojilukmansyah@gmail.com',0,0,1),(3,'nurojilukmansyah2@gmail.com',1,1,9),(4,'zahry04@gmail.com',1,1,10),(5,'tachikaaltaira@gmail.com',1,1,11),(6,'fokcbb@gmail.com',1,1,12),(7,'niela12mahillah@gmail.com',1,1,13),(8,'vickyfarahani0104@gmail.com',1,1,14);
/*!40000 ALTER TABLE `account_emailaddress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_emailconfirmation`
--

DROP TABLE IF EXISTS `account_emailconfirmation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_emailconfirmation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `sent` datetime(6) DEFAULT NULL,
  `key` varchar(64) NOT NULL,
  `email_address_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`),
  KEY `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` (`email_address_id`),
  CONSTRAINT `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` FOREIGN KEY (`email_address_id`) REFERENCES `account_emailaddress` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_emailconfirmation`
--

LOCK TABLES `account_emailconfirmation` WRITE;
/*!40000 ALTER TABLE `account_emailconfirmation` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_emailconfirmation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets_asset`
--

DROP TABLE IF EXISTS `assets_asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets_asset` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `asset_id` varchar(50) NOT NULL,
  `purchase_date` date NOT NULL,
  `purchase_price` decimal(10,2) NOT NULL,
  `warranty_expiration` date DEFAULT NULL,
  `image` varchar(100) DEFAULT NULL,
  `location` varchar(200) NOT NULL,
  `current_value` decimal(10,2) DEFAULT NULL,
  `category_id` bigint NOT NULL,
  `status_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  KEY `assets_asset_category_id_b30c6baf_fk_config_option_id` (`category_id`),
  KEY `assets_asset_status_id_dbcec5aa_fk_config_option_id` (`status_id`),
  CONSTRAINT `assets_asset_category_id_b30c6baf_fk_config_option_id` FOREIGN KEY (`category_id`) REFERENCES `config_option` (`id`),
  CONSTRAINT `assets_asset_status_id_dbcec5aa_fk_config_option_id` FOREIGN KEY (`status_id`) REFERENCES `config_option` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets_asset`
--

LOCK TABLES `assets_asset` WRITE;
/*!40000 ALTER TABLE `assets_asset` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets_asset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets_assetassignment`
--

DROP TABLE IF EXISTS `assets_assetassignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets_assetassignment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `assigned_date` date NOT NULL,
  `return_date` date DEFAULT NULL,
  `remarks` longtext,
  `asset_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assets_assetassignment_asset_id_dc1a4798_fk_assets_asset_id` (`asset_id`),
  KEY `assets_assetassignment_user_id_1613d84a_fk_people_customuser_id` (`user_id`),
  CONSTRAINT `assets_assetassignment_asset_id_dc1a4798_fk_assets_asset_id` FOREIGN KEY (`asset_id`) REFERENCES `assets_asset` (`id`),
  CONSTRAINT `assets_assetassignment_user_id_1613d84a_fk_people_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets_assetassignment`
--

LOCK TABLES `assets_assetassignment` WRITE;
/*!40000 ALTER TABLE `assets_assetassignment` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets_assetassignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets_assetlifecycle`
--

DROP TABLE IF EXISTS `assets_assetlifecycle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets_assetlifecycle` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `stage` varchar(100) NOT NULL,
  `date` date NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `remarks` longtext,
  `asset_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assets_assetlifecycle_asset_id_f47a2bf1_fk_assets_asset_id` (`asset_id`),
  CONSTRAINT `assets_assetlifecycle_asset_id_f47a2bf1_fk_assets_asset_id` FOREIGN KEY (`asset_id`) REFERENCES `assets_asset` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets_assetlifecycle`
--

LOCK TABLES `assets_assetlifecycle` WRITE;
/*!40000 ALTER TABLE `assets_assetlifecycle` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets_assetlifecycle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets_compliance`
--

DROP TABLE IF EXISTS `assets_compliance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets_compliance` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `compliance_type` varchar(100) NOT NULL,
  `status` varchar(50) NOT NULL,
  `last_checked` date NOT NULL,
  `next_check_due` date DEFAULT NULL,
  `remarks` longtext,
  `asset_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assets_compliance_asset_id_94cba0ca_fk_assets_asset_id` (`asset_id`),
  CONSTRAINT `assets_compliance_asset_id_94cba0ca_fk_assets_asset_id` FOREIGN KEY (`asset_id`) REFERENCES `assets_asset` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets_compliance`
--

LOCK TABLES `assets_compliance` WRITE;
/*!40000 ALTER TABLE `assets_compliance` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets_compliance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets_depreciation`
--

DROP TABLE IF EXISTS `assets_depreciation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets_depreciation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `depreciation_date` date NOT NULL,
  `depreciation_amount` decimal(10,2) NOT NULL,
  `remaining_value` decimal(10,2) NOT NULL,
  `asset_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assets_depreciation_asset_id_8bd42a02_fk_assets_asset_id` (`asset_id`),
  CONSTRAINT `assets_depreciation_asset_id_8bd42a02_fk_assets_asset_id` FOREIGN KEY (`asset_id`) REFERENCES `assets_asset` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets_depreciation`
--

LOCK TABLES `assets_depreciation` WRITE;
/*!40000 ALTER TABLE `assets_depreciation` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets_depreciation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets_inventory`
--

DROP TABLE IF EXISTS `assets_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets_inventory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `stock_quantity` int unsigned NOT NULL,
  `reorder_threshold` int unsigned NOT NULL,
  `asset_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`),
  CONSTRAINT `assets_inventory_asset_id_cbd5867e_fk_assets_asset_id` FOREIGN KEY (`asset_id`) REFERENCES `assets_asset` (`id`),
  CONSTRAINT `assets_inventory_chk_1` CHECK ((`stock_quantity` >= 0)),
  CONSTRAINT `assets_inventory_chk_2` CHECK ((`reorder_threshold` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets_inventory`
--

LOCK TABLES `assets_inventory` WRITE;
/*!40000 ALTER TABLE `assets_inventory` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets_maintenance`
--

DROP TABLE IF EXISTS `assets_maintenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets_maintenance` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `maintenance_date` date NOT NULL,
  `next_maintenance_date` date DEFAULT NULL,
  `cost` decimal(10,2) NOT NULL,
  `performed_by` varchar(200) NOT NULL,
  `remarks` longtext,
  `asset_id` bigint NOT NULL,
  `maintenance_type_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assets_maintenance_asset_id_c201b606_fk_assets_asset_id` (`asset_id`),
  KEY `assets_maintenance_maintenance_type_id_3c19259b_fk_config_op` (`maintenance_type_id`),
  CONSTRAINT `assets_maintenance_asset_id_c201b606_fk_assets_asset_id` FOREIGN KEY (`asset_id`) REFERENCES `assets_asset` (`id`),
  CONSTRAINT `assets_maintenance_maintenance_type_id_3c19259b_fk_config_op` FOREIGN KEY (`maintenance_type_id`) REFERENCES `config_option` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets_maintenance`
--

LOCK TABLES `assets_maintenance` WRITE;
/*!40000 ALTER TABLE `assets_maintenance` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets_maintenance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets_procurement`
--

DROP TABLE IF EXISTS `assets_procurement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets_procurement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `procurement_date` date NOT NULL,
  `cost` decimal(10,2) NOT NULL,
  `payment_status` varchar(50) NOT NULL,
  `asset_id` bigint NOT NULL,
  `supplier_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assets_procurement_asset_id_a8922e62_fk_assets_asset_id` (`asset_id`),
  KEY `assets_procurement_supplier_id_b901ce2b_fk_assets_supplier_id` (`supplier_id`),
  CONSTRAINT `assets_procurement_asset_id_a8922e62_fk_assets_asset_id` FOREIGN KEY (`asset_id`) REFERENCES `assets_asset` (`id`),
  CONSTRAINT `assets_procurement_supplier_id_b901ce2b_fk_assets_supplier_id` FOREIGN KEY (`supplier_id`) REFERENCES `assets_supplier` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets_procurement`
--

LOCK TABLES `assets_procurement` WRITE;
/*!40000 ALTER TABLE `assets_procurement` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets_procurement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assets_supplier`
--

DROP TABLE IF EXISTS `assets_supplier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets_supplier` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `contact_person` varchar(100) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `email` varchar(254) NOT NULL,
  `address` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets_supplier`
--

LOCK TABLES `assets_supplier` WRITE;
/*!40000 ALTER TABLE `assets_supplier` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets_supplier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=245 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add site',6,'add_site'),(22,'Can change site',6,'change_site'),(23,'Can delete site',6,'delete_site'),(24,'Can view site',6,'view_site'),(25,'Can add custom user',7,'add_customuser'),(26,'Can change custom user',7,'change_customuser'),(27,'Can delete custom user',7,'delete_customuser'),(28,'Can view custom user',7,'view_customuser'),(29,'Can add organization',8,'add_organization'),(30,'Can change organization',8,'change_organization'),(31,'Can delete organization',8,'delete_organization'),(32,'Can view organization',8,'view_organization'),(33,'Can add person',9,'add_person'),(34,'Can change person',9,'change_person'),(35,'Can delete person',9,'delete_person'),(36,'Can view person',9,'view_person'),(37,'Can add writer',10,'add_writer'),(38,'Can change writer',10,'change_writer'),(39,'Can delete writer',10,'delete_writer'),(40,'Can view writer',10,'view_writer'),(41,'Can add staff',11,'add_staff'),(42,'Can change staff',11,'change_staff'),(43,'Can delete staff',11,'delete_staff'),(44,'Can view staff',11,'view_staff'),(45,'Can add speaker',12,'add_speaker'),(46,'Can change speaker',12,'change_speaker'),(47,'Can delete speaker',12,'delete_speaker'),(48,'Can view speaker',12,'view_speaker'),(49,'Can add relationship',13,'add_relationship'),(50,'Can change relationship',13,'change_relationship'),(51,'Can delete relationship',13,'delete_relationship'),(52,'Can view relationship',13,'view_relationship'),(53,'Can add microsoft account',14,'add_microsoftaccount'),(54,'Can change microsoft account',14,'change_microsoftaccount'),(55,'Can delete microsoft account',14,'delete_microsoftaccount'),(56,'Can view microsoft account',14,'view_microsoftaccount'),(57,'Can add xbox live account',15,'add_xboxliveaccount'),(58,'Can change xbox live account',15,'change_xboxliveaccount'),(59,'Can delete xbox live account',15,'delete_xboxliveaccount'),(60,'Can view xbox live account',15,'view_xboxliveaccount'),(61,'Can add Aset',16,'add_asset'),(62,'Can change Aset',16,'change_asset'),(63,'Can delete Aset',16,'delete_asset'),(64,'Can view Aset',16,'view_asset'),(65,'Can add asset assignment',17,'add_assetassignment'),(66,'Can change asset assignment',17,'change_assetassignment'),(67,'Can delete asset assignment',17,'delete_assetassignment'),(68,'Can view asset assignment',17,'view_assetassignment'),(69,'Can add asset lifecycle',18,'add_assetlifecycle'),(70,'Can change asset lifecycle',18,'change_assetlifecycle'),(71,'Can delete asset lifecycle',18,'delete_assetlifecycle'),(72,'Can view asset lifecycle',18,'view_assetlifecycle'),(73,'Can add compliance',19,'add_compliance'),(74,'Can change compliance',19,'change_compliance'),(75,'Can delete compliance',19,'delete_compliance'),(76,'Can view compliance',19,'view_compliance'),(77,'Can add depreciation',20,'add_depreciation'),(78,'Can change depreciation',20,'change_depreciation'),(79,'Can delete depreciation',20,'delete_depreciation'),(80,'Can view depreciation',20,'view_depreciation'),(81,'Can add inventory',21,'add_inventory'),(82,'Can change inventory',21,'change_inventory'),(83,'Can delete inventory',21,'delete_inventory'),(84,'Can view inventory',21,'view_inventory'),(85,'Can add maintenance',22,'add_maintenance'),(86,'Can change maintenance',22,'change_maintenance'),(87,'Can delete maintenance',22,'delete_maintenance'),(88,'Can view maintenance',22,'view_maintenance'),(89,'Can add procurement',23,'add_procurement'),(90,'Can change procurement',23,'change_procurement'),(91,'Can delete procurement',23,'delete_procurement'),(92,'Can view procurement',23,'view_procurement'),(93,'Can add supplier',24,'add_supplier'),(94,'Can change supplier',24,'change_supplier'),(95,'Can delete supplier',24,'delete_supplier'),(96,'Can view supplier',24,'view_supplier'),(97,'Can add analytics visitor data',25,'add_analyticsvisitordata'),(98,'Can change analytics visitor data',25,'change_analyticsvisitordata'),(99,'Can delete analytics visitor data',25,'delete_analyticsvisitordata'),(100,'Can view analytics visitor data',25,'view_analyticsvisitordata'),(101,'Can add database backup',26,'add_databasebackup'),(102,'Can change database backup',26,'change_databasebackup'),(103,'Can delete database backup',26,'delete_databasebackup'),(104,'Can view database backup',26,'view_databasebackup'),(105,'Can add conversation',27,'add_conversation'),(106,'Can change conversation',27,'change_conversation'),(107,'Can delete conversation',27,'delete_conversation'),(108,'Can view conversation',27,'view_conversation'),(109,'Can add message',28,'add_message'),(110,'Can change message',28,'change_message'),(111,'Can delete message',28,'delete_message'),(112,'Can view message',28,'view_message'),(113,'Can add code content',29,'add_codecontent'),(114,'Can change code content',29,'change_codecontent'),(115,'Can delete code content',29,'delete_codecontent'),(116,'Can view code content',29,'view_codecontent'),(117,'Can add image content',30,'add_imagecontent'),(118,'Can change image content',30,'change_imagecontent'),(119,'Can delete image content',30,'delete_imagecontent'),(120,'Can view image content',30,'view_imagecontent'),(121,'Can add text content',31,'add_textcontent'),(122,'Can change text content',31,'change_textcontent'),(123,'Can delete text content',31,'delete_textcontent'),(124,'Can view text content',31,'view_textcontent'),(125,'Can add Category',32,'add_category'),(126,'Can change Category',32,'change_category'),(127,'Can delete Category',32,'delete_category'),(128,'Can view Category',32,'view_category'),(129,'Can add Option',33,'add_option'),(130,'Can change Option',33,'change_option'),(131,'Can delete Option',33,'delete_option'),(132,'Can view Option',33,'view_option'),(133,'Can add photo backup',34,'add_photobackup'),(134,'Can change photo backup',34,'change_photobackup'),(135,'Can delete photo backup',34,'delete_photobackup'),(136,'Can view photo backup',34,'view_photobackup'),(137,'Can add photo',35,'add_photo'),(138,'Can change photo',35,'change_photo'),(139,'Can delete photo',35,'delete_photo'),(140,'Can view photo',35,'view_photo'),(141,'Can add notification',36,'add_notification'),(142,'Can change notification',36,'change_notification'),(143,'Can delete notification',36,'delete_notification'),(144,'Can view notification',36,'view_notification'),(145,'Can add budget',37,'add_budget'),(146,'Can change budget',37,'change_budget'),(147,'Can delete budget',37,'delete_budget'),(148,'Can view budget',37,'view_budget'),(149,'Can add grant',38,'add_grant'),(150,'Can change grant',38,'change_grant'),(151,'Can delete grant',38,'delete_grant'),(152,'Can view grant',38,'view_grant'),(153,'Can add journal entry',39,'add_journalentry'),(154,'Can change journal entry',39,'change_journalentry'),(155,'Can delete journal entry',39,'delete_journalentry'),(156,'Can view journal entry',39,'view_journalentry'),(157,'Can add budget allocation',40,'add_budgetallocation'),(158,'Can change budget allocation',40,'change_budgetallocation'),(159,'Can delete budget allocation',40,'delete_budgetallocation'),(160,'Can view budget allocation',40,'view_budgetallocation'),(161,'Can add grant expense',41,'add_grantexpense'),(162,'Can change grant expense',41,'change_grantexpense'),(163,'Can delete grant expense',41,'delete_grantexpense'),(164,'Can view grant expense',41,'view_grantexpense'),(165,'Can add document proof',42,'add_documentproof'),(166,'Can change document proof',42,'change_documentproof'),(167,'Can delete document proof',42,'delete_documentproof'),(168,'Can view document proof',42,'view_documentproof'),(169,'Can add pos allocation',43,'add_posallocation'),(170,'Can change pos allocation',43,'change_posallocation'),(171,'Can delete pos allocation',43,'delete_posallocation'),(172,'Can view pos allocation',43,'view_posallocation'),(173,'Can add pos expense',44,'add_posexpense'),(174,'Can change pos expense',44,'change_posexpense'),(175,'Can delete pos expense',44,'delete_posexpense'),(176,'Can view pos expense',44,'view_posexpense'),(177,'Can add currency',45,'add_currency'),(178,'Can change currency',45,'change_currency'),(179,'Can delete currency',45,'delete_currency'),(180,'Can view currency',45,'view_currency'),(181,'Can add exchange rate',46,'add_exchangerate'),(182,'Can change exchange rate',46,'change_exchangerate'),(183,'Can delete exchange rate',46,'delete_exchangerate'),(184,'Can view exchange rate',46,'view_exchangerate'),(185,'Can add email address',47,'add_emailaddress'),(186,'Can change email address',47,'change_emailaddress'),(187,'Can delete email address',47,'delete_emailaddress'),(188,'Can view email address',47,'view_emailaddress'),(189,'Can add email confirmation',48,'add_emailconfirmation'),(190,'Can change email confirmation',48,'change_emailconfirmation'),(191,'Can delete email confirmation',48,'delete_emailconfirmation'),(192,'Can view email confirmation',48,'view_emailconfirmation'),(193,'Can add social account',49,'add_socialaccount'),(194,'Can change social account',49,'change_socialaccount'),(195,'Can delete social account',49,'delete_socialaccount'),(196,'Can view social account',49,'view_socialaccount'),(197,'Can add social application',50,'add_socialapp'),(198,'Can change social application',50,'change_socialapp'),(199,'Can delete social application',50,'delete_socialapp'),(200,'Can view social application',50,'view_socialapp'),(201,'Can add social application token',51,'add_socialtoken'),(202,'Can change social application token',51,'change_socialtoken'),(203,'Can delete social application token',51,'delete_socialtoken'),(204,'Can view social application token',51,'view_socialtoken'),(205,'Can add project',52,'add_project'),(206,'Can change project',52,'change_project'),(207,'Can delete project',52,'delete_project'),(208,'Can view project',52,'view_project'),(209,'Can add progress',53,'add_progress'),(210,'Can change progress',53,'change_progress'),(211,'Can delete progress',53,'delete_progress'),(212,'Can view progress',53,'view_progress'),(213,'Can add event',54,'add_event'),(214,'Can change event',54,'change_event'),(215,'Can delete event',54,'delete_event'),(216,'Can view event',54,'view_event'),(217,'Can add project grant',55,'add_projectgrant'),(218,'Can change project grant',55,'change_projectgrant'),(219,'Can delete project grant',55,'delete_projectgrant'),(220,'Can view project grant',55,'view_projectgrant'),(221,'Can add grant report',56,'add_grantreport'),(222,'Can change grant report',56,'change_grantreport'),(223,'Can delete grant report',56,'delete_grantreport'),(224,'Can view grant report',56,'view_grantreport'),(225,'Can add project member',57,'add_projectmember'),(226,'Can change project member',57,'change_projectmember'),(227,'Can delete project member',57,'delete_projectmember'),(228,'Can view project member',57,'view_projectmember'),(229,'Can add publication',58,'add_publication'),(230,'Can change publication',58,'change_publication'),(231,'Can delete publication',58,'delete_publication'),(232,'Can view publication',58,'view_publication'),(233,'Can add research data',59,'add_researchdata'),(234,'Can change research data',59,'change_researchdata'),(235,'Can delete research data',59,'delete_researchdata'),(236,'Can view research data',59,'view_researchdata'),(237,'Can add completed task',60,'add_completedtask'),(238,'Can change completed task',60,'change_completedtask'),(239,'Can delete completed task',60,'delete_completedtask'),(240,'Can view completed task',60,'view_completedtask'),(241,'Can add task',61,'add_task'),(242,'Can change task',61,'change_task'),(243,'Can delete task',61,'delete_task'),(244,'Can view task',61,'view_task');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `background_task`
--

DROP TABLE IF EXISTS `background_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `background_task` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `task_name` varchar(190) NOT NULL,
  `task_params` longtext NOT NULL,
  `task_hash` varchar(40) NOT NULL,
  `verbose_name` varchar(255) DEFAULT NULL,
  `priority` int NOT NULL,
  `run_at` datetime(6) NOT NULL,
  `repeat` bigint NOT NULL,
  `repeat_until` datetime(6) DEFAULT NULL,
  `queue` varchar(190) DEFAULT NULL,
  `attempts` int NOT NULL,
  `failed_at` datetime(6) DEFAULT NULL,
  `last_error` longtext NOT NULL,
  `locked_by` varchar(64) DEFAULT NULL,
  `locked_at` datetime(6) DEFAULT NULL,
  `creator_object_id` int unsigned DEFAULT NULL,
  `creator_content_type_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `background_task_creator_content_type_61cc9af3_fk_django_co` (`creator_content_type_id`),
  KEY `background_task_task_name_4562d56a` (`task_name`),
  KEY `background_task_task_hash_d8f233bd` (`task_hash`),
  KEY `background_task_priority_88bdbce9` (`priority`),
  KEY `background_task_run_at_7baca3aa` (`run_at`),
  KEY `background_task_queue_1d5f3a40` (`queue`),
  KEY `background_task_attempts_a9ade23d` (`attempts`),
  KEY `background_task_failed_at_b81bba14` (`failed_at`),
  KEY `background_task_locked_by_db7779e3` (`locked_by`),
  KEY `background_task_locked_at_0fb0f225` (`locked_at`),
  CONSTRAINT `background_task_creator_content_type_61cc9af3_fk_django_co` FOREIGN KEY (`creator_content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `background_task_chk_1` CHECK ((`creator_object_id` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `background_task`
--

LOCK TABLES `background_task` WRITE;
/*!40000 ALTER TABLE `background_task` DISABLE KEYS */;
INSERT INTO `background_task` VALUES (1,'app.people.views.process_backup','[[1], {}]','4a4f68b43c6d3072641a36f9d0f3e57093f6fb5a',NULL,0,'2024-10-24 06:41:49.338942',0,NULL,NULL,0,NULL,'','2561037','2024-10-24 06:47:16.963781',NULL,NULL),(2,'app.people.views.process_backup','[[1], {}]','4a4f68b43c6d3072641a36f9d0f3e57093f6fb5a',NULL,0,'2024-10-24 06:42:29.167757',0,NULL,NULL,0,NULL,'',NULL,NULL,NULL,NULL),(3,'app.people.views.process_backup','[[1], {}]','4a4f68b43c6d3072641a36f9d0f3e57093f6fb5a',NULL,0,'2024-10-24 06:42:41.270680',0,NULL,NULL,0,NULL,'',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `background_task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `background_task_completedtask`
--

DROP TABLE IF EXISTS `background_task_completedtask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `background_task_completedtask` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `task_name` varchar(190) NOT NULL,
  `task_params` longtext NOT NULL,
  `task_hash` varchar(40) NOT NULL,
  `verbose_name` varchar(255) DEFAULT NULL,
  `priority` int NOT NULL,
  `run_at` datetime(6) NOT NULL,
  `repeat` bigint NOT NULL,
  `repeat_until` datetime(6) DEFAULT NULL,
  `queue` varchar(190) DEFAULT NULL,
  `attempts` int NOT NULL,
  `failed_at` datetime(6) DEFAULT NULL,
  `last_error` longtext NOT NULL,
  `locked_by` varchar(64) DEFAULT NULL,
  `locked_at` datetime(6) DEFAULT NULL,
  `creator_object_id` int unsigned DEFAULT NULL,
  `creator_content_type_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `background_task_comp_creator_content_type_21d6a741_fk_django_co` (`creator_content_type_id`),
  KEY `background_task_completedtask_task_name_388dabc2` (`task_name`),
  KEY `background_task_completedtask_task_hash_91187576` (`task_hash`),
  KEY `background_task_completedtask_priority_9080692e` (`priority`),
  KEY `background_task_completedtask_run_at_77c80f34` (`run_at`),
  KEY `background_task_completedtask_queue_61fb0415` (`queue`),
  KEY `background_task_completedtask_attempts_772a6783` (`attempts`),
  KEY `background_task_completedtask_failed_at_3de56618` (`failed_at`),
  KEY `background_task_completedtask_locked_by_edc8a213` (`locked_by`),
  KEY `background_task_completedtask_locked_at_29c62708` (`locked_at`),
  CONSTRAINT `background_task_comp_creator_content_type_21d6a741_fk_django_co` FOREIGN KEY (`creator_content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `background_task_completedtask_chk_1` CHECK ((`creator_object_id` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `background_task_completedtask`
--

LOCK TABLES `background_task_completedtask` WRITE;
/*!40000 ALTER TABLE `background_task_completedtask` DISABLE KEYS */;
/*!40000 ALTER TABLE `background_task_completedtask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `config_category`
--

DROP TABLE IF EXISTS `config_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `config_category` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `updated_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `config_category_created_by_id_c542c717_fk_people_customuser_id` (`created_by_id`),
  KEY `config_category_updated_by_id_2ab1223d_fk_people_customuser_id` (`updated_by_id`),
  CONSTRAINT `config_category_created_by_id_c542c717_fk_people_customuser_id` FOREIGN KEY (`created_by_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `config_category_updated_by_id_2ab1223d_fk_people_customuser_id` FOREIGN KEY (`updated_by_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `config_category`
--

LOCK TABLES `config_category` WRITE;
/*!40000 ALTER TABLE `config_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `config_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `config_option`
--

DROP TABLE IF EXISTS `config_option`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `config_option` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `value` varchar(255) DEFAULT NULL,
  `description` longtext NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `order` int unsigned NOT NULL,
  `category_id` bigint NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `parent_id` bigint DEFAULT NULL,
  `updated_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `config_option_category_id_name_18770eed_uniq` (`category_id`,`name`),
  KEY `config_option_created_by_id_33c8e10b_fk_people_customuser_id` (`created_by_id`),
  KEY `config_option_parent_id_5b1e96e2_fk_config_option_id` (`parent_id`),
  KEY `config_option_updated_by_id_c18d2175_fk_people_customuser_id` (`updated_by_id`),
  CONSTRAINT `config_option_category_id_fe215282_fk_config_category_id` FOREIGN KEY (`category_id`) REFERENCES `config_category` (`id`),
  CONSTRAINT `config_option_created_by_id_33c8e10b_fk_people_customuser_id` FOREIGN KEY (`created_by_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `config_option_parent_id_5b1e96e2_fk_config_option_id` FOREIGN KEY (`parent_id`) REFERENCES `config_option` (`id`),
  CONSTRAINT `config_option_updated_by_id_c18d2175_fk_people_customuser_id` FOREIGN KEY (`updated_by_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `config_option_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `config_option`
--

LOCK TABLES `config_option` WRITE;
/*!40000 ALTER TABLE `config_option` DISABLE KEYS */;
/*!40000 ALTER TABLE `config_option` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_people_customuser_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_people_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2024-10-17 04:32:02.237012','1','nurojilukmansyah.com',2,'[{\"changed\": {\"fields\": [\"Domain name\", \"Display name\"]}}]',6,1),(2,'2024-10-23 03:02:55.885309','1','Knowledgehub',1,'[{\"added\": {}}]',50,1),(3,'2024-10-23 03:03:33.089971','1','Knowledgehub',2,'[{\"changed\": {\"fields\": [\"Sites\"]}}]',50,1),(4,'2024-10-23 04:50:12.785888','1','Knowledgehub',2,'[]',50,1),(5,'2024-10-23 05:22:30.398982','1','asasa asasa',1,'[{\"added\": {}}]',9,1),(6,'2024-10-24 04:19:09.413213','1','Knowledgehub',3,'',50,1),(7,'2024-10-24 06:38:26.597227','8','zahry04@gmail.com',3,'',7,1),(8,'2024-10-24 06:42:18.670161','2','Backup 2 - nurojilukmansyah@gmail.com - completed',3,'',34,1),(9,'2024-10-24 06:42:18.681954','1','Backup 1 - nurojilukmansyah@gmail.com - completed',3,'',34,1),(10,'2024-10-24 06:48:30.677549','3','Backup 3 - nurojilukmansyah@gmail.com - processing',3,'',34,1),(11,'2024-10-24 07:01:43.514433','10','zahry04@gmail.com',2,'[{\"changed\": {\"fields\": [\"Staff status\"]}}]',7,1),(12,'2024-10-24 07:02:05.738900','2','dev.csis.id@gmail.com',2,'[{\"changed\": {\"fields\": [\"User type\", \"Staff status\", \"Superuser status\"]}}]',7,1),(13,'2024-10-24 07:02:13.167550','9','nurojilukmansyah2@gmail.com',2,'[{\"changed\": {\"fields\": [\"Staff status\", \"Superuser status\"]}}]',7,1),(14,'2024-10-24 08:56:01.264110','11','Backup 11 - nurojilukmansyah@gmail.com - processing',3,'',34,1),(15,'2024-10-24 08:56:01.271656','10','Backup 10 - nurojilukmansyah@gmail.com - processing',3,'',34,1),(16,'2024-10-24 08:56:01.280304','9','Backup 9 - nurojilukmansyah@gmail.com - processing',3,'',34,1),(17,'2024-10-24 08:56:01.285413','8','Backup 8 - nurojilukmansyah@gmail.com - processing',3,'',34,1),(18,'2024-10-24 08:56:01.297549','7','Backup 7 - nurojilukmansyah@gmail.com - processing',3,'',34,1),(19,'2024-10-24 08:56:01.306219','6','Backup 6 - dev.csis.id@gmail.com - failed',3,'',34,1),(20,'2024-10-24 08:56:01.325156','5','Backup 5 - dev.csis.id@gmail.com - failed',3,'',34,1),(21,'2024-10-24 08:56:01.335596','4','Backup 4 - dev.csis.id@gmail.com - failed',3,'',34,1),(22,'2024-10-24 13:16:03.652079','12','Backup 12 - zahry04@gmail.com - processing',3,'',34,1),(23,'2024-10-24 13:16:51.074821','13','Backup 13 - zahry04@gmail.com - processing',3,'',34,1),(24,'2024-10-25 05:59:06.209946','17','Backup 17 - nurojilukmansyah@gmail.com - completed',3,'',34,1),(25,'2024-10-25 05:59:06.256683','16','Backup 16 - nurojilukmansyah@gmail.com - completed',3,'',34,1),(26,'2024-10-25 05:59:06.261035','15','Backup 15 - nurojilukmansyah@gmail.com - processing',3,'',34,1),(27,'2024-10-25 05:59:06.264362','14','Backup 14 - nurojilukmansyah@gmail.com - completed',3,'',34,1),(28,'2024-10-25 05:59:57.433084','12','fokcbb@gmail.com',2,'[{\"changed\": {\"fields\": [\"User type\", \"Staff status\"]}}]',7,1),(29,'2024-10-26 02:17:43.244998','19','Backup 19 - nurojilukmansyah@gmail.com - processing',3,'',34,1),(30,'2024-10-26 02:17:43.250663','18','Backup 18 - nurojilukmansyah@gmail.com - processing',3,'',34,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (47,'account','emailaddress'),(48,'account','emailconfirmation'),(1,'admin','logentry'),(16,'assets','asset'),(17,'assets','assetassignment'),(18,'assets','assetlifecycle'),(19,'assets','compliance'),(20,'assets','depreciation'),(21,'assets','inventory'),(22,'assets','maintenance'),(23,'assets','procurement'),(24,'assets','supplier'),(3,'auth','group'),(2,'auth','permission'),(60,'background_task','completedtask'),(61,'background_task','task'),(32,'config','category'),(33,'config','option'),(4,'contenttypes','contenttype'),(37,'finance','budget'),(40,'finance','budgetallocation'),(45,'finance','currency'),(42,'finance','documentproof'),(46,'finance','exchangerate'),(38,'finance','grant'),(41,'finance','grantexpense'),(39,'finance','journalentry'),(43,'finance','posallocation'),(44,'finance','posexpense'),(14,'microsoft_auth','microsoftaccount'),(15,'microsoft_auth','xboxliveaccount'),(7,'people','customuser'),(8,'people','organization'),(9,'people','person'),(35,'people','photo'),(34,'people','photobackup'),(13,'people','relationship'),(12,'people','speaker'),(11,'people','staff'),(10,'people','writer'),(54,'project','event'),(56,'project','grantreport'),(53,'project','progress'),(52,'project','project'),(55,'project','projectgrant'),(57,'project','projectmember'),(58,'project','publication'),(59,'project','researchdata'),(5,'sessions','session'),(6,'sites','site'),(49,'socialaccount','socialaccount'),(50,'socialaccount','socialapp'),(51,'socialaccount','socialtoken'),(25,'tools','analyticsvisitordata'),(29,'tools','codecontent'),(27,'tools','conversation'),(26,'tools','databasebackup'),(30,'tools','imagecontent'),(28,'tools','message'),(36,'tools','notification'),(31,'tools','textcontent');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2024-10-17 02:58:00.851357'),(2,'contenttypes','0002_remove_content_type_name','2024-10-17 02:58:01.009359'),(3,'auth','0001_initial','2024-10-17 02:58:01.568474'),(4,'auth','0002_alter_permission_name_max_length','2024-10-17 02:58:01.684037'),(5,'auth','0003_alter_user_email_max_length','2024-10-17 02:58:01.716662'),(6,'auth','0004_alter_user_username_opts','2024-10-17 02:58:01.729239'),(7,'auth','0005_alter_user_last_login_null','2024-10-17 02:58:01.743375'),(8,'auth','0006_require_contenttypes_0002','2024-10-17 02:58:01.750284'),(9,'auth','0007_alter_validators_add_error_messages','2024-10-17 02:58:01.761757'),(10,'auth','0008_alter_user_username_max_length','2024-10-17 02:58:01.773327'),(11,'auth','0009_alter_user_last_name_max_length','2024-10-17 02:58:01.781016'),(12,'auth','0010_alter_group_name_max_length','2024-10-17 02:58:01.806341'),(13,'auth','0011_update_proxy_permissions','2024-10-17 02:58:01.818322'),(14,'auth','0012_alter_user_first_name_max_length','2024-10-17 02:58:01.826969'),(15,'people','0001_initial','2024-10-17 02:58:03.250242'),(16,'admin','0001_initial','2024-10-17 02:58:03.520978'),(17,'admin','0002_logentry_remove_auto_add','2024-10-17 02:58:03.536191'),(18,'admin','0003_logentry_add_action_flag_choices','2024-10-17 02:58:03.549489'),(19,'microsoft_auth','0001_initial','2024-10-17 02:58:03.763776'),(20,'microsoft_auth','0002_fix_microsoft_id_length','2024-10-17 02:58:03.800609'),(21,'microsoft_auth','0003_microsoft_id_openid','2024-10-17 02:58:03.929030'),(22,'sessions','0001_initial','2024-10-17 02:58:04.004214'),(23,'sites','0001_initial','2024-10-17 02:58:04.037465'),(24,'sites','0002_alter_domain_unique','2024-10-17 02:58:04.086567'),(25,'config','0001_initial','2024-10-17 03:39:45.510729'),(26,'assets','0001_initial','2024-10-17 03:39:45.729039'),(27,'assets','0002_initial','2024-10-17 03:39:46.233299'),(28,'assets','0003_initial','2024-10-17 03:39:47.311989'),(29,'config','0002_initial','2024-10-17 03:39:48.021661'),(30,'tools','0001_initial','2024-10-17 03:39:48.480657'),(31,'tools','0002_codecontent_imagecontent_textcontent_and_more','2024-10-17 03:39:48.814945'),(32,'microsoft_auth','0004_alter_microsoftaccount_id_alter_xboxliveaccount_id','2024-10-17 03:40:07.507583'),(33,'account','0001_initial','2024-10-22 16:53:13.386557'),(34,'account','0002_email_max_length','2024-10-22 16:53:13.421118'),(35,'account','0003_alter_emailaddress_create_unique_verified_email','2024-10-22 16:53:13.493007'),(36,'account','0004_alter_emailaddress_drop_unique_email','2024-10-22 16:53:13.550945'),(37,'account','0005_emailaddress_idx_upper_email','2024-10-22 16:53:13.605543'),(38,'account','0006_emailaddress_lower','2024-10-22 16:53:13.645174'),(39,'account','0007_emailaddress_idx_email','2024-10-22 16:53:13.736309'),(40,'account','0008_emailaddress_unique_primary_email_fixup','2024-10-22 16:53:13.772829'),(41,'account','0009_emailaddress_unique_primary_email','2024-10-22 16:53:13.895817'),(42,'finance','0001_initial','2024-10-22 16:53:14.151702'),(43,'finance','0002_documentproof_posallocation_posexpense_and_more','2024-10-22 16:53:15.073110'),(44,'finance','0003_rename_total_amount_budget_initial_amount_and_more','2024-10-22 16:53:15.152481'),(45,'finance','0004_currency_alter_budget_additional_amount_and_more','2024-10-22 16:53:16.317280'),(46,'people','0002_backupzip','2024-10-22 16:53:16.421605'),(47,'people','0003_customuser_google_refresh_token_and_more','2024-10-22 16:53:16.620194'),(48,'people','0004_photobackup_delete_backupzip','2024-10-22 16:53:16.723564'),(49,'people','0005_alter_photobackup_options','2024-10-22 16:53:16.742027'),(50,'people','0006_alter_photobackup_options_and_more','2024-10-22 16:53:17.157162'),(51,'people','0007_alter_photo_filename_alter_photo_google_photo_id_and_more','2024-10-22 16:53:17.271889'),(52,'socialaccount','0001_initial','2024-10-22 16:53:17.727745'),(53,'socialaccount','0002_token_max_lengths','2024-10-22 16:53:17.790733'),(54,'socialaccount','0003_extra_data_default_dict','2024-10-22 16:53:17.809292'),(55,'socialaccount','0004_app_provider_id_settings','2024-10-22 16:53:17.955738'),(56,'socialaccount','0005_socialtoken_nullable_app','2024-10-22 16:53:18.120082'),(57,'socialaccount','0006_alter_socialaccount_extra_data','2024-10-22 16:53:18.212381'),(58,'tools','0002_notification','2024-10-22 16:53:18.382986'),(59,'people','0008_alter_photobackup_photos_limit','2024-10-22 17:09:45.058963'),(60,'finance','0005_alter_budget_options_alter_budgetallocation_options_and_more','2024-10-23 15:13:59.346494'),(61,'finance','0006_alter_exchangerate_options_and_more','2024-10-23 15:13:59.514664'),(62,'people','0008_alter_customuser_options_alter_customuser_managers_and_more','2024-10-23 15:14:00.198592'),(63,'project','0001_initial','2024-10-23 15:14:08.275601'),(64,'background_task','0001_initial','2024-10-24 05:52:31.263673'),(65,'background_task','0002_auto_20170927_1109','2024-10-24 05:52:31.316342'),(66,'background_task','0003_alter_completedtask_id_alter_task_id','2024-10-24 05:53:43.419252'),(67,'people','0009_alter_photobackup_photos_limit','2024-10-24 05:53:43.455242'),(68,'tools','0003_databasebackup_created_at_and_more','2024-10-26 02:48:40.033063');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('0yaao1bwdaj5m5wwhrvcp4kmzi1pai2s','.eJylkE1rwzAMhv-LziHNpx331l26yxhsPW0Uo9hKY-o5WeyUQul_nzvSQc-7CKRHel9JF_CDMmhRqWF2QfqAgTysL_Cmen7iI2fP36M_vr7D-vMC4zQo8pGDHQ7GQQIaA8LazdYmMB4VSTVokieaTGdouhNH5xCHVhp93w446RVck5wXgtcxsrTIhajqYp_A9uNQ79i0O79s57Fi9h-2fw5NUaZNkzOR8f01gfutS7eW9IXG3tUkzqGXs6dJGh0d8wweii2qI7kbQWtv5XTRS397FuzTTczIBaMwmME9LVMPUn38RtTJSt2wmjHdUq5VWXdVg6Lq4t6aOl3GEzTPOiYiyzHrVJvVxBWxpitRaF7A9QcmQpd4:1t3rUx:lSGJeqfkoejgtLnM9Mo-FpZ_ikR82H3GvUJu2JiOFlI','2024-11-23 06:39:07.476013'),('69h1nl8z2c2s6wt0norwnmjeihhnrrjk','.eJxVjMEOwiAQRP-FsyFIF1g9eu83kAW2UjWQlPZk_Hdp0oNe5jDvzbyFp23Nfmu8-DmJqziL028XKD657CA9qNyrjLWsyxzkrsiDNjnWxK_b4f4dZGq5rxF0RItaDQgDOaMB0TozaGayFw7JukRacQ8yALFjDDZMwegJnALx-QK1dTci:1t2kvu:LI93t_AwhvAx0olDaMqC_3jR-XIPAcfAOnSQnnec8dg','2024-11-04 05:26:22.235652'),('6locma42bcyr5uv7wek5h1dtb2q23s6l','.eJxVjDsOgzAQRO-ydYQw_kKXXMRaL4uw4hgJmzQod89HpKCcNzNvh7JQxIREy5arLxUrFxj21wX-7MlrnCKPnh8YEwx5S-kCHrc6-63w6uMIAwgBJxiQ7py_Dab0xc3ha36boy7N9ZM410hY45Jvx-ukmrHMH09QpCwZqbVynVItt5M0tiejuCOtg7POjb3sWqTOyZ5bY8UYqLdCTJMOEl5vWZhQ-w:1t4CtT:PZns5WkJ-gj_p7BvOQdzBXj3lwOc475G2IzumNRgUwE','2024-11-24 05:29:51.715398'),('9hl5i6wg2m8rgtfq3hqt994s8l4jis9e','.eJxVj81uhDAMhN_FZ4RCfp29ta9RVcgE74JKSUVCL4h3b9ilBy6WNfPNyN4gxTDSRCHEdc5typQ5wW3bK_jXaM0Dz3kMlMc4t9-ch9gX5mOD1w63awuUbIZb46R3Vkg0tWq80MpW8LPE37HnpUQeMT4mLuw6Hg2NcLZBRG9FIyUqNN542D8reB7QromX9kXCResofPF8GDRNh1yfZ9RP5rRT_XZ54_1MXaoGSkPpQS0DWpRCoVbkjNSI1hklmcl67nrrepKCyyCjdSg2dra7d0betRMa9j-7hG-d:1t3tfR:PZTatLOg_cae5xqMeRz4OdtB0s36l32uSAUlO4_Quec','2024-11-23 08:58:05.511782'),('ay1ufzflicp42r4guufv9sy9mkbm9u90','.eJxVjstqwzAQRf9l1sYPWbHs7FoodJ0UCi1FjEfjWESVgiWXgsm_1ynOIsu5597DLBADWXRIFGafdEyYOMJ-gcNHPIaXU1epI72_HV5h_7nAZQrEceXgwsl6yMBgQtj72bkMLmdiTcGw_uHJDpanO_H8m9ZRkUJwsaARUwHXrFKia2W5K1UuhGibVnxdM7i_sjmM5m-07m7SOKdRz5Enbc2qrGp4CHukM_sbQeducb758v_OhmP-tF7skyVMNvjnbfWgGjGOq6crTV9LQ0LIuq-7AXe9MKYXXLfMiqgpWSrVKmTRIFdkkExTC9nJVsqhKuH6B9vleC4:1t4EZL:1vTSpu2tsBJjI0XAmXvfjE1kWaOLjra0vebzDqUSubQ','2024-11-24 07:17:11.627010'),('b58aoif1lw96wpy4c0hbunkebl1mzxlg','.eJxVjMEOgyAQRP9lz8aggBZv7Y-QZV0iKcWkYC_Gf6829uBx3sy8FfJMASMSzUsqNhcsnGFYtwr-7MPv4AOPll8YIgxpibECi0uZ7JL5bcMIAzQKLtAhPTkdDcZ44Pr01b_NWef6vidOJRCWMKfH-bqoJszT7tFNpwyJXhC3pkMvup6kcmQ8OdndtDaN96JFppHdjtBLJRlV7yRpHgVsX4roUsI:1t4FLt:zLsBXGLeGDcrhrHovcvGKZy9jFe6BwlXAL5zRqABHQw','2024-11-24 08:07:21.712347'),('mzih0ajel4dnmq4s8qzocxqew8zxqd4z','.eJxVjMEOwiAQRP-FsyFIF1g9eu83kAW2UjWQlPZk_Hdp0oNe5jDvzbyFp23Nfmu8-DmJqziL028XKD657CA9qNyrjLWsyxzkrsiDNjnWxK_b4f4dZGq5rxF0RItaDQgDOaMB0TozaGayFw7JukRacQ8yALFjDDZMwegJnALx-QK1dTci:1t3dFk:mKG2QCyWtP_1on5ube_tyquisHo2-kMda2JVe1LqZA4','2024-11-22 15:26:28.089967'),('oo97rhw001v683s8mlu0mp95b4s9yq49','.eJy1kMFqwzAMht9F55DWju3YvXU9DMbYYFAYjBIUW1lN3bjEzjYoffelIz30AXaUPv2fhM6QovUY0No49rlJGTMlWJ3hdauZeX88GW02xzFIWH2c4TRES2niEOKn76EAhxlh1Y8hFHA6WGpsdNR80eA7T8ON9PSTp9DCYdq3EQe3gEvBam50JbmqSs05q5XcFcDF9nvz9rIOS_aU1PPh39YKY0ohGRda7C4F3B4wK1xDR_ThJmpwzPtmTDQ03k1GxuGu2aI9UH8lGMK1Xc6-8m9mxqlcTxX12VvMPvYPc-pOtZ9unTw1OtMpW2urai20bGtZaSurjki3RtdK0dKwlpbYVhJFZSwKzjrLpO20qSRcfgGaHZw0:1t4DHo:aNrFJRkQ5mG2wHS7t5Ldj2Pluw24klAYP_2-Gxt8_Co','2024-11-24 05:55:00.986339');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_site` (
  `id` int NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'nurojilukmansyah.com','nurojilukmansyah');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_budget`
--

DROP TABLE IF EXISTS `finance_budget`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_budget` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fiscal_year` int NOT NULL,
  `initial_amount` decimal(12,2) NOT NULL,
  `additional_amount` decimal(12,2) NOT NULL,
  `currency_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `finance_budget_currency_id_c81e7c9d_fk_finance_currency_id` (`currency_id`),
  CONSTRAINT `finance_budget_currency_id_c81e7c9d_fk_finance_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `finance_currency` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_budget`
--

LOCK TABLES `finance_budget` WRITE;
/*!40000 ALTER TABLE `finance_budget` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_budget` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_budgetallocation`
--

DROP TABLE IF EXISTS `finance_budgetallocation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_budgetallocation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `category` varchar(100) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `budget_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `finance_budgetallocation_budget_id_daa06115_fk_finance_budget_id` (`budget_id`),
  CONSTRAINT `finance_budgetallocation_budget_id_daa06115_fk_finance_budget_id` FOREIGN KEY (`budget_id`) REFERENCES `finance_budget` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_budgetallocation`
--

LOCK TABLES `finance_budgetallocation` WRITE;
/*!40000 ALTER TABLE `finance_budgetallocation` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_budgetallocation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_currency`
--

DROP TABLE IF EXISTS `finance_currency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_currency` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(3) NOT NULL,
  `name` varchar(50) NOT NULL,
  `symbol` varchar(5) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_currency`
--

LOCK TABLES `finance_currency` WRITE;
/*!40000 ALTER TABLE `finance_currency` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_currency` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_documentproof`
--

DROP TABLE IF EXISTS `finance_documentproof`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_documentproof` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `upload_date` datetime(6) NOT NULL,
  `description` varchar(255) NOT NULL,
  `object_id` int unsigned NOT NULL,
  `content_type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `finance_documentproo_content_type_id_689f0aaf_fk_django_co` (`content_type_id`),
  CONSTRAINT `finance_documentproo_content_type_id_689f0aaf_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `finance_documentproof_chk_1` CHECK ((`object_id` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_documentproof`
--

LOCK TABLES `finance_documentproof` WRITE;
/*!40000 ALTER TABLE `finance_documentproof` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_documentproof` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_exchangerate`
--

DROP TABLE IF EXISTS `finance_exchangerate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_exchangerate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rate` decimal(12,6) NOT NULL,
  `date` date NOT NULL,
  `from_currency_id` bigint NOT NULL,
  `to_currency_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `finance_exchangerate_from_currency_id_to_curr_1dc2256b_uniq` (`from_currency_id`,`to_currency_id`,`date`),
  KEY `finance_exchangerate_to_currency_id_40e7306f_fk_finance_c` (`to_currency_id`),
  CONSTRAINT `finance_exchangerate_from_currency_id_e03d0ac7_fk_finance_c` FOREIGN KEY (`from_currency_id`) REFERENCES `finance_currency` (`id`),
  CONSTRAINT `finance_exchangerate_to_currency_id_40e7306f_fk_finance_c` FOREIGN KEY (`to_currency_id`) REFERENCES `finance_currency` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_exchangerate`
--

LOCK TABLES `finance_exchangerate` WRITE;
/*!40000 ALTER TABLE `finance_exchangerate` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_exchangerate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_grant`
--

DROP TABLE IF EXISTS `finance_grant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_grant` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `currency_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `finance_grant_currency_id_92ee573e_fk_finance_currency_id` (`currency_id`),
  CONSTRAINT `finance_grant_currency_id_92ee573e_fk_finance_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `finance_currency` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_grant`
--

LOCK TABLES `finance_grant` WRITE;
/*!40000 ALTER TABLE `finance_grant` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_grant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_grantexpense`
--

DROP TABLE IF EXISTS `finance_grantexpense`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_grantexpense` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` decimal(12,2) NOT NULL,
  `date` date NOT NULL,
  `grant_id` bigint NOT NULL,
  `description` varchar(255) NOT NULL,
  `document_proof_id` bigint DEFAULT NULL,
  `currency_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `finance_grantexpense_grant_id_1470da26_fk_finance_grant_id` (`grant_id`),
  KEY `finance_grantexpense_document_proof_id_bfef66fd_fk_finance_d` (`document_proof_id`),
  KEY `finance_grantexpense_currency_id_e5ba78bd_fk_finance_currency_id` (`currency_id`),
  CONSTRAINT `finance_grantexpense_currency_id_e5ba78bd_fk_finance_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `finance_currency` (`id`),
  CONSTRAINT `finance_grantexpense_document_proof_id_bfef66fd_fk_finance_d` FOREIGN KEY (`document_proof_id`) REFERENCES `finance_documentproof` (`id`),
  CONSTRAINT `finance_grantexpense_grant_id_1470da26_fk_finance_grant_id` FOREIGN KEY (`grant_id`) REFERENCES `finance_grant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_grantexpense`
--

LOCK TABLES `finance_grantexpense` WRITE;
/*!40000 ALTER TABLE `finance_grantexpense` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_grantexpense` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_journalentry`
--

DROP TABLE IF EXISTS `finance_journalentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_journalentry` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `description` varchar(255) NOT NULL,
  `debit_account` varchar(100) NOT NULL,
  `credit_account` varchar(100) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `object_id` int unsigned DEFAULT NULL,
  `currency_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `finance_journalentry_content_type_id_b1a8ac00_fk_django_co` (`content_type_id`),
  KEY `finance_journalentry_currency_id_ab6aa0bb_fk_finance_currency_id` (`currency_id`),
  CONSTRAINT `finance_journalentry_content_type_id_b1a8ac00_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `finance_journalentry_currency_id_ab6aa0bb_fk_finance_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `finance_currency` (`id`),
  CONSTRAINT `finance_journalentry_chk_1` CHECK ((`object_id` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_journalentry`
--

LOCK TABLES `finance_journalentry` WRITE;
/*!40000 ALTER TABLE `finance_journalentry` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_journalentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_posallocation`
--

DROP TABLE IF EXISTS `finance_posallocation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_posallocation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `budget_id` bigint DEFAULT NULL,
  `grant_id` bigint DEFAULT NULL,
  `currency_id` bigint NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `object_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `finance_posallocation_budget_id_b29c3f09_fk_finance_budget_id` (`budget_id`),
  KEY `finance_posallocation_grant_id_8630d1fd_fk_finance_grant_id` (`grant_id`),
  KEY `finance_posallocatio_currency_id_1f7f02a4_fk_finance_c` (`currency_id`),
  KEY `finance_posallocatio_content_type_id_a1dccccb_fk_django_co` (`content_type_id`),
  CONSTRAINT `finance_posallocatio_content_type_id_a1dccccb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `finance_posallocatio_currency_id_1f7f02a4_fk_finance_c` FOREIGN KEY (`currency_id`) REFERENCES `finance_currency` (`id`),
  CONSTRAINT `finance_posallocation_budget_id_b29c3f09_fk_finance_budget_id` FOREIGN KEY (`budget_id`) REFERENCES `finance_budget` (`id`),
  CONSTRAINT `finance_posallocation_grant_id_8630d1fd_fk_finance_grant_id` FOREIGN KEY (`grant_id`) REFERENCES `finance_grant` (`id`),
  CONSTRAINT `finance_posallocation_chk_1` CHECK ((`object_id` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_posallocation`
--

LOCK TABLES `finance_posallocation` WRITE;
/*!40000 ALTER TABLE `finance_posallocation` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_posallocation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_posexpense`
--

DROP TABLE IF EXISTS `finance_posexpense`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_posexpense` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `description` varchar(255) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `document_proof_id` bigint DEFAULT NULL,
  `pos_allocation_id` bigint NOT NULL,
  `currency_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `finance_posexpense_document_proof_id_5bb5f330_fk_finance_d` (`document_proof_id`),
  KEY `finance_posexpense_pos_allocation_id_49b243e8_fk_finance_p` (`pos_allocation_id`),
  KEY `finance_posexpense_currency_id_da8486fe_fk_finance_currency_id` (`currency_id`),
  CONSTRAINT `finance_posexpense_currency_id_da8486fe_fk_finance_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `finance_currency` (`id`),
  CONSTRAINT `finance_posexpense_document_proof_id_5bb5f330_fk_finance_d` FOREIGN KEY (`document_proof_id`) REFERENCES `finance_documentproof` (`id`),
  CONSTRAINT `finance_posexpense_pos_allocation_id_49b243e8_fk_finance_p` FOREIGN KEY (`pos_allocation_id`) REFERENCES `finance_posallocation` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_posexpense`
--

LOCK TABLES `finance_posexpense` WRITE;
/*!40000 ALTER TABLE `finance_posexpense` DISABLE KEYS */;
/*!40000 ALTER TABLE `finance_posexpense` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `microsoft_auth_microsoftaccount`
--

DROP TABLE IF EXISTS `microsoft_auth_microsoftaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `microsoft_auth_microsoftaccount` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `microsoft_id` varchar(64) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `microsoft_auth_micro_user_id_4377262f_fk_people_cu` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `microsoft_auth_microsoftaccount`
--

LOCK TABLES `microsoft_auth_microsoftaccount` WRITE;
/*!40000 ALTER TABLE `microsoft_auth_microsoftaccount` DISABLE KEYS */;
/*!40000 ALTER TABLE `microsoft_auth_microsoftaccount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `microsoft_auth_xboxliveaccount`
--

DROP TABLE IF EXISTS `microsoft_auth_xboxliveaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `microsoft_auth_xboxliveaccount` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `xbox_id` varchar(32) NOT NULL,
  `gamertag` varchar(16) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `xbox_id` (`xbox_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `microsoft_auth_xboxl_user_id_5581861b_fk_people_cu` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `microsoft_auth_xboxliveaccount`
--

LOCK TABLES `microsoft_auth_xboxliveaccount` WRITE;
/*!40000 ALTER TABLE `microsoft_auth_xboxliveaccount` DISABLE KEYS */;
/*!40000 ALTER TABLE `microsoft_auth_xboxliveaccount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_customuser`
--

DROP TABLE IF EXISTS `people_customuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_customuser` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `user_type` varchar(20) NOT NULL,
  `oauth_refresh_token` longtext,
  `oauth_token` longtext,
  `oauth_token_expiry` datetime(6) DEFAULT NULL,
  `is_email_verified` tinyint(1) NOT NULL,
  `oauth_provider` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `people_customuser_email_82a8c288_uniq` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_customuser`
--

LOCK TABLES `people_customuser` WRITE;
/*!40000 ALTER TABLE `people_customuser` DISABLE KEYS */;
INSERT INTO `people_customuser` VALUES (1,'pbkdf2_sha256$600000$3mcl6LPaTBTk5C31Nr1AwS$lpwcPiikPbqDwCPbs5STOHPIBl+ZVR68/N/rTchUp8Y=','2024-10-24 08:58:05.462636',1,'','','nurojilukmansyah@gmail.com',1,1,'2024-10-17 02:58:33.725260','','1//0go7-fIYd5HoRCgYIARAAGBASNwF-L9Ir-gH0APwpgSGGqt_Emq6WwoO7BABO8gSNwLVIrvy53FjRXJcjEz5TRWqinFtZrZLdzh8','ya29.a0AeDClZDgqgoMMt8ixRZylFLD89JpziHmkfXOb8H1-0s7BOUS4Y1Js4Sm2MPkrtgK4N36UVDzF4hXzWZfF6SB1d1GtTBOge-tl5NTxvWkeZsoUx99recQBcrSj97_RJ7g90S-aB26S2Z_z05Z9fcoaRxxwqliVulzvgXvS1h8aCgYKAW8SARASFQHGX2MiwEoUPvleJO_Cp7NE7Ge0tQ0175','2024-10-24 09:58:04.125598',0,'google'),(2,'!yE5NsmAWJ6JvyhXKYs1RQ0jtG066jFo9VtAC0lp3','2024-10-24 08:34:28.924057',1,'Nuroji','Lukmansyah','dev.csis.id@gmail.com',1,1,'2024-10-22 17:01:24.820009','staff','1//0gr7b88nuJYw-CgYIARAAGBASNwF-L9IrifC41U_oaN9H6sZ8SN7SVMcqChGoEha6H-7fIelG_EIKd1qC3Os0muCpAehdxSeIDBU','ya29.a0AeDClZBBybkJfwajyzwfOPpJPKSUIgi_Yk5VHNPpcOfGukjqMI8g5sJxhcdG6Js8cTWK3FnMHjh5WzMVPsN-o94qoVV1ySxLyCFX9DiiAPZVJbNtB9hm4zPAlgAzcZpZ_FItghMBS1w7tAyxiZuaMfONLIIOGc9gGwfndX_raCgYKAbgSARASFQHGX2Mi8Rp4iX-2QcA6zoRToYdY4Q0175','2024-10-24 09:34:27.842344',0,'google'),(9,'!ReFWnsN7KDDpG4jHy4NgF6GVpsA2Sl40yzBNGMjG','2024-10-24 06:57:47.040305',1,'nuroji','lukmansyah','nurojilukmansyah2@gmail.com',1,1,'2024-10-24 04:20:13.555327','visitor','1//0gk889H_LD3WGCgYIARAAGBASNwF-L9IrnEqJfwekxMzCwa8N-zhCP39wjmMdy6lGTJ63PyX9kxqEwK5XGTLfYYXqcLsVBpXHXMs','ya29.a0AeDClZC0KSteVHMIkRp-yAt4v8szelM30V-NbfNvxZFd2PHQkcjCtLmsPZoLu4oj_U958ZMo1RHX6G3lpMzMSRsL7WJWSE9jfOSLMUUhCdIWROD4x-AZ9W40fHrV3HS9SSZSQ1EXTTR4eZZ7BEet5kNz2NvE8vP0Gh4yWicfaCgYKAY0SARESFQHGX2MiROpvFWsnZLRJeQp6o0SJ3Q0175','2024-10-24 07:57:45.000000',1,'google'),(10,'!WVaXV16YRnmLDx0OrxbvnHrVLPlRZgMlklStaNGL','2024-10-24 06:39:07.448728',0,'Nafiza Suci','Azzahri','zahry04@gmail.com',1,1,'2024-10-24 06:39:07.221688','visitor','1//0gmLheg_PW3BPCgYIARAAGBASNwF-L9IrobCgWX-U6WIrt-f2TuSj-Y5xlcd2or7wWHMv7GGO6j6yI7NtmpzWYnzYtIGsibSfIwA','ya29.a0AeDClZARmlQQlOcXJIbAu4O5HE01lfajRQGL36yGPFg-jymeNkZHHxBxlqVlbBH1rNRg3iEN6nn8NtNixPOVycxxVXIISCEWjDUBuw4iYiMLnwvzRNQ74DhxqLEB1iitEFTL-w1WIRs1ynPVQ8JO_lVy-ar8Q6aOmKt36lFZaCgYKAQgSARASFQHGX2MiaOxq64B48PudDB05EG2okw0175','2024-10-24 07:39:06.000000',1,'google'),(11,'!xkcZx3XkfsjCoZ1Oq62IPrjfp0GElohKK8r3fQ5n','2024-10-25 05:29:51.706861',0,'Tachika','Altaira','tachikaaltaira@gmail.com',0,1,'2024-10-25 05:29:51.613916','visitor','1//0gWm0P4IYbqAOCgYIARAAGBASNwF-L9IrdZX587PSKbQv71_kIEXpzwGXjpSq_5JVF3BiFuvv0IXLtH7LdJW08EJQDhsM78ncmzE','ya29.a0AeDClZBz8D0zswBZA7EfKZiTIBx5dl8jUd749e7R3ovT4UIgxtpbpxwPx-RjdEykyLlVbU-3KqypwozIp116G4UgzO2UEyis1HbjTa8mwDajYFNHeOeSFJ8SeP2Rwy29o0wx0dAJlf_prRdgwIT4Zc7AO9btrzHGQZZhTyOqaCgYKAdQSARASFQHGX2MiIXjL136jLd4thuS87OFrYQ0175','2024-10-25 06:29:50.610661',1,'google'),(12,'!WDrmMIqAp0N0idipkOsyNeHUhZWJHQjtyqa5wLSs','2024-10-25 05:55:00.980951',0,'fo','kcbb','fokcbb@gmail.com',1,1,'2024-10-25 05:55:00.932391','staff','1//0gXLmFj_97xssCgYIARAAGBASNwF-L9Ire77m7vQrJPp9n6RQUxd8w6hSQzh5zMsv0NBwf4HaIS4EnTO_a8Q-0X23a7VnznhJW1o','ya29.a0AeDClZCacaMdCcXO42pc6uoBDVJAHc8RMn8koXy9q_OasnMPrOd19Mid0JLH0qqmLFyQQGscLcJ4uZ3JkoYoHdJS24Tbjh5iYf2UGuR41lt0ilceGjIRM7gRv6gnJJcs5FHeo7OLJzMsOSCIuq9SWit70iXDXpz6JKIj6r-DaCgYKAbsSARASFQHGX2Mixj_a0JGXqrtgmc7UGo73RA0175','2024-10-25 06:54:59.000000',1,'google'),(13,'!KS3voX0MbnqAFtIukyY185ULHY3viBz7AjnxlUlf','2024-10-25 07:17:11.616624',0,'niela12','mahillah','niela12mahillah@gmail.com',0,1,'2024-10-25 07:17:11.547455','visitor','1//0gsIpkYJbL1-_CgYIARAAGBASNwF-L9IrZGAYkA7ZhR5zxGEKE-L8FWPCaopTWodfOMUOlurFotPtiS_YJ666QcsmBMha5eMw7x0','ya29.a0AeDClZBYgpMp-ccU8o0GwZhK1kYmp5qu3jhZXMl2Br1DjenP_UZvAF9io6vOLBtONSCflRv4iyQcoakZYpE1Ff-YaVxctTYGavg7MTWgEV__tx1byO33MGvUM_mLUBojc5B1vpAcGeIo9vVd3SZTowAI1AEXDI53cM0D44fvaCgYKAWMSARMSFQHGX2MiNnAtn0Cfb-4s7917IgxHCw0175','2024-10-25 08:17:10.544569',1,'google'),(14,'!rpQXXN2Zq8lvyWkRdpAfoYNJUMXZxzAdTjLdQBBf','2024-10-25 08:07:21.703846',0,'Vicky','Farahani','vickyfarahani0104@gmail.com',0,1,'2024-10-25 08:07:21.621919','visitor','1//0gSvuuXLU5ngGCgYIARAAGBASNwF-L9IrUVhxxEgx6lE6E0BVR7F7KMfm1MRCA1z_TRjfHDWi2a_V562diJgbTyRoDV4R4dnGLfM','ya29.a0AcM612wTl7mnQCTcTCNHWEMHrgbJ3uzjHGJhZlPND5_nvlaIgopNui0aTNfUYSYz0gYteurZgo4KP-rVWsby2m1DkKTVfG3V-0lokTS5cPyIauBO3am96Rf2rpxEr3O0mXtVHZaH5do5JSQpC1FkLGy-8fUgMkszhEKxCuftaCgYKAYMSARESFQHGX2MiG9m45hAFtvDgXDQehE6HuQ0175','2024-10-25 09:07:20.617977',1,'google');
/*!40000 ALTER TABLE `people_customuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_customuser_groups`
--

DROP TABLE IF EXISTS `people_customuser_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_customuser_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `people_customuser_groups_customuser_id_group_id_66a351b8_uniq` (`customuser_id`,`group_id`),
  KEY `people_customuser_groups_group_id_1adc6231_fk_auth_group_id` (`group_id`),
  CONSTRAINT `people_customuser_gr_customuser_id_99fd5cd1_fk_people_cu` FOREIGN KEY (`customuser_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `people_customuser_groups_group_id_1adc6231_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_customuser_groups`
--

LOCK TABLES `people_customuser_groups` WRITE;
/*!40000 ALTER TABLE `people_customuser_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `people_customuser_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_customuser_user_permissions`
--

DROP TABLE IF EXISTS `people_customuser_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_customuser_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `people_customuser_user_p_customuser_id_permission_c7164069_uniq` (`customuser_id`,`permission_id`),
  KEY `people_customuser_us_permission_id_883d8025_fk_auth_perm` (`permission_id`),
  CONSTRAINT `people_customuser_us_customuser_id_04e9246e_fk_people_cu` FOREIGN KEY (`customuser_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `people_customuser_us_permission_id_883d8025_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_customuser_user_permissions`
--

LOCK TABLES `people_customuser_user_permissions` WRITE;
/*!40000 ALTER TABLE `people_customuser_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `people_customuser_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_organization`
--

DROP TABLE IF EXISTS `people_organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_organization` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `logo` varchar(100) DEFAULT NULL,
  `description` longtext,
  `publish` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_organization`
--

LOCK TABLES `people_organization` WRITE;
/*!40000 ALTER TABLE `people_organization` DISABLE KEYS */;
/*!40000 ALTER TABLE `people_organization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_person`
--

DROP TABLE IF EXISTS `people_person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_person` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `image` varchar(100) DEFAULT NULL,
  `email` varchar(254) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `address` longtext NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `people_person_user_id_6381a4ab_fk_people_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_person`
--

LOCK TABLES `people_person` WRITE;
/*!40000 ALTER TABLE `people_person` DISABLE KEYS */;
INSERT INTO `people_person` VALUES (1,'asasa','asasa','2024-10-23','people/2024/10/23/Gita.jpeg','dev@csis.or.id','','',1);
/*!40000 ALTER TABLE `people_person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_photo`
--

DROP TABLE IF EXISTS `people_photo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_photo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `google_photo_id` varchar(500) NOT NULL,
  `filename` varchar(500) NOT NULL,
  `original_url` longtext NOT NULL,
  `mime_type` varchar(100) NOT NULL,
  `created_time` datetime(6) DEFAULT NULL,
  `downloaded_at` datetime(6) NOT NULL,
  `photo_file` varchar(100) NOT NULL,
  `metadata` json NOT NULL,
  `backup_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `people_photo_backup_id_google_photo_id_3c6d9fa6_uniq` (`backup_id`,`google_photo_id`),
  CONSTRAINT `people_photo_backup_id_1d73624b_fk_people_photobackup_id` FOREIGN KEY (`backup_id`) REFERENCES `people_photobackup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10798 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_photo`
--

LOCK TABLES `people_photo` WRITE;
/*!40000 ALTER TABLE `people_photo` DISABLE KEYS */;
/*!40000 ALTER TABLE `people_photo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_photobackup`
--

DROP TABLE IF EXISTS `people_photobackup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_photobackup` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `total_photos` int NOT NULL,
  `status` varchar(20) NOT NULL,
  `error_message` longtext,
  `user_id` bigint NOT NULL,
  `photos_limit` int NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `people_photobackup_user_id_7ee57931_fk_people_customuser_id` (`user_id`),
  CONSTRAINT `people_photobackup_user_id_7ee57931_fk_people_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_photobackup`
--

LOCK TABLES `people_photobackup` WRITE;
/*!40000 ALTER TABLE `people_photobackup` DISABLE KEYS */;
/*!40000 ALTER TABLE `people_photobackup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_relationship`
--

DROP TABLE IF EXISTS `people_relationship`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_relationship` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `relationship_type` varchar(20) NOT NULL,
  `kontak_darurat` tinyint(1) NOT NULL,
  `person_id` bigint NOT NULL,
  `related_person_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `people_relationship_person_id_37b60c82_fk_people_person_id` (`person_id`),
  KEY `people_relationship_related_person_id_8274b84c_fk_people_pe` (`related_person_id`),
  CONSTRAINT `people_relationship_person_id_37b60c82_fk_people_person_id` FOREIGN KEY (`person_id`) REFERENCES `people_person` (`id`),
  CONSTRAINT `people_relationship_related_person_id_8274b84c_fk_people_pe` FOREIGN KEY (`related_person_id`) REFERENCES `people_person` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_relationship`
--

LOCK TABLES `people_relationship` WRITE;
/*!40000 ALTER TABLE `people_relationship` DISABLE KEYS */;
/*!40000 ALTER TABLE `people_relationship` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_speaker`
--

DROP TABLE IF EXISTS `people_speaker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_speaker` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bio` longtext NOT NULL,
  `areas_of_expertise` varchar(255) NOT NULL,
  `speaking_fee` decimal(10,2) DEFAULT NULL,
  `organization_id` bigint DEFAULT NULL,
  `person_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `person_id` (`person_id`),
  KEY `people_speaker_organization_id_8bfd4d96_fk_people_or` (`organization_id`),
  CONSTRAINT `people_speaker_organization_id_8bfd4d96_fk_people_or` FOREIGN KEY (`organization_id`) REFERENCES `people_organization` (`id`),
  CONSTRAINT `people_speaker_person_id_c32389ba_fk_people_person_id` FOREIGN KEY (`person_id`) REFERENCES `people_person` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_speaker`
--

LOCK TABLES `people_speaker` WRITE;
/*!40000 ALTER TABLE `people_speaker` DISABLE KEYS */;
/*!40000 ALTER TABLE `people_speaker` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_staff`
--

DROP TABLE IF EXISTS `people_staff`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_staff` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `employee_id` varchar(20) NOT NULL,
  `department` varchar(100) NOT NULL,
  `position` varchar(100) NOT NULL,
  `hire_date` date NOT NULL,
  `person_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_id` (`employee_id`),
  UNIQUE KEY `person_id` (`person_id`),
  CONSTRAINT `people_staff_person_id_b7069ffe_fk_people_person_id` FOREIGN KEY (`person_id`) REFERENCES `people_person` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_staff`
--

LOCK TABLES `people_staff` WRITE;
/*!40000 ALTER TABLE `people_staff` DISABLE KEYS */;
/*!40000 ALTER TABLE `people_staff` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `people_writer`
--

DROP TABLE IF EXISTS `people_writer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `people_writer` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `genre` varchar(100) NOT NULL,
  `publications` longtext NOT NULL,
  `organization_id` bigint DEFAULT NULL,
  `person_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `person_id` (`person_id`),
  KEY `people_writer_organization_id_3997d686_fk_people_organization_id` (`organization_id`),
  CONSTRAINT `people_writer_organization_id_3997d686_fk_people_organization_id` FOREIGN KEY (`organization_id`) REFERENCES `people_organization` (`id`),
  CONSTRAINT `people_writer_person_id_14f020dd_fk_people_person_id` FOREIGN KEY (`person_id`) REFERENCES `people_person` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `people_writer`
--

LOCK TABLES `people_writer` WRITE;
/*!40000 ALTER TABLE `people_writer` DISABLE KEYS */;
/*!40000 ALTER TABLE `people_writer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_event`
--

DROP TABLE IF EXISTS `project_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_event` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `event_type` varchar(20) NOT NULL,
  `date` datetime(6) NOT NULL,
  `location` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `target_audience` varchar(255) NOT NULL,
  `expected_participants` int unsigned NOT NULL,
  `actual_participants` int unsigned DEFAULT NULL,
  `pos_allocation_id` bigint DEFAULT NULL,
  `project_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_event_pos_allocation_id_3c72e8ed_fk_finance_p` (`pos_allocation_id`),
  KEY `project_event_project_id_fd293270_fk_project_project_id` (`project_id`),
  CONSTRAINT `project_event_pos_allocation_id_3c72e8ed_fk_finance_p` FOREIGN KEY (`pos_allocation_id`) REFERENCES `finance_posallocation` (`id`),
  CONSTRAINT `project_event_project_id_fd293270_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_event_chk_1` CHECK ((`expected_participants` >= 0)),
  CONSTRAINT `project_event_chk_2` CHECK ((`actual_participants` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_event`
--

LOCK TABLES `project_event` WRITE;
/*!40000 ALTER TABLE `project_event` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_event_organizers`
--

DROP TABLE IF EXISTS `project_event_organizers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_event_organizers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_id` bigint NOT NULL,
  `customuser_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_event_organizers_event_id_customuser_id_072c5575_uniq` (`event_id`,`customuser_id`),
  KEY `project_event_organi_customuser_id_58ba2a7c_fk_people_cu` (`customuser_id`),
  CONSTRAINT `project_event_organi_customuser_id_58ba2a7c_fk_people_cu` FOREIGN KEY (`customuser_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `project_event_organizers_event_id_b867297b_fk_project_event_id` FOREIGN KEY (`event_id`) REFERENCES `project_event` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_event_organizers`
--

LOCK TABLES `project_event_organizers` WRITE;
/*!40000 ALTER TABLE `project_event_organizers` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_event_organizers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_grantreport`
--

DROP TABLE IF EXISTS `project_grantreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_grantreport` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `narrative` longtext NOT NULL,
  `financial_report` varchar(100) NOT NULL,
  `approved` tinyint(1) NOT NULL,
  `submitted_by_id` bigint DEFAULT NULL,
  `project_grant_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `project_grantreport_submitted_by_id_029d0c13_fk_people_cu` (`submitted_by_id`),
  KEY `project_grantreport_project_grant_id_85f28c6d_fk_project_p` (`project_grant_id`),
  CONSTRAINT `project_grantreport_project_grant_id_85f28c6d_fk_project_p` FOREIGN KEY (`project_grant_id`) REFERENCES `project_projectgrant` (`id`),
  CONSTRAINT `project_grantreport_submitted_by_id_029d0c13_fk_people_cu` FOREIGN KEY (`submitted_by_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_grantreport`
--

LOCK TABLES `project_grantreport` WRITE;
/*!40000 ALTER TABLE `project_grantreport` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_grantreport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_progress`
--

DROP TABLE IF EXISTS `project_progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_progress` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `progress_type` varchar(20) NOT NULL,
  `description` longtext NOT NULL,
  `due_date` date NOT NULL,
  `completion_date` date DEFAULT NULL,
  `status` smallint unsigned NOT NULL,
  `notes` longtext NOT NULL,
  `attachments` varchar(100) DEFAULT NULL,
  `responsible_person_id` bigint DEFAULT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `project_progress_responsible_person_i_2561e8d9_fk_people_cu` (`responsible_person_id`),
  KEY `project_progress_project_id_c9b0d403_fk_project_project_id` (`project_id`),
  CONSTRAINT `project_progress_project_id_c9b0d403_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_progress_responsible_person_i_2561e8d9_fk_people_cu` FOREIGN KEY (`responsible_person_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `project_progress_chk_1` CHECK ((`status` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_progress`
--

LOCK TABLES `project_progress` WRITE;
/*!40000 ALTER TABLE `project_progress` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_progress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_project`
--

DROP TABLE IF EXISTS `project_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_project` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `budget_id` bigint DEFAULT NULL,
  `currency_id` bigint DEFAULT NULL,
  `project_manager_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_project_budget_id_2f77e4da_fk_finance_budget_id` (`budget_id`),
  KEY `project_project_currency_id_0445783f_fk_finance_currency_id` (`currency_id`),
  KEY `project_project_project_manager_id_8f8a9b66_fk_people_cu` (`project_manager_id`),
  CONSTRAINT `project_project_budget_id_2f77e4da_fk_finance_budget_id` FOREIGN KEY (`budget_id`) REFERENCES `finance_budget` (`id`),
  CONSTRAINT `project_project_currency_id_0445783f_fk_finance_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `finance_currency` (`id`),
  CONSTRAINT `project_project_project_manager_id_8f8a9b66_fk_people_cu` FOREIGN KEY (`project_manager_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_project`
--

LOCK TABLES `project_project` WRITE;
/*!40000 ALTER TABLE `project_project` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_projectgrant`
--

DROP TABLE IF EXISTS `project_projectgrant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_projectgrant` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `status` varchar(20) NOT NULL,
  `submission_deadline` date NOT NULL,
  `requirements` longtext NOT NULL,
  `reporting_frequency` varchar(50) NOT NULL,
  `grant_id` bigint NOT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `grant_id` (`grant_id`),
  KEY `project_projectgrant_project_id_0cdad750_fk_project_project_id` (`project_id`),
  CONSTRAINT `project_projectgrant_grant_id_594ba7ba_fk_finance_grant_id` FOREIGN KEY (`grant_id`) REFERENCES `finance_grant` (`id`),
  CONSTRAINT `project_projectgrant_project_id_0cdad750_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_projectgrant`
--

LOCK TABLES `project_projectgrant` WRITE;
/*!40000 ALTER TABLE `project_projectgrant` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_projectgrant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_projectmember`
--

DROP TABLE IF EXISTS `project_projectmember`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_projectmember` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(20) NOT NULL,
  `join_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `time_commitment` int unsigned NOT NULL,
  `member_id` bigint NOT NULL,
  `pos_allocation_id` bigint DEFAULT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_projectmember_project_id_member_id_f43ebef2_uniq` (`project_id`,`member_id`),
  KEY `project_projectmember_member_id_668b7906_fk_people_customuser_id` (`member_id`),
  KEY `project_projectmembe_pos_allocation_id_39494bab_fk_finance_p` (`pos_allocation_id`),
  CONSTRAINT `project_projectmembe_pos_allocation_id_39494bab_fk_finance_p` FOREIGN KEY (`pos_allocation_id`) REFERENCES `finance_posallocation` (`id`),
  CONSTRAINT `project_projectmember_member_id_668b7906_fk_people_customuser_id` FOREIGN KEY (`member_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `project_projectmember_project_id_8b722a5e_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_projectmember_chk_1` CHECK ((`time_commitment` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_projectmember`
--

LOCK TABLES `project_projectmember` WRITE;
/*!40000 ALTER TABLE `project_projectmember` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_projectmember` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_publication`
--

DROP TABLE IF EXISTS `project_publication`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_publication` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `publication_type` varchar(20) NOT NULL,
  `publisher` varchar(255) NOT NULL,
  `publication_date` date NOT NULL,
  `doi` varchar(255) DEFAULT NULL,
  `url` varchar(200) DEFAULT NULL,
  `citation` longtext NOT NULL,
  `abstract` longtext NOT NULL,
  `pos_allocation_id` bigint DEFAULT NULL,
  `project_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_publication_pos_allocation_id_6f0f30d3_fk_finance_p` (`pos_allocation_id`),
  KEY `project_publication_project_id_998ac7e5_fk_project_project_id` (`project_id`),
  CONSTRAINT `project_publication_pos_allocation_id_6f0f30d3_fk_finance_p` FOREIGN KEY (`pos_allocation_id`) REFERENCES `finance_posallocation` (`id`),
  CONSTRAINT `project_publication_project_id_998ac7e5_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_publication`
--

LOCK TABLES `project_publication` WRITE;
/*!40000 ALTER TABLE `project_publication` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_publication` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_publication_authors`
--

DROP TABLE IF EXISTS `project_publication_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_publication_authors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `publication_id` bigint NOT NULL,
  `customuser_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_publication_auth_publication_id_customuse_4d0c3aa1_uniq` (`publication_id`,`customuser_id`),
  KEY `project_publication__customuser_id_ee97ff99_fk_people_cu` (`customuser_id`),
  CONSTRAINT `project_publication__customuser_id_ee97ff99_fk_people_cu` FOREIGN KEY (`customuser_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `project_publication__publication_id_dff8c43e_fk_project_p` FOREIGN KEY (`publication_id`) REFERENCES `project_publication` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_publication_authors`
--

LOCK TABLES `project_publication_authors` WRITE;
/*!40000 ALTER TABLE `project_publication_authors` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_publication_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_researchdata`
--

DROP TABLE IF EXISTS `project_researchdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_researchdata` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `data_type` varchar(20) NOT NULL,
  `collection_date` date NOT NULL,
  `description` longtext NOT NULL,
  `methodology` longtext NOT NULL,
  `storage_location` varchar(255) NOT NULL,
  `file` varchar(100) NOT NULL,
  `metadata` json NOT NULL,
  `pos_allocation_id` bigint DEFAULT NULL,
  `project_id` bigint NOT NULL,
  `responsible_person_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_researchdata_pos_allocation_id_4a9bb98f_fk_finance_p` (`pos_allocation_id`),
  KEY `project_researchdata_project_id_7eff2bbc_fk_project_project_id` (`project_id`),
  KEY `project_researchdata_responsible_person_i_223ee70b_fk_people_cu` (`responsible_person_id`),
  CONSTRAINT `project_researchdata_pos_allocation_id_4a9bb98f_fk_finance_p` FOREIGN KEY (`pos_allocation_id`) REFERENCES `finance_posallocation` (`id`),
  CONSTRAINT `project_researchdata_project_id_7eff2bbc_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_researchdata_responsible_person_i_223ee70b_fk_people_cu` FOREIGN KEY (`responsible_person_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_researchdata`
--

LOCK TABLES `project_researchdata` WRITE;
/*!40000 ALTER TABLE `project_researchdata` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_researchdata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialaccount`
--

DROP TABLE IF EXISTS `socialaccount_socialaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialaccount` (
  `id` int NOT NULL AUTO_INCREMENT,
  `provider` varchar(200) NOT NULL,
  `uid` varchar(191) NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `extra_data` json NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialaccount_provider_uid_fc810c6e_uniq` (`provider`,`uid`),
  KEY `socialaccount_social_user_id_8146e70c_fk_people_cu` (`user_id`),
  CONSTRAINT `socialaccount_social_user_id_8146e70c_fk_people_cu` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialaccount`
--

LOCK TABLES `socialaccount_socialaccount` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialaccount` DISABLE KEYS */;
INSERT INTO `socialaccount_socialaccount` VALUES (1,'google','104622456360367688369','2024-10-24 08:34:28.861399','2024-10-22 17:01:24.835094','{\"aud\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"azp\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"exp\": 1729762468, \"iat\": 1729758868, \"iss\": \"https://accounts.google.com\", \"sub\": \"104622456360367688369\", \"name\": \"Nuroji Lukmansyah\", \"email\": \"dev.csis.id@gmail.com\", \"at_hash\": \"FjX9NkjSm9bQLVPUSbSehw\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocLl5F_kDnxQllZxOf6jztCUF-moNs-IMsblqX6k4FbMQVHZfw=s96-c\", \"given_name\": \"Nuroji\", \"family_name\": \"Lukmansyah\", \"email_verified\": true}',2),(2,'google','107618889601228385959','2024-10-24 08:58:05.161798','2024-10-22 17:03:28.630688','{\"aud\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"azp\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"exp\": 1729763885, \"iat\": 1729760285, \"iss\": \"https://accounts.google.com\", \"sub\": \"107618889601228385959\", \"name\": \"nuroji lukmansyah\", \"email\": \"nurojilukmansyah@gmail.com\", \"at_hash\": \"gNreWlKiH6N-G-I-HoMBiA\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocJQ1fGvpEt6H-l-INgRChy9bnYtUqPDDf6-jxh7DYp_GveCNwf9=s96-c\", \"given_name\": \"nuroji\", \"family_name\": \"lukmansyah\", \"email_verified\": true}',1),(3,'google','116780108639195704866','2024-10-24 06:57:46.980881','2024-10-24 04:20:13.581244','{\"aud\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"azp\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"exp\": 1729756666, \"iat\": 1729753066, \"iss\": \"https://accounts.google.com\", \"sub\": \"116780108639195704866\", \"name\": \"nuroji lukmansyah\", \"email\": \"nurojilukmansyah2@gmail.com\", \"at_hash\": \"6C7GpXXg1uiiXdrdKDEMWA\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocJ8xp_kb0jw7l1W1SAf0pYkWBoYCUOvNT4oNTRlOojmSpWOAQ=s96-c\", \"given_name\": \"nuroji\", \"family_name\": \"lukmansyah\", \"email_verified\": true}',9),(4,'google','104699856066131714908','2024-10-24 06:39:07.287765','2024-10-24 06:39:07.287887','{\"aud\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"azp\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"exp\": 1729755547, \"iat\": 1729751947, \"iss\": \"https://accounts.google.com\", \"sub\": \"104699856066131714908\", \"name\": \"Nafiza Suci Azzahri\", \"email\": \"zahry04@gmail.com\", \"at_hash\": \"n9X7Ju49E6UbnSlnCvOGOA\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocJ50TGrf7PA2Lj0JcLSkm-yXz7RopO_nwDTWNJimWwTZ_N4Jw=s96-c\", \"given_name\": \"Nafiza Suci\", \"family_name\": \"Azzahri\", \"email_verified\": true}',10),(5,'google','109701079060083924163','2024-10-25 05:29:51.638554','2024-10-25 05:29:51.638594','{\"aud\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"azp\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"exp\": 1729837791, \"iat\": 1729834191, \"iss\": \"https://accounts.google.com\", \"sub\": \"109701079060083924163\", \"name\": \"Tachika Altaira\", \"email\": \"tachikaaltaira@gmail.com\", \"at_hash\": \"mViDp5ijw9i7hVquDXlzvA\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocLgqMb26vqEZgKSHAbxLemZrQgA9U3xlJBcRxEAqUqDKdwRoY08=s96-c\", \"given_name\": \"Tachika\", \"family_name\": \"Altaira\", \"email_verified\": true}',11),(6,'google','101763863225671280900','2024-10-25 05:55:00.952973','2024-10-25 05:55:00.953011','{\"aud\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"azp\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"exp\": 1729839300, \"iat\": 1729835700, \"iss\": \"https://accounts.google.com\", \"sub\": \"101763863225671280900\", \"name\": \"fo kcbb\", \"email\": \"fokcbb@gmail.com\", \"at_hash\": \"csMLO4bY3TwmpS0caMKzOA\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocLRlmzZdfJP3NGHmfaQLOEu9w4R1ZqgEVTx4daBV502dOp2zMk=s96-c\", \"given_name\": \"fo\", \"family_name\": \"kcbb\", \"email_verified\": true}',12),(7,'google','101323380351854142391','2024-10-25 07:17:11.573681','2024-10-25 07:17:11.573727','{\"aud\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"azp\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"exp\": 1729844231, \"iat\": 1729840631, \"iss\": \"https://accounts.google.com\", \"sub\": \"101323380351854142391\", \"name\": \"niela12 mahillah\", \"email\": \"niela12mahillah@gmail.com\", \"at_hash\": \"IuxuUJyjs-AYlcswt1YBUQ\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocIBeYUzr4Jl27xFroiCroPv-5iRbpU4qJek219aEba-E9ys7Q=s96-c\", \"given_name\": \"niela12\", \"family_name\": \"mahillah\", \"email_verified\": true}',13),(8,'google','116354671838063004882','2024-10-25 08:07:21.654021','2024-10-25 08:07:21.654114','{\"aud\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"azp\": \"345346541837-dqookjqqlnj956ngnpqbep305tb8rpup.apps.googleusercontent.com\", \"exp\": 1729847241, \"iat\": 1729843641, \"iss\": \"https://accounts.google.com\", \"sub\": \"116354671838063004882\", \"name\": \"Vicky Farahani\", \"email\": \"vickyfarahani0104@gmail.com\", \"at_hash\": \"Ppr8j0coj7KSl1SAC38rVw\", \"picture\": \"https://lh3.googleusercontent.com/a/ACg8ocIcloaVdv1dhBH7zt45NGIT4L0sOzm-7IiB5Smvdq4r27wqt4vK=s96-c\", \"given_name\": \"Vicky\", \"family_name\": \"Farahani\", \"email_verified\": true}',14);
/*!40000 ALTER TABLE `socialaccount_socialaccount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialapp`
--

DROP TABLE IF EXISTS `socialaccount_socialapp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialapp` (
  `id` int NOT NULL AUTO_INCREMENT,
  `provider` varchar(30) NOT NULL,
  `name` varchar(40) NOT NULL,
  `client_id` varchar(191) NOT NULL,
  `secret` varchar(191) NOT NULL,
  `key` varchar(191) NOT NULL,
  `provider_id` varchar(200) NOT NULL,
  `settings` json NOT NULL DEFAULT (_utf8mb3'{}'),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialapp`
--

LOCK TABLES `socialaccount_socialapp` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialapp` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialapp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialapp_sites`
--

DROP TABLE IF EXISTS `socialaccount_socialapp_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialapp_sites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `socialapp_id` int NOT NULL,
  `site_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialapp_sites_socialapp_id_site_id_71a9a768_uniq` (`socialapp_id`,`site_id`),
  KEY `socialaccount_socialapp_sites_site_id_2579dee5_fk_django_site_id` (`site_id`),
  CONSTRAINT `socialaccount_social_socialapp_id_97fb6e7d_fk_socialacc` FOREIGN KEY (`socialapp_id`) REFERENCES `socialaccount_socialapp` (`id`),
  CONSTRAINT `socialaccount_socialapp_sites_site_id_2579dee5_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialapp_sites`
--

LOCK TABLES `socialaccount_socialapp_sites` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialapp_sites` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialapp_sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialtoken`
--

DROP TABLE IF EXISTS `socialaccount_socialtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialtoken` (
  `id` int NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `token_secret` longtext NOT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `account_id` int NOT NULL,
  `app_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq` (`app_id`,`account_id`),
  KEY `socialaccount_social_account_id_951f210e_fk_socialacc` (`account_id`),
  CONSTRAINT `socialaccount_social_account_id_951f210e_fk_socialacc` FOREIGN KEY (`account_id`) REFERENCES `socialaccount_socialaccount` (`id`),
  CONSTRAINT `socialaccount_social_app_id_636a42d7_fk_socialacc` FOREIGN KEY (`app_id`) REFERENCES `socialaccount_socialapp` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialtoken`
--

LOCK TABLES `socialaccount_socialtoken` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialtoken` DISABLE KEYS */;
INSERT INTO `socialaccount_socialtoken` VALUES (1,'ya29.a0AeDClZBBybkJfwajyzwfOPpJPKSUIgi_Yk5VHNPpcOfGukjqMI8g5sJxhcdG6Js8cTWK3FnMHjh5WzMVPsN-o94qoVV1ySxLyCFX9DiiAPZVJbNtB9hm4zPAlgAzcZpZ_FItghMBS1w7tAyxiZuaMfONLIIOGc9gGwfndX_raCgYKAbgSARASFQHGX2Mi8Rp4iX-2QcA6zoRToYdY4Q0175','1//0gr7b88nuJYw-CgYIARAAGBASNwF-L9IrifC41U_oaN9H6sZ8SN7SVMcqChGoEha6H-7fIelG_EIKd1qC3Os0muCpAehdxSeIDBU','2024-10-24 09:34:27.842344',1,NULL),(2,'ya29.a0AeDClZDgqgoMMt8ixRZylFLD89JpziHmkfXOb8H1-0s7BOUS4Y1Js4Sm2MPkrtgK4N36UVDzF4hXzWZfF6SB1d1GtTBOge-tl5NTxvWkeZsoUx99recQBcrSj97_RJ7g90S-aB26S2Z_z05Z9fcoaRxxwqliVulzvgXvS1h8aCgYKAW8SARASFQHGX2MiwEoUPvleJO_Cp7NE7Ge0tQ0175','1//0go7-fIYd5HoRCgYIARAAGBASNwF-L9Ir-gH0APwpgSGGqt_Emq6WwoO7BABO8gSNwLVIrvy53FjRXJcjEz5TRWqinFtZrZLdzh8','2024-10-24 09:58:04.125598',2,NULL),(3,'ya29.a0AeDClZC0KSteVHMIkRp-yAt4v8szelM30V-NbfNvxZFd2PHQkcjCtLmsPZoLu4oj_U958ZMo1RHX6G3lpMzMSRsL7WJWSE9jfOSLMUUhCdIWROD4x-AZ9W40fHrV3HS9SSZSQ1EXTTR4eZZ7BEet5kNz2NvE8vP0Gh4yWicfaCgYKAY0SARESFQHGX2MiROpvFWsnZLRJeQp6o0SJ3Q0175','1//0gk889H_LD3WGCgYIARAAGBASNwF-L9IrnEqJfwekxMzCwa8N-zhCP39wjmMdy6lGTJ63PyX9kxqEwK5XGTLfYYXqcLsVBpXHXMs','2024-10-24 07:57:45.966125',3,NULL),(4,'ya29.a0AeDClZARmlQQlOcXJIbAu4O5HE01lfajRQGL36yGPFg-jymeNkZHHxBxlqVlbBH1rNRg3iEN6nn8NtNixPOVycxxVXIISCEWjDUBuw4iYiMLnwvzRNQ74DhxqLEB1iitEFTL-w1WIRs1ynPVQ8JO_lVy-ar8Q6aOmKt36lFZaCgYKAQgSARASFQHGX2MiaOxq64B48PudDB05EG2okw0175','1//0gmLheg_PW3BPCgYIARAAGBASNwF-L9IrobCgWX-U6WIrt-f2TuSj-Y5xlcd2or7wWHMv7GGO6j6yI7NtmpzWYnzYtIGsibSfIwA','2024-10-24 07:39:06.211676',4,NULL),(5,'ya29.a0AeDClZBz8D0zswBZA7EfKZiTIBx5dl8jUd749e7R3ovT4UIgxtpbpxwPx-RjdEykyLlVbU-3KqypwozIp116G4UgzO2UEyis1HbjTa8mwDajYFNHeOeSFJ8SeP2Rwy29o0wx0dAJlf_prRdgwIT4Zc7AO9btrzHGQZZhTyOqaCgYKAdQSARASFQHGX2MiIXjL136jLd4thuS87OFrYQ0175','1//0gWm0P4IYbqAOCgYIARAAGBASNwF-L9IrdZX587PSKbQv71_kIEXpzwGXjpSq_5JVF3BiFuvv0IXLtH7LdJW08EJQDhsM78ncmzE','2024-10-25 06:29:50.610661',5,NULL),(6,'ya29.a0AeDClZCacaMdCcXO42pc6uoBDVJAHc8RMn8koXy9q_OasnMPrOd19Mid0JLH0qqmLFyQQGscLcJ4uZ3JkoYoHdJS24Tbjh5iYf2UGuR41lt0ilceGjIRM7gRv6gnJJcs5FHeo7OLJzMsOSCIuq9SWit70iXDXpz6JKIj6r-DaCgYKAbsSARASFQHGX2Mixj_a0JGXqrtgmc7UGo73RA0175','1//0gXLmFj_97xssCgYIARAAGBASNwF-L9Ire77m7vQrJPp9n6RQUxd8w6hSQzh5zMsv0NBwf4HaIS4EnTO_a8Q-0X23a7VnznhJW1o','2024-10-25 06:54:59.928973',6,NULL),(7,'ya29.a0AeDClZBYgpMp-ccU8o0GwZhK1kYmp5qu3jhZXMl2Br1DjenP_UZvAF9io6vOLBtONSCflRv4iyQcoakZYpE1Ff-YaVxctTYGavg7MTWgEV__tx1byO33MGvUM_mLUBojc5B1vpAcGeIo9vVd3SZTowAI1AEXDI53cM0D44fvaCgYKAWMSARMSFQHGX2MiNnAtn0Cfb-4s7917IgxHCw0175','1//0gsIpkYJbL1-_CgYIARAAGBASNwF-L9IrZGAYkA7ZhR5zxGEKE-L8FWPCaopTWodfOMUOlurFotPtiS_YJ666QcsmBMha5eMw7x0','2024-10-25 08:17:10.544569',7,NULL),(8,'ya29.a0AcM612wTl7mnQCTcTCNHWEMHrgbJ3uzjHGJhZlPND5_nvlaIgopNui0aTNfUYSYz0gYteurZgo4KP-rVWsby2m1DkKTVfG3V-0lokTS5cPyIauBO3am96Rf2rpxEr3O0mXtVHZaH5do5JSQpC1FkLGy-8fUgMkszhEKxCuftaCgYKAYMSARESFQHGX2MiG9m45hAFtvDgXDQehE6HuQ0175','1//0gSvuuXLU5ngGCgYIARAAGBASNwF-L9IrUVhxxEgx6lE6E0BVR7F7KMfm1MRCA1z_TRjfHDWi2a_V562diJgbTyRoDV4R4dnGLfM','2024-10-25 09:07:20.617977',8,NULL);
/*!40000 ALTER TABLE `socialaccount_socialtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools_analyticsvisitordata`
--

DROP TABLE IF EXISTS `tools_analyticsvisitordata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools_analyticsvisitordata` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `timestamp` datetime(6) NOT NULL,
  `source` varchar(255) NOT NULL,
  `device` varchar(100) NOT NULL,
  `browser` varchar(100) NOT NULL,
  `os` varchar(100) NOT NULL,
  `country` varchar(100) NOT NULL,
  `ip_address` char(39) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools_analyticsvisitordata`
--

LOCK TABLES `tools_analyticsvisitordata` WRITE;
/*!40000 ALTER TABLE `tools_analyticsvisitordata` DISABLE KEYS */;
/*!40000 ALTER TABLE `tools_analyticsvisitordata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools_codecontent`
--

DROP TABLE IF EXISTS `tools_codecontent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools_codecontent` (
  `id` char(32) NOT NULL,
  `code` longtext NOT NULL,
  `language` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools_codecontent`
--

LOCK TABLES `tools_codecontent` WRITE;
/*!40000 ALTER TABLE `tools_codecontent` DISABLE KEYS */;
INSERT INTO `tools_codecontent` VALUES ('22d450eeb5614e6d8e51464c2823d4d9','# Initialize a counter for odd numbers\nodd_count = 0\n\n# Loop through numbers from 1 to 100\nfor num in range(1, 101):\n    # Check if the number is odd\n    if num % 2 != 0:\n        odd_count += 1\n\n# Print the result\nprint(f\"The count of odd numbers from 1 to 100 is: {odd_count}\")','python'),('6781a13aebf1442fa88207bce4b0f401','import requests\nfrom bs4 import BeautifulSoup\nimport csv\n\ndef scrape_books():\n    url = \"http://books.toscrape.com/catalogue/category/books/mystery_3/index.html\"\n    response = requests.get(url)\n    soup = BeautifulSoup(response.text, \'html.parser\')\n    \n    books = []\n    \n    for book in soup.find_all(\'article\', class_=\'product_pod\'):\n        title = book.h3.a[\'title\']\n        price = book.select_one(\'div p.price_color\').text\n        books.append({\'title\': title, \'price\': price})\n    \n    return books\n\ndef save_to_csv(books):\n    with open(\'books.csv\', \'w\', newline=\'\', encoding=\'utf-8\') as csvfile:\n        fieldnames = [\'title\', \'price\']\n        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)\n        \n        writer.writeheader()\n        for book in books:\n            writer.writerow(book)\n\nif __name__ == \"__main__\":\n    scraped_books = scrape_books()\n    save_to_csv(scraped_books)\n    print(f\"Scraped {len(scraped_books)} books and saved to books.csv\")','python');
/*!40000 ALTER TABLE `tools_codecontent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools_conversation`
--

DROP TABLE IF EXISTS `tools_conversation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools_conversation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uuid` char(32) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `is_cleared` tinyint(1) DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `tools_conversation_user_id_d5006e0d_fk_people_customuser_id` (`user_id`),
  CONSTRAINT `tools_conversation_user_id_d5006e0d_fk_people_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools_conversation`
--

LOCK TABLES `tools_conversation` WRITE;
/*!40000 ALTER TABLE `tools_conversation` DISABLE KEYS */;
INSERT INTO `tools_conversation` VALUES (1,'b6d58beb667e41428e797b655db929b1','Chat about test...','2024-10-20 09:41:42.436203','2024-10-20 09:41:47.797102','conversation-2024-10-20-0941',0,0,1),(2,'84fc9a5cd38a48c79ad1dd2c2d5881dc','Chat about generate images of i...','2024-10-20 09:42:24.511932','2024-10-22 23:47:15.956495','conversation-2024-10-20-0942',0,0,1),(3,'376aa31a04094c1aa1e90de1c016fa45','Chat about i am testing softwar...','2024-10-22 23:47:19.738790','2024-10-22 23:48:06.415423','conversation-2024-10-22-2347',0,0,1),(4,'98ee38c4cc644f8781cdca610c6a0109','Chat about bisakah buatkan spee...','2024-10-23 02:40:31.278398','2024-10-25 06:35:18.385314','conversation-2024-10-23-0240',0,0,1),(6,'5c031889e1f6439ba831bcc15b98f671','Chat about generate an image of...','2024-10-24 06:40:02.040999','2024-10-24 06:41:04.597693','conversation-2024-10-24-0640',0,0,10),(8,'995110e57d8249618087579eb0915ce7','Conversation 2024-10-25 06:03','2024-10-25 06:03:55.131450','2024-10-25 06:03:55.131483','conversation-2024-10-25-0603',0,0,12),(9,'6f2c7789493f4626ac053fda8753c327','Chat about PIHAK KEDUA setuju u...','2024-10-25 06:06:53.353276','2024-10-25 06:07:17.320053','conversation-2024-10-25-0606',0,0,11),(10,'dc3f0b60b5bf4e2795b7e17a0b3641e9','Chat about apa yang harus saya ...','2024-10-25 07:20:16.446373','2024-10-25 08:00:36.699439','conversation-2024-10-25-0720',0,0,13);
/*!40000 ALTER TABLE `tools_conversation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools_databasebackup`
--

DROP TABLE IF EXISTS `tools_databasebackup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools_databasebackup` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `timestamp` datetime(6) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_size` bigint NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `database_type` varchar(20) NOT NULL,
  `error_message` longtext,
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools_databasebackup`
--

LOCK TABLES `tools_databasebackup` WRITE;
/*!40000 ALTER TABLE `tools_databasebackup` DISABLE KEYS */;
/*!40000 ALTER TABLE `tools_databasebackup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools_imagecontent`
--

DROP TABLE IF EXISTS `tools_imagecontent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools_imagecontent` (
  `id` char(32) NOT NULL,
  `image` varchar(100) NOT NULL,
  `caption` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools_imagecontent`
--

LOCK TABLES `tools_imagecontent` WRITE;
/*!40000 ALTER TABLE `tools_imagecontent` DISABLE KEYS */;
INSERT INTO `tools_imagecontent` VALUES ('05d66c8d75154134b29b77adda1369ff','ai_images/p6Vm3rBOS10opDvMLvuT04mEkDWgwxq2WMdHg3D','generate images of indonesian independence day'),('0c01d4c24229449393f194edfe72b299','ai_images/e83D','generate images prabowo'),('56ceeb237b3047e5b3cbadac62273cf5','ai_images/pngskoidd505667d-d6c1-4a0a-bac7-5c84a87759f8sktida48cca56-e6da-484e-a814-9c849652b_46GFRXm','generate images of monas in jakarta'),('b7473d7f4b3e4bbeb2f85d4090420038','ai_images/pngskoidd505667d-d6c1-4a0a-bac7-5c84a87759f8sktida48cca56-e6da-484e-a814-9c849652b_ROPo8EF','generate images of indonesian independence day');
/*!40000 ALTER TABLE `tools_imagecontent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools_message`
--

DROP TABLE IF EXISTS `tools_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools_message` (
  `id` char(32) NOT NULL,
  `is_user` tinyint(1) NOT NULL,
  `ai_service` varchar(20) DEFAULT NULL,
  `timestamp` datetime(6) NOT NULL,
  `metadata` json DEFAULT NULL,
  `conversation_id` bigint NOT NULL,
  `content_type_id` int NOT NULL,
  `object_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tools_message_conversation_id_f0a84848_fk_tools_conversation_id` (`conversation_id`),
  KEY `tools_message_content_type_id_1041a9ee_fk_django_content_type_id` (`content_type_id`),
  CONSTRAINT `tools_message_content_type_id_1041a9ee_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `tools_message_conversation_id_f0a84848_fk_tools_conversation_id` FOREIGN KEY (`conversation_id`) REFERENCES `tools_conversation` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools_message`
--

LOCK TABLES `tools_message` WRITE;
/*!40000 ALTER TABLE `tools_message` DISABLE KEYS */;
INSERT INTO `tools_message` VALUES ('07f90bb2f4a44d799f1126865f5e40fb',0,'claude','2024-10-21 02:31:03.555167',NULL,2,29,'22d450eeb5614e6d8e51464c2823d4d9'),('0b8d535a4824492e8ce0f62d6ccb55a0',1,NULL,'2024-10-25 08:00:25.872460',NULL,10,31,'067c2e54bddb449a94307e4634a114ba'),('151bfead26b849419bae7a96f01a7448',1,NULL,'2024-10-25 06:16:05.608352',NULL,4,31,'0c60db6275504cca89cfff7b4b0f96fc'),('16b0e5167aa54366ab6988475337f8d3',1,NULL,'2024-10-25 06:07:10.749919',NULL,9,31,'eafca62e571f4d02a4d8bb287db5116d'),('1bdb5764d6904c5d8819534758f27efa',0,'openai','2024-10-21 05:29:10.034652',NULL,2,30,'56ceeb237b3047e5b3cbadac62273cf5'),('20834f6712694029959122a17a011ec9',0,'perplexity','2024-10-25 06:16:14.718934',NULL,4,31,'70c97345086841728a889426d77fadca'),('23775bfb3a3b4b3ba60f52a481b60171',1,NULL,'2024-10-25 06:17:42.626201',NULL,4,31,'b038b4ae415d451d9a67045cad83800f'),('24ab34387558454ebe810ad4e2aa9915',0,'openai','2024-10-22 23:47:44.984726',NULL,3,31,'deb41e981c3c47529af090ab1934d97d'),('270e697f04eb45ef9e4e317d3b3a5471',0,'claude','2024-10-25 06:17:57.644070',NULL,4,31,'6e99e8433d03471f91ac10be0de3e76d'),('2a8290e083f44107a9ca6f981a3df687',0,'claude','2024-10-22 23:47:15.952600',NULL,2,31,'a965f801ad5146ffb629aa2fb1b3bc03'),('2d4c43ec13b94a2ba20839e021135cb6',1,NULL,'2024-10-21 05:27:31.797874',NULL,2,31,'1aa2d03eab904d64894b452e433c5635'),('30aaedfe7ff24c2d9cc25b6a98f71f73',1,NULL,'2024-10-20 10:47:16.279383',NULL,2,31,'f54a8702aad749ccba139186f6edbadd'),('30b434f0b42c4310a220697f32e3755e',0,'claude','2024-10-20 09:41:47.781714',NULL,1,31,'105c34bca7fd4bd4aab80f62d861215b'),('373f7d75282a4c3d84146d413c5449ca',0,'openai','2024-10-22 23:46:34.598270',NULL,2,31,'84ecf7e16afb44f0be5bea137135b790'),('39fc9cb3fe22425cac8fc49259295a56',0,'openai','2024-10-22 23:47:56.364694',NULL,3,31,'05d7f87ae30442cb9e2516fc267ee0fc'),('3f8105a312c742fba9a5d2b8db00ecdf',1,NULL,'2024-10-22 23:46:14.093982',NULL,2,31,'973ae55f97b140c789826b3a2e4aa5cb'),('4c108b90bfda4295a3578753a9f18ff8',0,'claude','2024-10-25 07:21:11.790720',NULL,10,31,'207ea5ddb9ca466fabfbdb0bce34b0ba'),('4d7039c4290949ffaf2bd638a0b23862',1,NULL,'2024-10-22 23:47:43.196871',NULL,3,31,'28ef5cb953da4d8faa0423d585285845'),('522bcffeda76487eba91369f761d387c',1,NULL,'2024-10-24 06:40:37.274115',NULL,6,31,'09a1689c3d2b4e7c9e3e379a01e84d66'),('609cf2d6c342496c8ba0ce352c00a47b',1,NULL,'2024-10-25 06:35:06.213987',NULL,4,31,'cb3ffb754fbb4b25b213e9566ed59ddd'),('60f2ae22af774c39a0ac1df44783c970',1,NULL,'2024-10-21 02:30:55.141454',NULL,2,31,'03e530d514024c1c9c7523fbc3beb7ba'),('61369fb79d164c40943c6b194b2756db',1,NULL,'2024-10-25 06:17:57.669077',NULL,4,31,'008afdbf585b4a3abd81d78917a97438'),('62e37909a1284fa89d134ff973320afe',1,NULL,'2024-10-22 23:46:32.685807',NULL,2,31,'e18ef0ba2b5b44829eb973b713f92c5b'),('667811ba00454aa9bca624201a27965e',1,NULL,'2024-10-21 05:28:53.480644',NULL,2,31,'78ee772989004785b6c867c13d3c0416'),('6e46aa3f26fc41f8a09426a73f21b3b0',0,'claude','2024-10-25 07:20:41.683281',NULL,10,31,'ca7b3f11cba34cdcb323f48e943349a9'),('76c53eb739bd4798a533d7f7c4ea70ad',0,'perplexity','2024-10-25 06:16:44.830739',NULL,4,31,'2d723951590c4ce88a79c16aca5221a9'),('7701f65333d847af9331989f7657c623',1,NULL,'2024-10-22 23:47:11.374015',NULL,2,31,'517cdf9dd48b4e12ae19d5fe3b864a21'),('80a822772a2b4403843abd7aa11d79ef',1,NULL,'2024-10-22 23:45:45.408967',NULL,2,31,'4d8179dbeaf144918e12e489c6d15749'),('81c3b14133bd47858ef2673d48323131',1,NULL,'2024-10-24 06:41:03.098784',NULL,6,31,'622dd158612d4116a279c250f6c71b92'),('8d41fd7a79a94a4b9bb41c06a91c8c19',0,'claude','2024-10-25 06:35:18.378417',NULL,4,31,'48123209667649c0be29d0121d843b69'),('94fbd081237a4e9a94d438cfebc0a670',1,NULL,'2024-10-21 05:28:30.575643',NULL,2,31,'b80e28bf42944f7eb41114382cfc4825'),('97f2e364c59e4422bc615400e7773344',1,NULL,'2024-10-20 10:47:11.180887',NULL,2,31,'21857cf554cd420f9990928e6df4a5ff'),('99cd01a93c39405685ec90dff8047c28',0,'claude','2024-10-25 06:18:12.705176',NULL,4,31,'0317e30a00164604be998508f44dcf76'),('9b2b5252d11a47e7950bc5df303c8f6b',0,'openai','2024-10-22 23:48:06.411599',NULL,3,31,'2683c2a8213146e0954d33b6c1c0cad0'),('a0067f835b00498eae5f7becc73f8c1f',1,NULL,'2024-10-25 07:21:05.537945',NULL,10,31,'8252c49a7c8447868015249418a8f5fa'),('a94328878af5499887b2f9f0cd396253',1,NULL,'2024-10-20 09:41:45.678195',NULL,1,31,'11cb0919a9a84911948d8278173ad4dc'),('aa9f1430a95d48d6ae35fa3043db7e3c',0,'perplexity','2024-10-21 02:29:27.101658',NULL,2,31,'e57205571dab488c8e9f581ec8b94ef2'),('ac230d195ccf41a5953b7097e9c35268',1,NULL,'2024-10-21 02:29:18.517641',NULL,2,31,'8841b871006e4feeb422251eb274ee0d'),('b082947b36534218a104872bb1234fc8',0,'openai','2024-10-21 05:28:32.061533',NULL,2,31,'822a82fbca0e4e97b14adfbec16c8581'),('b604a65bd6a3424ca95408c860126739',0,'openai','2024-10-24 06:41:04.584448',NULL,6,31,'8cf5904fb65c4f96b0cb49f5687f2434'),('b7ab0110fcf84e089eaa1ed4c67fbef6',1,NULL,'2024-10-22 23:48:04.889424',NULL,3,31,'e99180e25d764b01837291bbb41a7791'),('c0f8be4bdc674055bfaa9000ee30f016',0,'openai','2024-10-20 10:47:28.290163',NULL,2,30,'b7473d7f4b3e4bbeb2f85d4090420038'),('c4783938d824459b9adbd38738b4c44c',1,NULL,'2024-10-22 23:47:55.251533',NULL,3,31,'79dbf6bddad64449a2e55caeb8a94239'),('c586fe821fb6420fa45f16054eafd52e',1,NULL,'2024-10-25 06:16:40.630719',NULL,4,31,'d72b2036e92f4b3384fe406c739def4d'),('cc8ba99ed03b4357b485d7a0e30fff1e',0,'openai','2024-10-22 23:46:16.168588',NULL,2,31,'41e2c48235014470b0164a03105402f2'),('ce5602eeb87942c6b0a0927686ee2555',0,'claude','2024-10-22 23:45:49.412757',NULL,2,31,'516afe7668424db59b940bb60de5c946'),('ce5cba5069964b5aab7661899f5b50e9',0,'openai','2024-10-21 05:27:43.129094',NULL,2,30,'0c01d4c24229449393f194edfe72b299'),('d9818c47d0bb46fc92b8e876bbcbc4fe',1,NULL,'2024-10-25 07:20:32.743332',NULL,10,31,'360d80f2d8c04db3ae68e1049e405c40'),('df956a7e2fb54b8897991b1cdc63a6c1',0,'openai','2024-10-20 10:47:31.487684',NULL,2,30,'05d66c8d75154134b29b77adda1369ff'),('e5d2a23ff778404cb2490a88dae8826b',0,'claude','2024-10-25 06:07:17.318037',NULL,9,31,'7bbe9680564644f18fba650b4e6caea1'),('ff75716817c84f5c95c9445848fae4cc',0,'claude','2024-10-25 08:00:36.691235',NULL,10,31,'f3625e4e61c741b883a9bc688955b495'),('ffef2d0e222e4de5873526ccbe16adf3',0,'openai','2024-10-24 06:40:39.967870',NULL,6,31,'67d427e814ef489799a6a5311104aa8e');
/*!40000 ALTER TABLE `tools_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools_notification`
--

DROP TABLE IF EXISTS `tools_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools_notification` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `object_id` int unsigned NOT NULL,
  `message` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `content_type_id` int NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tools_notification_content_type_id_9e2d0813_fk_django_co` (`content_type_id`),
  KEY `tools_notification_user_id_7102fd5a_fk_people_customuser_id` (`user_id`),
  CONSTRAINT `tools_notification_content_type_id_9e2d0813_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `tools_notification_user_id_7102fd5a_fk_people_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `people_customuser` (`id`),
  CONSTRAINT `tools_notification_chk_1` CHECK ((`object_id` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools_notification`
--

LOCK TABLES `tools_notification` WRITE;
/*!40000 ALTER TABLE `tools_notification` DISABLE KEYS */;
/*!40000 ALTER TABLE `tools_notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools_textcontent`
--

DROP TABLE IF EXISTS `tools_textcontent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools_textcontent` (
  `id` char(32) NOT NULL,
  `text` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools_textcontent`
--

LOCK TABLES `tools_textcontent` WRITE;
/*!40000 ALTER TABLE `tools_textcontent` DISABLE KEYS */;
INSERT INTO `tools_textcontent` VALUES ('008afdbf585b4a3abd81d78917a97438','can you blend the speech instead make segmentation for each'),('0317e30a00164604be998508f44dcf76','I apologize for the confusion. It seems I misunderstood your previous request. I\'ll provide a fully blended speech without any segmentation, focusing on the economic issues and the new cabinet, tailored for an audience of both ministry officials and academics. Here\'s a revised version:\n\n---\n\nDistinguished guests, esteemed colleagues, ladies and gentlemen,\n\nToday, as we celebrate the 50th anniversary of the Centre for Strategic and International Studies (CSIS), we find ourselves at a pivotal moment in Indonesia\'s economic journey. For half a century, CSIS has been an integral part of our nation\'s policy landscape, bridging the gap between research, academia, and government action. This milestone offers us an opportunity to reflect on our economic challenges and the path forward, particularly in light of our new cabinet and the evolving global economic landscape.\n\nIn recent years, Indonesia has navigated through significant economic shifts, from managing transitional state budgets to developing sustainable growth strategies. Our resilience in the face of global uncertainties has been commendable, but the road ahead demands even greater innovation and collaboration.\n\nAs we approach the formulation of the 2025 State Budget (RAPBN 2025), we must confront the realities of an uncertain global economy. The preparation of the Macroeconomic Framework and Fiscal Policy Principles (KEM-PPKF) will be crucial in setting the tone for our fiscal planning. We need to consider a balanced approach, potentially incorporating Keynesian stimulus strategies to boost growth while maintaining fiscal responsibility.\n\nThe recent formation of our new cabinet brings fresh perspectives to these challenges. It\'s imperative that we harness this new energy to craft policies that address both immediate needs and long-term sustainability. This requires a delicate balance between stimulating current economic activity and investing in our future prosperity.\n\nIn this context, the role of research and in-depth analysis becomes even more critical. The collaboration between government institutions, think tanks like CSIS, and our academic community is essential in developing robust, evidence-based policies. We must leverage our collective expertise to navigate complex global economic trends, technological advancements, and shifting geopolitical dynamics.\n\nLooking towards Indonesia\'s economic transformation by 2045, we need to focus on sustainable development strategies, including the promotion of a green economy. This transformation demands a carefully orchestrated approach across sectors, stakeholders, and regions. Our goal should be to elevate our economic structure from lower to higher productivity, fostering innovation and enhancing our global competitiveness.\n\nThe challenges we face – from climate change to digital transformation – require innovative solutions and collaborative efforts. It\'s through the synergy of government action, academic research, and policy analysis that we can develop strategies that are both theoretically sound and practically viable.\n\nAs we celebrate CSIS\'s 50 years of contribution to public policy, let\'s also look forward to the next half-century. The institution\'s role in bridging theoretical knowledge and practical policymaking will be more crucial than ever. We must continue to foster an environment of open dialogue and knowledge sharing to develop more effective and sustainable economic policies.\n\nIn conclusion, this 50th anniversary of CSIS is not just a celebration of past achievements, but a call to action for our future. The synergy between government, academia, and think tanks will be pivotal in shaping Indonesia\'s economic trajectory. Together, we can create policies that not only drive economic growth but also ensure equitable and sustainable development for all Indonesians.\n\nAs we face the economic challenges ahead, let us draw inspiration from CSIS\'s legacy of thoughtful analysis and collaborative policymaking. With our combined efforts, I am confident that we can navigate the complexities of our economic landscape and build a prosperous future for Indonesia.\n\nThank you for your attention, and here\'s to another 50 years of CSIS\'s invaluable contributions to our nation\'s progress.\n\n---\n\nThis speech is designed to last approximately 10 minutes when delivered at a moderate pace. It blends perspectives relevant to both ministry officials and academics without explicit segmentation, creating a cohesive narrative that addresses the key points of economic issues and the new cabinet. Feel free to adjust or refine it further based on your specific needs or preferences.'),('03e530d514024c1c9c7523fbc3beb7ba','write code in python for count odd number from 1 to 100'),('05d7f87ae30442cb9e2516fc267ee0fc','I can create a mosaic-style image for you. Please provide me with more details about the subject of the image, the colors you would like to include, and any other specific elements you want to be part of the mosaic. Let me know so I can create the image you have in mind.'),('067c2e54bddb449a94307e4634a114ba','lalu rencna financial apa ya yang bagus sebelum resign?'),('09a1689c3d2b4e7c9e3e379a01e84d66','generate an image of pikachu'),('0c60db6275504cca89cfff7b4b0f96fc','bisakah buatkan speech untuk acara 50 tahun csis, dengan penakan pada isu ekonomi dan kabinet baru, dengan segmentasi pendengar dari kementrian dan akademisi untuk speech selama 10 menit'),('105c34bca7fd4bd4aab80f62d861215b','I see you\'ve written \"test\" twice. Is there something specific you\'d like assistance with or a question you want to ask? I\'m here to help with a wide range of topics and tasks, so please feel free to ask anything.'),('11cb0919a9a84911948d8278173ad4dc','test'),('1aa2d03eab904d64894b452e433c5635','generate images prabowo'),('207ea5ddb9ca466fabfbdb0bce34b0ba','Haha, pertanyaan yang menarik! \"Makan apa kalau resign\" bukan makna harfiah, tapi bisa diartikan sebagai \"apa yang akan dilakukan untuk mencari nafkah setelah resign\". Beberapa pilihan \"makanan\" setelah resign:\n\n1. \"Makan\" tabungan - gunakan dana darurat sementara mencari pekerjaan baru\n2. \"Makan\" dari bisnis sampingan yang sudah disiapkan\n3. \"Makan\" dari pekerjaan freelance atau kontrak jangka pendek  \n4. \"Makan\" dari skill baru yang dipelajari untuk karir baru\n5. \"Makan\" dari investasi yang sudah dilakukan sebelumnya\n\nIntinya, pastikan ada rencana finansial yang matang sebelum memutuskan resign. Jangan sampai benar-benar kehabisan \"makanan\" ya!'),('21857cf554cd420f9990928e6df4a5ff','generate images of indonesian independence day'),('2658a262458a4464966943a104d8644d','please define collaborative governance'),('2683c2a8213146e0954d33b6c1c0cad0','I\'m sorry for any confusion, but as a text-based assistant, I\'m unable to create or display images directly. However, I can guide you on how to create a mosaic image of a mosque using various online tools or software. Would you like some suggestions on how you can create a mosaic image of a mosque yourself?'),('28ef5cb953da4d8faa0423d585285845','i am testing software, draw me something'),('2d723951590c4ce88a79c16aca5221a9','The speech I provided earlier was designed to be concise and focused, given the 10-minute time limit. However, there are several limitations and considerations when crafting a speech within a specific time frame:\n\n1. **Attention Span**: Most adults have an average attention span of 10 to 20 minutes. This means that maintaining engagement and clarity is crucial within this time frame.\n\n2. **Content Prioritization**: For shorter speeches, you need to prioritize your main points and ensure they are relevant, specific, and supported by evidence or examples.\n\n3. **Pacing and Tone**: Adjusting your pace and tone according to the time limit is essential. For shorter speeches, you may need to speak faster without losing clarity, while for longer ones, you should speak slower but not too slow.\n\n4. **Word Count**: A 10-minute speech typically contains around 500 to 700 words, depending on the speaking rate (approximately 130-150 words per minute). This means you need to be concise and focused on key points.\n\n5. **Audience Engagement**: Engaging your audience throughout the speech is crucial. Using rhetorical questions, anecdotes, humor, or interactive elements can help keep them involved and interested.\n\n6. **Structuring the Speech**: Breaking your speech into sections (e.g., introduction, main points) and ensuring each section is well-timed can help you stay within the allotted time.\n\n7. **Practice and Feedback**: Practicing your speech and getting feedback from others can help you refine your delivery and ensure you stay within the time limit.\n\nBy considering these factors, you can effectively adapt your speech to meet the 10-minute time limit while maintaining clarity and engagement for your audience.\n\n---\n\nIf you need further adjustments or more detailed guidance, feel free to ask'),('360d80f2d8c04db3ae68e1049e405c40','apa yang harus saya lakukan kalo mau resign?'),('41e2c48235014470b0164a03105402f2','I\'m unable to draw or create images. However, you can search for historical images or artwork depicting the war between Indonesia and the Netherlands during Indonesia\'s struggle for independence on the internet or in history books. If you need any information or details about this historical event, feel free to ask!'),('48123209667649c0be29d0121d843b69','Maaf atas kesalahpahaman sebelumnya. Saya akan mencoba membuat versi singkat dari pidato tersebut dalam bahasa Minangkabau. Harap diingat bahwa ini adalah upaya terbaik saya, dan mungkin tidak sepenuhnya akurat atau idiomatik:\n\n---\n\nAssalamualaikum Warahmatullahi Wabarakatuh,\n\nSanak sadonyo nan tahormat,\n\nHari ko, kito bakumpua untuak marayoan 50 taun CSIS. Salamo ko, CSIS alah mambantu mamajuan nagari kito malalui pamikiran dan panelitian nan cadiak.\n\nKito sadang maadoki maso-maso nan sulik dalam ekonomi. Dunia sadang barubah capek, dan kito musti siap maadokinyo. Kabinet baru kito paralu mancari caro untuak mamajuan ekonomi, tapi indak buliah lupo jo masa depan.\n\nKito paralu karajo samo antaro pamarintah, ahli, dan urang pandai dari kampuih. Samo-samo kito dapek mancari jalan kalua dari masalah ekonomi ko. CSIS alah manolong banyak dalam hal iko, dan kito harap inyo dapek taruih mambantu 50 taun ka muko.\n\nDalam manyusun RAPBN 2025, kito musti ati-ati. Dunia masih indak manantu, jadi kito paralu rancana nan elok. Kito juo musti pikia tantang ekonomi ijau dan caro mambuek nagari kito labiah maju.\n\nAkhir kato, mari kito samo-samo bakarajo untuak mamajuan ekonomi Indonesia. Dengan karajo samo, insya Allah kito dapek mancapai kamajuan untuak sadonyo urang Indonesia.\n\nTarimo kasih. Wassalamualaikum Warahmatullahi Wabarakatuh.\n\n---\n\nPidato ko alah dicubo untuak manggunoan bahaso Minangkabau, tapi mungkin ado kato-kato atau ungkapan nan kurang tapek. Mohon maaf jiko ado kasalahan atau kakurangan. Jiko ado nan paralu diubah atau diperbaiki, tolong kecek sajo.'),('4d8179dbeaf144918e12e489c6d15749','draw me war indonesia and netherland on independence day'),('516afe7668424db59b940bb60de5c946','I apologize, but I am not able to draw, generate, create, edit, manipulate or produce images. I can only perceive and analyze existing images. I don\'t have the capability to create new images or artwork.\n\nIf you\'re looking for an image depicting the war between Indonesia and the Netherlands during Indonesia\'s struggle for independence, you may want to try using an image creation tool or service, or search for historical photos or artwork related to that period in Indonesian history. \n\nIs there perhaps some other way I can assist you with information about Indonesia\'s war for independence against the Netherlands?'),('517cdf9dd48b4e12ae19d5fe3b864a21','i\'m testing my software, draw me something'),('5bc36029de16434fbee3bfb07edce352','write me a code for data scraping'),('622dd158612d4116a279c250f6c71b92','pikhacu standing'),('67d427e814ef489799a6a5311104aa8e','I can help you create an image of Pikachu! Could you please provide specific details on how you would like Pikachu to be depicted? For example, do you want Pikachu to be standing, sitting, or doing a specific pose? Any additional details you can provide will help me create the image you have in mind.'),('6bf83556c4e64cd5a340a7c217a006ea','Collaborative governance is a form of governance that involves the collective engagement of various stakeholders, including public agencies, non-state actors, private organizations, and community groups, to address public policy issues and manage public programs or assets. This approach emphasizes inclusivity, transparency, and consensus-oriented decision-making processes.\n\nHere are the key elements that define collaborative governance:\n\n1. **Initiation by Public Agencies**: The process is typically initiated by one or more public agencies or institutions.\n2. **Involvement of Non-State Actors**: Participants include non-state actors such as civil society organizations, private companies, and individual citizens.\n3. **Decision-Making Power**: Non-state actors are not merely consulted but have direct decision-making power.\n4. **Formal Process**: The forum is formally organized and structured to facilitate collective decision-making.\n5. **Consensus-Oriented**: Decision-making is consensus-oriented, aiming to achieve agreement among stakeholders.\n6. **Focus on Public Policy**: The focus of collaboration is on making or implementing public policy or managing public programs or assets.\n\nCollaborative governance aims to leverage the unique attributes and resources of each sector to address complex societal challenges and achieve mutually beneficial outcomes. It fosters sustainable solutions by engaging diverse stakeholders in a cooperative manner, enhancing stakeholder buy-in, optimizing resource utilization, and encouraging innovative problem-solving.\n\n### Examples of Definitions\n\n- **Ansell and Gash (2008)**: \"A governing arrangement where one or more public agencies directly engage non-state stakeholders in a collective decision-making process that is formal, consensus-oriented, and deliberative and that aims to make or implement public policy or manage public programs or assets\".\n- **Emerson, Nabatchi, and Balogh (2011)**: \"The processes and structures of public policy decision making and management that engage people constructively across the boundaries of public agencies, levels of government, and/or the public, private and civic spheres in order to carry out a public purpose that could not otherwise be accomplished\".\n- **Policy Consensus Initiative (2007)**: \"Leaders engaging with all sectors—public, private, non-profit, citizens, and others—to develop effective, lasting solutions to public problems that go beyond what any sector could achieve on its own\".\n\nThese definitions collectively highlight the core principles and practices of collaborative governance.'),('6e99e8433d03471f91ac10be0de3e76d','Certainly! I\'ll create a blended version of the speech that integrates the content for both the ministry officials and academics without explicit segmentation. This approach will create a more cohesive narrative for the entire audience. Here\'s a revised version:\n\n---\n\n**Speech for CSIS 50th Anniversary**\n\nDistinguished guests, esteemed colleagues, ladies and gentlemen,\n\nIt is my great honor to address you today as we celebrate the 50th anniversary of the Centre for Strategic and International Studies (CSIS). For half a century, CSIS has been at the forefront of shaping public policy in Indonesia, contributing invaluable insights and fostering dialogue between government, academia, and civil society.\n\nAs we gather here today, we find ourselves at a critical juncture in Indonesia\'s economic journey. The global landscape is rapidly evolving, presenting us with both unprecedented challenges and exciting opportunities. It is in times like these that the collaboration between government institutions, think tanks like CSIS, and our esteemed academic community becomes more crucial than ever.\n\nIn recent years, we have witnessed significant shifts in Indonesia\'s economic policies. From the management of transitional state budgets to the development of sustainable growth strategies, our nation has demonstrated resilience and adaptability. However, the road ahead demands even greater cooperation and innovative thinking.\n\nAs we look towards the preparation of the 2025 State Budget (RAPBN 2025), we must acknowledge the uncertainties in both global and domestic economic conditions. The formulation of the Macroeconomic Framework and Fiscal Policy Principles (KEM-PPKF) will be pivotal in laying the groundwork for our fiscal planning. In this context, we must consider the potential benefits of Keynesian stimulus strategies to boost economic growth while maintaining fiscal prudence.\n\nThe role of research and in-depth analysis cannot be overstated in addressing these complex economic issues. CSIS has consistently provided objective and professional insights that have greatly influenced public policy development. As we chart our course towards Indonesia\'s economic transformation by 2045, we must pay close attention to sustainable development strategies, including the green economy.\n\nThis transformation requires a carefully orchestrated approach across sectors, stakeholders, and regions. Our goal should be to elevate our economic structure from lower to higher productivity, fostering innovation and competitiveness on the global stage.\n\nThe recent formation of a new cabinet brings fresh perspectives and challenges to our economic management. It is imperative that we design economic policies that not only address short-term needs but also ensure long-term sustainability. This requires a delicate balance between immediate economic stimulus and strategic investments in our future.\n\nThe collaboration between government officials, policymakers, and academics is more important than ever. We must leverage our collective expertise to navigate the complexities of global economic trends, technological advancements, and shifting geopolitical dynamics. By fostering an environment of open dialogue and knowledge sharing, we can develop more robust and effective economic policies.\n\nAs we celebrate CSIS\'s 50 years of contribution to public policy, let us also look forward to the next half-century. The challenges we face – from climate change to digital transformation – require innovative solutions and collaborative efforts. It is through institutions like CSIS that we can bridge the gap between theoretical knowledge and practical policymaking, ensuring that our economic strategies are both academically sound and practically viable.\n\nIn conclusion, as we commemorate this significant milestone for CSIS, let us renew our commitment to collaborative policymaking. The synergy between government, academia, and think tanks like CSIS will be crucial in shaping Indonesia\'s economic future. Together, we can create policies that not only drive economic growth but also ensure equitable and sustainable development for all Indonesians.\n\nThank you for your attention, and here\'s to another 50 years of CSIS\'s invaluable contributions to our nation\'s progress.\n\n---\n\nThis blended speech integrates perspectives relevant to both ministry officials and academics, creating a cohesive narrative that addresses the key points without explicit segmentation. The speech is designed to last approximately 10 minutes when delivered at a moderate pace. Feel free to adjust or refine it further based on your specific needs or preferences.'),('70c97345086841728a889426d77fadca','Saya dengan senang hati membantu Anda dalam menyusun sebuah speech untuk acara 50 tahun CSIS yang berfokus pada isu ekonomi dan kabinet baru. Berikut adalah contoh speech yang dapat Anda gunakan, dengan segmentasi pendengar dari kementrian dan akademisi:\n\n---\n\n**Speech untuk Acara 50 Tahun CSIS**\n\n**Selamat Datang, Bapak/Ibu**\n\nHari ini, kita berada di sini untuk merayakan 50 tahun CSIS, sebuah lembaga yang telah berkontribusi besar dalam pengembangan kebijakan publik di Indonesia. Saya sangat menghargai kesempatan ini untuk berbicara tentang isu-isu ekonomi dan kabinet baru yang sedang kita hadapi.\n\n**Segmentasi Pendengar: Kementrian**\n\nUntuk para pejabat kementrian, saya ingin menekankan pentingnya kerja sama antara lembaga pemerintah dan think tank seperti CSIS. Dalam beberapa tahun terakhir, kita telah melihat banyak perubahan dalam kebijakan ekonomi Indonesia, dari pengelolaan APBN transisi hingga strategi pembangunan berkelanjutan. Kita harus terus berkomunikasi dan berkolaborasi untuk menciptakan kebijakan yang efektif dan berkelanjutan.\n\nMisalnya, dalam penyusunan RAPBN 2025, kita harus mempertimbangkan kondisi ekonomi global dan domestik yang masih penuh ketidakpastian. Kita perlu merancang dokumen Kerangka Ekonomi Makro dan Pokok-Pokok Kebijakan Fiskal (KEM-PPKF) yang menjadi landasan dalam penyusunan RAPBN 2025. Stimulus Keynesian akan menjadi salah satu strategi yang digunakan untuk meningkatkan pertumbuhan ekonomi.\n\n**Segmentasi Pendengar: Akademisi**\n\nUntuk para akademisi, saya ingin menekankan pentingnya penelitian dan analisis yang mendalam dalam menghadapi isu-isu ekonomi. CSIS telah berkontribusi besar dalam pengembangan kebijakan publik melalui penelitian dan analisis yang objektif dan profesional.\n\nMisalnya, dalam transformasi ekonomi Indonesia menuju 2045, kita perlu memperhatikan strategi pembangunan berkelanjutan seperti ekonomi hijau. Transformasi ekonomi ini memerlukan orkestrasi lintas sektor, lintas pelaku, dan lintas wilayah. Dengan demikian, kita dapat meningkatkan produktivitas dan mengubah struktur perekonomian dari lower productivity ke higher productivity.\n\n**Kabinet Baru dan Isu Ekonomi**\n\nDalam konteks kabinet baru, kita harus siap untuk menghadapi tantangan-tantangan baru dalam pengelolaan ekonomi. Kita perlu memastikan bahwa kebijakan ekonomi yang diambil tidak hanya berfokus pada jangka pendek tetapi juga berkelanjutan.\n\nDalam beberapa tahun terakhir, kita telah melihat banyak perubahan dalam kebijakan ekonomi Indonesia. Dari pengelolaan APBN transisi hingga strategi pembangunan berkelanjutan, kita harus terus berkomunikasi dan berkolaborasi untuk menciptakan kebijakan yang efektif dan berkelanjutan.\n\n**Kesimpulan**\n\nHari ini, kita merayakan 50 tahun CSIS, sebuah lembaga yang telah berkontribusi besar dalam pengembangan kebijakan publik di Indonesia. Saya berharap bahwa kita dapat terus berkolaborasi dan berkomunikasi untuk menciptakan kebijakan ekonomi yang efektif dan berkelanjutan. Terima kasih.\n\n---\n\nSaya harap contoh speech ini dapat membantu Anda dalam menyusun speech untuk acara 50 tahun CSIS. Jika Anda memiliki pertanyaan atau perlu penyesuaian lebih lanjut, silakan bertanya'),('78ee772989004785b6c867c13d3c0416','generate images of monas in jakarta'),('79dbf6bddad64449a2e55caeb8a94239','like mosaic image'),('7bbe9680564644f18fba650b4e6caea1','Berikut adalah versi yang telah diperbaiki dengan tata bahasa yang lebih baik:\n\nPIHAK KEDUA menyetujui untuk berkolaborasi dalam penyelenggaraan dua acara:\n\n1. Playdate Inklusif, yang akan diselenggarakan secara tatap muka dalam dua sesi pada tanggal 30 November 2024 di Youreka Kids Farm, Kuningan.\n\n2. Pesta Inklusif 2024, yang akan diselenggarakan secara tatap muka pada tanggal 6 Desember 2024 di Taman Ismail Marzuki, Cikini, Jakarta.\n\nKedua acara tersebut akan dilaksanakan secara langsung (offline) sesuai dengan tanggal dan lokasi yang telah ditentukan.'),('822a82fbca0e4e97b14adfbec16c8581','I can certainly generate an image of Monas (National Monument) in Jakarta, Indonesia. Could you please provide more specific details or preferences for the image of Monas that you would like me to create?'),('8252c49a7c8447868015249418a8f5fa','kalo resign makan apa ya?'),('84ecf7e16afb44f0be5bea137135b790','I\'m unable to draw or create images. However, I can describe the flag of Indonesia for you. The flag of Indonesia is a simple horizontal bicolor with two equal horizontal bands, red (top) and white (bottom). The red symbolizes courage and the white represents purity. \n\nIf you\'re looking for images of Indonesia, I recommend searching for photographs or illustrations of Indonesia online or in image databases. If you have specific requirements or details you\'d like in an image of Indonesia, please let me know, and I can help guide you in finding the right image.'),('8841b871006e4feeb422251eb274ee0d','tell me about prabowo subianto'),('8cf5904fb65c4f96b0cb49f5687f2434','It seems like there was a typo in your request. Did you mean you want an image of Pikachu standing? If so, I can help you create an image of Pikachu standing. Would you like any specific background or details included in the image, or should I just focus on Pikachu standing?'),('973ae55f97b140c789826b3a2e4aa5cb','draw me war indonesia and netherland on independence day'),('a0cbba73dc984e22afb0fbd6edee3220','please define collaborative governance'),('a965f801ad5146ffb629aa2fb1b3bc03','I apologize, but I am not able to draw, generate, create, edit, or produce images in any way. I can only perceive and analyze existing images. I don\'t have the capability to create new images or artwork, even for testing purposes.\n\nIf you\'re testing software related to image generation or manipulation, you may need to use a different AI model or tool specifically designed for image creation. There are various AI image generation tools available that might be suitable for your testing needs.\n\nIs there perhaps another way I can assist you with your software testing? I\'d be happy to help with text-based tasks or provide information if that would be useful.'),('b038b4ae415d451d9a67045cad83800f','can you blend the speech instead make segmentation for each'),('b80e28bf42944f7eb41114382cfc4825','generate monas'),('ca7b3f11cba34cdcb323f48e943349a9','Jika Anda ingin mengundurkan diri (resign) dari pekerjaan Anda, berikut adalah langkah-langkah yang sebaiknya Anda lakukan:\n\n1. Pertimbangkan keputusan Anda dengan matang\nPastikan Anda sudah memikirkan baik-baik alasan pengunduran diri dan konsekuensinya.\n\n2. Periksa kontrak kerja\nCek ketentuan pengunduran diri dalam kontrak kerja Anda, termasuk masa pemberitahuan yang diperlukan.\n\n3. Siapkan surat pengunduran diri\nTulis surat resmi yang menyatakan niat Anda untuk mengundurkan diri, tanggal efektif, dan ucapan terima kasih.\n\n4. Bicarakan dengan atasan langsung\nSampaikan keputusan Anda secara langsung kepada atasan sebelum memberitahu rekan kerja lain.\n\n5. Serahkan surat pengunduran diri\nBerikan surat pengunduran diri kepada atasan dan bagian HR.\n\n6. Tawarkan bantuan dalam masa transisi\nBersedia membantu proses serah terima pekerjaan kepada pengganti Anda.\n\n7. Selesaikan tugas-tugas yang tersisa\nPastikan semua pekerjaan Anda terselesaikan dengan baik sebelum pergi.\n\n8. Kembalikan properti perusahaan\nKembalikan semua barang milik perusahaan yang Anda gunakan.\n\n9. Minta surat referensi\nJika diperlukan, minta surat referensi dari atasan atau HR.\n\n10. Ucapkan perpisahan\nSampaikan salam perpisahan kepada rekan kerja secara profesional.\n\nIngatlah untuk tetap profesional dan menjaga hubungan baik sepanjang proses pengunduran diri ini.'),('cb3ffb754fbb4b25b213e9566ed59ddd','can you use bahasa minangkabay'),('d72b2036e92f4b3384fe406c739def4d','why so short? is there any lmitation'),('deb41e981c3c47529af090ab1934d97d','I can help with that! What specific image would you like me to create for you? Please provide details such as the subject, colors, style, and any other specific elements you would like to include in the image.'),('e18ef0ba2b5b44829eb973b713f92c5b','draw me image of indonesia'),('e57205571dab488c8e9f581ec8b94ef2','Prabowo Subianto is a prominent Indonesian politician, businessman, and retired honorary army general. Here is a detailed overview of his background and career:\n\n### Early Life and Education\n- **Birth and Family**: Prabowo Subianto Djojohadikusumo was born on October 17, 1951, to one of Indonesia\'s most influential families. His father, Sumitro Djojohadikusumo, was a prominent economist and politician who served under Presidents Sukarno and Suharto.\n- **Education**: Prabowo graduated from the Indonesian Military Academy (Akademi Militer Nasional) in 1970 and later completed a Special Forces Officer Course at Fort Benning in the United States.\n\n### Military Career\n- **Service**: Prabowo spent nearly three decades in the military, primarily serving in the Special Forces (Kopassus). He was involved in operations in East Timor and was commander of a group operating there in the 1980s and 1990s.\n- **Human Rights Allegations**: Human rights groups have accused Prabowo of involvement in human rights violations during Indonesia\'s occupation of East Timor. He has denied these allegations, but the controversy led to him being banned from traveling to the U.S. until 2020.\n\n### Political Career\n- **Entry into Politics**: After being dishonorably discharged from the military in 1998, Prabowo entered politics. He cofounded the Gerindra Party in 2008 and became its chairman in 2014.\n- **Presidential Campaigns**:\n  - **2009**: Prabowo ran for vice president as part of Megawati Sukarnoputri\'s campaign but lost to Susilo Bambang Yudhoyono.\n  - **2014**: He ran for president but was defeated by Joko Widodo, which he initially disputed.\n  - **2019**: Prabowo made another unsuccessful run for the presidency with Sandiaga Uno as his running mate. His refusal to accept the election results led to protests and riots in Jakarta, resulting in eight deaths and 737 injuries.\n  - **2024**: Prabowo secured a majority in the election, winning 59% of the vote, and was inaugurated as Indonesia\'s president on October 20, 2024.\n\n### Business Career\n- **Nusantara Group**: After leaving the military, Prabowo joined his brother\'s business ventures. He now controls the Nusantara Group, which includes companies in various sectors such as oil and gas, coal, palm oil plantations, and fisheries.\n\n### Leadership and Policies\n- **Defense Minister**: Prabowo served as Indonesia\'s Defense Minister from 2019 to 2024, during which he continued the modernization agenda initiated by his predecessor, Joko Widodo. He has vowed to continue Widodo\'s economic development plans, including the $30 billion project to build a new capital city called Nusantara.\n- **Human Rights Concerns**: Despite his promises to defend the people, Prabowo\'s human rights record remains a concern for activists and some analysts. His past involvement in human rights abuses during his military career has raised questions about his commitment to democracy and human rights.\n\nPrabowo Subianto\'s career is marked by both significant achievements and controversies. His inauguration as Indonesia\'s president in 2024 has sparked both hope and concern among the Indonesian people and international observers.'),('e69fa0715c944d5bb36a16cb5260cc95','Collaborative governance is a participatory approach to decision-making and problem-solving that involves multiple stakeholders working together to address complex issues and achieve common goals. This collaborative process typically includes government agencies, non-profit organizations, community groups, and other relevant parties who come together to share information, resources, and responsibilities in a transparent and inclusive manner.\n\nKey characteristics of collaborative governance include:\n\n1. **Shared Decision-Making**: Stakeholders work together to make decisions and shape policies or programs.\n2. **Mutual Accountability**: All parties are accountable to each other and share responsibility for the outcomes.\n3. **Information Sharing**: Open communication and sharing of information among stakeholders.\n4. **Resource Sharing**: Pooling of resources, expertise, and capabilities to address common challenges.\n5. **Consensus Building**: Seeking agreement and common ground among stakeholders through dialogue and negotiation.\n6. **Inclusivity**: Ensuring that diverse perspectives and voices are represented in the decision-making process.\n\nCollaborative governance is often used in contexts where traditional top-down approaches may not be sufficient to address complex, multi-faceted issues. By leveraging the strengths and expertise of various stakeholders, collaborative governance can lead to more innovative solutions, increased buy-in and support from the community, and greater overall effectiveness in achieving shared goals.\n\nIf you\'d like more specific details or examples related to collaborative governance, feel free to ask!'),('e99180e25d764b01837291bbb41a7791','mosaic of mosque'),('eafca62e571f4d02a4d8bb287db5116d','PIHAK KEDUA setuju untuk bekerja sama dalam pelaksanaan Playdate Inklusif yang merupakan kegiatan yang dilakukan secara offline dengan dua sesi pada tanggal 30 November 2024 di Youreka Kids Farm, Kuningan serta Pesta Inklusif 2024 yang merupakan kegiatan yang dilakukan secara offline pada 6 Desember 2024 di Taman Ismail Marzuki, Cikini, Jakarta.\ntuliskan ulang dengan tata bahasa yang lebih baik'),('f3625e4e61c741b883a9bc688955b495','Rencana finansial yang baik sebelum resign sangat penting untuk menjaga stabilitas keuangan Anda. Berikut beberapa rencana finansial yang sebaiknya Anda persiapkan:\n\n1. Dana darurat\nSiapkan dana darurat setara 6-12 bulan pengeluaran bulanan Anda. Ini akan membantu Anda bertahan selama masa transisi atau pencarian kerja baru.\n\n2. Anggaran ketat\nBuat anggaran yang lebih ketat dan mulai mengurangi pengeluaran yang tidak perlu.\n\n3. Pelunasan utang\nUsahakan untuk melunasi atau setidaknya mengurangi utang-utang Anda, terutama yang berbunga tinggi.\n\n4. Asuransi\nPastikan Anda memiliki asuransi kesehatan yang memadai, terutama jika asuransi dari perusahaan akan berakhir.\n\n5. Rencana karir selanjutnya\nTentukan langkah karir selanjutnya, apakah mencari pekerjaan baru, memulai bisnis, atau menjadi freelancer.\n\n6. Pengembangan keterampilan\nInvestasikan waktu dan uang untuk mengembangkan keterampilan yang dapat meningkatkan prospek karir Anda.\n\n7. Diversifikasi pendapatan\nJika memungkinkan, mulai membangun sumber pendapatan tambahan sebelum resign.\n\n8. Perencanaan pajak\nPertimbangkan implikasi pajak dari pengunduran diri Anda, terutama jika ada pesangon atau pembayaran lain.\n\n9. Evaluasi investasi\nTinjau dan sesuaikan portofolio investasi Anda sesuai dengan perubahan situasi keuangan.\n\n10. Konsultasi finansial\nPertimbangkan untuk berkonsultasi dengan perencana keuangan profesional untuk mendapatkan saran yang lebih personal.\n\nDengan mempersiapkan rencana finansial yang matang, Anda akan lebih siap menghadapi masa transisi setelah resign dan memiliki landasan yang lebih kuat untuk langkah karir selanjutnya.'),('f54a8702aad749ccba139186f6edbadd','generate images of indonesian independence day');
/*!40000 ALTER TABLE `tools_textcontent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'nurojilu_knowledgehub'
--

--
-- Dumping routines for database 'nurojilu_knowledgehub'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-10-26  9:48:45
