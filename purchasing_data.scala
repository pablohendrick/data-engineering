// Importing libraries
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

// Creating a Spark session
val spark = SparkSession.builder()
  .appName("PurchaseClassification")
  .master("local[*]") // Change to desired execution mode (local, cluster, etc.)
  .getOrCreate()

// Loading data from the file (replace 'file/path' with the actual path to your file)
val filePath = "file/path"
val purchaseData = spark.read.option("header", "true").csv(filePath)

// Displaying the schema of the data
purchaseData.printSchema()

// Creating a column to classify purchases based on the value
val classifiedData = purchaseData.withColumn("Classification",
  when(col("PurchaseValue") < 100, "Purchase below $100")
  .otherwise(when(col("PurchaseValue") <= 1000, "Purchase up to $1000")
  .otherwise("Purchase above $1000")))

// Displaying the first few rows of classified data
classifiedData.show()

// Saving the classified data into the Data Lake (replace 'path/to/save' with desired path)
val savePath = "path/to/save"
classifiedData.write.mode("overwrite").parquet(savePath)

// Stopping the Spark session
spark.stop()
