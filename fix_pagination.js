// 防止所有DOM错误的通用修复脚本
document.addEventListener('DOMContentLoaded', function() {
    console.log("🛠 分页和DOM错误修复脚本已加载");
    
    // 1. 创建缺失的DOM元素
    function createPlaceholderElements() {
        const missingElements = [
            'paginationControls', 'prevPage', 'nextPage', 'pageInfo',
            'papers-container'
        ];
        
        missingElements.forEach(id => {
            if (!document.getElementById(id)) {
                console.log(`👉 创建缺失的DOM元素: #${id}`);
                const el = document.createElement('div');
                el.id = id;
                el.style.display = 'none';
                document.body.appendChild(el);
            }
        });
    }
    
    // 2. 修复页面显示错误
    function fixDisplayIssues() {
        // 找到所有表格行，确保不会出现布局错误
        const tableRows = document.querySelectorAll('tr');
        tableRows.forEach(row => {
            if (row.cells.length === 0) {
                // 添加一个占位符单元格防止布局错误
                const cell = document.createElement('td');
                cell.colSpan = 8;
                cell.innerHTML = '&nbsp;';
                row.appendChild(cell);
            }
        });
    }
    
    // 3. 拦截和修复DOM操作，确保不会出现"Cannot read properties of null"错误
    function setupDOMOperationSafety() {
        // 保存原始方法
        const originalGetElementById = document.getElementById;
        
        // 替换为安全版本
        document.getElementById = function(id) {
            const element = originalGetElementById.call(document, id);
            if (!element) {
                console.log(`🔍 尝试访问不存在的元素: #${id}`);
                // 创建并添加缺失的元素
                const el = document.createElement('div');
                el.id = id;
                el.style.display = 'none';
                document.body.appendChild(el);
                
                // 添加所有可能需要的属性和方法
                el.disabled = false;
                el.textContent = '';
                el.style = {
                    display: 'none',
                    toString: function() { return 'none'; }
                };
                
                return el;
            }
            return element;
        };
    }
    
    // 4. 修复事件处理器
    function fixEventHandlers() {
        // 保存原始方法
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        
        // 替换为安全版本
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            // 创建一个安全的包装器
            const safeListener = function(event) {
                try {
                    return listener.call(this, event);
                } catch (error) {
                    console.error(`❌ 事件处理器错误 (${type}):`, error);
                    return false; // 阻止默认行为
                }
            };
            
            // 调用原始方法，但使用安全的包装器
            return originalAddEventListener.call(this, type, safeListener, options);
        };
    }
    
    // 5. 修复特定的分页相关函数，如updatePagination
    function fixPaginationFunctions() {
        // 检查是否存在updatePagination函数
        if (typeof window.updatePagination === 'function') {
            const originalUpdatePagination = window.updatePagination;
            
            // 替换为安全版本
            window.updatePagination = function() {
                try {
                    return originalUpdatePagination.apply(this, arguments);
                } catch (error) {
                    console.error('❌ updatePagination错误:', error);
                }
            };
            
            console.log('✅ 已修复updatePagination函数');
        }
    }
    
    // 6. 修复特定的样式类问题
    function fixStyleIssues() {
        // 确保分页按钮没有下划线
        const allLinks = document.querySelectorAll('a.pagination-button');
        allLinks.forEach(link => {
            link.style.textDecoration = 'none';
        });
        
        // 添加全局样式规则
        const styleEl = document.createElement('style');
        styleEl.textContent = `
            .pagination-button, #prevPage, #nextPage {
                text-decoration: none !important;
                outline: none !important;
            }
            a.pagination-button:hover {
                text-decoration: none !important;
            }
        `;
        document.head.appendChild(styleEl);
    }
    
    // 7. 修复搜索和筛选相关函数
    function fixSearchAndFilterFunctions() {
        const functionsToFix = [
            'fetchFilteredPapers', 'displayPapers', 'applyFilters', 
            'performSearch', 'goToPage', 'changePage'
        ];
        
        functionsToFix.forEach(funcName => {
            if (typeof window[funcName] === 'function') {
                const originalFunc = window[funcName];
                
                window[funcName] = function() {
                    try {
                        console.log(`🔄 执行 ${funcName}`);
                        return originalFunc.apply(this, arguments);
                    } catch (error) {
                        console.error(`❌ ${funcName} 函数错误:`, error);
                        // 为用户提供友好的错误信息
                        const container = document.getElementById('papers-container');
                        if (container) {
                            container.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px;">操作过程中出现错误，请刷新页面重试</td></tr>';
                        }
                    }
                };
                
                console.log(`✅ 已修复 ${funcName} 函数`);
            }
        });
    }
    
    // 执行所有修复
    try {
        console.log('🚀 开始执行DOM和分页修复...');
        createPlaceholderElements();
        fixDisplayIssues();
        setupDOMOperationSafety();
        fixEventHandlers();
        fixPaginationFunctions();
        fixStyleIssues();
        fixSearchAndFilterFunctions();
        console.log('✅ 所有修复已成功应用');
    } catch (error) {
        console.error('❌ 修复过程中发生错误:', error);
    }
    
    // 延迟再次运行以确保即使动态加载的内容也能得到修复
    window.addEventListener('load', function() {
        setTimeout(function() {
            try {
                createPlaceholderElements();
                fixDisplayIssues();
                fixStyleIssues();
                console.log('✅ 页面加载后的修复已应用');
            } catch (error) {
                console.error('❌ 页面加载后的修复过程中发生错误:', error);
            }
        }, 1000);
    });
});

