from pathlib import Path
from typing import Optional, Union

import psutil
import pyspark.sql.functions as f
from pyspark.sql import DataFrame, SparkSession

from blackops.core.typing import tableNames


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
                "spark.jars.packages": "io.delta:delta-spark_2.12:3.2.0,io.delta:delta-sharing-spark_2.12:3.2.0",
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


def read_table(
    config_share_path: Union[str, Path] = "config.share",
    spark: Optional[SparkSession] = None,
    share_name: str = "esic__black_ops",
    table_name: tableNames = "unsw_nb15_dataset",
) -> DataFrame:
    """
    Reads a dataset as Spark DataFrame.

    A file called `config.share` must be located in the same path where the notebook runs.
    It is possible also to specify a different directory in `config_share_path` argument.

    For example, let's suppose your notebook is in the following path:
        `/home/alumno/blackops/trabajo.ipynb`
    Then you should put the `config.share` file in:
        `/home/alumno/blackops/config.share`

    The available datasets to load for group work are:

    * `unsw_nb15_dataset`
    * `unsw_nb15_dim_attack_cat`
    * `unsw_nb15_dim_ip`
    * `unsw_nb15_dim_proto`
    * `unsw_nb15_dim_service`
    * `unsw_nb15_dim_state`
    * `unsw_nb15_features`

    Returns
    -------
    `pyspark.sql.DataFrame`:
        The requested table, as a Spark DataFrame.

    Example
    -------
    ```
    from blackops.utils.catalog import read_table

    df_main = read_table(table_name="unsw_nb15_dataset")
    dim_ip = read_table(table_name="unsw_nb15_dim_ip")
    ```
    """
    ALLOWED_TABLES = [
        "esic.unsw_nb15_dataset",
        "esic.unsw_nb15_dim_attack_cat",
        "esic.unsw_nb15_dim_ip",
        "esic.unsw_nb15_dim_proto",
        "esic.unsw_nb15_dim_service",
        "esic.unsw_nb15_dim_state",
        "esic.unsw_nb15_features",
        "esic.cybersecurity_attacks",
    ]
    if isinstance(config_share_path, str):
        config_share_path = Path(config_share_path)

    if not table_name.startswith("esic."):
        table_name = "esic." + table_name

    if table_name not in ALLOWED_TABLES:
        raise ValueError(
            f"You have selected an invalid table: {table_name}. The only allowed tables are: {ALLOWED_TABLES}"
        )

    if not config_share_path.exists():
        raise ValueError(
            f"Config share path doesn't exist: {config_share_path}. Please ensure you place `config.share` file in the same directory of your notebook."
        )
    if spark is None:
        spark = SparkSession.getActiveSession()
        if spark is None:
            spark = start_spark_session()
    return spark.read.format("deltaSharing").load(
        f"{config_share_path}#{share_name}.{table_name}"
    )
