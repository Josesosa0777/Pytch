BEGIN TRANSACTION;
DROP TABLE IF EXISTS "Module";
CREATE TABLE IF NOT EXISTS "Module" (
	"ModuleID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"Name"	TEXT NOT NULL UNIQUE,
	"Description"	TEXT,
	"Author"	TEXT,
	"Revision"	TEXT,
	"Date"	TEXT,
	"Image"	BLOB,
	"ImageType"	TEXT,
	"Geometry"	TEXT,
	"TypeID"	INTEGER,
	FOREIGN KEY("TypeID") REFERENCES "VisualizationTypes"("VisualizationTypeID")
);
DROP TABLE IF EXISTS "ListSignalDetails";
CREATE TABLE IF NOT EXISTS "ListSignalDetails" (
	"ListSignalDetailID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"Label"	TEXT,
	"Offset"	NUMERIC,
	"Factor"	NUMERIC,
	"DisplayScaled"	BOOL,
	"Unit"	TEXT,
	"AliasName"	TEXT,
	"DeviceName"	TEXT,
	"SignalName"	TEXT,
	"IsCustomExpression"	BOOL,
	"CustomExpression"	TEXT,
	"CustomExpressionSignalList"	TEXT,
	"ListID"	INTEGER,
	FOREIGN KEY("ListID") REFERENCES "ListDetails"("ListDetailID")
);
DROP TABLE IF EXISTS "PlotSignalDetails";
CREATE TABLE IF NOT EXISTS "PlotSignalDetails" (
	"PlotSignalDetailID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"Label"	TEXT,
	"Offset"	NUMERIC,
	"Factor"	NUMERIC,
	"DisplayScaled"	BOOL,
	"Unit"	TEXT,
	"AliasName"	TEXT,
	"DeviceName"	TEXT,
	"SignalName"	TEXT,
	"IsCustomExpression"	BOOL,
	"CustomExpression"	TEXT,
	"CustomExpressionSignalList"	TEXT,
	"PlotID"	INTEGER,
	FOREIGN KEY("PlotID") REFERENCES "PlotDetails"("PlotDetailID")
);
DROP TABLE IF EXISTS "VisualizationTypes";
CREATE TABLE IF NOT EXISTS "VisualizationTypes" (
	"VisualizationTypeID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"Name"	TEXT NOT NULL UNIQUE
);
DROP TABLE IF EXISTS "PlotDetails";
CREATE TABLE IF NOT EXISTS "PlotDetails" (
	"PlotDetailID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"AxesName"	TEXT NOT NULL,
	"XLabel"	TEXT,
	"YLabel"	TEXT,
	"YTicks"	TEXT,
	"RowNumber"	INTEGER,
	"ColumnNumber"	INTEGER,
	"ModuleID"	INTEGER,
	FOREIGN KEY("ModuleID") REFERENCES "Module"("ModuleID")
);
DROP TABLE IF EXISTS "ListDetails";
CREATE TABLE IF NOT EXISTS "ListDetails" (
	"ListDetailID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"GroupName"	TEXT NOT NULL,
	"BackgroundColor"	TEXT,
	"ModuleID"	INTEGER,
	FOREIGN KEY("ModuleID") REFERENCES "Module"("ModuleID")
);
INSERT INTO "VisualizationTypes" ("VisualizationTypeID","Name") VALUES (1,'Plot'),
 (2,'List');
COMMIT;
