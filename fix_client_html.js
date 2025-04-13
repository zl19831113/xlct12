// 修复Client.html中的HTML实体和组卷顺序问题
(function() {
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('修复Client.html中的问题');
        
        // 1. 修复HTML实体显示问题
        function fixHtmlEntities() {
            // 查找所有包含文本的元素
            const textElements = document.querySelectorAll('.question-text, .question-content, .answer-content, p, span, div');
            
            // 替换HTML实体
            textElements.forEach(element => {
                // 处理&middot;实体
                if (element.innerHTML && element.innerHTML.includes('&middot;')) {
                    element.innerHTML = element.innerHTML.replace(/&middot;/g, '·');
                    console.log('已替换元素中的&middot;实体');
                }
                
                // 处理可能的其他HTML实体
                if (element.innerHTML && element.innerHTML.includes('&')) {
                    element.innerHTML = element.innerHTML
                        .replace(/&nbsp;/g, ' ')
                        .replace(/&lt;/g, '<')
                        .replace(/&gt;/g, '>')
                        .replace(/&amp;/g, '&')
                        .replace(/&quot;/g, '"')
                        .replace(/&#39;/g, "'");
                    console.log('已替换元素中的其他HTML实体');
                }
            });
        }
        
        // 2. 修复组卷顺序问题
        function fixPaperGenerationOrder() {
            // 如果存在generatePaper函数，拦截并修改它
            if (typeof window.generatePaper === 'function') {
                const originalGeneratePaper = window.generatePaper;
                
                window.generatePaper = function() {
                    // 在发送请求前先处理题目顺序
                    try {
                        // 获取所有已选题目
                        let questionIds = Array.from(selectedQuestions);
                        console.log('原始顺序的题目IDs:', questionIds);
                        
                        // 获取题目类型信息
                        let questionTypes = {};
                        let questionSelectionOrder = {};
                        
                        // 遍历DOM获取题目类型和选择顺序
                        questionIds.forEach((id, index) => {
                            const questionElement = document.querySelector(`.question-card[data-question-id="${id}"]`);
                            if (questionElement) {
                                // 检查是否为选择题
                                const isObjective = questionElement.querySelector('.question-text')?.textContent.includes('选择') || 
                                                   questionElement.querySelector('.question-type')?.textContent.includes('选择');
                                
                                questionTypes[id] = isObjective ? 'objective' : 'subjective';
                                
                                // 记录选择顺序
                                questionSelectionOrder[id] = index;
                            }
                        });
                        
                        // 按照题目类型和选择顺序重新排序
                        questionIds.sort((a, b) => {
                            // 首先按题目类型排序（选择题在前）
                            if (questionTypes[a] === 'objective' && questionTypes[b] === 'subjective') {
                                return -1;
                            }
                            if (questionTypes[a] === 'subjective' && questionTypes[b] === 'objective') {
                                return 1;
                            }
                            
                            // 如果类型相同，按照选择顺序排序
                            return questionSelectionOrder[a] - questionSelectionOrder[b];
                        });
                        
                        console.log('重新排序后的题目IDs:', questionIds);
                        
                        // 覆盖原有的selectedQuestions
                        const titleInput = document.getElementById('paperTitleInput');
                        const paperTitle = titleInput.value.trim() || '我的试卷';
                        
                        document.getElementById('paperTitleModal').style.display = 'none';
                        titleInput.value = '';
                        
                        // 使用重新排序后的题目ID数组
                        fetch('/generate_paper', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                question_ids: questionIds,
                                paper_title: paperTitle
                            })
                        })
                        .then(response => {
                            if (!response.ok) throw new Error('生成试卷失败');
                            return response.blob();
                        })
                        .then(blob => {
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = paperTitle + '.docx';
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            a.remove();
                            
                            // 下载成功后清空已选题目
                            selectedQuestions.clear();
                            updateDownloadPanel();
                            
                            // 从localStorage中也清除
                            localStorage.removeItem(STORAGE_KEY);
                            
                            // 更新题目渲染状态，清除选中标记
                            const selectedButtons = document.querySelectorAll('.select-btn.selected');
                            selectedButtons.forEach(btn => {
                                btn.classList.remove('selected');
                                // 恢复按钮文本
                                btn.innerHTML = '<span class="btn-text">组卷</span>';
                            });
                        })
                        .catch(error => {
                            alert('生成试卷失败：' + error.message);
                        });
                        
                        // 阻止原始函数执行
                        return false;
                    } catch (error) {
                        console.error('排序题目时出错:', error);
                        // 出错时回退到原始函数
                        return originalGeneratePaper();
                    }
                };
                
                console.log('已增强generatePaper函数，修复了组卷顺序问题');
            }
        }
        
        // 首次执行修复
        fixHtmlEntities();
        fixPaperGenerationOrder();
        
        // 每2秒执行一次HTML实体修复，确保动态加载的内容也被处理
        setInterval(fixHtmlEntities, 2000);
    });
})(); 