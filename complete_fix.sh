#!/bin/bash

# 完整修复脚本 - 同时修复本地和服务器上的问题
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 本地路径
LOCAL_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"

echo "===== 开始修复本地和服务器上的问题 ====="

# ===== 第1步：恢复原始文件 =====
echo "1. 恢复原始文件..."

# 恢复服务器上的client.html
echo "   恢复服务器上的client.html..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cp $REMOTE_DIR/templates/client.html.bak_20250402134551 $REMOTE_DIR/templates/client.html"

# 恢复服务器上的app.py
echo "   恢复服务器上的app.py..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "if [ -f $REMOTE_DIR/app.py.bak ]; then cp $REMOTE_DIR/app.py.bak $REMOTE_DIR/app.py; fi"

# ===== 第2步：创建简单的localStorage修复 =====
echo "2. 创建localStorage修复..."

# 创建localStorage修复脚本
cat > $LOCAL_DIR/localStorage_fix.js << 'EOF'
// 简单的localStorage修复
(function() {
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('localStorage修复脚本已加载');
        
        // 确保selectedQuestions已定义
        if (typeof window.selectedQuestions === 'undefined') {
            window.selectedQuestions = new Set();
            console.log('创建了selectedQuestions集合');
        }
        
        // 从localStorage恢复已选题目
        try {
            const savedQuestions = localStorage.getItem('selectedQuestions');
            if (savedQuestions) {
                const questionIds = JSON.parse(savedQuestions);
                questionIds.forEach(id => window.selectedQuestions.add(parseInt(id)));
                console.log('从localStorage恢复已选题目:', window.selectedQuestions.size);
                
                // 更新UI
                if (typeof window.updateDownloadPanel === 'function') {
                    window.updateDownloadPanel();
                }
            }
        } catch (error) {
            console.error('恢复已选题目出错:', error);
        }
        
        // 保存已选题目到localStorage的函数
        window.saveSelectedQuestions = function() {
            try {
                const questionIds = Array.from(window.selectedQuestions);
                localStorage.setItem('selectedQuestions', JSON.stringify(questionIds));
                console.log('保存题目到localStorage:', questionIds.length);
            } catch (error) {
                console.error('保存已选题目出错:', error);
            }
        };
        
        // 拦截toggleSelect函数
        if (typeof window.toggleSelect === 'function') {
            const originalToggleSelect = window.toggleSelect;
            window.toggleSelect = function(questionId) {
                // 调用原始函数
                originalToggleSelect(questionId);
                // 保存到localStorage
                window.saveSelectedQuestions();
            };
            console.log('已增强toggleSelect函数');
        }
        
        // 拦截clearSelectedQuestions函数
        if (typeof window.clearSelectedQuestions === 'function') {
            const originalClearSelectedQuestions = window.clearSelectedQuestions;
            window.clearSelectedQuestions = function() {
                // 调用原始函数
                originalClearSelectedQuestions();
                // 从localStorage中清除
                localStorage.removeItem('selectedQuestions');
                console.log('已清除localStorage中的selectedQuestions');
            };
            console.log('已增强clearSelectedQuestions函数');
        }
        
        // 拦截generatePaper函数
        if (typeof window.generatePaper === 'function') {
            const originalGeneratePaper = window.generatePaper;
            window.generatePaper = function() {
                // 调用原始函数
                originalGeneratePaper();
                // 从localStorage中清除
                localStorage.removeItem('selectedQuestions');
                console.log('生成试卷后已清除localStorage中的selectedQuestions');
            };
            console.log('已增强generatePaper函数');
        }
        
        // 为所有选择按钮添加点击事件
        setTimeout(function() {
            const selectButtons = document.querySelectorAll('.select-btn');
            selectButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    // 保存到localStorage
                    setTimeout(window.saveSelectedQuestions, 100);
                });
            });
            console.log('已为', selectButtons.length, '个选择按钮添加点击事件');
        }, 1000);
    });
})();
EOF

