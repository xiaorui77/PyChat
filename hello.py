#!/usr/bin/python
# -*- coding: UTF-8 -*-
import _tkinter
import tkinter

import json
import socket
import _thread
import time
import tkinter.font as tkFont


class Client():
     
    title = 'Python聊天TCP'
    serverIP = '127.0.0.1'
    serverPort = 1367
     
    #初始化类的相关属性，类似于构造方法
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title(self.title + '正在初始化')
         
        #窗口面板
        self.frame = [tkinter.Frame(),tkinter.Frame(),tkinter.Frame(),tkinter.Frame()]
 
        #显示消息
        self.chatTextScrollBar = tkinter.Scrollbar(self.frame[0])
        self.chatTextScrollBar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
        
        self.chatText = tkinter.Text(self.frame[0],width=80,height=18)
        #self.chatText.configure(selectbackground='FF')
        #self.chatText.configure(selectforeground='#060606')
        self.chatText['yscrollcommand'] = self.chatTextScrollBar.set
        self.chatText.pack(expand=1,fill=tkinter.BOTH)
        self.chatTextScrollBar['command'] = self.chatText.yview()
        self.frame[0].pack(expand=1,fill=tkinter.BOTH)
         
        #分隔
        label = tkinter.Label(self.frame[1],height=2)
        label.pack(fill=tkinter.BOTH)
        self.frame[1].pack(expand=1,fill=tkinter.BOTH)
         
        #输入消息Text的滚动条
        self.inputTextScrollBar = tkinter.Scrollbar(self.frame[2])
        self.inputTextScrollBar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
         
        #输入消息Text，并与滚动条绑定
        ft = tkFont.Font(family='Fixdsys',size=11)
        self.inputText = tkinter.Text(self.frame[2],width=80,height=8,font=ft)
        self.inputText['yscrollcommand'] = self.inputTextScrollBar.set
        self.inputText.pack(expand=1,fill=tkinter.BOTH)
        self.inputTextScrollBar['command'] = self.chatText.yview()
        self.frame[2].pack(expand=1,fill=tkinter.BOTH)
         

        #发送消息按钮
        self.sendButton=tkinter.Button(self.frame[3],text=' 发 送 ',width=10,command=self.sendMessage)
        self.sendButton.pack(expand=1,side=tkinter.BOTTOM and tkinter.RIGHT,padx=15,pady=8)
 
        #关闭按钮
        #self.closeButton=tkinter.Button(self.frame[3],text=' 关 闭 ',width=10,command=self.close)
        #self.closeButton.pack(expand=1,side=tkinter.RIGHT,padx=15,pady=8)
        #self.frame[3].pack(expand=1,fill=tkinter.BOTH)
        #发送人
        self.closeButton=tkinter.Entry(self.frame[3],text='1',width=20,show=None)
        self.closeButton.pack(expand=1,side=tkinter.RIGHT,padx=15,pady=8)
        self.frame[3].pack(expand=1,fill=tkinter.BOTH)

    #接收消息
    def receiveMessage(self):
        #建立Socket连接
        try:
            self.clientSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.clientSock.connect((self.serverIP, self.serverPort))
            self.flag = True
            self.root.title(self.title + " - 已连接")
        except:
            self.flag = False
            self.root.title(self.title + " - 未连接")
            return
        
        self.buffer = 1024
        msg= {"type":1,"data":"success"}
        json_string = json.dumps(msg)
        self.clientSock.send(bytes(json_string, encoding = "utf8"))

        while True:
            try:
                if self.flag == True:
                    #连接建立，接收服务器端消息
                    self.serverMsg = self.clientSock.recv(self.buffer)
                    msg=json.loads(self.serverMsg)

                    msg['type']

                    if msg['type'] == 2:
                        if msg['data'] == 'ok':
                            self.root.title(self.title)
                        else:
                            self.root.title(self.title + " - 未连接" )
                    elif msg['type'] == 12:
                        self.chatText.tag_config("tag_1", foreground="#008000")
                        self.chatText.insert(tkinter.END, msg['sender']+' ' + msg['time'] +':\n','tag_1')
                        self.chatText.tag_config("tag_2", foreground="#0c0c0c")
                        self.chatText.insert(tkinter.END,' ' + msg['data'] + '\n','tag_2')
                else:
                    break
            except:
                self.root.title(self.title + " - 出现错误")
                time.sleep(1000)
                self.flag = False
                self.clientSock.close()
                   
    #发送消息
    def sendMessage(self):
        #得到text_input中的消息
        message = self.inputText.get('1.0',tkinter.END)
        if not message:
            return

        try:
            self.sendSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sendSock.connect((self.serverIP, self.serverPort))
        except:
            self.root.title(self.title + " - 连接失败")
            return
        
        #格式化当前的时间 %Y-%m-%d %H:%M:%S
        theTime = time.strftime("%H:%M:%S", time.localtime())
        
        
        #将消息发送到服务器端
        self.chatText.tag_config("tag_1", foreground="#008000")
        self.chatText.insert(tkinter.END, '我 ' + theTime +':\n','tag_1')
        self.chatText.tag_config("tag_2", foreground="#0c0c0c")
        self.chatText.insert(tkinter.END,'  ' + message + '\n','tag_2')
        self.inputText.delete('0.0','end')#清空用户在Text中输入的消息

        #格式化数据并发送
        me = 1
        to = 2
        msg = {"type":11,"from":me,"to":to,"data":message}
        json_string = json.dumps(msg)
        self.sendSock.send(bytes(json_string, encoding = "utf8"))
        self.sendSock.close()

    # 建立状态
    def reServer(self):
        self.flag = 0
        while True:
            try:
                self.sendSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.sendSock.connect((self.serverIP, self.serverPort))
            except:
                self.root.title(self.title + " - 连接失败")
                return

            if self.flag != 1:
                msg= {"type":1,"id":1,"data":"login"}
                json_string = json.dumps(msg)
                try:
                    self.sendSock.send(bytes(json_string, encoding = "utf8"))
                    self.flag = 1
                    self.root.title(self.title + " - 已登录")
                except:
                    self.root.title(self.title + " - 连接失败")
                finally:
                    self.sendSock.close()

            time.sleep(5)
     
    def startRun(self):
        # 接受消息线程
        #_thread.start_new_thread(self.receiveMessage,())
        # 状态线程
        _thread.start_new_thread(self.reServer,())
 
def main():
    client = Client()
    client.startRun()
    client.root.mainloop()
     
if __name__=='__main__':
    main()