import datetime


def log(s):
    current_time = datetime.datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")
    line = f"[{formatted_time}] " + s
    print(line)

    with open("amonet.log", "a") as fout:
        fout.write(line + "\n")