# 创建分页修复脚本
cat > $LOCAL_DIR/pagination_fix.js << 'EOF'
// 简单的分页修复
(function() {
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('分页修复脚本已加载');
        
        // 拦截所有分页链接的点击事件
        function setupPaginationLinks() {
            // 查找所有分页链接
            const paginationLinks = document.querySelectorAll('.pagination-button, #prevPage, #nextPage');
            
            paginationLinks.forEach(link => {
                // 移除现有的点击事件
                const newLink = link.cloneNode(true);
                if (link.parentNode) {
                    link.parentNode.replaceChild(newLink, link);
                }
                
                // 添加新的点击事件
                newLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // 获取页码
                    let pageNum = 1;
                    if (this.id === 'prevPage') {
                        const currentPage = parseInt(new URLSearchParams(window.location.search).get('page') || '1');
                        pageNum = Math.max(1, currentPage - 1);
                    } else if (this.id === 'nextPage') {
                        const currentPage = parseInt(new URLSearchParams(window.location.search).get('page') || '1');
                        pageNum = currentPage + 1;
                    } else {
                        pageNum = parseInt(this.getAttribute('data-page') || '1');
                    }
                    
                    // 构建新URL，保留所有筛选参数
                    const urlParams = new URLSearchParams(window.location.search);
                    urlParams.set('page', pageNum);
                    
                    // 获取所有筛选标签
                    const filterTags = document.querySelectorAll('.filter-tag');
                    filterTags.forEach(tag => {
                        const filterType = tag.getAttribute('data-type');
                        const filterValue = tag.getAttribute('data-value');
                        if (filterType && filterValue) {
                            urlParams.set(filterType, filterValue);
                        }
                    });
                    
                    // 跳转到新URL
                    const newUrl = `/papers?${urlParams.toString()}`;
                    console.log('跳转到:', newUrl);
                    window.location.href = newUrl;
                });
            });
            
            console.log('已设置', paginationLinks.length, '个分页链接');
        }
        
        // 初始设置
        setupPaginationLinks();
        
        // 每秒检查一次，确保动态加载的分页链接也被处理
        setInterval(setupPaginationLinks, 1000);
    });
})();
EOF

# ===== 第3步：上传修复脚本到服务器 =====
echo "3. 上传修复脚本到服务器..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $LOCAL_DIR/localStorage_fix.js $USER@$SERVER:$REMOTE_DIR/
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $LOCAL_DIR/pagination_fix.js $USER@$SERVER:$REMOTE_DIR/

# ===== 第4步：修复app.py中的HTML实体和题目顺序问题 =====
echo "4. 修复app.py中的HTML实体和题目顺序问题..."

# 创建app.py修复脚本
cat > $LOCAL_DIR/fix_app_py.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复app.py中的HTML实体和题目顺序问题
"""

import os
import re
import sys

def fix_html_entities(content):
    """修复HTML实体编码处理"""
    # 查找clean_and_split_question函数中的HTML实体替换部分
    pattern = r'(# 1\) 去除常见HTML实体和多余空格换行\n\s+replacements = \{[^}]+\})'
    
    # 检查是否找到匹配
    match = re.search(pattern, content)
    if not match:
        print("无法找到HTML实体替换代码段")
        return content
    
    # 原始代码段
    original_code = match.group(1)
    
    # 添加&middot;的处理
    if "&middot;" not in original_code:
        new_code = original_code.replace(
            '"&mdash;": "—"',
            '"&mdash;": "—",\n        "&middot;": "·"'
        )
        
        # 替换代码
        content = content.replace(original_code, new_code)
        print("已添加&middot;实体处理")
    else:
        print("&middot;实体处理已存在")
    
    return content

def fix_question_order(content):
    """修复题目顺序问题"""
    # 查找generate_paper函数中的题目查询部分
    pattern = r'(question_ids = request\.json\.get\(\'question_ids\', \[\]\).*?\n.*?questions = SU\.query\.filter\(SU\.id\.in_\(question_ids\)\)\.all\(\))'
    
    # 检查是否找到匹配
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print("无法找到题目查询代码段")
        return content
    
    # 原始代码段
    original_code = match.group(1)
    
    # 检查是否已经修复
    if "question_map" in original_code:
        print("题目顺序问题已修复")
        return content
    
    # 新代码：保持原始顺序
    new_code = """question_ids = request.json.get('question_ids', [])
        paper_title = request.json.get('paper_title', '试卷')
        
        # 查询所有题目
        all_questions = SU.query.filter(SU.id.in_(question_ids)).all()
        
        # 创建ID到题目的映射
        question_map = {q.id: q for q in all_questions}
        
        # 按照原始顺序排列题目
        questions = [question_map[qid] for qid in question_ids if qid in question_map]"""
    
    # 替换代码
    content = content.replace(original_code, new_code)
    print("已修复题目顺序问题")
    
    return content

def main():
    """主函数"""
    # 获取app.py路径
    app_path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
    
    # 检查文件是否存在
    if not os.path.exists(app_path):
        print(f"错误: 找不到文件 {app_path}")
        sys.exit(1)
    
    # 创建备份
    backup_path = f"{app_path}.bak"
    try:
        with open(app_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"已创建备份: {backup_path}")
    except Exception as e:
        print(f"创建备份失败: {e}")
        sys.exit(1)
    
    # 修复HTML实体编码
    content = fix_html_entities(content)
    
    # 修复题目顺序
    content = fix_question_order(content)
    
    # 写回文件
    try:
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"修复完成，已更新 {app_path}")
    except Exception as e:
        print(f"写入文件失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# 修复本地app.py
echo "   修复本地app.py..."
python3 $LOCAL_DIR/fix_app_py.py $LOCAL_DIR/app.py

# 上传修复脚本到服务器并执行
echo "   修复服务器app.py..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $LOCAL_DIR/fix_app_py.py $USER@$SERVER:$REMOTE_DIR/
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_DIR && python3 fix_app_py.py app.py"

# ===== 第5步：将修复脚本注入到HTML文件中 =====
echo "5. 将修复脚本注入到HTML文件中..."

# 创建注入脚本
cat > $LOCAL_DIR/inject_fixes.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将修复脚本注入到HTML文件中
"""

