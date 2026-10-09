#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gmapping을 이용해 2D Occupancy Grid Map을 생성하고, /map을 PGM+YAML로 저장하는 스크립트.
- Gmapping 노드 자동 실행(roslaunch API)
- (선택) rosbag 재생
- /map 구독 후 최신 지도를 저장

사용 예)
1) 실시간 센서로 구축:
   $ roscore
   $ python gmapping_mapper.py --save_base map_out

2) rosbag로 재생하여 구축:
   $ roscore
   $ python gmapping_mapper.py --bag myroom.bag --save_base room_map --rate 1.0

3) Gmapping 파라미터 yaml 로딩:
   $ python gmapping_mapper.py --params gmapping_params.yaml --save_base map01
"""

from __future__ import print_function
import os
import sys
import signal
import time
import math
import yaml
import argparse
import subprocess

import rospy
import roslaunch
from nav_msgs.msg import OccupancyGrid

# ---------- 유틸: PGM + YAML로 맵 저장 ----------
def save_occupancy_grid(map_msg, save_base):
    """
    nav_msgs/OccupancyGrid -> save_base.pgm, save_base.yaml 저장
    (map_server의 map_saver와 동일한 포맷)
    """
    import numpy as np

    data = map_msg.data
    width = map_msg.info.width
    height = map_msg.info.height
    res = map_msg.info.resolution
    origin = map_msg.info.origin  # geometry_msgs/Pose

    arr = np.array(data, dtype=np.int16).reshape((height, width))

    # PGM 작성 규칙(표준):
    #   -1(unknown) -> 205(회색), [0..100]은 확률로 간주: >=65(점유) -> 0(검정), 나머지(자유) -> 254(흰색)
    img = np.zeros_like(arr, dtype=np.uint8)
    img[arr < 0] = 205
    img[(arr >= 0) & (arr <= 100)] = 254
    img[arr >= 65] = 0

    # PGM은 좌상단 원점. ROS map은 좌하단이 원점이므로 상하반전
    img = np.flipud(img)

    pgm_path = save_base + ".pgm"
    yaml_path = save_base + ".yaml"

    with open(pgm_path, "wb") as f:
        f.write(b"P5\n")
        header = "{} {}\n255\n".format(width, height)
        f.write(header.encode("ascii"))
        f.write(bytearray(img.flatten().tolist()))

    meta = {
        "image": os.path.basename(pgm_path),
        "resolution": float(res),
        # origin: (x, y, yaw) in meters
        "origin": [float(origin.position.x), float(origin.position.y), 0.0],
        "negate": 0,
        "occupied_thresh": 0.65,
        "free_thresh": 0.196
    }
    with open(yaml_path, "w") as f:
        yaml.safe_dump(meta, f, default_flow_style=False, sort_keys=False)

    rospy.loginfo("맵 저장 완료: %s(.pgm/.yaml)", save_base)
    return pgm_path, yaml_path


# ---------- /map 구독 및 최신본 저장 ----------
class MapRecorder(object):
    def __init__(self, save_base, autosave_secs=3.0):
        self.save_base = save_base
        self.last_map = None
        self.last_saved_time = 0.0
        self.autosave_secs = autosave_secs
        self.sub = rospy.Subscriber("map", OccupancyGrid, self.cb, queue_size=1)

    def cb(self, msg):
        self.last_map = msg
        # 주기적으로 자동 저장(맵이 갱신될 때)
        now = time.time()
        if self.autosave_secs and (now - self.last_saved_time) > self.autosave_secs:
            save_occupancy_grid(msg, self.save_base)
            self.last_saved_time = now

    def save_once(self):
        if self.last_map:
            save_occupancy_grid(self.last_map, self.save_base)
        else:
            rospy.logwarn("아직 /map 데이터가 없습니다. 이동을 통해 맵을 누적해 주십시오.")


# ---------- Gmapping 실행 ----------
def start_gmapping(params_dict=None, scan_topic="/scan", base_frame="base_link",
                   odom_frame="odom", map_update_interval=2.0):
    """
    roslaunch API로 gmapping 노드를 실행합니다.
    params_dict가 주어지면 /slam_gmapping 네임스페이스로 파라미터를 올립니다.
    """
    uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
    roslaunch.configure_logging(uuid)
    launch = roslaunch.scriptapi.ROSLaunch()
    launch.parent = roslaunch.parent.ROSLaunchParent(uuid, [])

    # 파라미터 설정
    if params_dict:
        for k, v in params_dict.items():
            rospy.set_param("~" + k if not k.startswith("/") else k, v)

    # slam_gmapping 노드
    node = roslaunch.core.Node(
        package="gmapping",
        node_type="slam_gmapping",
        name="slam_gmapping",
        output="screen",
        args="",
        namespace=""
    )

    # 기본 파라미터(필요 시 덮어쓰기)
    rospy.set_param("~base_frame", base_frame)
    rospy.set_param("~odom_frame", odom_frame)
    rospy.set_param("~map_update_interval", map_update_interval)
    rospy.set_param("~particles", 80)
    rospy.set_param("~xmin", -10.0)
    rospy.set_param("~ymin", -10.0)
    rospy.set_param("~xmax",  10.0)
    rospy.set_param("~ymax",  10.0)
    rospy.set_param("~delta", 0.05)          # 해상도(미터/픽셀)
    rospy.set_param("~linearUpdate", 0.2)    # 선속 이동 누적 시 업데이트
    rospy.set_param("~angularUpdate", 0.1)   # 각속 이동 누적 시 업데이트
    rospy.set_param("~temporalUpdate", -1.0) # 시간 기반 업데이트 비활성(원하면 3.0 등)

    launch.start()
    process = launch.launch(node)
    rospy.loginfo("Gmapping 노드 실행됨 (pid=%s)", process.process.pid)
    return launch, process


# ---------- rosbag 재생(옵션) ----------
def start_rosbag_play(bag_path, rate=1.0, use_sim_time=True):
    if use_sim_time:
        rospy.set_param("/use_sim_time", True)
    cmd = ["rosbag", "play", bag_path, "--clock", "--rate", str(rate)]
    proc = subprocess.Popen(cmd)
    rospy.loginfo("rosbag 재생 시작: %s (pid=%s)", bag_path, proc.pid)
    return proc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_base", default="map_output",
                        help="저장 파일 베이스 경로(확장자 제외). 예: map_output → map_output.pgm/.yaml")
    parser.add_argument("--bag", default=None, help="재생할 rosbag 파일 경로(선택)")
    parser.add_argument("--rate", type=float, default=1.0, help="rosbag 재생 속도 (기본 1.0)")
    parser.add_argument("--params", default=None, help="Gmapping 파라미터 YAML 경로(선택)")
    parser.add_argument("--scan_topic", default="/scan")
    parser.add_argument("--base_frame", default="base_link")
    parser.add_argument("--odom_frame", default="odom")
    parser.add_argument("--map_update_interval", type=float, default=2.0)
    parser.add_argument("--duration", type=float, default=None,
                        help="지정 시 해당 시간(초) 후 저장하고 종료")
    args = parser.parse_args()

    rospy.init_node("gmapping_mapper", anonymous=True)

    # 파라미터 로딩
    params_dict = None
    if args.params and os.path.isfile(args.params):
        with open(args.params, "r") as f:
            params_dict = yaml.safe_load(f)
        rospy.loginfo("파라미터 로딩: %s", args.params)

    # Gmapping 실행
    launch, gm_proc = start_gmapping(
        params_dict=params_dict,
        scan_topic=args.scan_topic,
        base_frame=args.base_frame,
        odom_frame=args.odom_frame,
        map_update_interval=args.map_update_interval
    )

    # /map 구독 및 자동 저장
    recorder = MapRecorder(args.save_base, autosave_secs=3.0)

    # rosbag 재생(옵션)
    bag_proc = None
    if args.bag:
        bag_proc = start_rosbag_play(args.bag, rate=args.rate, use_sim_time=True)

    # 종료/신호 처리
    def handle_sigint(sig, frame):
        rospy.loginfo("SIGINT 수신, 맵 저장 후 종료합니다.")
        recorder.save_once()
        if bag_proc: bag_proc.terminate()
        if launch: launch.shutdown()
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_sigint)

    # duration이 지정되었으면 해당 시간 후 저장한 뒤 종료
    start_time = time.time()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        if args.duration and (time.time() - start_time) >= args.duration:
            rospy.loginfo("지정된 duration(%ss) 경과, 맵 저장 후 종료합니다.", args.duration)
            recorder.save_once()
            break
        rate.sleep()

    # 정리
    if bag_proc:
        try:
            bag_proc.terminate()
        except Exception:
            pass
    if launch:
        try:
            launch.shutdown()
        except Exception:
            pass

    rospy.loginfo("종료 완료.")

if __name__ == "__main__":
    main()
