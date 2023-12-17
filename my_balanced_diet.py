import streamlit as st
import pandas as pd
import json
import requests
import matplotlib.pyplot as plt

from streamlit_option_menu import option_menu

st.set_page_config(
    page_icon="😲",
    page_title="My Balanced Diet",
    layout="wide",
)

with st.sidebar:
    choice_menu = option_menu("My balanced diet", ['Recent', 'School', 'Balance'],
                              icons=['bi bi-calendar-check', 'bi bi-segmented-nav', 'bi bi-diagram-3-fill'],
                              menu_icon="bi bi-clipboard-data", default_index=0,
                              styles={
                                  "container": {"padding": "5!important", "background-color": "#fafafa"},
                                  "icon": {"color": "orange", "font-size": "25px"},
                                  "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                               "--hover-color": "#eee"},
                                  "nav-link-selected": {"background-color": "#02ab21"},
                              })

if choice_menu == 'Recent':
    # MentiMeter 결과 화면 바로가기 링크
    st.header("요즘 여러분이 먹은 음식은 무엇인가요? :fork_and_knife:") 

    # 응답하기 버튼 추가
    response_url = "https://www.menti.com/alja12kkhqzn"
    if st.button("MentiMeter 응답하기"):
     st.markdown(
        f'<a href="{response_url}" target="_blank" rel="noopener noreferrer">MentiMeter 응답 링크</a>',
        unsafe_allow_html=True
     )


    mentimeter_embed_code = """
    <div style='position: relative; padding-bottom: 56.25%; padding-top: 35px; height: 0; overflow: hidden;'>
        <iframe sandbox='allow-scripts allow-same-origin allow-presentation' allowfullscreen='true' allowtransparency='true' frameborder='0' 
                height='315' src='https://www.mentimeter.com/app/presentation/alpbwbshep6zd9qcjs2q2izv6eg6rpf4/embed' 
                style='position: absolute; top: 0; left: 0; width: 100%; height: 100%;' width='420'></iframe>
    </div>
    """
    st.markdown(mentimeter_embed_code, unsafe_allow_html=True)
    

    # 나머지 Recent 메뉴에 대한 코드 작성
    st.subheader(":fast_forward: :blue[최근 먹은 음식에 많이 들은 영양소는 무엇일까요?]")

if choice_menu == 'School':
    # School 메뉴에 해당하는 코드 블록
    st.header("학교 급식 메뉴:school:")

    # 사용자로부터 날짜 입력 받기
    selected_date = st.date_input("날짜를 선택하세요")

    # 입력된 날짜로 API 호출
    if selected_date:
        # 날짜를 원하는 형식으로 변환
        formatted_date = selected_date.strftime("%Y%m%d")

        school_data = pd.read_csv("학교정보.csv")
        code_list = list(school_data["표준학교코드"])

        url = "http://open.neis.go.kr/hub/mealServiceDietInfo"
        service_key = "01728ccfdd12426c969a9a8cec9865cc"

        meal_set = set()  # 중복 방지를 위한 set 사용
        for code in code_list[:6]:
            params = {
                'KEY': service_key,
                'Type': 'json',
                'pIndex': '1',
                'pSize': '100',
                'ATPT_OFCDC_SC_CODE': 'B10',
                'SD_SCHUL_CODE': 7130179,
                'MLSV_FROM_YMD': formatted_date,
                'MLSV_TO_YMD': formatted_date
            }
            response = requests.get(url, params=params, timeout=(10,30))

            # Print the status code and response text for debugging
            print("Status Code:", response.status_code)
            print("Response Text:", response.text)

            try:
                contents = response.json()
            except ValueError as e:
                # Print the exception for debugging
                print("JSON Decode Error:", e)
                contents = None

            if contents is not None:
                if list(contents.keys())[0] == "RESULT":
                    pass
                else:
                    con = pd.DataFrame(contents['mealServiceDietInfo'][1]['row'])

                    # DataFrame의 각 행을 반복
                    for index, row in con.iterrows():
                        ddish_nm = row["DDISH_NM"]
                        ntr_info = row["NTR_INFO"]

                        # 현재 항목이 이미 set에 있는지 확인한 후, 없다면 출력하고 set에 추가
                        if (ddish_nm, ntr_info) not in meal_set:
                            st.write("메뉴:", ddish_nm)
                            st.write("영양소:", ntr_info)
                            st.write("")

                            # 중복 방지를 위해 set에 항목 추가
                            meal_set.add((ddish_nm, ntr_info))

    st.header("단백질 권장 섭취량 알아보기 :muscle:")          
    excel_path = "protein RNI.xlsx"
    df = pd.read_excel(excel_path)

    # 사용자로부터 성별과 연령 입력 받기
    gender = st.radio("성별을 선택하세요", ["남자", "여자"])
    age = st.number_input("나이를 입력하세요 (만 75세 이상은 75로 입력)", min_value=1, max_value=75, value=1, step=1)

    filtered_data = df[(df["age"] == age) & (df["sex"] == gender)]

    if not filtered_data.empty:
      recommended_protein = filtered_data["RNI(protein,g/day)"].values[0]

      # 사용자로부터 실제 섭취량 입력 받기
      protein_intake = st.number_input("오늘 섭취한 단백질 양 (g)", min_value=0.0, step=0.1)

      # 권장 섭취량 대비 섭취한 양의 비율 계산
      percentage_intake = (protein_intake / recommended_protein) * 100
      remaining_amount = recommended_protein - protein_intake

     # 차트 데이터
      labels = ['intake_amount', 'remaining_amount']
      sizes = [percentage_intake, 100 - percentage_intake]
      colors = ['#FF9999', '#66B2FF']

      # 원 그래프 생성
      fig, ax = plt.subplots()
      ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
      ax.axis('equal')  

      # Streamlit에 그래프 표시
      st.pyplot(fig)
      st.write(f"섭취한 양: {protein_intake}g")
      st.write(f"남은 양: {remaining_amount}g")

    else:
      st.warning("선택한 나이와 성별에 대한 권장 섭취량 데이터가 없습니다.")


