// 清空文件内容，只保留必要的事件监听
document.addEventListener('DOMContentLoaded', function() {
    // 可添加通用表单验证逻辑
    document.querySelector('form')?.addEventListener('submit', function(e) {
        const requiredFields = this.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = 'red';
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('请填写所有必填字段（标红项）');
        }
    });
});

function formatQuestionText(text) {
    if (!text) return '';

    // 检查内容是否已经包含HTML结构（特别是我们的CSS类）
    if (text.includes('class="question-wrapper"') || 
        text.includes('class="options-container"') || 
        text.includes('class="answer-options"')) {
        // 内容已经有了结构化的HTML和CSS类，直接返回不做处理
        return text;
    }

    // 以下为处理纯文本的逻辑，仅在没有HTML结构时执行
    // 1) 清理文本
    text = text.replace(/[\r\n]+/g, ' ')
               .replace(/\s+/g, ' ')
               .trim();

    // 2) 查找题干（通常以"（ ）"结束）
    let stem = text;
    let options = '';

    const stemMatch = text.match(/(.*?)\s*（\s*）/);
    if (stemMatch) {
        stem = stemMatch[1] + "（ ）";
        options = text.substring(stemMatch[0].length).trim();
    } else {
        // 没有找到"（ ）"，尝试找第一个编号选项的位置
        const firstNumbered = text.match(/[①②③④⑤]/);
        if (firstNumbered) {
            stem = text.substring(0, firstNumbered.index).trim();
            options = text.substring(firstNumbered.index).trim();
        } else {
            // 没有编号选项，尝试找第一个字母选项
            const firstLetter = text.match(/[A-D][．.、]/);
            if (firstLetter) {
                stem = text.substring(0, firstLetter.index).trim();
                options = text.substring(firstLetter.index).trim();
            }
        }
    }

    // 3) 处理编号选项（①②③④）
    const numberedOptions = options.match(/[①②③④⑤][^①②③④⑤A-D]*(?=[①②③④⑤A-D]|$)/g);
    if (numberedOptions) {
        let html = '<div class="question-wrapper">';
        html += `<div class="question-content">${stem}</div>`;
        html += '<div class="options-container">';
        numberedOptions.forEach(option => {
            html += `<div class="option-item">${option.trim()}</div>`;
        });
        html += '</div>';
        
        // 查找字母选项
        const letterOptionsPart = options.substring(options.lastIndexOf(numberedOptions[numberedOptions.length - 1]) + numberedOptions[numberedOptions.length - 1].length).trim();
        if (letterOptionsPart) {
            const letterOptions = letterOptionsPart.match(/[A-D][．.、].*?(?=[A-D][．.、]|$)/g);
            if (letterOptions) {
                html += '<div class="answer-options">';
                letterOptions.forEach(option => {
                    html += `<div class="answer-option">${option.trim()}</div>`;
                });
                html += '</div>';
            }
        }
        
        html += '</div>';
        return html;
    }

    // 为没有编号选项的普通题目创建简单结构
    let html = '<div class="question-wrapper">';
    html += `<div class="question-content">${stem}</div>`;
    
    if (options) {
        html += '<div class="answer-options">';
        const letterOptions = options.match(/[A-D][．.、].*?(?=[A-D][．.、]|$)/g) || [];
        letterOptions.forEach(option => {
            html += `<div class="answer-option">${option.trim()}</div>`;
        });
        html += '</div>';
    }
    
    html += '</div>';
    return html;
}

function formatAnswerText(text) {
    if (!text) return '';

    // 1) 清理文本
    text = text.replace(/[\r\n]+/g, ' ')
               .replace(/\s+/g, ' ')
               .trim();

    // 2) 提取答案和解析
    const answerMatch = text.match(/^(?:\d+[.．]\s*)?([A-Z])\b(.*)/);
    if (!answerMatch) return text;

    const [, answer, explanation] = answerMatch;
    let cleanExplanation = explanation.trim();

    // 3) 处理【详解】标记
    if (!cleanExplanation.startsWith('【详解】')) {
        cleanExplanation = '【详解】 ' + cleanExplanation;
    }

    // 4) 格式化输出
    return `
        <div class="answer-option">答案：${answer}</div>
        <div class="answer-explanation">${cleanExplanation}</div>
    `;
}

// 在表格中显示题目
function displayQuestions(questions) {
    const tbody = document.querySelector('#questionTable tbody');
    tbody.innerHTML = '';
    
    questions.forEach((q, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <input type="checkbox" class="question-checkbox" data-id="${q.id}">
            </td>
            <td>${q.id}</td>
            <td>${q.subject || ''}</td>
            <td>${q.questionType || ''}</td>
            <td>${q.textbook || ''}</td>
            <td>${q.chapter || ''}</td>
            <td>${q.unit || ''}</td>
            <td>${q.lesson || ''}</td>
            <td>
                <div class="question-content">${formatQuestionText(q.question) || ''}</div>
            </td>
            <td>
                ${q.has_question_image ? 
                    `<img src="${q.question_image_url}" style="max-width:100px;">` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
}