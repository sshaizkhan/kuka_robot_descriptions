# Copyright (c) 2021 PickNik, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the {copyright_holder} nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author: Shahwaz Khan
# Modified from the original file by: Denis Stogl

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def validate_robot_config(context):
    """Validate that the robot type and DOF combination is supported."""
    # Define supported robot configurations
    ROBOT_CONFIGS = {
        # 6 DOF Industrial Robots
        "kr6_r700_sixx": [6],
        "kr6_r900_sixx": [6],
        "kr10_r1100_2": [6],
        "kr16_r2010_2": [6],
        "kr210_r2700_2": [6],
        "kr210_r3100_2": [6],
        "kr560_r3100_2": [6],
        "lbr_iisy3_r760": [6],
        "lbr_iisy11_r1300": [6],
        "lbr_iisy15_r930": [6],
        # 7 DOF Collaborative Robots (can also work in 6 DOF mode for some)
        "lbr_iiwa14_r820": [7],
    }

    kuka_type = LaunchConfiguration("kuka_type").perform(context)
    dof = int(LaunchConfiguration("dof").perform(context))

    if kuka_type not in ROBOT_CONFIGS:
        raise ValueError(f"Unsupported robot type: {kuka_type}")

    if dof not in ROBOT_CONFIGS[kuka_type]:
        supported_dofs = ROBOT_CONFIGS[kuka_type]
        raise ValueError(
            f"Robot {kuka_type} does not support {dof} DOF. " f"Supported DOF(s): {supported_dofs}"
        )

    print(f"✓ Validated: {kuka_type} with {dof} DOF is supported")
    return []


def launch_setup(context, *args, **kwargs):
    # Validate configuration first
    validate_robot_config(context)

    # Initialize Arguments
    kuka_type = LaunchConfiguration("kuka_type")
    dof = LaunchConfiguration("dof")
    description_package = LaunchConfiguration("description_package")
    description_file = LaunchConfiguration("description_file")
    tf_prefix = LaunchConfiguration("tf_prefix")

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare(description_package), "urdf", description_file]
            ),
            " ",
            "name:=",
            "kuka",
            " ",
            "kuka_type:=",
            kuka_type,
            " ",
            "tf_prefix:=",
            tf_prefix,
            " ",
            "dof:=",
            dof,
        ]
    )
    robot_description = {
        "robot_description": ParameterValue(robot_description_content, value_type=str)
    }

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare(description_package), "rviz", "view_robot.rviz"]
    )

    joint_state_publisher_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
    )
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
    )

    nodes_to_start = [
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node,
    ]

    return nodes_to_start


def generate_launch_description():
    declared_arguments = []

    # KUKA specific arguments
    declared_arguments.append(
        DeclareLaunchArgument(
            "kuka_type",
            description="Type/series of used KUKA robot.",
            choices=[
                # 6 DOF Industrial Robots
                "kr6_r700_sixx",
                "kr6_r900_sixx",
                "kr10_r1100_2",
                "kr16_r2010_2",
                "kr210_r2700_2",
                "kr210_r3100_2",
                "kr560_r3100_2",
                # 7 DOF Collaborative Robots
                "lbr_iisy3_r760",
                "lbr_iisy11_r1300",
                "lbr_iisy15_r930",
                "lbr_iiwa14_r820",
            ],
            default_value="kr6_r700_sixx",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "dof",
            description="Degrees of Freedom for the robot (6 or 7).",
            choices=["6", "7"],
            default_value="6",
        )
    )

    # General arguments
    declared_arguments.append(
        DeclareLaunchArgument(
            "description_package",
            default_value="kuka_robot_descriptions",
            description="Description package with robot URDF/XACRO files. Usually the argument \
        is not set, it enables use of a custom description.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "description_file",
            default_value="kuka.urdf.xacro",
            description="URDF/XACRO description file with the robot.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "tf_prefix",
            default_value='""',
            description="Prefix of the joint names, useful for \
        multi-robot setup. If changed than also joint names in the controllers' configuration \
        have to be updated.",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
