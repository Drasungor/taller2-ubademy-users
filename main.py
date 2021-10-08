import uvicorn

from fastapi import FastAPI, HTTPException

from models.user import User, fake_users_db


app = FastAPI()


@app.get('/users/{username}', response_model=User)
async def read_user(username: str):
    user_dict = fake_users_db[username]
    if not user_dict:
        raise HTTPException(status_code=400, detail='User not found')
    user = User(**user_dict)
    return user


@app.get('/')
async def home():
    return {'message': 'Hello users!'}


@app.get('/pong')
async def pong():
    return {'message': 'pong'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)
