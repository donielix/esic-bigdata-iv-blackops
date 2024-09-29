import psutil
import pyspark.sql.functions as f
from pyspark.sql import DataFrame, SparkSession


def start_spark_session() -> SparkSession:
    """
    Initializes a SparkSession locally with Delta catalog enabled, using half of the total RAM available in
    the system.
    """
    driver_memory = round(psutil.virtual_memory().total / 1024**3 / 2)
    spark = (
        SparkSession.Builder()
        .master("local[*]")
        .config(
            map={
                "spark.driver.memory": f"{driver_memory}g",
                "spark.jars.packages": "io.delta:delta-spark_2.12:3.2.0",
                "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
                "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                "spark.databricks.delta.retentionDurationCheck.enabled": "false",
                "spark.sql.catalogImplementation": "hive",
                "spark.sql.repl.eagerEval.enabled": "true",
                "spark.sql.repl.eagerEval.truncate": "100",
            }
        )
        .getOrCreate()
    )
    return spark


def get_detailed_tables_info(spark: SparkSession) -> DataFrame:
    return (
        spark.sql("show table extended like '*'")
        .withColumn("information", f.explode(f.split("information", "\n")))
        .select(
            "*",
            f.explode(
                f.create_map(
                    f.regexp_extract("information", r"^([A-Z][\w\s]+?): (.+)$", 1),
                    f.regexp_extract("information", r"^([A-Z][\w\s]+?): (.+)$", 2),
                )
            ).alias("key", "value"),
        )
        .groupBy("namespace", "tableName")
        .pivot("key")
        .agg(f.first("value"))
        .drop("Schema")
        .orderBy("namespace", "tableName")
    )
