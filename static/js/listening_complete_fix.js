// 英语听力题完整修复脚本
console.log("英语听力修复脚本已加载");

document.addEventListener("DOMContentLoaded", function() {
    // 监听DOM变化，查找并处理英语听力题
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // 查找所有问题元素
                const questionElements = document.querySelectorAll('.question');
                questionElements.forEach(function(element) {
                    // 检查是否是英语听力题
                    const text = element.textContent || '';
                    if (text.includes('听下面') && 
                        (text.includes('对话') || text.includes('短文') || text.includes('独白')) &&
                        text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g)) {
                        
                        console.log("找到英语听力题，开始处理");
                        const formattedText = parseQuestion(text);
                        if (formattedText !== text) {
                            element.innerHTML = formattedText;
                        }
                    }
                });
            }
        });
    });

    // 解析问题文本，提取出子问题和选项
    function parseQuestion(text) {
        console.log("解析英语听力题:", text.substring(0, 50) + "...");
        
        // 检查是否包含英语听力题标识
        if (!text.includes('听下面') || 
            !(text.includes('对话') || text.includes('短文') || text.includes('独白'))) {
            return text;
        }
        
        try {
            // 提取标题（如：听下面一段对话，回答以下小题。）
            let titleMatch = text.match(/(听下面一段.*?)[，。]/);
            let title = titleMatch ? titleMatch[0] : '';
            if (!title.endsWith('。')) {
                title += '，回答以下小题。';
            }
            
            console.log("题目标题:", title);
            
            // 移除题号前缀
            text = text.replace(/^\d+[、．\.]\s*/, '');
            
            // 提取所有英文问题
            const englishQuestions = text.match(/(What|Why|When|How|Who|Where|Which).*?\?/g) || [];
            console.log("找到英语问题数量:", englishQuestions.length);
            
            if (englishQuestions.length === 0) {
                return text;
            }
            
            // 处理每个问题及其选项
            let processedQuestions = [];
            for (let i = 0; i < englishQuestions.length; i++) {
                const question = englishQuestions[i];
                console.log(`处理问题 ${i+1}:`, question);
                
                // 查找问题在原文中的位置
                const questionPos = text.indexOf(question);
                if (questionPos === -1) continue;
                
                let options = {A: '', B: '', C: ''};
                let foundOptions = false;
                
                // 查找问题后的选项
                const afterQuestionText = text.substring(questionPos + question.length);
                const directOptionsMatch = afterQuestionText.match(/A[\s\.．]+(.*?)B[\s\.．]+(.*?)C[\s\.．]+(.*?)(?:\n|(?=What|Why|When|How|Who|Where|Which)|$)/s);
                
                if (directOptionsMatch) {
                    options.A = directOptionsMatch[1].trim();
                    options.B = directOptionsMatch[2].trim();
                    options.C = directOptionsMatch[3].trim();
                    foundOptions = true;
                    console.log(`问题 ${i+1} 找到直接跟随的选项`);
                } else {
                    // 如果没有直接找到选项，在剩余文本中搜索
                    const remainingText = text.substring(questionPos);
                    
                    // 查找下一个问题或文本结束之前的所有选项
                    let nextQuestionPos = text.length;
                    if (i < englishQuestions.length - 1) {
                        nextQuestionPos = text.indexOf(englishQuestions[i+1], questionPos);
                    }
                    
                    const searchText = text.substring(questionPos, nextQuestionPos);
                    
                    // 查找选项A
                    const optionA = searchText.match(/A[\s\.．]+(.*?)(?=B[\s\.．]|$)/s);
                    if (optionA) options.A = optionA[1].trim();
                    
                    // 查找选项B
                    const optionB = searchText.match(/B[\s\.．]+(.*?)(?=C[\s\.．]|$)/s);
                    if (optionB) options.B = optionB[1].trim();
                    
                    // 查找选项C
                    const optionC = searchText.match(/C[\s\.．]+(.*?)(?=$)/s);
                    if (optionC) options.C = optionC[1].trim();
                    
                    foundOptions = options.A && options.B && options.C;
                    console.log(`问题 ${i+1} 分段查找选项: A=${!!options.A}, B=${!!options.B}, C=${!!options.C}`);
                }
                
                processedQuestions.push({
                    question: question,
                    options: options,
                    foundOptions: foundOptions
                });
            }
            
            // 构建HTML输出
            let html = `<div class="listening-question">
                <div class="listening-title">${title}</div>
                <div class="listening-subquestions">`;
            
            for (const q of processedQuestions) {
                html += `<div class="listening-subquestion">
                    <div class="question-text">${q.question}（  ）</div>`;
                
                if (q.foundOptions) {
                    html += `<div class="options">
                        <div class="option">A．${q.options.A}</div>
                        <div class="option">B．${q.options.B}</div>
                        <div class="option">C．${q.options.C}</div>
                    </div>`;
                } else {
                    html += `<div class="options">
                        <div class="option">A．${q.options.A || '选项未找到'}</div>
                        <div class="option">B．${q.options.B || '选项未找到'}</div>
                        <div class="option">C．${q.options.C || '选项未找到'}</div>
                    </div>`;
                }
                
                html += `</div>`;
            }
            
            html += `</div></div>`;
            
            // 添加样式
            html += `<style>
                .listening-question {
                    margin-bottom: 20px;
                    font-size: 16px;
                }
                .listening-title {
                    font-weight: bold;
                    margin-bottom: 15px;
                }
                .listening-subquestions {
                    margin-left: 20px;
                }
                .listening-subquestion {
                    margin-bottom: 15px;
                }
                .question-text {
                    margin-bottom: 8px;
                    font-weight: bold;
                }
                .options {
                    margin-left: 20px;
                }
                .option {
                    margin-bottom: 5px;
                    line-height: 1.5;
                }
            </style>`;
            
            return html;
        } catch (error) {
            console.error("解析英语听力题出错:", error);
            return text;
        }
    }

    // 开始观察DOM变化
    observer.observe(document.body, { childList: true, subtree: true });
    console.log("英语听力题监听器已启动");
});

console.log("英语听力修复脚本加载完成");
