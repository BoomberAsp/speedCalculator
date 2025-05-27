import streamlit as st
import pandas as pd
import plotly.express as px

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
        num_allies = st.number_input(
            "我方角色数量",
            min_value=1,
            value=DEFAULT_CHARACTERS,
            key=f'num_allies_{battle_idx}'
        )

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
                results.append({
                    '场次': battle_idx + 1,
                    '敌方名称': enemy['name'],
                    '估算速度': avg_speed,
                    '参考我方角色数': len(speeds)
                })

    # 结果展示
    if results:
        df = pd.DataFrame(results)
        st.subheader("计算结果")
        st.dataframe(df.style.format({'估算速度': '{:.2f}'}))

        # 可视化
        fig = px.bar(df, x='敌方名称', y='估算速度', color='场次', barmode='group')
        st.plotly_chart(fig)
    else:
        st.error("无有效计算结果，请检查输入数据")
