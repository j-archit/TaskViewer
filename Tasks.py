import datetime
import json
import re

import tkinter as tk
import tkinter.ttk as ttk
# from tkinter import *
# from tkinter.ttk import *

treeColSpan     = 2
treeRowSpan     = 2
formColSpan     = 4
formRowSpan     = 6


class manager():
    def __init__(self, load_file = "tasklist.json"):
        self.taskFile   = load_file
        self.all        = []
        self.load_tasks()
        self.reorder()

    def save_tasks(self):
        with open(self.taskFile, "w") as f:
            json.dump(self.all, f)

    def load_tasks(self):
        with open(self.taskFile, "r") as f:
            try:
                self.all = json.load(f)
            except:
                print("Load Failed")

    def add_task(self, memo = "", priority = 10, due = 0, status = 0):
        self.all.append({
            "memo"      : memo, 
            "priority"  : priority, 
            "due"       : due,
            "status"    : status,
        })
        self.reorder()

    def edit_task(self):
        pass

    def delete_task(self):
        pass

    def add_group(self, memo = "", priority = 10, due = 0, status = 0):
        grp = {
                "memo"        : memo, 
                "priority"    : priority, 
                "status"      : status,
                "due"         : due,
                "tasks"       : []
        }
        self.all.append(grp)
        self.reorder()
        # return self.all.index(grp)
    
    def add_group_task(self, gid, memo = "", priority = 10, due = 0, status = 0):
        self.all[gid]['tasks'].append({
            "memo"      : memo, 
            "priority"  : priority, 
            "status"    : status,
            "due"       : due,
        })
        self.reorder()

    def edit_group(self, gid):
        pass

    def delete_group(self):
        pass

    def reorder(self):
        self.all.sort(key=lambda x: (x['priority'], x['due'], x['status']))
        for ind, task in enumerate(self.all):
            if task.get("tasks", 0) != 0:
                self.all[ind]["tasks"].sort(key=lambda x: (x['priority'], x['due'], x['status']))


def insertInTree(treeObj, manager_obj):
    taskTree = treeObj
    k = taskTree.get_children()
    [taskTree.delete(item) for item in k]
    for ID, task in enumerate(manager_obj.all):
        IID = ID + 1
        taskTree.insert(parent='', index='end', iid=IID, text=IID, values=tuple(task.values()))
        if task.get("tasks", 0) != 0:
            for subind, gtask in enumerate(task['tasks']):
                IIDs = 1000*IID + subind + 1
                taskTree.insert(parent=IID, index='end', iid=IIDs, text=IIDs, values=tuple(gtask.values()))

def placeTree(rootframe, manager_obj):
    displayFrame = ttk.Labelframe(
        master  = rootframe,
        relief  = tk.SUNKEN,
        text    = "All Tasks"
    )
    taskTree    = ttk.Treeview(
        master  = displayFrame
    )
    taskTree['columns'] = ("Task", "Priority", "Status", "Due")
    taskTree.column('#0', anchor=tk.CENTER, minwidth=25, width=75)
    taskTree.column('Task', anchor=tk.CENTER, minwidth=300, width=300)
    taskTree.column('Priority', anchor=tk.CENTER, minwidth=25, width=30)
    taskTree.column('Status', anchor=tk.CENTER, minwidth=50, width=50)
    taskTree.column('Due', anchor=tk.CENTER, minwidth=100, width=100)
    taskTree.heading('#0', text="ID",  anchor=tk.CENTER)
    taskTree.heading('Task', text="Task", anchor=tk.CENTER)
    taskTree.heading('Priority', text="Pri.", anchor=tk.CENTER)
    taskTree.heading('Status', text="Stat", anchor=tk.CENTER)
    taskTree.heading('Due', text="Due", anchor=tk.CENTER)

    insertInTree(taskTree, manager_obj)
            
    taskTree.grid(column=0, row=0, columnspan=treeColSpan, rowspan=treeRowSpan, **padding)
    displayFrame.grid(column=0, row=0, columnspan=treeColSpan, rowspan=treeRowSpan)

    return taskTree

