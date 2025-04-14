// Short passage listening questions formatter
document.addEventListener('DOMContentLoaded', function() {
    console.log("Running short passage listening format fix...");
    
    // Override the processListeningQuestion function to handle both dialogue and passage types
    const originalProcessListeningQuestion = window.processListeningQuestion;
    window.processListeningQuestion = function(stem) {
        console.log("Enhanced processListeningQuestion running for: ", stem.substring(0, 30) + "...");
        
        // Clean up number prefix if present
        stem = stem.replace(/^\d+．\s*/, '');
        
        // Check if this is a listening question (including both long dialogue and short passage)
        if (stem.includes('听下面一段较长对话') || 
            stem.includes('听录音') || 
            stem.includes('听下面一段独白') || 
            stem.includes('听下列独白') || 
            stem.includes('听短文') || 
            stem.includes('听独白') ||
            stem.includes('听短文选答案')) {
            
            // This is a complete listening question with multiple sub-questions
            console.log("Formatting complete listening question (dialogue or passage)");
            return formatMultiListeningQuestion(stem);
        }
        
        // Use original function for other cases
        if (typeof originalProcessListeningQuestion === 'function') {
            return originalProcessListeningQuestion(stem);
        }
        
        // Fallback if original function doesn't exist
        const questionPattern = /(What|Why|When|How|Who|Where|Which).*?\?/;
        const match = stem.match(questionPattern);
        
        if (match) {
            return match[0];
        }
        
        return stem.replace(/Listen to the recording.*?\./i, '').trim();
    };
    
    // Override the formatMultiListeningQuestion function to handle both dialogue and passage types
    const originalFormatMultiListeningQuestion = window.formatMultiListeningQuestion;
    window.formatMultiListeningQuestion = function(questionText) {
        console.log("格式化多题听力问题", questionText.substring(0, 50) + "...");
        
        // 检查是否包含短文或对话
        const isShortPassage = questionText.includes('听下面一段短文') || 
                               questionText.includes('听下面一段较长对话') || 
                               questionText.includes('听下面一段独白');
        
        if (!isShortPassage) {
            // 如果不是短文或对话，直接返回原始文本
            return questionText;
        }
        
        try {
            // 提取标题（如：听下面一段短文，回答以下小题。）
            let titleMatch = questionText.match(/(听下面一段.*?)[，。]/);
            let title = titleMatch ? titleMatch[0] : '';
            
            console.log("题目标题:", title);
            
            // 提取所有英文问题
            const englishQuestions = questionText.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || [];
            console.log("英语问题数量:", englishQuestions.length);
            
            if (englishQuestions.length === 0) {
                // 找不到英文问题，返回原始文本
                return questionText;
            }
            
            // 构建HTML输出
            let html = `<div class="listening-question">
                <div class="listening-title">${title}</div>
                <div class="listening-subquestions">`;
            
            // 处理每个问题
            for (let i = 0; i < englishQuestions.length; i++) {
                const question = englishQuestions[i];
                console.log(`处理问题 ${i+1}:`, question);
                
                // 查找问题在原文中的位置
                const questionPos = questionText.indexOf(question);
                
                if (questionPos === -1) continue;
                
                // 查找问题后的选项
                const optionsMatch = questionText.substring(questionPos + question.length)
                    .match(/A[\s\.．]+(.*?)(?:B[\s\.．]+(.*?)(?:C[\s\.．]+(.*?))?)?(?:\n|$)/s);
                
                if (!optionsMatch) {
                    console.log(`问题 ${i+1} 未找到选项`);
                    
                    // 查找后续文本中的任何选项块
                    const remainingText = questionText.substring(questionPos + question.length);
                    const laterOptionsMatch = remainingText.match(/A[\s\.．]+(.*?)B[\s\.．]+(.*?)C[\s\.．]+(.*?)(?:\n|$)/s);
                    
                    if (laterOptionsMatch) {
                        // 找到了选项，但它们可能不直接跟在问题后面
                        html += `<div class="listening-subquestion">
                            <div class="question-text">${question}（  ）</div>
                            <div class="options">
                                <div class="option">A．${laterOptionsMatch[1].trim()}</div>
                                <div class="option">B．${laterOptionsMatch[2].trim()}</div>
                                <div class="option">C．${laterOptionsMatch[3].trim()}</div>
                            </div>
                        </div>`;
                        console.log(`为问题 ${i+1} 找到了延迟的选项`);
                    } else {
                        // 真的找不到选项，只显示问题
                        html += `<div class="listening-subquestion">
                            <div class="question-text">${question}（  ）</div>
                            <div class="options">选项未找到</div>
                        </div>`;
                    }
                } else {
                    // 有选项，构建正常的问题和选项显示
                    html += `<div class="listening-subquestion">
                        <div class="question-text">${question}（  ）</div>
                        <div class="options">
                            <div class="option">A．${optionsMatch[1] ? optionsMatch[1].trim() : ''}</div>`;
                    
                    if (optionsMatch[2]) {
                        html += `<div class="option">B．${optionsMatch[2].trim()}</div>`;
                    }
                    
                    if (optionsMatch[3]) {
                        html += `<div class="option">C．${optionsMatch[3].trim()}</div>`;
                    }
                    
                    html += `</div></div>`;
                    console.log(`问题 ${i+1} 选项处理完成`);
                }
            }
            
            html += `</div></div>`;
            
            // 添加样式
            html += `<style>
                .listening-question {
                    margin-bottom: 15px;
                    font-size: 16px;
                }
                .listening-title {
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .listening-subquestions {
                    margin-left: 20px;
                }
                .listening-subquestion {
                    margin-bottom: 15px;
                }
                .question-text {
                    margin-bottom: 5px;
                }
                .options {
                    margin-left: 20px;
                }
                .option {
                    margin-bottom: 3px;
                }
            </style>`;
            
            return html;
        } catch (error) {
            console.error("格式化听力题出错:", error);
            return questionText; // 出错时返回原始文本
        }
    };
    
    // Specific function to handle "听短文选答案" and "听下面一段独白" format
    function formatShortPassageListening(text) {
        console.log("formatShortPassageListening running:", text.substring(0, 30) + "...");
        
        // Clean up number prefix if present
        text = text.replace(/^\d+[．,.、]\s*/, '');
        
        // 提取题目前导部分，并修复序号格式
        let title = '';
        let questionNum = '';
        
        // 查找序号，如 "1、" 或 "1．"
        const numMatch = text.match(/^(\d+)[、．\.]/);
        if (numMatch) {
            questionNum = numMatch[1] + '、';
        }
        
        // Extract title
        const titleMatch = text.match(/(听下面一段独白|听下列独白|听短文|听独白|听短文选答案).*?[，|。]/);
        title = titleMatch ? titleMatch[0] : '听下面一段独白，回答以下小题。';
        
        // Make sure the title has proper punctuation
        if (!title.includes('回答以下小题')) {
            title = title.replace(/[，|。]$/, '，回答以下小题。');
        }
        
        // 确保标题的开头有序号
        if (questionNum && !title.startsWith(questionNum)) {
            title = questionNum + title;
        }
        
        // Extract all English questions
        const questions = text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || [];
        console.log("Found questions:", questions.length, questions);
        
        if (questions.length === 0) {
            console.error("No English questions found in text");
            return text;
        }
        
        // Generate HTML with strict formatting according to example
        let formattedHTML = `<div class="listening-question-container" style="margin-bottom:24px;">
            <div class="listening-title" style="font-weight:bold;margin-bottom:16px;font-size:16px;color:#000;">${title}</div>`;
        
        // Split text into blocks, each containing one question and its options
        let questionBlocks = [];
        for (let i = 0; i < questions.length; i++) {
            const question = questions[i];
            const startPos = text.indexOf(question);
            const endPos = i < questions.length - 1 ? text.indexOf(questions[i+1]) : text.length;
            
            if (startPos >= 0 && endPos > startPos) {
                // Extract this question and its options block
                const block = text.substring(startPos, endPos).trim();
                questionBlocks.push(block);
            }
        }
        
        console.log("Question blocks:", questionBlocks.length);
        
        // Process each question block with updated styling
        for (let i = 0; i < questionBlocks.length; i++) {
            const block = questionBlocks[i];
            const question = questions[i];
            
            // Extract options from text after the question
            const optionsText = block.substring(question.length);
            console.log(`Question ${i+1} options text:`, optionsText.substring(0, Math.min(50, optionsText.length)));
            
            // Try to match A, B, C options
            const optionA = optionsText.match(/A[\s\.．](.*?)(?=B[\s\.．]|$)/s);
            const optionB = optionsText.match(/B[\s\.．](.*?)(?=C[\s\.．]|$)/s);
            const optionC = optionsText.match(/C[\s\.．](.*?)(?=$)/s);
            
            // Log extracted options for debugging
            console.log(`Options for question ${i+1}:`, 
                        optionA ? optionA[1].trim() : 'None',
                        optionB ? optionB[1].trim() : 'None',
                        optionC ? optionC[1].trim() : 'None');
            
            // Build options HTML with strict formatting
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
            
            // Add question and options with improved spacing and styling
            formattedHTML += `
                <div class="listening-subquestion" style="margin-bottom:15px">
                    <div class="question-text" style="margin-bottom:8px;font-weight:bold;line-height:1.5">${question}</div>
                    ${optionsHTML}
                </div>
            `;
        }
        
        formattedHTML += '</div>';
        console.log("Formatted HTML created with length:", formattedHTML.length);
        return formattedHTML;
    }
    
    // Fix the rendering of questions to apply the formatting to existing questions
    setTimeout(function() {
        console.log("Applying listening formatting to existing content...");
        // Find all question content divs
        const questionContents = document.querySelectorAll('.question-content');
        console.log("Found question contents:", questionContents.length);
        
        questionContents.forEach((content, index) => {
            const text = content.textContent || '';
            
            // Check if this is a short passage or monologue that needs formatting
            if ((text.includes('听下面一段独白') || 
                 text.includes('听下列独白') || 
                 text.includes('听短文') || 
                 text.includes('听独白') || 
                 text.includes('听短文选答案')) &&
                ((text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || []).length > 0)) {
                
                console.log(`Reformatting question ${index + 1}: short passage or monologue listening question`);
                const questions = text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || [];
                console.log(`Found ${questions.length} sub-questions`);
                
                // Apply formatting for short passage or monologue
                const formattedText = formatShortPassageListening(text);
                if (formattedText) {
                    content.innerHTML = formattedText;
                    console.log(`Successfully formatted question ${index + 1}`);
                }
            }
        });
    }, 1000);
    
    // Add observer to handle dynamically loaded content
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                // Check for new question content
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // Element node
                        const contents = node.querySelectorAll ? 
                                        node.querySelectorAll('.question-content') : [];
                        
                        contents.forEach((content, index) => {
                            const text = content.textContent || '';
                            
                            // Check if this is a short passage or monologue that needs formatting
                            if ((text.includes('听下面一段独白') || 
                                 text.includes('听下列独白') || 
                                 text.includes('听短文') || 
                                 text.includes('听独白') || 
                                 text.includes('听短文选答案')) &&
                                ((text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || []).length > 0)) {
                                
                                console.log(`Reformatting dynamically added question ${index + 1}: short passage or monologue`);
                                const questions = text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || [];
                                console.log(`Found ${questions.length} sub-questions in dynamic content`);
                                
                                // Apply formatting for short passage or monologue
                                const formattedText = formatShortPassageListening(text);
                                if (formattedText) {
                                    content.innerHTML = formattedText;
                                    console.log(`Successfully formatted dynamic question ${index + 1}`);
                                }
                            }
                        });
                    }
                });
            }
        });
    });
    
    // Start observing changes to the document
    observer.observe(document.body, { childList: true, subtree: true });
});

console.log("短文/对话听力修复脚本加载完成");
