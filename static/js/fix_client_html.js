/**
 * 客户端修复脚本 - 处理HTML实体和题目排序问题
 * 版本: 1.0.0
 * 日期: 2025-04-02
 */
(function() {
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('客户端修复脚本已加载');
        
        // 1. 修复HTML实体问题
        function fixHtmlEntities() {
            // 查找所有可能包含HTML实体的元素
            const textElements = document.querySelectorAll('.question-content, .question-text, .paper-content');
            
            textElements.forEach(element => {
                if (element && element.innerHTML) {
                    // 替换所有&middot;实体
                    element.innerHTML = element.innerHTML.replace(/&middot;/g, '');
                    
                    // 处理其他可能的HTML实体问题
                    element.innerHTML = element.innerHTML
                        .replace(/&amp;middot;/g, '')
                        .replace(/·/g, '');
                }
            });
            
            console.log('HTML实体修复完成');
        }
        
        // 2. 修复题目排序问题
        function fixQuestionOrder() {
            // 获取试卷生成区域
            const paperContainer = document.querySelector('#paper-container');
            if (!paperContainer) return;
            
            // 查找所有题目元素
            const questions = paperContainer.querySelectorAll('.question-item');
            if (!questions || questions.length === 0) return;
            
            // 将题目转换为数组以便排序
            const questionArray = Array.from(questions);
            
            // 排序函数
            questionArray.sort((a, b) => {
                // 1. 首先按照题目类型排序（选择题在前，主观题在后）
                const typeA = a.getAttribute('data-question-type') || '';
                const typeB = b.getAttribute('data-question-type') || '';
                
                // 获取题目类型的排序值（选择题为1，主观题为2，其他为3）
                const getTypeValue = (type) => {
                    const lowerType = type.toLowerCase();
                    if (lowerType.includes('choice') || lowerType.includes('select') || 
                        lowerType.includes('单选') || lowerType.includes('多选')) {
                        return 1;
                    } else if (lowerType.includes('subjective') || lowerType.includes('essay') || 
                              lowerType.includes('主观') || lowerType.includes('问答')) {
                        return 2;
                    }
                    return 3;
                };
                
                const typeValueA = getTypeValue(typeA);
                const typeValueB = getTypeValue(typeB);
                
                if (typeValueA !== typeValueB) {
                    return typeValueA - typeValueB;
                }
                
                // 2. 其次按照选择顺序排序（先选的在前，后选的在后）
                const orderA = parseInt(a.getAttribute('data-order') || '0');
                const orderB = parseInt(b.getAttribute('data-order') || '0');
                
                return orderA - orderB;
            });
            
            // 重新添加排序后的题目到容器中
            questionArray.forEach(question => {
                paperContainer.appendChild(question);
            });
            
            console.log('题目排序修复完成');
        }
        
        // 3. 修复下载PDF功能
        function fixPdfDownload() {
            // 查找下载按钮
            const downloadButtons = document.querySelectorAll('.download-btn, #downloadPdf');
            
            downloadButtons.forEach(button => {
                const originalClick = button.onclick;
                
                button.onclick = function(e) {
                    // 在下载前先修复HTML实体和排序问题
                    fixHtmlEntities();
                    fixQuestionOrder();
                    
                    console.log('下载前预处理完成');
                    
                    // 调用原始点击事件
                    if (typeof originalClick === 'function') {
                        return originalClick.call(this, e);
                    }
                };
            });
            
            console.log('PDF下载功能修复完成');
        }
        
        // 4. 监听动态添加的题目
        function setupMutationObserver() {
            // 创建一个MutationObserver实例
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        // 新元素添加时修复HTML实体
                        fixHtmlEntities();
                    }
                });
            });
            
            // 要观察的目标节点
            const targetNode = document.querySelector('#paper-container');
            if (targetNode) {
                // 观察器的配置
                const config = { childList: true, subtree: true };
                
                // 开始观察
                observer.observe(targetNode, config);
                console.log('变动观察器已设置');
            }
        }
        
        // 初始化修复
        fixHtmlEntities();
        fixQuestionOrder();
        fixPdfDownload();
        setupMutationObserver();
        
        // 每秒运行一次修复，确保动态加载的内容也被处理
        setInterval(function() {
            fixHtmlEntities();
        }, 1000);
        
        console.log('客户端修复脚本初始化完成');
    });
})(); 