#!/bin/bash

# 脚本用于在服务器上直接修复client.html文件
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank/templates"

# 创建修复脚本
cat > /tmp/fix_client.sh << 'EOF'
#!/bin/bash

# 目标文件
TARGET_FILE="/var/www/question_bank/templates/client.html"

# 创建备份
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
cp $TARGET_FILE ${TARGET_FILE}.bak_${TIMESTAMP}
echo "创建备份: ${TARGET_FILE}.bak_${TIMESTAMP}"

# 创建临时文件
TMP_FILE=$(mktemp)

# 添加localStorage功能
cat > $TMP_FILE << 'EOL'
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
    }
}

// 保存已选题目到localStorage
function saveSelectedQuestions() {
    try {
        const questionIds = Array.from(selectedQuestions);
        localStorage.setItem("selectedQuestions", JSON.stringify(questionIds));
        console.log("保存题目到localStorage:", questionIds.length);
    } catch (error) {
        console.error("保存已选题目出错:", error);
    }
}
EOL

# 1. 添加localStorage函数
sed -i "/let selectedQuestions = new Set();/r $TMP_FILE" $TARGET_FILE

# 2. 添加恢复函数调用
sed -i "/document.addEventListener('DOMContentLoaded', function() {/a \\            // 从localStorage恢复已选题目\\n            restoreSelectedQuestions();" $TARGET_FILE

# 3. 在点击处理中添加保存
sed -i "s/updateDownloadPanel();/updateDownloadPanel();\\n                    \/\/ 保存到localStorage\\n                    saveSelectedQuestions();/g" $TARGET_FILE

# 4. 在toggleSelect函数中添加保存
sed -i "/\/\/ 更新下载面板/{n;s/updateDownloadPanel();/updateDownloadPanel();\\n            \\n            \/\/ 保存到localStorage\\n            saveSelectedQuestions();/}" $TARGET_FILE

# 5. 在clearSelectedQuestions函数中添加清除localStorage
sed -i "/document.getElementById('paperTitleModal').style.display = 'none';/a \\            \\n            \/\/ 从localStorage中也清除\\n            localStorage.removeItem(\"selectedQuestions\");" $TARGET_FILE

# 6. 在generatePaper函数中添加清除localStorage
sed -i "/\/\/ 下载成功后清空已选题目/{n;n;a \\                \\n                \/\/ 从localStorage中也清除\\n                localStorage.removeItem(\"selectedQuestions\");}" $TARGET_FILE

echo "修复完成！"
EOF

# 上传修复脚本到服务器
echo "上传修复脚本到服务器..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no /tmp/fix_client.sh $USER@$SERVER:/tmp/fix_client.sh

# 执行修复脚本
echo "在服务器上执行修复脚本..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "chmod +x /tmp/fix_client.sh && /tmp/fix_client.sh"

# 重启服务
echo "重启服务器应用..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"

echo "操作完成！"
