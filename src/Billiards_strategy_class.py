#!/usr/bin/env python3
# license removed for brevity
# 撞球程式擊球策略
import rospy
import os
import enum
import math
import Hiwin_ros_Strategy as ros_strategy
from Hiwin_ros_Strategy import State_Flag
## 球桌與球與洞口參數
UpLeft_X = -30
UpLeft_Y = 57.8
UpRight_X = 30
UpRight_Y = 57.8
DownLeft_X = -30
DownLeft_Y = 17.8
DownRight_X = 30
DownRight_Y = 17.8
Ball_radius = 2.75
HoleState = 0
Hole_X = 0
Hole_Y = 0
##-----Mission 參數
GetInfoFlag = False
ExecuteFlag = False
GetKeyFlag = False
MotionSerialKey = []
MissionType_Flag = 0
MotionStep = 0
##-----手臂動作位置資訊
angle_SubCue = 0
LinePtpFlag = False
MoveFlag = False
PushBallHeight = 20
ObjAboveHeight = 20
SpeedValue = 10
MissionEndFlag = False
CurrentMissionType = 0
##---------------Enum---------------##
class ArmMotionCommand(enum.IntEnum):
    Arm_Stop = 0
    Arm_MoveToTargetUpside = 1
    Arm_MoveFowardDown = 2
    Arm_MoveVision = 3
    Arm_PushBall = 4
    Arm_LineUp = 5
    Arm_LineDown = 6
    Arm_Angle = 7
    Arm_StopPush = 8
class MissionType(enum.IntEnum):
    Get_Img = 0
    PushBall = 1
    Pushback = 2
    Mission_End = 3
##-----------switch define------------##
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
class pos():
    def __init__(self, x, y, z, pitch, roll, yaw):
        self.x = 0
        self.y = 50
        self.z = 20
        self.pitch = -90
        self.roll = 0
        self.yaw = 0 
class Target_pos():
    def __init__(self, x, y, z, pitch, roll, yaw):
        self.x = 0
        self.y = 50
        self.z = 20
        self.pitch = -90
        self.roll = 0
        self.yaw = 0 
class TargetPush_pos():
    def __init__(self, x, y, z, pitch, roll, yaw):
        self.x = 0
        self.y = 50
        self.z = 20
        self.pitch = -90
        self.roll = 0
        self.yaw = 0 
class Item():
    def __init__(self,x,y,label):
        self.x = x
        self.y = y
        self.label = label
def Billiards_Calculation():
    global angle_SubCue,HoleState
    SpecifyBall=Item(10,50,20)#母球
    CueBall=Item(10,50,20)#子球
    if SpecifyBall.x <= ((UpLeft_X+UpRight_X)/2) and SpecifyBall.y >= ((UpLeft_Y+DownLeft_Y)/2):
        HoleState = 0
        Hole_X = UpLeft_X
        Hole_Y = UpLeft_Y
    elif SpecifyBall.x > ((UpLeft_X+UpRight_X)/2) and SpecifyBall.y >= ((UpRight_Y+DownRight_Y)/2):
        HoleState = 1
        Hole_X = UpRight_X
        Hole_Y = UpRight_Y
    elif SpecifyBall.x <= ((DownLeft_X+DownRight_X)/2) and SpecifyBall.y < ((UpLeft_Y+DownLeft_Y)/2):
        HoleState = 2
        Hole_X = DownLeft_X
        Hole_Y = DownLeft_Y
    elif SpecifyBall.x > ((DownLeft_X+DownRight_X)/2) and SpecifyBall.y < ((UpRight_Y+DownRight_Y)/2):
        HoleState = 3
        Hole_X = DownRight_X
        Hole_Y = DownLeft_Y
    Sub_Hole_X = SpecifyBall.x - Hole_X
    Sub_Hole_Y = SpecifyBall.y - Hole_Y
    
    if Sub_Hole_X == 0:
        angle_HoleSub = math.pi/2.0
    else:
        angle_HoleSub = math.atan(math.fabs(Sub_Hole_Y/Sub_Hole_X))
    if Sub_Hole_X <0.0 and Sub_Hole_Y >= 0.0:
        angle_HoleSub = math.pi -angle_HoleSub
    elif Sub_Hole_X <0.0 and Sub_Hole_Y <0.0:
        angle_HoleSub = math.pi +angle_HoleSub
    elif Sub_Hole_X >=0.0 and Sub_Hole_Y <0.0:
        angle_HoleSub = math.pi*2.0 -angle_HoleSub
    angle_HoleSub = angle_HoleSub*180/math.pi
    
    Ball_radius_X = 2*Ball_radius*math.cos(angle_HoleSub*math.pi/180)
    Ball_radius_Y = 2*Ball_radius*math.sin(angle_HoleSub*math.pi/180)
    Cub_Sub_X = CueBall.x - SpecifyBall.x + Ball_radius_X
    Cub_Sub_Y = CueBall.y - SpecifyBall.y + Ball_radius_Y

    if Cub_Sub_X ==0.0:
        angle_SubCue = math.pi/2.0
    else:
        angle_SubCue = math.atan(math.fabs(Cub_Sub_Y/Cub_Sub_X))
    
    if Cub_Sub_X < 0.0 and Cub_Sub_Y >= 0.0:
        angle_SubCue = math.pi - angle_SubCue
    elif Cub_Sub_X < 0.0 and Cub_Sub_Y < 0.0:
        angle_SubCue = math.pi + angle_SubCue
    elif Cub_Sub_X >=0.0 and Cub_Sub_Y < 0.0:
        angle_SubCue = math.pi*2.0 - angle_SubCue
    angle_SubCue = angle_SubCue*180/math.pi

    # Target_pos.x = CueBall.x + 5*Ball_radius*math.cos(angle_SubCue*math.pi/180)
    # Target_pos.y = CueBall.y + 5*Ball_radius*math.sin(angle_SubCue*math.pi/180)
    # TargetPush_pos.x = CueBall.x
    # TargetPush_pos.y = CueBall.y

    Target_pos.x = 20
    Target_pos.y = 50
    TargetPush_pos.x = 10
    TargetPush_pos.y = 50
    return TargetPush_pos,Target_pos,angle_SubCue
