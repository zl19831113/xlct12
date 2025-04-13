/**
 * 试卷页面优化器 - 高效替换占位图为真实试卷预览
 * 使用懒加载和缓存机制提高性能
 */

class PapersOptimizer {
    constructor(options = {}) {
        // 默认配置
        this.config = {
            containerSelector: '#papers-container',
            paperSelector: 'tr',
            placeholderSelector: '.paper-icon-img',
            apiEndpoint: '/api/paper_preview/',
            batchSize: 5,
            preloadDistance: 300,
            cacheExpiration: 24 * 60 * 60 * 1000, // 24小时缓存
            ...options
        };

        // 初始化状态
        this.initialized = false;
        this.observer = null;
        this.paperElements = [];
        this.loadingQueue = [];
        this.cache = this.loadCache();
        
        // 绑定方法到实例
        this.init = this.init.bind(this);
        this.loadPaperPreview = this.loadPaperPreview.bind(this);
        this.processBatch = this.processBatch.bind(this);
        this.handleIntersection = this.handleIntersection.bind(this);
    }

    /**
     * 初始化优化器
     */
    init() {
        if (this.initialized) return;
        
        console.log('初始化试卷优化器...');
        
        // 获取所有试卷元素
        const container = document.querySelector(this.config.containerSelector);
        if (!container) {
            console.error('未找到试卷容器:', this.config.containerSelector);
            return;
        }
        
        this.paperElements = Array.from(container.querySelectorAll(this.config.paperSelector));
        
        if (this.paperElements.length === 0) {
            console.log('未找到试卷元素');
            return;
        }
        
        console.log(`找到 ${this.paperElements.length} 份试卷`);
        
        // 设置交叉观察器，实现懒加载
        this.setupIntersectionObserver();
        
        // 立即加载可见区域的试卷
        this.loadVisiblePapers();
        
        this.initialized = true;
    }
    
    /**
     * 设置交叉观察器
     */
    setupIntersectionObserver() {
        // 如果浏览器支持 IntersectionObserver
        if ('IntersectionObserver' in window) {
            const options = {
                root: null,
                rootMargin: `${this.config.preloadDistance}px`,
                threshold: 0.1
            };
            
            this.observer = new IntersectionObserver(this.handleIntersection, options);
            
            // 观察所有试卷元素
            this.paperElements.forEach(element => {
                this.observer.observe(element);
            });
            
            console.log('交叉观察器已设置');
        } else {
            // 如果不支持，则使用滚动事件
            console.log('浏览器不支持 IntersectionObserver，使用滚动事件替代');
            window.addEventListener('scroll', this.debounce(() => {
                this.loadVisiblePapers();
            }, 200));
            
            // 初始加载
            this.loadVisiblePapers();
        }
    }
    
    /**
     * 处理元素进入视口的事件
     */
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // 元素进入视口
                const element = entry.target;
                this.loadPaperPreview(element);
                
