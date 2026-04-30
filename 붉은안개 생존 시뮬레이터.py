import streamlit as st
import random
import time
import re

# --- [1] 도시의 전력 및 장비 데이터베이스 구축 ---
BUDGET = 1300

# 호위 목록 (이름: [가격, 기본 수치, 주사위 최댓값])
guards_db = {
    "리카르도": {"cost": 225, "power": 20, "dice": 10},
    "에즈라": {"cost": 250, "power": 25, "dice": 10},
    "모제스": {"cost": 275, "power": 0, "dice": 10},
    "뇌횡": {"cost": 300, "power": 30, "dice": 15},
    "어느 싱클레어": {"cost": 400, "power": 60, "dice": 10}, 
    "산초": {"cost": 450, "power": 55, "dice": 15}, 
    "니콜라이": {"cost": 500, "power": 60, "dice": 20},
    "샤오": {"cost": 500, "power": 65, "dice": 20},
    "엄지 아비 발렌치나": {"cost": 500, "power": 65, "dice": 20},
    "중지 아비 마티아스": {"cost": 500, "power": 66, "dice": 20},
    "노란작살 베스파": {"cost": 525, "power": 68, "dice": 20},
    "검지 아비 뤼엔": {"cost": 525, "power": 68, "dice": 20},
    "붉은시선 베르길리우스": {"cost": 550, "power": 75, "dice": 20},
    "가치우": {"cost": 550, "power": 70, "dice": 20},
    "푸른잔향 아르갈리아": {"cost": 575, "power": 78, "dice": 25},
    "롤랑": {"cost": 600, "power": 85, "dice": 25},
    "검은침묵 안젤리카": {"cost": 600, "power": 82, "dice": 25},
    "보라눈물 이오리": {"cost": 625, "power": 90, "dice": 25},
    "처형자 바랄": {"cost": 650, "power": 95, "dice": 25},
    "바퀴 황제": {"cost": 675, "power": 80, "dice": 30}, 
    "핏빛 밤 엘레나": {"cost": 850, "power": 115, "dice": 30},
    "장로 돈키호테": {"cost": 900, "power": 130, "dice": 30}
}

items_db = {
    "T사 보조 태엽": {"cost": 150, "desc": "매 시간 종료 시 25% 확률로 시간을 가속하여, 누적 효과(화상, 적응, 회복)를 한 번 더 발동시킵니다."},
    "K사 앰플 3개": {"cost": 200, "desc": "사망에 이르는 피해를 입을 시, 3회 부활합니다."},
    "T사 수사관 배지": {"cost": 250, "desc": "치명적인 위기의 순간, 붉은안개가 기세를 올리기 전으로 시간을 되감습니다."},
    "인식 저해 가면": {"cost": 275, "desc": "칼리의 공격이 당신을 향할 확률과 위력을 30% 감소시킵니다."},
    "M사 월광석": {"cost": 425, "desc": "칼리가 이성을 되찾는 데 도움을 줘, 버텨야 할 시간을 18시간으로 단축합니다."}
}

st.set_page_config(page_title="붉은안개로부터 살아남기", layout="wide")
st.title("붉은안개 생존 시뮬레이터")
st.markdown("칼리가 당신을 연구소 테러범으로 착각하여, 미미크리를 뽑아듭니다...행운을 빌어요!")

st.write("---")

# --- [2] 사용자 UI 및 고용 시스템 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛡️ 호위 고용")
    g_names = list(guards_db.keys())
    half = (len(g_names) + 1) // 2
    g_col1, g_col2 = st.columns(2)
    
    selected_guards = []
    with g_col1:
        for name in g_names[:half]:
            if st.checkbox(f"{name} ({guards_db[name]['cost']})", key=f"check_{name}"):
                selected_guards.append(name)
    with g_col2:
        for name in g_names[half:]:
            if st.checkbox(f"{name} ({guards_db[name]['cost']})", key=f"check_{name}"):
                selected_guards.append(name)

with col2:
    st.subheader("🧰 특이점 장비 구매")
    selected_items = [name for name in items_db if st.checkbox(f"{name} ({items_db[name]['cost']}) - {items_db[name]['desc']}")]

st.write("---")


synergy_messages = []
discount = 0

# 1. 검은침묵 부부 시너지
if "롤랑" in selected_guards and "검은침묵 안젤리카" in selected_guards:
    synergy_messages.append("💡 **[시너지 발견: 부부 동반 의뢰]** 부부가 전장에 함께 섭니다! (시작 시 K사 앰플과 T사 배지 무료 지급)")

# 2. 뒤틀림 탐정 시너지
detective_team = [g for g in selected_guards if g in ["모제스", "에즈라", "노란작살 베스파"]]
if len(detective_team) >= 2:
    discount = 200
    synergy_messages.append(f"💡 **[시너지 발견: 에즈라의 흥정]** 에즈라의 탁월한 협상 능력으로 거래가 수월해졌습니다! (고용 비용 200 광기 할인)")