def Mission_Trigger():
    if GetInfoFlag == True and GetKeyFlag == False and ExecuteFlag == False:
        GetInfo_Mission()
    if GetInfoFlag == False and GetKeyFlag == True and ExecuteFlag == False:
        GetKey_Mission()
    if GetInfoFlag == False and GetKeyFlag == False and ExecuteFlag == True:
        Execute_Mission()
    
def GetInfo_Mission():
    global GetInfoFlag,GetKeyFlag,ExecuteFlag
    
    #vision info 
    Billiards_Calculation()

    GetInfoFlag = False
    GetKeyFlag = True
    ExecuteFlag = False
def GetKey_Mission():
    global GetInfoFlag,GetKeyFlag,ExecuteFlag,MotionKey,MotionSerialKey

    Mission = Get_MissionType()
    #MotionSerialkey = MissionItem(Mission)
    MissionItem(Mission)
    MotionSerialKey = MotionKey
    GetInfoFlag = False
    GetKeyFlag = False
    ExecuteFlag = True
def Get_MissionType():
    global MissionType_Flag,CurrentMissionType
    for case in switch(MissionType_Flag): #傳送指令給socket選擇手臂動作
        if case(0):
            Type = MissionType.PushBall
            MissionType_Flag +=1
            break
        if case(1):
            Type = MissionType.Pushback
            MissionType_Flag -=1
            break
    CurrentMissionType = Type
    return Type
def MissionItem(ItemNo):
    global MotionKey
    Key_PushBallCommand = [\
        ArmMotionCommand.Arm_MoveFowardDown,\
        ArmMotionCommand.Arm_MoveToTargetUpside,\
        ArmMotionCommand.Arm_LineDown,\
        ArmMotionCommand.Arm_PushBall,\
        ArmMotionCommand.Arm_LineUp,\
        ArmMotionCommand.Arm_Stop,\
        ]
    Key_PushBackCommand = [\
        ArmMotionCommand.Arm_MoveFowardDown,\
        ArmMotionCommand.Arm_MoveVision,\
        ArmMotionCommand.Arm_Stop,\
        ArmMotionCommand.Arm_StopPush,\
        ]
    for case in switch(ItemNo): #傳送指令給socket選擇手臂動作
        if case(MissionType.PushBall):
            MotionKey = Key_PushBallCommand
            break
        if case(MissionType.Pushback):
            MotionKey = Key_PushBackCommand
            break
    return MotionKey
