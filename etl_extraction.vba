Sub ETL_SQLServer_To_Excel()
    ' ADO object references
    Dim conn As Object
    Dim rs As Object
    Dim query As String
    
    ' Define the SQL Server database connection string
    Dim connectionString As String
    connectionString = "Provider=SQLOLEDB;Data Source=YourSQLServer;Initial Catalog=YourDatabase;User ID=YourUser;Password=YourPassword;"
    
    ' Initialize the connection and recordset objects
    Set conn = CreateObject("ADODB.Connection")
    Set rs = CreateObject("ADODB.Recordset")
    
    ' Connect to the SQL Server database
    conn.Open connectionString
    
    ' SQL query to extract data from the subscriptions table
    query = "SELECT * FROM SubscriptionsTable;"
    
    ' Execute the query
    rs.Open query, conn
    
    ' Define the destination worksheet
    Dim destinationSheet As Worksheet
    Set destinationSheet = ThisWorkbook.Sheets("DestinationSheet")
    
    ' Clear existing data in the destination sheet
    destinationSheet.Cells.Clear
    
    ' Copy header to the destination sheet
    For i = 1 To rs.Fields.Count
        destinationSheet.Cells(1, i).Value = rs.Fields(i - 1).Name
    Next i
    
    ' Copy data to the destination sheet
    If Not rs.EOF Then
        destinationSheet.Range("A2").CopyFromRecordset rs
    End If
    
    ' Close the connection and recordset
    rs.Close
    conn.Close
    
    ' Release resources
    Set rs = Nothing
    Set conn = Nothing
    
    ' Completion message
    MsgBox "ETL completed successfully!"
End Sub
