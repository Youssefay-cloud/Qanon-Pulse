# Docker-compose to intialize the postgreSQL and Pgadmin 
`docker compose up -d ` Then you can use the pgadmin to interact with the database 
there is init.sql to create the schema if there isn't one and we took care of data we need to persist using volumes 

I deleted the init.sql because we have the data and well create the dtypes using pandas and then we will connect to the database using sqlalchemy.



### Script for reshaping the missed arabic text in /reshaping_data
the command to use the script is 

`python reshaping_data/reshape.py data/laws_structured.json data/reshaped_laws.json`

---

### Finished
1. Docker for db 
2. reshaping data 
3. ingest data to the database
4. Dockrize the ingestion file
5. 

Start the Transformation


---

### problems Fixed :
1. Drop empty articles
2. sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgresql.psycopg
3. Fixed schema



### problems:

Smaller things to fix in the ingestion file:

**Move secrets and paths out of the code**. Read the password and path from 
environment variables (or a .env file), because root:yoyo and a Desktop path make the script neither universal nor safe to commit. In a raw stringr"C:\\Users..." also keeps the double backslashes literally. Use r"C:\Users..." or pathlib.


**Wrap it in a main()** function with the path as an argument. That’s the cheapest step toward “universal” and makes it callable from Airflow later.



