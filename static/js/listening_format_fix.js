// English listening comprehension formatting fix
document.addEventListener('DOMContentLoaded', function() {
    console.log("Running English listening format fix...");
    
    // Override the formatMultiListeningQuestion function for better formatting
    const originalFormatMultiListeningQuestion = window.formatMultiListeningQuestion;
    window.formatMultiListeningQuestion = function(text) {
        // 检查是否是英语听力长对话
        if ((text.includes('听下面一段较长对话') || text.includes('听录音')) && 
            text.includes('小题') && 
            (text.includes('What') || text.includes('Where') || 
             text.includes('Why') || text.includes('When') || 
             text.includes('How') || text.includes('Who'))) {
            
            console.log("Converting English listening question to image format");
            
            // 转换为图片格式展示
            return createListeningQuestionImage(text);
        }
        
        // 如果不是英语听力长对话，使用原始函数处理
        if (typeof originalFormatMultiListeningQuestion === 'function') {
            return originalFormatMultiListeningQuestion(text);
        }
        
        // 如果原始函数不存在，提供基本处理
        return text;
    };
    
    // 创建听力题图片格式展示
    function createListeningQuestionImage(text) {
        // 创建一个包含听力题内容的div
        const container = document.createElement('div');
        container.className = 'listening-question-container';
        container.style.cssText = `
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            font-family: 'Times New Roman', serif;
            line-height: 1.5;
        `;
        
        // 分割听力题内容
        const parts = text.split(/(?=\d+[、，,\.．]\s*听下面一段)/);
        
        // 处理每一部分
        parts.forEach(part => {
            if (part.trim()) {
                // 识别题干和小题部分
                const stemMatch = part.match(/^(\d+[、，,\.．]\s*听下面一段.+?)(?=Where|What|Why|When|How|Who)/s);
                
                if (stemMatch) {
                    // 添加题干
                    const stemDiv = document.createElement('div');
                    stemDiv.className = 'listening-stem';
                    stemDiv.style.cssText = `
                        font-weight: bold;
                        margin-bottom: 10px;
                    `;
                    stemDiv.textContent = stemMatch[1].trim();
                    container.appendChild(stemDiv);
                    
                    // 提取所有小题
                    const questionsText = part.substring(stemMatch[0].length);
                    const questions = questionsText.split(/(?=(?:Where|What|Why|When|How|Who))/);
                    
                    // 创建小题容器
                    const questionsContainer = document.createElement('div');
                    questionsContainer.className = 'listening-subquestions';
                    questionsContainer.style.cssText = `
                        padding-left: 15px;
                    `;
                    
                    // 处理每个小题
                    questions.forEach(question => {
                        if (question.trim()) {
                            // 分割问题和选项
                            const questionParts = question.split(/(?=A[\s\.．]|B[\s\.．]|C[\s\.．])/);
                            
                            if (questionParts.length > 0) {
                                // 添加问题
                                const questionDiv = document.createElement('div');
                                questionDiv.className = 'listening-question';
                                questionDiv.style.cssText = `
                                    margin-bottom: 8px;
                                `;
                                questionDiv.textContent = questionParts[0].trim();
                                questionsContainer.appendChild(questionDiv);
                                
                                // 添加选项
                                if (questionParts.length > 1) {
                                    const optionsDiv = document.createElement('div');
                                    optionsDiv.className = 'listening-options-vertical';
                                    optionsDiv.style.cssText = `
                                        display: flex;
                                        flex-direction: column;
                                        align-items: flex-start;
                                        margin-bottom: 15px;
                                    `;
                                    
                                    // 处理每个选项
                                    for (let i = 1; i < questionParts.length; i++) {
                                        const optionDiv = document.createElement('div');
                                        optionDiv.className = 'option-line';
                                        optionDiv.style.cssText = `
                                            margin-bottom: 10px;
                                            width: 100%;
                                        `;
                                        optionDiv.textContent = questionParts[i].trim();
                                        optionsDiv.appendChild(optionDiv);
                                    }
                                    
                                    questionsContainer.appendChild(optionsDiv);
                                }
                            }
                        }
                    });
                    
                    container.appendChild(questionsContainer);
                } else {
                    // 如果无法识别结构，直接添加文本
                    const textDiv = document.createElement('div');
                    textDiv.textContent = part.trim();
                    container.appendChild(textDiv);
                }
            }
        });
        
        // 如果是移动设备，调整样式
        if (window.innerWidth <= 768) {
            container.style.fontSize = '14px';
            container.style.padding = '10px';
        }
        
        // 返回HTML字符串
        return container.outerHTML;
    }
    
    // 修补parseQuestion函数以支持听力题图片格式
    const originalParseQuestion = window.parseQuestion;
    if (typeof originalParseQuestion === 'function') {
        window.parseQuestion = function(questionText) {
            // 检查是否是英语听力长对话
            if ((questionText.includes('听下面一段较长对话') || questionText.includes('听录音')) && 
                questionText.includes('小题') && 
                (questionText.includes('What') || questionText.includes('Where') || 
                 questionText.includes('Why') || questionText.includes('When') || 
                 questionText.includes('How') || questionText.includes('Who'))) {
                
                console.log("Special handling for English listening question");
                
                // 基本解析，将保留原始格式用于createListeningQuestionImage
                const result = {
                    stem: questionText,
                    options: [],
                    subQuestions: [],
                    originalText: questionText,
                    isListeningQuestion: true
                };
                
                return result;
            }
            
            // 对于其他题目类型，使用原始函数处理
            return originalParseQuestion(questionText);
        };
    }
    
    // 修补renderQuestions函数以正确渲染听力题
    const originalRenderQuestions = window.renderQuestions;
    if (typeof originalRenderQuestions === 'function') {
        window.renderQuestions = function(questions) {
            // 处理普通题目
            const result = originalRenderQuestions(questions);
            
            // 查找并处理所有听力题目的内容区域
            setTimeout(() => {
                document.querySelectorAll('.question-item').forEach(item => {
                    const content = item.querySelector('.question-content');
                    if (content && content.textContent.includes('听下面一段较长对话') && 
                        (content.textContent.includes('What') || content.textContent.includes('Where') || 
                         content.textContent.includes('Why') || content.textContent.includes('How') || 
                         content.textContent.includes('Who'))) {
                        
                        // 获取原始文本
                        const originalText = content.textContent;
                        
                        // 转换为图片格式
                        content.innerHTML = createListeningQuestionImage(originalText);
                    }
                });
            }, 100);
            
            return result;
        };
    }
});