import os
import sys

def inject_script(html_path, script_path, script_type):
    """将脚本注入到HTML文件中"""
    try:
        # 读取HTML文件
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 读取脚本文件
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 创建脚本标签
        script_tag = f'<script>\n// {script_type}修复脚本\n{script_content}\n</script>'
        
        # 检查脚本是否已存在
        if script_content[:20] in html_content:
            print(f"{script_type}脚本已存在于{html_path}")
            return html_content
        
        # 在</body>前插入脚本
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{script_tag}\n</body>')
            print(f"已将{script_type}脚本注入到{html_path}")
        else:
            # 如果没有</body>标签，则在文件末尾添加
            html_content += f'\n{script_tag}\n'
            print(f"已将{script_type}脚本添加到{html_path}末尾")
        
        # 写回文件
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_content
    except Exception as e:
        print(f"注入{script_type}脚本到{html_path}失败: {e}")
        return None

def main():
    """主函数"""
    if len(sys.argv) < 4:
        print("用法: python3 inject_fixes.py <html_path> <localStorage_script_path> <pagination_script_path>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    localStorage_script_path = sys.argv[2]
    pagination_script_path = sys.argv[3]
    
    # 检查文件是否存在
    for path in [html_path, localStorage_script_path, pagination_script_path]:
        if not os.path.exists(path):
            print(f"错误: 找不到文件 {path}")
            sys.exit(1)
    
    # 创建备份
    backup_path = f"{html_path}.bak"
    try:
        with open(html_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"已创建备份: {backup_path}")
    except Exception as e:
        print(f"创建备份失败: {e}")
        sys.exit(1)
    
    # 确定HTML文件类型
    filename = os.path.basename(html_path)
    if filename == 'client.html':
        # 只注入localStorage修复
        inject_script(html_path, localStorage_script_path, 'localStorage')
    elif filename == 'papers.html':
        # 只注入分页修复
        inject_script(html_path, pagination_script_path, '分页')
    else:
        print(f"未知的HTML文件类型: {filename}")

if __name__ == "__main__":
    main()
EOF

# 注入修复脚本到本地HTML文件
echo "   注入修复脚本到本地HTML文件..."
python3 $LOCAL_DIR/inject_fixes.py $LOCAL_DIR/templates/client.html $LOCAL_DIR/localStorage_fix.js $LOCAL_DIR/pagination_fix.js
python3 $LOCAL_DIR/inject_fixes.py $LOCAL_DIR/templates/papers.html $LOCAL_DIR/localStorage_fix.js $LOCAL_DIR/pagination_fix.js

# 上传注入脚本到服务器并执行
echo "   注入修复脚本到服务器HTML文件..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $LOCAL_DIR/inject_fixes.py $USER@$SERVER:$REMOTE_DIR/
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_DIR && python3 inject_fixes.py $REMOTE_DIR/templates/client.html $REMOTE_DIR/localStorage_fix.js $REMOTE_DIR/pagination_fix.js"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_DIR && python3 inject_fixes.py $REMOTE_DIR/templates/papers.html $REMOTE_DIR/localStorage_fix.js $REMOTE_DIR/pagination_fix.js"

# ===== 第6步：重启服务 =====
echo "6. 重启服务..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"

# ===== 第7步：检查服务状态 =====
echo "7. 检查服务状态..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl status zujuanwang.service | head -n 20"

echo "===== 修复完成 ====="
echo "请访问网站检查是否已修复问题。"
