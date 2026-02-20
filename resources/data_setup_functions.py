"""
Helper functions for setting up Databricks Unity Catalog resources and file operations.
"""
import os
import logging
import requests
import pandas as pd
import io
from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)

def create_catalog_and_schema(spark, catalog: str, schema: str):
    """Create catalog and schema if they don't exist."""
    try:
        # spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
        logger.info(f"Catalog {catalog} and schema {schema} ensured.")
    except Exception as e:
        logger.error(f"Failed to create catalog or schema: {e}")
        raise

def create_volume(spark, catalog: str, schema: str, volume_name: str):
    """Create Unity Catalog volume if it doesn't exist."""
    try:
        spark.sql(f"""
            CREATE VOLUME IF NOT EXISTS {catalog}.{schema}.{volume_name}
            --LOCATION '/Volumes/{catalog}/{schema}/{volume_name}/'
        """)
        logger.info(f"Volume {catalog}.{schema}.{volume_name} ensured.")
    except Exception as e:
        logger.error(f"Failed to create volume: {e}")
        raise

def create_table(spark, catalog: str, schema: str, table: str):
    """Create table for storing document metadata if it doesn't exist."""
    try:
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {catalog}.{schema}.{table} (
                document_id STRING,
                file_name STRING,
                file_path STRING,
                upload_timestamp TIMESTAMP,
                file_size BIGINT,
                content_type STRING
            )
            USING DELTA
        """)
        logger.info(f"Table {catalog}.{schema}.{table} ensured.")
    except Exception as e:
        logger.error(f"Failed to create table: {e}")
        raise

def upload_file_to_volume(spark, local_file_path: str, catalog: str, schema: str, volume_name: str, table: str):
    """Upload file to Unity Catalog volume and log metadata to table."""
    try:
        file_name = os.path.basename(local_file_path)
        volume_path = f"/Volumes/{catalog}/{schema}/{volume_name}/{file_name}"

        # In a real Databricks environment, you would copy the file to the volume
        # For now, we'll simulate the upload and log the metadata
        logger.info(f"Uploading {local_file_path} to {volume_path}")

        # Get file stats
        file_stats = os.stat(local_file_path)
        file_size = file_stats.st_size

        # Create metadata record
        metadata_df = spark.createDataFrame([
            (file_name.replace('.pdf', ''), file_name, volume_path,
             spark.sql("SELECT current_timestamp()").collect()[0][0],
             file_size, "application/pdf")
        ], ["document_id", "file_name", "file_path", "upload_timestamp", "file_size", "content_type"])

        # Insert metadata into table
        full_table = f"{catalog}.{schema}.{table}"
        metadata_df.write.mode("append").saveAsTable(full_table)

        logger.info(f"Successfully uploaded {file_name} and logged metadata to {full_table}")

    except Exception as e:
        logger.error(f"Error uploading file {local_file_path}: {e}")
        raise

    try:
        w = WorkspaceClient()
 
        local_root = local_file_path
        volume_root = f"/Volumes/{catalog}/{schema}/{volume_name}"

        for root, _, files in os.walk(local_root):
            for filename in files:
                local_file = os.path.join(root, filename)

                # Path relative to the data/ folder
                relative_path = os.path.relpath(local_file, local_root)

                # Mirror structure in the volume
                target_path = f"{volume_root}/{relative_path}"

                with open(local_file, "rb") as f:
                    w.files.upload(
                        target_path,
                        io.BytesIO(f.read()),
                        overwrite=True
                    )

                print(f"Uploaded {relative_path}")
    except:
        logger.error(f"Error uploading to databricks volume")
        print('upload to volume failed')


def load_csv_to_table(spark, table: str, url: str, catalog: str, schema: str):
    """Download CSV, load into a Spark DataFrame, and save it as a Delta table."""
    try:
        logger.info(f"Loading CSV from {url} into table {catalog}.{schema}.{table}")
        resp = requests.get(url)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        spark_df = spark.createDataFrame(df)
        full_table = f"{catalog}.{schema}.{table}"
        spark_df.write.mode("overwrite").saveAsTable(full_table)
        logger.info(f"Successfully wrote table {full_table}")
    except Exception as e:
        logger.error(f"Error loading {table} from {url}: {e}")
        raise