#!/usr/bin/env python3
# license removed for brevity
#encoding:utf-8
import os
import threading
import tkinter as tk
from time import time
from tkinter import ttk

import numpy as np
import rospy
from PIL import Image, ImageTk

import shake_strategy_content as shake_cont
import shake_strategy_simulation as shake_simu

# smart-shaking interface(main)
# =======================================================================
# =24/07/2019:fix display error                                         =
# =======================================================================
#-----------------------------------------------------------------
root = tk.Tk()
root.title('Hiwin Smart Shaking')
root.geometry('630x710')   
root.wm_attributes("-topmost",1)

img_open = Image.open(os.path.abspath(os.path.dirname(__file__))+'/iclab_hiwin.png')
img_bottom = ImageTk.PhotoImage(img_open)
label_img = tk.Label(root, image = img_bottom)
label_img.place(x=0,y=600,width=630,height=110)
#---------------------------------------------------------------

#==============================Action Flags===========================================
start_time=0
#------------------------------select steps------------------------------------
step_str='加冰塊 加飲料 加果糖 蓋大蓋 搖飲 取小蓋 倒入手搖杯'
step_var=[]
step_checkbtn=[]

selected_steps=tk.Label(root,text='Exacuating Steps',font=('Arial', 13))
selected_steps.place(x=440,y=160)

def StepFlagGet():
    shake_cont.step_flag=[step_var[i].get() for i in range(7)]

for i in range(7):
    step_var.append(tk.IntVar(value=1))
    step_checkbtn.append(tk.Checkbutton(root,text=step_str.split()[i],font=('Arial', 13),variable=step_var[i],onvalue=1,offvalue=0,command=StepFlagGet))
    step_checkbtn[i].place(x=440,y=190+24*i)

def AllSteps():
    for i in range(7):
        step_var[i].set(value=all_step_var.get())
    StepFlagGet()
all_step_var=tk.IntVar(value=0)
all_step_ckbtn=tk.Checkbutton(root,text='All Steps',font=('Arial', 13),variable=all_step_var,onvalue=1,offvalue=0,command=AllSteps)
all_step_ckbtn.place(x=440,y=570)
#==============================Current Param===========================================
#------------------------------current state-----------------------------------
Label_obj = tk.Label(root,text='Aciton: Ready',fg='black',bg='white', font=('Arial', 15), width=50, height=2)
Label_obj.place(x=40,y=15)

pos_str='x y z pitch roll yaw'
pos_val=[shake_cont.Current_Pos.x,shake_cont.Current_Pos.y,shake_cont.Current_Pos.z,
        shake_cont.Current_Pos.pitch,shake_cont.Current_Pos.roll,shake_cont.Current_Pos.yaw]
