// Vertical format for English listening questions
document.addEventListener('DOMContentLoaded', function() {
    console.log("Running vertical listening format script...");
    
    // 直接重写DOM中现有的听力题内容
    function formatAllListeningQuestions() {
        console.log("Formatting all listening questions to vertical layout");
        
        // 查找页面中的所有听力题容器
        const listeningContainers = document.querySelectorAll('.listening-question-container');
        if (listeningContainers.length > 0) {
            console.log(`Found ${listeningContainers.length} listening question containers`);
            
            listeningContainers.forEach(container => {
                // 查找选项容器
                const optionsContainers = container.querySelectorAll('.listening-options');
                
                optionsContainers.forEach(optionsDiv => {
                    // 改变样式为垂直布局
                    optionsDiv.className = 'listening-options-vertical';
                    optionsDiv.style.display = 'flex';
                    optionsDiv.style.flexDirection = 'column';
                    optionsDiv.style.alignItems = 'flex-start';
                    optionsDiv.style.marginBottom = '15px';
                    
                    // 调整每个选项的样式
                    const options = optionsDiv.querySelectorAll('.listening-option');
                    options.forEach(option => {
                        option.className = 'option-line';
                        option.style.marginBottom = '10px';
                        option.style.width = '100%';
                        option.style.flex = 'none'; // 移除 flex: 1
                    });
                });
            });
            
            console.log("Vertical formatting completed");
        } else {
            console.log("No listening question containers found. Will try again later.");
            // 如果没有找到，稍后再尝试（页面可能仍在加载）
            setTimeout(formatAllListeningQuestions, 1000);
        }
    }
    
    // 初始执行
    setTimeout(formatAllListeningQuestions, 2000);
    
    // 每当页面内容变化时重新应用格式
    // 使用MutationObserver监听DOM变化
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                // 发现新节点，检查是否需要重新格式化
                setTimeout(formatAllListeningQuestions, 500);
            }
        });
    });
    
    // 开始观察文档体的变化
    observer.observe(document.body, { childList: true, subtree: true });
});
