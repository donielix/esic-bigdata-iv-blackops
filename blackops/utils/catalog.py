import pyspark.sql.functions as f
from pyspark.sql import DataFrame, SparkSession


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
