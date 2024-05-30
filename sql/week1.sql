-- db: daytrip-- ERROR 1824 (HY000): Failed to open the referenced table '~~~' -> 先に参照されるtableを作成する必要あり
-- float is faster but only 7 digits

CREATE TABLE `mrts` (
  `id` INT AUTO_INCREMENT,
  `name` VARCHAR(20) UNIQUE NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `categories` (
  `id` INT AUTO_INCREMENT,
  `name` VARCHAR(50) UNIQUE NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `attractions` (
  `id` INT AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `description` TEXT NOT NULL,
  `address` VARCHAR(255) NOT NULL,
  `transport` TEXT NOT NULL,
  `rate` INT NOT NULL,
  `latitude` DECIMAL(8,6) NOT NULL,
  `longitude` DECIMAL(9,6) NOT NULL,
  `mrt_id` INT NOT NULL,
  `category_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (`mrt_id`) REFERENCES `mrts` (`id`) ON UPDATE CASCADE ON DELETE CASCADE,
  INDEX `attractions_name` (`name`)
);

CREATE TABLE `images` (
  `id` INT AUTO_INCREMENT,
  `url` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `attraction_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
);



