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
        
        // 将整个文本分成块，每个块包含一个问题和它的选项
        let questionBlocks = [];
        
        // 改进的方法来分割问题和选项
        for (let i = 0; i < englishQuestions.length; i++) {
            const question = englishQuestions[i];
            const startPos = text.indexOf(question);
            let endPos;
            
            // 如果不是最后一个问题，找下一个问题的位置
            if (i < englishQuestions.length - 1) {
                endPos = text.indexOf(englishQuestions[i+1]);
            } else {
                // 对于最后一个问题，使用文本末尾
                endPos = text.length;
            }
            
            if (startPos >= 0 && endPos > startPos) {
                // 提取当前问题和它的选项块
                const block = text.substring(startPos, endPos).trim();
                questionBlocks.push(block);
            }
        }
        
        // 处理每个问题块
        for (let i = 0; i < questionBlocks.length; i++) {
            const block = questionBlocks[i];
            const question = englishQuestions[i];
            
            // 提取问题后面的选项文本
            const optionsText = block.substring(question.length);
            
            // 改进的选项提取正则表达式
            const optionA = optionsText.match(/A[\s\.．](.*?)(?=B[\s\.．]|$)/s);
            const optionB = optionsText.match(/B[\s\.．](.*?)(?=C[\s\.．]|$)/s);
            const optionC = optionsText.match(/C[\s\.．](.*?)(?=$)/s);
            
            // 构建选项HTML，严格使用全角点"．"
            let optionsHTML = '<div class="listening-options-vertical" style="display:flex;flex-direction:column;padding-left:20px;margin-top:10px">';
            
            if (optionA && optionA[1]) {
                optionsHTML += `<div class="option-line" style="margin-bottom:8px;line-height:1.5">A．${optionA[1].trim()}</div>`;
            }
            
            if (optionB && optionB[1]) {
                optionsHTML += `<div class="option-line" style="margin-bottom:8px;line-height:1.5">B．${optionB[1].trim()}</div>`;
            }
            
            if (optionC && optionC[1]) {
                optionsHTML += `<div class="option-line" style="margin-bottom:8px;line-height:1.5">C．${optionC[1].trim()}</div>`;
            }
            
            optionsHTML += '</div>';
            
            // 添加问题和选项到HTML - 问题文本加粗显示
            formattedHTML += `
                <div class="listening-subquestion" style="margin-bottom:15px">
                    <div class="question-text" style="margin-bottom:8px;font-weight:bold;line-height:1.5">${question}</div>
                    ${optionsHTML}
                </div>
            `;
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
                                         node.querySelectorAll('.question-content') : [];
                        
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
