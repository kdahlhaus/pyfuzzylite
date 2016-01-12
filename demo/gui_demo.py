"""
This is a simple GUI demo (using TKinter) to exercise
the rowing strategy fuzzy logic engine.
"""

from Tkinter import *

from fuzzy_logic_dynrow import get_fuzzy_output



class Application(Frame):
    def say_hi(self):
        print "hi there, everyone!"

    def createWidgets(self):
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        self.aib = Scale(self, from_=0.0, to=2000.0, command=self.update )
        self.aib.pack({"side":"left", "fill":"y"})

        self.ob = Scale(self, from_=0.0, to=2000.0, command=self.update)
        self.ob.pack({"side": "left", "fill":"y"})

        self.output = Text(self)
        self.output.pack({"side": "left", "fill":"both"})



    def update(self, control):
        self.output.delete(1.0, END)

        aib_dist=self.aib.get()
        ob_dist=self.ob.get()
        
        action, location, relative_location = get_fuzzy_output( aib_dist, ob_dist )
        output = action.defuzzify()
        rl_raw = aib_dist - ob_dist

        desc = "ai boat is %s meters %s the other boat\n\n"%(abs(rl_raw), "behind" if rl_raw<0 else "ahead")
        self.output.insert(END, desc)
        self.output.insert(END, "Action:\n")
        self.output.insert(END, action.fuzzify(output))

        self.output.insert(END, "\n\nRelative Location:\n")
        self.output.insert(END, relative_location.fuzzify(rl_raw))

        self.output.insert(END, "\n\nLocation in Race:\n")
        self.output.insert(END, location.fuzzify(aib_dist))




    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()

