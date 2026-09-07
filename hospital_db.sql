-- Create the database
CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- TABLE FOR allergy
CREATE TABLE `allergy` (
  `AllergyCode` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  `Triggers` varchar(255) DEFAULT NULL,
  `Severity` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`AllergyCode`)
); 

-- TABLE FOR room
CREATE TABLE `room` (
  `RoomNumber` int NOT NULL,
  `RoomType` enum('General','ICU','Private') DEFAULT NULL,
  `Wing` varchar(50) DEFAULT NULL,
  `NursingUnit` int DEFAULT NULL,
  PRIMARY KEY (`RoomNumber`)
); 

-- TABLE FOR bed
CREATE TABLE `bed` (
  `BedID` int NOT NULL AUTO_INCREMENT,
  `RoomNumber` int DEFAULT NULL,
  `BedLabel` varchar(10) DEFAULT NULL,
  `Availability` enum('Available','Occupied') DEFAULT 'Available',
  PRIMARY KEY (`BedID`),
  KEY `RoomNumber` (`RoomNumber`),
  CONSTRAINT `bed_ibfk_1` FOREIGN KEY (`RoomNumber`) REFERENCES `room` (`RoomNumber`)
); 



-- TABLE FOR clinic
CREATE TABLE `clinic` (
  `ClinicID` int NOT NULL AUTO_INCREMENT,
  `Address` varchar(100) DEFAULT NULL,
  `Type` varchar(50) DEFAULT NULL,
  `Name` varchar(100) NOT NULL,
  PRIMARY KEY (`ClinicID`)
); 


-- TABLE FOR employee
CREATE TABLE `employee` (
  `EmploymentNumber` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `TelephoneNumber` varchar(20) DEFAULT NULL,
  `SSN` varchar(15) DEFAULT NULL,
  `Gender` varchar(10) DEFAULT NULL,
  `Position` varchar(50) DEFAULT NULL,
  `ClinicID` int DEFAULT NULL,
  PRIMARY KEY (`EmploymentNumber`),
  KEY `ClinicID` (`ClinicID`),
  CONSTRAINT `employee_ibfk_1` FOREIGN KEY (`ClinicID`) REFERENCES `clinic` (`ClinicID`)
); 

-- TABLE FOR illness
CREATE TABLE `illness` (
  `IllnessCode` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  `Description` text,
  `Severity` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`IllnessCode`)
); 


-- TABLE FOR medication
CREATE TABLE `medication` (
  `MedicationCode` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  `Description` text,
  `Quantity` int DEFAULT NULL,
  `YearUsage` int DEFAULT NULL,
  `UnitCost` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`MedicationCode`)
); 




-- TABLE FOR operationtheater
CREATE TABLE `operationtheater` (
  `TheaterID` int NOT NULL AUTO_INCREMENT,
  `Location` varchar(100) DEFAULT NULL,
  `Capacity` int DEFAULT NULL,
  PRIMARY KEY (`TheaterID`)
); 



-- TABLE FOR owner
CREATE TABLE `owner` (
  `OwnerID` int NOT NULL AUTO_INCREMENT,
  `OwnerType` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`OwnerID`)
); 


-- TABLE FOR physician
CREATE TABLE `physician` (
  `EmploymentNumber` int NOT NULL,
  `Specialty` varchar(100) DEFAULT NULL,
  `Salary` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`EmploymentNumber`),
  CONSTRAINT `physician_ibfk_1` FOREIGN KEY (`EmploymentNumber`) REFERENCES `employee` (`EmploymentNumber`)
); 


-- TABLE FOR patient
CREATE TABLE `patient` (
  `PatientNumber` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `TelephoneNumber` varchar(20) DEFAULT NULL,
  `SSN` varchar(15) DEFAULT NULL,
  `Gender` varchar(10) DEFAULT NULL,
  `DOB` date DEFAULT NULL,
  `BloodType` varchar(5) DEFAULT NULL,
  `EmploymentNumber` int DEFAULT NULL,
  `Illness` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`PatientNumber`),
  KEY `EmploymentNumber` (`EmploymentNumber`),
  CONSTRAINT `patient_ibfk_1` FOREIGN KEY (`EmploymentNumber`) REFERENCES `physician` (`EmploymentNumber`) ON DELETE SET NULL
); 


