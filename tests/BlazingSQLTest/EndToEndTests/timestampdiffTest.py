from blazingsql import DataType
from Configuration import ExecutionMode
from Configuration import Settings as Settings
from DataBase import createSchema as cs
from pynvml import nvmlInit
from Runner import runTest
from Utils import Execution, gpuMemory, init_context, skip_test

queryType = "Timestampdiff"


def main(dask_client, drill, spark, dir_data_file, bc, nRals):

    start_mem = gpuMemory.capture_gpu_memory_usage()

    def executionTest():
        tables = ["lineitem", "orders", "nation"]
        data_types = [DataType.CSV, DataType.PARQUET]  # TODO json

        # Create Tables -----------------------------------------------------
        for fileSchemaType in data_types:
            if skip_test(dask_client, nRals, fileSchemaType, queryType):
                continue

            cs.create_tables(bc, dir_data_file, fileSchemaType, tables=tables)

            # Run Query ------------------------------------------------------
            # Parameter to indicate if its necessary to order
            # the resulsets before compare them
            worder = 1
            use_percentage = False
            acceptable_difference = 0.01

            print("==============================")
            print(queryType)
            print("==============================")

            # These Test still fails
            # TODO: Create a issue to track these
            # queryId = "TEST_01"
            # query = """select l_shipdate, l_commitdate,
            #             timestampdiff(DAY, l_commitdate, l_shipdate) as diff
            #         from lineitem  limit 20"""
            # query_spark = """select l_shipdate, l_commitdate,
            #         datediff(l_shipdate, l_commitdate) as diff
            #         from lineitem  limit 20"""
            # runTest.run_query(
            #     bc,
            #     spark,
            #     query,
            #     queryId,
            #     queryType,
            #     worder,
            #     "",
            #     acceptable_difference,
            #     use_percentage,
            #     fileSchemaType,
            #     query_spark=query_spark,
            # )

            # queryId = "TEST_02"
            # query = """select l_shipdate, timestampdiff(DAY,
            #              date '1970-01-01', l_shipdate) as diff
            #         from lineitem  limit 20"""
            # query_spark = """select l_shipdate, datediff(l_shipdate,
            #                 date '1970-01-01') as diff
            #             from lineitem  limit 20"""
            # runTest.run_query(
            #     bc,
            #     spark,
            #     query,
            #     queryId,
            #     queryType,
            #     worder,
            #     "",
            #     acceptable_difference,
            #     use_percentage,
            #     fileSchemaType,
            #     query_spark=query_spark,
            # )

            # queryId = "TEST_03"
            # query = """select * from orders
            #         where timestampdiff(DAY,  date '1995-02-04',
            #             o_orderdate) < 25"""
            # query_spark = """select * from orders where
            #         datediff(o_orderdate, date '1995-02-04') < 25"""
            # runTest.run_query(
            #     bc,
            #     spark,
            #     query,
            #     queryId,
            #     queryType,
            #     worder,
            #     "",
            #     acceptable_difference,
            #     use_percentage,
            #     fileSchemaType,
            #     query_spark=query_spark,
            # )

            queryId = "TEST_04"
            query = """select o_orderdate, TIMESTAMPADD(DAY, 4, o_orderdate) as add_day_col
                        from orders order by o_orderkey limit 150"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_05"
            query = """select o_orderdate, TIMESTAMPADD(HOUR, 12, o_orderdate) as add_hour_col
                        from orders order by o_orderkey limit 450"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_06"
            query = """select o_orderdate, TIMESTAMPADD(MINUTE, 42, o_orderdate) as add_minute_col
                        from orders order by o_orderkey limit 350"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_07"
            query = """select o_orderdate, TIMESTAMPADD(SECOND, 21, o_orderdate) as add_second_col
                        from orders order by o_orderkey limit 250"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_08"
            query = """select o_orderdate, 
                            TIMESTAMPADD(DAY, 18, CAST(o_orderdate AS TIMESTAMP)) as add_day_col
                        from orders order by o_orderkey limit 250"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            # Tests: [09 - 12] are to consider different cases
            # when using different type of TIMESTAMP unit
            queryId = "TEST_09"
            query = """with date_table as (
                            select cast(o_orderdate as date) as my_date
                            from orders order by o_orderkey limit 10000
                        ) 
                        select my_date, 
                                timestampadd(DAY, 17, cast(my_date as timestamp)) as add_day_col
                        from date_table limit 450"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_10"
            query = """with date_table as (
                            select cast(o_orderdate as date) as my_date
                            from orders order by o_orderkey limit 10000
                        ) 
                        select my_date, 
                                timestampadd(HOUR, 48, cast(my_date as timestamp)) as add_hour_col
                        from date_table limit 450"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_11"
            query = """with date_table as (
                            select cast(o_orderdate as date) as my_date
                            from orders order by o_orderkey limit 12000
                        ) 
                        select my_date, 
                                timestampadd(MINUTE, 75, cast(my_date as timestamp)) as add_minute_col
                        from date_table limit 400"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_12"
            query = """with date_table as (
                            select cast(o_orderdate as date) as my_date
                            from orders order by o_orderkey limit 12000
                        ) 
                        select my_date, 
                                timestampadd(SECOND, 150, cast(my_date as timestamp)) as add_second_col
                        from date_table limit 400"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            # Tests: [13 - 20] are just to ensure that TIMESTAMPADD works with constant values
            queryId = "TEST_13"
            query = """select TIMESTAMPADD(DAY, 22, TIMESTAMP '1995-12-10 02:06:17') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_14"
            query = """select TIMESTAMPADD(DAY, 92, date '1995-07-06') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_15"
            query = """select TIMESTAMPADD(HOUR, 21, TIMESTAMP '1995-12-10 02:06:17') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_16"
            query = """select TIMESTAMPADD(HOUR, 78, date '1995-07-06') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_17"
            query = """select TIMESTAMPADD(MINUTE, 72, TIMESTAMP '1995-12-10 02:06:17') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_18"
            query = """select TIMESTAMPADD(MINUTE, 47, date '1995-07-06') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_19"
            query = """select TIMESTAMPADD(SECOND, 105, TIMESTAMP '1995-12-10 02:06:17') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_20"
            query = """select TIMESTAMPADD(SECOND, 16, date '1995-07-06') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            # Tests: [21 -28] are just to ensure TIMESTAMPDIFF works with constant values
            queryId = "TEST_21"
            query = """select TIMESTAMPDIFF(DAY, date '1995-07-06', date '1995-02-06') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_22"
            query = """select TIMESTAMPDIFF(DAY, TIMESTAMP '1995-03-06 10:50:00', TIMESTAMP '1995-12-03 19:50:00') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_23"
            query = """select TIMESTAMPDIFF(HOUR, date '1995-07-06', date '1995-02-06') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_24"
            query = """select TIMESTAMPDIFF(HOUR, TIMESTAMP '1995-03-06 10:50:00', TIMESTAMP '1995-12-03 19:50:00') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_25"
            query = """select TIMESTAMPDIFF(MINUTE, date '1995-07-06', date '1995-02-06') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_26"
            query = """select TIMESTAMPDIFF(MINUTE, TIMESTAMP '1995-03-06 10:50:00', TIMESTAMP '1995-12-03 19:50:00') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_27"
            query = """select TIMESTAMPDIFF(SECOND, date '1995-07-06', date '1995-02-06') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_28"
            query = """select TIMESTAMPDIFF(SECOND, TIMESTAMP '1995-03-06 10:50:00', TIMESTAMP '1995-12-03 19:50:00') as constant_col
                        from nation"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            # Tests: [29 - 32] are to consider different cases
            # when using different type of TIMESTAMP unit
            queryId = "TEST_29"
            query = """with date_table as (
                            select cast(o_orderdate as date) as my_date
                            from orders order by o_orderkey limit 10000
                        ) select my_date, 
                            timestampdiff(DAY, CAST(my_date AS TIMESTAMP), TIMESTAMP '1996-12-01 12:00:01') as diff_day_col
                        from date_table limit 450"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_30"
            query = """with date_table as (
                            select cast(o_orderdate as date) as my_date
                            from orders order by o_orderkey limit 10000
                        ) select my_date,
                            timestampdiff(HOUR, CAST(my_date AS TIMESTAMP), TIMESTAMP '1996-12-01 12:00:01') as diff_hour_col
                        from date_table limit 450"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_31"
            query = """with date_table as (
                            select cast(o_orderdate as date) as my_date from
                            orders order by o_orderkey limit 12000
                        ) select my_date,
                            timestampdiff(MINUTE, CAST(my_date AS TIMESTAMP), TIMESTAMP '1996-12-01 12:00:01') as diff_minute_col
                        from date_table limit 400"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            queryId = "TEST_32"
            query = """with date_table as (
                            select cast(o_orderdate as date) as my_date
                            from orders order by o_orderkey limit 12000
                        ) select my_date,
                            timestampdiff(SECOND, CAST(my_date AS TIMESTAMP), TIMESTAMP '1996-12-01 12:00:01') as diff_second_col
                        from date_table limit 400"""
            runTest.run_query(
                bc,
                drill,
                query,
                queryId,
                queryType,
                worder,
                "",
                acceptable_difference,
                use_percentage,
                fileSchemaType,
            )

            if Settings.execution_mode == ExecutionMode.GENERATOR:
                print("==============================")
                break

    executionTest()

    end_mem = gpuMemory.capture_gpu_memory_usage()

    gpuMemory.log_memory_usage(queryType, start_mem, end_mem)


