import subprocess
import time

def run_command_as_daemon(command):
    while True:
        try:
            # 运行命令
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            # 处理命令运行出错的情况
            print(f"命令 '{command}' 执行出错: {e}")
        # 每次执行完命令后休眠一段时间，避免过于频繁地执行
        time.sleep(60)  # 休眠60秒

if __name__ == "__main__":
    # 要运行的命令
    command_to_run = "python main.py"
    # 运行命令作为守护进程
    run_command_as_daemon(command_to_run)