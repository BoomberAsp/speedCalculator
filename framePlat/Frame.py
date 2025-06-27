import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# from framePlat.Algorithm import process_double_images


# def align_characters(init_data, current_data):
#     """ 基于角色位置或名称的匹配算法 """
#     # 方案一：坐标匹配（适用于UI布局固定的游戏）
#     matched = []
#     for i_char in init_data:
#         min_distance = float('inf')
#         match = None
#         for c_char in current_data:
#             # 计算角色框中心点距离
#             dist = np.linalg.norm(
#                 np.array(i_char['position']) - np.array(c_char['position'])
#             )
#             if dist < min_distance and dist < 50:  # 50像素阈值
#                 min_distance = dist
#                 match = c_char
#         if match:
#             matched.append((i_char, match))
#
#     # 方案二：名称OCR匹配（备用方案）
#     if len(matched) != len(init_data):
#         for i_char in init_data:
#             for c_char in current_data:
#                 if i_char['name'] == c_char['name']:
#                     matched.append((i_char, c_char))
#
#     return matched
#

# def process_double_images(init_img, current_img, battle_idx):
#     ...

# 全局配置
DEFAULT_CHARACTERS = 3  # 双方默认角色数

# 战斗场次管理
num_battles = st.sidebar.number_input("战斗场次", min_value=1, value=1, key='num_battles')

# 主数据容器
all_battles = []

for battle_idx in range(num_battles):
    with st.expander(f"第 {battle_idx + 1} 场战斗数据", expanded=True):

        # 我方角色数据收集
        st.subheader("我方角色")
    #     # 双图上传容器
    #     with st.container(border=True):
    #         col_init, col_current = st.columns(2)
    #
    #         # 初始状态图
    #         with col_init:
    #             st.subheader("初始状态截图")
    #             init_img = st.file_uploader(
    #                 "上传初始行动值截图",
    #                 type=["png", "jpg"],
    #                 key=f"init_img_{battle_idx}",
    #                 help="应包含角色名称和初始行动值百分比"
    #             )
    #             if init_img:
    #                 st.image(init_img, use_column_width=True)
    #
    #         # 当前状态图
    #         with col_current:
    #             st.subheader("当前状态截图")
    #             current_img = st.file_uploader(
    #                 "上传当前行动值截图",
    #                 type=["png", "jpg"],
    #                 key=f"current_img_{battle_idx}",
    #                 help="应与初始图的角色顺序一致"
    #             )
    #             if current_img:
    #                 st.image(current_img, use_column_width=True)
    #
    #     # 识别触发按钮
    #     if init_img and current_img:
    #         if st.button("自动识别双图数据", key=f"ocr_double_{battle_idx}"):
    #             process_double_images(init_img, current_img, battle_idx)
        num_allies = st.number_input(
            "我方角色数量",
            min_value=1,
            value=DEFAULT_CHARACTERS,
            key=f'num_allies_{battle_idx}'
        )
        # 通过图片导入我方数据


        allies = []
        for ally_idx in range(num_allies):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                name = st.text_input(f"角色名", value=f"我方{ally_idx + 1}", key=f'ally_name_{battle_idx}_{ally_idx}')
            with col2:
                init = st.number_input("初始行动值%", min_value=0.0, value=0.0, key=f'ally_init_{battle_idx}_{ally_idx}')
            with col3:
                current = st.number_input("当前行动值%", min_value=0.0, value=100.0,
                                          key=f'ally_current_{battle_idx}_{ally_idx}')
                speed = st.number_input("角色速度(必须至少填写一名我方角色速度)", min_value=0, value=0, key=f'ally_speed_{battle_idx}_{ally_idx}')
            allies.append({
                'name': name,
                'speed': speed if(speed != 0) else None,  # 需后续计算
                'init': init,
                'current': current
            })

        # 敌方角色数据收集
        st.subheader("敌方角色")
        num_enemies = st.number_input(
            "敌方角色数量",
            min_value=1,
            value=DEFAULT_CHARACTERS,
            key=f'num_enemies_{battle_idx}'
        )

        enemies = []
        for enemy_idx in range(num_enemies):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                name = st.text_input(f"角色名", value=f"敌方{enemy_idx + 1}",
                                     key=f'enemy_name_{battle_idx}_{enemy_idx}')
            with col2:
                init = st.number_input("初始行动值%", min_value=0.0, value=0.0,
                                       key=f'enemy_init_{battle_idx}_{enemy_idx}')
            with col3:
                current = st.number_input("当前行动值%", min_value=0.0, value=100.0,
                                          key=f'enemy_current_{battle_idx}_{enemy_idx}')
            enemies.append({
                'name': name,
                'init': init,
                'current': current
            })

        all_battles.append({'allies': allies, 'enemies': enemies})

# 计算逻辑增强版
if st.button("开始计算"):
    results = []

    for battle in all_battles:
        # 预处理我方数据
        valid_allies = [a for a in battle['allies'] if a['current'] > a['init']]

        if not valid_allies:
            st.error(f"第{all_battles.index(battle) + 1}场战斗：我方角色行动值无有效变化")
            continue

        # 核心计算
        for enemy in battle['enemies']:
            enemy_diff = enemy['current'] - enemy['init']
            if enemy_diff <= 0:
                st.warning(f"敌方 {enemy['name']} 行动值未增加，跳过计算")
                continue

            speeds = []
            for ally in valid_allies:
                ally_diff = ally['current'] - ally['init']
                if ally_diff <= 0:
                    continue

                # 使用用户输入的已知速度或通过公式推导
                if 'speed' in ally and ally['speed']:  # 如果用户提供了速度
                    speed = (enemy_diff / ally_diff) * ally['speed']
                else:  # 需要其他方式获取速度
                    speed = None

                if speed:
                    speeds.append(speed)

            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                max_speed = max(speeds)
                results.append({
                    '场次': battle_idx + 1,
                    '敌方名称': enemy['name'],
                    '估算速度（平均）': avg_speed,
                    '最大速度': max_speed,
                    '参考我方角色数': len(speeds)
                })

    # 结果展示
    if results:
        df = pd.DataFrame(results)
        st.subheader("计算结果")
        st.dataframe(df.style.format({'估算速度（平均）': '{:.2f}','最大速度': '{:.2f}'}))


        # 可视化
        fig = px.bar(df, x='敌方名称', y='估算速度（平均）', color='场次', barmode='group')
        st.plotly_chart(fig)
    else:
        st.error("无有效计算结果，请检查输入数据")
