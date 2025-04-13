/**
 * 英语科目筛选逻辑修复脚本
 * 版本: 1.1.0
 * 日期: 2025-04-07
 * 功能: 根据学段和题型过滤章节选项
 */

(function() {
    console.log('英语科目筛选逻辑修复脚本已加载 版本 1.1.0');
    
    // 原始updateDependentSelector函数的引用
    let originalUpdateDependentSelector = null;
    // 原始filterQuestionsBasedOnCurrentSelections函数的引用
    let originalFilterQuestionsBasedOnCurrentSelections = null;
    
    // 当DOM加载完成后执行
    document.addEventListener('DOMContentLoaded', function() {
        // 保存原始函数引用
        if (typeof window.updateDependentSelector === 'function') {
            originalUpdateDependentSelector = window.updateDependentSelector;
            
            // 覆盖原始函数
            window.updateDependentSelector = function(currentSelectId, selectedValue) {
                // 首先调用原始函数以获取基础功能
                originalUpdateDependentSelector(currentSelectId, selectedValue);
                
                // 在原始函数执行后进行额外的过滤
                applyEnglishFilter();
            };
            
            console.log('已覆盖updateDependentSelector函数');
        } else {
            console.warn('未找到updateDependentSelector函数，将在页面加载后尝试覆盖');
            
            // 如果页面加载较慢，尝试稍后覆盖函数
            setTimeout(function() {
                if (typeof window.updateDependentSelector === 'function') {
                    originalUpdateDependentSelector = window.updateDependentSelector;
                    
                    window.updateDependentSelector = function(currentSelectId, selectedValue) {
                        originalUpdateDependentSelector(currentSelectId, selectedValue);
                        applyEnglishFilter();
                    };
                    
                    console.log('已延迟覆盖updateDependentSelector函数');
                    
                    // 立即应用筛选
                    applyEnglishFilter();
                } else {
                    console.error('无法找到updateDependentSelector函数，筛选功能可能无法正常工作');
                }
            }, 1000); // 等待1秒再尝试
        }
        
        // 覆盖filterQuestionsBasedOnCurrentSelections函数
        if (typeof window.filterQuestionsBasedOnCurrentSelections === 'function') {
            originalFilterQuestionsBasedOnCurrentSelections = window.filterQuestionsBasedOnCurrentSelections;
            
            window.filterQuestionsBasedOnCurrentSelections = function() {
                // 调用原始函数
                const filteredQuestions = originalFilterQuestionsBasedOnCurrentSelections();
                
                // 应用额外的筛选逻辑
                return applyAdditionalFiltering(filteredQuestions);
            };
            
            console.log('已覆盖filterQuestionsBasedOnCurrentSelections函数');
        }
        
        // 为相关选择器添加变更事件监听器
        attachFilterEventListeners();
    });
    
    // 应用英语筛选逻辑 - 处理听力题章节和学段过滤
    function applyEnglishFilter() {
        const educationStage = document.getElementById('educationStage')?.value || '';
        const subject = document.getElementById('subject')?.value || '';
        const questionType = document.getElementById('questionType')?.value || '';
        const chapterSelect = document.getElementById('chapter');
        const unitSelect = document.getElementById('unit');
        const lessonSelect = document.getElementById('lesson');
        
        // 仅在章节选择器存在且未禁用时执行逻辑
        if (!chapterSelect || chapterSelect.disabled) {
            return;
        }
        
        // 高中英语听力理解 - 不显示"听句子选答案"
        if (educationStage === '高中' && subject === '英语' && questionType === '听力理解') {
            removeChapterOption(chapterSelect, '听句子选答案');
            console.log('已移除高中英语听力理解中的"听句子选答案"选项');
        }
        
        // 初中英语听力理解 - 不显示"听短对话选答案"
        if (educationStage === '初中' && subject === '英语' && questionType === '听力理解') {
            removeChapterOption(chapterSelect, '听短对话选答案');
            console.log('已移除初中英语听力理解中的"听短对话选答案"选项');
        }
        
        // 确保只显示当前选择的学段的英语章节/单元/课程
        if (subject === '英语') {
            filterEnglishContentByEducationStage(educationStage);
        }
    }
    
    // 根据学段过滤英语内容
    function filterEnglishContentByEducationStage(educationStage) {
        // 获取所有下拉选择器
        const selectors = ['chapter', 'unit', 'lesson'].map(id => document.getElementById(id)).filter(el => el);
        
        // 查询当前已加载的所有题目
        const allQuestions = window.allQuestions || [];
        const chapterSelect = document.getElementById('chapter');
        const unitSelect = document.getElementById('unit');
        
        // 当前选中的章节
        const selectedChapter = chapterSelect ? chapterSelect.value : '';
        
        selectors.forEach(selector => {
            if (selector && !selector.disabled) {
                // 保存当前选中的值
                const currentValue = selector.value;
                
                // 获取符合当前学段的选项
                const validOptions = [];
                const seen = new Set(); // 用于去重
                
                // 从第一个选项开始（通常是标题选项）
                if (selector.options.length > 0) {
                    validOptions.push(selector.options[0].text);
                    seen.add(selector.options[0].text);
                }
                
                // 从题目数据中提取符合当前学段的选项
                allQuestions.forEach(question => {
                    // 基本条件：匹配教育阶段和科目
                    const matchesBasicCriteria = 
                        question.educationStage === educationStage && 
                        question.subject === '英语';
                    
                    // 针对单元选择器的特殊处理
                    if (selector.id === 'unit' && matchesBasicCriteria) {
                        // 如果选择了章节，则只显示该章节下的单元
                        if (selectedChapter && selectedChapter !== '请选择' && 
                            question.chapter !== selectedChapter) {
                            return; // 跳过不匹配当前章节的题目
                        }
                        
                        const value = question[selector.id]; // 使用选择器ID作为字段名
                        if (value && !seen.has(value)) {
                            seen.add(value);
                            validOptions.push(value);
                        }
                    } 
                    // 对其他选择器的处理
                    else if (matchesBasicCriteria) {
                        const value = question[selector.id]; // 使用选择器ID作为字段名
                        if (value && !seen.has(value)) {
                            seen.add(value);
                            validOptions.push(value);
                        }
                    }
                });
                
                // 如果没有有效选项，保持选择器禁用状态
                if (validOptions.length <= 1) {
                    selector.disabled = true;
                    if (selector.id === 'unit') {
                        console.log('单元选择器没有有效选项，已禁用');
                    }
                    return;
                }
                
                // 重建选择器选项
                const firstOption = selector.options[0]; // 保存标题选项
                selector.innerHTML = '';
                selector.appendChild(firstOption);
                
                // 添加有效选项
                validOptions.slice(1).forEach(option => { // 跳过标题选项
                    const optElement = document.createElement('option');
                    optElement.value = option;
                    optElement.textContent = option;
                    selector.appendChild(optElement);
                });
                
                // 尝试恢复之前的选择
                if (currentValue && Array.from(selector.options).some(opt => opt.value === currentValue)) {
                    selector.value = currentValue;
                }
                
                // 启用选择器
                selector.disabled = false;
                
                // 针对单元选择器的日志输出
                if (selector.id === 'unit') {
                    console.log(`单元选择器已更新，共${validOptions.length - 1}个选项，当前选择的章节: ${selectedChapter}`);
                }
            }
        });
    }
    
    // 额外的题目筛选逻辑 - 确保只返回匹配当前学段的题目
    function applyAdditionalFiltering(questions) {
        const educationStage = document.getElementById('educationStage')?.value || '';
        const subject = document.getElementById('subject')?.value || '';
        
        // 如果没有选择学段或科目，返回原始结果
        if (!educationStage || !subject) {
            return questions;
        }
        
        // 确保只返回匹配当前学段和科目的题目
        return questions.filter(q => 
            q.educationStage === educationStage && 
            (subject ? q.subject === subject : true)
        );
    }
    
    // 从选择器中移除指定选项
    function removeChapterOption(selectElement, optionText) {
        for (let i = 0; i < selectElement.options.length; i++) {
            if (selectElement.options[i].text === optionText || 
                selectElement.options[i].value === optionText) {
                selectElement.remove(i);
                break;
            }
        }
    }
    
    // 为相关选择器添加变更事件监听
    function attachFilterEventListeners() {
        const selectors = ['educationStage', 'subject', 'questionType', 'chapter', 'unit', 'lesson'];
        
        selectors.forEach(function(selectorId) {
            const element = document.getElementById(selectorId);
            if (element) {
                element.addEventListener('change', function() {
                    // 每当相关选择器的值变更时，应用筛选逻辑
                    setTimeout(applyEnglishFilter, 100); // 短暂延迟确保其他处理已完成
                    
                    // 特殊处理英语科目下的章节选择
                    if (selectorId === 'chapter') {
                        const subject = document.getElementById('subject')?.value || '';
                        const educationStage = document.getElementById('educationStage')?.value || '';
                        
                        if (subject === '英语') {
                            setTimeout(() => fetchEnglishUnits(educationStage, element.value), 200);
                        }
                    }
                });
            }
        });
        
        // 特别监听英语科目选择
        const subjectSelect = document.getElementById('subject');
        if (subjectSelect) {
            subjectSelect.addEventListener('change', function() {
                if (this.value === '英语') {
                    const educationStage = document.getElementById('educationStage')?.value || '';
                    const chapter = document.getElementById('chapter')?.value || '';
                    
                    // 获取英语相关的单元列表
                    if (chapter && chapter !== '请选择') {
                        setTimeout(() => fetchEnglishUnits(educationStage, chapter), 200);
                    }
                }
            });
        }
    }
    
    // 从API获取英语单元列表
    function fetchEnglishUnits(educationStage, chapter) {
        const unitSelect = document.getElementById('unit');
        if (!unitSelect) return;
        
        // 保存当前选择
        const currentValue = unitSelect.value;
        
        // 如果没有有效的章节，则禁用单元选择器
        if (!chapter || chapter === '请选择') {
            unitSelect.innerHTML = '<option value="">请选择</option>';
            unitSelect.disabled = true;
            return;
        }
        
        console.log(`正在获取英语单元列表: 学段=${educationStage}, 章节=${chapter}`);
        
        // 构建API URL
        const apiUrl = `/api/english_units?education_stage=${encodeURIComponent(educationStage)}&chapter=${encodeURIComponent(chapter)}`;
        
        // 获取单元列表
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success && Array.isArray(data.units)) {
                    // 重建单元选择器
                    unitSelect.innerHTML = '<option value="">请选择</option>';
                    
                    // 添加单元选项
                    data.units.forEach(unit => {
                        if (unit) {
                            const option = document.createElement('option');
                            option.value = unit;
                            option.textContent = unit;
                            unitSelect.appendChild(option);
                        }
                    });
                    
                    // 尝试恢复之前的选择
                    if (currentValue && Array.from(unitSelect.options).some(opt => opt.value === currentValue)) {
                        unitSelect.value = currentValue;
                    }
                    
                    // 启用单元选择器
                    unitSelect.disabled = false;
                    console.log(`单元选择器已更新，共${data.units.length}个选项`);
                    
                    // 如果当前单元已选择，更新课程列表
                    if (unitSelect.value && unitSelect.value !== '请选择') {
                        fetchEnglishLessons(educationStage, chapter, unitSelect.value);
                    }
                } else {
                    console.warn('获取英语单元列表失败:', data.error || '未知错误');
                    unitSelect.innerHTML = '<option value="">请选择</option>';
                    unitSelect.disabled = true;
                }
            })
            .catch(error => {
                console.error('获取英语单元列表出错:', error);
                unitSelect.innerHTML = '<option value="">请选择</option>';
                unitSelect.disabled = true;
            });
    }
    
    // 从API获取英语课程列表
    function fetchEnglishLessons(educationStage, chapter, unit) {
        const lessonSelect = document.getElementById('lesson');
        if (!lessonSelect) return;
        
        // 保存当前选择
        const currentValue = lessonSelect.value;
        
        // 如果没有有效的单元，则禁用课程选择器
        if (!unit || unit === '请选择') {
            lessonSelect.innerHTML = '<option value="">请选择</option>';
            lessonSelect.disabled = true;
            return;
        }
        
        console.log(`正在获取英语课程列表: 学段=${educationStage}, 章节=${chapter}, 单元=${unit}`);
        
        // 构建API URL
        const apiUrl = `/api/english_lessons?education_stage=${encodeURIComponent(educationStage)}&chapter=${encodeURIComponent(chapter)}&unit=${encodeURIComponent(unit)}`;
        
        // 获取课程列表
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success && Array.isArray(data.lessons)) {
                    // 重建课程选择器
                    lessonSelect.innerHTML = '<option value="">请选择</option>';
                    
                    // 添加课程选项
                    data.lessons.forEach(lesson => {
                        if (lesson) {
                            const option = document.createElement('option');
                            option.value = lesson;
                            option.textContent = lesson;
                            lessonSelect.appendChild(option);
                        }
                    });
                    
                    // 尝试恢复之前的选择
                    if (currentValue && Array.from(lessonSelect.options).some(opt => opt.value === currentValue)) {
                        lessonSelect.value = currentValue;
                    }
                    
                    // 启用课程选择器
                    lessonSelect.disabled = data.lessons.length === 0;
                    console.log(`课程选择器已更新，共${data.lessons.length}个选项`);
                } else {
                    console.warn('获取英语课程列表失败:', data.error || '未知错误');
                    lessonSelect.innerHTML = '<option value="">请选择</option>';
                    lessonSelect.disabled = true;
                }
            })
            .catch(error => {
                console.error('获取英语课程列表出错:', error);
                lessonSelect.innerHTML = '<option value="">请选择</option>';
                lessonSelect.disabled = true;
            });
    }
    
    // 初始页面加载完成后执行一次筛选
    window.addEventListener('load', function() {
        setTimeout(applyEnglishFilter, 500); // 延迟执行确保页面元素已加载
        
        // 添加特定的检查，确保高中英语听力的筛选按钮可用
        setTimeout(function() {
            const educationStage = document.getElementById('educationStage')?.value || '';
            const subject = document.getElementById('subject')?.value || '';
            const questionType = document.getElementById('questionType')?.value || '';
            
            if (educationStage === '高中' && subject === '英语' && questionType === '听力理解') {
                const unitSelect = document.getElementById('unit');
                if (unitSelect && unitSelect.disabled && unitSelect.options.length <= 1) {
                    // 强制启用单元选择器
                    unitSelect.disabled = false;
                    console.log('已强制启用高中英语听力的单元选择器');
                    
                    // 重新应用筛选
                    applyEnglishFilter();
                }
            }
        }, 1000);
    });
})();
