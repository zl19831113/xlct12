#!/bin/bash

# 脚本用于修复client.html和papers.html问题
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 1. 恢复client.html备份
echo "恢复client.html备份..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cp $REMOTE_DIR/templates/client.html.bak_20250402134551 $REMOTE_DIR/templates/client.html"

# 2. 检查client.html文件内容
echo "检查client.html文件内容..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "grep -A 5 'localStorage' $REMOTE_DIR/templates/client.html"

# 3. 手动添加localStorage功能到client.html
echo "添加localStorage功能到client.html..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cat > $REMOTE_DIR/localStorage_fix.js << 'EOF'
// 从localStorage恢复已选题目
function restoreSelectedQuestions() {
    try {
        const savedQuestions = localStorage.getItem('selectedQuestions');
        if (savedQuestions) {
            const questionIds = JSON.parse(savedQuestions);
            questionIds.forEach(id => selectedQuestions.add(parseInt(id)));
            console.log('从localStorage恢复已选题目:', selectedQuestions.size);
        }
    } catch (error) {
        console.error('恢复已选题目出错:', error);
    }
}

// 保存已选题目到localStorage
function saveSelectedQuestions() {
    try {
        const questionIds = Array.from(selectedQuestions);
        localStorage.setItem('selectedQuestions', JSON.stringify(questionIds));
        console.log('保存题目到localStorage:', questionIds.length);
    } catch (error) {
        console.error('保存已选题目出错:', error);
    }
}
EOF"

