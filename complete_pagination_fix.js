// 完整的分页和筛选修复脚本
(function() {
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('完整的分页和筛选修复脚本已加载');
        
        // 1. 替换所有服务器端分页链接
        function replacePaginationLinks() {
            // 查找所有分页链接
            const paginationLinks = document.querySelectorAll('#serverPaginationControls a.pagination-button');
            
            paginationLinks.forEach(link => {
                // 获取原始href
                const originalHref = link.getAttribute('href');
                
                // 提取页码
                const urlObj = new URL(originalHref, window.location.origin);
                const pageNum = urlObj.searchParams.get('page');
                
                // 设置data-page属性
                link.setAttribute('data-page', pageNum);
                
                // 移除href属性，防止默认导航
                link.removeAttribute('href');
                
                // 添加点击事件
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('点击分页链接，页码:', pageNum);
                    navigateWithAllFilters(pageNum);
                });
                
                console.log('替换分页链接:', originalHref, '为页码:', pageNum);
            });
        }
        
        // 2. 增强的导航函数，保留所有筛选条件
        window.navigateWithAllFilters = function(pageNum) {
            console.log('使用增强的导航函数，页码:', pageNum);
            
            // 获取当前的URL参数
            const urlParams = new URLSearchParams(window.location.search);
            
            // 设置页码
            urlParams.set('page', pageNum);
            
            // 获取所有可能的筛选参数
            const filterParams = [
                'region', 'subject', 'stage', 'source_type', 'source', 'year', 'keyword'
            ];
            
            // 保留现有的筛选参数
            filterParams.forEach(param => {
                // 从URL中获取
                const valueFromUrl = urlParams.get(param);
                if (valueFromUrl) {
                    console.log(`保留URL参数: ${param}=${valueFromUrl}`);
                }
                
                // 从selectedFilters中获取
                if (window.selectedFilters && window.selectedFilters[param]) {
                    urlParams.set(param, window.selectedFilters[param]);
                    console.log(`从selectedFilters添加: ${param}=${window.selectedFilters[param]}`);
                }
                
                // 从筛选标签中获取
                const filterTags = document.querySelectorAll('.filter-tag');
                filterTags.forEach(tag => {
                    const tagType = tag.getAttribute('data-type');
                    const tagValue = tag.getAttribute('data-value');
                    if (tagType === param && tagValue) {
                        urlParams.set(param, tagValue);
                        console.log(`从筛选标签添加: ${param}=${tagValue}`);
                    }
                });
            });
            
            // 检查搜索输入框的值
            const searchInput = document.getElementById('searchInput');
            if (searchInput && searchInput.value.trim()) {
                urlParams.set('keyword', searchInput.value.trim());
                console.log(`添加搜索关键词: keyword=${searchInput.value.trim()}`);
            }
            
            // 形成新URL并跳转
            const newUrl = `/papers?${urlParams.toString()}`;
            console.log(`跳转到新URL: ${newUrl}`);
            window.location.href = newUrl;
        };
        
        // 3. 拦截原始的分页函数
        if (typeof window.changePage === 'function') {
            const originalChangePage = window.changePage;
            window.changePage = function(direction) {
                console.log('拦截changePage函数，方向:', direction);
                
                // 获取当前页码
                const urlParams = new URLSearchParams(window.location.search);
                const currentPage = parseInt(urlParams.get('page') || '1');
                
                // 计算新页码
                const newPage = currentPage + direction;
                
                // 使用增强的导航函数
                navigateWithAllFilters(newPage);
            };
            console.log('已增强changePage函数');
        }
        
        if (typeof window.goToPage === 'function') {
            const originalGoToPage = window.goToPage;
            window.goToPage = function(pageNum) {
                console.log('拦截goToPage函数，页码:', pageNum);
                
                // 使用增强的导航函数
                navigateWithAllFilters(pageNum);
            };
            console.log('已增强goToPage函数');
        }
        
        // 4. 增强筛选功能
        function enhanceFilterButtons() {
            // 查找所有筛选按钮
            const filterButtons = document.querySelectorAll('.filter-btn');
            
            filterButtons.forEach(button => {
                const originalClick = button.onclick;
                
                button.onclick = function(e) {
                    console.log('筛选按钮点击:', this.getAttribute('data-filter-type'));
                    
                    // 调用原始点击事件
                    if (originalClick) {
                        originalClick.call(this, e);
                    }
                    
                    // 确保selectedFilters对象存在
                    if (!window.selectedFilters) {
                        window.selectedFilters = {};
                    }
                };
            });
            
            console.log('已增强筛选按钮');
        }
        
        // 5. 增强搜索功能
        function enhanceSearchButton() {
            const searchButton = document.getElementById('searchButton');
            if (searchButton) {
                const originalClick = searchButton.onclick;
                
                searchButton.onclick = function(e) {
                    console.log('搜索按钮点击');
                    
                    // 获取搜索关键词
                    const searchInput = document.getElementById('searchInput');
                    if (searchInput && searchInput.value.trim()) {
                        // 确保selectedFilters对象存在
                        if (!window.selectedFilters) {
                            window.selectedFilters = {};
                        }
                        
                        // 保存关键词到selectedFilters
                        window.selectedFilters.keyword = searchInput.value.trim();
                        console.log(`保存关键词到selectedFilters: ${searchInput.value.trim()}`);
                    }
                    
                    // 调用原始点击事件
                    if (originalClick) {
                        originalClick.call(this, e);
                    }
                };
                
                console.log('已增强搜索按钮');
            }
        }
        
        // 6. 初始化函数
        function initialize() {
            // 替换分页链接
            replacePaginationLinks();
            
            // 增强筛选按钮
            enhanceFilterButtons();
            
            // 增强搜索按钮
            enhanceSearchButton();
            
            // 从URL参数初始化selectedFilters
            const urlParams = new URLSearchParams(window.location.search);
            if (!window.selectedFilters) {
                window.selectedFilters = {};
            }
            
            ['region', 'subject', 'stage', 'source_type', 'source', 'year', 'keyword'].forEach(param => {
                const value = urlParams.get(param);
                if (value) {
                    window.selectedFilters[param] = value;
                    console.log(`从URL初始化selectedFilters: ${param}=${value}`);
                }
            });
            
            console.log('分页和筛选修复初始化完成');
        }
        
        // 执行初始化
        initialize();
        
        // 每秒检查一次，确保动态加载的元素也被处理
        setInterval(function() {
            replacePaginationLinks();
        }, 1000);
    });
})();
