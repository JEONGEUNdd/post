import mysql.connector
from datetime import datetime
from werkzeug.security import check_password_hash
from flask import session
class DBManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="10.0.66.31",
                user="sejong",
                password="1234",
                database="board_db2"
            )
            self.cursor = self.connection.cursor(dictionary=True)
            
        except mysql.connector.Error as error:
            print(f"데이터베이스 연결 실패: {error}")

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
    def get_all_posts(self):
        try:
            self.connect()
            sql = "SELECT * FROM posts"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"게시글 조회 실패: {error}")
            return []
        finally:
            self.disconnect()
    
    def insert_post(self,title,content,author,filename):
        try:
            self.connect()
            sql = "INSERT INTO posts (title,content,author,filename,created_at) values (%s,%s,%s,%s,%s)"     #여기에 view넣으면안됨
            values = (title,content,author,filename,datetime.now())            
            self.cursor.execute(sql, values)
            
            #values = [(name,email,department,salary,datetime.now().date()),(name,email,department,salary,datetime.now().date())]
            #self.cursor.executemany(sql, values)            
            
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"내용 추가 실패: {error}")
            return False
        finally:
            self.disconnect()
   
    def get_post_by_id(self, id):
        try:
            self.connect()
            sql = "SELECT * FROM posts WHERE id = %s"
            value = (id,) # 튜플 1개 일때
            self.cursor.execute(sql, value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"내용 조회 실패: {error}")
            return None
        finally:
            self.disconnect()
    
    def update_post(self,id,title,content,filename):
        try:
            self.connect()
            if filename:
                sql = """UPDATE posts 
                        SET title = %s, content = %s, filename = %s 
                        WHERE id = %s
                        """
                values = (title,content,filename,id)
            else:
                sql = """UPDATE posts 
                        SET title = %s, content = %s 
                        WHERE id = %s
                        """
                values = (title,content,id)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"게시글 수정 실패: {error}")
            return False
        finally:
            self.disconnect()
    
    def delete_post(self, id):
        try:
            self.connect()
            sql = "DELETE FROM posts WHERE id = %s"
            value = (id,) # 튜플 1개 일때
            self.cursor.execute(sql, value)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"게시판 삭제 실패: {error}")
            return False
        finally:
            self.disconnect()
              
    #조회수 증가       
    def update_views(self, id):
        try:
            self.connect()
            sql = """UPDATE posts SET views = views + 1 WHERE id = %s"""
            value = (id,)
            self.cursor.execute(sql, value)
            self.connection.commit()
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"조회수 업데이트 실패: {error}")
            return False
        finally:
            self.disconnect()
            
    def get_user_by_userid(self, userid):
        """사용자의 아이디로 사용자 정보 가져오기"""
        try:
            self.connect()
            sql = "SELECT * FROM users WHERE userid = %s"
            self.cursor.execute(sql, (userid,))
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"사용자 조회 실패: {error}")
            return None
        finally:
            self.disconnect()

    def validate_login(self, userid, password):
        """아이디와 비밀번호를 검증"""
        user = self.get_user_by_userid(userid)
        if not user:
            return False, "아이디가 존재하지 않습니다."
        
        # if not check_password_hash(user['password'], password):
        if user['password']!= password: 
            return False, "비밀번호가 일치하지 않습니다."
        
        return True, user  # 검증 성공 시 사용자 정보를 반환     
       
    def get_posts_count(self):
        try:
            self.connect()
            sql = "SELECT COUNT(*) AS count FROM posts"
            self.cursor.execute(sql)
            return self.cursor.fetchone()['count']  # 게시글 총 개수 반환
        except mysql.connector.Error as error:
            print(f"게시글 개수 조회 실패: {error}")
            return 0
        finally:
            self.disconnect()
            
    def get_posts_by_page(self, page, posts_per_page):
        try:
            self.connect()
            offset = (page - 1) * posts_per_page
            sql = "SELECT * FROM posts ORDER BY id DESC LIMIT %s OFFSET %s"
            self.cursor.execute(sql, (posts_per_page, offset))
            return self.cursor.fetchall()  # 페이지에 해당하는 게시글 반환
        except mysql.connector.Error as error:
            print(f"페이지별 게시글 조회 실패: {error}")
            return []
        finally:
            self.disconnect()
            
    def get_all_users(self):
        try:
            self.connect()
            sql = "SELECT userid, username, created_at, is_admin FROM users"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"회원 목록 조회 실패: {error}")
            return []
        finally:
            self.disconnect()
            
    #관리자페이지에서 회원 정보 찾기       
    def search_users(self, query):
        try:
            self.connect()
            sql = """
                SELECT userid, username, created_at, is_admin 
                FROM users 
                WHERE userid LIKE %s OR username LIKE %s
            """
            like_query = f"%{query}%"
            self.cursor.execute(sql, (like_query, like_query))
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"회원 검색 실패: {error}")
            return []
        finally:
            self.disconnect()
                        