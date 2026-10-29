-- 0. DDL: full schema (9 tables) -------------------------------------------
CREATE DATABASE IF NOT EXISTS wardrobe_python;
USE wardrobe_python;

CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `name` varchar(120) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `wear_limit` int NOT NULL,
  `sort_order` int NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `brand` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `season` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `slug` varchar(30) NOT NULL,
  `sort_order` int NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `clothingitem` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `category_id` int NOT NULL,
  `brand` varchar(80) DEFAULT NULL,
  `season` varchar(30) DEFAULT NULL,
  `brand_id` int DEFAULT NULL,
  `season_id` int DEFAULT NULL,
  `name` varchar(120) NOT NULL,
  `color` varchar(30) NOT NULL,
  `formality_score` int NOT NULL,
  `purchase_price` decimal(10,2) NOT NULL,
  `wear_count` int NOT NULL DEFAULT 0,
  `wear_count_since_wash` int NOT NULL DEFAULT 0,
  `status` varchar(20) NOT NULL DEFAULT 'CLEAN',
  `last_washed_at` date DEFAULT NULL,
  `sent_to_laundry_at` date DEFAULT NULL,
  `image_url` varchar(500) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `ix_clothingitem_user_category` (`user_id`,`category_id`),
  KEY `ix_clothingitem_user_season` (`user_id`,`season_id`),
  KEY `ix_clothingitem_user_brand` (`user_id`,`brand_id`),
  CONSTRAINT `fk_clothingitem_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_clothingitem_category` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_clothingitem_brand` FOREIGN KEY (`brand_id`) REFERENCES `brand` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_clothingitem_season` FOREIGN KEY (`season_id`) REFERENCES `season` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `outfit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(120) NOT NULL,
  `occasion` enum('CASUAL','SMART_CASUAL','WORK','FORMAL') NOT NULL,
  `notes` text,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `fk_outfit_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `outfititem` (
  `id` int NOT NULL AUTO_INCREMENT,
  `outfit_id` int NOT NULL,
  `item_id` int NOT NULL,
  `position` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_outfit_item` (`outfit_id`,`item_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `fk_outfititem_outfit` FOREIGN KEY (`outfit_id`) REFERENCES `outfit` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_outfititem_item` FOREIGN KEY (`item_id`) REFERENCES `clothingitem` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wearlog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `item_id` int NOT NULL,
  `outfit_id` int DEFAULT NULL,
  `date_worn` date NOT NULL,
  `weather_temp` int DEFAULT NULL,
  `notes` text,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `outfit_id` (`outfit_id`),
  KEY `ix_wearlog_user_date` (`user_id`,`date_worn`),
  KEY `ix_wearlog_item_date` (`item_id`,`date_worn`),
  CONSTRAINT `fk_wearlog_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wearlog_item` FOREIGN KEY (`item_id`) REFERENCES `clothingitem` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wearlog_outfit` FOREIGN KEY (`outfit_id`) REFERENCES `outfit` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `colorcompatibility` (
  `id` int NOT NULL AUTO_INCREMENT,
  `color1` varchar(30) NOT NULL,
  `color2` varchar(30) NOT NULL,
  `score` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_color_pair` (`color1`,`color2`),
  KEY `ix_colorcompat_color2` (`color2`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE OR REPLACE VIEW `V_ItemCostPerWear` AS
SELECT
  ci.id,
  ci.user_id,
  ci.name,
  cat.name AS category,
  ci.purchase_price,
  (SELECT COUNT(*) FROM WearLog w WHERE w.item_id = ci.id) AS wear_count,
  CASE
    WHEN ci.sent_to_laundry_at IS NOT NULL
      OR (SELECT COUNT(*) FROM WearLog w
          WHERE w.item_id = ci.id
            AND w.date_worn >= COALESCE(ci.last_washed_at, '1000-01-01')) >= cat.wear_limit
    THEN 'LAUNDRY' ELSE 'CLEAN'
  END AS status,
  ci.purchase_price / GREATEST(
    (SELECT COUNT(*) FROM WearLog w WHERE w.item_id = ci.id), 1) AS cost_per_wear
FROM ClothingItem ci
JOIN Category cat ON cat.id = ci.category_id;