-- TABLE FOR consultation
CREATE TABLE `consultation` (
  `ConsultationID` int NOT NULL AUTO_INCREMENT,
  `PatientNumber` int NOT NULL,
  `EmploymentNumber` int NOT NULL,
  `ConsultationDate` date DEFAULT NULL,
  `Notes` text,
  `startTime` time DEFAULT NULL,
  `endTime` time DEFAULT NULL,
  PRIMARY KEY (`ConsultationID`),
  KEY `PatientNumber` (`PatientNumber`),
  KEY `EmploymentNumber` (`EmploymentNumber`),
  CONSTRAINT `consultation_ibfk_1` FOREIGN KEY (`PatientNumber`) REFERENCES `patient` (`PatientNumber`),
  CONSTRAINT `consultation_ibfk_2` FOREIGN KEY (`EmploymentNumber`) REFERENCES `physician` (`EmploymentNumber`)
); 




-- TABLE FOR detectsallergy
CREATE TABLE `detectsallergy` (
  `ConsultationID` int NOT NULL,
  `AllergyCode` int NOT NULL,
  PRIMARY KEY (`ConsultationID`,`AllergyCode`),
  KEY `AllergyCode` (`AllergyCode`),
  CONSTRAINT `detectsallergy_ibfk_1` FOREIGN KEY (`ConsultationID`) REFERENCES `consultation` (`ConsultationID`),
  CONSTRAINT `detectsallergy_ibfk_2` FOREIGN KEY (`AllergyCode`) REFERENCES `allergy` (`AllergyCode`)
); 



-- TABLE FOR diagnoses
CREATE TABLE `diagnoses` (
  `ConsultationID` int NOT NULL,
  `IllnessCode` int NOT NULL,
  PRIMARY KEY (`ConsultationID`,`IllnessCode`),
  KEY `IllnessCode` (`IllnessCode`),
  CONSTRAINT `diagnoses_ibfk_1` FOREIGN KEY (`ConsultationID`) REFERENCES `consultation` (`ConsultationID`),
  CONSTRAINT `diagnoses_ibfk_2` FOREIGN KEY (`IllnessCode`) REFERENCES `illness` (`IllnessCode`)
); 





-- TABLE FOR prescribes
CREATE TABLE `prescribes` (
  `EmploymentNumber` int NOT NULL,
  `PatientNumber` int NOT NULL,
  `MedicationCode` int NOT NULL,
  `Dosage` varchar(50) DEFAULT NULL,
  `Frequency` varchar(50) DEFAULT NULL,
  `DatePrescribed` date NOT NULL,
  PRIMARY KEY (`EmploymentNumber`,`PatientNumber`,`MedicationCode`,`DatePrescribed`),
  KEY `PatientNumber` (`PatientNumber`),
  KEY `MedicationCode` (`MedicationCode`),
  CONSTRAINT `prescribes_ibfk_1` FOREIGN KEY (`EmploymentNumber`) REFERENCES `physician` (`EmploymentNumber`),
  CONSTRAINT `prescribes_ibfk_2` FOREIGN KEY (`PatientNumber`) REFERENCES `patient` (`PatientNumber`),
  CONSTRAINT `prescribes_ibfk_3` FOREIGN KEY (`MedicationCode`) REFERENCES `medication` (`MedicationCode`)
); 


-- TABLE FOR shift
CREATE TABLE `shift` (
  `EmploymentNumber` int DEFAULT NULL,
  `ClinicID` int NOT NULL,
  `ShiftDate` date NOT NULL,
  `BeginTime` time NOT NULL,
  `EndTime` time NOT NULL,
  PRIMARY KEY (`ClinicID`,`ShiftDate`,`BeginTime`,`EndTime`),
  CONSTRAINT `shift_ibfk_1` FOREIGN KEY (`ClinicID`) REFERENCES `clinic` (`ClinicID`)
); 

