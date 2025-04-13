// 简单的localStorage修复
(function() {
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('localStorage修复脚本已加载');
        
        // 确保selectedQuestions已定义
        if (typeof window.selectedQuestions === 'undefined') {
            window.selectedQuestions = new Set();
            console.log('创建了selectedQuestions集合');
        }
        
        // 从localStorage恢复已选题目
        try {
            const savedQuestions = localStorage.getItem('selectedQuestions');
            if (savedQuestions) {
                const questionIds = JSON.parse(savedQuestions);
                questionIds.forEach(id => window.selectedQuestions.add(parseInt(id)));
                console.log('从localStorage恢复已选题目:', window.selectedQuestions.size);
                
                // 更新UI
                if (typeof window.updateDownloadPanel === 'function') {
                    window.updateDownloadPanel();
                }
            }
        } catch (error) {
            console.error('恢复已选题目出错:', error);
        }
        
        // 保存已选题目到localStorage的函数
        window.saveSelectedQuestions = function() {
            try {
                const questionIds = Array.from(window.selectedQuestions);
                localStorage.setItem('selectedQuestions', JSON.stringify(questionIds));
                console.log('保存题目到localStorage:', questionIds.length);
            } catch (error) {
                console.error('保存已选题目出错:', error);
            }
        };
        
        // 拦截toggleSelect函数
        if (typeof window.toggleSelect === 'function') {
            const originalToggleSelect = window.toggleSelect;
            window.toggleSelect = function(questionId) {
                // 调用原始函数
                originalToggleSelect(questionId);
                // 保存到localStorage
                window.saveSelectedQuestions();
            };
            console.log('已增强toggleSelect函数');
        }
        
        // 拦截clearSelectedQuestions函数
        if (typeof window.clearSelectedQuestions === 'function') {
            const originalClearSelectedQuestions = window.clearSelectedQuestions;
            window.clearSelectedQuestions = function() {
                // 调用原始函数
                originalClearSelectedQuestions();
                // 从localStorage中清除
                localStorage.removeItem('selectedQuestions');
                console.log('已清除localStorage中的selectedQuestions');
            };
            console.log('已增强clearSelectedQuestions函数');
        }
        
        // 拦截generatePaper函数
        if (typeof window.generatePaper === 'function') {
            const originalGeneratePaper = window.generatePaper;
            window.generatePaper = function() {
                // 调用原始函数
                originalGeneratePaper();
                // 从localStorage中清除
                localStorage.removeItem('selectedQuestions');
                console.log('生成试卷后已清除localStorage中的selectedQuestions');
            };
            console.log('已增强generatePaper函数');
        }
        
        // 为所有选择按钮添加点击事件
        setTimeout(function() {
            const selectButtons = document.querySelectorAll('.select-btn');
            selectButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    // 保存到localStorage
                    setTimeout(window.saveSelectedQuestions, 100);
                });
            });
            console.log('已为', selectButtons.length, '个选择按钮添加点击事件');
        }, 1000);
    });
})();
