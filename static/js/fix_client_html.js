/**
 * 客户端修复脚本 - 处理HTML实体和题目排序问题
 * 版本: 1.0.2
 * 日期: 2025-04-02
 */
(function() {
    // 使用匿名自执行函数，避免污染全局命名空间
    
    // 检查当前页面是否为客户端页面
    function isClientPage() {
        try {
            return !!(
                document.querySelector('#paper-container') || 
                document.querySelector('.question-item') || 
                document.querySelector('.download-btn') || 
                document.querySelector('#downloadPdf')
            );
        } catch (e) {
            console.error('检查页面类型时出错:', e);
            return false;
        }
    }
    
    // 1. 修复HTML实体问题
    function fixHtmlEntities() {
        try {
            // 查找所有可能包含HTML实体的元素
            const textElements = document.querySelectorAll('.question-content, .question-text, .paper-content');
            
            if (!textElements || textElements.length === 0) {
                return; // 静默失败，不输出任何日志
            }
            
            textElements.forEach(element => {
                if (element && element.innerHTML) {
                    // 替换所有&middot;实体
                    element.innerHTML = element.innerHTML.replace(/&middot;/g, '')
                        .replace(/&amp;middot;/g, '')
                        .replace(/·/g, '');
                }
            });
        } catch (error) {
            // 静默失败，不输出任何日志
        }
    }
    
    // 2. 修复题目排序问题
    function fixQuestionOrder() {
        try {
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
        } catch (error) {
            // 静默失败，不输出任何日志
        }
    }
    
    // 3. 修复下载PDF功能
    function fixPdfDownload() {
        try {
            // 查找下载按钮
            const downloadButtons = document.querySelectorAll('.download-btn, #downloadPdf');
            
            if (!downloadButtons || downloadButtons.length === 0) return;
            
            downloadButtons.forEach(button => {
                if (!button) return;
                
                const originalClick = button.onclick;
                
                button.onclick = function(e) {
                    // 在下载前先修复HTML实体和排序问题
                    fixHtmlEntities();
                    fixQuestionOrder();
                    
                    // 调用原始点击事件
                    if (typeof originalClick === 'function') {
                        return originalClick.call(this, e);
                    }
                };
            });
        } catch (error) {
            // 静默失败，不输出任何日志
        }
    }
    
    // 4. 监听动态添加的题目
    function setupMutationObserver() {
        try {
            // 要观察的目标节点
            const targetNode = document.querySelector('#paper-container');
            if (!targetNode) return;
            
            // 创建一个MutationObserver实例
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        // 新元素添加时修复HTML实体
                        fixHtmlEntities();
                    }
                });
            });
            
            // 观察器的配置
            const config = { childList: true, subtree: true };
            
            // 开始观察
            observer.observe(targetNode, config);
        } catch (error) {
            // 静默失败，不输出任何日志
        }
    }
    
    // 初始化函数 - 会在页面加载后自动执行
    function initFixes() {
        // 只在客户端页面上执行修复
        if (isClientPage()) {
            fixHtmlEntities();
            fixQuestionOrder();
            fixPdfDownload();
            setupMutationObserver();
            
            // 每秒运行一次修复，确保动态加载的内容也被处理
            setInterval(fixHtmlEntities, 1000);
        }
    }
    
    // 以更安全的方式初始化
    if (document.readyState === 'loading') {
        window.addEventListener('load', initFixes);
    } else {
        initFixes();
    }
})(); 