# 3. 엄지 시너지
if "엄지 아비 발렌치나" in selected_guards and "뇌횡" in selected_guards:
    synergy_messages.append("💡 **[시너지 발견: 작열하는 탄환]** 엄지의 이글거리는 탄환이 쏟아집니다! (턴당 화상 부여량 +3)")

# 4. 거미집 시너지
spider_members = ["엄지 아비 발렌치나", "검지 아비 뤼엔", "중지 아비 마티아스"]
spider_count = sum(1 for g in spider_members if g in selected_guards)
if spider_count >= 2:
    synergy_messages.append(f"💡 **[시너지 발견: 거미집의 사냥법]** {spider_count}인의 아비가 모여 거미줄을 칩니다! (붉은안개의 위력 -40)")

# 5. 특색 시너지
color_fixers = [g for g in selected_guards if g in ["푸른잔향 아르갈리아", "붉은시선 베르길리우스", "노란작살 베스파", "검은침묵 안젤리카", "보라눈물 이오리"]]
if len(color_fixers) >= 2:
    synergy_messages.append("💡 **[시너지 발견: 컬러 팔레트]** 특색 해결사들이 모였습니다! (아군 진형의 영구 방어선 +30)")

# 6. 소지 시너지
if "가치우" in selected_guards and "뇌횡" in selected_guards:
    synergy_messages.append("💡 **[시너지 발견: 엇갈린 맹약]** 인협과 호걸의 기묘한 조화가 이루어집니다! (아군 진형의 영구 방어선 +15)")

# 7. 차원 유랑 시너지
if "처형자 바랄" in selected_guards and "보라눈물 이오리" in selected_guards:
    synergy_messages.append("💡 **[시너지 발견: 차원 도약]** 이오리와 바랄이 차원을 가로지르는 경험에 대해 의견을 교환합니다! (바랄의 혈청 W를 추가로 한 번 더 사용 가능)")

# 8. 무기 진심녀 시너지
if "에즈라" in selected_guards and "검은침묵 안젤리카" in selected_guards:
    synergy_messages.append("💡 **[시너지 발견: 무기 진심녀]** 두 여전사가 공방의 무기와 방어구에 대한 수다를 시작합니다! (30% 확률로 에즈라가 무기를 한 번 더 전개)")

# 9. 연기 전쟁 시너지
smoke_war = ["에즈라", "모제스", "어느 싱클레어", "니콜라이", "엄지 아비 발렌치나", "바퀴 황제", "롤랑"]
smoke_war_count = sum(1 for g in smoke_war if g in selected_guards)
if smoke_war_count >= 3:  # 발동 조건을 3인 이상으로 빡빡하게 올림!
    smoke_penalty = smoke_war_count * 4
    synergy_messages.append(f"💡 **[시너지 발견: 연기전쟁의 참상]** {smoke_war_count}인의 참전용사가 모여, 끔찍한 진흙탕 싸움을 유도합니다! (매 4시간마다 붉은안개의 위력 -{smoke_penalty})")

# 10. 원본과 모조품 시너지
if "롤랑" in selected_guards and "검지 아비 뤼엔" in selected_guards:
    synergy_messages.append("💡 **[시너지 발견: 진품과 모조품]** 뤼엔과 롤랑이 기묘한 이중주를 전장에 그려냅니다! (필살기 발동 확률 및 피해량이 증가, 뤼엔의 공격이 빗나가지 않음)")

if synergy_messages:
    for msg in synergy_messages:
        st.success(msg)

# 최종 비용 산출 (할인 적용)
total_cost = sum([guards_db[g]["cost"] for g in selected_guards]) + sum([items_db[i]["cost"] for i in selected_items])
total_cost -= discount 

st.markdown(f"### 💰 현재 소모 광기: **{total_cost}** / {BUDGET}")

