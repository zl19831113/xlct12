#!/bin/bash
# 修复模板中的路由问题

# 连接到服务器
ssh root@120.26.12.100 << 'EOF'
# 1. 检查header.html文件中的路由问题
echo "检查header.html文件中的路由问题..."
HEADER_PATH="/var/www/question_bank/templates/header.html"

# 备份header.html
cp $HEADER_PATH ${HEADER_PATH}.bak_$(date +%Y%m%d%H%M%S)

# 修复header.html中的路由问题
# 将upload_page替换为upload_paper
sed -i 's/url_for("upload_page")/url_for("upload_paper")/g' $HEADER_PATH

# 2. 添加缺失的路由到app.py
echo "添加缺失的路由到app.py..."
APP_PATH="/var/www/question_bank/app.py"

# 检查app.py是否已经包含upload_paper路由
if ! grep -q "def upload_paper" $APP_PATH; then
    # 如果没有找到upload_paper路由，添加一个简单的实现
    cat >> $APP_PATH << 'END_ROUTE'

# 确保upload_paper路由存在
@app.route('/upload_paper')
def upload_paper():
    try:
        # 获取所有地区、学科、学段等数据
        regions = db.session.query(Paper.region).distinct().all()
        subjects = db.session.query(Paper.subject).distinct().all()
        stages = db.session.query(Paper.stage).distinct().all()
        source_types = db.session.query(Paper.source_type).distinct().all()
        sources = db.session.query(Paper.source).distinct().all()
        
        return render_template('upload_paper.html', 
                              regions=[r[0] for r in regions if r[0]], 
                              subjects=[s[0] for s in subjects if s[0]], 
                              stages=[s[0] for s in stages if s[0]], 
                              source_types=[st[0] for st in source_types if st[0]], 
                              sources=[s[0] for s in sources if s[0]],
                              active_page='upload_paper')
    except Exception as e:
        print(f"上传页面加载失败: {str(e)}")
        traceback.print_exc()
        return render_template('upload_paper.html', error=str(e))
END_ROUTE
    echo "已添加upload_paper路由"
else
    echo "upload_paper路由已存在"
fi

# 3. 重启服务
echo "重启服务..."
systemctl restart question_bank

# 4. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank
EOF
