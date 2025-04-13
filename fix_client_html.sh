#!/bin/bash

# 脚本用于修复client.html文件，添加localStorage功能
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank/templates"
LOCAL_FILE="/var/www/question_bank/templates/client.html"

# 创建备份
echo "在服务器上创建备份..."
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_COMMAND="cp $LOCAL_FILE ${LOCAL_FILE}.bak_$TIMESTAMP"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "$BACKUP_COMMAND"

if [ $? -eq 0 ]; then
    echo "服务器备份创建成功: client.html.bak_$TIMESTAMP"
else
    echo "警告: 无法在服务器上创建备份，操作终止"
    exit 1
fi

# 添加localStorage功能到client.html文件
echo "正在修改client.html文件..."

# 1. 添加恢复和保存函数
ADD_FUNCTIONS='
        // 从localStorage恢复已选题目
        function restoreSelectedQuestions() {
            try {
                const savedQuestions = localStorage.getItem("selectedQuestions");
                if (savedQuestions) {
                    const questionIds = JSON.parse(savedQuestions);
                    questionIds.forEach(id => selectedQuestions.add(parseInt(id)));
                    console.log("从localStorage恢复已选题目:", selectedQuestions.size);
                }
            } catch (error) {
                console.error("恢复已选题目出错:", error);
                selectedQuestions = new Set();
            }
        }
        
        // 保存已选题目到localStorage
        function saveSelectedQuestions() {
            try {
                const questionIds = Array.from(selectedQuestions);
                localStorage.setItem("selectedQuestions", JSON.stringify(questionIds));
            } catch (error) {
                console.error("保存已选题目出错:", error);
            }
        }

        // 使用 DOMContentLoaded 确保在 DOM 加载完成后绑定事件'

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i 's/        \/\/ 使用 DOMContentLoaded 确保在 DOM 加载完成后绑定事件/$ADD_FUNCTIONS/g' $LOCAL_FILE"

# 2. 添加恢复函数调用
ADD_RESTORE='            // 从localStorage恢复已选题目
            restoreSelectedQuestions();
            const container = document.getElementById("questionCards");'

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i 's/            const container = document.getElementById(\"questionCards\");/$ADD_RESTORE/g' $LOCAL_FILE"

# 3. 在点击处理中添加保存
ADD_SAVE_IN_CLICK='                    updateDownloadPanel();
                    // 保存到localStorage
                    saveSelectedQuestions();
                    return false; // 阻止事件冒泡和默认行为'

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i 's/                    updateDownloadPanel();\\n                    return false; \/\/ 阻止事件冒泡和默认行为/$ADD_SAVE_IN_CLICK/g' $LOCAL_FILE"

# 4. 在toggleSelect函数中添加保存
ADD_SAVE_IN_TOGGLE='            // 更新下载面板
            updateDownloadPanel();
            
            // 保存到localStorage
            saveSelectedQuestions();'

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i 's/            \/\/ 更新下载面板\\n            updateDownloadPanel();/$ADD_SAVE_IN_TOGGLE/g' $LOCAL_FILE"

# 5. 在clearSelectedQuestions函数中添加清除localStorage
ADD_CLEAR_STORAGE='            // 关闭弹窗
            document.getElementById("paperTitleModal").style.display = "none";
            
            // 从localStorage中也清除
            localStorage.removeItem("selectedQuestions");'

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i 's/            \/\/ 关闭弹窗\\n            document.getElementById(\"paperTitleModal\").style.display = \"none\";/$ADD_CLEAR_STORAGE/g' $LOCAL_FILE"

# 6. 在generatePaper函数中添加清除localStorage
ADD_CLEAR_IN_GENERATE='                // 下载成功后清空已选题目
                selectedQuestions.clear();
                updateDownloadPanel();
                
                // 从localStorage中也清除
                localStorage.removeItem("selectedQuestions");'

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i 's/                \/\/ 下载成功后清空已选题目\\n                selectedQuestions.clear();\\n                updateDownloadPanel();/$ADD_CLEAR_IN_GENERATE/g' $LOCAL_FILE"

# 重启服务
echo "正在重启服务器应用..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"

if [ $? -eq 0 ]; then
    echo "服务器应用重启成功!"
else
    echo "警告: 服务器应用重启失败，请手动重启"
fi

echo "操作完成!"
