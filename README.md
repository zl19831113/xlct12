# 小鹿出题系统

这是一个使用 Flask 框架开发的智能组卷和试题管理系统。

## 功能

- 题目管理（增删改查）
- 试卷库管理
- 智能组卷
- 用户管理 (TODO)
- 英语听力支持 (带二维码)

## 技术栈

- 后端: Flask, SQLAlchemy
- 数据库: SQLite
- 前端: HTML, CSS, JavaScript
- Word 文档生成: python-docx
- 二维码生成: qrcode

## 安装和运行

1.  **克隆仓库:**

    ```bash
    git clone https://github.com/zl19831113/xlct12.git
    cd xlct12
    ```

2.  **创建并激活虚拟环境:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate  # Windows
    ```

3.  **安装依赖:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **运行应用:**

    ```bash
    flask run --port=5002
    ```
    或者使用 Gunicorn (推荐生产环境):
    ```bash
    gunicorn --bind 0.0.0.0:5002 app:app
    ```

5.  **访问应用:** 打开浏览器访问 `http://127.0.0.1:5002`

## 数据库

- 数据库文件位于 `instance/xlct12.db`。
- 应用启动时会自动检查并创建必要的表结构。

## 上传试卷

- 支持上传 PDF, DOC, DOCX, ZIP, RAR 格式的试卷文件。
- 上传的文件会保存在 `uploads/papers/` 目录下。

## 智能组卷

- 根据科目、学段、题型和数量要求，从题库中随机抽取题目生成 Word 试卷。
- 支持为包含听力题的英语试卷生成带二维码的 Word 文档，扫描二维码可播放在线音频。

## 注意事项

- 请确保 `instance/` 目录具有写入权限。
- 生产环境建议使用 Gunicorn 或其他 WSGI 服务器部署。
- 备份 `instance/xlct12.db` 文件以防数据丢失。

## 贡献

欢迎提出问题或贡献代码！ 