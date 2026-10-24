# Docker-compose to intialize the postgreSQL and Pgadmin 
`docker compose up -d ` Then you can use the pgadmin to interact with the database 
there is init.sql to create the schema if there isn't one and we took care of data we need to persist using volumes 

I deleted the init.sql because we have the data and well create the dtypes using pandas and then we will connect to the database using sqlalchemy.



### Script for reshaping the missed arabic text in /reshaping_data
the command to use the script is 

`python reshaping_data/reshape.py data/laws_structured.json data/reshaped_laws.json`


1. Docker for db 
2. reshaping data 
3. ingest data to the database

    **Smaller things to fix in the ingestion file:**

    **Drop empty articles before normalizing**. Laws with an empty articles list explode to NaN, and json_normalize will choke on that. Use df.explode('articles').dropna(subset=['articles']). 
    Your current dropna(subset=['content']) runs too late.

    **Move secrets and paths out of the code**. Read the password and path from environment variables (or a .env file), because root:yoyo and a Desktop path make the script neither universal nor safe to commit. In a raw string, r"C:\\Users..." also keeps the double backslashes literally. Use r"C:\Users..." or pathlib.

    **Wrap it in a main()** function with the path as an argument. That’s the cheapest step toward “universal” and makes it callable from Airflow later.

4. Dockrize the ingestion file





problems:

1. sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgresql.psycopg




Smaller things to fix in the ingestion file:

**Drop empty articles before normalizing**. Laws with an empty articles list explode to NaN, and json_normalize will choke on that. Use df.explode('articles').dropna(subset=['articles']). 
Your current dropna(subset=['content']) runs too late.

**Move secrets and paths out of the code**. Read the password and path from environment variables (or a .env file), because root:yoyo and a Desktop path make the script neither universal nor safe to commit. In a raw string, r"C:\\Users..." also keeps the double backslashes literally. Use r"C:\Users..." or pathlib.

**Wrap it in a main()** function with the path as an argument. That’s the cheapest step toward “universal” and makes it callable from Airflow later.