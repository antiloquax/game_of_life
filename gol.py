"""gol.py - game of life using tkinter. """

from tkinter import *
import time

def main():
    """Create an instance of gol class and run it."""
    columns, delay = 30, 0
    gol = Gol(columns, delay)
    gol.run() 

class Gol():
    def __init__(self, size, delay):
        """Constructor. Set up some initial variables."""
        self.size, self.delay = size, delay
        self.generating = self.generations = self.alive = 0
        self.message = "Ready"
        
        # Set of live cells & their neighbours.
        self.watch = set()
  
    def run(self):
        """Set up the GUI and start the loop."""
        self.root = Tk()
        self.gol = Frame(self.root)
        self.gol.grid()
        self.root.title("Game of Life")
        
        # Create an empty 2d list to hold all cells.
        self.cells = [[] for x in range(self.size)]
        
        # Flat list of cells - used in some GUI commands.
        self.flat = [cell for row in self.cells for cell in row]
        
        # Use an image for the Cell, so we can specify size in pixels.
        empty = PhotoImage("cell.png", master=self.root)
        
        # Create the cells.
        for row, col in [(row, col) for row in range(self.size) for col in range(self.size)]:
            self.cells[row].append(Cell(self.gol, image=empty, height=10, width=10, relief="flat", bg="grey", activebackground="white"))
            self.cells[row][col].grid(row=row,column=col)
            self.cells[row][col].initialise(self, row, col)

        # Set up the neighbour data.
        for c in [cell for row in self.cells for cell in row]:
            c.addNeighbours(self)

        # Buttons.
        self.start = Button(self.gol, text = "Start")
        self.start["command"] = lambda: self.generate()
        self.start.grid(row=0, column = self.size+1,rowspan=3)

        self.stop = Button(self.gol, text = "Stop")
        self.stop["command"] = lambda: self.stopped()
        self.stop.grid(row=2, column = self.size+1,rowspan=3)

        self.reset = Button(self.gol, text = "Reset")
        self.reset["command"] = lambda: self.clear()
        self.reset.grid(row=4, column = self.size+1, rowspan=3)

        # Labels.
        self.gens = Label(self.gol,text = "Generations:\n0", fg="blue")
        self.gens.grid(row=6, column = self.size+1, rowspan=5, padx=3)

        self.alert = Label(self.gol, text=self.message, fg="blue")
        self.alert.grid(row=8, column = self.size+1, rowspan=5,padx=3)

        self.active = Label(self.gol, text= "Population:\n0", fg="blue")
        self.active.grid(row=10, column = self.size+1, rowspan=5,padx=3)

        # Start the loop running.
        self.root.mainloop()
        
    
    def clear(self):
        """Clear all cells."""
        self.generating = self.generations = 0
        self.message="Cleared"
        self.refresh()
        # Turn off all alive cells. Make into a list first, so we can modify the set.
        for cell in [x for x in self.watch if x.status]:
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
        # List of cells that will change.
        temp =[]

        # Cells we can remove from watch list.
        ignore = set()
        
        for cell in self.watch:
            if cell.willChange():
                temp.append(cell)
            # If a cell's neighbours are all dead, remove from the list.
            if not cell.nCount:
                ignore.add(cell)

        # Update watch list.
        self.watch = self.watch.difference(ignore)

        # Apply changes - only to cells that have changed.
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
        
        # How many live neighbours.
        self.nCount = 0

    def willChange(self):
        """Check if cell lives or dies."""
        self.nCount = sum([x.status for x in self.neighbours])
            # These are the rules for whether the cell lives on.
        if self.status and self.nCount == 2:
            self.next = 1
        elif self.nCount == 3:
            self.next = 1
        else:
            self.next = 0
        if self.status != self.next:
            return 1
        else:
            return 0

    def addNeighbours(self, parent):
        """Assign neighbours. Taking care to avoid index errors."""
        if self.row > 0:
            if self.col > 0:
                self.neighbours.append(parent.cells[self.row-1][self.col-1])
            if self.col < (parent.size - 1):
                self.neighbours.extend((parent.cells[self.row-1][self.col],
                                        parent.cells[self.row-1][self.col+1]))
        if self.row < (parent.size - 1):
            if  self.col > 0:
                self.neighbours.extend((parent.cells[self.row][self.col-1],
                                        parent.cells[self.row+1][self.col-1]))
            if self.col < (parent.size - 1):
                self.neighbours.extend((parent.cells[self.row][self.col+1],
                                       parent.cells[self.row+1][self.col],
                                       parent.cells[self.row+1][self.col+1]))


    def toggle(self, parent):
        """Toggle cells, update count of living cells, update population label."""
        if self.status == 0:
            self.status = 1
            parent.alive += 1
            # Add to watch list.
            parent.watch.add(self)
            # Add neighbours to watch list.
            for n in self.neighbours:
                parent.watch.add(n)
            self.configure(bg="white")
        else:
            self.status = 0
            parent.alive -= 1
            self.configure(bg="grey")
        parent.active.config(text="Population:\n" + str(parent.alive))

if __name__ == "__main__":
    main()
