-- 试卷科目不匹配修复SQL脚本
-- 生成时间: Tue Apr  1 06:44:46 CST 2025
-- 总共需要修复的记录数: 83

BEGIN TRANSACTION;

-- ID: 2703, 名称: 浙江省新阵地教育联盟2025届高三下学期第二次联考试题 技术 PDF版含答案【 高考】
-- 原科目: 语文, 检测科目: 数学
-- 文件路径: uploads/papers/20250313_194503_31_2023-2024.zip
UPDATE papers SET subject = '数学' WHERE id = 2703;

-- ID: 2754, 名称: 山西省衡水金卷2024-2025学年高三下学期2月开学联考试题 日语 PDF版含答案（含听力）【 高考】
-- 原科目: 语文, 检测科目: 政治, 英语
-- 文件路径: uploads/papers/20250313_193545_17_2023-2024.zip
UPDATE papers SET subject = '政治' WHERE id = 2754;

-- ID: 6140, 名称: 理综丨河南省TOP二十名校2024届高三下学期5月冲刺（一）理综试卷及答案 
-- 原科目: 物理, 检测科目: 政治
-- 文件路径: uploads/papers/20250313_193545_27_2023-2024.zip
UPDATE papers SET subject = '政治' WHERE id = 6140;

-- ID: 6154, 名称: 理综丨内蒙古包头市2024届高三下学期4月三模考试理综试卷及答案 
-- 原科目: 物理, 检测科目: 英语
-- 文件路径: uploads/papers/20250313_201311_112_2023-2024.docx.zip
UPDATE papers SET subject = '英语' WHERE id = 6154;

-- ID: 6160, 名称: 理综丨宁夏银川一中2024届高三下学期3月第一次模拟考试理综试卷及答案
-- 原科目: 物理, 检测科目: 英语
-- 文件路径: uploads/papers/20250313_203207_46_3.docx.zip
UPDATE papers SET subject = '英语' WHERE id = 6160;

-- ID: 6163, 名称: 理综丨青海省西宁市2024届高三5月二模理综试卷及答案 
-- 原科目: 物理, 检测科目: 历史
-- 文件路径: uploads/papers/20250313_195946_8_2022-2023_36714192.zip
UPDATE papers SET subject = '历史' WHERE id = 6163;

-- ID: 6172, 名称: 理综丨山西省晋中市2024届高三5月适应训练考试理综试卷及答案 
-- 原科目: 物理, 检测科目: 英语
-- 文件路径: uploads/papers/papers/20250228_133505_0_20259_PDF.zip
UPDATE papers SET subject = '英语' WHERE id = 6172;

-- ID: 6208, 名称: 理综丨四川省南充市2024届高三高考适应性考试（一诊）理综试卷及答案
-- 原科目: 物理, 检测科目: 历史
-- 文件路径: uploads/papers/20250313_202419_18_docx.zip
UPDATE papers SET subject = '历史' WHERE id = 6208;

-- ID: 6229, 名称: 理综丨云南省昆明市第一中学2024届高三5月第十次月考理综试卷及答案 
-- 原科目: 物理, 检测科目: 政治
-- 文件路径: uploads/papers/20250306_082948_16_2024_Word.zip
UPDATE papers SET subject = '政治' WHERE id = 6229;

-- ID: 6235, 名称: 理综丨云南省昭通市2024届高三上学期1月期末诊断性检测理综试卷及答案
-- 原科目: 物理, 检测科目: 英语
-- 文件路径: uploads/papers/papers/20250302_044556_0_2020I.zip
UPDATE papers SET subject = '英语' WHERE id = 6235;

-- ID: 7027, 名称: 日语丨衡水金卷广东省2025届高三8月摸底联考日语试卷及答案 
-- 原科目: 英语, 检测科目: 地理
-- 文件路径: uploads/papers/20250313_202144_73_2023.docx.zip
UPDATE papers SET subject = '地理' WHERE id = 7027;

-- ID: 7815, 名称: 史地政｜衡水金卷2024届高三4月大联考史地政试卷及答案
-- 原科目: 历史, 检测科目: 语文
-- 文件路径: uploads/papers/20250313_201613_47_2021-202211.doc.zip
UPDATE papers SET subject = '语文' WHERE id = 7815;

-- ID: 7841, 名称: 史地政｜云南省三校联考备考2024届高三上学期实用性联考（五）史地政试卷及答案
-- 原科目: 历史, 检测科目: 英语
-- 文件路径: uploads/papers/20250313_204227_111_2022-2023.docx.zip
UPDATE papers SET subject = '英语' WHERE id = 7841;

-- ID: 9078, 名称: 文综丨金太阳百万联考2024届高三5月大联考文综试卷及答案 
-- 原科目: 历史, 检测科目: 英语
-- 文件路径: uploads/papers/20250313_205115_87_2022.docx.zip
UPDATE papers SET subject = '英语' WHERE id = 9078;

