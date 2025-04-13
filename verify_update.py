#!/usr/bin/env python3
import os
import sqlite3
import time

# 设置路径
DB_PATH = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/xlct12.db"
FILES_DIR = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/uploads/papers"

# 确保目录存在
if not os.path.exists(DB_PATH):
    print(f"错误: 数据库 {DB_PATH} 不存在")
    exit(1)
if not os.path.exists(FILES_DIR):
    print(f"错误: 目录 {FILES_DIR} 不存在")
    exit(1)

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"开始验证数据库更新结果...")

# 获取所有papers表记录
cursor.execute("SELECT id, name, file_path, subject FROM papers")
db_records = cursor.fetchall()

print(f"数据库中总记录数: {len(db_records)}")

# 分类统计路径类型
zujuanwang81_paths = 0
other_paths = 0
invalid_paths = 0
invalid_records = []

for rec_id, name, file_path, subject in db_records:
    if 'zujuanwang81' in file_path:
        # 检查文件是否存在
        if os.path.exists(file_path):
            zujuanwang81_paths += 1
        else:
            invalid_paths += 1
            invalid_records.append((rec_id, name, file_path, subject, "zujuanwang81路径但文件不存在"))
    else:
        other_paths += 1
        invalid_records.append((rec_id, name, file_path, subject, "非zujuanwang81路径"))

# 输出验证结果
print("\n== 验证结果 ==")
print(f"总记录数: {len(db_records)}")
print(f"有效的zujuanwang81路径: {zujuanwang81_paths} ({zujuanwang81_paths/len(db_records)*100:.1f}%)")
print(f"非zujuanwang81路径: {other_paths} ({other_paths/len(db_records)*100:.1f}%)")
print(f"无效路径: {invalid_paths} ({invalid_paths/len(db_records)*100:.1f}%)")

# 创建报告文件
report_file = f"verification_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
with open(report_file, "w") as f:
    f.write(f"数据库更新验证报告 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("== 验证结果 ==\n")
    f.write(f"总记录数: {len(db_records)}\n")
    f.write(f"有效的zujuanwang81路径: {zujuanwang81_paths} ({zujuanwang81_paths/len(db_records)*100:.1f}%)\n")
    f.write(f"非zujuanwang81路径: {other_paths} ({other_paths/len(db_records)*100:.1f}%)\n")
    f.write(f"无效路径: {invalid_paths} ({invalid_paths/len(db_records)*100:.1f}%)\n\n")
    
    # 按科目统计未更新记录
    subjects_count = {}
    for _, _, _, subject, _ in invalid_records:
        if subject not in subjects_count:
            subjects_count[subject] = 0
        subjects_count[subject] += 1
    
    if subjects_count:
        f.write("== 按科目统计未更新记录 ==\n")
        for subject, count in sorted(subjects_count.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{subject}: {count} 条记录\n")
        
        f.write("\n== 未更新记录示例(前50条) ==\n\n")
        for idx, (rec_id, name, file_path, subject, reason) in enumerate(invalid_records[:50], 1):
            f.write(f"{idx}. ID: {rec_id}, 科目: {subject}\n")
            f.write(f"   名称: {name}\n")
            f.write(f"   路径: {file_path}\n")
            f.write(f"   原因: {reason}\n")
            f.write("-" * 80 + "\n")
        
        if len(invalid_records) > 50:
            f.write(f"\n... 以及其他 {len(invalid_records) - 50} 条记录\n")

# 关闭数据库连接
conn.close()

print(f"\n详细报告已保存到: {report_file}")
