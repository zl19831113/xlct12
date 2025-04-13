#!/bin/bash
# 手动修复 SQLAlchemy case() 函数语法问题

ssh root@120.26.12.100 << 'EOF'
echo "===== 开始手动修复 SQLAlchemy case() 函数语法 ====="

# 1. 备份 app.py
APP_PATH="/var/www/question_bank/app.py"
BACKUP_TIME=$(date +%Y%m%d%H%M%S)
APP_BACKUP="${APP_PATH}.bak_manual_${BACKUP_TIME}"
cp $APP_PATH $APP_BACKUP
echo "已创建 app.py 备份: $APP_BACKUP"

# 2. 提取 filter_papers 函数并修改
echo "提取并修改 filter_papers 函数..."

# 创建一个临时文件来存储修改后的函数
TMP_FILE="/tmp/filter_papers_fixed.py"

# 提取 filter_papers 函数
grep -n "def filter_papers" $APP_PATH | head -1 > $TMP_FILE
START_LINE=$(grep -n "def filter_papers" $APP_PATH | head -1 | cut -d':' -f1)
END_LINE=$((START_LINE + 200))  # 假设函数不超过200行
sed -n "${START_LINE},${END_LINE}p" $APP_PATH > /tmp/filter_papers_original.py

# 手动修改 case() 函数调用
cat > $TMP_FILE << 'END_FUNCTION'
@app.route('/filter_papers', methods=['GET', 'POST'])
def filter_papers():
    try:
        if request.method == 'POST':
            # 从POST请求JSON中获取筛选参数
            filter_data = request.get_json()
            region = filter_data.get('region')
            subject = filter_data.get('subject')
            stage = filter_data.get('stage')
            source_type = filter_data.get('source_type')
            source = filter_data.get('source')
            year = filter_data.get('year')
            keyword = filter_data.get('keyword')
            page = filter_data.get('page', 1)
            per_page = filter_data.get('per_page', 20)
        else:  # GET请求
            # 从URL参数获取筛选条件
            region = request.args.get('region')
            subject = request.args.get('subject')
            stage = request.args.get('stage')
            source_type = request.args.get('source_type')
            source = request.args.get('source')
            year = request.args.get('year')
            keyword = request.args.get('keyword')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
        
        print(f"筛选参数 [{request.method}]: 地区={region}, 科目={subject}, 学段={stage}, 类型={source_type}, 来源={source}, 年份={year}, 关键词={keyword}, 页码={page}")
        
        # 构建查询
        query = Paper.query
        
        # 添加筛选条件
        if region:
            query = query.filter(Paper.region == region)
        if subject:
            query = query.filter(Paper.subject == subject)
        if stage:
            query = query.filter(Paper.stage == stage)
        if source_type:
            query = query.filter(Paper.source_type == source_type)
        if source:
            query = query.filter(Paper.source == source)
        if year:
            try:
                if isinstance(year, str) and year.isdigit():
                    query = query.filter(Paper.year == int(year))
                elif isinstance(year, (int, float)):
                    query = query.filter(Paper.year == int(year))
            except (ValueError, TypeError) as e:
                print(f"年份转换错误: {e}")
        if keyword:
            query = query.filter(Paper.name.like(f'%{keyword}%'))
            
        # 排序逻辑 - 使用正确的SQLAlchemy 2.0语法
        sorted_query = query.order_by(
            Paper.year.desc(),
            # 湖北地区优先 - 使用case()函数
            case((Paper.region == "湖北", 1), else_=0).desc(),
            # 下学期优先于上学期 - 使用case()函数
            case(
                (Paper.name.like("%下学期%"), 2),
                (Paper.name.like("%上学期%"), 1),
                else_=0
            ).desc(),
            # 3月优先于2月优先于1月 - 使用case()函数
            case(
                (Paper.name.like("%3月%"), 3),
                (Paper.name.like("%2月%"), 2),
                (Paper.name.like("%1月%"), 1),
                else_=0
            ).desc(),
            # 最后按上传时间降序排序(最新上传的优先)
            Paper.upload_time.desc()
        )
        
        # 计算总数
        total = sorted_query.count()
        print(f"筛选结果总数: {total}")
        
        # 分页
        paginated = sorted_query.paginate(page=page, per_page=per_page, error_out=False)
        papers = paginated.items
        
        # 构建试卷数据
        papers_data = []
        for paper in papers:
            try:
                if hasattr(paper, 'to_dict'):
                    papers_data.append(paper.to_dict())
                else:
                    # 手动构建字典
                    papers_data.append({
                        'id': paper.id,
                        'name': paper.name,
                        'region': paper.region,
                        'subject': paper.subject,
                        'stage': paper.stage,
                        'source_type': paper.source_type,
                        'source': paper.source,
                        'year': paper.year
                    })
            except Exception as paper_error:
                print(f"处理试卷数据时出错: {paper_error}")
        
        return jsonify(papers_data)
    except Exception as e:
        print(f"筛选试卷出错: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': str(e)
        }), 500
