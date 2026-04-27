import streamlit as st
import random
import time

# --- [1] 도시의 전력 및 장비 데이터베이스 구축 ---
BUDGET = 1300

# 호위 목록 (이름: [가격, 전투/지연력 수치])
# 수치는 설정상 무력, 생존력, 지연전 적합도를 종합한 척도입니다.
guards_db = {
    "천퇴성 뇌횡": {"cost": 300, "power": 30},
    "어느 싱클레어": {"cost": 400, "power": 45}, 
    "제2권속 산초": {"cost": 450, "power": 55}, 
    "R사 제 4무리 대장들": {"cost": 500, "power": 60},
    "E.G.O 발현 샤오": {"cost": 500, "power": 65},
    "노란작살 베스파": {"cost": 525, "power": 68},
    "붉은시선 베르길리우스": {"cost": 550, "power": 75},
    "옥기린 가치우": {"cost": 550, "power": 70},
    "푸른잔향 아르갈리아": {"cost": 575, "power": 78},
    "검은침묵 롤랑 (광란)": {"cost": 600, "power": 85},
    "검은침묵 안젤리카": {"cost": 600, "power": 82},
    "보라눈물 이오리": {"cost": 625, "power": 90},
    "처형자 바랄": {"cost": 650, "power": 95},
    "바퀴 황제": {"cost": 675, "power": 80}, 
    "거미집 아비들 전원": {"cost": 800, "power": 110},
    "핏빛 밤 엘레나": {"cost": 850, "power": 115},
    "장로 돈키호테": {"cost": 900, "power": 130}
}

# 장비 목록 (이름: [가격, 효과 설명])
items_db = {
    "K사 앰플 3개": {"cost": 200, "desc": "사망에 이르는 피해를 입을 시, 3회 부활합니다."},
    "T사 수사관 배지": {"cost": 250, "desc": "치명적인 위기 순간, 단 1회 시간을 정지시켜 회피합니다."},
    "인식 저해 가면": {"cost": 275, "desc": "칼리의 공격이 당신을 향할 확률과 위력을 30% 감소시킵니다."},
    "M사 월광석": {"cost": 300, "desc": "칼리의 정신 착란을 완화하여, 버텨야 할 시간을 12시간으로 단축합니다."}
}

st.set_page_config(page_title="Project Moon: 생존 시뮬레이터", layout="wide")
st.title("🩸 붉은안개 생존 시뮬레이터")
st.markdown("전성기 시절의 붉은안개 칼리로부터 살아남기 위해 전력을 구성하십시오.")

# --- [2] 사용자 UI 및 고용 시스템 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛡️ 호위 고용")
    selected_guards = []
    for name, data in guards_db.items():
        if st.checkbox(f"{name} (비용: {data['cost']} 광기)"):
            selected_guards.append(name)

with col2:
    st.subheader("🧰 특이점 장비 구매")
    selected_items = []
    for name, data in items_db.items():
        if st.checkbox(f"{name} (비용: {data['cost']} 광기) - {data['desc']}"):
            selected_items.append(name)

# 예산 계산
total_cost = sum([guards_db[g]["cost"] for g in selected_guards]) + sum([items_db[i]["cost"] for i in selected_items])
st.write("---")
st.markdown(f"### 💰 현재 소모 광기: **{total_cost}** / {BUDGET}")

# --- [3] 시뮬레이션 논리 및 실행 ---
if st.button("⏳ 시뮬레이션 시작"):
    if total_cost > BUDGET:
        st.error("경고: 소지한 광기(1300)를 초과했습니다. 조합을 수정하십시오.")
    elif len(selected_guards) == 0 and len(selected_items) == 0:
        st.error("아무런 대비 없이 붉은안개를 맞이할 수는 없습니다.")
    else:
        st.write("---")
        st.subheader("⚔️ 생존 기록 로그")
        
        # 장비 효과 초기화
        target_hours = 12 if "M사 월광석" in selected_items else 24
        revives_left = 3 if "K사 앰플 3개" in selected_items else 0
        has_t_badge = True if "T사 수사관 배지" in selected_items else False
        aggro_multiplier = 0.7 if "인식 저해 가면" in selected_items else 1.0
        
        # 호위 전력 합산
        team_power = sum([guards_db[g]["power"] for g in selected_guards])
        
        survival_status = True
        log_container = st.empty()
        battle_logs = ""

        # 시간 흐름에 따른 전투 루프
        for hour in range(1, target_hours + 1):
            # 시간이 지날수록 칼리의 E.G.O 발현 및 분노로 인해 기본 공격력이 상승함
            kali_base_attack = 40 + (hour * 6)
            kali_roll = random.randint(kali_base_attack - 15, kali_base_attack + 35)
            
            # 인식 저해 가면 효과 적용 (나를 향한 공격 위력 감소)
            effective_kali_attack = int(kali_roll * aggro_multiplier)
            
            time.sleep(0.3) # 로그 연출을 위한 딜레이
            
            if team_power >= effective_kali_attack:
                battle_logs += f"🕒 **[{hour}시간 경과]** 호위들이 붉은안개의 맹공을 막아냈습니다. (칼리의 위력: {effective_kali_attack} / 호위 방어선: {team_power})\n\n"
            else:
                # 방어선이 뚫렸을 때 장비 효과 발동 판정
                if has_t_badge:
                    battle_logs += f"⚠️ **[{hour}시간 경과]** 방어선 붕괴! 붉은안개의 대검이 목을 노리지만, **[T사 수사관 배지]**로 시간을 멈추고 회피했습니다! (배지 파괴됨)\n\n"
                    has_t_badge = False
                elif revives_left > 0:
                    revives_left -= 1
                    battle_logs += f"🩸 **[{hour}시간 경과]** 치명상 발생! 그러나 **[K사 앰플]**의 효과로 육체가 즉시 수복되었습니다. (남은 앰플: {revives_left}개)\n\n"
                else:
                    battle_logs += f"💀 **[{hour}시간 경과]** 모든 방어 수단이 소진되었습니다. 붉은안개의 대검에 의해 사망했습니다.\n\n"
                    survival_status = False
                    break
            
            log_container.markdown(battle_logs)

        # 최종 결과 출력
        st.write("---")
        if survival_status:
            st.success(f"🎉 **미션 성공!** {target_hours}시간 동안 붉은안개로부터 무사히 살아남았습니다. 그녀의 착란이 멎었습니다.")
        else:
            st.error("💀 **미션 실패.** 당신의 기록은 여기서 끊어졌습니다.")