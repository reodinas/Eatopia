from flask import request
from flask_restful import Resource
from mysql.connector import Error
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
import pandas as pd
import numpy as np
from haversine import haversine

from mysql_connection import get_connection
from utils import check_password, hash_password


class RestaurantListResource(Resource):

    # 식당리스트 가져오는 API
    @jwt_required(optional=True)
    def get(self):

        user_id = get_jwt_identity()

        # 클라이언트에서 쿼리스트링으로 보내는 데이터는
        # request.args에 들어있다.
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        order = request.args.get('order')
        keyword = request.args.get('keyword')
        
        if not lat or not lng:
            return {'error' : 'lat와 lng는 필수 파라미터입니다.'}, 400
   
        if not offset:
            offset = 0
        
        if not limit:
            limit = 20

        if not order:
            order = 'distance'

        if not keyword:
            keyword = ''

        lat = float(lat)
        lng = float(lng)
        offset = int(offset)
        limit = int(limit)

        if not (-90 <= lat <=90):
            return {'error' : 'lat값을 확인하세요.'}, 400
        
        if not (-180 <= lng <=180):
            return {'error' : 'lng값을 확인하세요.'}, 400

        try:
            connection = get_connection()
            query = '''
                    select r.id, r.name, r.category, r.locCity, r.locDistrict, r.locDetail,
                        r.longitude, r.latitude, r.imgUrl,
                        ifnull(count(rv.restaurantId), 0) as count,
                        ifnull(avg(rv.rating), 0) as rating
                    from restaurant r
                    left join review rv
                    on r.id = rv.restaurantId
                    where name like "%'''+keyword+'''%" 
                        or category like "%'''+keyword+'''%"
                        or locCity like "%'''+keyword+'''%"
                        or locDistrict like "%'''+keyword+'''%"
                        or locDetail like "%'''+keyword+'''%"
                    group by r.id;
                    '''  
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            result_list = cursor.fetchall()

            for row in result_list:
                row['rating'] = float(row['rating'])

            cursor.close()
            connection.close()
        
        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
        
        if not result_list:
            return {'msg' : '검색결과가 없습니다.'}, 205 
        
        df = pd.DataFrame(data=result_list)

        # print(df)
        myLocation = (lat, lng)
        # print(myLocation)

        LocationList = np.array(df[['latitude','longitude']])

        distanceList = []
        for row in LocationList:
            distanceList.append(haversine(myLocation, row, unit='m'))
            
        df['distance'] = distanceList
        
        if order == 'distance':
            df = df.sort_values(order, ascending=True)
        elif order == 'count' or order == 'rating':
            df = df.sort_values(order, ascending=False)
        else:
            return {'error' : '올바르지 않은 order 입니다.'}, 400
        
        # print(df)
        result_list = df.iloc[offset:limit]
        result_list = result_list.to_dict('records')
        # print(result_list)

        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}
    

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

        