END_FUNCTION

# 3. 将修改后的函数替换到app.py中
echo "替换 filter_papers 函数..."
END_LINE=$(grep -n "^@app.route" $APP_PATH | awk -v start=$START_LINE '$1 > start {print $1; exit}' | cut -d':' -f1)
END_LINE=$((END_LINE - 1))

# 如果找不到下一个路由，则假设函数到文件末尾
if [ -z "$END_LINE" ]; then
    END_LINE=$(wc -l < $APP_PATH)
fi

# 替换函数
sed -i "${START_LINE},${END_LINE}d" $APP_PATH
sed -i "${START_LINE}r $TMP_FILE" $APP_PATH

# 4. 修复papers_list函数中的case语法
echo "修复papers_list函数中的case语法..."
PAPERS_LIST_START=$(grep -n "def papers_list" $APP_PATH | head -1 | cut -d':' -f1)
PAPERS_LIST_END=$((PAPERS_LIST_START + 200))

# 创建一个临时文件来存储修改后的函数
TMP_PAPERS_LIST="/tmp/papers_list_fixed.py"

# 提取papers_list函数
sed -n "${PAPERS_LIST_START},${PAPERS_LIST_END}p" $APP_PATH > /tmp/papers_list_original.py

# 查找case语句所在的行
CASE_LINES=$(grep -n "case(" /tmp/papers_list_original.py | cut -d':' -f1)

