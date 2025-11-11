import re
import os
import json
from datetime import datetime

# 数据目录
DATA_DIR = "data"
global sn
sn =0 
def parse_pdf_content(pdf_text):
    """解析PDF文本内容，提取题目"""
    questions = []
    
    # 更灵活的正则表达式匹配，处理PDF文本格式
    pattern = r'\[I\].+?(?=\[I\]|$)'
    question_blocks = re.findall(pattern, pdf_text, re.DOTALL)    
    for block in question_blocks:
        question_data = parse_question_block(block)
        if question_data:
            questions.append(question_data)
        else:
            print("无效题目：", question_data)
    print("共有多少道题：", len(questions))
    
    return questions

def parse_question_block(block):

    question_data = {
        'id': '',
        'question': '',
        'correct': '',
        'options': []
    }

    """解析单个题目块"""
    # print("正在解析题目：", block,"---",type(block))
    par_ID = r'\[I\](.+?)(\n|\[Q\])'
    question_data['id'] = re.findall(par_ID, block)[0][0]

    

    par_question = r'\[Q\](.+?)(\n|\[T\])'
    question_data['question'] = re.findall(par_question, block)[0][0]

    par_correct = r'\[T\](.+?)(\n|\[A\])'
    question_data['correct'] = re.findall(par_correct, block)[0][0]

    par_A = r'\[A\](.+?)(\[B\]|\n|$)'
    par_B = r'\[B\](.+?)(\[C\]|\n|$)'
    par_C = r'\[C\](.+?)(\[D\]|\n|$)'
    par_D = r'\[D\](.+?)(\n|$)'


    question_data['options'].append({'key': 'A', 'text': re.findall(par_A, block)[0][0]})
    question_data['options'].append({'key': 'B', 'text': re.findall(par_B, block)[0][0]})
    question_data['options'].append({'key': 'C', 'text': re.findall(par_C, block)[0][0]})
    question_data['options'].append({'key': 'D', 'text': re.findall(par_D, block)[0][0]})

    # 验证题目数据完整性
    if (question_data['id'] and question_data['question'] and 
        question_data['correct'] and len(question_data['options']) >= 2):
        return question_data
    else:
        print("无效的题目数据：", question_data)
    return question_data
    
    
def create_questions_from_pdf_text():
    """从PDF文本文件创建题目数据库"""
    pdf_text_path = os.path.join(DATA_DIR, "pdf_content.txt")
    
    if not os.path.exists(pdf_text_path):
        print("PDF文本文件不存在")
        return []
   
    try:
        with open(pdf_text_path, 'r', encoding='utf-8') as f:
            pdf_content = f.read()
        
        questions = parse_pdf_content(pdf_content)
        print(f"从文本文件解析出 {len(questions)} 道题目")
        return questions
        
    except Exception as e:
        print(f"读取PDF文本文件失败: {e}")
        return []

def get_sample_questions():
    """获取示例题目（作为后备）"""
    return [
        {
            "id": "MC2-0001",
            "question": "我国专门针对无线电管理的行政法规及其制定机构是:",
            "correct": "AC",
            "options": [
                {"key": "A", "text": "《中华人民共和国无线电管理条例》"},
                {"key": "B", "text": "《中华人民共和国无线电管理办法》"},
                {"key": "C", "text": "国务院和中央军委"},
                {"key": "D", "text": "工业和信息化部"}
            ]
        },
        {
            "id": "MC2-0002",
            "question": "我国专门针对业余无线电台的管理文件及其制定机构分别是:",
            "correct": "AC",
            "options": [
                {"key": "A", "text": "《业余无线电台管理办法》"},
                {"key": "B", "text": "《业余无线电台管理暂行规定》"},
                {"key": "C", "text": "工业和信息化部"},
                {"key": "D", "text": "国务院"}
            ]
        },
        {
            "id": "MC1-0003",
            "question": "我国依法负责对业余无线电台实施监督管理的机构是:",
            "correct": "A",
            "options": [
                {"key": "A", "text": "国家无线电管理机构和省、自治区、直辖市无线电管理机构"},
                {"key": "B", "text": "在国家或地方民政部门注册的业余无线电协会"},
                {"key": "C", "text": "国家体育管理机构和地方体育管理机构"},
                {"key": "D", "text": "国家和地方公安部门"}
            ]
        },
        {
            "id": "MC1-0004",
            "question": "我国对无线电管理术语'业余业务'、'卫星业余业务'和'业余电台'做出具体定义的法规文件是:",
            "correct": "A",
            "options": [
                {"key": "A", "text": "《中华人民共和国无线电频率划分规定》"},
                {"key": "B", "text": "《中华人民共和国无线电管理条例》"},
                {"key": "C", "text": "《中华人民共和国电信条例》"},
                {"key": "D", "text": "《无线电台执照管理规定》"}
            ]
        }
    ]

def create_questions_from_pdf():
    """创建题目数据库（主函数）"""
    questions = create_questions_from_pdf_text()
    
    if len(questions) == 0:
        print("PDF文本解析失败，使用示例题目")
        # questions = get_sample_questions()
    
    return questions

def save_questions(questions):
    """保存题目到JSON文件"""
    questions_file = os.path.join(DATA_DIR, "questions.json")
    try:
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"题目已保存到 {questions_file}")
        return True
    except Exception as e:
        print(f"保存题目失败: {e}")
        return False

def load_questions():
    """从JSON文件加载题目"""
    questions_file = os.path.join(DATA_DIR, "questions.json")
    
    if not os.path.exists(questions_file):
        print("题目文件不存在，创建新题目")
        questions = create_questions_from_pdf()
        save_questions(questions)
        return questions
    
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        print(f"从文件加载 {len(questions)} 道题目")
        return questions
    except Exception as e:
        print(f"加载题目失败: {e}，创建新题目")
        questions = create_questions_from_pdf()
        save_questions(questions)
        return questions

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 创建并保存题目
    questions = create_questions_from_pdf()
    save_questions(questions)
    
    # 显示前几题作为示例
    print("\n前5题示例:")
    for i, q in enumerate(questions[100:6]):
        print(f"\n{i+1}. ID: {q['id']}")
        print(f"   题目: {q['question']}")
        print(f"   正确答案: {q['correct']}")
        print("   选项:")
        for opt in q['options']:
            print(f"     {opt['key']}. {opt['text']}")