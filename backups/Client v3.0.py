import wx
import json
import _thread
import time
import socket


class ContentPanel(wx.SplitterWindow):

    # parent为父类实例
    def __init__(self, parent, logic, contact = {"type":11,"id":0,"name":"未知"}):
        super(ContentPanel, self).__init__(parent,id = -1, style= wx.SP_LIVE_UPDATE | wx.SP_BORDER | wx.SP_3DSASH)
        self.logicClient = logic
        self.contact = contact

        upper = wx.Panel(self)
        lower = wx.Panel(self)

        self.SplitHorizontally(upper, lower, -220)
        self.SetMinimumPaneSize(120)

        self.contact_name = wx.StaticText(upper, -1, label = self.contact["name"])
        font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.contact_name.SetFont(font)
        
        self.content_text = wx.TextCtrl(upper,style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.BORDER_NONE)
        self.input_text = wx.TextCtrl(lower,style=wx.TE_MULTILINE | wx.BORDER_NONE)
        self.input_text.SetFont(wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        ctrl_panel = wx.Panel(lower)
        send_button = wx.Button(ctrl_panel,label='发送')
        send_button.Bind(wx.EVT_BUTTON,self.OnClick_sendButton)
        
        # boxSizer
        upperbox = wx.BoxSizer(wx.VERTICAL)
        upper.SetSizer(upperbox)
        upperbox.Add(self.contact_name,proportion =0,flag = wx.EXPAND | wx.RIGHT | wx.TOP , border = 15)
        upperbox.Add(self.content_text,proportion = 1,flag = wx.EXPAND | wx.RIGHT | wx.TOP , border=15)
        
        lowerbox = wx.BoxSizer(wx.VERTICAL)
        lower.SetSizer(lowerbox)
        lowerbox.Add(self.input_text,proportion = 1,flag = wx.EXPAND|wx.RIGHT|wx.BOTTOM , border=15)
        lowerbox.Add(ctrl_panel,proportion = 0,flag = wx.EXPAND|wx.RIGHT , border=20)
        
        
    def setContact(self,contact={"type":11, "id":0, "name":"未知"}):
        self.contact = contact
        self.contact_name.SetLabel(contact["name"])
    # 显示消息
    def showMessage(self,title,text,type = 0):
        if type == 0:
            titleColor = wx.Colour(0,128,64)
        else:
            titleColor = wx.Colour(0,0,255)
        titleFont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False)
        textFont = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        
        self.content_text.SetDefaultStyle(wx.TextAttr(titleColor,wx.NullColour,titleFont)) # 文本样式
        self.content_text.AppendText(title+'\n')

        self.content_text.SetDefaultStyle(wx.TextAttr(wx.BLACK,wx.NullColour,textFont))       
        self.content_text.AppendText(text+'\n')

    # 发送按钮
    def OnClick_sendButton(self,event):
        text = self.input_text.GetValue()
        text = text.strip('\n')
        if text and self.contact['id'] >= 0: # 0为系统，控制能不能给系统发送消息
            theTime = time.strftime("%H:%M:%S", time.localtime()) # 时间 %Y-%m-%d %H:%M:%S
            if self.logicClient.sendMsg(self.contact['type'],text,self.contact['id'],{"time":theTime}):
                #将消息显示到窗口
                title = "我 " + theTime
                message = " " + text
                self.showMessage(title,message)
                self.input_text.Clear()
            else:    
                self.showMessage("系统消息：发送数据失败！","")
 
## -------------- sp --------------------- ##


