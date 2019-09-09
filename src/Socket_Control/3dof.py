from kinematics import *
arm_limit=np.array([[-360,360],[-360,360],[-360,360]]) 
arm = Kinematics_Model_cls(3,[10,30,30],\
                            [0,30,30],
                            [pi/2,0,0],
                            [10,0,0],
                            [pi/2,0,0],
                            [0,0,0],
                            arm_limit)
# ang=AngInput()



pos=PosInput('')
pos[2]-=10
ang=arm.InverseKinematics(pos)
# ang[1]+=90
# ang[2]-=90



current_plt=plt.subplot(111,projection='3d', aspect='equal') 
current_plt.set_zlabel('Z')  # 座標軸
current_plt.set_ylabel('Y')
current_plt.set_xlabel('X')
arm.KinematicsDraw(ang,'bo-',2,'3D')
end=arm.ForwardKinematics(ang)
end[2]+=10
print('角度:',np.around(ang,decimals=1))
print('末端點:',np.around(end,decimals=1))
plt.show()