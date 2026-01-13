# DBInputSp
一个双拼正反查工具，协助输入法的开发，用于批量生成双拼和全拼对照表进行输入法测试
# 主要有三个作用
- 1、正查：把文字转化为双拼编码
- 2、反查：把双拼编码转换成拼音
- 3、查表：输出完整双拼对应键位表
- 
<img width="696" height="927" alt="image" src="https://github.com/user-attachments/assets/e4ae6bbd-0d39-431a-b683-0171d511784b" />


目前添加了小鹤双拼的示例方案method/xiaohe.py，你可以自己在method文件夹仿照示例文件，自己添加其他双拼文件，并且在config.py里面修改方案名称指向你新建的方案。
