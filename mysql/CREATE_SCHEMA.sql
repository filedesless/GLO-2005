-- MySQL Workbench Forward Engineering
-- -----------------------------------------------------
-- Schema KOJOJO
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `KOJOJO` ;

-- -----------------------------------------------------
-- Schema KOJOJO
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `KOJOJO` DEFAULT CHARACTER SET utf8 ;
USE `KOJOJO` ;

-- -----------------------------------------------------
-- Table `KOJOJO`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `KOJOJO`.`User` (
  `UserId` INT NOT NULL AUTO_INCREMENT,
  `UserName` VARCHAR(45) NOT NULL,
  `PasswordHash` VARCHAR(128) NOT NULL,
  `RegistrationDate` DATE NOT NULL,
  `Email` VARCHAR(45) NOT NULL,
  `Phone` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`UserId`),
  UNIQUE INDEX `Email_UNIQUE` (`Email` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `KOJOJO`.`Category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `KOJOJO`.`Category` (
  `CategoryId` INT NOT NULL AUTO_INCREMENT,
  `Type` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`CategoryId`),
  UNIQUE INDEX `Type_UNIQUE` (`Type` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `KOJOJO`.`Town`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `KOJOJO`.`Town` (
  `TownId` INT NOT NULL AUTO_INCREMENT,
  `TownName` VARCHAR(45) NULL,
  PRIMARY KEY (`TownId`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `KOJOJO`.`Image`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `KOJOJO`.`Image` (
  `ImageId` INT NOT NULL AUTO_INCREMENT,
  `FileName` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ImageId`),
  UNIQUE INDEX `FileName_UNIQUE` (`FileName` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `KOJOJO`.`Product`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `KOJOJO`.`Product` (
  `ProductId` INT NOT NULL AUTO_INCREMENT,
  `ProductName` VARCHAR(45) NOT NULL,
  `Price` DECIMAL(10,2) NOT NULL,
  `Description` VARCHAR(300) NOT NULL,
  `Date` DATETIME NOT NULL,
  `CategoryId` INT NOT NULL,
  `UserId` INT NOT NULL,
  `TownId` INT NOT NULL,
  `ImageId` INT NULL,
  PRIMARY KEY (`ProductId`),
  INDEX `fk_Product_User_UserId_idx` (`UserId` ASC),
  INDEX `fk_Product_Town_TownId_idx` (`TownId` ASC),
  INDEX `Product_ProductName_idx` USING BTREE (`ProductName` ASC),
  INDEX `fk_Product_Image_ImageId_idx` (`ImageId` ASC),
  CONSTRAINT `fk_Product_Category_CategoryId`
    FOREIGN KEY (`CategoryId`)
    REFERENCES `KOJOJO`.`Category` (`CategoryId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Product_User_UserId`
    FOREIGN KEY (`UserId`)
    REFERENCES `KOJOJO`.`User` (`UserId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Product_Town_TownId`
    FOREIGN KEY (`TownId`)
    REFERENCES `KOJOJO`.`Town` (`TownId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Product_Image_ImageId`
    FOREIGN KEY (`ImageId`)
    REFERENCES `KOJOJO`.`Image` (`ImageId`)
    ON DELETE SET NULL
    ON UPDATE SET NULL)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `KOJOJO`.`Session`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `KOJOJO`.`Session` (
  `SessionId` VARCHAR(32) NOT NULL,
  `UserId` INT NOT NULL,
  PRIMARY KEY (`SessionId`),
  INDEX `UserID_idx` (`UserId` ASC),
  CONSTRAINT `fk_Session_User_UserId`
    FOREIGN KEY (`UserId`)
    REFERENCES `KOJOJO`.`User` (`UserId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

