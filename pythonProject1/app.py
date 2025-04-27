from flask import Flask, render_template, make_response
import time
import random

app = Flask(__name__)

# 初始化任务列表和打印机状态
tasks = []
printer_busy = False
last_processing_time = 0


# 模拟生产者提交任务
def producer_submit_task():
    global tasks
    producer_id = random.randint(0, 2)
    task_id = len(tasks)
    submit_time = time.time()
    task = {
        "time": submit_time,
        "source": f"Producer {producer_id}",
        "task": f"submitted task {task_id}",
        "status": "submitted"
    }
    tasks.append(task)


# 模拟打印机处理任务
def printer_process_task():
    global tasks, printer_busy, last_processing_time
    if not printer_busy and tasks:
        for task in tasks:
            if task["status"] == "submitted":
                task["status"] = "processing"
                printer_busy = True
                last_processing_time = time.time()
                break


# 模拟任务完成
def task_complete():
    global tasks, printer_busy
    for task in tasks:
        if task["status"] == "processing":
            elapsed_time = time.time() - last_processing_time
            if elapsed_time > random.uniform(1, 3):  # 处理时间在1 - 3秒之间
                task["status"] = "completed"
                printer_busy = False
                break


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@app.route('/')
def index():
    # 模拟任务状态变化
    if random.random() < 0.3:  # 30% 的概率提交新任务
        producer_submit_task()
    printer_process_task()
    task_complete()

    # 计算处理中、排队中、已完成任务数量
    processing_count = sum(1 for task in tasks if task["status"] == "processing")
    queued_count = sum(1 for task in tasks if task["status"] == "submitted")
    completed_count = sum(1 for task in tasks if task["status"] == "completed")

    # 格式化任务列表
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            "time": "{:.6f}".format(task["time"]),
            "source": task["source"],
            "task": task["task"]
        })

    return render_template(
        'index.html',
        tasks=formatted_tasks,
        processing_count=processing_count,
        queued_count=queued_count,
        completed_count=completed_count
    )


if __name__ == '__main__':
    app.run(debug=True)