# --- [3] 시뮬레이션 논리 및 실행 ---
if st.button("⏳ 시뮬레이션 시작"):
    if total_cost > BUDGET:
        st.error("경고: 소지한 광기를 초과했습니다. 조합을 수정하십시오.")
    elif not selected_guards and not selected_items:
        st.error("아무런 대비 없이 붉은안개를 맞이할 수는 없습니다.")
    else:
        initial_guards = selected_guards.copy()
        initial_items = selected_items.copy()
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
        carried_shield = 0

        battle_logs = ""
        
        blood_gauge = (100 if "산초" in selected_guards else 0) + (250 if "장로 돈키호테" in selected_guards else 0)
        baral_w_serum = 3 if "처형자 바랄" in selected_guards else 0
        if "처형자 바랄" in selected_guards and "보라눈물 이오리" in selected_guards:
            baral_w_serum += 1
            battle_logs += "> 🌌 :blue[**[시너지 발동: 차원 유랑]**] 이오리가 차원의 문을 열어 바랄의 혈청 W 실린더를 하나 더 꺼내옵니다. (혈청 W 사용 가능 횟수 +1)\n\n"
        is_roland_berserk = False
        last_hour_gap = 0  # 직전 시간의 위력 격차 저장
        gachiu_shield_used = False
        is_angelica_alive = "검은침묵 안젤리카" in selected_guards

        # --- [시너지 전투 수치 적용 구역] ---
        thumb_burn_bonus = 0 # 엄지 시너지 화상 보너스 초기화
        
        # 1. 검은침묵 부부 시너지
        if "롤랑" in selected_guards and "검은침묵 안젤리카" in selected_guards:
            revives_left += 1  # K사 앰플 1회 분량 추가 (또는 3회로 하려면 += 3)
            has_t_badge = True # T사 배지 강제 활성화

        # 2. 뒤틀림 탐정 시너지
        # (결제 화면에서 200광기 할인으로 이미 완벽히 처리되었으므로 전투 수치 변동은 없음!)

        # 3. 엄지 시너지
        if "엄지 아비 발렌치나" in selected_guards and "뇌횡" in selected_guards:
            thumb_burn_bonus = 3

        # 4. 거미집 시너지 (초기 영구 디버프)
        spider_count = sum(1 for g in ["엄지 아비 발렌치나", "검지 아비 뤼엔", "중지 아비 마티아스"] if g in selected_guards)
        if spider_count >= 2:
            kali_perm_debuff += 40

        # 5. 특색 시너지 (영구 방어선 증가)
        color_fixers = [g for g in selected_guards if g in ["푸른잔향 아르갈리아", "붉은시선 베르길리우스", "노란작살 베스파", "검은침묵 안젤리카"]]
        if len(color_fixers) >= 2:
            persistent_power_bonus += 30

        # 6. 소지 시너지 (영구 방어선 증가)
        if "가치우" in selected_guards and "뇌횡" in selected_guards:
            persistent_power_bonus += 15

        log_container = st.empty()
        survival_status = True

        shin_users = ["에즈라", "뇌횡", "어느 싱클레어", "엄지 아비 발렌치나", "노란작살 베스파", "검지 아비 뤼엔", "붉은시선 베르길리우스", "가치우"]

        has_t_gear = "T사 보조 태엽" in selected_items
        t_gear_triggers = 0  # 가속이 터진 횟수 누적

        smoke_war_members = ["에즈라", "모제스", "어느 싱클레어", "니콜라이", "엄지 아비 발렌치나", "바퀴 황제", "롤랑"]
        smoke_war_count_sim = sum(1 for g in smoke_war_members if g in selected_guards)
        is_smoke_war = smoke_war_count_sim >= 3 # 3명 이상일 때만 True

        # 리카르도의 장부 기록용 변수
        previous_missed_guards = []

        # 시간 흐름 루프 시작
        for hour in range(1, target_hours + 1):
            hour_log = f"#### **🕒 {hour}시간 경과**\n"
            missed_guards_this_turn = []
            
            if hour == 1:
                hour_log += "> 🗡️ **[전투 개시]** 붉은안개가 당신과 호위들을 향해 천천히 접근합니다.\n\n"
            elif hour == 13:
                hour_log += "> 🔴 :red[**[E.G.O 발현]**] 칼리가 붉은 갑주로 스스로를 감싸며 엄청난 살의를 내뿜습니다!\n\n"
                if any(g in selected_guards for g in shin_users):
                    hour_log += "> 💫 :yellow[**[신(心) 발산]**] 압도적인 공포 앞에서도, 경지에 이른 전사들의 투지는 꺾이지 않습니다. (신 사용자 1명 당 방어선 영구 +15)\n\n"
            elif hour == 21:
                hour_log += "> ⚠️ :red[**[대절단 - 가로]**] 붉은안개가 모든 것을 양단하는 필살의 참격을 날립니다!\n\n"
                if "처형자 바랄" in selected_guards:
                    hour_log += "> 💉 :red[**[무력화]**] 처형자 바랄이 가볍게 손을 내밀어, 칼리의 붉은 파동을 억눌러 소멸시킵니다!\n\n"

            # 🪖 [연기전쟁의 참상] 3인 이상 스케일링 기믹
            if is_smoke_war and hour % 6 == 0:
                smoke_penalty = smoke_war_count_sim * 4
                kali_perm_debuff += smoke_penalty
                hour_log += f"> 🪖 :blue[**[시너지 발동: 사람 냄새 나는 연기]**] {smoke_war_count_sim}인의 참전용사들이 뿜어낸 매캐한 연기가 칼리의 폐부를 찌릅니다! (칼리 영구 위력 -{smoke_penalty})\n\n"
            
            # 이오리 기믹 처리
            if "보라눈물 이오리" in selected_guards and hour % 4 == 0:
                hour_log += "> 🐍 **[차원을 걷는 자]** 보라눈물 이오리가 차원을 열어 당신을 숨겼습니다. (전투 패스)\n\n"
                battle_logs += hour_log
                log_container.markdown(battle_logs)
                time.sleep(0.3)
                continue
                

            # 호위 전력 및 주사위 난수 계산
            current_team_power = persistent_power_bonus + carried_shield # 영구 버프(바퀴 황제 등)부터 시작
            if carried_shield > 0:
                hour_log += f"> 💪 **[기세 유지]** 이전 시간의 압도적인 우위로 기세를 이어갑니다. (이월된 방어선 +{carried_shield})\n\n"
                carried_shield = 0 # 적용했으니 다음 턴을 위해 다시 0으로 초기화합니다.
            if len(selected_guards) == 0:
                current_team_power = 0
                hour_log += "> 😨 **[고립무원]** 곁을 지켜주던 모든 호위가 쓰러졌습니다. 당신은 맨몸으로 붉은안개와 마주합니다...\n\n"
            
            for guard in selected_guards:
                base_power = guards_db[guard]["power"]
                max_dice = guards_db[guard]["dice"]
                if guard == "검지 아비 뤼엔" and "롤랑" in selected_guards:
                    max_dice = max(5, max_dice // 2)

                if max_dice > 0:
                    roll = random.randint(1, max_dice)
                    if guard in shin_users and hour >= 13:
                        current_team_power += 15
                    current_team_power += (base_power + roll)
                    
                    # 🎯 필살기 발동 로직 - 주사위가 최댓값이 떴을 때!
                    if roll == max_dice:
                        if guard == "리카르도":
                            current_team_power += 15
                            hour_log += "> 🕶️ :red[**[전원, 처형이다!]**] 리카르도가 원한 문신의 힘을 끌어내 지면을 강타합니다!\n\n"
                            
                        elif guard == "에즈라":
                            current_team_power += 15
                            hour_log += "> 🦮 :red[**[유리아 공방 - 총공 모드, 마크 17!]**] 에즈라가 온갖 무기를 한꺼번에 전개하여 화력을 쏟아붓습니다!\n\n"
                        
                        elif guard == "모제스":
                            kali_perm_debuff += 10 
                            hour_log += "> 👁️ :red[**[붉은 점]**] 모제스가 연기 너머로 E.G.O의 가장 취약한 틈새를 꿰뚫어 봅니다! (칼리 영구 위력 -10)\n\n"
                        
                        elif guard == "뇌횡":
                            current_team_power += 20
                            hour_log += "> 🐯 :red[**[초절맹호살격난참]**] 뇌횡이 맹호의 기세로 적의 숨통을 끊을 난격을 꽂아 넣습니다!\n\n"
                        
                        elif guard == "어느 싱클레어":
                            current_team_power += 25
                            hour_log += "> 🐣 :red[**[취수낭랑 - 성]**] 어느 싱클레어의 할버드와 대검이 붉은안개의 참격을 깔끔하게 흘려냅니다!\n\n"
                        
                        elif guard == "산초":
                            current_team_power += 30
                            hour_log += "> 🩸 :red[**[아류 산초 경혈식 - 라 샹그레]**] 산초가 끓어오르는 피를 창끝에 모아 폭발시킵니다!\n\n"
                        
                        elif guard == "니콜라이":
                            current_team_power += 35
                            hour_log += "> 🎯 :red[**[처분]**] 니콜라이가 붉은안개에게 처분 표식을 새겨넣고, 검으로 주홍빛 궤적을 그려냅니다!\n\n"
                        
                        elif guard == "샤오":
                            current_team_power += 35
                            hour_log += "> 🐉 :red[**[도철]**] 샤오가 불타오르는 언월도를 휘두르며 거대한 화염의 용을 뿜어냅니다!\n\n"
                        
                        elif guard == "엄지 아비 발렌치나":
                            current_team_power += 35
                            hour_log += "> 🤺 :red[**[처분]**] 발렌치나가 원망을 실은 칼날 두 자루를 무자비하게 휘두릅니다!\n\n"
                        
                        elif guard == "중지 아비 마티아스":
                            current_team_power += 35
                            hour_log += "> ⛓️ :red[**[즉결처형 - 레바테인]**] 마티아스가 장부의 기록에 따라 피할 수 없는 징벌을 내립니다!\n\n"
                        
                        elif guard == "노란작살 베스파":
                            current_team_power += 40
                            hour_log += "> 🐝 :red[**[섬봉광검술 - 환도]**] 베스파가 시야에서 사라진 순간, 사각을 파고드는 치명적인 참격이 작렬합니다!\n\n"
                        
                        elif guard == "검지 아비 뤼엔":
                            if "롤랑" in selected_guards:
                                current_team_power += 60
                                hour_log += "> 📜 :red[**[Furioso - Resonance]**] 뤼엔이 원본의 움직임에 완벽히 동기화하여 파괴적인 모방 난무를 펼칩니다!\n\n"
                            else:
                                current_team_power += 40
                                hour_log += "> 📜 :red[**[Furioso - Replica]**] 뤼엔이 헤르메스의 의지로 검은침묵의 난무를 기괴하게 모방해냅니다!\n\n"
                        
                        elif guard == "붉은시선 베르길리우스":
                            current_team_power += 45
                            hour_log += "> 🩸 :red[**[죽은 혈귀를 위한 장례]**] 베르길리우스의 글라디우스가 피의 궤적을 그리며 주변을 압도합니다!\n\n"
                        
                        elif guard == "가치우":
                            current_team_power += 45
                            hour_log += "> 🍂 :red[**[천강성 - 격]**] 가치우의 봉에 다섯 개의 망이 감기고, 파괴적인 힘을 뿜어냅니다!\n\n"
                        
                        elif guard == "푸른잔향 아르갈리아":
                            current_team_power += 50
                            hour_log += "> 🎼 :red[**[최후의 선율]**] 아르갈리아가 광소하며 치명적인 진동의 낫을 휘두릅니다!\n\n"
                        
                        elif guard == "롤랑":
                            if "검지 아비 뤼엔" in selected_guards:
                                current_team_power += 75
                                hour_log += "> ⬛ :red[**[Furioso - Original]**] 롤랑이 모조품 앞에서 원본의 품격을 보여줍니다!\n\n"
                            else:
                                current_team_power += 50
                                hour_log += "> ⬛ :red[**[Furioso]**] 롤랑이 9개의 무기를 꺼내어 숨 쉴 틈 없는 난무를 펼칩니다!\n\n"
                        
                        elif guard == "검은침묵 안젤리카":
                            current_team_power += 50
                            hour_log += "> 🧤 :red[**[백색 왈츠]**] 안젤리카가 무도회를 거닐듯 우아하고도 파괴적인 공방 무기 연계를 선보입니다!\n\n"
                        
                        elif guard == "보라눈물 이오리":
                            current_team_power += 50
                            hour_log += "> 🐍 :red[**[환영난무]**] 보라눈물이 여러 차원의 자세를 동시에 전개하여 회피불능의 참격을 날립니다!\n\n"
                        
                        elif guard == "처형자 바랄":
                            current_team_power += 55
                            hour_log += "> 💉 :red[**[혈청 R]**] 바랄이 혈청 R을 투여하여 폭발적인 기세로 칼리에게 돌진합니다!\n\n"
                        
                        elif guard == "바퀴 황제":
                            current_team_power += 60
                            hour_log += "> 🪳 :red[**[황제의 적출]**] 진화를 거듭한 황제가 거대한 껍데기를 휘둘러 대지를 짓뭉갭니다!\n\n"
                        
                        elif guard == "핏빛 밤 엘레나":
                            current_team_power += 70
                            hour_log += "> 🧛‍♀️ :red[**[핏빛 밤의 진노]**] 엘레나가 굶주림을 개방하여 시야에 보이는 모든 것을 찢어발깁니다!\n\n"
                        
                        elif guard == "장로 돈키호테":
                            current_team_power += 85
                            hour_log += "> 🎠 :red[**[돈키호테류 경혈 오의 - 구]**] 장로 돈키호테가 만든 피의 구가 폭발하며 전장을 뒤덮습니다!\n\n"
                    # 💥 대실패 발동 로직 - 주사위가 1이 떴을 때
                    elif roll == 1:
                        # 1. 어느 싱클레어 (기본 패시브)
                        if guard == "어느 싱클레어":
                            half_power = base_power // 2
                            penalty = (base_power + 1) - half_power
                            current_team_power -= penalty
                            hour_log += f"> 🐣 **[빗나간 일격]** 어느 싱클레어의 타점이 어긋났지만, 공수부대의 노련함으로 방어선의 절반({half_power})은 사수해냅니다!\n\n"
                        
                        # 2. 검지 아비 뤼엔 (롤랑 시너지 시 발동)
                        elif guard == "검지 아비 뤼엔" and "롤랑" in selected_guards:
                            hour_log += "> 🎭 :blue[**[시너지 발동: 공조의 극의]**] 롤랑의 빈틈없는 엄호가 뤼엔의 서툰 동작을 보완합니다! (빗나감 면역)\n\n"
                        else:
                            current_team_power -= (base_power + 1) # 방금 더했던 위력을 다시 빼서 0으로 무효화
                            hour_log += f"> 🌀 **[빗나감]** {guard}의 공격이 완전히 빗나갔습니다... ({guard} 공격 모두 취소)\n\n"
                            missed_guards_this_turn.append(guard)

            if "리카르도" in selected_guards:
                actual_victims = [g for g in previous_missed_guards if g != "리카르도"]
                if actual_victims:
                    retaliation_bonus = 30 # 압도적인 보복 보너스
                    current_team_power += (base_power + retaliation_bonus)
                    
                    victims_str = ", ".join(actual_victims)
                    hour_log += f"> 🕶️ **[되갚기]** 리카르도가 이전 공방에서 {victims_str}이(가) 당한 수모를 앙갚음하기 위해 무자비한 맹공을 퍼붓습니다! ({retaliation_bonus})\n\n"
            
            if "가치우" in selected_guards: 
                current_team_power *= 1.2
                if hour == 1:
                    hour_log += "> 🍂 **[천강성의 가르침]** 옥기린의 지도를 통해, 아군 전체의 방어 점수가 1.2배 증폭됩니다.\n\n"

            if "에즈라" in selected_guards and "에즈라" not in missed_guards_this_turn:
                ezra_buff = random.randint(5, 25)
                current_team_power += ezra_buff
                hour_log += f"> 🦮 **[시제품 테스트]** 에즈라가 가방에서 미완성 장비를 뽑아듭니다. (+{ezra_buff})\n\n"
                if "검은침묵 안젤리카" in selected_guards and random.random() < 0.30:
                    extra_buff = random.randint(5, 25)
                    current_team_power += extra_buff
                    hour_log += f"> ⚔️ :blue[**[시너지 발동: 무기 진심녀]**] 안젤리카의 예리한 조언에 자극받은 에즈라가 무기를 한 번 더 전개합니다! (+{extra_buff})\n\n"

            # 발렌치나 기믹 처리
            if "엄지 아비 발렌치나" in selected_guards and hour % 3 == 0 and "엄지 아비 발렌치나" not in missed_guards_this_turn:
                current_team_power += 30
                hour_log += "> 🤺 **[팔레르모 검술]** 발렌치나가 예비 탄환을 쏟아부어 화력을 집중합니다. (이번 시간 방어선 +30)\n\n"
                
            if is_angelica_alive and "검은침묵 안젤리카" not in missed_guards_this_turn: 
                angelica_buff = random.randint(5, 45)
                current_team_power += angelica_buff
                hour_log += f"> 🧤 **[차원장갑]** 검은침묵 안젤리카가 무작위 공방 무기를 전개합니다. (추가 방어 점수 +{angelica_buff})\n\n"

            # 칼리 기본 공격력 결정
            if hour <= 12:
                kali_max_roll = 10 if "니콜라이" in selected_guards else 20
                kali_base = 50 + (hour * 5) 
                kali_roll = random.randint(kali_base - 10, kali_base + kali_max_roll)

            else:
                kali_max_roll = 15 if "니콜라이" in selected_guards else 40
                kali_base = 100 + ((hour - 12) * 20) 
                kali_roll = random.randint(kali_base - 15, kali_base + kali_max_roll)
                if hour == 21:
                    if "처형자 바랄" in selected_guards:
                        kali_roll = 0
                    else:
                        kali_roll = 300
            
            # 다수의 적을 상대할 때 칼리의 투지 상승
            crowd_bonus = len(selected_guards) * 15
            kali_roll += crowd_bonus
            
            if hour == 1 and len(selected_guards) >= 3:
                hour_log += f"> 🔴 **[붉은안개의 투지]** 적이 많을수록 칼리의 참격이 더욱 거세집니다. (매 턴 위력 +{crowd_bonus})\n\n"

            # 디버프 적용 계산 (화상, 베스파, 롤랑 등)
            burn_debuff = (2 if "뇌횡" in selected_guards else 0) + (3 if "샤오" in selected_guards else 0) + (3 if "붉은시선 베르길리우스" in selected_guards else 0) + (2 + thumb_burn_bonus if "엄지 아비 발렌치나" in selected_guards else 0)
            current_burn_penalty = burn_debuff * ((hour + t_gear_triggers) // 2)
            temp_debuff = current_burn_penalty + kali_perm_debuff
            
            if current_burn_penalty > 0:
                hour_log += f"> 🔥 **[화상 누적]** 타오르는 불꽃이 칼리의 육체를 갉아먹어 위력을 {current_burn_penalty}만큼 깎아냅니다.\n\n"
            
            if "노란작살 베스파" in selected_guards and hour % 3 == 0 and "노란작살 베스파" not in missed_guards_this_turn: 
                # 기본 30 + 지난 격차의 20% 보너스
                tactical_bonus = int(last_hour_gap * 0.2)
                temp_debuff += (30 + tactical_bonus)
                hour_log += f"> 🐝 **[궁니르 공명]** 베스파가 칼리의 공격 궤적에서 찾아낸 허점을 놓치지 않고 찌릅니다. (칼리의 위력 -30 / 전술 보너스 -{tactical_bonus})\n\n"
            
            # 롤랑 기믹 처리
            if "롤랑" in selected_guards:
                if is_roland_berserk:
                    current_team_power += 9999 
                    kali_perm_debuff += 25 
                    
                    hour_log += "> ⬛ **[광란]** 롤랑이 당신의 앞을 가로막고 붉은안개와 단독 혈투를 벌입니다! (플레이어 무적 / 칼리 위력 지속적으로 -25)\n\n"
                    if random.random() < 0.30:
                        selected_guards.remove("롤랑")
                        hour_log += "> 🥀 **[그 사람은 그렇게...]** 롤랑이 피를 토하며 허망한 얼굴로 쓰러집니다...\n\n"
                    else:
                        hour_log += "\n"
                        
                else:
                    # --- (B) 일반 상태: 전술적 복기 적용 ---
                    if hour % 6 == 0 and "롤랑" not in missed_guards_this_turn:
                        base_tactical_bonus = int(last_hour_gap * 0.4)
                        if "검은침묵 안젤리카" in selected_guards:
                            boosted_bonus = int(base_tactical_bonus * 1.2)
                            temp_debuff += (50 + boosted_bonus)
                            hour_log += f"> ⬛ **[검은침묵의 왈츠]** 롤랑 부부가 지난 공방의 빈틈을 완벽히 분석했습니다. (칼리의 위력 -50 / 전술 보너스 -{boosted_bonus})\n\n"
                        else:
                            temp_debuff += (50 + base_tactical_bonus)
                            
                            hour_log += f"> ⬛ **[뒤랑달]** 롤랑이 홀로 칼리의 흐트러진 자세를 파고들어 맹공을 퍼붓습니다. (칼리의 위력 -50 / 전술 보너스 -{base_tactical_bonus})\n\n"
            
            if "니콜라이" in selected_guards and "니콜라이" not in missed_guards_this_turn:
                hour_log += "> 🎯 **[위력 억제]** 니콜라이의 지휘로 칼리의 위력 최댓값이 억제되고 있습니다.\n\n"

            # 칼리 최종 공격력 산출
            effective_kali_attack = int((kali_roll - temp_debuff) * aggro_multiplier)
            if effective_kali_attack < 0: effective_kali_attack = 0

            # 모제스의 연기 디버프 (최종 위력 10% 감소)
            if "모제스" in selected_guards and hour % 2 == 0 and "모제스" not in missed_guards_this_turn:
                reduction = int(effective_kali_attack * 0.1)
                effective_kali_attack -= reduction
                hour_log += f"> 💨 **[곰방대의 연기]** 모제스가 연기를 뿜어 칼리의 공격 궤적을 흐트러뜨립니다. (감소된 위력: {reduction})\n\n"

            # 뤼엔의 지령 회피 (15% 확률로 위력 0)
            if "검지 아비 뤼엔" in selected_guards and random.random() < 0.15 and "검지 아비 뤼엔" not in missed_guards_this_turn:
                effective_kali_attack = 0
                hour_log += "> 📜 **[지령 수행]** 뤼엔이 헤르메스의 의지로 칼리의 공격을 완전히 간파해냅니다. (칼리의 위력 무효화)\n\n"

            if effective_kali_attack < 0: effective_kali_attack = 0


            # 최종 방어 판정
            if "푸른잔향 아르갈리아" in selected_guards and abs(effective_kali_attack - current_team_power) <= 10 and "푸른잔향 아르갈리아" not in missed_guards_this_turn:
                persistent_power_bonus += 20
                hour_log += "> 🎼 **[아르갈리아의 공명]** 칼리의 궤적과 아슬아슬하게 합을 맞추며 영구적인 흐름을 가져옵니다. (영구 방어선 +20)\n\n"
                
                # 만약 방어선이 뚫릴 뻔했다면, 강제로 방어 점수를 끌어올려 세이브
                if current_team_power < effective_kali_attack:
                    current_team_power = effective_kali_attack
            
            time.sleep(0.3)
            if current_team_power >= effective_kali_attack:
                if "바퀴 황제" in selected_guards: 
                    # 13시간 이전에는 +4, E.G.O 발현 이후에는 +8로 성장폭 대폭 증가
                    emp_bonus = 6 if hour >= 13 else 4
                    persistent_power_bonus += emp_bonus
                    hour_log += f"> 🪳 **[황제의 피]** 바퀴 황제가 칼리의 참격을 버텨내며 외골격을 단단하게 진화시킵니다. (영구 방어선 +{emp_bonus})\n\n"
                if "핏빛 밤 엘레나" in selected_guards: 
                    persistent_power_bonus += 2
                    hour_log += "> 🧛‍♀️ **[퍼져나가는 혈액]** 핏빛 밤 엘레나가 흩뿌려진 피를 흡수하여 방어선을 복구합니다. (영구 방어선 +2)\n\n"
                if has_t_gear and random.random() < 0.25:
                    t_gear_triggers += 1
                    hour_log += "> ⚙️ :orange[**[시간 가속]**] T사 보조 태엽이 회전하며 시간이 가속됩니다! (턴 종료 효과 2배 적용)\n\n"
                    
                    if "바퀴 황제" in selected_guards: 
                        emp_bonus = 6 if hour >= 13 else 4 # 여기서 다시 계산
                        persistent_power_bonus += emp_bonus
                        hour_log += f"> 🪳 **[황제의 피 - 가속]** 황제의 외골격이 한 번 더 진화합니다! (영구 방어선 +{emp_bonus})\n\n"
                        
                    if "핏빛 밤 엘레나" in selected_guards: 
                        persistent_power_bonus += 2
                        hour_log += "> 🧛‍♀️ **[퍼져나가는 혈액 - 가속]** 엘레나가 피를 추가로 흡수합니다! (영구 방어선 +2)\n\n"
                hour_log += f"> 🛡️ **[방어 성공]** (칼리의 위력: {effective_kali_attack} / 호위 방어선: {int(current_team_power)})\n\n"
            else:
                # 0순위 생존기: 롤랑 부부 전용 기믹 (마티아스와 겹칠 일은 예산상 없지만 최상단에 배치)
                if "롤랑" in selected_guards and "검은침묵 안젤리카" in selected_guards:
                    selected_guards.remove("검은침묵 안젤리카")
                    is_angelica_alive = False
                    is_roland_berserk = True
                    hour_log += "> 🪦 **[안젤리카의 희생]** 붉은안개의 대검이 당신과 롤랑을 가르려는 찰나, 안젤리카가 뛰어들어 대신 참격을 받아냅니다!\n\n"
                    hour_log += "> 💔 **[롤랑의 절규]** 아내를 지키지 못한 롤랑의 눈빛에 섬뜩한 광기가 차오릅니다...\n\n"
                # 1순위 생존기: 마티아스의 강제 희생
                elif "중지 아비 마티아스" in selected_guards and len(selected_guards) > 1:
                    # 조건이 만족되었을 때(elif 안쪽) 비로소 명단을 작성합니다.
                    available_sacrifices = [g for g in selected_guards if g != "중지 아비 마티아스"]
                    sacrifice = random.choice(available_sacrifices)
                    selected_guards.remove(sacrifice)
                    if sacrifice == "검은침묵 안젤리카":
                        is_angelica_alive = False
                    sacrifice_power = guards_db[sacrifice]["power"]
                    debuff_amount = int(sacrifice_power * 0.5)
                    kali_perm_debuff += debuff_amount
                    
                    hour_log += f"> ⛓️ **[마티아스의 변덕]** 방어선이 무너지자, 마티아스가 충동적으로 곁에 있던 **{sacrifice}**를 붉은안개의 참격 앞으로 밀쳐냅니다.\n\n"
                    hour_log += f"> 😵 **[희생양 즉사 / 붉은안개의 영구 위력 {debuff_amount} 감소 / 이번 턴 강제 생존]**\n\n"
                elif blood_gauge >= 50:
                    blood_gauge -= 50
                    hour_log += f"> 🩸 **[돈키호테류 경혈식 방패]** 혈액을 소모하여 버텼습니다. (남은 혈액: {blood_gauge})\n\n"
                elif baral_w_serum > 0:
                    baral_w_serum -= 1
                    hour_log += f"> 💉 **[처형자의 기지]** 혈청 W를 투여해 공간을 격리했습니다. (남은 회피: {baral_w_serum})\n\n"
                elif "가치우" in selected_guards and not gachiu_shield_used:
                    gachiu_shield_used = True
                    hour_log += f"> 🍂 **[가치우의 인협]** 가치우가 당신을 밀쳐내고 붉은안개의 맹공을 홀로 받아냈습니다!\n\n"
                elif has_t_badge:
                    has_t_badge = False
                    kali_perm_debuff += 30  # 시간 역행으로 칼리의 위력 스노우볼을 깎아버림
                    hour_log += f"> ⏱️ :orange[**[시간 역행]**] 방어선이 붕괴된 순간, 배지를 부수어 붉은안개가 기세를 올리기 전으로 시간을 되감습니다!\n\n"
                    hour_log += f"> ⚠️ **(강제 생존 / 붉은안개의 위력이 영구적으로 30 감소)**\n\n"
                elif revives_left > 0:
                    revives_left -= 1
                    if is_angelica_alive and random.random() < 0.5: is_angelica_alive = False
                    hour_log += f"> 🧪 :orange[**[앰플 투여]**] 치명상을 입었으나, K사 앰플의 효과로 육체가 즉시 수복됩니다. (남은 앰플: {revives_left})\n\n"
                else:
                    hour_log += f"> 💀 **[방어 수단 없음]** 붉은안개의 미미크리가 당신을 갈랐습니다.\n\n"
                    battle_logs += hour_log
                    log_container.markdown(battle_logs)
                    survival_status = False
                    break
            
            # 시간 경과 후처리 기믹
            raw_gap = abs(effective_kali_attack - current_team_power)
            last_hour_gap = min(300, raw_gap) 
            if current_team_power > effective_kali_attack and raw_gap >= 50:
                if current_team_power >= 9000:
                    carried_shield = 0
                else:
                    carried_shield = int(raw_gap * 0.3) # 초과분의 30%를 다음 턴으로 이월
            else:
                carried_shield = 0
            
            battle_logs += hour_log
            log_container.markdown(battle_logs)
            time.sleep(0.3)


        # 결과 출력
        st.write("---")
        if survival_status:
            st.success(f"🎉 **미션 성공!** {target_hours}시간 동안 붉은안개로부터 살아남았습니다. 칼리가 빠르게 당신의 시야 너머로 사라집니다.")
        else:
            st.error("❌ **미션 실패!** 호위들은 전멸했고, 당신의 기록은 여기서 끊어졌습니다.")

        st.write("---")
        
        final_report = f"#### 🛡️ 고용한 호위 및 장비\n> 호위: {', '.join(initial_guards)}\n> 장비: {', '.join(initial_items)}\n\n"
        final_report += battle_logs

        clean_report = re.sub(r':[a-zA-Z]+\[(.*?)\]', r'\1', final_report)
        clean_report = clean_report.replace('**', '')
        clean_report = clean_report.replace('\n\n>', '\n>')

        # 2. 클릭 한 번으로 복사할 수 있도록 원문 코드를 숨겨두는 구역 (보관용)
        with st.expander("📋 기록 원문 복사하기"):
            st.code(clean_report, language="text")