class ClientUI(wx.Frame):
    
    contacts = [] # 联系人
    contentPanels = [] # 所有面板
    last_selection = 0

    def __init__(self,logic):
        super().__init__(parent=None, title="py聊天", size=(1024, 768))

        self.Center()
        self.logicClient = logic

        swindow = wx.SplitterWindow(parent=self, id=-1, style= wx.SP_LIVE_UPDATE)
        
        left = wx.Panel(parent=swindow)
        self.right = wx.Panel(parent=swindow)
        # 设置左右布局的分割窗口left和right
        swindow.SplitVertically(left, self.right, 100)
        swindow.SetMinimumPaneSize(260) 
        
        # 创建布局管理器
        leftbox = wx.BoxSizer(wx.VERTICAL)
        left.SetSizer(leftbox)
        
        # 为right面板设置一个布局管理器
        self.rightbox = wx.BoxSizer(wx.VERTICAL)
        self.right.SetSizer((self.rightbox))

        # left 联系人面板
        contact_tab = wx.StaticText(left, -1, label = " 联系人列表:", style = wx.ST_ELLIPSIZE_END)
        contact_tab.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        leftbox.Add(contact_tab,0,flag = wx.TOP | wx.LEFT, border = 15)
        self.contact_list = wx.ListBox(left,style = wx.LB_SINGLE | wx.LB_OWNERDRAW | wx.BORDER_NONE)
        self.contact_list.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False,faceName="微软雅黑"))
        self.contact_list.SetBackgroundColour("#FAFAFA")
        leftbox.Add(self.contact_list, 1, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, border=15)

        self.init()

    def init(self):
        self.contact_list.Bind(wx.EVT_LISTBOX, self.On_listSelect)

        for i in range(20):
            pp= ContentPanel(self.right, self.logicClient)
            self.contentPanels.append(pp)
            self.rightbox.Add(pp, proportion = 1, flag=wx.EXPAND|wx.BOTTOM, border = 15)
            pp.Hide()
        
        self.refreshUserList([{"type": 11, "id": 0, "name": "系统"}])
        self.contentPanels[0].Show()

        # 登录
        dlg = wx.TextEntryDialog(self, "请输入您的PY号", "登录", style =  wx.OK | wx.CANCEL)
        if  dlg.ShowModal() == wx.ID_OK:
            self.logicClient.setMe(int(dlg.GetValue()))
            #self.Close(True)

 
    # 用户列表监听
    def On_listSelect(self,event):
        selection = event.GetEventObject().GetSelection()
        if self.last_selection >= 0:
            self.contentPanels[self.last_selection].Hide()
        self.contact_list.SetItemBackgroundColour(selection,"#FAFAFA")
        self.contentPanels[selection].Show()
        self.contact_list.Refresh()
        self.right.Layout()

        self.last_selection = selection

    # 刷新联系人列表 datas:[{"id":3,"type":11or13,"name":"cyt"}]
    def refreshUserList(self,datas = []):
        for i in range(len(self.contacts)-1, -1, -1):
            if self.contacts[i]['id'] == 0:
                continue
            isfind = False
            for nu in datas:
                if self.contacts[i]['id'] == nu['id']:
                    isfind = True
                    # 名字不对改名字
                    if self.contacts[i]['name'] != nu['name']:
                        self.contacts[i]['name'] = nu['name']
                        self.contentPanels[i].setContact(nu)
                    datas.remove(nu)
                    break
            if not isfind:
                self.contacts.pop(i)
                #self.rightbox.Remove(i) #Detach移除不破坏，remove移除破坏
                #self.rightbox.Layout()
                po = self.contentPanels.pop(i)
                self.contentPanels.append(po)

        for su in datas:
            self.contacts.append(su)
            self.contentPanels[len(self.contacts)-1].setContact(su)
            

        if self.contact_list.Items and len(self.contact_list.Items):
            self.contact_list.Clear()
            pass

        # 插入系统用户
        #self.contacts.insert(0,{"type": 11, "id": 0, "name": "系统"})

        # 联系人列表显示
        for i,sub in enumerate(self.contacts):
            if sub['type'] == 11:
                content = " " + sub['name'] + "（py：" + str(sub['id']) + "）"
            else:
                content = " 群：" + sub['name'] + "（PY：" + str(sub['id']) + "）"
            self.contact_list.Append(content)
            self.contact_list.SetItemBackgroundColour(i,"#FAFAFA")

        self.contact_list.Refresh()

    # 传递消息
    def addMessage(self, to, title,text,type = 0):
        # 暂时添加到0中
        for index,us in enumerate(self.contacts):
            if us['id'] == to:
                if not self.last_selection == index:
                    self.contact_list.SetItemBackgroundColour(index,"#F0A670")
                    self.contact_list.Refresh()
                self.contentPanels[index].showMessage(title,text,type)
                return True
        return False
    
