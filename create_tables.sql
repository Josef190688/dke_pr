DROP TABLE IF EXISTS web122_db10.securities_position, web122_db10.deposit, web122_db10.person, web122_db10.account CASCADE;

CREATE TABLE `web122_db10`.`account` (
  `account_id` INT NOT NULL AUTO_INCREMENT COMMENT "Eindeutige ID des Kontos einer Person",
  `account_balance_in_euro` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT "Vermögen am Konto einer Person in Euro",
  `displayed_currency` ENUM('EUR', 'USD') NOT NULL DEFAULT 'EUR' COMMENT "Währung, in der das Vermögen einer Person im UI angezeigt wird",
  PRIMARY KEY (`account_id`)
);

CREATE TABLE `web122_db10`.`person` (
  `person_id` INT NOT NULL AUTO_INCREMENT COMMENT "Eindeutige ID einer Person",
  `username` VARCHAR(255) NOT NULL UNIQUE COMMENT "Eindeutiger Username einer Person",
  `password_hash` VARCHAR(255) NOT NULL COMMENT "Hashwert eines Passworts einer Person",
  `first_name` VARCHAR(255) NOT NULL COMMENT "Vorname einer Person",
  `last_name` VARCHAR(255) NOT NULL COMMENT "Nachname einer Person",
  `birth_date` DATETIME NULL COMMENT "Geburtsdatum einer Person",
  `phone_number` VARCHAR(255) NULL COMMENT "Telefonnummer einer Person",
  `profession` VARCHAR(255) NULL COMMENT "Beruf einer Person",
  `is_admin` TINYINT NOT NULL COMMENT "Zeigt, ob Person Administrator ist",
  `persons_account_id` INT NOT NULL UNIQUE COMMENT "Eindeutige ID des Kontos einer Person",
  PRIMARY KEY (`person_id`),
  INDEX `first_name_index` (`first_name`) VISIBLE,
  INDEX `last_name_index` (`last_name`) VISIBLE,
  CONSTRAINT `FKC_account`
    FOREIGN KEY (`persons_account_id`)
    REFERENCES `web122_db10`.`account` (`account_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE `web122_db10`.`deposit` (
  `deposit_id` INT NOT NULL AUTO_INCREMENT COMMENT "Eindeutige ID des Depots einer Person",
  `deposit_name` VARCHAR(255) NOT NULL UNIQUE COMMENT "Eindeutiger Depotname",
  `deposits_person_id` INT NOT NULL COMMENT "Eindeutige ID des Kontos einer Person",
  PRIMARY KEY (`deposit_id`),
  CONSTRAINT `FKC_person`
    FOREIGN KEY (`deposits_person_id`)
    REFERENCES `web122_db10`.`person` (`person_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE `web122_db10`.`securities_position` (
  `securities_position_id` INT NOT NULL AUTO_INCREMENT COMMENT "Eindeutige ID einer Wertpapier-Position in einem Depot",
  `company_id` INT NOT NULL COMMENT "Eindeutige ID der Firma des Wertpapieres",
  `amount` INT NOT NULL COMMENT "Anzahl der Wertpapiere in dieser Position",
  `market_id` INT NOT NULL COMMENT "Eindeutige ID der Börse, an der das Wertpapier erworben wurde",
  `purchase_timestamp` TIMESTAMP NOT NULL COMMENT "Zeitpunkt, an dem die Wertpapiere in dieser Position an der Börse gekauft wurden",
  `positions_deposit_id` INT NOT NULL COMMENT "Eindeutige ID des Depots einer Person",
  PRIMARY KEY (`securities_position_id`),
  CONSTRAINT `FKC_deposit`
    FOREIGN KEY (`positions_deposit_id`)
    REFERENCES `web122_db10`.`deposit` (`deposit_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE  
);
