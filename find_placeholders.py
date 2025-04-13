#!/usr/bin/env python3
import os
import time
from pathlib import Path

# 设置目录路径
PAPERS_DIR = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/uploads/papers"

# 检查文件是否是占位符
def is_placeholder(filepath):
    # 检查文件大小
    if os.path.getsize(filepath) != 11:
        return False
    
    # 检查文件内容
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            return content == b'Placeholder'
    except:
        return False

# 统计信息
total_files = 0
placeholder_files = 0
placeholder_list = []

# 遍历目录
print(f"开始搜索 {PAPERS_DIR} 中的占位符文件...")
start_time = time.time()

for root, dirs, files in os.walk(PAPERS_DIR):
    for file in files:
        total_files += 1
        
        # 每1000个文件显示进度
        if total_files % 1000 == 0:
            print(f"已处理 {total_files} 个文件...")
        
        filepath = os.path.join(root, file)
        
        if is_placeholder(filepath):
            placeholder_files += 1
            placeholder_list.append({
                'path': filepath,
                'relative_path': os.path.relpath(filepath, PAPERS_DIR)
            })

end_time = time.time()

# 输出结果
print(f"\n扫描完成! 用时: {end_time - start_time:.2f} 秒")
print(f"总共扫描了 {total_files} 个文件")
print(f"找到 {placeholder_files} 个占位符文件 ({placeholder_files/total_files*100:.2f}%)")

# 创建报告文件
output_file = f"placeholder_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
with open(output_file, "w") as f:
    f.write(f"uploads/papers 目录中的占位符文件报告 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"总共扫描了 {total_files} 个文件\n")
    f.write(f"找到 {placeholder_files} 个占位符文件 ({placeholder_files/total_files*100:.2f}%)\n\n")
    
    # 按目录组织占位符文件
    dirs_with_placeholders = {}
    for ph in placeholder_list:
        dirname = os.path.dirname(ph['relative_path'])
        if dirname not in dirs_with_placeholders:
            dirs_with_placeholders[dirname] = []
        dirs_with_placeholders[dirname].append(os.path.basename(ph['path']))
    
    # 输出每个目录中的占位符文件
    f.write("== 按目录列出占位符文件 ==\n\n")
    for dirname, files in sorted(dirs_with_placeholders.items()):
        f.write(f"目录: {dirname if dirname else '根目录'}\n")
        f.write(f"包含 {len(files)} 个占位符文件\n")
        
        # 只列出前10个文件作为示例
        if len(files) > 10:
            for filename in sorted(files)[:10]:
                f.write(f"  - {filename}\n")
            f.write(f"  ... 以及其他 {len(files) - 10} 个文件\n")
        else:
            for filename in sorted(files):
                f.write(f"  - {filename}\n")
        
        f.write("\n")
    
    # 列出所有占位符文件
    f.write("\n== 所有占位符文件的完整列表 ==\n\n")
    for idx, ph in enumerate(sorted(placeholder_list, key=lambda x: x['relative_path']), 1):
        if idx <= 100:  # 只输出前100个文件作为示例
            f.write(f"{idx}. {ph['relative_path']}\n")
    
    if len(placeholder_list) > 100:
        f.write(f"\n... 以及其他 {len(placeholder_list) - 100} 个文件\n")

print(f"详细报告已保存到: {output_file}")
