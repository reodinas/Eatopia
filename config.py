
class Config :
    HOST = ''
    DATABASE = ''
    DB_USER = ''
    DB_PASSWORD = ''
    SALT = ''

    # JWT 관련 변수 셋팅
    JWT_SECRET_KEY = ''
    JWT_ACCESS_TOKEN_EXPIRES = False 
    
    PROPAGATE_EXCEPTIONS = True # JWT 에러메시지를 명시함
    