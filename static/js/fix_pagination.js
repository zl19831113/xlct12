/**
 * 分页修复脚本 - 确保在分页导航时保留所有筛选条件
 * 版本: 1.0.0
 * 日期: 2025-04-02
 */
(function() {
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('分页修复脚本已加载');
        
        // 用于存储所有筛选条件
        window.selectedFilters = window.selectedFilters || {};
        
        // 从URL中获取当前筛选条件
        const urlParams = new URLSearchParams(window.location.search);
        const filterParams = ['region', 'subject', 'stage', 'source_type', 'source', 'year', 'keyword'];
        
        // 初始化筛选条件
        filterParams.forEach(param => {
            const value = urlParams.get(param);
            if (value) {
                window.selectedFilters[param] = value;
            }
        });
        
        // 带有所有筛选条件的页面导航函数
        window.navigateWithAllFilters = function(pageNum) {
            // 获取当前URL参数
            const params = new URLSearchParams(window.location.search);
            
            // 更新页码
            params.set('page', pageNum);
            
            // 添加已保存的筛选条件
            for (const [key, value] of Object.entries(window.selectedFilters)) {
                if (value) {
                    params.set(key, value);
                }
            }
            
            // 跳转到新页面
            window.location.href = `/papers?${params.toString()}`;
        };
        
        // 为了向后兼容
        window.navigateWithFilters = window.navigateWithAllFilters;
        
        // 增强分页按钮功能
        function enhancePaginationButtons() {
            // 处理前一页和后一页按钮
            const prevButton = document.getElementById('prevPage');
            if (prevButton) {
                prevButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    const currentPage = parseInt(urlParams.get('page') || '1');
                    if (currentPage > 1) {
                        navigateWithAllFilters(currentPage - 1);
                    }
                });
            }
            
            const nextButton = document.getElementById('nextPage');
            if (nextButton) {
                nextButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    const currentPage = parseInt(urlParams.get('page') || '1');
                    navigateWithAllFilters(currentPage + 1);
                });
            }
            
            // 处理分页数字按钮
            const paginationButtons = document.querySelectorAll('.pagination-button');
            paginationButtons.forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const pageNum = this.getAttribute('data-page') || 
                                   this.textContent.trim();
                    navigateWithAllFilters(pageNum);
                });
            });
        }
        
        // 增强筛选按钮功能
        function enhanceFilterButtons() {
            const filterButtons = document.querySelectorAll('.filter-btn');
            filterButtons.forEach(button => {
                const originalOnclick = button.onclick;
                
                button.onclick = function(e) {
                    // 获取筛选类型和值
                    const filterType = this.getAttribute('data-filter-type');
                    const filterValue = this.getAttribute('data-filter-value');
                    
                    // 保存筛选条件
                    if (filterType && filterValue) {
                        window.selectedFilters[filterType] = filterValue;
                    }
                    
                    // 调用原始点击事件
                    if (typeof originalOnclick === 'function') {
                        return originalOnclick.call(this, e);
                    }
                };
            });
        }
        
        // 增强搜索功能
        function enhanceSearchButton() {
            const searchButton = document.getElementById('searchButton');
            const searchInput = document.getElementById('searchInput');
            
            if (searchButton && searchInput) {
                const originalOnclick = searchButton.onclick;
                
                searchButton.onclick = function(e) {
                    // 保存关键词
                    const keyword = searchInput.value.trim();
                    if (keyword) {
                        window.selectedFilters.keyword = keyword;
                    }
                    
                    // 调用原始点击事件
                    if (typeof originalOnclick === 'function') {
                        return originalOnclick.call(this, e);
                    }
                };
            }
        }
        
        // 增强changePage函数
        if (typeof window.changePage === 'function') {
            const originalChangePage = window.changePage;
            window.changePage = function(direction) {
                const currentPage = parseInt(urlParams.get('page') || '1');
                navigateWithAllFilters(currentPage + direction);
                return false;
            };
        }
        
        // 增强goToPage函数
        if (typeof window.goToPage === 'function') {
            const originalGoToPage = window.goToPage;
            window.goToPage = function(pageNum) {
                navigateWithAllFilters(pageNum);
                return false;
            };
        }
        
        // 初始化
        enhancePaginationButtons();
        enhanceFilterButtons();
        enhanceSearchButton();
        
        console.log('分页修复脚本初始化完成');
    });
})(); 