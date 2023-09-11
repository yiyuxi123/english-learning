import tkinter as tk
from tkinter import ttk

# 假设这些是你的工厂和效率数据
factories = {
    '钻头A': {'output': 10, 'input': {}},  # 每分钟产生10单位的资源A
    '钻头B': {'output': 8, 'input': {}},   # 每分钟产生8单位的资源B
    '兵工厂': {'output': 1, 'input': {'A': 5, 'B': 3}}  # 每分钟产生1单位的产品，需要5单位的A和3单位的B
}

def calculate():
    target_output = float(target_output_entry.get())
    factory_name = factory_var.get()
    factory_info = factories[factory_name]

    required_factories = target_output / factory_info['output']
    results.delete(1.0, tk.END)
    results.insert(tk.END, f"所需{factory_name}数量: {required_factories:.2f}\n")

    for input_resource, amount in factory_info['input'].items():
        results.insert(tk.END, f"每分钟所需{input_resource}: {required_factories * amount:.2f}\n")

# GUI
window = tk.Tk()
window.title("工厂模拟")

frame = ttk.Frame(window, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

factory_var = tk.StringVar()
factory_var.set('钻头A')  # default value
factory_menu = ttk.OptionMenu(frame, factory_var, '钻头A', *factories.keys())
factory_menu.grid(row=0, column=1)

ttk.Label(frame, text="选择工厂:").grid(row=0, column=0)
ttk.Label(frame, text="目标每分钟产值:").grid(row=1, column=0)

target_output_entry = ttk.Entry(frame)
target_output_entry.grid(row=1, column=1)

ttk.Button(frame, text="计算", command=calculate).grid(row=2, columnspan=2)

results = tk.Text(window, wrap=tk.WORD, width=40, height=10)
results.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

window.mainloop()
