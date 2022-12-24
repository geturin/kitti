#!/usr/bin/python3.8
import rospy
from sensor_msgs.msg import PointCloud2,Image
import sensor_msgs.point_cloud2 as pcd2
from std_msgs.msg import Header
import numpy as np
import cv2
from depth2pcd import *
from nav_msgs.msg import Odometry





class pointcloud_pub(object):

    def __init__(self) -> None:
        rospy.init_node('pcd_pub', anonymous=True)
        return
    
    def read_pcd(self,pcd) -> str:
        self.pcd = pcd

    def pub(self,frame_id,topic_name) -> str:
        self.header = Header()
        self.header.frame_id = frame_id
        self.pcldata = pcd2.create_cloud_xyz32(self.header, self.pcd)
        rospy.Publisher(topic_name, PointCloud2, queue_size=1).publish(self.pcldata)


def canny_filter(rgb,depth):
    #使用边缘检测来对深度图滤波 去除掉边缘毛躁点
    imgray=cv2.cvtColor(rgb,cv2.COLOR_BGR2GRAY)
    ret,thresh=cv2.threshold(imgray,100,200,0)
    contours,hierarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    depth=cv2.drawContours(depth,contours,-1,(0),5) 
    return depth


# def pcd_filter(pcd):
#     p = pcl.PointCloud(np.array(pcd, dtype=np.float32))
#     k=p.to_array()


#     fil = p.make_statistical_outlier_filter()
#     fil.set_mean_k(50)
#     fil.set_std_dev_mul_thresh(1.1)


#     cloud_filtered = fil.filter()

#     pcd=cloud_filtered.to_array()

#     return pcd


publisher = pointcloud_pub()
orb_pub = pointcloud_pub()

frame =0
rate = rospy.Rate(0.5)
mesh_scal=10
depth_transform = depth_to_pcd(3)

odom_pub = rospy.Publisher("/visual_slam/odom", Odometry, queue_size=1)
odom = Odometry()
odom.child_frame_id = "camera"
depth=15.11806784*np.load("/home/kero/catkin_ws/src/kitti/data/ai_depth.npy")
rgb = cv2.imread("/home/kero/catkin_ws/src/kitti/data/raw_image.png")

pcd = depth_transform.get_pcd(depth)
pcd_fillter = depth_transform.get_pcd(canny_filter(rgb,depth))

while not rospy.is_shutdown():
    

    # #pcd = pcd_filter(pcd)
    # #栅格化（test）
    # pcd =(mesh_scal*pcd).astype(int)
    # pcd = (pcd.astype(float)/mesh_scal)
    # pcd = np.unique(pcd,axis=0)

    # pcd = pcd_filter(pcd)

    # orb_pcd = np.load("/home/kero/catkin_ws/src/kitti/data/testPCD.npy")

    publisher.read_pcd(pcd)
    publisher.pub(frame_id="world",topic_name='/raw')

    # odom_pub.publish(odom)

    orb_pub.read_pcd(pcd_fillter)
    orb_pub.pub(frame_id="world",topic_name='/filter')

    
    rate.sleep() 


        

