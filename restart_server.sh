#!/bin/bash

# 试卷数据库修复成功后重启应用
# 功能: 停止当前运行的服务，然后重新启动

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}      试卷系统重启工具                           ${NC}"
echo -e "${GREEN}==================================================${NC}"

# 停止当前正在运行的进程
echo -e "${YELLOW}正在停止当前运行的Flask进程...${NC}"
pkill -f "python3 app.py" || true

# 等待进程完全停止
sleep 2

# 再次确认进程已停止
if pgrep -f "python3 app.py" > /dev/null; then
    echo -e "${RED}仍有Flask进程在运行，强制终止...${NC}"
    pkill -9 -f "python3 app.py" || true
    sleep 1
fi

# 启动应用
echo -e "${YELLOW}正在启动应用...${NC}"

# 使用nohup在后台运行应用
nohup python3 app.py > app.log 2>&1 &

# 检查应用是否成功启动
sleep 3
if pgrep -f "python3 app.py" > /dev/null; then
    echo -e "${GREEN}应用已成功在后台启动!${NC}"
    echo -e "${BLUE}应用日志保存在 app.log 文件中${NC}"
    echo -e "${BLUE}您现在可以通过浏览器访问应用${NC}"
else
    echo -e "${RED}应用启动失败，请检查错误日志${NC}"
    tail -n 20 app.log
fi

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}      重启操作完成                             ${NC}"
echo -e "${GREEN}==================================================${NC}"
