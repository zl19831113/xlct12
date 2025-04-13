// 简单的分页修复
(function() {
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('分页修复脚本已加载');
        
        // 拦截所有分页链接的点击事件
        function setupPaginationLinks() {
            // 查找所有分页链接
            const paginationLinks = document.querySelectorAll('.pagination-button, #prevPage, #nextPage');
            
            paginationLinks.forEach(link => {
                // 移除现有的点击事件
                const newLink = link.cloneNode(true);
                if (link.parentNode) {
                    link.parentNode.replaceChild(newLink, link);
                }
                
                // 添加新的点击事件
                newLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // 获取页码
                    let pageNum = 1;
                    if (this.id === 'prevPage') {
                        const currentPage = parseInt(new URLSearchParams(window.location.search).get('page') || '1');
                        pageNum = Math.max(1, currentPage - 1);
                    } else if (this.id === 'nextPage') {
                        const currentPage = parseInt(new URLSearchParams(window.location.search).get('page') || '1');
                        pageNum = currentPage + 1;
                    } else {
                        pageNum = parseInt(this.getAttribute('data-page') || '1');
                    }
                    
                    // 构建新URL，保留所有筛选参数
                    const urlParams = new URLSearchParams(window.location.search);
                    urlParams.set('page', pageNum);
                    
                    // 获取所有筛选标签
                    const filterTags = document.querySelectorAll('.filter-tag');
                    filterTags.forEach(tag => {
                        const filterType = tag.getAttribute('data-type');
                        const filterValue = tag.getAttribute('data-value');
                        if (filterType && filterValue) {
                            urlParams.set(filterType, filterValue);
                        }
                    });
                    
                    // 跳转到新URL
                    const newUrl = `/papers?${urlParams.toString()}`;
                    console.log('跳转到:', newUrl);
                    window.location.href = newUrl;
                });
            });
            
            console.log('已设置', paginationLinks.length, '个分页链接');
        }
        
        // 初始设置
        setupPaginationLinks();
        
        // 每秒检查一次，确保动态加载的分页链接也被处理
        setInterval(setupPaginationLinks, 1000);
    });
})();