# 创建修复后的函数
cat > $TMP_PAPERS_LIST << 'END_PAPERS_LIST'
@app.route('/papers')
def papers_list():
    try:
        # 获取筛选参数
        region = request.args.get('region')
        subject = request.args.get('subject')
        stage = request.args.get('stage')
        source_type = request.args.get('source_type')
        source = request.args.get('source')
        year = request.args.get('year')
        keyword = request.args.get('keyword')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        papers_query = Paper.query
        
        # 添加筛选条件
        if region:
            papers_query = papers_query.filter(Paper.region == region)
        if subject:
            papers_query = papers_query.filter(Paper.subject == subject)
        if stage:
            papers_query = papers_query.filter(Paper.stage == stage)
        if source_type:
            papers_query = papers_query.filter(Paper.source_type == source_type)
        if source:
            papers_query = papers_query.filter(Paper.source == source)
        if year:
            try:
                if isinstance(year, str) and year.isdigit():
                    papers_query = papers_query.filter(Paper.year == int(year))
                elif isinstance(year, (int, float)):
                    papers_query = papers_query.filter(Paper.year == int(year))
            except (ValueError, TypeError) as e:
                print(f"年份转换错误: {e}")
        if keyword:
            papers_query = papers_query.filter(Paper.name.like(f'%{keyword}%'))
        
        try:
            # 排序规则：年份降序 > 湖北地区优先 > 下学期优先于上学期 > 3月优先于2月优先于1月 > 上传时间降序
            sorted_query = papers_query.order_by(
                Paper.year.desc(),
                # 湖北地区优先
                case((Paper.region == "湖北", 1), else_=0).desc(),
                # 下学期优先于上学期
                case(
                    (Paper.name.like("%下学期%"), 2),
                    (Paper.name.like("%上学期%"), 1),
                    else_=0
                ).desc(),
                # 3月优先于2月优先于1月
                case(
                    (Paper.name.like("%3月%"), 3),
                    (Paper.name.like("%2月%"), 2),
                    (Paper.name.like("%1月%"), 1),
                    else_=0
                ).desc(),
                # 最后按上传时间降序排序(最新上传的优先)
                Paper.upload_time.desc()
            )
            
            # 获取总试卷数
            total_papers = sorted_query.count()
            print(f"总共 {total_papers} 份试卷")
            
            # 实现分页
            paginated_papers = sorted_query.paginate(page=page, per_page=per_page, error_out=False)
            papers = paginated_papers.items
            
            print(f"成功查询到当前页 {len(papers)} 份试卷")
        except Exception as query_error:
            print(f"排序查询失败: {str(query_error)}")
            traceback.print_exc()
            # 使用简单查询作为备选
            sorted_query = papers_query.order_by(Paper.year.desc())
            total_papers = sorted_query.count()
            paginated_papers = sorted_query.paginate(page=page, per_page=per_page, error_out=False)
            papers = paginated_papers.items
            print(f"备选查询成功，获取到 {len(papers)} 份试卷")
        
        try:
            # 获取所有地区、学科、学段、来源类型和来源
            regions = db.session.query(Paper.region).distinct().all()
            subjects = db.session.query(Paper.subject).distinct().all()
            stages = db.session.query(Paper.stage).distinct().all()
            source_types = db.session.query(Paper.source_type).distinct().all()
            sources = db.session.query(Paper.source).distinct().all()
            print("成功获取筛选选项")
        except Exception as filter_error:
            print(f"获取筛选选项失败: {str(filter_error)}")
            traceback.print_exc()
            # 提供空列表作为备选
            regions = []
            subjects = []
            stages = []
            source_types = []
            sources = []
        
        # 准备渲染模板
        print("开始渲染模板")
        return render_template('papers.html', 
                             papers=papers, 
                             regions=regions, 
                             subjects=subjects, 
                             stages=stages, 
                             source_types=source_types, 
                             sources=sources, 
                             active_page='papers',
                             pagination=paginated_papers,
                             per_page=per_page,
                             page=page,
                             total=total_papers,
                             # 传递当前的筛选参数到模板
                             current_filters={
                                 'region': region,
                                 'subject': subject,
                                 'stage': stage,
                                 'source_type': source_type,
                                 'source': source,
                                 'year': year,
                                 'keyword': keyword
                             })
    except Exception as e:
        print(f"获取试卷列表失败: {str(e)}")
        traceback.print_exc()
        return render_template('papers.html', papers=[], error=str(e))
END_PAPERS_LIST

# 替换papers_list函数
PAPERS_LIST_END=$(grep -n "^@app.route" $APP_PATH | awk -v start=$PAPERS_LIST_START '$1 > start {print $1; exit}' | cut -d':' -f1)
PAPERS_LIST_END=$((PAPERS_LIST_END - 1))

# 如果找不到下一个路由，则假设函数到文件末尾
if [ -z "$PAPERS_LIST_END" ]; then
    PAPERS_LIST_END=$(wc -l < $APP_PATH)
fi

# 替换函数
sed -i "${PAPERS_LIST_START},${PAPERS_LIST_END}d" $APP_PATH
sed -i "${PAPERS_LIST_START}r $TMP_PAPERS_LIST" $APP_PATH

# 5. 确保导入了正确的 case 函数
echo "确保导入了正确的 case 函数..."
if ! grep -q "from sqlalchemy import case" $APP_PATH; then
    # 在文件开头添加导入语句
    sed -i '1s/^/from sqlalchemy import case\n/' $APP_PATH
    echo "已添加 case 函数导入"
fi

# 6. 检查语法
echo "检查 Python 语法..."
python3 -m py_compile $APP_PATH
if [ $? -ne 0 ]; then
    echo "语法检查失败，恢复备份..."
    cp $APP_BACKUP $APP_PATH
    exit 1
fi
echo "语法检查通过！"

# 7. 重启服务
echo "重启服务..."
systemctl restart question_bank

# 8. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20

# 9. 等待服务启动
echo "等待服务启动..."
sleep 3

# 10. 测试筛选功能
echo "测试筛选功能..."
curl -s -X POST http://localhost:5001/filter_papers \
  -H "Content-Type: application/json" \
  -d '{"region":"湖北","page":1,"per_page":5}' | head -20

echo "===== SQLAlchemy case() 函数语法手动修复完成 ====="
EOF
