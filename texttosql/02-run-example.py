#!/usr/bin/env python3
import os
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.ollama import Ollama
from sqlalchemy import create_engine, text
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.indices.struct_store.sql_query import (
    SQLTableRetrieverQueryEngine,
)
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core import VectorStoreIndex


Settings.llm = Ollama(model=os.environ['OLLAMA_MODEL'], request_timeout=360.0, base_url=os.environ['OLLAMA_URL'])

# quick sanity check of LLM connectivity
response = Settings.llm.complete("What is the capital of France?")
print(response)

# setup embedding model
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

engine = create_engine("sqlite:///data/sqlitedatabase.db")

with engine.connect() as con:
    rows = con.execute(text("SELECT sum(yellow_cards) FROM appearances"))
    print("Sum of yellow cards given out:")
    for row in rows:
        print(row)

with engine.connect() as con:
    rows = con.execute(text("SELECT player_id, player_name, sum(yellow_cards) FROM appearances group by player_id, player_name order by sum(yellow_cards) desc limit 1"))
    print("Player with most yellowcards:")
    for row in rows:
        print(row)

with engine.connect() as con:
    rows = con.execute(text("SELECT player_id, first_name, last_name, name, country_of_birth, city_of_birth, country_of_citizenship FROM players where player_id = '25557'"))
    print("What country is Sergio Ramos from?")
    for row in rows:
        print(row)

with engine.connect() as con:
    rows = con.execute(text("SELECT player_id, date, market_value_in_eur FROM player_valuations where player_id = '25557' group by date order by date desc limit 1"))
    print("What is the most recent valuation in Euros of Sergio Ramos?")
    for row in rows:
        print(row)

with engine.connect() as con:
    rows = con.execute(text("""
        select
            a.*,
            clubs.name as club_name
        from
        (
            SELECT game_id, club_id, count(*) as number_subs from game_events where type = 'Substitutions' group by game_id, club_id order by count(*) desc limit 1
        ) a
        left join clubs
        on a.club_id = clubs.club_id
        """))
    print("What club had the most number of substitutions in a single game and how many substitutions were there?")
    for row in rows:
        print(row)

sql_database = SQLDatabase(engine, include_tables=["appearances", "club_games", "clubs", "competitions", "game_events", "game_lineups", "games", "player_valuations", "players", "transfers"])

# set Logging to DEBUG for more detailed outputs
table_node_mapping = SQLTableNodeMapping(sql_database)
table_schema_objs = [
    (SQLTableSchema(table_name="appearances", context_str="Each row denotes the appearance a soccer player has in games.  The yellow and red cards columns denote the total number of cards assigned to each player each game.  Players can earn multiple yellow and red cards per game. For example, the appearances file contains one row per player appearance, i.e. one row per player per game played. For each appearance you will find attributes such as goals, assists or yellow_cards and IDs referencing other entities within the dataset, such as player_id and game_id.")),
    (SQLTableSchema(table_name="club_games")),
    (SQLTableSchema(table_name="clubs", context_str="All clubs in leagues. One row per club.")),
    (SQLTableSchema(table_name="competitions")),
    (SQLTableSchema(table_name="game_events", context_str="This stores game events as each row in the table.  The type column will have one of the following four values: Cards, Goals, Shootout, Substitutions.")),
    (SQLTableSchema(table_name="game_lineups")),
    (SQLTableSchema(table_name="games")),
    (SQLTableSchema(table_name="player_valuations", context_str="Valuations of players over various dates.  Valuations are provided through the market_value_in_eur column which is in Euros.")),
    (SQLTableSchema(table_name="players")),
    (SQLTableSchema(table_name="transfers")),
]

obj_index = ObjectIndex.from_objects(
    table_schema_objs,
    table_node_mapping,
    VectorStoreIndex,
)
# the similarity_top_k value should be adjusted up or down depending on the number of tables involved in the SQL query
# if lots of table joins are needed, this should be increased
# setting it too high though may result in extra tables that may confuse the LLM
# this limits the number of tables sent to the context window so we don't overflow
# TODO: how does this perform or even run if we have 100s of tables?
query_engine = SQLTableRetrieverQueryEngine(
    sql_database, obj_index.as_retriever(similarity_top_k=3)
)



for question in ["How many total yellow cards have been given out?",
                 "What player had the most number of total yellow cards?",
                 "What country is Sergio Ramos from?",
                 "What is the most recent valuation in Euros of Sergio Ramos?",
                 "What club had the most number of substitutions in a single game and how many substitutions were there?"]:
    response = query_engine.query(question)
    print(response)
    #print(type(response)) - <class 'llama_index.core.base.response.schema.Response'>

    if 'sql_query' in response.metadata:
        print("Generated Query ::>")
        print(response.metadata['sql_query'])
        print("=====================")

    if 'result' in response.metadata:
        print("Generated Query Result ::>")
        print(response.metadata['result'])
        print("=====================")