# DBInputSp
一个双拼正反查工具，协助输入法的开发和日常使用
# 主要有三个作用
- 1、正查：把文字转化为双拼编码
- 2、反查：把双拼编码转换成拼音
- 3、查表：输出完整双拼对应键位表

现在添加了过滤器的内容，我们遍历了所有声母（包括零声母）+韵母的组合，从中反选了具有候选词含义的组合，然后添加到config.py中的过滤表

如果你发现了漏网之鱼或者意料之外的输出，可以手动添加到过滤表中，也可以在issues里面提醒我们

<img width="822" height="371" alt="image" src="https://github.com/user-attachments/assets/b50afbd6-1999-4e77-9953-0c2df9499b09" />

目前method/添加了主流的双拼方案，你可以自己在method文件夹仿照示例文件，自己添加其他双拼文件，并且在config.py里面登记。

如果你希望从源代码运行，请下载https://github.com/BlueSky-07/Shuang/releases/tag/6.0

随后解压到工程目录下，以获得双拼练习和显示双拼键位表的的功能

按下回车键可查看具体的帮助：

<img width="1122" height="1383" alt="image" src="https://github.com/user-attachments/assets/5c84c3b1-5d05-452d-b383-151f192f1f49" />