## -------------- sp --------------------- ##


class Client():
    title = 'Python聊天TCP'
    serverIP = '192.168.200.233'
    serverPort = 1367
    hostIP = '192.168.200.233'
    hostPort = 3784
    status = 0 # 1为在线 # 0为离线

    me = -1 #自己的id
    myName = ""
    contacts = []

    def setMe(self,id):
        self.me = id
        pass

    # sendMsg(self,type,data,to,extra = {})函数 成功返回True，失败返回False
    def sendMsg(self,type,data,to,extra= {}):
        if not data:
            return False
        try:
            self.sendSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sendSock.connect((self.serverIP, self.serverPort))
            #格式化数据并发送
            msg = {"type":type, "from":self.me, "to":to, "data":data}
            json_string = json.dumps(dict(msg,**extra))
            self.sendSock.send(bytes(json_string, encoding = "utf8"))
            self.sendSock.close()
            return True
        except:
            self.sendSock.close()
            return False
        return False


    # 开一个线程接受一个用户的处理
    def receive(self,sock,addr):
        while True:
            try:
                data = sock.recv(1024).decode(encoding = "utf8")
                if not data:
                    break
                msg = json.loads(data)

                if msg['type'] == 2:
                    break
                elif msg['type'] == 4:
                    if msg['code'] == "contacts":
                        #获取联系人列表
                        self.contacts = msg['data']
                        # 除去自己
                        for u in self.contacts:
                            if u['id'] == self.me:
                                self.myName = u['name']
                                self.contacts.remove(u)
                                break
                        self.ui.refreshUserList(self.contacts)
                elif msg['type'] == 12 or msg['type'] == 14:
                    data = msg['data']
                    for ms in data:
                        title = ms['fromName']+" "+ms['time']
                        message = " " + ms['msg']
                        self.ui.addMessage(ms["from"], title, message,1)
            except:
                self.ui.addMessage(0, "系统消息：接受数据失败！", "")
        sock.close()

    # 接受消息线程
    def receiveThread(self):
        try:
            self.receiveSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.receiveSock.bind((self.hostIP,self.hostPort))
            self.receiveSock.listen(5) #允许最大连接数为5
            self.buffersize = 1024

            while True:
                sock,addr = self.receiveSock.accept()
                t = _thread.start_new_thread(self.receive,(sock,addr))

        except:
            self.ui.addMessage(0, "系统消息：", "接受线程错误，请重启程序！")
        finally:
            self.receiveSock.close()

    # 同步消息
    def syncServer(self):
        while True:
            if self.status == 0:
                if self.sendMsg(1,"login",0,{"ip":self.hostIP,"port":self.hostPort}):
                    self.status = 1
                    clientUI.SetTitle(self.title + " - 已登录")
                    # 请求联系人列表
                    if self.sendMsg(3,"contacts",0,{"code":"contacts"}):
                        clientUI.SetTitle(self.title +" "+ self.myName+ " - 已登录")   
                else:
                    clientUI.SetTitle(self.title + " - 连接失败")
            elif self.status > 0:
                if not self.sendMsg(1,"hello",0) :
                    self.status = 0
                    clientUI.SetTitle(self.title + " - 连接失败")
            time.sleep(5)
        self.ui.addMessage(0, "系统消息：同步线程（syncServer）异常退出！", "")

    def startRun(self,ui):
        self.ui = ui
        _thread.start_new_thread(self.syncServer,()) #同步状态线程
        _thread.start_new_thread(self.receiveThread,()) # 接受消息线程
        


if __name__ == '__main__':
    app = wx.App(False)
    client = Client()
    clientUI = ClientUI(client)
    clientUI.Show(True)
    client.startRun(clientUI)
    app.MainLoop()





# code=1 客户端向服务端发送登录，问候信息
# code=2 
# code=3 客户端查询用户信息（例请求联系人列表code="contacts"）
# code=4 服务端返回结果(返回联系人列表code="contacts")
# code=5 客户端向服务端发送更改信息（ip，port等）
# code=11,13 客户端向服务端发送消息（单发，群发）
# code=12 服务端向客户端发送消息
