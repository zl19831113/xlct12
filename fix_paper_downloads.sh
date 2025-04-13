#!/bin/bash

# 修复试卷下载功能的脚本 - 增强版
# 2025-03-29

# 显示彩色文本
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}===================================================${NC}"
echo -e "${GREEN}      修复试卷下载功能 - 增强版一键式修复工具      ${NC}"
echo -e "${GREEN}===================================================${NC}"

# 检查当前目录是否是项目目录
if [ ! -f "app.py" ]; then
    echo -e "${RED}错误: 未找到app.py文件，请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 步骤1: 备份app.py和数据库文件
echo -e "\n${YELLOW}步骤1: 创建安全备份...${NC}"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
BACKUP_FILE="app.py.bak.$TIMESTAMP"
cp app.py "$BACKUP_FILE"
echo -e "${BLUE}已备份app.py到 $BACKUP_FILE${NC}"

# 备份数据库
DB_PATH="instance/questions.db"
if [ ! -f "$DB_PATH" ]; then
    DB_PATH="questions.db"
fi

if [ -f "$DB_PATH" ]; then
    DB_BACKUP="$DB_PATH.bak.$TIMESTAMP"
    cp "$DB_PATH" "$DB_BACKUP"
    echo -e "${BLUE}已备份数据库到 $DB_BACKUP${NC}"
else
    echo -e "${RED}警告: 未找到数据库文件，跳过备份${NC}"
fi

# 步骤2: 修复数据库中的文件路径 - 使用增强版匹配算法
echo -e "\n${YELLOW}步骤2: 修复数据库中的文件路径指向...${NC}"
echo -e "${BLUE}运行增强版匹配算法...${NC}"
python3 fix_papers_db.py

# 检查上一步是否成功
if [ $? -ne 0 ]; then
    echo -e "${RED}修复数据库时出错，但会继续下一步...${NC}"
fi

# 步骤3: 自动检测需要特殊处理的云学名校联盟试卷
echo -e "\n${YELLOW}步骤3: 检测需要特殊处理的试卷...${NC}"

# 创建一个临时Python脚本来检测特殊试卷
cat > detect_special_papers.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检测需要特殊处理的试卷
"""

import os
import sqlite3

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, 'questions.db')

def main():
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查papers表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
    if not cursor.fetchone():
        print("错误: 数据库中不存在papers表")
        conn.close()
        return
    
    # 查找特殊试卷
    cursor.execute("SELECT id, name FROM papers WHERE name LIKE '%云学名校联盟%' AND name LIKE '%联考%'")
    special_papers = cursor.fetchall()
    
    print(f"找到 {len(special_papers)} 份需要特殊处理的云学名校联盟系列试卷")
    
    if len(special_papers) > 0:
        print("\n示例:")
        for i, (paper_id, paper_name) in enumerate(special_papers[:5], 1):
            print(f"{i}. ID={paper_id}, 名称='{paper_name}'")
        
        if len(special_papers) > 5:
            print(f"...以及其他 {len(special_papers) - 5} 份试卷")
    
    conn.close()

if __name__ == "__main__":
    main()
EOF

# 运行检测脚本
python3 detect_special_papers.py

# 步骤4: 进行最后的准备
echo -e "\n${YELLOW}步骤4: 准备重启应用...${NC}"

# 检查是否有gunicorn进程
GUNICORN_PID=$(pgrep gunicorn)
FLASK_PID=$(pgrep -f "python3.*app.py")

if [ ! -z "$GUNICORN_PID" ]; then
    echo -e "${BLUE}检测到Gunicorn进程，正在重启...${NC}"
    # 如果使用systemd
    if systemctl is-active --quiet zujuanwang.service; then
        sudo systemctl restart zujuanwang.service
        echo -e "${GREEN}已通过systemd重启服务${NC}"
    else
        # 手动重启
        kill -HUP $GUNICORN_PID
        echo -e "${GREEN}已发送HUP信号给Gunicorn进程${NC}"
    fi
elif [ ! -z "$FLASK_PID" ]; then
    echo -e "${BLUE}检测到Flask开发服务器，正在重启...${NC}"
    kill $FLASK_PID
    nohup python3 app.py > flask.log 2>&1 &
    echo -e "${GREEN}已重启Flask开发服务器${NC}"
else
    echo -e "${YELLOW}未检测到运行中的应用，正在启动...${NC}"
    nohup python3 app.py > flask.log 2>&1 &
    echo -e "${GREEN}已启动应用${NC}"
fi

# 清理临时文件
rm -f detect_special_papers.py

echo -e "\n${GREEN}===================================================${NC}"
echo -e "${GREEN}        修复完成！现在试卷下载应该正常工作         ${NC}"
echo -e "${GREEN}===================================================${NC}"
echo -e "${YELLOW}提示：如果仍有部分试卷无法下载，请手动检查uploads目录中是否包含对应试卷文件${NC}"

exit 0 