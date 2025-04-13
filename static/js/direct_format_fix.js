// 直接格式化英语听力题目
document.addEventListener('DOMContentLoaded', function() {
    console.log("Direct format fix script loaded");
    
    // 一秒后执行，确保页面内容已加载
    setTimeout(function() {
        console.log("Running direct format fix");
        applyDirectFormatting();
        
        // 监听DOM变化，处理动态加载的内容
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    applyDirectFormatting();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }, 1000);
    
    // 同时也在点击事件后应用格式化
    document.addEventListener('click', function(event) {
        // 延迟执行以确保DOM更新完成
        setTimeout(applyDirectFormatting, 500);
    });
});

// 直接在DOM中应用垂直格式
function applyDirectFormatting() {
    console.log("Applying direct formatting to listening questions");
    
    // 查找所有题目容器
    const questionContainers = document.querySelectorAll('.question-content');
    
    questionContainers.forEach(function(container) {
        // 检查是否包含听力题目特征
        const questionText = container.textContent || '';
        
        if (questionText.includes('听下面一段较长对话') && 
            (questionText.includes('What') || questionText.includes('Where') || 
             questionText.includes('Why') || questionText.includes('When') || 
             questionText.includes('How') || questionText.includes('Who'))) {
            
            console.log("Found English listening question, formatting...");
            
            // 保存原始HTML以便检查是否需要修改
            const originalHTML = container.innerHTML;
            
            // 处理英语听力题
            let formattedHTML = container.innerHTML;
            
            // 为所有英文字母选项添加换行
            formattedHTML = formattedHTML.replace(/([A-C][\s\.．](?!In|It|Eating|Attending|Ordering))/g, '<br>$1');
            
            // 为所有问题(What, Where等)添加换行和额外空间
            formattedHTML = formattedHTML.replace(/(What|Where|Why|When|How|Who)/g, '<br><br>$1');
            
            // 修改Question结尾处
            formattedHTML = formattedHTML.replace(/\?(?=\s*[A-C])/g, '?<br>');
            
            // 只有当内容有变化时才更新DOM
            if (formattedHTML !== originalHTML) {
                container.innerHTML = formattedHTML;
                console.log("Question formatted successfully");
            }
        }
    });
}
