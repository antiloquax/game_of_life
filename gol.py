# gol.py - game of life
from tkinter import *
import time

def main():
    columns, delay = 45, 0
    gol = Gol(columns, delay)
    gol.run() 

class Gol():
    def __init__(self, size, delay):
        """Constructor. Set up some initial variables."""
        self.size, self.delay = size, delay
        self.generating = self.generations = self.alive = 0
        self.message = "Ready"
  
    def run(self):
        """Set up the GUI and start the loop."""
        self.root = Tk()
        self.gol = Frame(self.root)
        self.gol.grid()
        self.root.title("Game of Life")
        self.cells = [[] for x in range(self.size)]
        
        # use an image for the Cell, so we can specify size in pixels
        empty = PhotoImage("cell.png", master=self.root)
        
        # create the cells
        for row, col in [(row, col) for row in range(self.size) for col in range(self.size)]:
            self.cells[row].append(Cell(self.gol, image=empty, height=10, width=10, relief="flat", bg="grey", activebackground="white"))
            self.cells[row][col].grid(row=row,column=col)
            self.cells[row][col].initialise(self, row, col)
        self.flat = [cell for row in self.cells for cell in row]

        # buttons
        self.start = Button(self.gol, text = "Start")
        self.start["command"] = lambda: self.generate()
        self.start.grid(row=0, column = self.size+1,rowspan=3)

        self.stop = Button(self.gol, text = "Stop")
        self.stop["command"] = lambda: self.stopped()
        self.stop.grid(row=2, column = self.size+1,rowspan=3)

        self.reset = Button(self.gol, text = "Reset")
        self.reset["command"] = lambda: self.clear()
        self.reset.grid(row=4, column = self.size+1, rowspan=3)

        # labels
        self.gens = Label(self.gol,text = "Generations:\n0", fg="blue")
        self.gens.grid(row=6, column = self.size+1, rowspan=5, padx=3)

        self.alert = Label(self.gol, text=self.message, fg="blue")
        self.alert.grid(row=8, column = self.size+1, rowspan=5,padx=3)

        self.active = Label(self.gol, text= "Population:\n0", fg="blue")
        self.active.grid(row=10, column = self.size+1, rowspan=5,padx=3)
        
        self.root.mainloop()
        
    
    def clear(self):
        """Clear all cells."""
        self.generating = self.generations = 0
        self.message="Cleared"
        self.refresh()
        # Turn off all alive cells.
        for cell in [x for x in self.flat if x.status]:
            cell.toggle(self)
            
    def refresh(self):
        """Update labels."""
        self.gens.config(text = "Generations:\n" + str(self.generations))
        self.alert.config(text = self.message)
        
    def stopped(self):
        """The command bound to the stop button."""
        self.generating = False
        self.message = "Paused"
        
    def buttonsOn(self):
        """Make the buttons clickable."""
        for cell in self.flat:
            cell.config(state="normal")
            
    def buttonsOff(self):
        """Stop buttons from being clickable."""
        for cell in self.flat:
            cell.config(state="disabled")
        
    def generate(self):
        """Start the simulation."""
        self.generating = True
        self.message = "Running"
        self.buttonsOff()
        while self.generating:
            self.nextGen()
            self.gol.update()
            self.refresh()
            self.gol.after(self.delay)
        self.buttonsOn()
                
    def nextGen(self):
        """Make changes to display next generation."""
        # Find out status of next generation.
        temp =[]
        for cell in self.flat:
            count = sum([self.cells[r][c].status for (r, c) in cell.neighbours])
            if cell.status and count == 2:
                cell.next = 1
            elif count == 3:
                cell.next = 1
            else:
                cell.next = 0
            if cell.status != cell.next:
                temp.append(cell)

        # Apply changes
        self.changed = False
        for cell in temp:
            cell.toggle(self)
            self.changed = True
        if not self.changed:
            if not self.alive:
                self.message = "Extinction"
            else:
                self.message = "Stasis"
            self.generating = False
        else:
             self.generations +=1

class Cell(Button):
    """Cell class inherits from Button class."""
    def initialise(self, parent, row, col):
        """Associate the cell's command with toggle()."""
        self.status = 0
        self["command"] = lambda: self.toggle(parent)
        self.row = row
        self.col = col
        self.next = 0
        self.neighbours =[]
        
        # Assign neighbours. Taking care to avoid index errors.
        if row > 0:
            if col > 0:
                self.neighbours.append((row-1, col-1))
            if col < (parent.size - 1):
                self.neighbours.extend(((row-1, col), (row-1, col+1)))
        if row < (parent.size - 1):
            if  col > 0:
                self.neighbours.extend(((row, col-1), (row+1, col-1)))
            if col < (parent.size - 1):
                self.neighbours.extend(((row,col+1), (row+1, col), (row+1, col+1)))


    def toggle(self, parent):
        """Toggle cells, update count of living cells, update population label."""
        if self.status == 0:
            self.status = 1
            parent.alive += 1
            self.configure(bg="white")
        else:
            self.status = 0
            parent.alive -= 1
            self.configure(bg="grey")
        parent.active.config(text="Population:\n" + str(parent.alive))

if __name__ == "__main__":
    main()
