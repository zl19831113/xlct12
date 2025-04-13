// 英语听力题完整修复脚本
document.addEventListener('DOMContentLoaded', function() {
    console.log("Running enhanced English listening complete fix...");
    
    // 辅助函数：从英语听力题中移除数字序号
    function removeNumberPrefixFromListening(text) {
        if (!text) return text;
        // 移除题目开头的数字序号（如"3．"）
        return text.replace(/^\d+．\s*/g, '');
    }

    // 修复英语听力题的格式和结构
    function fixListeningQuestionFormat(text) {
        if (!text) return text;
        
        console.log("Fixing listening question format for:", text.substring(0, 50) + "...");
        
        // 处理多个题目粘连在一起的情况
        // 查找类似 "A. xxx B. xxx C. xxx D. xxx What is" 这种模式，在选项结束后添加换行
        let formattedText = text.replace(/([A-D]\..*?)(?=What|Where|Why|When|How|Who)/g, "$1\n\n");
        
        // 查找选项模式，确保每个选项单独成行
        formattedText = formattedText.replace(/([A-D])\.\s*/g, "\n$1. ");
        
        // 确保问题与选项之间有适当的空间
        formattedText = formattedText.replace(/(What|Where|Why|When|How|Who.*?\?)\s*/g, "\n$1\n");
        
        // 确保每个问题都有明确的分隔
        formattedText = formattedText.replace(/(\n[A-D]\.\s+.*?)(\n(?:What|Where|Why|When|How|Who))/g, "$1\n$2");
        
        // 修复听录音后的小题目序号
        formattedText = formattedText.replace(/(听下面.*?小题.*?)(\d+)([、．,\.])/g, "$1\n$2$3");
        
        // 处理常见听力题序号格式
        formattedText = formattedText.replace(/(\d+)([、．,\.])(\s*听下面)/g, "\n$1$2$3");
        
        console.log("Fixed format:", formattedText.substring(0, 50) + "...");
        return formattedText;
    }
    
    // 覆盖原parseQuestion函数，确保英语听力题的处理正确
    const originalParseQuestion = window.parseQuestion;
    window.parseQuestion = function(questionText) {
        // 先检查是否是英语听力题
        if (questionText && typeof questionText === 'string' && 
            ((questionText.includes('听下面') && questionText.includes('对话')) || 
             questionText.includes('听录音')) && 
            (questionText.includes('英语') || 
             questionText.includes('What') || questionText.includes('Where') || 
             questionText.includes('Why') || questionText.includes('When') || 
             questionText.includes('How') || questionText.includes('Who'))) {
            
            console.log("Processing English listening question");
            
            // 修复格式
            questionText = fixListeningQuestionFormat(questionText);
            
            // 移除数字序号
            questionText = removeNumberPrefixFromListening(questionText);
        }
        
        // 使用原始函数处理
        return originalParseQuestion(questionText);
    };
    
    // 覆盖formatMultiListeningQuestion函数
    const originalFormatMulti = window.formatMultiListeningQuestion;
    window.formatMultiListeningQuestion = function(text) {
        // 检查是否是英语听力题
        if (text && typeof text === 'string' && 
            ((text.includes('听下面') && text.includes('对话')) || 
             text.includes('听录音')) && 
            (text.includes('英语') || 
             text.includes('What') || text.includes('Where') || 
             text.includes('Why') || text.includes('When') || 
             text.includes('How') || text.includes('Who'))) {
            
            console.log("Enhanced formatting for listening question");
            text = fixListeningQuestionFormat(text);
        }
        
        // 使用原始函数处理
        if (typeof originalFormatMulti === 'function') {
            return originalFormatMulti(text);
        }
        
        return text;
    };
    
    // 确保渲染时错误处理
    window.renderQuestions = (function() {
        const originalRenderQuestions = window.renderQuestions;
        return function(questions) {
            try {
                // 对每个英语听力题进行修复处理
                if (Array.isArray(questions)) {
                    questions.forEach(q => {
                        if (q && q.question && typeof q.question === 'string' && 
                            ((q.question.includes('听下面') && q.question.includes('对话')) || 
                             q.question.includes('听录音')) && 
                            (q.subject === '英语' || q.question.includes('What') || 
                             q.question.includes('Where') || q.question.includes('Why') || 
                             q.question.includes('When') || q.question.includes('How') || 
                             q.question.includes('Who'))) {
                            
                            // 确保格式修复已应用
                            q.question = fixListeningQuestionFormat(q.question);
                        }
                    });
                }
                
                return originalRenderQuestions(questions);
            } catch (error) {
                console.error("渲染题目时出错:", error);
                // 恢复显示基本信息
                const container = document.getElementById('questionCards');
                if (container) {
                    container.innerHTML = `<div class="error-message">
                        <p>加载题目时出现错误，请刷新页面重试。</p>
                        <p>错误详情: ${error.message}</p>
                    </div>`;
                }
                return null;
            }
        };
    })();
    
    // 在DOM更新后应用修复
    setTimeout(function() {
        const questionItems = document.querySelectorAll('.question-item');
        questionItems.forEach(item => {
            const contentElement = item.querySelector('.question-content');
            if (contentElement && contentElement.textContent && 
                ((contentElement.textContent.includes('听下面') && contentElement.textContent.includes('对话')) || 
                 contentElement.textContent.includes('听录音')) && 
                (contentElement.textContent.includes('英语') || 
                 contentElement.textContent.includes('What') || contentElement.textContent.includes('Where') || 
                 contentElement.textContent.includes('Why') || contentElement.textContent.includes('When') || 
                 contentElement.textContent.includes('How') || contentElement.textContent.includes('Who'))) {
                
                console.log("Post-render fix for listening question");
                const text = contentElement.textContent;
                const fixedText = fixListeningQuestionFormat(text);
                
                // 使用格式化的HTML
                contentElement.innerHTML = fixedText
                    .replace(/\n/g, '<br>')
                    .replace(/(What|Where|Why|When|How|Who.*?\?)/g, '<strong>$1</strong>')
                    .replace(/([A-D]\.)/g, '<span class="option-letter">$1</span>');
            }
        });
    }, 500);
});
