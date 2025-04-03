/**
 * 客户端修复脚本 - 处理HTML实体、题目排序和A4格式排版
 * 版本: 1.2.0
 * 日期: 2025-04-04
 */
(function() {
    // 使用window.onload确保在所有资源加载完成后执行
    window.onload = function() {
        console.log('客户端修复脚本已加载 版本 1.2.0');
        
        // 1. 修复HTML实体问题
        function fixHtmlEntities() {
            // 查找所有可能包含HTML实体的元素
            const textElements = document.querySelectorAll('.question-content, .question-text, .paper-content, .question-stem, .option-text, .answer-content, .explanation');
            
            if (textElements && textElements.length > 0) {
                textElements.forEach(element => {
                    if (element && element.innerHTML) {
                        // 替换所有HTML实体
                        element.innerHTML = element.innerHTML
                            // 中点
                            .replace(/&middot;/g, '')
                            .replace(/&amp;middot;/g, '')
                            .replace(/·/g, '')
                            // 引号 - 完全删除
                            .replace(/&ldquo;/g, '')
                            .replace(/&rdquo;/g, '')
                            .replace(/&lsquo;/g, '')
                            .replace(/&rsquo;/g, '')
                            // 箭头 - 完全删除
                            .replace(/&rarr;/g, '')
                            .replace(/&#8594;/g, '')
                            .replace(/&#x2192;/g, '')
                            .replace(/→/g, '')
                            // 其他常见实体
                            .replace(/&nbsp;/g, ' ')
                            .replace(/&hellip;/g, '...')
                            .replace(/&mdash;/g, '—')
                            .replace(/&bull;/g, '')
                            .replace(/&amp;/g, '&')
                            .replace(/&lt;/g, '<')
                            .replace(/&gt;/g, '>')
                            // 捕获所有剩余的HTML实体
                            .replace(/&[a-zA-Z0-9#]+;/g, '');
                        
                        // 去除题号（如：11. 或 11．）
                        element.innerHTML = element.innerHTML.replace(/^\d+[\.．]\s*/gm, '');
                    }
                });
                
                console.log('HTML实体修复完成 - 已删除所有引号实体');
            }
        }
        
        // 2. 修复题目排序问题
        function fixQuestionOrder() {
            // 获取试卷生成区域
            const paperContainer = document.querySelector('#paper-container');
            if (!paperContainer) {
                console.log('未找到试卷容器');
                return;
            }
            
            // 查找所有题目元素
            const questions = paperContainer.querySelectorAll('.question-item');
            if (!questions || questions.length === 0) {
                console.log('未找到题目元素');
                return;
            }
            
            console.log(`找到 ${questions.length} 个题目元素，准备排序`);
            
            // 将题目转换为数组以便排序
            const questionArray = Array.from(questions);
            
            // 分类函数：判断是否为选择题
            function isChoiceQuestion(question) {
                // 1. 检查题目类型属性
                const questionType = question.getAttribute('data-question-type') || '';
                const questionTypeText = questionType.toLowerCase();
                const isChoiceByType = questionTypeText.includes('choice') || 
                                      questionTypeText.includes('select') || 
                                      questionTypeText.includes('单选') || 
                                      questionTypeText.includes('多选');
                if (isChoiceByType) return true;
                
                // 2. 检查题目内容是否含有选项标记(A. B. C. D.)
                const questionContent = question.innerHTML || '';
                const hasOptionMarkers = /[A-D][.．]\s*\w+/.test(questionContent);
                
                // 3. 检查是否有选项元素
                const hasOptions = question.querySelectorAll('.option').length > 0 || 
                                  question.querySelectorAll('.combined-option').length > 0;
                
                return isChoiceByType || hasOptionMarkers || hasOptions;
            }
            
            // 分类所有题目为选择题和非选择题两组
            const choiceQuestions = [];
            const nonChoiceQuestions = [];
            
            questionArray.forEach(question => {
                if (isChoiceQuestion(question)) {
                    choiceQuestions.push(question);
                } else {
                    nonChoiceQuestions.push(question);
                }
            });
            
            console.log(`分类结果: ${choiceQuestions.length} 个选择题, ${nonChoiceQuestions.length} 个非选择题`);
            
            // 在每个分组内部按照选择顺序排序（先选的在前，后选的在后）
            function sortBySelectionOrder(questions) {
                return questions.sort((a, b) => {
                    // 获取题目的选择顺序
                    const orderA = parseInt(a.getAttribute('data-order') || '0');
                    const orderB = parseInt(b.getAttribute('data-order') || '0');
                    
                    // 如果顺序为0（未设置），则保持原始顺序
                    if (orderA === 0 && orderB === 0) {
                        // 使用DOM顺序作为备用
                        const indexA = questionArray.indexOf(a);
                        const indexB = questionArray.indexOf(b);
                        return indexA - indexB;
                    }
                    
                    // 如果只有一个顺序为0，则有设置顺序的排在前面
                    if (orderA === 0) return 1;
                    if (orderB === 0) return -1;
                    
                    // 正常比较顺序
                    return orderA - orderB;
                });
            }
            
            // 对两个分组分别按选择顺序排序
            const sortedChoiceQuestions = sortBySelectionOrder(choiceQuestions);
            const sortedNonChoiceQuestions = sortBySelectionOrder(nonChoiceQuestions);
            
            // 合并两个分组，选择题排在前面
            const sortedQuestions = [...sortedChoiceQuestions, ...sortedNonChoiceQuestions];
            
            // 清空原容器并按排序后的顺序添加题目
            while (paperContainer.firstChild) {
                paperContainer.removeChild(paperContainer.firstChild);
            }
            
            sortedQuestions.forEach(question => {
                paperContainer.appendChild(question);
            });
            
            console.log('题目排序修复完成');
        }
        
        // 3. 修复下载PDF功能
        function fixPdfDownload() {
            // 查找下载按钮
            const downloadButtons = document.querySelectorAll('.download-btn, #downloadPdf');
            
            if (downloadButtons && downloadButtons.length > 0) {
                downloadButtons.forEach(button => {
                    if (button) {
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
                    }
                });
                
                console.log('PDF下载功能修复完成');
            }
        }
        
        // 4. 增强提交试卷功能，确保生成前正确排序
        function enhanceGeneratePaper() {
            if (typeof window.generatePaper === 'function') {
                const originalGeneratePaper = window.generatePaper;
                
                window.generatePaper = function() {
                    // 在生成试卷前确保题目排序正确
                    fixHtmlEntities();
                    fixQuestionOrder();
                    
                    // 添加生成文档的类，修改呈现样式
                    document.body.classList.add('generating-paper');
                    updatePageStyles();
                    
                    console.log('试卷生成前预处理完成');
                    
                    // 使用延时从而在生成前看到好的排版
                    setTimeout(function() {
                        // 调用原始生成函数
                        const result = originalGeneratePaper.apply(this, arguments);
                        
                        // 在生成后恢复样式
                        setTimeout(function() {
                            document.body.classList.remove('generating-paper');
                        }, 1000);
                        
                        return result;
                    }, 500);
                };
                
                console.log('试卷生成功能增强完成');
            }
        }
        
        // 7. 更新页面样式为A4排版格式
        function updatePageStyles() {
            // 创建样式元素
            const styleElement = document.createElement('style');
            styleElement.type = 'text/css';
            styleElement.id = 'a4-paper-styles';
            
            // A4纸张样式和字体设置
            const styles = `
                /* 页面设置 - A4纸张 */
                #paper-container {
                    width: 210mm;
                    /* 页面大小修正 */
                    margin: 0 auto;
                    padding: 25.4mm;
                    background-color: white;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
                
                /* 标题样式：宋体，15磅，加粗，居中 */
                #paper-container h1 {
                    font-family: 宋体, SimSun, sans-serif;
                    font-size: 15pt;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 20px;
                }
                
                /* 章节标题（如“一、单选题”）：宋体，10.5磅，加粗，左对齐 */
                #paper-container .section-title {
                    font-family: 宋体, SimSun, sans-serif;
                    font-size: 10.5pt;
                    font-weight: bold;
                    text-align: left;
                    margin-top: 15px;
                    margin-bottom: 10px;
                }
                
                /* 题目内容：宋体，10.5磅，左对齐 */
                #paper-container .question-item,
                #paper-container .question-text,
                #paper-container .question-stem {
                    font-family: 宋体, SimSun, sans-serif;
                    font-size: 10.5pt;
                    text-align: left;
                    line-height: 1.5;
                    margin-bottom: 5px;
                }
                
                /* 选项内容：与题目内容相同的字体和字号 */
                #paper-container .option-text,
                #paper-container .option {
                    font-family: 宋体, SimSun, sans-serif;
                    font-size: 10.5pt;
                    line-height: 1.5;
                }
                
                /* 当生成文档时修改选择器 */
                body.generating-paper {
                    background-color: white;
                }
                
                body.generating-paper .filter-sidebar,
                body.generating-paper .header,
                body.generating-paper #downloadPanel,
                body.generating-paper .pagination-controls {
                    display: none !important;
                }
                
                body.generating-paper .main-container {
                    padding: 0;
                    margin: 0;
                    width: 210mm;
                    max-width: 210mm;
                }
                
                body.generating-paper .content-area {
                    width: 100%;
                    padding: 0;
                }
                
                body.generating-paper #paper-container {
                    box-shadow: none;
                }
            `;
            
            styleElement.textContent = styles;
            document.head.appendChild(styleElement);
            
            // 检查是否需要添加章节标题
            const paperContainer = document.getElementById('paper-container');
            if (paperContainer) {
                // 找出所有题型
                const questionTypes = {};
                const questionItems = paperContainer.querySelectorAll('.question-item');
                
                questionItems.forEach(item => {
                    const type = item.getAttribute('data-question-type') || '未分类';
                    if (!questionTypes[type]) {
                        questionTypes[type] = [];
                    }
                    questionTypes[type].push(item);
                });
                
                // 如果找到了题目并且有至少一种题型，添加章节标题
                if (Object.keys(questionTypes).length > 0) {
                    const chineseNumbers = {
                        1: '一',
                        2: '二',
                        3: '三',
                        4: '四',
                        5: '五',
                        6: '六',
                        7: '七',
                        8: '八',
                        9: '九',
                        10: '十'
                    };
                    
                    // 定义题型顺序
                    const typeOrder = [
                        '单选题', '多选题', '判断题', '填空题', '解答题', 
                        '主观题', '计算题', '论述题', '作文',
                        '诗词鉴赏', '文言文阅读', '现代文阅读',
                        '未分类'
                    ];
                    
                    // 排序题型
                    const orderedTypes = [];
                    typeOrder.forEach(type => {
                        if (questionTypes[type]) {
                            orderedTypes.push(type);
                        }
                    });
                    
                    // 添加没有在预定义顺序中的题型
                    Object.keys(questionTypes).forEach(type => {
                        if (!orderedTypes.includes(type)) {
                            orderedTypes.push(type);
                        }
                    });
                    
                    console.log('检测到题型：', orderedTypes);
                    
                    // 为每个题型添加标题
                    orderedTypes.forEach((type, index) => {
                        const sectionTitle = document.createElement('div');
                        sectionTitle.className = 'section-title';
                        sectionTitle.textContent = `${chineseNumbers[index+1] || (index+1)}、${type}`;
                        
                        // 找到该题型的第一道题
                        const firstQuestion = questionTypes[type][0];
                        firstQuestion.parentNode.insertBefore(sectionTitle, firstQuestion);
                    });
                }
            }
            
            console.log('A4纸张样式已应用');
        }
        
        // 5. 监听动态添加的题目
        function setupMutationObserver() {
            // 创建一个MutationObserver实例
            if (typeof MutationObserver !== 'undefined') {
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                            // 新元素添加时修复HTML实体并重排题目
                            fixHtmlEntities();
                            fixQuestionOrder();
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
        }
        
        // 6. 增强题目选择功能，记录选择顺序
        function enhanceQuestionSelection() {
            if (typeof window.toggleSelect === 'function') {
                const originalToggleSelect = window.toggleSelect;
                let selectionOrder = 1; // 初始选择顺序计数器
                
                window.toggleSelect = function(questionId) {
                    // 调用原始函数
                    const result = originalToggleSelect.apply(this, arguments);
                    
                    // 找到相关题目元素
                    const questionItems = document.querySelectorAll(`.question-item[data-question-id="${questionId}"]`);
                    
                    if (questionItems.length > 0) {
                        questionItems.forEach(item => {
                            // 判断题目是否被选中
                            const isSelected = item.querySelector('.select-btn.selected') !== null;
                            
                            if (isSelected) {
                                // 如果是新选择的题目，设置选择顺序
                                if (!item.hasAttribute('data-order')) {
                                    item.setAttribute('data-order', selectionOrder++);
                                    console.log(`题目 ${questionId} 设置选择顺序: ${selectionOrder-1}`);
                                }
                            } else {
                                // 如果取消选择，移除选择顺序
                                item.removeAttribute('data-order');
                                console.log(`题目 ${questionId} 移除选择顺序`);
                            }
                        });
                    }
                    
                    return result;
                };
                
                console.log('题目选择功能增强完成');
            }
        }
        
        // 初始化修复
        setTimeout(function() {
            try {
                fixHtmlEntities();
                enhanceQuestionSelection(); // 先增强选择功能，记录选择顺序
                fixQuestionOrder();         // 然后执行排序
                fixPdfDownload();
                enhanceGeneratePaper();     // 增强试卷生成功能
                setupMutationObserver();
                updatePageStyles();         // 应用A4纸张样式
                
                // 每隔5秒检查一次，确保动态加载的内容也被处理
                setInterval(function() {
                    fixHtmlEntities();
                }, 5000);
                
                console.log('客户端修复脚本初始化完成，版本1.2.0');
            } catch (error) {
                console.error('客户端修复脚本出错:', error);
            }
        }, 1000); // 延长延时，确保页面完全加载
    };
})();
