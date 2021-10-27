update:
	source .env && python src/run_pipeline.py

local_postgis:
	docker run --name local_postgis -p 5432:5432 -e POSTGRES_PASSWORD=${POSTGRES_PASS} -e POSTGRES_USER=${POSTGRES_USER} -e POSTGRES_DB=${POSTGRES_DB} -d postgis/postgis