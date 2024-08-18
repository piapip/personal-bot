from tkinter import ttk
import tkinter as tk

def SetStyle() -> None:
    # Set style for the Entry, to make the text having some type of padding.
    ttk.Style().configure('pad.TEntry', padding='5 3 3 3 ')

# StyledEntry returns an entry with nicing padding style.
def StyledEntry(master: tk.Frame) -> ttk.Entry:
    return ttk.Entry(master=master, style="pad.TEntry")
