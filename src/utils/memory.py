import duckdb as dd

__CON = dd.connect(':memory:')


query = __CON.query
execute = __CON.execute
