const Header = () => {
  return (
    <header className="header-container">
      <div className="logo-section">
        <picture>
          <source srcSet="/logo/logo.webp" type="image/webp" />
          <img 
            src="/logo/logo.png" // 路径根据实际存放位置调整
            alt="小鹿出题 Logo"
            className="logo"
            onError={(e) => {
              e.target.style.display = 'none'; // 图片加载失败时隐藏
            }}
          />
        </picture>
        <div className="site-info">
          <h1 className="site-title">小鹿出题</h1>
          <span className="domain">xlct12.com</span>
        </div>
      </div>
      <form className="search-form">
        <input
          type="search"
          placeholder="请输入题目关键词..."
          className="search-input"
        />
        <button type="submit" className="search-button">
          搜索
        </button>
      </form>
    </header>
  );
}; 