# 4. 将localStorage功能插入到client.html
echo "将localStorage功能插入到client.html..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i '/let selectedQuestions = new Set();/a\\
        \\
        // 从localStorage恢复已选题目\\
        function restoreSelectedQuestions() {\\
            try {\\
                const savedQuestions = localStorage.getItem(\"selectedQuestions\");\\
                if (savedQuestions) {\\
                    const questionIds = JSON.parse(savedQuestions);\\
                    questionIds.forEach(id => selectedQuestions.add(parseInt(id)));\\
                    console.log(\"从localStorage恢复已选题目:\", selectedQuestions.size);\\
                }\\
            } catch (error) {\\
                console.error(\"恢复已选题目出错:\", error);\\
            }\\
        }\\
        \\
        // 保存已选题目到localStorage\\
        function saveSelectedQuestions() {\\
            try {\\
                const questionIds = Array.from(selectedQuestions);\\
                localStorage.setItem(\"selectedQuestions\", JSON.stringify(questionIds));\\
                console.log(\"保存题目到localStorage:\", questionIds.length);\\
            } catch (error) {\\
                console.error(\"保存已选题目出错:\", error);\\
            }\\
        }' $REMOTE_DIR/templates/client.html"

# 5. 添加恢复函数调用
echo "添加恢复函数调用..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i '/document.addEventListener.*DOMContentLoaded.*function() {/a\\
            // 从localStorage恢复已选题目\\
            restoreSelectedQuestions();' $REMOTE_DIR/templates/client.html"

# 6. 在toggleSelect函数中添加保存
echo "在toggleSelect函数中添加保存..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i '/\/\/ 更新下载面板/,/updateDownloadPanel();/c\\
            // 更新下载面板\\
            updateDownloadPanel();\\
            \\
            // 保存到localStorage\\
            saveSelectedQuestions();' $REMOTE_DIR/templates/client.html"

# 7. 在clearSelectedQuestions函数中添加清除localStorage
echo "在clearSelectedQuestions函数中添加清除localStorage..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i '/document.getElementById.*paperTitleModal.*style.display = \"none\";/a\\
            \\
            // 从localStorage中也清除\\
            localStorage.removeItem(\"selectedQuestions\");' $REMOTE_DIR/templates/client.html"

# 8. 在generatePaper函数中添加清除localStorage
echo "在generatePaper函数中添加清除localStorage..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i '/\/\/ 下载成功后清空已选题目/,/updateDownloadPanel();/c\\
                // 下载成功后清空已选题目\\
                selectedQuestions.clear();\\
                updateDownloadPanel();\\
                \\
                // 从localStorage中也清除\\
                localStorage.removeItem(\"selectedQuestions\");' $REMOTE_DIR/templates/client.html"

# 9. 修复papers.html页面的分页问题
echo "修复papers.html页面的分页问题..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cat > $REMOTE_DIR/pagination_fix.js << 'EOF'
// 保留筛选参数的分页导航函数
function navigateWithFilters(pageNum) {
    console.log('正在跳转到页面', pageNum, '并保留所有筛选条件');
    
    // 获取当前的URL参数
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('page', pageNum);
    
    // 保留所有可能的筛选参数
    const filtersToKeep = ['region', 'subject', 'stage', 'source', 'source_type', 'year', 'keyword'];
    filtersToKeep.forEach(filter => {
        const value = urlParams.get(filter);
        if (value) {
            console.log(`保留URL中的筛选参数: ${filter}=${value}`);
        }
    });
    
    // 添加当前选择的筛选条件（可能是通过UI选择但尚未提交的）
    for (const key in selectedFilters) {
        if (selectedFilters[key]) {
            urlParams.set(key, selectedFilters[key]);
            console.log(`添加已选择的筛选条件: ${key}=${selectedFilters[key]}`);
        }
    }
    
    // 检查搜索输入框的值
    const searchInput = document.getElementById('searchInput');
    if (searchInput && searchInput.value.trim()) {
        urlParams.set('keyword', searchInput.value.trim());
        console.log(`添加搜索关键词: keyword=${searchInput.value.trim()}`);
    }
    
    // 获取当前激活的筛选标签
    const filterTags = document.querySelectorAll('.filter-tag');
    filterTags.forEach(tag => {
        const filterType = tag.getAttribute('data-type');
        const filterValue = tag.getAttribute('data-value');
        if (filterType && filterValue) {
            urlParams.set(filterType, filterValue);
            console.log(`从筛选标签添加: ${filterType}=${filterValue}`);
        }
    });
    
    // 形成新URL并跳转
    const newUrl = \`/papers?\${urlParams.toString()}\`;
    console.log(\`跳转到新URL: \${newUrl}\`);
    window.location.href = newUrl;
}

// 切换页码
function changePage(direction) {
    // 检查当前是否在搜索或筛选模式
    const urlParams = new URLSearchParams(window.location.search);
    const hasFilters = urlParams.has('keyword') || 
                      urlParams.has('region') || 
                      urlParams.has('subject') || 
                      urlParams.has('stage') || 
                      urlParams.has('source_type') || 
                      urlParams.has('year');
    
    // 获取当前页码
    let nextPage = parseInt(urlParams.get('page') || '1') + direction;
    if (nextPage < 1) nextPage = 1;
    
    // 无论是否有筛选条件，都使用navigateWithFilters确保保留筛选参数
    navigateWithFilters(nextPage);
}

// 跳转到指定页面
function goToPage(pageNum) {
    // 直接使用navigateWithFilters函数确保保留所有筛选条件
    navigateWithFilters(pageNum);
}
EOF"

# 10. 直接将修复后的函数插入到papers.html页面底部
echo "将修复后的函数插入到papers.html页面..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i '/function navigateWithFilters/,/}$/d' $REMOTE_DIR/templates/papers.html"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i '/function changePage/,/}$/d' $REMOTE_DIR/templates/papers.html"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i '/function goToPage/,/}$/d' $REMOTE_DIR/templates/papers.html"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cat $REMOTE_DIR/pagination_fix.js >> $REMOTE_DIR/templates/papers.html.tmp"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "sed -i '/<\/script>/i\\
        // 保留筛选参数的分页导航函数\\
        function navigateWithFilters(pageNum) {\\
            console.log(\"正在跳转到页面\", pageNum, \"并保留所有筛选条件\");\\
            \\
            // 获取当前的URL参数\\
            const urlParams = new URLSearchParams(window.location.search);\\
            urlParams.set(\"page\", pageNum);\\
            \\
            // 保留所有可能的筛选参数\\
            const filtersToKeep = [\"region\", \"subject\", \"stage\", \"source\", \"source_type\", \"year\", \"keyword\"];\\
            filtersToKeep.forEach(filter => {\\
                const value = urlParams.get(filter);\\
                if (value) {\\
                    console.log(`保留URL中的筛选参数: ${filter}=${value}`);\\
                }\\
            });\\
            \\
            // 添加当前选择的筛选条件（可能是通过UI选择但尚未提交的）\\
            for (const key in selectedFilters) {\\
                if (selectedFilters[key]) {\\
                    urlParams.set(key, selectedFilters[key]);\\
                    console.log(`添加已选择的筛选条件: ${key}=${selectedFilters[key]}`);\\
                }\\
            }\\
            \\
            // 检查搜索输入框的值\\
            const searchInput = document.getElementById(\"searchInput\");\\
            if (searchInput && searchInput.value.trim()) {\\
                urlParams.set(\"keyword\", searchInput.value.trim());\\
                console.log(`添加搜索关键词: keyword=${searchInput.value.trim()}`);\\
            }\\
            \\
            // 获取当前激活的筛选标签\\
            const filterTags = document.querySelectorAll(\".filter-tag\");\\
            filterTags.forEach(tag => {\\
                const filterType = tag.getAttribute(\"data-type\");\\
                const filterValue = tag.getAttribute(\"data-value\");\\
                if (filterType && filterValue) {\\
                    urlParams.set(filterType, filterValue);\\
                    console.log(`从筛选标签添加: ${filterType}=${filterValue}`);\\
                }\\
            });\\
            \\
            // 形成新URL并跳转\\
            const newUrl = \`/papers?\${urlParams.toString()}\`;\\
            console.log(\`跳转到新URL: \${newUrl}\`);\\
            window.location.href = newUrl;\\
        }\\
\\
        // 切换页码\\
        function changePage(direction) {\\
            // 检查当前是否在搜索或筛选模式\\
            const urlParams = new URLSearchParams(window.location.search);\\
            const hasFilters = urlParams.has(\"keyword\") || \\
                              urlParams.has(\"region\") || \\
                              urlParams.has(\"subject\") || \\
                              urlParams.has(\"stage\") || \\
                              urlParams.has(\"source_type\") || \\
                              urlParams.has(\"year\");\\
            \\
            // 获取当前页码\\
            let nextPage = parseInt(urlParams.get(\"page\") || \"1\") + direction;\\
            if (nextPage < 1) nextPage = 1;\\
            \\
            // 无论是否有筛选条件，都使用navigateWithFilters确保保留筛选参数\\
            navigateWithFilters(nextPage);\\
        }\\
\\
        // 跳转到指定页面\\
        function goToPage(pageNum) {\\
            // 直接使用navigateWithFilters函数确保保留所有筛选条件\\
            navigateWithFilters(pageNum);\\
        }' $REMOTE_DIR/templates/papers.html"

# 11. 重启服务
echo "重启服务器应用..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"

echo "修复完成！"
