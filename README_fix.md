# 试卷系统问题修复指南

## 1. 问题修复总结

我们对试卷系统进行了以下主要修复：

1. **移除随机替代文件逻辑**：之前系统在找不到文件时会随机选择一个文件替代，这导致用户下载到不匹配的试卷文件。我们已修改代码，现在会直接提示文件不存在。

2. **精确匹配工具**：创建了新的脚本`fix_paper_matches.py`，可以基于试卷名称和文件内容的语义匹配，为每个数据库记录找到最合适的文件。

3. **清除缺失文件记录**：添加了`clean_missing_papers.py`脚本，可以检测并删除数据库中没有对应文件的试卷记录。

4. **处理重复文件**：添加了`remove_duplicate_files.py`脚本，可以检测MD5哈希值相同的重复文件，并进行重命名或删除处理，同时更新数据库记录。

## 2. 如何使用修复工具

### 2.1 精确匹配试卷文件

执行以下命令运行精确匹配工具：

```bash
python3 fix_paper_matches.py
```

该工具会：
- 自动备份数据库
- 分析每个试卷记录的名称、科目、区域等信息
- 寻找最匹配的文件并更新数据库
- 优先处理云学名校联盟语文试卷等特定需求
- 生成详细日志(`paper_matching.log`)

### 2.2 清除缺失文件记录

如果您希望清除那些找不到对应文件的记录，请使用以下命令：

```bash
# 演习模式，只显示要删除的记录，不会实际删除
python3 clean_missing_papers.py

# 执行模式，实际删除缺失文件的记录
python3 clean_missing_papers.py --confirm
```

该工具会：
- 自动备份数据库
- 检查每条记录的文件是否存在
- 删除没有对应文件的记录
- 生成详细日志(`clean_papers.log`)

### 2.3 处理重复文件

如果您希望处理系统中的重复文件，请使用以下命令：

```bash
# 演习模式，只显示要处理的文件，不会实际操作
python3 remove_duplicate_files.py

# 执行模式-重命名，将重复文件重命名为*.duplicate.1.ext格式
python3 remove_duplicate_files.py --rename --confirm

# 执行模式-删除，删除重复文件（会先备份）
python3 remove_duplicate_files.py --delete --confirm
```

该工具会：
- 计算所有文件的MD5哈希值
- 识别完全相同的文件
- 更新数据库中的引用到保留的文件
- 重命名或删除重复文件（会先备份）
- 生成详细日志(`duplicate_files.log`)

### 2.4 重启应用

工具运行完成后，重启应用以应用更改：

```bash
./restart_server.sh
```

## 3. 后续维护建议

1. **文件命名规范**：建议对新上传的试卷文件采用规范化命名，包含以下要素：
   - 年份
   - 区域/省份
   - 学校/机构名称
   - 科目
   - 年级
   - 类型(期中/期末/模拟等)

   例如：`2025年湖北云学名校联盟高三语文2月联考.pdf`

2. **文件组织**：可以考虑按以下方式组织文件结构：
   ```
   uploads/papers/
     ├─ 语文/
     │   ├─ 高中/
     │   │   ├─ 高一/
     │   │   ├─ 高二/
     │   │   └─ 高三/
     │   └─ 初中/
     ├─ 数学/
     └─ ...
   ```

3. **定期维护**：
   - 每月运行一次`fix_paper_matches.py`工具，确保新上传的试卷都有正确的匹配
   - 每季度运行一次`clean_missing_papers.py`工具，清理没有对应文件的记录
   - 每季度运行一次`remove_duplicate_files.py`工具，处理重复上传的文件

## 4. 上传新版本到服务器

请使用以下命令将修复后的系统上传到服务器：

```bash
# 上传修复后的代码
rsync -avz --progress --partial --partial-dir=.rsync-partial --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' ./ root@120.26.12.100:/var/www/question_bank/

# 上传试卷文件
rsync -avz --progress --partial --partial-dir=.rsync-partial uploads/ root@120.26.12.100:/var/www/question_bank/uploads/
```

## 5. 更新日志

- **2025-04-04**: 移除了随机替代文件逻辑，增加了精确匹配工具
- **2025-04-04**: 修复了云学名校联盟语文试卷找不到问题
- **2025-04-04**: 添加了清除缺失文件记录的工具
- **2025-04-04**: 添加了重复文件处理工具，支持重命名和删除

如有任何问题，请联系系统管理员。 