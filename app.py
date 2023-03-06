from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from config import Config



app = Flask(__name__)
# 환경변수 셋팅
app.config.from_object(Config)

# JWT 매니저 초기화(initialize)
# JWTManager(app)을 설정해줘야 flask istance에서 jwt를 사용할 수 있게 된다.
jwt = JWTManager(app)

api = Api(app)

# 경로와 리소스를 연결한다.



if __name__ == '__main__':
    app.run()