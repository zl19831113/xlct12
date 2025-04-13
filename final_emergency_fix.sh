#!/bin/bash
# 紧急修复脚本 - 直接修改header.html和添加缺失的路由

ssh root@120.26.12.100 << 'EOF'
echo "===== 开始紧急修复 ====="

# 1. 直接修改header.html文件，移除或替换client路由链接
HEADER_PATH="/var/www/question_bank/templates/header.html"
echo "备份header.html..."
cp $HEADER_PATH ${HEADER_PATH}.bak_emergency

echo "修改header.html..."
# 方法1：注释掉client链接行
sed -i 's/<a href="{{ url_for('\''client'\'') }}" class="header-link.*<\/a>/<!-- 临时移除client链接 -->/g' $HEADER_PATH

# 2. 添加client路由到app.py
APP_PATH="/var/www/question_bank/app.py"
echo "备份app.py..."
cp $APP_PATH ${APP_PATH}.bak_emergency

echo "添加client路由到app.py..."
# 在app.py的适当位置添加client路由
# 在文件末尾但在if __name__ == '__main__'之前添加
sed -i '/if __name__ == '\''__main__'\''/i \
# 添加client路由以修复模板错误\
@app.route('\''/client'\'')\
def client():\
    return render_template('\''client.html'\'', active_page='\''client'\'')\
\
# 如果client.html不存在，创建一个简单的页面\
if not os.path.exists('\''templates/client.html'\''):\
    with open('\''templates/client.html'\'', '\''w'\'') as f:\
        f.write('\''{% extends "layout.html" %}\\n{% block content %}\\n<div class="container">\\n<h1>小鹿出题功能即将上线</h1>\\n<p>该功能正在开发中，敬请期待！</p>\\n</div>\\n{% endblock %}'\'')\
' $APP_PATH

# 3. 检查是否有layout.html，如果没有，创建一个基本的
LAYOUT_PATH="/var/www/question_bank/templates/layout.html"
if [ ! -f "$LAYOUT_PATH" ]; then
    echo "创建基本的layout.html..."
    cat > $LAYOUT_PATH << 'END_LAYOUT'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小鹿题库系统</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    {% include 'header.html' %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; 2025 小鹿题库系统 - 版权所有</p>
        </div>
    </footer>
    
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
END_LAYOUT
fi

# 4. 确保templates/client.html存在
CLIENT_PATH="/var/www/question_bank/templates/client.html"
if [ ! -f "$CLIENT_PATH" ]; then
    echo "创建client.html..."
    mkdir -p $(dirname "$CLIENT_PATH")
    cat > $CLIENT_PATH << 'END_CLIENT'
{% extends "layout.html" %}
{% block content %}
<div class="container">
    <h1>小鹿出题功能即将上线</h1>
    <p>该功能正在开发中，敬请期待！</p>
</div>
{% endblock %}
END_CLIENT
fi

# 5. 重启服务
echo "重启服务..."
systemctl restart question_bank

# 6. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20

# 7. 等待服务启动
echo "等待服务启动..."
sleep 3

# 8. 测试网站访问
echo "测试网站访问..."
curl -s -I http://localhost:5001/ | head -1

echo "===== 紧急修复完成 ====="
EOF
