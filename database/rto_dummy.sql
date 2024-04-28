CREATE DATABASE EDI;

USE EDI;

CREATE TABLE VEHICLE_DETAILS(
	state VARCHAR(2) NOT NULL,
    district INT(2) NOT NULL,
    series_char VARCHAR(2) NOT NULL,
	series_num VARCHAR(4) NOT NULL,
    onwer_name VARCHAR(50) NOT NULL,
    onwer_mob_no VARCHAR(10) NOT NULL,
    ins_valid_from DATE,
    ins_valid_to DATE,
    puc_valid_from DATE,
    puc_valid_to DATE,
    CONSTRAINT vehicle PRIMARY KEY (state, district, series_char, series_num)
);

INSERT INTO VEHICLE_DETAILS (state, district, series_char, series_num, onwer_name, onwer_mob_no, ins_valid_from, ins_valid_to, puc_valid_from, puc_valid_to)
VALUES
('KA', 01, 'AB', '1234', 'John Doe', '9876543210', '2024-01-01', '2024-12-31', '2024-01-01', '2024-12-31'),
('MH', 02, 'CD', '5678', 'Jane Smith', '9876543211', '2024-02-01', '2024-12-31', '2024-02-01', '2024-12-31'),
('TN', 03, 'EF', '9101', 'Alice Johnson', '9876543212', '2024-03-01', '2024-12-31', '2024-03-01', '2024-12-31');

INSERT INTO VEHICLE_DETAILS (state, district, series_char, series_num, onwer_name, onwer_mob_no, ins_valid_from, ins_valid_to, puc_valid_from, puc_valid_to)
VALUES('MH', 28, 'JS', '7656', 'Mahesh Sathe', '8745124345', '2022-01-20', '2024-01-23', '2024-01-02', '2025-01-20');

INSERT INTO VEHICLE_DETAILS (state, district, series_char, series_num, onwer_name, onwer_mob_no, ins_valid_from, ins_valid_to, puc_valid_from, puc_valid_to)
VALUES('MH', 12, 'JC', '3005', 'Bhushan Sangle', '9011425556', '2022-01-20', '2024-01-23', '2024-01-02', '2025-01-20');

DROP TABLE VEHICLE_DETAILS;

SELECT * FROM VEHICLE_DETAILS
WHERE state='MH' AND district=02 AND series_char='CD' AND series_num='5678';