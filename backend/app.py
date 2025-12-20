from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import random
import hashlib
import jwt
from functools import wraps

app = Flask(__name__)
CORS(app)

# JWT密钥
SECRET_KEY = "radio_exam_secret_key_2024"

# 数据文件路径
DATA_DIR = "data"
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
WRONG_QUESTIONS_FILE = os.path.join(DATA_DIR, "wrong_questions.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 导入PDF解析器
try:
    from pdf_parser import load_questions
except ImportError:
    print("PDF解析器导入失败，使用内置解析器")
    
    def load_questions():
        """内置题目加载器"""
        if os.path.exists(QUESTIONS_FILE):
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print("获取题目失败")
            return {}


def save_questions(questions):
    """保存题目数据"""
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def load_wrong_questions(user_id=None):
    """加载错题数据"""
    if os.path.exists(WRONG_QUESTIONS_FILE):
        with open(WRONG_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            all_wrong_questions = json.load(f)
            # 如果指定了用户ID，只返回该用户的错题
            if user_id:
                return all_wrong_questions.get(str(user_id), {})
            # 否则返回所有用户的错题（向后兼容）
            return all_wrong_questions
    return {} if user_id else {}

def save_wrong_questions(wrong_questions, user_id=None):
    """保存错题数据"""
    # 如果指定了用户ID，保存到该用户的错题本中
    if user_id:
        # 先加载所有用户的错题数据
        all_wrong_questions = load_wrong_questions()
        all_wrong_questions[str(user_id)] = wrong_questions
        with open(WRONG_QUESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_wrong_questions, f, ensure_ascii=False, indent=2)
    else:
        # 直接保存（向后兼容）
        with open(WRONG_QUESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(wrong_questions, f, ensure_ascii=False, indent=2)

def normalize_answer(answer):
    """标准化答案（排序并去重）"""
    if not answer:
        return ""
    # 将答案转换为大写，排序并去重
    return ''.join(sorted(set(str(answer).upper())))

def is_answer_correct(user_answer, correct_answer):
    """判断答案是否正确（支持多选题）"""
    user_normalized = normalize_answer(user_answer)
    correct_normalized = normalize_answer(correct_answer)
    return user_normalized == correct_normalized

# 用户认证相关函数
def load_users():
    """加载用户数据"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """保存用户数据"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def check_user_access(user):
    """检查用户访问权限（时间限制）"""
    if user.get('is_admin', False):
        return {'access': True, 'message': '管理员无时间限制'}
    
    now = datetime.now()
    
    # 检查开始时间
    start_time = user.get('start_time')
    if start_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if now < start_dt:
                return {'access': False, 'message': '账号未到生效时间'}
        except:
            pass
    
    # 检查到期时间
    expire_time = user.get('expire_time')
    if expire_time:
        try:
            expire_dt = datetime.fromisoformat(expire_time.replace('Z', '+00:00'))
            if now > expire_dt:
                return {'access': False, 'message': '当前账号已到期，请联系管理员！'}
        except:
            pass
    
    # 计算剩余天数
    days_left = None
    if expire_time:
        try:
            expire_dt = datetime.fromisoformat(expire_time.replace('Z', '+00:00'))
            # 计算总的小时差，然后向上取整到天数
            total_hours = (expire_dt - now).total_seconds() / 3600
            if total_hours > 0:
                # 如果还有时间，至少显示1天
                days_left = max(1, int((total_hours + 23) // 24))
            else:
                days_left = 0
        except:
            pass
    
    return {
        'access': True, 
        'days_left': days_left,
        'expire_time': expire_time
    }

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """验证密码"""
    return hash_password(password) == hashed

def generate_token(user_id, phone, is_admin):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'phone': phone,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(f):
    """JWT认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'error': '缺少认证令牌'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = {
                'user_id': data['user_id'],
                'phone': data['phone'],
                'is_admin': data['is_admin']
            }
        except:
            return jsonify({'error': '令牌无效'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user['is_admin']:
            return jsonify({'error': '需要管理员权限'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

def init_default_admin():
    """初始化默认管理员"""
    users = load_users()
    if not users:
        # 创建默认管理员
        admin_user = {
            'user_id': 'admin_001',
            'phone': '17610788168',
            'password': hash_password('administrator'),
            'is_admin': True,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
            # 管理员不需要时间限制
        }
        users['admin_001'] = admin_user
        save_users(users)
        print("默认管理员已创建: 17610788168 / administrator")

@app.route('/api/questions', methods=['GET'])
@token_required
def get_all_questions(current_user):
    """获取所有题目"""
    # 检查用户访问权限
    users = load_users()
    user = users.get(current_user['user_id'])
    if user:
        access_check = check_user_access(user)
        if not access_check['access']:
            return jsonify({'error': access_check['message']}), 401
    
    questions = load_questions()
    return jsonify(questions)


# 新增：获取指定范围的试卷
@app.route('/api/exam/custom', methods=['GET'])
@token_required
def get_custom_exam(current_user):
    # 检查用户访问权限
    users = load_users()
    user = users.get(current_user['user_id'])
    if user:
        access_check = check_user_access(user)
        if not access_check['access']:
            return jsonify({'error': access_check['message']}), 401
    questions = load_questions()
    
    if not questions:
        return jsonify({"error": "题库为空"}), 400
    
    # 获取请求参数
    start_id = request.args.get('start_id', type=int, default=1)
    count = request.args.get('count', type=int, default=20)
    
    # 参数验证
    if start_id < 1:
        return jsonify({"error": "起始题号必须大于0"}), 400
    
    if count < 1 or count > 1000:
        return jsonify({"error": "题目数量必须在1-100之间"}), 400
    
    
    # 选择题目
    selected_questions = questions[start_id-1:start_id+count-1]

    
    
    exam = {
        "exam_id": f"custom_exam_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "questions": selected_questions,
        "start_id": start_id,
        "actual_count": len(selected_questions)
    }
    
    return jsonify(exam)

@app.route('/api/exam', methods=['GET'])
@token_required
def generate_exam(current_user):
    """生成试卷（随机20题）"""
    # 检查用户访问权限
    users = load_users()
    user = users.get(current_user['user_id'])
    if user:
        access_check = check_user_access(user)
        if not access_check['access']:
            return jsonify({'error': access_check['message']}), 401
    
    questions = load_questions()
    
    # 随机选择20题
    if len(questions) > 20:
        exam_questions = random.sample(questions, 20)
    else:
        exam_questions = questions
    return jsonify({
        'exam_id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'questions': exam_questions
    })

@app.route('/api/exam/submit', methods=['POST'])
@token_required
def submit_exam(current_user):
    """提交试卷"""
    # 检查用户访问权限
    users = load_users()
    user = users.get(current_user['user_id'])
    if user:
        access_check = check_user_access(user)
        if not access_check['access']:
            return jsonify({'error': access_check['message']}), 401
    data = request.json
    exam_id = data.get('exam_id')
    answers = data.get('answers', {})
    
    questions = load_questions()
    wrong_questions = load_wrong_questions(current_user['user_id'])
    
    results = []
    correct_count = 0
    wrong_questions_list = []
    correct_questions_list = []
    
    for q_id, user_answer in answers.items():
        question = next((q for q in questions if q['id'] == q_id), None)
        if question:
            is_correct = is_answer_correct(user_answer, question.get('correct', ''))
            
            results.append({
                'question_id': q_id,
                'user_answer': user_answer,
                'correct_answer': question.get('correct', ''),
                'is_correct': is_correct
            })
            
            if is_correct:
                correct_count += 1
                # 添加到正确题目列表
                correct_questions_list.append({
                    'question_id': q_id,
                    'question_text': question.get('question', ''),
                    'user_answer': user_answer,
                    'correct_answer': question.get('correct', '')
                })
            else:
                # 添加到当前用户的错题本
                if q_id not in wrong_questions:
                    wrong_questions[q_id] = {
                        'question': question,
                        'wrong_count': 1,
                        'correct_count': 0,
                        'last_wrong_time': datetime.now().isoformat()
                    }
                else:
                    wrong_questions[q_id]['wrong_count'] += 1
                    wrong_questions[q_id]['last_wrong_time'] = datetime.now().isoformat()
                
                # 添加到本次考试的错题列表
                wrong_questions_list.append({
                    'question_id': q_id,
                    'question_text': question.get('question', ''),
                    'user_answer': user_answer,
                    'correct_answer': question.get('correct', '')
                })
    
    save_wrong_questions(wrong_questions, current_user['user_id'])
    
    return jsonify({
        'exam_id': exam_id,
        'total': len(answers),
        'correct_count': correct_count,
        'score': int(correct_count / len(answers) * 100) if answers else 0,
        'wrong_questions': wrong_questions_list,
        'correct_questions': correct_questions_list,
        'results': results
    })

@app.route('/api/wrong-questions', methods=['GET'])
@token_required
def get_wrong_questions(current_user):
    """获取错题本"""
    # 检查用户访问权限
    users = load_users()
    user = users.get(current_user['user_id'])
    if user:
        access_check = check_user_access(user)
        if not access_check['access']:
            return jsonify({'error': access_check['message']}), 401
    wrong_questions = load_wrong_questions(current_user['user_id'])
    
    # 转换为列表格式
    wrong_list = []
    for q_id, wrong_info in wrong_questions.items():
        wrong_list.append({
            'question_id': q_id,
            'question': wrong_info['question'],
            'wrong_count': wrong_info['wrong_count'],
            'correct_count': wrong_info['correct_count'],
            'last_wrong_time': wrong_info['last_wrong_time']
        })
    
    return jsonify(wrong_list)

@app.route('/api/wrong-questions/practice', methods=['POST'])
@token_required
def practice_wrong_question(current_user):
    """练习错题"""
    # 检查用户访问权限
    users = load_users()
    user = users.get(current_user['user_id'])
    if user:
        access_check = check_user_access(user)
        if not access_check['access']:
            return jsonify({'error': access_check['message']}), 401
    data = request.json
    q_id = data.get('question_id')
    is_correct = data.get('is_correct')
    
    wrong_questions = load_wrong_questions(current_user['user_id'])
    
    if q_id in wrong_questions:
        if is_correct:
            wrong_questions[q_id]['correct_count'] += 1
            # 连续做对3次，从错题本移除
            if wrong_questions[q_id]['correct_count'] >= 3:
                del wrong_questions[q_id]
                save_wrong_questions(wrong_questions, current_user['user_id'])
                return jsonify({
                    'success': True,
                    'removed': True,
                    'message': '题目已从错题本移除'
                })
        else:
            wrong_questions[q_id]['correct_count'] = 0
            wrong_questions[q_id]['wrong_count'] += 1
            wrong_questions[q_id]['last_wrong_time'] = datetime.now().isoformat()
    
    save_wrong_questions(wrong_questions, current_user['user_id'])
    
    return jsonify({
        'success': True,
        'removed': False,
        'message': '错题本已更新'
    })

@app.route('/api/wrong-questions/practice-exam', methods=['GET'])
@token_required
def generate_practice_exam(current_user):
    """生成错题练习试卷"""
    # 检查用户访问权限
    users = load_users()
    user = users.get(current_user['user_id'])
    if user:
        access_check = check_user_access(user)
        if not access_check['access']:
            return jsonify({'error': access_check['message']}), 401
    wrong_questions = load_wrong_questions(current_user['user_id'])
    
    if not wrong_questions:
        return jsonify({
            'error': '暂无错题可练习'
        }), 404
    
    # 从错题本中选择题目（最多20题）
    practice_questions = []
    for q_id, wrong_info in wrong_questions.items():
        practice_questions.append(wrong_info['question'])
        
        if len(practice_questions) >= 20:
            break
    
    return jsonify({
        'exam_id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'questions': practice_questions,
        'type': 'practice'
    })

@app.route('/api/wrong-questions/practice-submit', methods=['POST'])
@token_required
def submit_practice_exam(current_user):
    """提交错题练习"""
    # 检查用户访问权限
    users = load_users()
    user = users.get(current_user['user_id'])
    if user:
        access_check = check_user_access(user)
        if not access_check['access']:
            return jsonify({'error': access_check['message']}), 401
    data = request.json
    exam_id = data.get('exam_id')
    answers = data.get('answers', {})
    
    wrong_questions = load_wrong_questions(current_user['user_id'])
    
    results = []
    correct_count = 0
    updated_questions = []
    wrong_questions_list = []
    correct_questions_list = []
    
    for q_id, user_answer in answers.items():
        if q_id in wrong_questions:
            question = wrong_questions[q_id]['question']
            is_correct = is_answer_correct(user_answer, question.get('correct', ''))
            
            results.append({
                'question_id': q_id,
                'user_answer': user_answer,
                'correct_answer': question.get('correct', ''),
                'is_correct': is_correct
            })
            
            if is_correct:
                correct_count += 1
                wrong_questions[q_id]['correct_count'] += 1
                # 添加到正确题目列表
                correct_questions_list.append({
                    'question_id': q_id,
                    'question_text': question.get('question', ''),
                    'user_answer': user_answer,
                    'correct_answer': question.get('correct', '')
                })
                
                # 连续做对3次，从错题本移除
                if wrong_questions[q_id]['correct_count'] >= 3:
                    updated_questions.append({
                        'question_id': q_id,
                        'action': 'removed'
                    })
                    del wrong_questions[q_id]
                else:
                    updated_questions.append({
                        'question_id': q_id,
                        'action': 'correct',
                        'correct_count': wrong_questions[q_id]['correct_count']
                    })
            else:
                wrong_questions[q_id]['correct_count'] = 0
                wrong_questions[q_id]['wrong_count'] += 1
                wrong_questions[q_id]['last_wrong_time'] = datetime.now().isoformat()
                
                # 添加到错题列表
                wrong_questions_list.append({
                    'question_id': q_id,
                    'question_text': question.get('question', ''),
                    'user_answer': user_answer,
                    'correct_answer': question.get('correct', '')
                })
                
                updated_questions.append({
                    'question_id': q_id,
                    'action': 'wrong',
                    'wrong_count': wrong_questions[q_id]['wrong_count']
                })
    
    save_wrong_questions(wrong_questions, current_user['user_id'])
    
    return jsonify({
        'exam_id': exam_id,
        'total': len(answers),
        'correct_count': correct_count,
        'score': int(correct_count / len(answers) * 100) if answers else 0,
        'updated_questions': updated_questions,
        'results': results,
        'wrong_questions': wrong_questions_list,
        'correct_questions': correct_questions_list
    })

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    questions = load_questions()
    all_wrong_questions = load_wrong_questions()  # 获取所有用户的错题数据
    
    # 计算总的错题数量（所有用户的错题总数）
    total_wrong_count = 0
    user_wrong_counts = {}
    
    for user_id, user_wrong_questions in all_wrong_questions.items():
        user_wrong_count = len(user_wrong_questions)
        total_wrong_count += user_wrong_count
        user_wrong_counts[user_id] = user_wrong_count
    
    return jsonify({
        'total_questions': len(questions),
        'wrong_questions_count': total_wrong_count,
        'user_wrong_counts': user_wrong_counts,
        'total_users_with_wrong_questions': len(user_wrong_counts),
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    """重置系统（清空所有用户的错题本）"""
    save_wrong_questions({})  # 清空所有错题数据
    return jsonify({'success': True, 'message': '系统已重置，所有用户的错题本已清空'})

@app.route('/api/system/reset-user/<user_id>', methods=['POST'])
@token_required
def reset_user_wrong_questions(current_user, user_id):
    """清空指定用户的错题本（仅管理员）"""
    # 检查当前用户是否为管理员
    users = load_users()
    current_user_data = users.get(current_user['user_id'])
    if not current_user_data or not current_user_data.get('is_admin', False):
        return jsonify({'error': '权限不足，仅管理员可执行此操作'}), 403
    
    # 清空指定用户的错题本
    save_wrong_questions({}, user_id)
    return jsonify({'success': True, 'message': f'用户 {user_id} 的错题本已清空'})

# 用户认证相关API
@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    
    if not phone or not password:
        return jsonify({'error': '手机号和密码不能为空'}), 400
    
    users = load_users()
    
    # 查找用户
    user = None
    for user_id, user_data in users.items():
        if user_data['phone'] == phone and user_data['status'] == 'active':
            user = user_data
            break
    
    if not user:
        return jsonify({'error': '用户不存在或已被禁用'}), 401
    
    if not verify_password(password, user['password']):
        return jsonify({'error': '密码错误'}), 401
    
    # 检查用户访问权限
    access_check = check_user_access(user)
    if not access_check['access']:
        return jsonify({'error': access_check['message']}), 401
    
    # 生成token
    token = generate_token(user['user_id'], user['phone'], user['is_admin'])
    
    # 构建返回的用户信息
    user_info = {
        'user_id': user['user_id'],
        'phone': user['phone'],
        'is_admin': user['is_admin']
    }
    
    # 添加时间限制信息
    if not user['is_admin']:
        user_info.update({
            'days_left': access_check.get('days_left'),
            'expire_time': access_check.get('expire_time')
        })
    
    return jsonify({
        'success': True,
        'token': token,
        'user': user_info
    })

@app.route('/api/auth/register', methods=['POST'])
@token_required
@admin_required
def register(current_user):
    """管理员添加用户"""
    data = request.json
    phone = data.get('phone')
    start_time = data.get('start_time')
    expire_time = data.get('expire_time')
    
    if not phone:
        return jsonify({'error': '手机号不能为空'}), 400
    
    users = load_users()
    
    # 检查手机号是否已存在
    for user_data in users.values():
        if user_data['phone'] == phone:
            return jsonify({'error': '该手机号已被注册'}), 400
    
    # 生成用户ID
    user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 创建新用户
    new_user = {
        'user_id': user_id,
        'phone': phone,
        'password': hash_password('wxd666a'),  # 默认密码
        'is_admin': False,
        'created_at': datetime.now().isoformat(),
        'status': 'active'
    }
    
    # 添加时间限制
    if start_time:
        new_user['start_time'] = start_time
    if expire_time:
        new_user['expire_time'] = expire_time
    
    users[user_id] = new_user
    save_users(users)
    
    return jsonify({
        'success': True,
        'message': '用户添加成功',
        'user': {
            'user_id': user_id,
            'phone': phone,
            'password': 'wxd666a',  # 返回默认密码
            'is_admin': False,
            'start_time': start_time,
            'expire_time': expire_time
        }
    })

@app.route('/api/auth/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    """获取用户列表"""
    users = load_users()
    user_list = []
    
    for user_id, user_data in users.items():
        user_info = {
            'user_id': user_id,
            'phone': user_data['phone'],
            'is_admin': user_data['is_admin'],
            'created_at': user_data['created_at'],
            'status': user_data['status']
        }
        
        # 添加时间限制信息
        if not user_data['is_admin']:
            user_info.update({
                'start_time': user_data.get('start_time'),
                'expire_time': user_data.get('expire_time')
            })
            
            # 检查访问状态
            access_check = check_user_access(user_data)
            user_info['access_status'] = 'valid' if access_check['access'] else 'expired'
            user_info['days_left'] = access_check.get('days_left')
        
        user_list.append(user_info)
    
    return jsonify({'users': user_list})

@app.route('/api/auth/users/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """删除用户"""
    users = load_users()
    
    if user_id not in users:
        return jsonify({'error': '用户不存在'}), 404
    
    # 不能删除管理员
    if users[user_id]['is_admin']:
        return jsonify({'error': '不能删除管理员账户'}), 403
    
    del users[user_id]
    save_users(users)
    
    return jsonify({'success': True, 'message': '用户删除成功'})

@app.route('/api/auth/reset-password/<user_id>', methods=['POST'])
@token_required
@admin_required
def reset_password(current_user, user_id):
    """重置用户密码"""
    users = load_users()
    
    if user_id not in users:
        return jsonify({'error': '用户不存在'}), 404
    
    # 重置为默认密码
    users[user_id]['password'] = hash_password('wxd666a')
    save_users(users)
    
    return jsonify({
        'success': True,
        'message': '密码重置成功',
        'new_password': 'wxd666a'
    })

@app.route('/api/auth/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """用户修改密码"""
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'error': '旧密码和新密码不能为空'}), 400
    
    users = load_users()
    user_id = current_user['user_id']
    
    if user_id not in users:
        return jsonify({'error': '用户不存在'}), 404
    
    # 验证旧密码
    if not verify_password(old_password, users[user_id]['password']):
        return jsonify({'error': '旧密码错误'}), 401
    
    # 更新密码
    users[user_id]['password'] = hash_password(new_password)
    save_users(users)
    
    return jsonify({
        'success': True,
        'message': '密码修改成功'
    })

@app.route('/api/auth/update-user-time/<user_id>', methods=['POST'])
@token_required
@admin_required
def update_user_time(current_user, user_id):
    """管理员更新用户时间限制"""
    data = request.json
    start_time = data.get('start_time')
    expire_time = data.get('expire_time')
    
    users = load_users()
    
    if user_id not in users:
        return jsonify({'error': '用户不存在'}), 404
    
    # 不能修改管理员的时间限制
    if users[user_id]['is_admin']:
        return jsonify({'error': '不能修改管理员账户的时间限制'}), 403
    
    # 更新时间限制
    if start_time is not None:
        users[user_id]['start_time'] = start_time
    if expire_time is not None:
        users[user_id]['expire_time'] = expire_time
    
    save_users(users)
    
    return jsonify({
        'success': True,
        'message': '用户时间限制更新成功',
        'user': {
            'user_id': user_id,
            'start_time': start_time,
            'expire_time': expire_time
        }
    })

@app.route('/api/auth/user-access', methods=['GET'])
@token_required
def check_user_access_info(current_user):
    """检查用户访问权限信息"""
    users = load_users()
    user_id = current_user['user_id']
    
    if user_id not in users:
        return jsonify({'error': '用户不存在'}), 404
    
    user = users[user_id]
    access_check = check_user_access(user)
    
    return jsonify({
        'success': True,
        'access': access_check['access'],
        'message': access_check['message'] if not access_check['access'] else '访问正常',
        'days_left': access_check.get('days_left'),
        'expire_time': access_check.get('expire_time')
    })

@app.route('/api/auth/verify', methods=['POST'])
@token_required
def verify_token(current_user):
    """验证token有效性"""
    return jsonify({
        'success': True,
        'user': current_user
    })

if __name__ == '__main__':
    # 初始化默认管理员
    init_default_admin()
    
    # 初始化题目数据（如果不存在）
    if not os.path.exists(QUESTIONS_FILE):
        print("初始化题目数据库...")
        questions = load_questions()
        save_questions(questions)
        print(f"已初始化 {len(questions)} 道题目")
    
    print("启动业余无线电考试系统...")
    print(f"题目数量: {len(load_questions())}")
    print(f"错题数量: {len(load_wrong_questions())}")
    print(f"用户数量: {len(load_users())}")
    print("后端服务运行在: http://localhost:5001")
    print("前端服务运行在: http://localhost:3001")
    
    app.run(debug=True, port=5001)