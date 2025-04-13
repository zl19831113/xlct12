/**
 * 客户端页面修复脚本 - 解决重复函数定义和其他问题
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log("客户端修复脚本加载完成，准备处理各种冲突...");
    
    // 确保allQuestions始终存在，防止脚本错误
    if (!window.allQuestions) {
        window.allQuestions = [];
        console.log("初始化空的全局allQuestions数组");
    }
    
    // 提供一个测试数据初始化函数，确保有一些示例数据可用
    window.initializeTestData = function() {
        if (!window.allQuestions || window.allQuestions.length === 0) {
            console.log("提供测试数据...");
            window.allQuestions = [
                {
                    id: 1,
                    subject: '英语',
                    questionType: '阅读理解',
                    educationStage: '初中',
                    chapter: '八年级上册',
                    unit: 'Unit 1',
                    lesson: 'Reading',
                    question: 'Sample English reading comprehension question',
                    answer: 'Sample answer for reading question'
                },
                {
                    id: 2,
                    subject: '英语',
                    questionType: '完形填空',
                    educationStage: '初中',
                    chapter: '八年级上册',
                    unit: 'Unit 2',
                    lesson: 'Grammar',
                    question: 'Sample English cloze test question',
                    answer: 'Sample answer for cloze test'
                },
                {
                    id: 3,
                    subject: '英语',
                    questionType: '语法填空',
                    educationStage: '初中',
                    chapter: '八年级上册',
                    unit: 'Unit 3',
                    lesson: 'Writing',
                    question: 'Sample English grammar question',
                    answer: 'Sample answer for grammar question'
                }
            ];
            console.log(`初始化了 ${window.allQuestions.length} 个测试题目`);
            
            // 触发渲染
            if (typeof window.renderQuestions === 'function') {
                window.renderQuestions(window.allQuestions);
            }
            
            // 触发筛选器更新
            try {
                if (typeof window.updateFilters === 'function') {
                    window.updateFilters();
                }
            } catch (error) {
                console.error('更新筛选器失败:', error);
            }
        }
    };

    // 安全获取元素值的辅助函数
    function safeGetElementValue(id) {
        const element = document.getElementById(id);
        return element ? element.value : '';
    }

    // 安全设置元素文本内容的辅助函数
    function safeSetElementText(id, text) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
        }
    }

    // 安全设置元素样式的辅助函数
    function safeSetElementStyle(id, property, value) {
        const element = document.getElementById(id);
        if (element) {
            element.style[property] = value;
        }
    }

    // 创建一个新的函数来检查预期的DOM元素是否存在
    function verifyRequiredElements() {
        const requiredElements = [
            {id: 'subject', type: 'select', placeholder: '选择科目'},
            {id: 'questionType', type: 'select', placeholder: '选择题型'},
            {id: 'educationStage', type: 'select', placeholder: '选择学段'},
            {id: 'chapter', type: 'select', placeholder: '选择章节'},
            {id: 'unit', type: 'select', placeholder: '选择单元'},
            {id: 'lesson', type: 'select', placeholder: '选择课程'},
            {id: 'searchBox', type: 'input', placeholder: '搜索题目'},
            {id: 'questionCount', type: 'div', placeholder: '题目数量'},
            {id: 'noQuestions', type: 'div', placeholder: '无题目提示'},
            {id: 'questionCards', type: 'div', placeholder: '题目卡片容器'}
        ];
        
        let missingElements = [];
        
        requiredElements.forEach(element => {
            if (!document.getElementById(element.id)) {
                missingElements.push(element);
                createMissingElement(element);
            }
        });
        
        if (missingElements.length > 0) {
            console.warn('已创建以下缺失元素：', missingElements.map(e => e.id));
        }
        
        return missingElements.length === 0;
    }
    
    // 创建缺失的元素
    function createMissingElement(elementDef) {
        let element;
        
        switch(elementDef.type) {
            case 'input':
                element = document.createElement('input');
                element.type = 'text';
                element.placeholder = elementDef.placeholder;
                element.style.display = 'none'; // 隐藏元素
                break;
                
            case 'select':
                element = document.createElement('select');
                const option = document.createElement('option');
                option.value = '';
                option.textContent = elementDef.placeholder;
                element.appendChild(option);
                element.style.display = 'none'; // 隐藏元素
                break;
                
            case 'div':
            default:
                element = document.createElement('div');
                element.style.display = 'none'; // 隐藏元素
                break;
        }
        
        element.id = elementDef.id;
        document.body.appendChild(element);
        console.log(`创建了缺失的${elementDef.id}元素`);
    }

    // 验证所需元素并创建缺失的元素
    verifyRequiredElements();

    // 在页面顶部添加题目计数器
    if (document.getElementById('questionCount') && document.getElementById('questionCount').style.display === 'none') {
        // 删除显示计数器的代码，避免显示"共找到0道题目"
        /*
        const contentArea = document.querySelector('.content-area');
        if (contentArea) {
            const countDiv = document.getElementById('questionCount');
            countDiv.style.display = 'block';
            countDiv.style.padding = '10px';
            countDiv.style.margin = '10px 0';
            countDiv.style.backgroundColor = '#f5f7fa';
            countDiv.style.borderRadius = '5px';
            countDiv.style.fontWeight = 'bold';
            countDiv.textContent = '共找到 0 道题目';
            
            // 将计数器插入到内容区域的开始位置
            const firstChild = contentArea.firstChild;
            contentArea.insertBefore(countDiv, firstChild);
        }
        */
    }

    // 修复科目选择器
    function fixSubjectSelector() {
        const subjectSelect = document.getElementById('subject');
        if (subjectSelect) {
            // 确保科目选择器有初始的选项
            if (subjectSelect.options.length <= 1) {
                console.log("修复科目选择器...");
                const subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理'];
                
                // 保留第一个选项（通常是提示文本）
                const firstOption = subjectSelect.options[0] || document.createElement('option');
                if (!firstOption.value) {
                    firstOption.value = '';
                    firstOption.textContent = '选择科目';
                }
                
                subjectSelect.innerHTML = '';
                subjectSelect.appendChild(firstOption);
                
                subjects.forEach(subject => {
                    const option = document.createElement('option');
                    option.value = subject;
                    option.textContent = subject;
                    subjectSelect.appendChild(option);
                });
            }
            
            // 确保科目变更时能触发题型更新和筛选
            if (!subjectSelect._hasFixedOnChange) {
                const oldOnChange = subjectSelect.onchange;
                subjectSelect.onchange = function(event) {
                    console.log(`科目变更为: ${this.value}`);
                    
                    // 更新题型选择器
                    if (typeof window.updateQuestionTypes === 'function') {
                        window.updateQuestionTypes();
                    }
                    
                    // 初始化章节选择器
                    setTimeout(() => {
                        initializeChapterData();
                    }, 100);
                    
                    // 应用筛选
                    setTimeout(() => {
                        if (typeof window.filterQuestions === 'function') {
                            window.filterQuestions();
                        }
                    }, 200);
                    
                    // 调用原有的事件处理函数（如果存在）
                    if (typeof oldOnChange === 'function') {
                        oldOnChange.call(this, event);
                    }
                };
                subjectSelect._hasFixedOnChange = true;
            }
        }
    }

    // 修复学段选择器
    function fixEducationStageSelector() {
        const educationStageSelect = document.getElementById('educationStage');
        if (educationStageSelect) {
            // 确保学段选择器有初始的选项
            if (educationStageSelect.options.length <= 1) {
                console.log("修复学段选择器...");
                const stages = ['小学', '初中', '高中'];
                
                // 保留第一个选项（通常是提示文本）
                const firstOption = educationStageSelect.options[0] || document.createElement('option');
                if (!firstOption.value) {
                    firstOption.value = '';
                    firstOption.textContent = '选择学段';
                }
                
                educationStageSelect.innerHTML = '';
                educationStageSelect.appendChild(firstOption);
                
                stages.forEach(stage => {
                    const option = document.createElement('option');
                    option.value = stage;
                    option.textContent = stage;
                    educationStageSelect.appendChild(option);
                });
            }
            
            // 确保学段变更时能触发筛选
            if (!educationStageSelect._hasFixedOnChange) {
                const oldOnChange = educationStageSelect.onchange;
                educationStageSelect.onchange = function(event) {
                    console.log(`学段变更为: ${this.value}`);
                    
                    // 应用筛选
                    setTimeout(() => {
                        if (typeof window.filterQuestions === 'function') {
                            window.filterQuestions();
                        }
                    }, 200);
                    
                    // 调用原有的事件处理函数（如果存在）
                    if (typeof oldOnChange === 'function') {
                        oldOnChange.call(this, event);
                    }
                };
                educationStageSelect._hasFixedOnChange = true;
            }
        }
    }

    // 激活章节选择器
    function enableChapterSelectors() {
        const chapterSelect = document.getElementById('chapter');
        if (chapterSelect && chapterSelect.disabled) {
            console.log("激活章节选择器");
            chapterSelect.disabled = false;
        }
        
        const unitSelect = document.getElementById('unit');
        if (unitSelect && unitSelect.disabled) {
            unitSelect.disabled = false;
        }
        
        const lessonSelect = document.getElementById('lesson');
        if (lessonSelect && lessonSelect.disabled) {
            lessonSelect.disabled = false;
        }
    }

    // 初始化章节数据
    function initializeChapterData() {
        if (!window.allQuestions || !Array.isArray(window.allQuestions) || window.allQuestions.length === 0) {
            console.warn('无法初始化章节数据：allQuestions 为空或未定义');
            return;
        }

        const subject = safeGetElementValue('subject');
        if (!subject) {
            console.log("未选择学科，无需初始化章节数据");
            return;
        }

        console.log(`准备初始化章节数据，当前有 ${window.allQuestions.length} 道题目，已选择学科: ${subject}`);
        
        // 根据选择的学科筛选题目
        const filteredQuestions = window.allQuestions.filter(q => q.subject === subject);
        console.log(`该学科有 ${filteredQuestions.length} 道题目`);
        
        if (filteredQuestions.length === 0) {
            console.warn(`未找到学科为 ${subject} 的题目`);
            return;
        }
        
        // 收集所有可用的章节
        const chapters = new Set();
        filteredQuestions.forEach(q => {
            if (q.chapter) {
                chapters.add(q.chapter);
            }
        });
        
        // 填充章节选择器
        if (chapters.size > 0) {
            populateSelect('chapter', Array.from(chapters));
            enableChapterSelectors();
            console.log(`已加载 ${chapters.size} 个章节选项`);
            
            // 重新绑定章节选择器事件
            const chapterSelect = document.getElementById('chapter');
            if (chapterSelect && !chapterSelect._hasFixedOnChange) {
                const oldOnChange = chapterSelect.onchange;
                chapterSelect.onchange = function(event) {
                    const chapter = this.value;
                    console.log(`章节变更为: ${chapter}`);
                    
                    // 更新单元选择器
                    if (chapter && window.allQuestions) {
                        const units = new Set();
                        window.allQuestions.filter(q => q.subject === subject && q.chapter === chapter).forEach(q => {
                            if (q.unit) units.add(q.unit);
                        });
                        
                        populateSelect('unit', Array.from(units));
                    }
                    
                    // 应用筛选
                    setTimeout(() => {
                        if (typeof window.filterQuestions === 'function') {
                            window.filterQuestions();
                        }
                    }, 200);
                    
                    // 调用原有的事件处理函数（如果存在）
                    if (typeof oldOnChange === 'function') {
                        oldOnChange.call(this, event);
                    }
                };
                chapterSelect._hasFixedOnChange = true;
            }
        } else {
            console.warn('未找到章节数据');
        }
    }
    
    // 填充选择器的通用函数
    function populateSelect(selectId, options) {
        const select = document.getElementById(selectId);
        if (!select) return;
        
        // 保留第一个选项（通常是提示文本）
        const firstOption = select.options[0];
        select.innerHTML = '';
        select.appendChild(firstOption);
        
        // 获取当前科目
        const currentSubject = document.getElementById('subject').value;
        
        // 章节的自定义排序
        if ((currentSubject === '政治' || currentSubject === '历史') && selectId === 'chapter') {
            // 自定义排序顺序
            const chapterOrder = {
                '必修一': 1,
                '必修二': 2,
                '必修三': 3, 
                '必修四': 4,
                '选择性必修一': 5,
                '选择性必修二': 6,
                '选择性必修三': 7
            };
            
            // 排序函数，按指定顺序排列章节
            options.sort((a, b) => {
                // 提取章节关键词 (必修一, 必修二, etc.)
                const getChapterKey = (str) => {
                    for (const key in chapterOrder) {
                        if (str.includes(key)) {
                            return key;
                        }
                    }
                    return str; // 如果不匹配任何关键词，返回原字符串
                };
                
                const keyA = getChapterKey(a);
                const keyB = getChapterKey(b);
                
                // 如果都能找到对应的排序值，按顺序排
                if (chapterOrder[keyA] && chapterOrder[keyB]) {
                    return chapterOrder[keyA] - chapterOrder[keyB];
                }
                // 如果只有一个能找到排序值，有排序值的排在前面
                else if (chapterOrder[keyA]) {
                    return -1;
                }
                else if (chapterOrder[keyB]) {
                    return 1;
                }
                // 否则按字母顺序排
                else {
                    return a.localeCompare(b);
                }
            });
        } 
        // 单元的自定义排序
        else if (selectId === 'unit') {
            // 定义单元的排序权重
            const getUnitWeight = (str) => {
                // 标准的单元格式处理: "第X单元"
                if (str.includes('第一单元')) return 1;
                if (str.includes('第二单元')) return 2;
                if (str.includes('第三单元')) return 3;
                if (str.includes('第四单元')) return 4;
                if (str.includes('第五单元')) return 5;
                if (str.includes('第六单元')) return 6;
                if (str.includes('第七单元')) return 7;
                if (str.includes('第八单元')) return 8;
                if (str.includes('第九单元')) return 9;
                if (str.includes('第十单元')) return 10;
                
                // 如果是其他格式，使用高数值，排在后面
                return 999;
            };
            
            // 按单元权重排序
            options.sort((a, b) => {
                return getUnitWeight(a) - getUnitWeight(b);
            });
        }
        // 课程的自定义排序
        else if (selectId === 'lesson') {
            // 定义课程的排序权重
            const getLessonWeight = (str) => {
                // 标准的课程格式处理: "第X课"
                if (str.includes('第一课')) return 1;
                if (str.includes('第二课')) return 2;
                if (str.includes('第三课')) return 3;
                if (str.includes('第四课')) return 4;
                if (str.includes('第五课')) return 5;
                if (str.includes('第六课')) return 6;
                if (str.includes('第七课')) return 7;
                if (str.includes('第八课')) return 8;
                if (str.includes('第九课')) return 9;
                if (str.includes('第十课')) return 10;
                if (str.includes('第十一课')) return 11;
                if (str.includes('第十二课')) return 12;
                if (str.includes('第十三课')) return 13;
                if (str.includes('第十四课')) return 14;
                if (str.includes('第十五课')) return 15;
                if (str.includes('第十六课')) return 16;
                if (str.includes('第十七课')) return 17;
                if (str.includes('第十八课')) return 18;
                if (str.includes('第十九课')) return 19;
                if (str.includes('第二十课')) return 20;
                
                // 如果是其他格式，使用高数值，排在后面
                return 999;
            };
            
            // 按课程权重排序
            options.sort((a, b) => {
                return getLessonWeight(a) - getLessonWeight(b);
            });
        } else {
            // 其他情况使用默认排序
            options.sort();
        }
        
        // 添加新选项
        options.forEach(option => {
            if (option) { // 确保选项不为空
                const optElement = document.createElement('option');
                optElement.value = option;
                optElement.textContent = option;
                select.appendChild(optElement);
            }
        });
    }

    // 监控数据加载情况
    function monitorDataLoading() {
        console.log('开始监控数据加载...');
        let checkCount = 0;
        const maxChecks = 30; // 最多检查30次
        
        const checkInterval = setInterval(() => {
            checkCount++;
            // 检查是否有题目元素或已显示无题目提示
            const questionCards = document.getElementById('questionCards');
            const noQuestions = document.getElementById('noQuestions');
            
            if ((questionCards && questionCards.children.length > 0) || 
                (noQuestions && noQuestions.style.display !== 'none')) {
                clearInterval(checkInterval);
                console.log('数据加载完成');
                
                // 在加载完成后，检查是否有依赖的页面元素需要初始化
                initializeMissingElements();
            } else {
                console.log(`等待数据加载... (${checkCount}/${maxChecks})`);
                
                // 如果检查次数过多，尝试帮助加载
                if (checkCount > 15 && typeof filterQuestions === 'function') {
                    console.log('尝试帮助初始化数据...');
                    try {
                        filterQuestions();
                    } catch (e) {
                        console.error('尝试初始化数据时出错:', e);
                    }
                }
            }
            
            // 如果检查次数达到上限，停止检查
            if (checkCount >= maxChecks) {
                clearInterval(checkInterval);
                console.warn('数据加载超时，尝试自动修复中...');
                
                // 尝试进行修复操作
                repairDataLoading();
            }
        }, 1000);
    }
    
    // 修复数据加载问题
    function repairDataLoading() {
        // 检查并修复关键元素
        ['loading', 'noQuestions', 'questionCards'].forEach(id => {
            const element = document.getElementById(id);
            if (!element) {
                console.log(`创建缺失的${id}元素`);
                const newElement = document.createElement('div');
                newElement.id = id;
                
                if (id === 'loading') {
                    newElement.style.padding = '20px';
                    newElement.style.textAlign = 'center';
                    newElement.innerText = '正在加载题目数据...';
                    newElement.style.display = 'none'; // 默认隐藏
                } else if (id === 'noQuestions') {
                    newElement.style.padding = '20px';
                    newElement.style.textAlign = 'center';
                    newElement.innerHTML = '<p>没有找到符合条件的题目</p>';
                    newElement.style.display = 'block'; // 显示无题目提示
                } else if (id === 'questionCards') {
                    newElement.className = 'question-list';
                }
                
                // 添加到内容区域
                const contentArea = document.querySelector('.content-area');
                if (contentArea) {
                    contentArea.appendChild(newElement);
                } else {
                    document.body.appendChild(newElement);
                }
            }
        });
        
        // 检查元素后，尝试再次触发筛选
        if (typeof filterQuestions === 'function') {
            console.log('尝试重新筛选题目...');
            setTimeout(() => {
                try {
                    filterQuestions();
                } catch (e) {
                    console.error('尝试筛选题目时出错:', e);
                }
            }, 1000);
        }
    }
    
    // 初始化可能缺失的页面元素
    function initializeMissingElements() {
        // 原来的分页控件代码会导致移动端出现两个分页，注释掉解决问题
        // const paginationControls = document.getElementById('paginationControls');
        // if (paginationControls) {
        //     if (!paginationControls.querySelector('.pagination-btn')) {
        //         // 创建分页按钮
        //         const prevBtn = document.createElement('button');
        //         prevBtn.className = 'pagination-btn';
        //         prevBtn.innerText = '上一页';
        //         prevBtn.onclick = () => window.changePage(-1);
        //         
        //         const nextBtn = document.createElement('button');
        //         nextBtn.className = 'pagination-btn';
        //         nextBtn.innerText = '下一页';
        //         nextBtn.onclick = () => window.changePage(1);
        //         
        //         const pageInfo = document.createElement('span');
        //         pageInfo.id = 'pageInfo';
        //         pageInfo.className = 'page-info';
        //         pageInfo.innerText = '第 1 页';
        //         
        //         paginationControls.appendChild(prevBtn);
        //         paginationControls.appendChild(pageInfo);
        //         paginationControls.appendChild(nextBtn);
        //     }
        // }
    }

    // 启动数据加载监控
    monitorDataLoading();

    // 安全重置依赖的选择器函数，替换原始函数
    window.resetDependentSelectors = function(selectId) {
        console.log(`安全重置依赖选择器: ${selectId}`);
        const hierarchy = ['subject', 'chapter', 'unit', 'lesson'];
        const startIndex = hierarchy.indexOf(selectId);
        
        if (startIndex === -1) return;
        
        // 重置后续所有选择器
        for (let i = startIndex + 1; i < hierarchy.length; i++) {
            const select = document.getElementById(hierarchy[i]);
            if (!select) {
                console.warn(`选择器元素不存在: ${hierarchy[i]}`);
                continue;
            }
            
            if (!select.options || select.options.length === 0) {
                console.warn(`选择器 ${hierarchy[i]} 没有选项`);
                select.innerHTML = `<option value="">请选择</option>`;
            } else {
                const categoryName = select.options[0].text || "请选择"; 
                select.innerHTML = `<option value="">${categoryName}</option>`;
            }
            select.disabled = true;
        }
    };

    // 覆盖原始的筛选函数
    function overrideFilterQuestions() {
        console.log("覆盖原始的filterQuestions函数");
        
        window.originalFilterQuestions = window.filterQuestions;
        
        window.filterQuestions = function() {
            // **加强检查**: 确保allQuestions已定义并且是一个数组
            if (!window.allQuestions || !Array.isArray(window.allQuestions)) {
                console.warn('filterQuestions: allQuestions尚未准备好或不是数组');
                // 移除显示"共找到0道题目"的文本
                // safeSetElementText('questionCount', '共找到 0 道题目');
                return; // 提前返回，不执行筛选
            }

            console.log(`开始筛选，原始题目数量：${window.allQuestions.length}`);

            const subject = safeGetElementValue('subject');
            const questionType = safeGetElementValue('questionType');
            const educationStage = safeGetElementValue('educationStage');
            const chapter = safeGetElementValue('chapter');
            const unit = safeGetElementValue('unit');
            const lesson = safeGetElementValue('lesson');
            const searchText = safeGetElementValue('searchBox').toLowerCase();
            
            console.log(`筛选条件: 学科=${subject}, 题型=${questionType}, 学段=${educationStage}, 章节=${chapter}, 单元=${unit}, 课程=${lesson}`);
            
            // 应用筛选条件
            const filteredQuestions = window.allQuestions.filter(q => {
                // 基本筛选条件
                if (subject && q.subject !== subject) return false;
                if (questionType && q.questionType !== questionType) return false;
                if (educationStage && q.educationStage !== educationStage) return false;
                if (chapter && q.chapter !== chapter) return false;
                if (unit && q.unit !== unit) return false;
                if (lesson && q.lesson !== lesson) return false;
                
                // 搜索文本筛选
                if (searchText) {
                    const questionText = (q.question || '').toLowerCase();
                    const answerText = (q.answer || '').toLowerCase();
                    return questionText.includes(searchText) || answerText.includes(searchText);
                }
                
                return true;
            });
            
            console.log(`筛选后题目数量：${filteredQuestions.length}`);
            
            // 确保renderQuestions函数存在
            if (typeof window.renderQuestions === 'function') {
                try {
                    // 更新题目显示
                    window.renderQuestions(filteredQuestions);
                    
                    // 移除显示"共找到0道题目"的文本
                    // safeSetElementText('questionCount', `共找到 ${filteredQuestions.length} 道题目`);
                    
                    // 显示或隐藏"无题目"提示
                    if (filteredQuestions.length > 0) {
                        safeSetElementStyle('noQuestions', 'display', 'none');
                    } else {
                        safeSetElementStyle('noQuestions', 'display', 'block');
                    }
                    
                    // 保存筛选后的题目列表
                    window.filteredQuestions = filteredQuestions;
                } catch (error) {
                    console.error('渲染题目时出错:', error);
                }
            } else {
                console.error('renderQuestions函数未定义');
            }
        };
    }
    
    // 覆盖原始的filterQuestionsBasedOnCurrentSelections函数
    function overrideFilterQuestionsBasedOnCurrentSelections() {
        console.log("覆盖原始的filterQuestionsBasedOnCurrentSelections函数");
        
        window.originalFilterQuestionsBasedOnCurrentSelections = window.filterQuestionsBasedOnCurrentSelections;
        
        window.filterQuestionsBasedOnCurrentSelections = function() {
            // **加强检查**: 确保allQuestions已定义并且是一个数组
            if (!window.allQuestions || !Array.isArray(window.allQuestions)) {
                console.warn('filterQuestionsBasedOnCurrentSelections: allQuestions尚未准备好或不是数组');
                return []; // 返回空数组，因为无法筛选
            }

            const subject = safeGetElementValue('subject');
            const questionType = safeGetElementValue('questionType');
            const educationStage = safeGetElementValue('educationStage');
            const chapter = safeGetElementValue('chapter');
            const unit = safeGetElementValue('unit');
            
            return window.allQuestions.filter(q => {
                if (subject && q.subject !== subject) return false;
                if (questionType && q.questionType !== questionType) return false;
                if (educationStage && q.educationStage !== educationStage) return false;
                if (chapter && q.chapter !== chapter) return false;
                if (unit && q.unit !== unit) return false;
                return true;
            });
        };
    }

    // 确保populateSelect函数定义在全局作用域
    window.populateSelect = populateSelect;

    // 检查updateQuestionTypes函数是否已存在，如果没有则定义它
    if (typeof window.updateQuestionTypes !== 'function') {
        // 定义updateQuestionTypes函数
        window.updateQuestionTypes = function() {
            const subject = safeGetElementValue('subject');
            if (!subject) return;
            
            const questionTypes = {
                '语文': ['文言文阅读', '现代文阅读', '古诗词鉴赏', '名篇名句默写', '语言文字运用', '作文'],
                '数学': ['单项选择题', '多项选择题', '填空题', '解答题', '证明题', '应用题'],
                '英语': ['听力理解', '阅读理解', '完形填空', '语法填空', '短文改错', '书面表达'],
                '物理': ['选择题', '实验题', '计算题', '作图题', '论述题', '创新设计题'],
                '化学': ['选择题', '物质推断题', '实验综合题', '工艺流程题', '反应原理题', '结构分析题'],
                '生物': ['选择题', '实验探究题', '遗传分析题', '生态综合题', '生理调节题', '生物技术题'],
                '政治': ['选择题', '辨析题', '材料分析题', '论述题', '综合探究题', '时政评析题'],
                '历史': ['选择题', '材料解析题', '历史小论文', '时空定位题', '史实辨析题', '历史地图题'],
                '地理': ['选择题', '读图分析题', '区位分析题', '地理计算题', '自然灾害题', '区域发展题']
            };
            
            // 获取当前科目对应的题型
            const types = questionTypes[subject] || [];
            
            // 填充题型选择器
            const typeSelect = document.getElementById('questionType');
            if (typeSelect) {
                // 保留第一个选项
                const firstOption = typeSelect.options[0];
                typeSelect.innerHTML = '';
                typeSelect.appendChild(firstOption);
                
                // 添加题型选项
                types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type;
                    option.textContent = type;
                    typeSelect.appendChild(option);
                });
                
                // 确保题型变更时能触发筛选
                if (!typeSelect._hasFixedOnChange) {
                    const oldOnChange = typeSelect.onchange;
                    typeSelect.onchange = function(event) {
                        console.log(`题型变更为: ${this.value}`);
                        
                        // 应用筛选
                        setTimeout(() => {
                            if (typeof window.filterQuestions === 'function') {
                                window.filterQuestions();
                            }
                        }, 200);
                        
                        // 调用原有的事件处理函数（如果存在）
                        if (typeof oldOnChange === 'function') {
                            oldOnChange.call(this, event);
                        }
                    };
                    typeSelect._hasFixedOnChange = true;
                }
            }
        };
    }

    // 在适当的时间点执行，确保原始函数已定义
    setTimeout(() => {
        // 覆盖原始的筛选函数
        overrideFilterQuestions();
        overrideFilterQuestionsBasedOnCurrentSelections();
        
        // 确保章节选择器可用
        enableChapterSelectors();
        
        // 修复科目和学段选择器
        fixSubjectSelector();
        fixEducationStageSelector();
        
        // 注册搜索框事件
        const searchBox = document.getElementById('searchBox');
        if (searchBox && !searchBox._hasFixedOnInput) {
            searchBox.addEventListener('input', function() {
                if (typeof window.filterQuestions === 'function') {
                    window.filterQuestions();
                }
            });
            searchBox._hasFixedOnInput = true;
        }
        
        console.log('客户端修复脚本已完成所有修复和优化');
    }, 1000);
});
