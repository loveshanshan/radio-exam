from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# 数据文件路径
DATA_DIR = "data"
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
WRONG_QUESTIONS_FILE = os.path.join(DATA_DIR, "wrong_questions.json")

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

def load_wrong_questions():
    """加载错题数据"""
    if os.path.exists(WRONG_QUESTIONS_FILE):
        with open(WRONG_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_wrong_questions(wrong_questions):
    """保存错题数据"""
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

@app.route('/api/questions', methods=['GET'])
def get_all_questions():
    """获取所有题目"""
    questions = load_questions()
    return jsonify(questions)


# 新增：获取指定范围的试卷
@app.route('/api/exam/custom', methods=['GET'])
def get_custom_exam():
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
def generate_exam():
    """生成试卷（随机20题）"""
    
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
def submit_exam():
    """提交试卷"""
    data = request.json
    exam_id = data.get('exam_id')
    answers = data.get('answers', {})
    
    questions = load_questions()
    wrong_questions = load_wrong_questions()
    
    results = []
    correct_count = 0
    wrong_questions_list = []
    
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
            else:
                # 添加到错题本
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
    
    save_wrong_questions(wrong_questions)
    
    return jsonify({
        'exam_id': exam_id,
        'total': len(answers),
        'correct_count': correct_count,
        'score': int(correct_count / len(answers) * 100) if answers else 0,
        'wrong_questions': wrong_questions_list,
        'results': results
    })

@app.route('/api/wrong-questions', methods=['GET'])
def get_wrong_questions():
    """获取错题本"""
    wrong_questions = load_wrong_questions()
    
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
def practice_wrong_question():
    """练习错题"""
    data = request.json
    q_id = data.get('question_id')
    is_correct = data.get('is_correct')
    
    wrong_questions = load_wrong_questions()
    
    if q_id in wrong_questions:
        if is_correct:
            wrong_questions[q_id]['correct_count'] += 1
            # 连续做对3次，从错题本移除
            if wrong_questions[q_id]['correct_count'] >= 3:
                del wrong_questions[q_id]
                save_wrong_questions(wrong_questions)
                return jsonify({
                    'success': True,
                    'removed': True,
                    'message': '题目已从错题本移除'
                })
        else:
            wrong_questions[q_id]['correct_count'] = 0
            wrong_questions[q_id]['wrong_count'] += 1
            wrong_questions[q_id]['last_wrong_time'] = datetime.now().isoformat()
    
    save_wrong_questions(wrong_questions)
    
    return jsonify({
        'success': True,
        'removed': False,
        'message': '错题本已更新'
    })

@app.route('/api/wrong-questions/practice-exam', methods=['GET'])
def generate_practice_exam():
    """生成错题练习试卷"""
    wrong_questions = load_wrong_questions()
    
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
def submit_practice_exam():
    """提交错题练习"""
    data = request.json
    exam_id = data.get('exam_id')
    answers = data.get('answers', {})
    
    wrong_questions = load_wrong_questions()
    
    results = []
    correct_count = 0
    updated_questions = []
    
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
                updated_questions.append({
                    'question_id': q_id,
                    'action': 'wrong',
                    'wrong_count': wrong_questions[q_id]['wrong_count']
                })
    
    save_wrong_questions(wrong_questions)
    
    return jsonify({
        'exam_id': exam_id,
        'total': len(answers),
        'correct_count': correct_count,
        'score': int(correct_count / len(answers) * 100) if answers else 0,
        'updated_questions': updated_questions,
        'results': results
    })

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    questions = load_questions()
    wrong_questions = load_wrong_questions()
    
    return jsonify({
        'total_questions': len(questions),
        'wrong_questions_count': len(wrong_questions),
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    """重置系统（清空错题本）"""
    save_wrong_questions({})
    return jsonify({'success': True, 'message': '系统已重置'})

if __name__ == '__main__':
    # 初始化题目数据（如果不存在）
    if not os.path.exists(QUESTIONS_FILE):
        print("初始化题目数据库...")
        questions = load_questions()
        save_questions(questions)
        print(f"已初始化 {len(questions)} 道题目")
    
    print("启动业余无线电考试系统...")
    print(f"题目数量: {len(load_questions())}")
    print(f"错题数量: {len(load_wrong_questions())}")
    print("后端服务运行在: http://localhost:5000")
    print("前端服务运行在: http://localhost:3000")
    
    app.run(debug=True, port=5000)