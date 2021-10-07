from sqlalchemy import create_engine
from sqlalchemy import text

engine = create_engine("postgres://pwmutypretbutp:e74306821a303bd574c10c1444dc22cd053edcc139d06b53fd5f457b1df725eb@ec2-34-199-15-136.compute-1.amazonaws.com:5432/df3a67v8n8bo9b", echo = True)
with engine.connect() as conn:
    result = conn.execute(text("select 'hello world'"))
    #print(result.all())
    print(result)