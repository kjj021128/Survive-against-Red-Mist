import streamlit as st
import random
import time

# --- [1] 도시의 전력 및 장비 데이터베이스 구축 ---
BUDGET = 1300

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

items_db = {
    "K사 앰플 3개": {"cost": 200, "desc": "사망에 이르는 피해를 입을 시, 3회 부활합니다."},
    "T사 수사관 배지": {"cost": 250, "desc": "치명적인 위기의 순간, 단 1회 시간을 정지시켜 회피합니다."},
    "인식 저해 가면": {"cost": 275, "desc": "칼리의 공격이 당신을 향할 확률과 위력을 30% 감소시킵니다."},
    "M사 월광석": {"cost": 425, "desc": "칼리의 정신 착란을 완화하여, 버텨야 할 시간을 18시간으로 단축합니다."}
}

st.set_page_config(page_title="Project Moon: 생존 시뮬레이터", layout="wide")
st.title("🔴 붉은안개 생존 시뮬레이터")
st.markdown("특수 능력이 완전히 개방되었습니다. 전성기 시절의 붉은안개로부터 살아남으십시오.")

# --- [2] 사용자 UI 및 고용 시스템 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛡️ 호위 고용")
    selected_guards = [name for name in guards_db if st.checkbox(f"{name} (비용: {guards_db[name]['cost']})")]

with col2:
    st.subheader("🧰 특이점 장비 구매")
    selected_items = [name for name in items_db if st.checkbox(f"{name} (비용: {items_db[name]['cost']}) - {items_db[name]['desc']}")]

total_cost = sum([guards_db[g]["cost"] for g in selected_guards]) + sum([items_db[i]["cost"] for i in selected_items])
st.write("---")
st.markdown(f"### 💰 현재 소모 광기: **{total_cost}** / {BUDGET}")

