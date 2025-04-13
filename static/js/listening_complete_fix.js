// 英语听力题完整修复脚本
document.addEventListener('DOMContentLoaded', function() {
    console.log("Running English listening complete fix...");
    
    // 辅助函数：从英语听力题中移除数字序号
    function removeNumberPrefixFromListening(text) {
        if (!text) return text;
        // 移除题目开头的数字序号（如"3．"）
        return text.replace(/^\d+．\s*/g, '');
    }
    
    // 覆盖原parseQuestion函数，确保英语听力题的处理正确
    const originalParseQuestion = window.parseQuestion;
    window.parseQuestion = function(questionText) {
        // 先移除数字序号
        if (questionText && typeof questionText === 'string' && 
            (questionText.includes('听下面一段较长对话') || questionText.includes('听录音')) && 
            questionText.includes('英语')) {
            // 处理英语听力题
            questionText = removeNumberPrefixFromListening(questionText);
        }
        
        // 使用原始函数处理
        return originalParseQuestion(questionText);
    };
    
    // 确保stem变量始终有值
    window.renderQuestions = (function() {
        const originalRenderQuestions = window.renderQuestions;
        return function(questions) {
            try {
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
});