if __name__ == "__main__":

    Execution.getArgs()

    nvmlInit()

    drill = "drill"  # None
    spark = "spark"

    compareResults = True
    if "compare_results" in Settings.data["RunSettings"]:
        compareResults = Settings.data["RunSettings"]["compare_results"]

    if ((Settings.execution_mode == ExecutionMode.FULL and
         compareResults == "true") or
            Settings.execution_mode == ExecutionMode.GENERATOR):
        # Create Table Drill ------------------------------------------------
        print("starting drill")
        from pydrill.client import PyDrill

        drill = PyDrill(host="localhost", port=8047)
        cs.init_drill_schema(drill,
                             Settings.data["TestSettings"]["dataDirectory"])

        # Create Table Spark -------------------------------------------------
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.appName("timestampTest").getOrCreate()
        cs.init_spark_schema(spark,
                             Settings.data["TestSettings"]["dataDirectory"])

    # Create Context For BlazingSQL

    bc, dask_client = init_context()

    nRals = Settings.data["RunSettings"]["nRals"]

    main(dask_client,
        drill,
        spark,
        Settings.data["TestSettings"]["dataDirectory"],
        bc,
        nRals)

    if Settings.execution_mode != ExecutionMode.GENERATOR:
        runTest.save_log()
        gpuMemory.print_log_gpu_memory()
