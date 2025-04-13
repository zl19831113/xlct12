#!/bin/bash

# 正确修改hosts文件的脚本

echo "===== 添加域名映射到hosts文件 ====="

# 使用sudo但以不同方式写入hosts文件
echo "通过sudo写入hosts文件..."
sudo sh -c 'echo "120.26.12.100 xlct12.com www.xlct12.com" >> /etc/hosts'

# 确认hosts文件被正确修改
echo "检查hosts文件是否已修改..."
grep "xlct12.com" /etc/hosts

# 清除本地DNS缓存
echo "清除DNS缓存..."
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

echo "===== hosts文件修改完成 ====="
echo "现在请重新尝试访问 https://xlct12.com/"
echo "如果还是不能访问，请关闭并重新打开浏览器再试"