-- TABLE FOR schedule
CREATE TABLE `schedule` (
  `EmploymentNumber` int NOT NULL,
  `ClinicID` int NOT NULL,
  `ScheduleDate` date NOT NULL,
  `BeginTime` time NOT NULL,
  `EndTime` time NOT NULL,
  PRIMARY KEY (`EmploymentNumber`,`ClinicID`,`ScheduleDate`,`BeginTime`,`EndTime`),
  KEY `ClinicID` (`ClinicID`,`ScheduleDate`,`BeginTime`,`EndTime`),
  CONSTRAINT `schedule_ibfk_1` FOREIGN KEY (`EmploymentNumber`) REFERENCES `employee` (`EmploymentNumber`) ON DELETE CASCADE,
  CONSTRAINT `schedule_ibfk_2` FOREIGN KEY (`ClinicID`, `ScheduleDate`, `BeginTime`, `EndTime`) REFERENCES `shift` (`ClinicID`, `ShiftDate`, `BeginTime`, `EndTime`)
); 


-- TABLE FOR supportstaff
CREATE TABLE `supportstaff` (
  `EmploymentNumber` int NOT NULL,
  `Salary` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`EmploymentNumber`),
  CONSTRAINT `supportstaff_ibfk_1` FOREIGN KEY (`EmploymentNumber`) REFERENCES `employee` (`EmploymentNumber`)
); 



-- TABLE FOR surgeon
CREATE TABLE `surgeon` (
  `EmploymentNumber` int NOT NULL,
  `Specialty` varchar(100) DEFAULT NULL,
  `Contract` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`EmploymentNumber`),
  CONSTRAINT `surgeon_ibfk_1` FOREIGN KEY (`EmploymentNumber`) REFERENCES `employee` (`EmploymentNumber`)
); 


