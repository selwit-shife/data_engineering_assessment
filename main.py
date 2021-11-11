import os
import re
import pandas as pd
import pyodbc


''' Notes:
    1. All the Print(*) statements can be uncommented and run to use as unit testing, In addition to the print messages 
        that execute after each transaction.
    2. install the required packages from the requiremnts.txt file
    3. change the DB to appropriate connection and create a Database called PersonDatabase or change to dersired Database name
    4. After executing the main.py code, Run the below code to test in SQL Server to see if data is loaded correctly.
        SELECT * FROM [PersonDatabase].[dbo].[Demographics]

        SELECT * FROM [PersonDatabase].[dbo].[Quarters_Risk]
        order by 1
    5. For future loads, Comment the Drop Table Statements to add more data to the existing one

    '''



# Place the Privia Family Medicine 113018.xlsx file in D folder and read file into df For Demographics Table
file = 'D:\Privia Family Medicine 113018.xlsx'
df = pd.read_excel(file,header=3,usecols=[1,2,3,4,5,6,7],skipfooter=3)
df.columns = df.columns.str.replace(' ','')

# Transform Data
df['Sex'] = ['M' if x == 0 else 'F' for x in df['Sex']]
df['MiddleName'] = df['MiddleName'].str[0]
df.columns = df.columns.str.replace('[^a-zA-Z^0-9]','')
df = df.fillna(value='')
#print(df)

# read file into df_QR For Quarter_Risk Table
df_QR = pd.read_excel(file,header=3,usecols=[1,8,9,10,11,12],skipfooter=3)
df_QR.columns = df_QR.columns.str.replace(' ','')

# Filter Data for Only records in which the patients risk has increased.
df_QR=df_QR[df_QR['RiskIncreasedFlag']=='Yes']
df_QR=df_QR[ ['ID', 'AttributedQ1', 'AttributedQ2' , 'RiskQ1',  'RiskQ2']]
#print (df_QR)

df_QR=pd.wide_to_long(df_QR, ["Attributed", "Risk"], i="ID", j="Quarter",suffix='\w+').reset_index()
#print (df_QR)

# Get File Name and File Date
file_name = os.path.basename(file)
file_name = str.replace(file_name,".xlsx","")
file_name=re.sub('[^a-zA-Z]+', ' ', file_name)
print(file_name)

filedate = int("".join(filter(str.isdigit, file)))
print(filedate)


# Connect to SQL Server
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=BESELAM\SQLEXPRESS;'   ## Use the appropritate Instance
                      'Database=PersonDatabase;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()


# Drop Demographics Table
cursor.execute('''
		IF EXISTS (SELECT 1 FROM SYS.tables WHERE NAME = 'Demographics')
	DROP table Demographics
               ''')
print('Demographics Table Dropped')


# Create Demographics Table
cursor.execute('''
		CREATE TABLE Demographics (
			ID int,
			FirstName nvarchar(255),
			MiddleName nvarchar(255),
			LastName nvarchar(255),
			DOB1 datetime,
			Sex varchar(1),
			FavoriteColor nvarchar(255),
			ProviderGroup nvarchar(1000),
			FileDate int
			)
               ''')
print('Demographics Table Created')


# Insert Demographics DataFrame to Demographics Table
for row in df.itertuples():
  #print(row)
  cursor.execute('''
                INSERT INTO Demographics (ID, FirstName, MiddleName ,LastName , DOB1 ,Sex , FavoriteColor ,ProviderGroup ,FileDate)
                VALUES (?,?,?,?,?,?,?,?,?)
                ''',
                row.ID,
                row.FirstName,
                row.MiddleName,
                row.LastName,
                row.DOB1,
                row.Sex,
                row.FavoriteColor,
                file_name,
                filedate
                )
print('Demographics Table is Populated')

# Drop Quarters_Risk Table
cursor.execute('''
		IF EXISTS (SELECT 1 FROM SYS.tables WHERE NAME = 'Quarters_Risk')
	DROP table Quarters_Risk
               ''')
print('Quarters_Risk Table Dropped')


# Create Quarters_Risk Table
cursor.execute('''
		CREATE TABLE Quarters_Risk (
			ID int,
			Quarter nvarchar(50),
			AttributedFlag nvarchar(50),
			Risk_Score float,
			FileDate int
			)
               ''')
print('Quarters_Risk Table Created')


# Insert Quarters_Risk DataFrame to Quarters_Risk Table
for row in df_QR.itertuples():
  #print(row)
  cursor.execute('''
                INSERT INTO Quarters_Risk (ID, Quarter, AttributedFlag ,Risk_Score ,FileDate)
                VALUES (?,?,?,?,?)
                ''',
                row.ID,
                row.Quarter,
                row.Attributed,
                row.Risk,
                filedate
                )
print('Quarters_Risk Table is Populated')

conn.commit()


