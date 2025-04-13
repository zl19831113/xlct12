import React, { useState } from 'react';

const [currentSubject, setCurrentSubject] = useState('chinese');

// 在上传表单中添加相同的选择器结构 

const questionTypes = {
  // ...保持与QuestionForm相同的结构
};

// 添加上传页面的科目选择器
<select
  value={currentSubject}
  onChange={(e) => setCurrentSubject(e.target.value)}
>
  {/* 包含全部9个科目选项 */}
</select>

// 同样添加父元素包裹
<div className="upload-filters">
  {/* 两个选择器布局 */}
</div> 