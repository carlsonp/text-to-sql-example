# text-to-sql-example

## Introduction

Leverages LlamaIndex and CrewAI to showcase how basic questions can be translated into SQL queries and run on databases.

## Requirements

* Docker (with buildkit enabled, see `/etc/docker/daemon.json`)
* docker compose

## Installation and Setup

Copy `.env-copy` to `.env` and edit as needed.

Here are some of the models tested:

* Worked Well:
  * `codellama:13b`
  * `llama3.1:8b`
* Struggled With Questions:
  * `llama3.2:3b`
  * `phi3:14b`

In general, the smaller models (<3b parameters) seemed to struggle while medium sized (>8b) (and likely larger models) seemed to do much better.
Code tailored models like `codellama` and others likely have an edge with SQL generation.

Download the following datasets from Kaggle and extract into the `data` folder.

* https://www.kaggle.com/datasets/davidcariboo/player-scores

The files should then match the following:

```shell
./data/appearances.csv
./data/club_games.csv
./data/clubs.csv
./data/competitions.csv
./data/empty.txt
./data/game_events.csv
./data/game_lineups.csv
./data/games.csv
./data/players.csv
./data/player_valuations.csv
./data/transfers.csv
```

Build the image

```shell
docker compose build --pull
```

## Running

```shell
docker compose run texttosql
```

## For Developers

* If you come up with a question and the model is unable to come up with correct query or hallucinates an answer, try adding more metadata.
If the columns and tables by themselves aren't conveying a lot of information more metadata, particularly on the column descriptions can help the
model with figuring out what to run.

## References

* https://docs.llamaindex.ai/en/stable/examples/index_structs/struct_indices/SQLIndexDemo/
