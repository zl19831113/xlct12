import sqlite3
import re
import logging
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_listening_questions(question_text):
    """Split a listening question into sub-questions"""
    try:
        # 移除题目编号和指令说明
        main_text = re.sub(r'^\d+．[^A-Za-z]+', '', question_text)
        
        # 首先尝试按照问题标记分割
        sub_questions = []
        
        # 匹配所有问题和选项
        pattern = r'([A-Za-z][^A-Z\n]*\?)\s*\n*\s*(A．[^\n]+\s*\nB．[^\n]+\s*\nC．[^\n]+)'
        matches = re.finditer(pattern, main_text, re.DOTALL)
        
        for match in matches:
            question = match.group(1).strip()
            options = match.group(2).strip()
            sub_questions.append(f"{question}\n\n{options}")
        
        return sub_questions
    except Exception as e:
        logger.error(f"Error splitting questions: {e}")
        logger.error(f"Question text: {question_text}")
        return []

def process_options(question_text):
    """Extract options from question text"""
    try:
        options_match = re.search(r'(A．[^\n]+\s*\nB．[^\n]+\s*\nC．[^\n]+)(?=\n\n|$)', question_text, re.DOTALL)
        if options_match:
            return options_match.group(1).strip()
        return ""
    except Exception as e:
        logger.error(f"Error processing options: {e}")
        return ""

def main():
    # 确保数据库目录存在
    os.makedirs('instance', exist_ok=True)
    
    try:
        conn = sqlite3.connect('instance/xlct12.db')
        cursor = conn.cursor()
        
        # 开始事务
        cursor.execute("BEGIN TRANSACTION")
        
        # 获取所有听力题目
        cursor.execute("""
            SELECT id, subject, textbook, chapter, unit, lesson, question, answer, 
                   question_image, answer_image, question_image_filename, 
                   answer_image_filename, question_type, education_stage, unit_order,
                   audio_file_path, audio_filename, audio_content, question_number
            FROM su 
            WHERE question LIKE '%听下面一段较长对话%' 
               OR question LIKE '%听录音%'
            ORDER BY question_number
        """)
        
        listening_questions = cursor.fetchall()
        logger.info(f"Found {len(listening_questions)} listening questions")
        
        # 创建临时表
        cursor.execute("DROP TABLE IF EXISTS su_temp")
        cursor.execute("CREATE TABLE su_temp AS SELECT * FROM su WHERE 1=0")
        
        processed_count = 0
        for row in listening_questions:
            try:
                parent_id = row[0]  # Original question ID becomes parent_id
                question_text = row[6]
                answer_text = row[7]
                
                # 记录原始题目内容
                logger.info(f"Processing question {parent_id}:")
                logger.info(f"Question text: {question_text[:200]}...")
                
                # Split into sub-questions
                sub_questions = split_listening_questions(question_text)
                
                if not sub_questions:
                    logger.info(f"Skipping question {parent_id} - no sub-questions found")
                    continue
                
                logger.info(f"Found {len(sub_questions)} sub-questions")
                
                # Split answers - 移除空行并清理答案
                answers = [ans.strip() for ans in answer_text.split('\n') if ans.strip() and not ans.startswith('【')]
                
                # Insert each sub-question
                for i, sub_q in enumerate(sub_questions):
                    try:
                        # Get the corresponding answer if available
                        sub_answer = answers[i] if i < len(answers) else ""
                        
                        # Insert into temporary table
                        cursor.execute("""
                            INSERT INTO su_temp (
                                subject, textbook, chapter, unit, lesson, question, answer,
                                question_image, answer_image, question_image_filename,
                                answer_image_filename, question_type, education_stage,
                                unit_order, audio_file_path, audio_filename, audio_content,
                                question_number, parent_id
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row[1], row[2], row[3], row[4], row[5], sub_q, sub_answer,
                            row[8], row[9], row[10], row[11], row[12], row[13], row[14],
                            row[15], row[16], row[17], row[18], parent_id
                        ))
                        processed_count += 1
                        logger.info(f"Successfully processed sub-question {i+1}")
                    except Exception as e:
                        logger.error(f"Error processing sub-question {i} of question {parent_id}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error processing question {row[0]}: {e}")
                continue
        
        logger.info(f"Successfully processed {processed_count} sub-questions")
        
        # 更新原始表
        cursor.execute("DELETE FROM su WHERE id IN (SELECT parent_id FROM su_temp)")
        cursor.execute("INSERT INTO su SELECT * FROM su_temp")
        cursor.execute("DROP TABLE su_temp")
        
        # 提交事务
        conn.commit()
        logger.info("Successfully committed all changes")
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main() 