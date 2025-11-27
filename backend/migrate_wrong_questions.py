#!/usr/bin/env python3
"""
错题本数据迁移脚本
将全局错题数据迁移到用户特定的格式
"""

import json
import os
import shutil
from datetime import datetime

def migrate_wrong_questions():
    """迁移错题数据"""
    data_dir = "data"
    wrong_questions_file = os.path.join(data_dir, "wrong_questions.json")
    users_file = os.path.join(data_dir, "users.json")
    
    # 备份原文件
    if os.path.exists(wrong_questions_file):
        backup_file = f"{wrong_questions_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(wrong_questions_file, backup_file)
        print(f"已备份原错题文件到: {backup_file}")
    
    # 读取原错题数据
    old_wrong_questions = {}
    if os.path.exists(wrong_questions_file):
        with open(wrong_questions_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                try:
                    old_wrong_questions = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"解析原错题文件失败: {e}")
                    return False
    
    # 读取用户数据
    users = {}
    if os.path.exists(users_file):
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
    
    # 如果原数据已经是用户特定的格式，则跳过迁移
    if isinstance(old_wrong_questions, dict) and old_wrong_questions:
        # 检查是否已经是用户特定的格式
        first_key = list(old_wrong_questions.keys())[0]
        if isinstance(old_wrong_questions[first_key], dict) and 'question' in old_wrong_questions[first_key]:
            # 这是旧的全局格式，需要迁移
            print("检测到旧的全局错题格式，开始迁移...")
            
            # 获取第一个用户ID（或者创建一个默认用户）
            user_ids = list(users.keys())
            if not user_ids:
                print("没有找到用户，无法迁移错题数据")
                return False
            
            # 将错题数据分配给第一个用户
            first_user_id = user_ids[0]
            new_wrong_questions = {
                str(first_user_id): old_wrong_questions
            }
            
            # 保存新格式
            with open(wrong_questions_file, 'w', encoding='utf-8') as f:
                json.dump(new_wrong_questions, f, ensure_ascii=False, indent=2)
            
            print(f"已将 {len(old_wrong_questions)} 道错题迁移到用户 {first_user_id}")
            return True
    
    print("错题数据格式已经是用户特定的，无需迁移")
    return True

if __name__ == "__main__":
    print("开始错题数据迁移...")
    if migrate_wrong_questions():
        print("错题数据迁移完成")
    else:
        print("错题数据迁移失败")