import tkinter as tk
from tkinter import ttk

# 工厂和效率数据
factories = {
    '煤炭采集器': {'output': {'煤炭': 60}, 'input': {}, 'power': 5, 'tech': '赛普罗'},
    '石墨压缩机': {'output': {'石墨': 0.66}, 'input': {'煤炭': 1.33}, 'power': 10, 'tech': '埃里克尔'}
}

def calculate():
    target_output = float(target_output_entry.get())
    factory_name = factory_var.get()
    tech_tree = tech_var.get()
    
    factory_info = factories[factory_name]
    
    # 检查科技树
    if tech_tree != '全部' and factory_info['tech'] != tech_tree:
        results.insert(tk.END, f"{factory_name} 不在选择的科技树 {tech_tree} 中。\n")
        return

    required_factories = target_output / list(factory_info['output'].values())[0]
    
    results.delete(1.0, tk.END)
    results.insert(tk.END, f"所需{factory_name}数量: {required_factories:.2f}\n")
    results.insert(tk.END, f"总电力需求: {required_factories * factory_info['power']:.2f}\n")
    
    for input_resource, amount in factory_info['input'].items():
        results.insert(tk.END, f"每秒所需{input_resource}: {required_factories * amount:.2f}\n")

        input_factory_name = [name for name, info in factories.items() if input_resource in info['output']][0]
        required_input_factories = (required_factories * amount) / factories[input_factory_name]['output'][input_resource]
        results.insert(tk.END, f"所需{input_factory_name}数量: {required_input_factories:.2f}\n")

# GUI
window = tk.Tk()
window.title("工厂模拟")

frame = ttk.Frame(window, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

factory_var = tk.StringVar()
factory_var.set('石墨压缩机')  # 默认值

tech_var = tk.StringVar()
tech_var.set('全部')  # 默认值

factory_menu = ttk.OptionMenu(frame, factory_var, '石墨压缩机', *factories.keys())
factory_menu.grid(row=0, column=1)

tech_menu = ttk.OptionMenu(frame, tech_var, '全部', '赛普罗', '埃里克尔')
tech_menu.grid(row=1, column=1)

ttk.Label(frame, text="选择工厂:").grid(row=0, column=0)
ttk.Label(frame, text="选择科技树:").grid(row=1, column=0)
ttk.Label(frame, text="目标每秒产值:").grid(row=2, column=0)

target_output_entry = ttk.Entry(frame)
target_output_entry.grid(row=2, column=1)

ttk.Button(frame, text="计算", command=calculate).grid(row=3, columnspan=2)

results = tk.Text(window, wrap=tk.WORD, width=40, height=10)
results.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

window.mainloop()
