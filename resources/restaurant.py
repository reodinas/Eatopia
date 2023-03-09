from flask import request
from flask_restful import Resource
from mysql.connector import Error
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity

from mysql_connection import get_connection
from utils import check_password, hash_password


# class RestaurantListResource(Resource):

#     # 식당리스트 가져오는 API
#     @jwt_required(optional=True)
#     def get(self):

#         user_id = get_jwt_identity()

#         # 클라이언트에서 쿼리스트링으로 보내는 데이터는
#         # request.args에 들어있다.
#         offset = request.args.get('offset')
#         limit = request.args.get('limit')

        

#         return
    

class RestaurantResource(Resource):

    # 식당 상세정보 가져오는 API
    @jwt_required(optional=True) # 회원도 똑같이 동작하기 때문에 안써도 됨
    def get(self, restaurantId):
        
        try:
            connection = get_connection()
            query = '''
                    select r.*, 
                        ifnull(count(rv.restaurantId), 0) as cnt,
                        ifnull(avg(rv.rating), 0) as avg 
                    from restaurant r
                    left join review rv
                    on r.id = rv.restaurantId
                    where r.id = %s;
                    '''  
            record = (restaurantId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchone()

            

            # safe coding
            if result['id'] is None:
                return {'errer' : '잘못된 restaurantId 입니다.'}, 400

            result['createdAt'] = result['createdAt'].isoformat()
            result['updatedAt'] = result['updatedAt'].isoformat()
            result['avg'] = float(result['avg'])

            print(result)

            cursor.close()
            connection.close()
        
        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
        
        return {'result' : 'success',
                'restaurantInfo' : result}, 200
    

class RestaurantMenuResource(Resource):

    # 식당 메뉴리스트 가져오는 API
    @jwt_required(optional=True) 
    def get(self, restaurantId):

        try:
            connection = get_connection()
            query = '''
                    select * 
                    from menu
                    where restaurantId = %s;
                    '''  
            record = (restaurantId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            for row in result_list:
                row['createdAt'] = row['createdAt'].isoformat()
                row['updatedAt'] = row['updatedAt'].isoformat()
            
            cursor.close()
            connection.close()
        
        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
        
        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}, 200

        
