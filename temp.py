
def save(*args, **kwargs):
    # 在这里添加你的自定义逻辑
    print("自定义逻辑：在保存之前执行")
    filename = kwargs.pop("filename")
    print(filename)
    # 假设你想要使用一个额外的参数 'filename'
    # if "filename" in kwargs:
    #     filename = kwargs.pop("filename")

    # 调用父类的 save 方法

    # 可以在这里添加更多的自定义逻辑
    
    print(kwargs)


save(filename="example_filename.txt",info="test")
