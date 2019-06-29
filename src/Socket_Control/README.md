#test lauch file

roslaunch ROS_Socket Hiwin_RT605_Strategy_test.launch 

#更新時間 20190628 
#尚有的問題
1. 有機會跳動作
2. 策略中有下0.2sec delay
#注意
1. 若主程式封包處理完成,即可不須delay,跳動作問題也解決
2. 以上問題尚未解決前,測試中速度放慢,請小心運行

#程式注意
1. 呼叫手臂動作如:point_data,Arm_Mode,Speed_Mode
2. 使用以上功能須最後輸入Arm_Mode,因為呼叫他才會發送指令
若先呼叫Arm_Mode再呼叫point_data則不會存入點位
3. 上述注意事項可參考Hiwin_RT605_Strategy_test.py中的寫法
4. ex:
ArmTask.point_data(pos.x,pos.y,pos.z,pos.pitch,pos.roll,pos.yaw)

ArmTask.Arm_Mode(2,1,0,10,2)#action,ra,grip,vel,both
                