-- TABLE FOR surgeryskill
CREATE TABLE `surgeryskill` (
  `SkillCode` int NOT NULL AUTO_INCREMENT,
  `Description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`SkillCode`)
); 



-- TABLE FOR surgerytype
CREATE TABLE `surgerytype` (
  `SurgeryCode` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) DEFAULT NULL,
  `Category` varchar(100) DEFAULT NULL,
  `AnatomicalLocation` varchar(100) DEFAULT NULL,
  `SpecialNeeds` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`SurgeryCode`)
); 


-- TABLE FOR surgery
CREATE TABLE `surgery` (
  `SurgeryID` int NOT NULL AUTO_INCREMENT,
  `SurgeryDate` date DEFAULT NULL,
  `SurgeryTime` time DEFAULT NULL,
  `PatientNumber` int DEFAULT NULL,
  `SurgeonEmploymentNumber` int DEFAULT NULL,
  `TheaterID` int DEFAULT NULL,
  `SurgeryCode` int DEFAULT NULL,
  `StartTime` time DEFAULT NULL,
  `EndTime` time DEFAULT NULL,
  PRIMARY KEY (`SurgeryID`),
  KEY `PatientNumber` (`PatientNumber`),
  KEY `SurgeonEmploymentNumber` (`SurgeonEmploymentNumber`),
  KEY `TheaterID` (`TheaterID`),
  KEY `SurgeryCode` (`SurgeryCode`),
  CONSTRAINT `surgery_ibfk_1` FOREIGN KEY (`PatientNumber`) REFERENCES `patient` (`PatientNumber`),
  CONSTRAINT `surgery_ibfk_2` FOREIGN KEY (`SurgeonEmploymentNumber`) REFERENCES `surgeon` (`EmploymentNumber`),
  CONSTRAINT `surgery_ibfk_3` FOREIGN KEY (`TheaterID`) REFERENCES `operationtheater` (`TheaterID`),
  CONSTRAINT `surgery_ibfk_4` FOREIGN KEY (`SurgeryCode`) REFERENCES `surgerytype` (`SurgeryCode`)
); 
-- TABLE FOR requires
CREATE TABLE `requires` (
  `SurgeryCode` int NOT NULL,
  `SkillCode` int NOT NULL,
  PRIMARY KEY (`SurgeryCode`,`SkillCode`),
  KEY `SkillCode` (`SkillCode`),
  CONSTRAINT `requires_ibfk_1` FOREIGN KEY (`SurgeryCode`) REFERENCES `surgerytype` (`SurgeryCode`),
  CONSTRAINT `requires_ibfk_2` FOREIGN KEY (`SkillCode`) REFERENCES `surgeryskill` (`SkillCode`)
); 


-- TABLE FOR nurse
CREATE TABLE `nurse` (
  `EmploymentNumber` int NOT NULL,
  `YearsOfExperience` int DEFAULT NULL,
  `Grade` varchar(10) DEFAULT NULL,
  `Salary` decimal(10,2) DEFAULT NULL,
  `SurgeryCode` int DEFAULT NULL,
  PRIMARY KEY (`EmploymentNumber`),
  KEY `SurgeryCode` (`SurgeryCode`),
  CONSTRAINT `nurse_ibfk_1` FOREIGN KEY (`EmploymentNumber`) REFERENCES `employee` (`EmploymentNumber`),
  CONSTRAINT `nurse_ibfk_2` FOREIGN KEY (`SurgeryCode`) REFERENCES `surgerytype` (`SurgeryCode`)
); 

-- TABLE FOR possesses
CREATE TABLE `possesses` (
  `EmploymentNumber` int NOT NULL,
  `SkillCode` int NOT NULL,
  PRIMARY KEY (`EmploymentNumber`,`SkillCode`),
  KEY `SkillCode` (`SkillCode`),
  CONSTRAINT `possesses_ibfk_1` FOREIGN KEY (`EmploymentNumber`) REFERENCES `nurse` (`EmploymentNumber`),
  CONSTRAINT `possesses_ibfk_2` FOREIGN KEY (`SkillCode`) REFERENCES `surgeryskill` (`SkillCode`)
); 


-- TABLE FOR treatedfor
CREATE TABLE `treatedfor` (
  `EmploymentNumber` int NOT NULL,
  `IllnessCode` int NOT NULL,
  PRIMARY KEY (`EmploymentNumber`,`IllnessCode`),
  KEY `IllnessCode` (`IllnessCode`),
  CONSTRAINT `treatedfor_ibfk_1` FOREIGN KEY (`EmploymentNumber`) REFERENCES `employee` (`EmploymentNumber`),
  CONSTRAINT `treatedfor_ibfk_2` FOREIGN KEY (`IllnessCode`) REFERENCES `illness` (`IllnessCode`)
);

-- TABLE FOR hasallergy
CREATE TABLE `hasallergy` (
  `PatientNumber` int NOT NULL,
  `AllergyCode` int NOT NULL,
  PRIMARY KEY (`PatientNumber`,`AllergyCode`),
  KEY `AllergyCode` (`AllergyCode`),
  CONSTRAINT `hasallergy_ibfk_1` FOREIGN KEY (`PatientNumber`) REFERENCES `patient` (`PatientNumber`),
  CONSTRAINT `hasallergy_ibfk_2` FOREIGN KEY (`AllergyCode`) REFERENCES `allergy` (`AllergyCode`)
); 



-- TABLE FOR hasillness
CREATE TABLE `hasillness` (
  `PatientNumber` int NOT NULL,
  `IllnessCode` int NOT NULL,
  PRIMARY KEY (`PatientNumber`,`IllnessCode`),
  KEY `IllnessCode` (`IllnessCode`),
  CONSTRAINT `hasillness_ibfk_1` FOREIGN KEY (`PatientNumber`) REFERENCES `patient` (`PatientNumber`),
  CONSTRAINT `hasillness_ibfk_2` FOREIGN KEY (`IllnessCode`) REFERENCES `illness` (`IllnessCode`)
); 

-- TABLE FOR ownership
CREATE TABLE `ownership` (
  `OwnerID` int NOT NULL,
  `EmploymentNumber` int NOT NULL,
  `ClinicID` int NOT NULL,
  `OwnershipPercentage` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`OwnerID`,`EmploymentNumber`,`ClinicID`),
  KEY `EmploymentNumber` (`EmploymentNumber`),
  KEY `ClinicID` (`ClinicID`),
  CONSTRAINT `ownership_ibfk_1` FOREIGN KEY (`OwnerID`) REFERENCES `owner` (`OwnerID`),
  CONSTRAINT `ownership_ibfk_2` FOREIGN KEY (`EmploymentNumber`) REFERENCES `physician` (`EmploymentNumber`),
  CONSTRAINT `ownership_ibfk_3` FOREIGN KEY (`ClinicID`) REFERENCES `clinic` (`ClinicID`)
); 

-- TABLE FOR interactswith
CREATE TABLE `interactswith` (
  `MedicationCode1` int NOT NULL,
  `MedicationCode2` int NOT NULL,
  `Severity` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`MedicationCode1`,`MedicationCode2`),
  KEY `MedicationCode2` (`MedicationCode2`),
  CONSTRAINT `interactswith_ibfk_1` FOREIGN KEY (`MedicationCode1`) REFERENCES `medication` (`MedicationCode`),
  CONSTRAINT `interactswith_ibfk_2` FOREIGN KEY (`MedicationCode2`) REFERENCES `medication` (`MedicationCode`)
); 



-- TABLE FOR medicalcorporation
CREATE TABLE `medicalcorporation` (
  `OwnerID` int NOT NULL,
  `CorporationName` varchar(100) DEFAULT NULL,
  `Headquarters` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`OwnerID`),
  CONSTRAINT `medicalcorporation_ibfk_1` FOREIGN KEY (`OwnerID`) REFERENCES `owner` (`OwnerID`)
); 


-- TABLE FOR inpatient
CREATE TABLE `inpatient` (
  `PatientNumber` int NOT NULL,
  `BedLabel` varchar(20) DEFAULT NULL,
  `NursingUnit` varchar(50) DEFAULT NULL,
  `RoomNumber` varchar(20) DEFAULT NULL,
  `Wing` varchar(50) DEFAULT NULL,
  `DateOfAdmission` date DEFAULT NULL,
  `EmploymentNumber` int DEFAULT NULL,
  `BedID` int DEFAULT NULL,
  PRIMARY KEY (`PatientNumber`),
  UNIQUE KEY `unique_room_bed` (`RoomNumber`,`BedID`),
  KEY `EmploymentNumber` (`EmploymentNumber`),
  CONSTRAINT `inpatient_ibfk_1` FOREIGN KEY (`PatientNumber`) REFERENCES `patient` (`PatientNumber`),
  CONSTRAINT `inpatient_ibfk_2` FOREIGN KEY (`EmploymentNumber`) REFERENCES `nurse` (`EmploymentNumber`)
); 




-- TABLE FOR medicaldata
CREATE TABLE `medicaldata` (
  `PatientNumber` int NOT NULL,
  `Date` date NOT NULL,
  `BloodSugar` decimal(5,2) DEFAULT NULL,
  `TotalCholesterol` decimal(5,2) DEFAULT NULL,
  `LDLCholesterol` decimal(5,2) DEFAULT NULL,
  `HDLCholesterol` decimal(5,2) DEFAULT NULL,
  `TriglyceridesCholesterol` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`PatientNumber`,`Date`),
  CONSTRAINT `medicaldata_ibfk_1` FOREIGN KEY (`PatientNumber`) REFERENCES `patient` (`PatientNumber`)
);