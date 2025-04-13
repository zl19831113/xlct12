from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Paper(db.Model):
    __tablename__ = 'papers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 试卷名称
    region = db.Column(db.String(50), nullable=False)  # 地区
    subject = db.Column(db.String(50), nullable=False)  # 科目
    stage = db.Column(db.String(20), nullable=False)   # 阶段
    source = db.Column(db.String(100), nullable=False) # 来源
    year = db.Column(db.Integer, nullable=False)       # 年份
    file_path = db.Column(db.String(500), nullable=False) # 文件路径
    upload_time = db.Column(db.DateTime, default=datetime.now) # 上传时间 