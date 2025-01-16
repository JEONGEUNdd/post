from flask import Flask,render_template,request,redirect,url_for,jsonify,send_from_directory,flash
import os
from datetime import datetime
from models import DBManager
from flask import session
import mysql.connector
app = Flask(__name__)
app.secret_key = 'your_secret_key'

#app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

manager = DBManager()

# 목록보기
@app.route('/')
def index():
    # 요청된 페이지 번호 가져오기 (기본값: 1)
    page = request.args.get('page', 1, type=int)
    posts_per_page = 10  # 페이지당 게시글 수

    # 게시글 총 개수와 현재 페이지의 게시글 가져오기
    total_posts = manager.get_posts_count()  # 총 게시글 수
    posts = manager.get_posts_by_page(page, posts_per_page)

    # 총 페이지 수 계산
    total_pages = (total_posts + posts_per_page - 1) // posts_per_page

    return render_template('index.html', posts=posts, page=page, total_pages=total_pages)

#로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']

        # 로그인 검증
        success, result = manager.validate_login(userid, password)
        if success:
            session['userid'] = result['userid']
            session['username'] = result['username']
            session['is_admin'] = result.get('is_admin', False)
            return redirect('/')
        else:
            flash("아이디와 비밀번호를 다시 입력해주세요.", 'danger')  # 오류 메시지 표시
    return render_template('login.html')
    
#로그인된 사용자만 이용 가능   
@app.route('/dashboard')
def dashboard():
    if 'userid' in session:
        return f"안녕하세요, {session['username']}님!"
    else:
        return "로그인 후 이용해주세요."
    
#로그아웃시 세션 정보 삭제   
@app.route('/logout')
def logout():
    session.clear()  # 모든 세션 정보 삭제
    flash("로그아웃되었습니다.", "custom") 
    return redirect(url_for('index')) 

# 내용보기
@app.route('/post/<int:id>')
def view_post(id):
    manager.update_views(id)
    post = manager.get_post_by_id(id)
    return render_template('view.html',post=post)

# 내용추가
# 파일업로드: enctype="multipart/form-data", method='POST', type='file', accept=".png,.jpg,.gif" 
@app.route('/post/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = session.get('username')
        # 첨부파일 한 개
        file = request.files['file']
        filename = file.filename if file else None
        
        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        
        if manager.insert_post(title,content,author,filename):
            return redirect("/")
        return "게시글 추가 실패", 400        
    return render_template('add.html')


@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = manager.get_post_by_id(id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        file = request.files['file']
        filename = file.filename if file else None
        
        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        if manager.update_post(id,title,content,filename):
            return redirect("/")
        return "게시글 추가 실패", 400        
    return render_template('edit.html',post=post)

@app.route('/post/delete/<int:id>', methods=['POST'])
def delete_post(id):
    if manager.delete_post(id):
        return redirect(url_for('index'))
    return "게시글 삭제 실패", 400

#회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        username = request.form['username']

        # 모든 필드 입력 여부 확인
        if not userid or not password or not username:
            flash("모든 필드를 입력해주세요.", "danger")
            return render_template('register.html')

        try:
            manager.connect()
            sql = "INSERT INTO users (userid, password, username) VALUES (%s, %s, %s)"
            manager.cursor.execute(sql, (userid, password, username))
            manager.connection.commit()
            flash("회원가입이 완료되었습니다.", "success")
            return redirect('/login')
        except mysql.connector.Error as e:
            flash(f"회원가입 실패: {e}", "danger")
            return render_template('register.html')  # 반환값 추가
        finally:
            manager.disconnect()

    # 기본 반환값 추가
    return render_template('register.html')

#관리자페이지
@app.route('/admin')
def admin_page():
    if not session.get('is_admin'):  # 관리자가 아닌 경우
        flash("관리자만 접근할 수 있습니다.", "danger")
        return redirect('/')

    query = request.args.get('query', '')  # 검색어 가져오기
    if query:
        users = manager.search_users(query)  # 검색 쿼리를 처리하는 메서드
    else:
        users = manager.get_all_users()  # 모든 회원 가져오기

    return render_template('admin.html', users=users)

   
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5003,debug=True)
    
   