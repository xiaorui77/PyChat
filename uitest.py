import wx

class CourseListCtrl(wx.ListCtrl):
    def __init__(self, parent, subDatas, size, id=-1, pos=(0, 0), style=wx.LC_REPORT):
        wx.ListCtrl.__init__(self,parent, id, pos, size, style)

        self.subDatas = subDatas
        self.InitUI()
        
    def InitUI(self):
        il = wx.ImageList(45, 45, True)
        logoBmp = wx.Bitmap(r"D:\book_icon.png", wx.BITMAP_TYPE_PNG)
        il.Add(logoBmp)

        self.AssignImageList(il, wx.IMAGE_LIST_SMALL)
        self.ShowListDatas(self.subDatas)
        self.SetColumnWidth(-1,200)

    def ShowListDatas(self, datas):
        self.subDatas = datas
        for sub in self.subDatas:
            index = sub['id']
            content = '  '+ sub['nickname']
            self.InsertImageStringItem(index, content, 0)
            self.InsertImageStringItem(index,"在线",1)

    def refreshDataShow(self, newDatas):
        self.datas = newDatas
        self.DeleteAllItems()
        self.ShowListDatas(self.datas)
        self.Refresh()

class ServerUI(wx.Frame):
    def __init__(self,parent=None,id=-1,title=''):
        wx.Frame.__init__(self,parent,id,title,size=(1024,600))
        self.panel = wx.Panel(self)
        self.panel_user = CourseListCtrl(self.panel,[{'id':1,'nickname':"yuwen",'status':1},{'id':1,'nickname':"yingyfdsfsdfu","status":0}],size=(600,600))



if __name__ == '__main__':
    app = wx.App(False)
    serverUI = ServerUI(None, wx.ID_ANY, "Hello, World!")
    serverUI.Show(True)
    
    app.MainLoop()