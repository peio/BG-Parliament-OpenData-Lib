SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

DROP SCHEMA IF EXISTS `Parliament` ;
CREATE SCHEMA IF NOT EXISTS `Parliament` DEFAULT CHARACTER SET utf8 ;
USE `Parliament` ;

-- -----------------------------------------------------
-- Table `Parliament`.`MP`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Parliament`.`MP` ;

CREATE  TABLE IF NOT EXISTS `Parliament`.`MP` (
  `ID` INT(11) NOT NULL ,
  `FullName` VARCHAR(64) NULL DEFAULT NULL ,
  `PoliticalForce` VARCHAR(5) NULL DEFAULT NULL ,
  `BirthDate` DATE NULL DEFAULT NULL ,
  `MIR` TINYINT NULL DEFAULT NULL ,
  `PlaceOfBirth` VARCHAR(64) NULL DEFAULT NULL ,
  `DataUrl` VARCHAR(128) NULL DEFAULT NULL ,
  `Region` VARCHAR(20) NULL ,
  PRIMARY KEY (`ID`) ,
  UNIQUE INDEX `FullName_UNIQUE` (`FullName` ASC) )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8
COMMENT = 'Members of 41 Bulgarian Parliament' ;


-- -----------------------------------------------------
-- Table `Parliament`.`MP2Signature`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Parliament`.`MP2Signature` ;

CREATE  TABLE IF NOT EXISTS `Parliament`.`MP2Signature` (
  `MPID` INT(11) NULL DEFAULT NULL ,
  `Signature` VARCHAR(10) NULL DEFAULT '000-000' ,
  PRIMARY KEY (`MPID`, `Signature`) )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8, 
COMMENT = 'MP 2 Bills' ;


-- -----------------------------------------------------
-- Table `Parliament`.`Questions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Parliament`.`Questions` ;

CREATE  TABLE IF NOT EXISTS `Parliament`.`Questions` (
  `MPID` INT(11) NULL DEFAULT 0 ,
  `Date` DATE NULL ,
  `ToWhom` TINYTEXT NULL DEFAULT NULL ,
  `About` TEXT NULL DEFAULT NULL ,
  `QuestionSHA1` CHAR(40) NULL ,
  `QID` INT NOT NULL AUTO_INCREMENT ,
  PRIMARY KEY (`QID`) ,
  UNIQUE INDEX `Question_UNIQUE` (`QuestionSHA1` ASC) ,
  INDEX `MP_INDEX` (`MPID` ASC) )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8, 
COMMENT = 'Questions asked' ;


-- -----------------------------------------------------
-- Table `Parliament`.`Bills`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Parliament`.`Bills` ;

CREATE  TABLE IF NOT EXISTS `Parliament`.`Bills` (
  `ID` INT NOT NULL ,
  `Signature` VARCHAR(10) NULL ,
  `BillName` TEXT NULL ,
  `Type` VARCHAR(16) NULL ,
  `Date` DATE NULL ,
  `Status` VARCHAR(45) NULL ,
  PRIMARY KEY (`ID`) ,
  INDEX `Signarure` (`Signature` ASC) ,
  UNIQUE INDEX `ID_UNIQUE` (`ID` ASC) )
ENGINE = MyISAM;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