import streamlit as st
import pandas as pd

if choice_menu == 'Balance':
    st.header("나의 권장 식사 패턴에 맞는 식사 구성하기:eyes:")
    # Balance 메뉴에 해당하는 코드 블록

    # recommend_diet 엑셀 파일에서 데이터 읽기
    df_recommend_diet = pd.read_excel("recommend_diet.xlsx")

    # 사용자로부터 권장 식사 패턴의 타입 선택 받기
    pattern = st.radio("권장식사패턴을 선택하세요. (A는 만18세까지, B는 만19세부터)", ["A", "B"])
  
    # 사용자로부터 총 Kcal 입력 받기
    kcal = st.number_input("총 섭취할 Kcal을 입력하세요. (A는 900부터 2800, B는 1000부터 2700)", min_value=1000.0)

    recommended_counts = {}
    food_types = ['cereal', 'protein', 'vegetable', 'fruit', 'milk']
    
    # 패턴과 총 칼로리에 맞는 데이터 추출
    recommended_data = df_recommend_diet[(df_recommend_diet['pattern'] == pattern) & (df_recommend_diet['kcal'] <= kcal)]

    if not recommended_data.empty:
        # 추출된 데이터가 비어 있지 않은 경우 권장 섭취 횟수 계산
        for food_type in food_types:
            # pattern과 칼로리가 모두 일치하는 행 찾기
            matching_rows = recommended_data[(recommended_data['pattern'] == pattern) & (recommended_data['kcal'] == kcal)]

            if not matching_rows.empty:
                # 해당 행의 해당 식품군 횟수를 사용
                recommended_counts[food_type] = matching_rows[food_type].iloc[0]
            else:
                recommended_counts[food_type] = 0
    else:
        # 추출된 데이터가 비어 있는 경우 예외 처리
        st.warning("선택한 패턴과 총 칼로리에 맞는 데이터가 없습니다. 입력값을 다시 확인해주세요.")

    current_counts = {}
    for food_type in food_types:
        current_counts[food_type] = st.number_input(f"{food_type} 식품군의 현재 섭취 횟수를 입력하세요", min_value=0)

    # 남은 섭취 횟수 계산
    remaining_counts = {food_type: recommended_counts[food_type] - current_counts[food_type] for food_type in food_types}

    # 결과 출력 - 왼쪽 열
    col1, col2 = st.columns(2)

    # 왼쪽 열에 권장 섭취 횟수, 현재 섭취 횟수, 남은 섭취 횟수 표시
    with col1:
        st.subheader("계산 결과")
        result_df = pd.DataFrame({
            '식품군': food_types,
            '권장 섭취 횟수': list(recommended_counts.values()),
            '현재 섭취 횟수': list(current_counts.values()),
            '남은 섭취 횟수': list(remaining_counts.values())
        })
        st.table(result_df.style.format({
            '권장 섭취 횟수': '{:.1f}',
            '현재 섭취 횟수': '{:.1f}',
            '남은 섭취 횟수': '{:.1f}'
        }))

    # 오른쪽 열에 어떤 식사를 하면 좋을지 입력 받는 부분
    with col2:
        st.subheader(":fast_forward: :blue[어떤 식사를 할까?]")
        ingredients = st.text_input("재료를 입력하세요:")
        dish_name = st.text_input("음식명을 입력하세요:")

        if st.button('저장'):
            st.success('식단이 저장되었습니다!')









