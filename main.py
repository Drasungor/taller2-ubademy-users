from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session

#engine = create_engine("postgres://pwmutypretbutp:e74306821a303bd574c10c1444dc22cd053edcc139d06b53fd5f457b1df725eb@ec2-34-199-15-136.compute-1.amazonaws.com:5432/df3a67v8n8bo9b", echo = True)
engine = create_engine("postgres://pwmutypretbutp:e74306821a303bd574c10c1444dc22cd053edcc139d06b53fd5f457b1df725eb@ec2-34-199-15-136.compute-1.amazonaws.com:5432/df3a67v8n8bo9b")
with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    #print(result.all())
    print(result)
    #conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    #conn.execute(text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),[{"x": 1, "y": 1}, {"x": 2, "y": 4}])
    #conn.commit()
    result = conn.execute(text("SELECT x, y FROM some_table WHERE x > 1"))
    for row in result:
        print(f"x: {row.x}  y: {row.y}")




