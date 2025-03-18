import openai
import os
import random
import pyttsx3
import speech_recognition as sr
import subprocess  # ✅ TTS 실행을 위한 추가 모듈
from dotenv import load_dotenv
import re  # ✅ 정규식 사용

# ✅ 환경 변수 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ✅ OpenAI 클라이언트 생성
client = openai.Client(api_key=api_key)

# ✅ 마스터 키
MASTER_KEY = "우주최강 임수연"

# ✅ TTS 설정 (오프라인 음성 출력)
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)  # 음성 속도 조절

# ✅ STT 설정 (음성 인식)
recognizer = sr.Recognizer()

# ✅ GPT 기반 스토리 & 정답 단어 리스트 생성
def generate_story_and_code(level):
    word_count = 2 + level

    prompt = f"""
    너는 훌륭한 판타지 스토리텔러이자 게임 마스터야.
    플레이어는 '용감한 다람쥐 전사'이며, 현재 {level}단계의 도전을 진행 중이야.
    
    ✨ 아래 형식으로 응답해:
    
    이야기: "빛을 잃은 숲을 본 다람쥐는 어둠을 밝히기 위해 모험을 떠났다..."
    정답: ["빛", "숲", "모험"]

    
    ✨ 주의 사항:
    - 5~6줄의 짧고 완결성 있는 이야기를 작성해.
    - 스토리 속에서 자연스럽게 포함된 **{word_count}개의 키워드**를 정답 리스트에 추가해.
    - **"정답" 리스트에는 암호 단어만 포함하고, 스토리에 직접 노출되지 않도록 주의해!**
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=250
    )

    story = ""
    code_names = []
    lines = response.choices[0].message.content.strip().split("\n")
    for line in lines:
        if line.startswith("이야기:"):
            story = line.replace("이야기:", "").strip().strip('"')
        elif line.startswith("정답:"):
            code_names = eval(line.replace("정답:", "").strip())

    return story, code_names

# ✅ TTS (암호 음성 출력 - subprocess 사용)
def speak_text(text):
    """
    Streamlit 환경에서 TTS 실행 충돌을 방지하기 위해 subprocess 사용.
    """
    try:
        subprocess.run(["python", "-c", f"import pyttsx3; engine = pyttsx3.init(); engine.say('{text}'); engine.runAndWait()"])
    except Exception as e:
        print(f"TTS 오류 발생: {e}")

# ✅ STT (사용자 음성 입력)
def recognize_speech():
    """사용자가 음성을 입력하면 텍스트로 변환."""
    with sr.Microphone() as source:
        print("🎙️ 음성을 듣고 있습니다...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="ko-KR")
        return text.lower().strip()
    except sr.UnknownValueError:
        return "음성을 인식하지 못했습니다."
    except sr.RequestError:
        return "STT 서비스 오류 발생."

# ✅ 힌트 제공 함수
def provide_hint(code_names):
    return random.choice(code_names) if code_names else "🚨 오류: 암호가 추출되지 않았습니다!"

# ✅ 정답 확인 함수 (띄어쓰기 & 콤마 무시)
def check_answer(user_input, code_names):
    """사용자 입력과 정답 리스트 비교 (띄어쓰기, 콤마 무시)"""
    if user_input.strip() == MASTER_KEY:
        return True
    
    if not user_input:
        return False

    # ✅ 입력값에서 콤마와 띄어쓰기를 제거하고 단어만 추출
    user_words = set(re.findall(r'\b\w+\b', user_input.lower()))
    correct_words = set([word.lower() for word in code_names])

    return user_words == correct_words

# ✅ DALL·E를 활용한 AI 이미지 생성 함수
def generate_story_image(story):
    """현재까지의 스토리를 기반으로 AI가 이미지를 생성"""
    prompt = f"""
    아래 내용을 기반으로 멋진 판타지 일러스트를 생성해줘:
    
    "{story}"
    
    그림 스타일은 동화책 삽화처럼 따뜻하고 신비로운 분위기로 해줘.
    """
    
    response = client.images.generate(
        model="dall-e-3",  # ✅ 최신 DALL·E 모델 사용
        prompt=prompt,
        n=1,  # ✅ 이미지 1장 생성
        size="1024x1024"  # ✅ 정사각형 크기
    )
    
    return response.data[0].url  # ✅ 생성된 이미지 URL 반환

