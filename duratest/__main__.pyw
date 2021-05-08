# Copyright (c) 2021 Admiral Instruments

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from signal import *
import asyncio
from experiment import Experiment, ExperimentError
import logging
import tkinter as tk
from tkinter import messagebox, VERTICAL, HORIZONTAL, N, S, E, W , ttk
import sys
import threading
import queue
from tkinter.scrolledtext import ScrolledText


def threadHandler(loop,logger,exp):
    try:
        loop.run_until_complete(exp.run_experiment())
        logger.info("Experiment Finished successfully")

        def cleanup():
            raise ExperimentError("Experiment cancelled before its specified duration.")

        for sig in (SIGABRT, SIGBREAK, SIGILL, SIGINT, SIGSEGV, SIGTERM):
            signal(sig, cleanup)

    except BaseException as err:
        logger.fatal(str(err) + " Aborting Experiment.")
    finally:
        tasks = asyncio.all_tasks(loop)
        if ((len(tasks) != 0)):
            loop.run_until_complete(asyncio.gather(*tasks))
            loop.run_until_complete(exp.stop_experiment())
            logger.info("Experiment finished.")



class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

class ConsoleUi:
    def __init__(self, frame,logger):
        self.frame = frame
        self.logger = logger
        
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.queue_handler.setFormatter(formatter)
        self.logger.addHandler(self.queue_handler)
        
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)


class App:
    
    def __init__(self, root,loop,logger,exp):
        self.root = root
        self.loop = loop
        self.logger = logger
        self.exp = exp

        root.title('Logging Handler')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Create the panes and frames
        vertical_pane = ttk.PanedWindow(self.root, orient=VERTICAL)
        vertical_pane.grid(row=0, column=0, sticky="nsew")
        horizontal_pane = ttk.PanedWindow(vertical_pane, orient=HORIZONTAL)
        vertical_pane.add(horizontal_pane)
        
        console_frame = ttk.Labelframe(horizontal_pane, text="Console")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        horizontal_pane.add(console_frame, weight=1)
        
        self.console = ConsoleUi(console_frame,self.logger)

        def key_pressed(event):
            self.quit();

        self.root.bind("<Control-q>",key_pressed)
        self.root.bind("<Control-c>",key_pressed)
        self.root.protocol('WM_DELETE_WINDOW', self.quit)

    def quit(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
                tasks = asyncio.all_tasks(self.loop)
                if ((len(tasks) != 0)):
                    self.loop.run_until_complete(asyncio.gather(*tasks))
                    self.loop.run_until_complete(self.exp.stop_experiment())
                    self.logger.info("Application is close.")
                self.root.destroy()
                
            

def main():
    root = tk.Tk()
    
    logger = logging.getLogger("experiment")
    exp = Experiment()  # note, experiment.json needs to be in the current working directory!!!
    loop = asyncio.get_event_loop()

    threading.Thread(target=threadHandler, args=(loop,logger,exp,), daemon=True).start();
    app = App(root,loop,logger,exp)
    app.root.mainloop()

if __name__ == "__main__":
    main()