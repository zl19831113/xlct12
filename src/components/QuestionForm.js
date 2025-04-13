import React, { useState } from 'react';

const [subject, setSubject] = useState('chinese');
const questionTypes = {
  chinese: [
    '文言文阅读', 
    '现代文阅读',
    '古诗词鉴赏',
    '名篇名句默写',
    '语言文字运用',
    '作文'
  ],
  math: [
    '单项选择题',
    '多项选择题',
    '填空题',
    '解答题',
    '证明题',
    '应用题'
  ],
  english: [
    '听力理解',
    '阅读理解',
    '完形填空',
    '语法填空',
    '短文改错',
    '书面表达'
  ]
};

// 在表单中添加科目选择
<select 
  value={subject} 
  onChange={(e) => setSubject(e.target.value)}
>
  <option value="chinese">语文</option>
  <option value="math">数学</option>
  <option value="english">英语</option>
</select>

// 添加题型选择
<select>
  {questionTypes[subject].map(type => (
    <option key={type} value={type}>{type}</option>
  ))}
</select> 