pos_label=[]
for i in range(6):
    pos_label.append(tk.Label(root,text=pos_str.split()[i]+':'+str(pos_val[i]),fg='black',bg='white', font=('Arial', 15), width=14, height=1))
    pos_label[i].place(x=40+200*(i%3),y=80+40*(i//3))

Label_grip=tk.Label(root,text='Grip: '+shake_cont.Current_grip,fg='black',bg='white', font=('Arial', 15), width=14, height=1)
Label_grip.place(x=440,y=390)

sugar_tm_label=tk.Label(root,text='果糖: {:.2f}s'.format(shake_cont.sugar_end_tm-shake_cont.sugar_start_tm),font=('Arial', 11))
sugar_tm_label.place(x=125,y=570)
ice_tm_label=tk.Label(root,text='冰塊: {:.2f}s'.format(shake_cont.ice_end_tm-shake_cont.ice_start_tm),font=('Arial', 11))
ice_tm_label.place(x=35,y=570)

def SpeedMode():
    global param_val,speed_mode_var
    shake_cont.SpeedModeToggle(int(speed_mode_var.get()))
    param_val[0]=shake_cont.speed_value
    # print('action:',shake_cont.arm_speed_action,'\nmode:',shake_cont.arm_speed_mode,'\nspeed:',shake_cont.speed_value)
speed_mode_var=tk.IntVar(value=0)
speed_mode_ckbtn=tk.Checkbutton(root,text='Operating Mode',font=('Arial', 13),variable=speed_mode_var,onvalue=1,offvalue=0,command=SpeedMode)
speed_mode_ckbtn.place(x=240,y=570)

# def GripDelay():
#     global grip_delay_var
#     shake_cont.grip_delay=int(grip_delay_var.get())
#     # print(shake_cont.grip_delay)
# grip_delay_var=tk.IntVar(value=1)
# grip_delay_ckbtn=tk.Checkbutton(root,text='Grip Delay',font=('Arial', 13),variable=grip_delay_var,onvalue=1,offvalue=0,command=GripDelay)
# grip_delay_ckbtn.place(x=40,y=570)
#------------------------------show current param-----------------------------------
current_title=tk.Label(root,text='Current Parameters',font=('Arial', 13))
current_title.place(x=40,y=160)

param_label=[]
show_param=[]
change_param_entry=[]
param_val=[shake_cont.speed_value,shake_cont.Animation_Simulation.Simu.fps,shake_cont.arm_height,shake_cont.table_height]
param_label_str='Speed FPS Arm_H Tab_H'
for i in range(4):
    param_label.append(tk.Label(root,text=param_label_str.split()[i],font=('Arial', 11)))
    param_label[i].place(x=40,y=190+33*i)
    show_param.append(tk.Label(root,text=str(param_val[i]),width=5,fg='black',bg='white',font=('Arial', 11)))
    show_param[i].place(x=100,y=190+33*i)
    change_param_entry.append(tk.Entry(root,width=5))
    change_param_entry[i].place(x=150,y=190+33*i)

current_cmd=tk.Label(root,text='Current Command',font=('Arial', 13))
current_cmd.place(x=240,y=160)
show_cmd=tk.Label(root,text=shake_cont.cmd_str,width=17,fg='black',bg='white',font=('Arial', 12))
show_cmd.place(x=240,y=200)
#------------------------------change current param-----------------------------------
def ChangeParam():
    for i in range(4):
        if change_param_entry[i].get():
            if i == 0:
                param_val[i]=int(change_param_entry[i].get())  
            else:
                param_val[i]=float(change_param_entry[i].get())
    [shake_cont.speed_value,shake_cont.Animation_Simulation.Simu.fps,shake_cont.arm_height,shake_cont.table_height]=param_val
    shake_cont.RefreshDelt_Z()
    print('delt_z:',shake_cont.delt_z)
param_change_confirm = tk.Button(root,text='Submit',font=('Arial', 11),width=6,height=1,command=ChangeParam) 
param_change_confirm.place(x=120,y=320)

def DefaultParam():
    shake_cont.speed_value= 30
    shake_cont.delt_z= float(0)
    shake_cont.Animation_Simulation.Simu.fps=24
defaut_param_confirm = tk.Button(root,text='Default',font=('Arial', 11),width=6,height=1,command=DefaultParam) 
defaut_param_confirm.place(x=40,y=320)


def CmdInput():
    shake_cont.cmd_str = cmd_entry.get()
    if auto_simu_var.get():
        StartSimu()
cmd_entry = tk.Entry(root,width=19)
cmd_entry.place(x=240,y=240)
cmd_confirm = tk.Button(root,text='Submit',font=('Arial', 11),width=6,height=1,command=CmdInput) 
cmd_confirm.place(x=320,y=280)

#=============================================================================================

# #===================================General Func=============================================
auto_simu_var=tk.IntVar(value=0)
auto_simu_ckbtn=tk.Checkbutton(root,text='Simu',font=('Arial', 13),variable=auto_simu_var,onvalue=1,offvalue=0)
auto_simu_ckbtn.place(x=240,y=325)
def AudioRecord():
    audio_thread=threading.Thread(target=shake_simu.SpeechRecog)
    audio_thread.start()
    if auto_simu_var.get():
        audio_thread.join()
        StartSimu()
audio_record = tk.Button(root,text='Record',font=('Arial', 11),width=6,height=1,command=AudioRecord) 
audio_record.place(x=320,y=320)
def DefaultCmd():
    shake_cont.cmd_str = '冬瓜紅茶半糖少冰'
    if auto_simu_var.get():
        StartSimu()
default_cmd = tk.Button(root,text='Default',font=('Arial', 11),width=6,height=1,command=DefaultCmd) 
default_cmd.place(x=240,y=280)
# #======================================================================================

# #===================================from shake_trigger==============================================
online_func=tk.Label(root,text='ON-Line Functions',font=('Arial', 13))
online_func.place(x=240,y=360)
arm_listening_flag=False
def ArmConnect():
    global arm_listening_flag
    if not arm_listening_flag:
        argv = rospy.myargv()
        rospy.init_node('strategy', anonymous=True)
        arm_listening_flag=True
def RecordnStart():
    import shake_strategy_trigger as shake_trig
    ArmConnect()
    shake_trig.arm_state_listener()
    record_n_start_thread=threading.Thread(target=shake_trig.SpeechTriggerShaking)
    record_n_start_thread.start()
    del shake_trig
record_n_start=tk.Button(root,text='Record & Start!',font=('Arial', 16),width=11,height=2,fg='red',command=RecordnStart)
record_n_start.place(x=240,y=510)
def DefaultShake():
    import shake_strategy_trigger as shake_trig
    ArmConnect()
    shake_trig.arm_state_listener()
    default_shaking_thread=threading.Thread(target=shake_trig.DefaultShaking)
    default_shaking_thread.start()
    del shake_trig
default_shaking = tk.Button(root,text='Default Shake',font=('Arial', 11),width=16,height=1,command=DefaultShake) 
default_shaking.place(x=240,y=430)
def PosAdjustTest():
    global speed_mode_var
    speed_mode_var.set(value=0)
    SpeedMode()
    import shake_strategy_trigger as shake_trig
    ArmConnect()
    shake_trig.arm_state_listener()
    adjust_thread=threading.Thread(target=shake_trig.PosAdjust)
    adjust_thread.start()
    del shake_trig
pos_adjust_test = tk.Button(root,text='Pos-Adjustable',font=('Arial', 11),width=16,height=1,command=PosAdjustTest) 
pos_adjust_test.place(x=240,y=390)
def CoordinateCollate():
    global speed_mode_var
    speed_mode_var.set(value=0)
    SpeedMode()
    StepFlagGet()
    import coordinate_collation_interface as collate_inter
    collate_thread=threading.Thread(target=collate_inter.Collation)
    collate_thread.start()
    del collate_inter
coordinate_collate = tk.Button(root,text='Coordinate Collation',font=('Arial', 11),width=16,height=1,command=CoordinateCollate) 
coordinate_collate.place(x=240,y=470)
def GripStop():
    import shake_strategy_trigger as shake_trig
    ArmConnect()
    shake_trig.arm_state_listener()
    stop_thread=threading.Thread(target=shake_trig.Hiwin_Action.GripCtrl,args =(shake_cont.Current_Pos,shake_cont.speed_value,shake_cont.gp_stop,'控制夾爪','停止'))
    stop_thread.start()
    del shake_trig
def GripTightCatch():
    import shake_strategy_trigger as shake_trig
    ArmConnect()
    shake_trig.arm_state_listener()
    catch_thread=threading.Thread(target=shake_trig.Hiwin_Action.GripCtrl,args =(shake_cont.Current_Pos,shake_cont.speed_value,shake_cont.gp_tight_catch,'控制夾爪','緊夾'))
    catch_thread.start()
    del shake_trig
def GripSoftCatch():
    import shake_strategy_trigger as shake_trig
    ArmConnect()
    shake_trig.arm_state_listener()
    open_thread=threading.Thread(target=shake_trig.Hiwin_Action.GripCtrl,args =(shake_cont.Current_Pos,shake_cont.speed_value,shake_cont.gp_soft_catch,'控制夾爪','鬆夾'))
    open_thread.start()
    del shake_trig
def GripOpen():
    import shake_strategy_trigger as shake_trig
    ArmConnect()
    shake_trig.arm_state_listener()
    op_thread=threading.Thread(target=shake_trig.Hiwin_Action.GripCtrl,args =(shake_cont.Current_Pos,shake_cont.speed_value,shake_cont.gp_open,'控制夾爪','鬆開'))
    op_thread.start()
    del shake_trig
grip_state=tk.Label(root,text='Grip Control',font=('Arial', 13))
grip_state.place(x=440,y=360)
grip_stop = tk.Button(root,text='Stop',font=('Arial', 11),width=6,height=1,command=GripStop) 
grip_stop.place(x=440,y=430)
grip_catch = tk.Button(root,text='Tight',font=('Arial', 11),width=6,height=1,command=GripTightCatch) 
grip_catch.place(x=520,y=430)
grip_open = tk.Button(root,text='Soft',font=('Arial', 11),width=6,height=1,command=GripSoftCatch) 
grip_open.place(x=440,y=470)
grip_loosen = tk.Button(root,text='Open',font=('Arial', 11),width=6,height=1,command=GripOpen) 
grip_loosen.place(x=520,y=470)
# #======================================================================================

# #===================================from shake_simu==============================================
offline_func=tk.Label(root,text='OFF-Line Functions',font=('Arial', 13))
offline_func.place(x=40,y=360)
def StartSimu():
    shake_cont.Hiwin_Simu_Log.StartWrite('Simu Action')
    shake_cont.Hiwin_Simu_Log.WriteDate()
    simu_thread=threading.Thread(target=shake_simu.AnimationSimulation)
    simu_thread.start()
start_simu=tk.Button(root,text='Start Animation!',font=('Arial', 16),width=11,height=2,command=StartSimu)
start_simu.place(x=40,y=510)
def PrintFullPos():
    print_thread=threading.Thread(target=shake_simu.WritePos)
    print_thread.start()
write_pos = tk.Button(root,text='Write Pos',font=('Arial', 11),width=16,height=1,command=PrintFullPos) 
write_pos.place(x=40,y=390)
def Kine():
    import kinematics_interface as kine_inter
    print_thread=threading.Thread(target=kine_inter.Kinematics)
    print_thread.start()
    del kine_inter
kinematic = tk.Button(root,text='Kinematics',font=('Arial', 11),width=16,height=1,command=Kine) 
kinematic.place(x=40,y=470)
def HeightRangeTest():
    height_test_thread=threading.Thread(target=shake_simu.HeightRangeAccessibleTest)
    height_test_thread.start()
height_test = tk.Button(root,text='Height Test',font=('Arial', 11),width=16,height=1,command=HeightRangeTest) 
height_test.place(x=40,y=430)
# #======================================================================================

#==============================Interface Control==================================================
#-----------------------------update-----------------------------------
def update():
    global Label_grip,pos_label,pos_val,start_time
    shake_cont.step_flag=[step_var[i].get() for i in range(7)]
    show_cmd.config(text=shake_cont.cmd_str)
    if not shake_cont.finished_flag:
        Label_obj.config(text='Action: '+shake_cont.move_str+'  Time: {:.0f}m {:.2f}s'.format((time()-start_time)//60,(time()-start_time)%60))
    if shake_cont.simu_flag:
        for i in range(6):
            pos_val[i]=np.around(shake_cont.Animation_Simulation.Simu.start_pos[i]*0.1*10**(i//3),decimals=2)

    else:
        pos_val=[shake_cont.Current_Pos.x,shake_cont.Current_Pos.y,shake_cont.Current_Pos.z,
                shake_cont.Current_Pos.pitch,shake_cont.Current_Pos.roll,shake_cont.Current_Pos.yaw]
    for i in range(6):
        pos_label[i].config(text=pos_str.split()[i]+': {:.2f}'.format(pos_val[i]))
    for i in range(4):
        show_param[i].config(text=str(param_val[i]))
    show_cmd.config(text=shake_cont.cmd_str)
    Label_grip.config(text='Grip: '+shake_cont.Current_grip)
    sugar_tm_label.config(text='果糖: {:.2f}s'.format(shake_cont.sugar_end_tm-shake_cont.sugar_start_tm))
    ice_tm_label.config(text='冰塊: {:.2f}s'.format(shake_cont.ice_end_tm-shake_cont.ice_start_tm))
    speed_mode_var.set(value=shake_cont.arm_speed_mode)
    start_time=shake_cont.start_time
    root.after(5, update)

update_thread=threading.Thread(target=update)
update_thread.start()

#-----------------------------close------------------------------------
def close():
    root.destroy()
    os._exit(0)
    if arm_listening_flag:
        rospy.spin()
        import Hiwin_RT605_Socket as ArmTask
        ArmTask.rospy.spin()

shutdown = tk.Button(root,text='QUIT',font=('Arial', 16),width=11,height=2,command=close) 
shutdown.place(x=440,y=510)

root.protocol('WM_DELETE_WINDOW', close)
#-------------------------------main----------------------------------
if __name__ == "__main__":
    root.mainloop()
