import psycopg2


conn = psycopg2.connect(dbname='yugabyte',
                        host='ap-south-1.5e98aaa0-7d64-4a7e-80eb-5c3923368534.aws.yugabyte.cloud',
                        port='5433',
                        user='admin',password='QoiO7D-xmmzcCOxTWup6xjIicWoNFb')


cur = conn.cursor()
cur.execute('DROP TABLE influencers')
rows = cur.fetchall()
for row in rows:
  print(row)
