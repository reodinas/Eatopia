
class Config :
    HOST = 'yh-db.cdtkthbhsama.ap-northeast-2.rds.amazonaws.com'
    DATABASE = 'movie_db2'
    DB_USER = 'movie_db_user'
    DB_PASSWORD = 'yh1234db'
    SALT = 'friday'

    # JWT 관련 변수 셋팅
    JWT_SECRET_KEY = 'moviemovie'
    JWT_ACCESS_TOKEN_EXPIRES = False 
    
    PROPAGATE_EXCEPTIONS = True # JWT 에러메시지를 명시함
    
