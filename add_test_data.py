from app import app, db, SU
from datetime import datetime

# 在应用上下文中执行
with app.app_context():
    # 检查是否已有英语题目
    english_count = SU.query.filter_by(subject='英语').count()
    print(f"当前英语题目数量: {english_count}")
    
    # 检查所有科目分布
    from sqlalchemy import func
    subject_counts = db.session.query(SU.subject, func.count(SU.id)).group_by(SU.subject).all()
    print("当前科目分布:")
    for subject, count in subject_counts:
        print(f"  {subject}: {count}题")
    
    # 如果英语题目少于5道，添加测试数据
    if english_count < 5:
        print("\n添加英语测试题目...")
        
        # 添加5道英语听力理解题目
        test_questions = [
            {
                'subject': '英语',
                'textbook': '初中英语(新标准)',  # 添加教材信息
                'question_type': '听力理解',
                'education_stage': '初中',
                'chapter': '第一章',
                'unit': '第一单元',
                'lesson': '第一课时',
                'question': '''
                Listen to the recording and answer the question.
                What does the boy want to do this weekend?
                A. Go to the movies
                B. Visit the museum
                C. Play basketball
                D. Stay at home
                ''',
                'answer': 'A. Go to the movies\n【详解】从对话中可以得知，男孩想周末去看电影。'
            },
            {
                'subject': '英语',
                'textbook': '初中英语(新标准)',
                'question_type': '听力理解',
                'education_stage': '初中',
                'chapter': '第二章',
                'unit': '第二单元',
                'lesson': '第一课时',
                'question': '''
                Listen to the recording and choose the correct answer.
                Where does the conversation take place?
                A. In a restaurant
                B. In a classroom
                C. In a library
                D. In a bookstore
                ''',
                'answer': 'C. In a library\n【详解】从对话中提到"be quiet"和"borrow some books"可以判断是在图书馆。'
            },
            {
                'subject': '英语',
                'textbook': '初中英语(新标准)',
                'question_type': '阅读理解',
                'education_stage': '初中',
                'chapter': '第三章',
                'unit': '第一单元',
                'lesson': '第二课时',
                'question': '''
                Read the passage and answer the questions.
                
                Tom woke up late this morning. He quickly got dressed and ran to school. When he arrived, the classroom was empty. He looked at his watch. It was 8:30. He was confused because school should start at 8:00. Then he remembered it was Saturday! There was no school today.
                
                Why was Tom confused?
                A. Because he was late for school
                B. Because the classroom was empty
                C. Because he forgot it was Saturday
                D. Because his watch was wrong
                ''',
                'answer': 'C. Because he forgot it was Saturday\n【详解】根据文章最后一句"Then he remembered it was Saturday!"可知Tom困惑的原因是他忘记了今天是星期六。'
            },
            {
                'subject': '英语',
                'textbook': '初中英语(新标准)',
                'question_type': '完形填空',
                'education_stage': '初中',
                'chapter': '第二章',
                'unit': '第三单元',
                'lesson': '第三课时',
                'question': '''
                Read the passage and fill in the blanks with proper words.
                
                Last weekend, I __1__ my grandparents in the countryside. The weather was __2__ and we had a great time. We went fishing by the river and caught three big fish. My grandmother cooked them for dinner. It was the most delicious meal I've ever had!
                
                1. A. visited   B. visit   C. visits   D. visiting
                2. A. bad      B. cold    C. nice     D. hot
                ''',
                'answer': '1. A\n2. C\n【详解】根据文章时态和上下文，1处应填visited表示过去时；2处应填nice表示天气很好。'
            },
            {
                'subject': '英语',
                'textbook': '初中英语(新标准)',
                'question_type': '短文改错',
                'education_stage': '初中',
                'chapter': '第四章',
                'unit': '第二单元',
                'lesson': '第四课时',
                'question': '''
                The following passage has five errors. Find and correct them.
                
                Last summer, I go to Beijing with my family. We stayed there for one week. We visited the Great Wall in the first day. It was more long than I thought. We took many photos and buyed some souvenirs. I will never forget this trip.
                ''',
                'answer': '''
                1. go → went (过去时态)
                2. in → on (介词用法)
                3. more long → longer (比较级形式)
                4. buyed → bought (不规则动词过去式)
                5. this → that (指示代词使用)
                '''
            }
        ]
        
        # 添加到数据库
        for q_data in test_questions:
            new_question = SU(
                subject=q_data['subject'],
                textbook=q_data['textbook'],  # 确保提供textbook字段
                question_type=q_data['question_type'], 
                education_stage=q_data['education_stage'],
                chapter=q_data['chapter'],
                unit=q_data['unit'],
                lesson=q_data['lesson'],
                question=q_data['question'],
                answer=q_data['answer']
            )
            db.session.add(new_question)
        
        # 提交事务
        db.session.commit()
        print("已添加5道英语题目到数据库")
        
        # 再次检查英语题目数量
        english_count = SU.query.filter_by(subject='英语').count()
        print(f"现在英语题目数量: {english_count}")
    else:
        print("数据库中已有足够的英语题目，无需添加测试数据")