# --- [3] 시뮬레이션 논리 및 실행 ---
if st.button("⏳ 시뮬레이션 시작"):
    if total_cost > BUDGET:
        st.error("경고: 소지한 광기를 초과했습니다. 조합을 수정하십시오.")
    elif not selected_guards and not selected_items:
        st.error("아무런 대비 없이 붉은안개를 맞이할 수는 없습니다.")
    else:
        st.write("---")
        st.subheader("⚔️ 생존 기록 로그")
        
        # 기본 장비 변수
        target_hours = 18 if "M사 월광석" in selected_items else 24
        revives_left = 3 if "K사 앰플 3개" in selected_items else 0
        has_t_badge = "T사 수사관 배지" in selected_items
        aggro_multiplier = 0.7 if "인식 저해 가면" in selected_items else 1.0
        
        # 특수 능력 상태 추적 변수
        team_power_base = sum([guards_db[g]["power"] for g in selected_guards])
        persistent_power_bonus = 0 # 바퀴 황제, 엘레나 등의 누적 스탯 
        kali_perm_debuff = 0
        
        blood_gauge = (100 if "제2권속 산초" in selected_guards else 0) + (300 if "장로 돈키호테" in selected_guards else 0)
        baral_w_serum = 2 if "처형자 바랄" in selected_guards else 0
        gachiu_shield_used = False
        is_angelica_alive = "검은침묵 안젤리카" in selected_guards
        
        battle_logs = ""
        log_container = st.empty()
        survival_status = True

        # 시간 흐름 루프 시작
        for hour in range(1, target_hours + 1):
            hour_log = f"**🕒 [{hour}시간 경과]**\n"
            
            # [이오리 기믹] 차원 도약
            if "보라눈물 이오리" in selected_guards and hour % 4 == 0:
                hour_log += "> 🔮 **[차원을 걷는 자]** 보라눈물 이오리가 뱀처럼 차원을 열어 당신을 숨겼습니다. (전투 패스)\n\n"
                battle_logs += hour_log
                log_container.markdown(battle_logs)
                time.sleep(0.3)
                continue

            # [호위 전력 계산]
            current_team_power = team_power_base + persistent_power_bonus
            
            if "옥기린 가치우" in selected_guards: 
                current_team_power *= 1.2
                # [수정점] 상시 유지 버프는 1시간째에 한 번만 출력되도록 제한
                if hour == 1:
                    hour_log += "> 🐉 **[천강성의 오망]** 옥기린의 가르침으로, 아군 전체의 방어 점수가 1.2배 증폭됩니다!\n\n"
                
            if "어느 싱클레어" in selected_guards and hour <= 4: 
                current_team_power += guards_db["어느 싱클레어"]["power"]
                # [수정점] 4시간 동안 유지되는 초반 버프 역시 1시간째에 한 번만 선언
                if hour == 1:
                    hour_log += "> 🌿 **[아브락사스의 전차]** 싱클레어가 전차와도 같은 맹렬한 기세로 전열을 굳힙니다!\n\n"
                
            if is_angelica_alive: 
                angelica_buff = random.randint(5, 45)
                current_team_power += angelica_buff
                # 안젤리카의 버프는 매시간 수치가 바뀌는 '동적' 스킬이므로 그대로 둡니다.
                hour_log += f"> 🧤 **[차원장갑]** 검은침묵 안젤리카가 무작위 공방 무기를 전개합니다. (추가 방어 점수 +{angelica_buff})\n\n"

            # [칼리 기본 공격력 결정]
            if hour <= 12:
                kali_max_roll = 10 if "R사 제 4무리 대장들" in selected_guards else 20
                kali_base = 40 + (hour * 4) 
                kali_roll = random.randint(kali_base - 10, kali_base + kali_max_roll)
                if hour == 1:
                    hour_log += "> 🗡️ **[전투 개시]** 붉은안개가 대검을 가볍게 쥐고 천천히 접근합니다.\n\n"
            else:
                kali_max_roll = 15 if "R사 제 4무리 대장들" in selected_guards else 40
                kali_base = 88 + ((hour - 12) * 18) 
                kali_roll = random.randint(kali_base - 15, kali_base + kali_max_roll)
                if hour == 13:
                    hour_log += "> 🩸 **[E.G.O 발현]** *\"이것이... 내 껍데기다.\"* 칼리가 붉은 흉갑에 휩싸이며 위력이 폭증합니다!\n\n"
                if hour == 20:
                    kali_roll = 200
                    hour_log += "> ⚠️ **[대절단 - 가로]** *\"갈라져라!\"* 붉은안개가 모든 것을 양단하는 필살의 참격을 날립니다!\n\n"

            # [디버프 적용 계산 (화상, 베스파, 롤랑 등)]
            burn_debuff = (2 if "천퇴성 뇌횡" in selected_guards else 0) + (3 if "E.G.O 발현 샤오" in selected_guards else 0) + (3 if "붉은시선 베르길리우스" in selected_guards else 0)
            current_burn_penalty = burn_debuff * (hour // 2)
            temp_debuff = current_burn_penalty + kali_perm_debuff
            
            if current_burn_penalty > 0:
                hour_log += f"> 🔥 **[화상 누적]** 타오르는 불꽃이 칼리의 육체를 갉아먹어 위력을 {current_burn_penalty}만큼 깎아냅니다.\n\n"
            
            if "노란작살 베스파" in selected_guards and hour % 3 == 0: 
                temp_debuff += 30
                hour_log += "> 🐝 **[궁니르 공명]** 노란작살 베스파가 맹렬한 찌르기로 칼리의 템포를 늦춥니다! (위력 -30)\n\n"
            
            furioso_cycle = 4 if not is_angelica_alive and "검은침묵 롤랑 (광란)" in selected_guards else 6
            if "검은침묵 롤랑 (광란)" in selected_guards and hour % furioso_cycle == 0: 
                temp_debuff += 50
                if is_angelica_alive:
                    hour_log += "> ⬛ **[Furioso]** 롤랑이 9개의 공방 무기를 난무하여 칼리의 흐름을 완전히 끊어냅니다! (위력 -50)\n\n"
                else:
                    hour_log += "> ⬛ **[Furioso]** 롤랑이 안젤리카를 잃은 분노로 미친 듯이 무기를 휘두릅니다! (위력 -50)\n\n"
            
            if "R사 제 4무리 대장들" in selected_guards:
                hour_log += "> 🎯 **[처분 표식]** 니콜라이의 지휘로 칼리의 위력 최댓값이 억제되고 있습니다.\n"

            # [칼리 최종 공격력 산출]
            effective_kali_attack = int((kali_roll - temp_debuff) * aggro_multiplier)
            if effective_kali_attack < 0: effective_kali_attack = 0

            # [거미집 아비들 전원 기믹]
            if "거미집 아비들 전원" in selected_guards:
                finger_cycle = hour % 5
                if finger_cycle == 1: 
                    current_team_power += 15
                    hour_log += "> 🧥 **[엄지의 규율]** 발렌치나가 기세를 발산해 방어 점수가 15 상승합니다.\n\n"
                elif finger_cycle == 2: 
                    if random.random() < 0.15: 
                        effective_kali_attack = 0
                        hour_log += "> 📜 **[검지의 지령]** 헤르메스의 의지로 공격을 흘려보냈습니다!\n\n"
                elif finger_cycle == 3: 
                    if effective_kali_attack > current_team_power:
                        damage_diff = effective_kali_attack - current_team_power
                        counter_reflect = int(damage_diff * 0.25)
                        effective_kali_attack -= counter_reflect
                        hour_log += f"> ⛓️ **[중지의 반격]** 마티아스가 받은 피해의 25%({counter_reflect})를 역으로 상쇄했습니다.\n\n"
                    else:
                        hour_log += "> ⛓️ **[중지의 대기]** 마티아스가 반격을 준비했으나, 칼리의 참격이 닿지 않았습니다.\n\n"
                elif finger_cycle == 4: 
                    effective_kali_attack -= 15
                    if effective_kali_attack < 0: effective_kali_attack = 0
                    hour_log += "> 🎨 **[약지의 예술]** 칼리스토의 예술적인 조형물로 위력을 15 감소시켰습니다.\n\n"
                elif finger_cycle == 0: 
                    kali_perm_debuff += 5
                    effective_kali_attack -= 5
                    if effective_kali_attack < 0: effective_kali_attack = 0
                    hour_log += "> 🤫 **[천살성도 발도]** 시오미 요루가 천살성도로 칼리를 상처입힙니다. 위력이 영구적으로 5 감소합니다.\n\n"

            # [최종 방어 판정]
            time.sleep(0.3)
            if current_team_power >= effective_kali_attack:
                if "바퀴 황제" in selected_guards: 
                    persistent_power_bonus += 4
                    hour_log += "> 🪳 **[황제의 피]** 바퀴 황제가 칼리의 참격을 버텨내며 외골격을 단단하게 진화시킵니다. (영구 방어선 +4)\n\n"
                if "핏빛 밤 엘레나" in selected_guards: 
                    persistent_power_bonus += 2
                    hour_log += "> 🧛‍♀️ **[퍼져나가는 혈액]** 핏빛 밤 엘레나가 흩뿌려진 피를 흡수하여 방어선을 복구합니다. (영구 방어선 +2)\n\n"
                
                hour_log += f"> 🛡️ **방어 성공!** (칼리의 위력: {effective_kali_attack} / 호위 방어선: {int(current_team_power)})\n\n"
            else:
                if "푸른잔향 아르갈리아" in selected_guards and (effective_kali_attack - current_team_power) <= 5:
                    persistent_power_bonus += 10
                    hour_log += f"> 🎸 **아르갈리아의 공명!** 치명적인 참격의 진동을 무력화하고 영구적인 흐름을 가져옵니다.\n\n"
                elif blood_gauge >= 50:
                    blood_gauge -= 50
                    hour_log += f"> 🩸 **경혈식 발동!** 혈액을 소모하여 버텼습니다. (남은 혈액: {blood_gauge})\n\n"
                elif baral_w_serum > 0:
                    baral_w_serum -= 1
                    hour_log += f"> 💉 **처형자 바랄 개입!** 혈청 W를 투입해 공간을 격리했습니다. (남은 회피: {baral_w_serum})\n\n"
                elif "옥기린 가치우" in selected_guards and not gachiu_shield_used:
                    gachiu_shield_used = True
                    hour_log += f"> 🍂 **가치우의 인협!** 가치우가 당신을 밀쳐내고 붉은안개의 맹공을 홀로 받아냈습니다!\n\n"
                elif has_t_badge:
                    has_t_badge = False
                    hour_log += f"> ⚠️ **방어선 붕괴!** T사 수사관 배지를 사용해 시간을 멈추고 도망칩니다.\n\n"
                elif revives_left > 0:
                    revives_left -= 1
                    if is_angelica_alive and random.random() < 0.5: is_angelica_alive = False
                    hour_log += f"> 💊 **치명상 발생!** K사 앰플의 효과로 육체가 즉시 수복됩니다. (남은 앰플: {revives_left})\n\n"
                else:
                    hour_log += f"> 💀 **방어 수단 소진...** 붉은안개의 대검이 당신을 갈랐습니다.\n\n"
                    battle_logs += hour_log
                    log_container.markdown(battle_logs)
                    survival_status = False
                    break
            
            # [시간 경과 후처리 기믹]
            if "어느 싱클레어" in selected_guards and hour == 4:
                team_power_base -= guards_db["어느 싱클레어"]["power"]
                kali_perm_debuff += 5
                hour_log += "> 🍂 **[알을 깨고 나온 자]** 힘을 다한 싱클레어가 물러나며, 연기 장막을 영구적으로 남깁니다.\n\n"
            
            battle_logs += hour_log
            log_container.markdown(battle_logs)

        # 결과 출력
        st.write("---")
        if survival_status:
            st.success(f"🎉 **미션 성공!** {target_hours}시간 동안 붉은안개로부터 살아남았습니다. 칼리가 쑥쓰러운 듯 사과를 남기고 빠르게 시야 너머로 사라집니다.")
        else:
            st.error("💀 **미션 실패.** 호위들은 전멸했고, 당신의 기록은 여기서 끊어졌습니다.")