def placeTaskAddEdit(editFrame, manager_obj, taskTree):
    rowSpan = treeRowSpan + 1
    addEdit     = tk.Variable()
    tasktitle   = tk.Variable() 
    taskpriority= tk.Variable()
    taskdue     = tk.Variable()
    groupenable = tk.Variable()
    grouptitle  = tk.Variable()

    # Select Add or Edit Task - RadioButton 
    def updateFormButtom():
        submitButtom["text"] = f"{'Add' if addEdit.get() == 'a' else 'Edit'} Task"
    Add         = ttk.Radiobutton(master=editFrame, text="Add", value="a", variable=addEdit, command=updateFormButtom)
    Edit        = ttk.Radiobutton(master=editFrame, text="Edit", value="e", variable=addEdit, command=updateFormButtom)
    addEdit.set("a")
    Add.grid    (column=0, row=rowSpan, sticky=tk.W)
    Edit.grid   (column=1, row=rowSpan, sticky=tk.W)

    # Task Memo Entry Box
    TitleL  = ttk.Label(master=editFrame, text="Memo", width=15)
    Title   = ttk.Entry(master=editFrame, textvariable=tasktitle, width=20)
    TitleL.grid(column=0, row=rowSpan+1, sticky=tk.W)
    Title.grid(column=1, row=rowSpan+1, sticky=tk.E)

    # Priority Entry Dropdown
    PriorityL   = ttk.Label(master=editFrame, text="Priority", width=15)
    Priority    = ttk.Combobox(master=editFrame, textvariable=taskpriority, width=5)
    Priority['values'] = tuple(range(1,11))
    Priority.state(['readonly'])
    taskpriority.set(10)
    PriorityL.grid(column=0, row=rowSpan+2, sticky=tk.W)
    Priority.grid(column=1, row=rowSpan+2, sticky=tk.E)

    # Task Group
    def groupEnDis():
        Group["state"] = groupenable.get()
    GroupC  = ttk.Checkbutton(master=editFrame, text="Group", variable=groupenable, onvalue="readonly", offvalue="disabled", command=groupEnDis)
    Group   = ttk.Combobox(master=editFrame, textvariable=grouptitle, width=17)
    GroupC.grid(column=0, row=rowSpan+3, sticky=tk.W)
    Group.grid(column=1, row=rowSpan+3, sticky=tk.E)

    Group['values'] = tuple(
        [f"{ID+1}. {task['memo']}" for ID, task in enumerate(manager_obj.all) if task.get("tasks", None) != None]
    )
    Group["state"] = "disabled"
    
    # Submit Button and Action
    def taskAddEdit():
        if addEdit.get() == "a":
            task = {
                "memo"      : Title.get(),
                "priority"  : int(Priority.get()),
                "due"       : 0,
                "status"    : 0
            }
            tasktitle.set("")
            taskpriority.set(10)
            if groupenable.get() == "readonly":
                k = re.search(r'(\d+)\.', grouptitle.get())
                taskGroup   = int(k.group(1)) - 1
                manager_obj.add_group_task(taskGroup, **task)
            else:
                manager_obj.add_task(**task)
            insertInTree(taskTree, manager_obj)
            Group['values'] = tuple(
               [f"{ID+1}. {task['memo']}" for ID, task in enumerate(manager_obj.all) if task.get("tasks", None) != None]
            )
    submitButtom    = ttk.Button(master=editFrame, text=f"{'Add' if addEdit.get() == 'a' else 'Edit'} Task", command=taskAddEdit)
    ttk.Separator(editFrame, orient="horizontal").grid(column=0, row=treeRowSpan+5)
    submitButtom.grid(column=0, row=rowSpan+5, sticky=tk.W)

    return Group

def placeGroupAddEdit(editFrame, manager_obj, taskTree, AETaskGroup):
    addEdit         = tk.Variable()
    grouptitle      = tk.Variable() 
    grouppriority   = tk.Variable()
    groupdue        = tk.Variable()
    groupenable     = tk.Variable()
    grouptitle      = tk.Variable()

    # Select Add or Edit Task - RadioButton 
    def updateFormButtom():
        submitButtom["text"] = f"{'Add' if addEdit.get() == 'a' else 'Edit'} Group"
    Add         = ttk.Radiobutton(master=editFrame, text="Add", value="a", variable=addEdit, command=updateFormButtom)
    Edit        = ttk.Radiobutton(master=editFrame, text="Edit", value="e", variable=addEdit, command=updateFormButtom)
    addEdit.set("a")
    Add.grid(column=0, row=0, sticky=tk.W)
    Edit.grid(column=1, row=0, sticky=tk.W)

    # Task Memo Entry Box
    TitleL  = ttk.Label(master=editFrame, text="Memo", width=15)
    Title   = ttk.Entry(master=editFrame, textvariable=grouptitle, width=20)
    TitleL.grid(column=0, row=1, sticky=tk.W)
    Title.grid(column=1, row=1, sticky=tk.E)

    # Priority Entry Dropdown
    PriorityL   = ttk.Label(master=editFrame, text="Priority", width=15)
    Priority    = ttk.Combobox(master=editFrame, textvariable=grouppriority, width=5)
    Priority['values'] = tuple(range(1,11))
    Priority.state(['readonly'])
    grouppriority.set(10)
    PriorityL.grid(column=0, row=2, sticky=tk.W)
    Priority.grid(column=1, row=2, sticky=tk.E)
    
    # Submit Button and Action
    def groupAddEdit():
        if addEdit.get() == "a":
            task = {
                "memo"      : Title.get(),
                "priority"  : int(Priority.get()),
                "due"       : 0,
                "status"    : 0
            }
            grouptitle.set("")
            grouppriority.set(10)
            manager_obj.add_group(**task)
            insertInTree(taskTree, manager_obj)
            AETaskGroup['values'] = tuple(
               [f"{ID+1}. {task['memo']}" for ID, task in enumerate(manager_obj.all) if task.get("tasks", None) != None]
            )

    submitButtom    = ttk.Button(master=editFrame, text=f"{'Add' if addEdit.get() == 'a' else 'Edit'} Group", command=groupAddEdit)
    submitButtom.grid(column=0, row=5, sticky=tk.W)


if __name__ == "__main__":
    padding = {
        "pady": 20,
        "padx": 20,
    }
    mobj = manager()
    root = tk.Tk()
    root.title("TaskView v1.0")

    # mobj.add_task("144")
    # mobj.add_group("Hi", priority=2)
    # mobj.add_group_task(0, 'memo', priority=3)

    taskTree = placeTree(root, mobj)
    sep = ttk.Separator(root, orient="horizontal").grid()

    editFrameTask   = ttk.Labelframe(
        master  = root,
        relief  = tk.RAISED,
        text    = "Add/Edit Tasks"
    )
    editFrameGroup   = ttk.Labelframe(
        master  = root,
        relief  = tk.RAISED,
        text    = "Add/Edit Groups"
    )
    editFrameTask.grid(column=0, row=4, columnspan=1, rowspan=6, sticky=tk.W, **padding)
    editFrameGroup.grid(column=1, row=4, sticky=tk.W, **padding)

    AETaskGroup = placeTaskAddEdit(editFrameTask, mobj, taskTree)
    placeGroupAddEdit(editFrameGroup, mobj, taskTree, AETaskGroup)

    root.mainloop()
    mobj.save_tasks()