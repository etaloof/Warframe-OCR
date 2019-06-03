CREATE TABLE User (
	IDUser integer PRIMARY KEY AUTOINCREMENT,
	Pseudo varchar
);

CREATE TABLE Relic (
	IDRelique integer PRIMARY KEY AUTOINCREMENT,
	Name varchar,
	Era text,
	IDOwner integer,
	Quantity integer
);

CREATE TABLE RelicData (
	IDRelique integer PRIMARY KEY AUTOINCREMENT
);

