from fastapi import FastAPI

from app.database import ch_client

app = FastAPI(title="NL to ClickHouse Query Tool")

@app.get("/")
async def root():
    return {"message": "NL ClickHouse Query API"}

@app.get("/tables")
async def get_tables():
    return ch_client.get_tables()

@app.post("/query")
async def execute_query(query: dict):
    sql = query.get("sql")
    return ch_client.execute_query(sql)