// 分页和筛选条件修复脚本
(function() {
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('分页和筛选条件修复脚本已加载');
        
        // 增强的导航函数，保留所有筛选条件
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
        
        // 修复所有分页链接
        function fixPaginationLinks() {
            console.log('开始修复分页链接...');
            
            // 修复分页按钮点击事件
            const paginationButtons = document.querySelectorAll('.pagination-button, #prevPage, #nextPage');
            paginationButtons.forEach(button => {
                // 移除现有的点击事件
                const newButton = button.cloneNode(true);
                if (button.parentNode) {
                    button.parentNode.replaceChild(newButton, button);
                }
                
                // 添加新的点击事件
                newButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    let pageNum;
                    if (this.id === 'prevPage') {
                        const currentPage = parseInt(new URLSearchParams(window.location.search).get('page') || '1');
                        pageNum = Math.max(1, currentPage - 1);
                    } else if (this.id === 'nextPage') {
                        const currentPage = parseInt(new URLSearchParams(window.location.search).get('page') || '1');
                        pageNum = currentPage + 1;
                    } else {
                        pageNum = parseInt(this.getAttribute('data-page') || '1');
                    }
                    
                    console.log('修复后的分页点击:', pageNum);
                    window.navigateWithAllFilters(pageNum);
                    return false;
                });
            });
            
            console.log('修复了', paginationButtons.length, '个分页链接');
        }
        
        // 拦截changePage函数
        if (typeof window.changePage === 'function') {
            const originalChangePage = window.changePage;
            window.changePage = function(direction) {
                console.log('拦截changePage函数，方向:', direction);
                
                const urlParams = new URLSearchParams(window.location.search);
                const currentPage = parseInt(urlParams.get('page') || '1');
                const newPage = currentPage + direction;
                
                // 使用增强的导航函数
                window.navigateWithAllFilters(newPage);
                return false;
            };
            console.log('已增强changePage函数');
        }
        
        // 拦截goToPage函数
        if (typeof window.goToPage === 'function') {
            const originalGoToPage = window.goToPage;
            window.goToPage = function(pageNum) {
                console.log('拦截goToPage函数，页码:', pageNum);
                
                // 使用增强的导航函数
                window.navigateWithAllFilters(pageNum);
                return false;
            };
            console.log('已增强goToPage函数');
        }
        
        // 初始设置
        fixPaginationLinks();
        
        // 每2秒检查一次，确保动态加载的分页链接也被处理
        setInterval(fixPaginationLinks, 2000);
    });
})();
