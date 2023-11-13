# small_tools_v2
使用tkinter和Python制作的小工具集，非常方便自己扩展


## 前景提要
之前做过一个[small-tools](https://github.com/1061700625/small-tools)，当时预期说要集成很多小工具进去，但后来发现，如果想加新东西进去，还是非常麻烦的。     

那能不能做一个以插件形式添加的工具呢？我只需要提供py文件，在主UI中就可以自动把这个py功能加进来？    

所以以下就是初次尝试！目前添加了以下功能，支持**py**和**exe**形式的插件。

<div align=center> 
  <img width="551" alt="image" src="https://github.com/1061700625/small_tools_v2/assets/31002981/9e44e336-25bf-4525-82d7-9479d45372ee">
</div>

## 目录结构说明
<div align=center> 
  <img width="300" alt="image" src="https://github.com/1061700625/small_tools_v2/assets/31002981/5994334a-1c9c-41e0-a1f4-c1b1ffa81812">
  <img width="300" alt="image" src="https://github.com/1061700625/small_tools_v2/assets/31002981/11aa38d2-6e3a-4c2f-b152-48a8b1721ad2">
</div>


自行添加py功能函数（或打包为exe），统一放在plugin文件夹下，然后在**config.txt**里记录一下。
注意自己加的py里面必须要有 **process()** 函数，供main.py调用。

## 运行示例
**运行：**
- 对于Windows：双击**main.exe**或者**启动.bat**即可    
- 对于MacOS：双击**启动_mac.command**即可

(不过由于运行py文件，因此可能需要安装缺少的库)


**打包：**
```bash
conda activate py37
pyinstaller -F -w .\main.py
```

## 其他说明
这里的**desktop_clock.exe**来自这个仓库[Tkinter_Desktop_Clock](https://github.com/1061700625/Tkinter_Desktop_Clock)。

## 插件功能清单
- **字符串格式化**：其实就是去除空格，特别是caj论文在复制时候，文字之间会有很多空格

<div align=center> 
  <img width="462" alt="image" src="https://github.com/1061700625/small_tools_v2/assets/31002981/d49dd2e7-86ff-4593-ab1a-adf8f76a73e4">
</div>


- **PPT修改DPI**：修改导出图片的DPI

<div align=center> 
  <img width="462" alt="image" src="https://github.com/1061700625/small_tools_v2/assets/31002981/943128e9-f45e-44f3-aeb8-c0d9f299a558">
</div>


- **桌面时钟**

<div align=center> 
  <img width="462" alt="image" src="https://github.com/1061700625/small_tools_v2/assets/31002981/ca2872a8-c2e6-490c-9d39-8b75ee58e5ad">
</div>


- **[论文排名](https://blog.csdn.net/sxf1061700625/article/details/132081355)**

<div align=center> 
  <img width="462" alt="image" src="https://github.com/1061700625/small_tools_v2/assets/31002981/1825b756-c573-4fe4-92ea-e070c09b1eb3">
</div>

- **np文件简易查看器**
<div align=center> 
  <img width="462" alt="image" style="margin: 0 auto;" src="https://github.com/1061700625/small_tools_v2/assets/31002981/7b5485c3-11ea-402c-8cc9-b33cec528706">
</div>

- **[SSH端口转发管理器](https://blog.csdn.net/sxf1061700625/article/details/133746872)**    
<div align=center> 
  <img width="462" alt="image" style="margin: 0 auto;" src="https://github.com/1061700625/small_tools_v2/assets/31002981/272662be-a67c-4399-a50c-303ddc6b70c9">
</div>

- **[图像旋转器(数据集制作辅助)](https://blog.csdn.net/sxf1061700625/article/details/134300561)**
<div align=center> 
  <img width="462" alt="image" style="margin: 0 auto;" src="https://github.com/1061700625/small_tools_v2/assets/31002981/fb31b279-b0da-4166-b2e4-537184635001">
</div>

- **word mathml公式格式转latex**
<div align=center> 
  <img width="462" alt="image" style="margin: 0 auto;" src="https://github.com/1061700625/small_tools_v2/assets/31002981/3a8019fc-926f-487e-8f46-f63911c20a0c">
</div>

- **系统代理设置**
<div align=center> 
  <img width="462" alt="image" style="margin: 0 auto;" src="https://github.com/1061700625/small_tools_v2/assets/31002981/04f4d0dd-d3a7-44ce-b307-94e5e0951063">
</div>


