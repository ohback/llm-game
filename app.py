import streamlit as st
import game  # ✅ 게임 로직 가져오기

st.set_page_config(page_title="🔒 단어 맞추기 게임 🔒", layout="wide")  # ✅ 전체 레이아웃 확장

# ✅ 화면 분할 (왼쪽: "사이드바처럼 보이는 영역", 오른쪽: "메인 게임 화면")
col1, spacer, col2 = st.columns([1, 0.2, 3])   # ✅ 왼쪽 1 : 오른쪽 3 비율로 화면 분할

# ✅ 📌 왼쪽 "고정 사이드바" (게임 설명, 목숨 & 힌트)
with col1:
    st.markdown("### &nbsp;")  # ✅ 오른쪽(col2)과 높이 맞추기 위해 공백 추가
    # ✅ 🎮 게임 설명 추가
    st.subheader("🎮 게임 설명")
    st.write("""
    당신은 숲을 구하기 위한 여정을 떠나는 다람쥐 전사입니다.  
    AI가 들려주는 단어를 기억한 뒤 **음성 또는 텍스트**로 정답을 입력하세요.  
    게임은 **3단계까지 진행**됩니다.
    """)

    # ✅ ❤️ 남은 목숨 표시 (제목 포함)
    st.subheader("💖 남은 목숨")
    lives_left = st.session_state.get("lives", 3)
    st.write("❤️ " * lives_left if lives_left > 0 else "💀 게임 오버")  # 목숨이 0이면 💀 표시

    # ✅ 힌트 버튼
    st.subheader("💡 힌트")
    if st.button("힌트 보기"):
        hint = game.provide_hint(st.session_state.get("code_names", []))
        st.warning(f"💡 힌트: {hint}")

# ✅ 📌 오른쪽 "게임 화면"
with col2:
    st.title("🔒 단어 맞추기 게임 🔒")

    # ✅ 세션 상태 초기화
    if "level" not in st.session_state:
        st.session_state["level"] = 1
    if "code_names" not in st.session_state:
        st.session_state["code_names"] = []
    if "story" not in st.session_state:
        st.session_state["story"] = ""
    if "story_history" not in st.session_state:
        st.session_state["story_history"] = []  # ✅ 이전 이야기 저장용 리스트
    if "lives" not in st.session_state:
        st.session_state["lives"] = 3
    if "attempts" not in st.session_state:
        st.session_state["attempts"] = 0
    if "user_input" not in st.session_state:
        st.session_state["user_input"] = ""
    if "recognized_text" not in st.session_state:
        st.session_state["recognized_text"] = ""  # ✅ 음성 인식 결과 저장 공간

    # ✅ **3단계를 초과하면 엔딩 출력**
    if st.session_state["level"] > 3:
        st.success("🎉 모든 단계를 통과했습니다! 해피엔딩이 공개됩니다!")

        # ✅ 모든 단계를 거친 스토리 출력
        st.subheader("🌿 최종 이야기 🌿")
        full_story = "\n\n".join(st.session_state["story_history"])
        st.write(full_story)

        # ✅ AI가 생성한 엔딩 이미지 추가
        with st.spinner("🖼️ AI가 엔딩 이미지를 생성 중..."):
            story_image_url = game.generate_story_image(full_story)  # ✅ AI 이미지 생성
            st.image(story_image_url, caption="🐿️ 다람쥐 전사 마을을 구하다 ⚔️", use_container_width=True)

        # ✅ 게임 리셋 버튼 추가
        if st.button("🔄 다시 시작하기"):
            st.session_state["level"] = 1
            st.session_state["code_names"] = []
            st.session_state["story"] = ""
            st.session_state["story_history"] = []
            st.session_state["lives"] = 3
            st.session_state["attempts"] = 0
            st.session_state["user_input"] = ""
            st.session_state["recognized_text"] = ""
            st.rerun()
        
        st.stop()


    # ✅ **스토리 & 정답을 한 번만 생성**
    if not st.session_state["story"] or not st.session_state["code_names"]:
        story, code_names = game.generate_story_and_code(st.session_state["level"])
        st.session_state["story"] = story
        st.session_state["code_names"] = code_names
        st.session_state["story_history"].append(story)  # ✅ 이전 스토리 저장

    # ✅ 게임 스토리 출력
    st.subheader(f"📖 {st.session_state['level']}단계 이야기")
    st.write(st.session_state["story"])

    # ✅ 암호 자동 음성 출력
    if st.button("🎙️ 암호 듣기"):
        game.speak_text(", ".join(st.session_state["code_names"]))

    # ✅ 입력 방식 선택
    input_method = st.radio("입력 방식을 선택하세요:", ["텍스트 입력", "음성 입력"])

    if input_method == "텍스트 입력":
        st.session_state["user_input"] = st.text_input("✍ 암호를 입력하세요:", value=st.session_state["user_input"])

    elif input_method == "음성 입력":
        if st.button("🎤 음성 입력"):
            recognized_text = game.recognize_speech()
            st.write(f"🎙️ 인식된 음성: {recognized_text}")
            if recognized_text:
                st.session_state["user_input"] = recognized_text
                st.session_state["recognized_text"] = recognized_text  # ✅ 음성 인식 결과 저장
                st.rerun()  # ✅ UI 즉시 업데이트

    # ✅ 음성 인식 결과 표시
    if st.session_state["recognized_text"]:
        st.write(f"🎙️ **인식된 음성:** {st.session_state['recognized_text']}")

    # ✅ 정답 확인 버튼
    if st.button("정답 확인") and st.session_state["user_input"]:
        # ✅ **마스터 키 확인 (즉시 클리어)**
        if st.session_state["user_input"].strip() == game.MASTER_KEY:
            st.success("🔑 마스터 키 입력 감지! 즉시 엔딩으로 이동합니다.")
            st.session_state["level"] = 4  # ✅ 강제 클리어 처리
            st.rerun()

        # ✅ 일반 정답 확인
        if game.check_answer(st.session_state["user_input"], st.session_state["code_names"]):
            st.success("🎉 정답입니다! 다음 단계로 이동합니다.")
            st.session_state["level"] += 1
            st.session_state["code_names"] = []
            st.session_state["story"] = ""  
            st.session_state["user_input"] = ""  # ✅ 사용자 입력 초기화
            st.session_state["recognized_text"] = ""  # ✅ 음성 인식 결과 초기화
            st.rerun()
        else:
            st.session_state["lives"] -= 1
            st.session_state["attempts"] += 1
            st.error(f"❌ 틀렸습니다! 남은 목숨: {st.session_state['lives']}")

            if st.session_state["lives"] == 0 or st.session_state["attempts"] >= 3:
                st.error("💀 게임 오버! 모든 목숨을 잃었습니다.")
                st.session_state["level"] = 1
                st.session_state["lives"] = 3
                st.session_state["attempts"] = 0
                st.session_state["story"] = ""
                st.session_state["code_names"] = []
                st.session_state["user_input"] = ""
                st.session_state["recognized_text"] = ""
                st.rerun()





