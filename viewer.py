#!/usr/bin/python
# -*- coding=utf8 -*-


import wx
import wx.lib.newevent
import wx.html
from lxml import etree

from model import HTMLRenderer

print wx.version()

NextCommandEvent, EVT_NEXT = wx.lib.newevent.NewCommandEvent()
PrevCommandEvent, EVT_PREV = wx.lib.newevent.NewCommandEvent()
ReblogCommandEvent, EVT_REBLOG = wx.lib.newevent.NewCommandEvent()



class ContentViewer(wx.html.HtmlWindow):
  '''
    Basic Keybinding
    'j' : next
    'k' : prev
    't' : reblog (open text box for comment)
    'q' : quit

   need to add:
    open link with...

  '''

  def __init__(self, parent, id):
    wx.html.HtmlWindow.__init__(self, parent, id)
    self.Bind(wx.EVT_CHAR, self.OnChar)
    self.Bind(EVT_NEXT, self.OnNext)
    self.Bind(EVT_PREV, self.OnPrev)
    self.Bind(EVT_REBLOG, self.OnReblog)
    #self.Bind(EVT_Close, self.Close)
    self.renderer = HTMLRenderer()

  def Prev(self):
    wx.PostEvent(self, PrevCommandEvent(0))

  def Next(self):
    wx.PostEvent(self, NextCommandEvent(0))

  def Reblog(self):
    wx.PostEvent(self, ReblogCommandEvent(0))

  def OnChar(self, evt):
    key =  evt.GetUniChar()
    
    print 'got %i'%(key, )
    if key == ord('k'):
      self.Prev()
    elif key == ord('j'):
      self.Next()
    elif key == ord('t'):
      self.Reblog()
    elif key == ord('q'):
      self.Close()
    else:
      pass

  def SetContent(self, post):
    html = self.renderer.render(post)
    print html
    self.SetPage(html)

  def OnNext(self, event):
    print 'OnNext'

  def OnPrev(self, event):
    print 'OnPrev'
    
  def OnReblog(self, event):
    print 'OnReblog'


if __name__ == '__main__':
  app = wx.App(False)
  frame = wx.Frame(None, wx.ID_ANY, 'Hey Tumblr Junkie!')

  cv = ContentViewer(frame, -1)
  cv.SetPage('<html><img src="Flowers002.JPG"/></html>')


  frame.Show(True)
  app.MainLoop()

