
-- Note: I found only the below 3 questions on the file

--QUESTION 1
  SELECT PersonName , RiskLevel   FROM 
  (
  select P.PersonName , R.RiskLevel ,P.PersonID, DENSE_RANK()OVER(PARTITION BY R.PersonID ORDER BY [RiskDateTime] DESC) RN
    FROM [PersonDatabase].[dbo].[Person] P
	LEFT JOIN [PersonDatabase].[dbo].[Risk] R
	ON P.PersonID = R.PersonID
) X
WHERE RN = 1



--QUESTION 2
SELECT TRIM(REPLACE(CASE WHEN CHARINDEX('(',[PersonName],1) > 0 THEN SUBSTRING([PersonName],1,CHARINDEX('(',[PersonName],1)-1) + ' ' + SUBSTRING([PersonName],CHARINDEX(')',[PersonName],1)+1,LEN([PersonName])) ELSE [PersonName] END,')','')) AS Full_Name
	  ,CASE WHEN CHARINDEX('(',[PersonName],1) > 0 THEN  SUBSTRING([PersonName],CHARINDEX('(',[PersonName],1)+1,CHARINDEX(')',[PersonName],1)-CHARINDEX('(',[PersonName],1)-1) ELSE '' END AS Nick_Name
  FROM [PersonDatabase].[dbo].[Person]




--QUESTION 6
 SELECT DISTINCT [PersonID]
      ,[AttributedPayer]
	  ,CONVERT(VARCHAR(20),AVG([RiskScore]) OVER (PARTITION BY [PersonID]   
                                            ORDER BY [RiskDateTime]   
                                           ),1) AS MovingAvg  
  FROM [PersonDatabase].[dbo].[Risk]
  



/*************************************************************************************************/


USE PersonDatabase
GO

CREATE TABLE dbo.Contracts
(
	PersonID INT
	, ContractStartDate datetime2(3)
	, ContractEndDate datetime2(3)
)

GO




BULK INSERT Contracts
FROM 'D:\dbo.Contracts.txt'
WITH
(
    FIRSTROW = 2, -- as 1st one is header
    FIELDTERMINATOR = '	',  --CSV field delimiter
    ROWTERMINATOR = '\n',   --Use to shift the control to next row
    TABLOCK
)
