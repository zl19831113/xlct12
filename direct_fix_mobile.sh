#!/bin/bash

# 脚本用于直接修复移动端localStorage问题
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank/templates"

# 创建临时文件
TMP_FILE="/tmp/client.html.fixed"

# 下载当前文件
echo "下载当前client.html文件..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $USER@$SERVER:$REMOTE_DIR/client.html $TMP_FILE

# 创建备份
echo "在服务器上创建备份..."
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_COMMAND="cp $REMOTE_DIR/client.html $REMOTE_DIR/client.html.bak_$TIMESTAMP"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "$BACKUP_COMMAND"

# 修改文件 - 添加localStorage功能
echo "修改client.html文件..."

# 1. 添加localStorage函数
sed -i '/let selectedQuestions = new Set();/a\
        \
        // 从localStorage恢复已选题目\
        function restoreSelectedQuestions() {\
            try {\
                const savedQuestions = localStorage.getItem("selectedQuestions");\
                if (savedQuestions) {\
                    const questionIds = JSON.parse(savedQuestions);\
                    questionIds.forEach(id => selectedQuestions.add(parseInt(id)));\
                    console.log("从localStorage恢复已选题目:", selectedQuestions.size);\
                }\
            } catch (error) {\
                console.error("恢复已选题目出错:", error);\
            }\
        }\
        \
        // 保存已选题目到localStorage\
        function saveSelectedQuestions() {\
            try {\
                const questionIds = Array.from(selectedQuestions);\
                localStorage.setItem("selectedQuestions", JSON.stringify(questionIds));\
                console.log("保存题目到localStorage:", questionIds.length);\
            } catch (error) {\
                console.error("保存已选题目出错:", error);\
            }\
        }' $TMP_FILE

# 2. 添加恢复函数调用
sed -i '/document.addEventListener('\''DOMContentLoaded'\'', function() {/a\
            // 从localStorage恢复已选题目\
            restoreSelectedQuestions();' $TMP_FILE

# 3. 在点击处理中添加保存
sed -i 's/updateDownloadPanel();/updateDownloadPanel();\
                    // 保存到localStorage\
                    saveSelectedQuestions();/g' $TMP_FILE

# 4. 在toggleSelect函数中添加保存
sed -i '/\/\/ 更新下载面板/,/updateDownloadPanel();/c\
            // 更新下载面板\
            updateDownloadPanel();\
            \
            // 保存到localStorage\
            saveSelectedQuestions();' $TMP_FILE

# 5. 在clearSelectedQuestions函数中添加清除localStorage
sed -i '/document.getElementById('\''paperTitleModal'\'').style.display = '\''none'\'';/a\
            \
            // 从localStorage中也清除\
            localStorage.removeItem("selectedQuestions");' $TMP_FILE

# 6. 在generatePaper函数中添加清除localStorage
sed -i '/\/\/ 下载成功后清空已选题目/,/updateDownloadPanel();/c\
                // 下载成功后清空已选题目\
                selectedQuestions.clear();\
                updateDownloadPanel();\
                \
                // 从localStorage中也清除\
                localStorage.removeItem("selectedQuestions");' $TMP_FILE

# 上传修改后的文件
echo "上传修改后的client.html文件..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $TMP_FILE $USER@$SERVER:$REMOTE_DIR/client.html

# 重启服务
echo "重启服务器应用..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"

# 清理临时文件
rm $TMP_FILE

echo "修复完成！"
