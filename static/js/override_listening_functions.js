// 覆盖client.html中定义的听力题目处理函数
document.addEventListener('DOMContentLoaded', function() {
    console.log("Overriding listening question functions...");
    
    // 覆盖processListeningQuestion函数
    window.processListeningQuestion = function(stem) {
        console.log("Using overridden processListeningQuestion function");
        
        // 如果题干包含数字序号（如"3．"），去除序号
        stem = stem.replace(/^\d+．\s*/, '');
        
        // 检查是否包含"听下面一段较长对话"或类似文本，这表明是完整的听力大题
        if (stem.includes('听下面一段较长对话') || 
            stem.includes('听录音') || 
            stem.includes('听短文选答案') || 
            stem.includes('听短文') || 
            stem.includes('听下面一段独白') || 
            stem.includes('听独白')) {
            
            // 这是一个包含多个小题的大题，保留整个内容并美化格式
            console.log("Detected complete listening question, formatting...");
            return window.formatMultiListeningQuestion(stem);
        }
        
        // 原有逻辑：提取What/Why/When/How/Who/Where/Which等开头的单个问题
        const questionPattern = /(What|Why|When|How|Who|Where|Which).*?\?/;
        const match = stem.match(questionPattern);
        
        // 如果找到匹配的问题，则只返回问题部分
        if (match) {
            return match[0];
        }
        
        // 如果没有找到标准问题模式，则去除常见的指令前缀
        return stem.replace(/Listen to the recording.*?\./i, '').trim();
    };
    
    // 覆盖formatMultiListeningQuestion函数
    window.formatMultiListeningQuestion = function(text) {
        console.log("Using overridden formatMultiListeningQuestion function: ", text.substring(0, 50));
        
        if (!text) return '';
        
        // 提取题目前导部分，并修复序号格式
        let title = '';
        let questionNum = '';
        
        // 查找序号，如 "1、" 或 "1．"
        const numMatch = text.match(/^(\d+)[、．\.]/);
        if (numMatch) {
            questionNum = numMatch[1] + '、';
        }
        
        const titlePattern = /(听下面一段较长对话|听下面一段独白|听短文|听录音|听独白|听短文选答案).*?[，|。]/;
        const titleMatch = text.match(titlePattern);
        
        if (titleMatch) {
            title = titleMatch[0];
            
            // 如果标题不包含"回答以下小题"，添加它
            if (!title.includes('回答以下小题')) {
                title = title.replace(/[，|。]$/, '，回答以下小题。');
            }
        } else {
            console.log("No title match found");
            // 如果没找到标题但是听力题，提供默认标题
            if ((text.includes('听') || text.toLowerCase().includes('listen')) && 
                ((text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || []).length > 0)) {
                title = '听下面一段较长对话,回答以下小题。';
            }
        }
        
        // 确保标题的开头有序号
        if (questionNum && !title.startsWith(questionNum)) {
            title = questionNum + title;
        }
        
        // 提取所有英文问题 - 增加对Which开头问题的支持
        const englishQuestions = text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || [];
        console.log("Found questions: ", englishQuestions.length);
        
        if (englishQuestions.length === 0) {
            console.log("No English questions found in text!");
            return text; // 如果找不到英文问题，返回原始文本
        }
        
        // 构建格式化后的HTML - 严格按照示例格式
        let formattedHTML = `<div class="listening-question-container" style="margin-bottom:24px;">
            <div class="listening-title" style="font-weight:bold;margin-bottom:16px;font-size:16px;color:#000;">${title}</div>`;
        
        // 改进方法：先分析整个文本中所有的选项
        // 收集所有的A, B, C选项模式
        const allOptions = [];
        let optionMatches = text.matchAll(/([A-C])[\s\.．]+(.*?)(?=(?:[A-C][\s\.．]+)|(?:What|Why|When|How|Who|Where|Which)|$)/gs);
        for (const match of optionMatches) {
            allOptions.push({
                letter: match[1],
                text: match[2].trim(),
                position: match.index
            });
        }
        console.log("Found total options: ", allOptions.length);
        
        // 分析问题和相应的选项
        let questionData = [];
        for (let i = 0; i < englishQuestions.length; i++) {
            const question = englishQuestions[i];
            const questionPos = text.indexOf(question);
            
            // 找出这个问题后面最近的选项
            const optionsForQuestion = {A: null, B: null, C: null};
            let nextQuestionPos = text.length;
            if (i < englishQuestions.length - 1) {
                nextQuestionPos = text.indexOf(englishQuestions[i+1], questionPos);
            }
            
            // 选择在问题位置之后，下一个问题位置之前的选项
            for (const option of allOptions) {
                if (option.position > questionPos && option.position < nextQuestionPos) {
                    optionsForQuestion[option.letter] = option.text;
                }
            }
            
            // 如果这个问题没有找到选项，但下一个问题前有What/Why等开头的文本但不在问题列表中
            // 说明可能是格式问题，尝试在整个文本中查找对应的选项
            if (!optionsForQuestion.A && !optionsForQuestion.B && !optionsForQuestion.C) {
                // 计算这个问题最可能的选项组
                const optionGroups = [];
                let currentGroup = [];
                let lastLetter = '';
                
                // 按字母顺序A->B->C对选项进行分组
                for (const option of allOptions) {
                    if (option.letter === 'A' && lastLetter !== 'A') {
                        if (currentGroup.length > 0) {
                            optionGroups.push(currentGroup);
                        }
                        currentGroup = [option];
                    } else if (option.letter === 'B' && lastLetter === 'A') {
                        currentGroup.push(option);
                    } else if (option.letter === 'C' && lastLetter === 'B') {
                        currentGroup.push(option);
                        optionGroups.push(currentGroup);
                        currentGroup = [];
                    }
                    lastLetter = option.letter;
                }
                
                // 如果有未完成的组，添加到组列表
                if (currentGroup.length > 0) {
                    optionGroups.push(currentGroup);
                }
                
                // 改进：长对话题的特殊处理，确保每个问题都有选项
                if (title.includes('较长对话') || title.includes('独白')) {
                    // 为长对话题，根据问题顺序分配选项组
                    const questionIndex = Math.floor(i / 2); // 两个问题一组
                    const groupIndex = questionIndex % optionGroups.length;
                    
                    if (optionGroups.length > 0) {
                        const group = optionGroups[groupIndex];
                        for (const option of group) {
                            optionsForQuestion[option.letter] = option.text;
                        }
                    }
                } else {
                    // 普通听力题，尝试按顺序分配选项组
                    if (optionGroups.length > i) {
                        const group = optionGroups[i];
                        for (const option of group) {
                            optionsForQuestion[option.letter] = option.text;
                        }
                    }
                }
            }
            
            questionData.push({
                question: question,
                options: optionsForQuestion
            });
        }
        
        // 构建问题HTML
        for (const data of questionData) {
            // 添加问题文本 - 加粗显示
            formattedHTML += `
                <div class="listening-subquestion" style="margin-bottom:15px">
                    <div class="question-text" style="margin-bottom:8px;font-weight:bold;line-height:1.5">${data.question}（  ）</div>`;
            
            // 添加选项 - 使用新的垂直布局
            formattedHTML += '<div class="listening-options-vertical" style="display:flex;flex-direction:column;padding-left:20px;margin-top:10px">';
            
            // 添加A选项
            if (data.options.A) {
                formattedHTML += `<div class="option-line" style="margin-bottom:8px;line-height:1.5">A．${data.options.A}</div>`;
            } else {
                // 如果找不到选项内容，使用通用的占位符
                formattedHTML += `<div class="option-line" style="margin-bottom:8px;line-height:1.5">A．选项A</div>`;
            }
            
            // 添加B选项
            if (data.options.B) {
                formattedHTML += `<div class="option-line" style="margin-bottom:8px;line-height:1.5">B．${data.options.B}</div>`;
            } else {
                formattedHTML += `<div class="option-line" style="margin-bottom:8px;line-height:1.5">B．选项B</div>`;
            }
            
            // 添加C选项
            if (data.options.C) {
                formattedHTML += `<div class="option-line" style="margin-bottom:8px;line-height:1.5">C．${data.options.C}</div>`;
            } else {
                formattedHTML += `<div class="option-line" style="margin-bottom:8px;line-height:1.5">C．选项C</div>`;
            }
            
            formattedHTML += '</div></div>';
        }
        
        formattedHTML += '</div>';
        return formattedHTML;
    };
    
    // 在DOM完全加载后再次执行，确保覆盖了所有函数
    setTimeout(function() {
        console.log("Re-applying overridden functions...");
        // 手动查找并修改已渲染的英语听力题内容
        const questionContents = document.querySelectorAll('.question-content');
        questionContents.forEach(function(content) {
            const text = content.textContent || '';
            
            // 检测听力题（包括长对话和独白）- 添加对Which开头问题的支持
            if ((text.includes('听下面一段较长对话') || 
                 text.includes('听短文') ||
                 text.includes('听短文选答案') ||
                 text.includes('听下面一段独白') || 
                 text.includes('听独白')) && 
                ((text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || []).length > 0)) {
                
                console.log("Found listening question, applying formatting");
                // 应用格式化
                const formattedText = window.formatMultiListeningQuestion(text);
                if (formattedText) {
                    content.innerHTML = formattedText;
                    // 添加标记表示此内容已被处理过
                    content.setAttribute('data-listening-processed', 'true');
                }
            }
        });
    }, 1000);
    
    // 添加监听器以处理动态加载的内容
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                // 检查新添加的问题内容
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // 元素节点
                        const contents = node.querySelectorAll ? 
                                         node.querySelectorAll('.question-content:not([data-listening-processed="true"])') : [];
                        
                        contents.forEach(content => {
                            const text = content.textContent || '';
                            
                            // 检测听力题（包括长对话和独白）- 添加对Which开头问题的支持
                            if ((text.includes('听下面一段较长对话') || 
                                 text.includes('听短文') ||
                                 text.includes('听短文选答案') ||
                                 text.includes('听下面一段独白') || 
                                 text.includes('听独白')) && 
                                ((text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || []).length > 0)) {
                                
                                console.log("Found dynamically added listening question");
                                // 应用格式化
                                const formattedText = window.formatMultiListeningQuestion(text);
                                if (formattedText) {
                                    content.innerHTML = formattedText;
                                    // 添加标记表示此内容已被处理过
                                    content.setAttribute('data-listening-processed', 'true');
                                }
                            }
                        });
                    }
                });
            }
        });
    });
    
    // 开始观察文档变化
    observer.observe(document.body, { childList: true, subtree: true });
});