-- ID: 9096, 名称: 文综丨山西省2024届高三下学期３月第二次学业质量评估文综试卷及答案
-- 原科目: 历史, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093401_1174_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 9096;

-- ID: 9109, 名称: 文综丨陕西省部分学校2024届高三5月第一次模拟文综试卷及答案 
-- 原科目: 历史, 检测科目: 语文
-- 文件路径: uploads/papers/20250306_082335_13_2024-2025_Word.zip
UPDATE papers SET subject = '语文' WHERE id = 9109;

-- ID: 9110, 名称: 文综丨陕西省商洛市2024届高三下学期４月第四次模拟检测试文综试卷及答案
-- 原科目: 历史, 检测科目: 语文
-- 文件路径: uploads/papers/20250313_191840_163_2023-2024_42364843.zip
UPDATE papers SET subject = '语文' WHERE id = 9110;

-- ID: 9124, 名称: 文综丨四川省成都市石室中学2024届高三上学期1月期末考试文综试卷及答案
-- 原科目: 历史, 检测科目: 英语
-- 文件路径: uploads/papers/20250313_201311_75_2022-2023.docx.zip
UPDATE papers SET subject = '英语' WHERE id = 9124;

-- ID: 9142, 名称: 文综丨天一大联考2024届高考考前模拟考试文综试卷及答案 
-- 原科目: 历史, 检测科目: 数学
-- 文件路径: uploads/papers/20250313_190509_7_2020-202110.zip
UPDATE papers SET subject = '数学' WHERE id = 9142;

-- ID: 9143, 名称: 文综丨天一大联考2024届高三下学期高中毕业班阶段性测试（五）文综试卷及答案
-- 原科目: 历史, 检测科目: 物理
-- 文件路径: uploads/papers/papers/20250226_172032_4_T8202512_PDF.zip
UPDATE papers SET subject = '物理' WHERE id = 9143;

-- ID: 9165, 名称: 物化生｜百师联盟2024届高三下学期二轮复习联考（一）（全国卷）物化生试卷及答案
-- 原科目: 物理, 检测科目: 语文
-- 文件路径: uploads/papers/20250313_201612_31_2.docx.zip
UPDATE papers SET subject = '语文' WHERE id = 9165;

-- ID: 9191, 名称: 物化生｜天一大联考2024届山西高三阶段性测试（定位）物化生试卷及答案
-- 原科目: 物理, 检测科目: 化学
-- 文件路径: uploads/papers/20250306_082508_8_2024_Word.zip
UPDATE papers SET subject = '化学' WHERE id = 9191;

-- ID: 26393, 名称: 2020年中考真题精品解析 道德与法治（湖北鄂州卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1448_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 26393;

-- ID: 26394, 名称: 2020年中考真题精品解析 道德与法治(湖北恩施卷)精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1449_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 26394;

-- ID: 26395, 名称: 2020年中考真题精品解析 道德与法治(湖北黄冈卷)精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1450_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 26395;

-- ID: 26396, 名称: 2020年中考真题精品解析 道德与法治（湖北荆门卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1451_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 26396;

-- ID: 26397, 名称: 2020年中考真题精品解析 道德与法治（湖北十堰卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1452_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 26397;

-- ID: 26398, 名称: 2020年中考真题精品解析 道德与法治（湖北随州卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1453_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 26398;

-- ID: 26401, 名称: 2020年中考真题精品解析 道德与法治（湖北咸宁卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1456_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 26401;

-- ID: 26405, 名称: 精品解析：2023年湖北黄冈市、孝感市、咸宁市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1460_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 26405;

-- ID: 26406, 名称: 精品解析：2023年湖北省鄂州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1461_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 26406;

-- ID: 26407, 名称: 精品解析：2023年湖北省恩施州中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1462_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 26407;

-- ID: 26409, 名称: 精品解析：2023年湖北省十堰市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1464_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 26409;

-- ID: 26410, 名称: 精品解析：2023年湖北省随州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1465_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 26410;

-- ID: 26412, 名称: 精品解析：2023年湖北省武汉市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_091640_1467_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 26412;

-- ID: 26416, 名称: 2020年中考真题精品解析 科学（河南卷）精编word版
-- 原科目: 语文, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_092805_0_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 26416;

-- ID: 26418, 名称: 精品解析：2023年河南省中考道德与法治真题
-- 原科目: 语文, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_092805_2_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 26418;

-- ID: 29421, 名称: 精品解析：2023年福建省中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093256_1350_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 29421;

-- ID: 30596, 名称: 精品解析：2023年浙江省湖州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093401_1173_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 30596;

-- ID: 30599, 名称: 精品解析：2023年浙江省丽水市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093401_1176_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 30599;

-- ID: 30600, 名称: 精品解析：2023年浙江省宁波市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093401_1177_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 30600;

