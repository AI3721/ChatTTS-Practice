# ChatTTS_Practice
> [!TIP]
> 新手小白入门——基于ChatTTS的FastAPI+Gradio入门练习项目
## 项目运行
### 1. 启动FastAPI
```bash
cd fastapi
uvicorn main:app --port 7788
```
### 2. 启动Gradio
```bash
cd gradio
python demo.py
```


## 使用示例
<details>
  <summary>文本转语音</summary>
  
  ##### ① 默认参数一键生成
  ![文本转语音](/examples/文本转语音.png)
  ##### ② 自定义参数生成
  ![可调参数](/examples/可调参数.png)
</details>


<details>
  <summary>声音克隆</summary>
  
  ![声音克隆](/examples/声音克隆.png)
</details>


<details>
  <summary>有声小说</summary>
  
  ![有声小说](/examples/有声小说.png)
</details>


## 参考

https://github.com/2noise/ChatTTS

https://github.com/6drf21e/ChatTTS_colab

https://github.com/CCmahua/ChatTTS-Enhanced

> [!Note]
> 本人是初学者，希望大家可以多提一点建议！
