import tkinter as tk
import tk_tools
import math
import serial
import threading
import queue
from time import sleep
from tkinter import *

class SerialThread(threading.Thread):
   def __init__(self, queue):
     threading.Thread.__init__(self)
     self.queue = queue

   def run(self):
     self.s1 = serial.Serial( 'COM3',9600)
     while 1:
          self.v = int(self.s1.readline())
          print(self.v)
          self.queue.put(self.v)


class DrawMeter(tk.Canvas):
   def __init__(self, parent, *args, **kwargs):
       tk.Canvas.__init__(self, parent, *args, **kwargs)
       self.config(bg = "grey")
       if (int(self['height'])*2 > int(self['width'])):
          side = int(self['width'])
       else:
          side = int(self['height'])
       self.X = side / 2
       self.Y = side / 2
       self.R = int(0.40 * float(side))
       self.start = 0
       self.end = 0
       self.queue = queue.Queue(maxsize=0)
       thread = SerialThread(self.queue)
       thread.start()
       self.background()
       self.Tick()
       self.needle()
       
   def background(self):
      bgColour = "black"
      a = self.X-self.X
      b = self.Y-self.Y
      c = self.X * 2
      d = self.Y * 2
      self.create_arc(a, b, c, d, fill = bgColour, start = 0, extent = 180)


   def Tick(self):
       length = self.R / 8
       for deg in range(1, 181, 2):
         rad = math.radians(deg)
         self.Tick_1(rad, length)
       for deg in range(10, 181, 10):
         rad =  math.radians(deg)
         self.Tick_1(rad, length * 2)

   def Tick_1(self, angle, length):
       cos = math.cos(angle)
       sin = math.sin(angle)
       radius = self.R
       X1 = self.X
       Y1 = self.Y
       x1 = X1 - radius * cos
       y1 = Y1 - radius * sin
       x2 = X1 - (radius - length) * cos
       y2 = Y1 - (radius - length) * sin
       self.create_line(x1, y1, x2, y2, fill = "white", width = 1)
   def drawText(self, start, end):
      value = start
      interval = end / 18
      length = self.R / 2
      for deg in range(10, 181, 10):
         rad = math.radians(deg)
         cos = math.cos(rad)
         sin = math.sin(rad)
         radius = self.R
         x3 = self.X  - (radius - length +50) * cos
         y3 = self.Y  - (radius - length +50) * sin
         self.create_text(x3, y3, text = str("{0:.1f}".format(value)), fill = "white", font = ("Arial" , 6, "bold"))
         value = value + interval

   def setRange(self, start, end):
      self.start = start
      self.end = end
      self.drawText(start, end)

   def needle(self):
      X2 = self.X
      Y2 = self.Y
      length = self.R - (self.R/4)
      self.meterHand = self.create_line(X2 , Y2 , X2-length ,Y2-length , fill = "red", width = 4)

   def updateNeedle(self):
      length = self.R
      deg = 180 * (self.queue.get() - self.start) / self.end + 10
      rad = math.radians(deg)
      self.coords(self.meterHand, self.X , self.Y , self.X - (length * math.cos(rad)), self.Y - (length * math.sin(rad)))

value = 0

def update_frame():
   meter.updateNeedle()
   container.after(200, update_frame)

root = tk.Tk()
container = tk.Frame(root)
container.pack()
meter = DrawMeter(container, height = 600, width = 600, bg = "red")
meter.setRange(10, 180)
meter.pack()
update_frame()
root.mainloop()