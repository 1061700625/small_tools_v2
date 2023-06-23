# small_tools_v2
使用tkinter和Python制作的小工具集，非常方便自己扩展


## 前景提要
之前做过一个[small-tools](https://github.com/1061700625/small-tools)，当时预期说要集成很多小工具进去，但后来发现，如果想加新东西进去，还是非常麻烦的。     

那能不能做一个以插件形式添加的工具呢？我只需要提供py文件，在主UI中就可以自动把这个py功能加进来？    

所以以下就是初次尝试！目前添加了三个功能，支持**py**和**exe**形式的插件。

![image](https://github.com/1061700625/small_tools_v2/assets/31002981/e0c8e0b9-ff1f-4796-8f4c-a71bf285aee2)

## 目录结构说明
![image](https://github.com/1061700625/small_tools_v2/assets/31002981/5994334a-1c9c-41e0-a1f4-c1b1ffa81812)
![image](https://github.com/1061700625/small_tools_v2/assets/31002981/11aa38d2-6e3a-4c2f-b152-48a8b1721ad2)

自行添加py功能函数（或打包为exe），统一放在plugin文件夹下，然后在**config.txt**里记录一下。
注意自己加的py里面必须要有**process()**函数，供main.py调用。

## 运行示例
**运行：**
双击main.exe即可

**打包：**
```bash
conda activate py37
pyinstaller -F -w .\main.py
```

## 其他说明
这里的**desktop_clock.exe**来自这个仓库[Tkinter_Desktop_Clock](https://github.com/1061700625/Tkinter_Desktop_Clock)。
