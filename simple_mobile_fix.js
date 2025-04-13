// 从localStorage恢复已选题目
function restoreSelectedQuestions() {
    try {
        const savedQuestions = localStorage.getItem("selectedQuestions");
        if (savedQuestions) {
            const questionIds = JSON.parse(savedQuestions);
            questionIds.forEach(id => selectedQuestions.add(parseInt(id)));
            console.log("从localStorage恢复已选题目:", selectedQuestions.size);
        }
    } catch (error) {
        console.error("恢复已选题目出错:", error);
    }
}

// 保存已选题目到localStorage
function saveSelectedQuestions() {
    try {
        const questionIds = Array.from(selectedQuestions);
        localStorage.setItem("selectedQuestions", JSON.stringify(questionIds));
        console.log("保存题目到localStorage:", questionIds.length);
    } catch (error) {
        console.error("保存已选题目出错:", error);
    }
}

// 在DOMContentLoaded事件中调用恢复函数
document.addEventListener('DOMContentLoaded', function() {
    // 从localStorage恢复已选题目
    restoreSelectedQuestions();
    
    // 在选择题目时保存到localStorage
    const container = document.getElementById('questionCards');
    if (container) {
        container.addEventListener('click', function(e) {
            if (e.target.classList.contains('select-btn')) {
                // 在选择后保存
                setTimeout(saveSelectedQuestions, 100);
            }
        });
    }
    
    // 重写toggleSelect函数
    const originalToggleSelect = window.toggleSelect;
    window.toggleSelect = function(questionId) {
        // 调用原始函数
        originalToggleSelect(questionId);
        // 保存到localStorage
        saveSelectedQuestions();
    };
    
    // 重写clearSelectedQuestions函数
    const originalClearSelectedQuestions = window.clearSelectedQuestions;
    window.clearSelectedQuestions = function() {
        // 调用原始函数
        originalClearSelectedQuestions();
        // 从localStorage中清除
        localStorage.removeItem("selectedQuestions");
    };
    
    // 重写generatePaper函数
    const originalGeneratePaper = window.generatePaper;
    window.generatePaper = function() {
        // 调用原始函数
        originalGeneratePaper();
        // 从localStorage中清除
        setTimeout(function() {
            localStorage.removeItem("selectedQuestions");
        }, 1000);
    };
});
