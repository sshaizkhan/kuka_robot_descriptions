#!/usr/bin/env python3
"""View a RoboDK-derived robot in RViz with a joint slider GUI.

  ros2 launch <pkg> view_robot.launch.py model:=<model>
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (Command, FindExecutable, LaunchConfiguration,
                                   PathJoinSubstitution)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = LaunchConfiguration("description_package")
    model = LaunchConfiguration("model")
    prefix = LaunchConfiguration("prefix")
    desc = {"robot_description": Command([
        FindExecutable(name="xacro"), " ",
        PathJoinSubstitution([FindPackageShare(pkg), "urdf",
                              [model, ".urdf.xacro"]]),
        " ", "prefix:=", prefix])}
    rviz = PathJoinSubstitution([FindPackageShare(pkg), "rviz", "view_robot.rviz"])
    return LaunchDescription([
        DeclareLaunchArgument("description_package", default_value="kuka_robot_descriptions"),
        DeclareLaunchArgument("model", description="model name (urdf/<model>.urdf.xacro)"),
        DeclareLaunchArgument("prefix", default_value=""),
        Node(package="robot_state_publisher", executable="robot_state_publisher",
             output="screen", parameters=[desc]),
        Node(package="joint_state_publisher_gui", executable="joint_state_publisher_gui",
             output="screen"),
        Node(package="rviz2", executable="rviz2", name="rviz2", output="screen",
             arguments=["-d", rviz]),
    ])
