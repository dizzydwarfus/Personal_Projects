from tkinter import *

root = Tk()
root.title('FirstGUI')
root.geometry('1800x900')
# root.state('zoomed')

###################################

# Label Widget

###################################

test_label = Label(root, text='This is a label', font=("Verdano", 35))
test_label.grid(row=0, column=0)

test_label_2 = Label(root, text='Hello there')
test_label_2.grid(row=1, column=0)

###################################

# Frame Widget

###################################

frame = LabelFrame(root)
frame.grid(row=0, column=2, padx=30, pady=32, ipadx=60, ipady=62)

test_label_inframe = Label(
    frame, text='This is a label inside a frame', font=("Verdano", 35))
test_label_inframe.grid(row=0, column=0)

root.mainloop()