def Execute_Mission():
    global GetInfoFlag,GetKeyFlag,ExecuteFlag,MotionKey,MotionStep,MotionSerialKey,MissionEndFlag,CurrentMissionType
    # print(State_Flag.Arm)
    # if State_Flag.Arm == 0 and State_Flag.Strategy == 1:
    #     State_Flag.Arm = 0 # test
    
    if MotionKey[MotionStep] == ArmMotionCommand.Arm_Stop:
        if MissionEndFlag == True:
            CurrentMissionType = MissionType.Mission_End
            GetInfoFlag = False
            GetKeyFlag = False
            ExecuteFlag = False
            print("Mission_End")
        elif CurrentMissionType == MissionType.PushBall:
            GetInfoFlag = False
            GetKeyFlag = True
            ExecuteFlag = False
            MotionStep = 0
            print("PushBall")
        else:
            GetInfoFlag = True
            GetKeyFlag = False
            ExecuteFlag = False
            MotionStep = 0
    else:
        #MotionItem(MotionSerialKey+MotionStep)
        MotionItem(MotionSerialKey[MotionStep])
        MotionStep += 1
    
def MotionItem(ItemNo):
    global angle_SubCue,SpeedValue,PushFlag,LinePtpFlag,MissionEndFlag
    SpeedValue = 10
    for case in switch(ItemNo): #傳送指令給socket選擇手臂動作
        if case(ArmMotionCommand.Arm_Stop):
            MoveFlag = False
            print("Arm_Stop")
            break
        if case(ArmMotionCommand.Arm_StopPush):
            MoveFlag = False
            PushFlag = True #重新掃描物件
            print("Arm_StopPush")
            break
        if case(ArmMotionCommand.Arm_MoveToTargetUpside):
            pos.x = Target_pos.x
            pos.y = Target_pos.y
            pos.z = ObjAboveHeight
            pos.pitch = -90
            pos.roll = -angle_SubCue #RobotArm5
            pos.yaw = 0
            MoveFlag = True
            LinePtpFlag = False
            print("Arm_MoveToTargetUpside")
            break
        if case(ArmMotionCommand.Arm_LineUp):
            pos.z = ObjAboveHeight
            SpeedValue = 5
            MoveFlag = True
            LinePtpFlag = True
            print("Arm_LineUp")
            break
        if case(ArmMotionCommand.Arm_LineDown):
            pos.z = PushBallHeight
            SpeedValue = 5
            MoveFlag = True
            LinePtpFlag = True
            print("Arm_LineDown")
            break
        if case(ArmMotionCommand.Arm_PushBall):
            pos.x = TargetPush_pos.x
            pos.y = TargetPush_pos.y
            pos.z = PushBallHeight
            pos.pitch = -90
            pos.roll = -angle_SubCue
            pos.yaw = 0
            #SpeedValue = 20   ##待測試up
            MoveFlag = True
            LinePtpFlag = True
            print("Arm_PushBall")
            break
        if case(ArmMotionCommand.Arm_MoveVision):
            pos.x = 0
            pos.y = 50
            pos.z = 30
            pos.pitch = -90
            pos.roll = 0
            pos.yaw = 0
            MoveFlag = True
            LinePtpFlag = False
            ##任務結束旗標
            MissionEndFlag = True
            print("Arm_MoveVision")
            break
        if case(ArmMotionCommand.Arm_MoveFowardDown):
            pos.x = 0
            pos.y = 50
            pos.z = 30
            pos.pitch = -90
            pos.roll = 0
            pos.yaw = 0
            MoveFlag = True
            LinePtpFlag = False
            print("Arm_MoveFowardDown")
            break
        if case(): # default, could also just omit condition or 'if True'
            print ("something else!")
            # No need to break here, it'll stop anyway
    if MoveFlag == True:
        if LinePtpFlag == False:
            SpeedValue = 10
            print('x: ',pos.x,' y: ',pos.y,' z: ',pos.z,' pitch: ',pos.pitch,' roll: ',pos.roll,' yaw: ',pos.yaw)
            ros_strategy.strategy_client_Arm_Mode(2,1,0,SpeedValue,2)#action,ra,grip,vel,both
            ros_strategy.strategy_client_pos_move(pos.x,pos.y,pos.z,pos.pitch,pos.roll,pos.yaw)
        elif LinePtpFlag == True:
            SpeedValue = 10
            print('x: ',pos.x,' y: ',pos.y,' z: ',pos.z,' pitch: ',pos.pitch,' roll: ',pos.roll,' yaw: ',pos.yaw)
            ros_strategy.strategy_client_Arm_Mode(3,1,0,SpeedValue,2)#action,ra,grip,vel,both
            ros_strategy.strategy_client_pos_move(pos.x,pos.y,pos.z,pos.pitch,pos.roll,pos.yaw)
    #action: ptp line
    #ra : abs rel
    #grip 夾爪
    #vel speed
    #both : Ctrl_Mode