# DBInputSp
一个双拼正反查工具，协助输入法的开发，用于批量生成双拼和全拼对照表进行输入法测试
# 主要有三个作用
- 1、正查：把文字转化为双拼编码
- 2、反查：把双拼编码转换成拼音
- 3、查表：输出完整双拼对应键位表
- 
<img width="810" height="693" alt="image" src="https://github.com/user-attachments/assets/ddb7b63c-bac1-46d7-9b2e-e51d124163cc" />


目前method/添加了小鹤双拼和自然码的示例方案xiaohe.py和ziranma.py，你可以自己在method文件夹仿照示例文件，自己添加其他双拼文件，并且在config.py里面修改方案名称指向你新建的方案。