-- ID: 30601, 名称: 精品解析：2023年浙江省衢州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093401_1178_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 30601;

-- ID: 30602, 名称: 精品解析：2023年浙江省绍兴市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093401_1179_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 30602;

-- ID: 30603, 名称: 精品解析：2023年浙江省台州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093401_1180_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 30603;

-- ID: 30604, 名称: 精品解析：2023年浙江省温州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093401_1181_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 30604;

-- ID: 31781, 名称: 精品解析：2023年浙江省湖州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093509_1173_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 31781;

-- ID: 31783, 名称: 精品解析：2023年浙江省金华市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093509_1175_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 31783;

-- ID: 31784, 名称: 精品解析：2023年浙江省丽水市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093509_1176_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 31784;

-- ID: 31785, 名称: 精品解析：2023年浙江省宁波市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093509_1177_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 31785;

-- ID: 31788, 名称: 精品解析：2023年浙江省台州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093509_1180_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 31788;

-- ID: 31789, 名称: 精品解析：2023年浙江省温州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093509_1181_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 31789;

-- ID: 32723, 名称: 精品解析：2023年福建省中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093611_930_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 32723;

-- ID: 32724, 名称: 精品解析：2024年福建省中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093611_931_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 32724;

-- ID: 33570, 名称: 精品解析：2023年山西省中考道德与法治真题
-- 原科目: 语文, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093717_845_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 33570;

-- ID: 33571, 名称: 精品解析：2024年山西省中考道德与法治真题
-- 原科目: 语文, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093717_846_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 33571;

-- ID: 35698, 名称: 2020年中考真题精品解析 道德与法治（广东广州卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093927_2126_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 35698;

-- ID: 35701, 名称: 精品解析：2023年广东省中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093927_2129_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 35701;

-- ID: 35702, 名称: 精品解析：2024年广东省广州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093927_2130_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 35702;

-- ID: 35703, 名称: 精品解析：2024年广东省中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_093927_2131_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 35703;

-- ID: 39931, 名称: 2020年中考真题精品解析 道德与法治（山东聊城卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4227_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 39931;

-- ID: 39932, 名称: 2020年中考真题精品解析 道德与法治（山东临沂卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4228_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 39932;

-- ID: 39934, 名称: 2020年中考真题精品解析 道德与法治(山东泰安卷)精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4230_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 39934;

-- ID: 39935, 名称: 2020年中考真题精品解析 道德与法治（山东威海卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4231_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 39935;

-- ID: 39936, 名称: 2020年中考真题精品解析 道德与法治（山东潍坊卷）精编word版
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4232_2020_word.zip
UPDATE papers SET subject = '政治' WHERE id = 39936;

-- ID: 39940, 名称: 精品解析：2022年山东省青岛市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4236_2022.zip
UPDATE papers SET subject = '政治' WHERE id = 39940;

-- ID: 39942, 名称: 精品解析：2023年山东省菏泽市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4238_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 39942;

-- ID: 39943, 名称: 精品解析：2023年山东省济南市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4239_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 39943;

-- ID: 39946, 名称: 精品解析：2023年山东省临沂市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4242_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 39946;

-- ID: 39948, 名称: 精品解析：2023年山东省泰安市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4244_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 39948;

-- ID: 39950, 名称: 精品解析：2023年山东省潍坊市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4246_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 39950;

-- ID: 39952, 名称: 精品解析：2023年山东省枣庄市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4248_2023.zip
UPDATE papers SET subject = '政治' WHERE id = 39952;

-- ID: 39953, 名称: 精品解析：2024年山东省德州市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4249_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39953;

-- ID: 39954, 名称: 精品解析：2024年山东省东营市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4250_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39954;

-- ID: 39955, 名称: 精品解析：2024年山东省菏泽市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4251_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39955;

-- ID: 39957, 名称: 精品解析：2024年山东省济宁市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4253_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39957;

-- ID: 39958, 名称: 精品解析：2024年山东省临沂市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4254_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39958;

-- ID: 39959, 名称: 精品解析：2024年山东省青岛市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4255_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39959;

-- ID: 39960, 名称: 精品解析：2024年山东省日照市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4256_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39960;

-- ID: 39962, 名称: 精品解析：2024年山东省威海市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4258_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39962;

-- ID: 39963, 名称: 精品解析：2024年山东省潍坊市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4259_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39963;

-- ID: 39964, 名称: 精品解析：2024年山东省烟台市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4260_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39964;

-- ID: 39965, 名称: 精品解析：2024年山东省枣庄市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4261_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39965;

-- ID: 39966, 名称: 精品解析：2024年山东省淄博市中考道德与法治真题
-- 原科目: 英语, 检测科目: 政治
-- 文件路径: uploads/papers/20250316_094351_4262_2024.zip
UPDATE papers SET subject = '政治' WHERE id = 39966;

COMMIT;