                // 停止观察已处理的元素
                this.observer.unobserve(element);
            }
        });
    }
    
    /**
     * 加载当前可见的试卷
     */
    loadVisiblePapers() {
        const viewportHeight = window.innerHeight;
        const scrollTop = window.scrollY;
        
        // 计算视口范围
        const viewportTop = scrollTop - this.config.preloadDistance;
        const viewportBottom = scrollTop + viewportHeight + this.config.preloadDistance;
        
        // 查找视口内的试卷
        this.paperElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            const elementTop = rect.top + scrollTop;
            const elementBottom = elementTop + rect.height;
            
            // 如果元素在视口范围内
            if (elementBottom >= viewportTop && elementTop <= viewportBottom) {
                this.loadPaperPreview(element);
            }
        });
    }
    
    /**
     * 加载试卷预览
     */
    loadPaperPreview(element) {
        // 如果已经处理过，跳过
        if (element.dataset.processed === 'true') return;
        
        // 标记为已处理
        element.dataset.processed = 'true';
        
        // 获取试卷ID
        const downloadLink = element.querySelector('a.download-btn');
        if (!downloadLink) return;
        
        const paperId = downloadLink.href.split('/').pop();
        
        // 检查缓存
        const cachedData = this.getCachedPreview(paperId);
        if (cachedData) {
            this.updatePaperPreview(element, cachedData);
            return;
        }
        
        // 添加到加载队列
        this.loadingQueue.push({
            element,
            paperId
        });
        
        // 处理队列
        if (this.loadingQueue.length >= this.config.batchSize) {
            this.processBatch();
        } else if (this.loadingQueue.length === 1) {
            // 如果这是队列中的第一个，设置定时器
            setTimeout(() => {
                if (this.loadingQueue.length > 0) {
                    this.processBatch();
                }
            }, 100);
        }
    }
    
    /**
     * 批量处理加载队列
     */
    processBatch() {
        // 取出一批
        const batch = this.loadingQueue.splice(0, this.config.batchSize);
        if (batch.length === 0) return;
        
        // 获取所有ID
        const paperIds = batch.map(item => item.paperId);
        
        // 构建URL
        const url = `${this.config.apiEndpoint}${paperIds.join(',')}`;
        
        // 显示加载中状态
        batch.forEach(item => {
            const placeholder = item.element.querySelector(this.config.placeholderSelector);
            if (placeholder) {
                placeholder.style.opacity = '0.5';
            }
        });
        
        // 发送请求
        fetch(url)
            .then(response => response.json())
            .then(data => {
                // 处理返回数据
                batch.forEach(item => {
                    if (data[item.paperId]) {
                        // 更新预览
                        this.updatePaperPreview(item.element, data[item.paperId]);
                        
                        // 保存到缓存
                        this.cachePreview(item.paperId, data[item.paperId]);
                    }
                });
            })
            .catch(error => {
                console.error('加载试卷预览失败:', error);
                
                // 恢复占位图
                batch.forEach(item => {
                    const placeholder = item.element.querySelector(this.config.placeholderSelector);
                    if (placeholder) {
                        placeholder.style.opacity = '1';
                    }
                });
            });
    }
    
    /**
     * 更新试卷预览
     */
    updatePaperPreview(element, previewData) {
        const placeholder = element.querySelector(this.config.placeholderSelector);
        if (!placeholder) return;
        
        // 如果有缩略图
        if (previewData.thumbnail) {
            // 创建新的缩略图元素
            const thumbnail = document.createElement('img');
            thumbnail.src = previewData.thumbnail;
            thumbnail.alt = '试卷预览';
            thumbnail.className = 'paper-preview-img';
            thumbnail.style.maxWidth = '40px';
            thumbnail.style.maxHeight = '40px';
            thumbnail.style.objectFit = 'contain';
            thumbnail.style.border = '1px solid #eee';
            thumbnail.style.borderRadius = '4px';
            
            // 替换占位图
            placeholder.parentNode.replaceChild(thumbnail, placeholder);
        }
        
        // 如果有meta信息，更新信息显示
        if (previewData.meta) {
            // 添加额外信息如总页数、题目数量等
            const infoSpan = document.createElement('span');
            infoSpan.className = 'paper-meta';
            infoSpan.style.fontSize = '12px';
            infoSpan.style.color = '#666';
            infoSpan.style.marginLeft = '5px';
            
            if (previewData.meta.pageCount) {
                infoSpan.textContent += `${previewData.meta.pageCount}页 | `;
            }
            
            if (previewData.meta.questionCount) {
                infoSpan.textContent += `${previewData.meta.questionCount}题`;
            }
            
            // 添加到试卷名称后面
            const nameTd = element.querySelector('td:first-child');
            if (nameTd) {
                nameTd.appendChild(infoSpan);
            }
        }
    }
    
    /**
     * 将预览数据保存到缓存
     */
    cachePreview(paperId, previewData) {
        const cacheKey = `paper_preview_${paperId}`;
        const cacheData = {
            data: previewData,
            timestamp: Date.now()
        };
        
        try {
            localStorage.setItem(cacheKey, JSON.stringify(cacheData));
            this.cache[paperId] = cacheData;
        } catch (error) {
            console.warn('缓存预览数据失败:', error);
            
            // 如果localStorage已满，清理旧缓存
            this.cleanupOldCache();
        }
    }
    
    /**
     * 从缓存获取预览数据
     */
    getCachedPreview(paperId) {
        // 先从内存缓存获取
        const memoryCache = this.cache[paperId];
        if (memoryCache) {
            // 检查是否过期
            if (Date.now() - memoryCache.timestamp < this.config.cacheExpiration) {
                return memoryCache.data;
            }
            
            // 如果过期，删除缓存
            delete this.cache[paperId];
            localStorage.removeItem(`paper_preview_${paperId}`);
            return null;
        }
        
        // 从localStorage获取
        try {
            const cacheKey = `paper_preview_${paperId}`;
            const cachedItem = localStorage.getItem(cacheKey);
            
            if (cachedItem) {
                const cacheData = JSON.parse(cachedItem);
                
                // 检查是否过期
                if (Date.now() - cacheData.timestamp < this.config.cacheExpiration) {
                    // 保存到内存缓存
                    this.cache[paperId] = cacheData;
                    return cacheData.data;
                }
                
                // 如果过期，删除缓存
                localStorage.removeItem(cacheKey);
            }
        } catch (error) {
            console.warn('读取缓存失败:', error);
        }
        
        return null;
    }
    
    /**
     * 加载缓存数据
     */
    loadCache() {
        const cache = {};
        
        try {
            // 遍历localStorage中的所有键
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                
                // 只处理试卷预览缓存
                if (key.startsWith('paper_preview_')) {
                    const paperId = key.replace('paper_preview_', '');
                    const cachedItem = localStorage.getItem(key);
                    
                    if (cachedItem) {
                        const cacheData = JSON.parse(cachedItem);
                        
                        // 检查是否过期
                        if (Date.now() - cacheData.timestamp < this.config.cacheExpiration) {
                            cache[paperId] = cacheData;
                        } else {
                            // 如果过期，删除缓存
                            localStorage.removeItem(key);
                        }
                    }
                }
            }
        } catch (error) {
            console.warn('加载缓存失败:', error);
        }
        
        return cache;
    }
    
    /**
     * 清理旧缓存
     */
    cleanupOldCache() {
        try {
            // 收集所有试卷预览缓存键
            const previewKeys = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith('paper_preview_')) {
                    previewKeys.push({
                        key,
                        timestamp: JSON.parse(localStorage.getItem(key)).timestamp
                    });
                }
            }
            
            // 如果缓存数量超过100个，删除最旧的一半
            if (previewKeys.length > 100) {
                // 按时间戳排序
                previewKeys.sort((a, b) => a.timestamp - b.timestamp);
                
                // 删除最旧的一半
                const keysToRemove = previewKeys.slice(0, Math.floor(previewKeys.length / 2));
                keysToRemove.forEach(item => {
                    localStorage.removeItem(item.key);
                    
                    // 从内存缓存中也删除
                    const paperId = item.key.replace('paper_preview_', '');
                    delete this.cache[paperId];
                });
                
                console.log(`清理了 ${keysToRemove.length} 个旧缓存`);
            }
        } catch (error) {
            console.warn('清理缓存失败:', error);
        }
    }
    
    /**
     * 防抖函数
     */
    debounce(func, wait) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                func.apply(context, args);
            }, wait);
        };
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 创建优化器实例并初始化
    window.papersOptimizer = new PapersOptimizer();
    window.papersOptimizer.init();
    
    // 监听分页或筛选变化事件
    document.addEventListener('paginationUpdated', function() {
        // 重新初始化优化器
        window.papersOptimizer = new PapersOptimizer();
        window.papersOptimizer.init();
    });
});
