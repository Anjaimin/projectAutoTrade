import streamlit as st
import base64


def show_portfolio():
    # 프로젝트 설명 부분
    st.markdown(
        """
        <style>
            .project-description {
                font-size: 18px; 
                line-height: 1.6; 
                margin-bottom: 40px;
                border: 2px solid #e6e6e6; 
                padding: 15px; 
                border-radius: 5px; 
            }
            .section-title {
                font-size: 22px; 
                font-weight: bold;
                margin-top: 40px;
                padding: 10px; 
                border-radius: 5px;
            }
            .grid-container {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                justify-items: center;
                margin-bottom: 40px;
                border: 2px solid #e6e6e6; 
                padding: 15px; 
                border-radius: 5px;
            }
            .grid-item {
                text-align: center;
                padding: 10px; 
                
            }
            .grid-item img {
                width: 120px;
                margin-top: 10px;
            }
            .flowchart-container {
                text-align: center;
                margin-top: 10px;
                border: 2px solid #e6e6e6;
                padding: 15px; 
                border-radius: 5px; 
            }
            .flowchart-container img {
                width: 80%;
                margin-top: 20px;
            }
                      .program-intro {
                font-size: 18px; 
                line-height: 1.6; 
                margin-bottom: 40px;
                border: 2px solid #e6e6e6; 
                padding: 15px; 
                border-radius: 5px; 
                text-align: center;
            }
            .program-intro img {
                width: 80%;
                margin-top: 20px;
            }
            
        </style>
        <div class="section-title">프로젝트 소개</div>
        <div class="project-description">
            <p>제가 만든 국내주식 자동매매 시스템은 키움증권 API와 연동하여 실시간으로 국내 주식 데이터를 받으며 설정된 전략에 따라 자동으로 매매를 실행합니다.</p>
            <p>모든 거래 내역은 데이터베이스에 저장되며, Slack 메신저를 통해 실시간 매매 결과를 확인할 수 있습니다.</p>
            <p>웹페이지를 통해 자동매매 결과를 시각화하여 투자 성과를 확인할 수 있습니다.</p>
        </div>

        <div class="section-title">프로젝트 환경</div>
        """,
        unsafe_allow_html=True
    )

    # Base64로 이미지를 인코딩하는 함수
    def get_image_as_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    image_dir = "C:/Users/ajm31/Desktop/소스코드_및_교안_(5장)/images/"
    image_kiwoom = f"{image_dir}kiwoom.jpg"
    image_python = f"{image_dir}python.png"
    image_aws = f"{image_dir}aws2.png"
    image_mysql = f"{image_dir}mysql.png"
    image_github = f"{image_dir}github.png"
    image_slack = f"{image_dir}slack.png"
    image_flowchart = f"{image_dir}flowchart.png"
    image_sample4 = f"{image_dir}sample4.png"
    image_streamlit = f"{image_dir}streamlit.png"


    # 이미지를 Base64로 인코딩
    image_base64_kiwoom = get_image_as_base64(image_kiwoom)
    image_base64_python = get_image_as_base64(image_python)
    image_base64_aws = get_image_as_base64(image_aws)
    image_base64_mysql = get_image_as_base64(image_mysql)
    image_base64_github = get_image_as_base64(image_github)
    image_base64_slack = get_image_as_base64(image_slack)
    image_base64_flowchart = get_image_as_base64(image_flowchart)
    image_base64_sample4 = get_image_as_base64(image_sample4)
    image_base64_streamlit = get_image_as_base64(image_streamlit)

    # HTML과 CSS로 이미지와 텍스트를 그리드 형태로 배치
    st.markdown(
        f"""
        <div class="grid-container">
            <div class="grid-item">
                <p>키움 OPEN API+</p>
                <img src="data:image/jpeg;base64,{image_base64_kiwoom}" alt="Kiwoom API">
            </div>
            <div class="grid-item">
                <p>사용 언어 : Python-3.10(32bit/64bit)</p>
                <img src="data:image/jpeg;base64,{image_base64_python}" alt="Python">
            </div>
            <div class="grid-item">
                <p>배포 : AWS EC2</p>
                <img src="data:image/jpeg;base64,{image_base64_aws}" alt="AWS">
            </div>
            <div class="grid-item">
                <p>웹페이지 : streamlit</p>
                <img src="data:image/jpeg;base64,{image_base64_streamlit}" alt="streamlit">
            </div>
            <div class="grid-item">
                <p>데이터베이스 : MySQL</p>
                <img src="data:image/jpeg;base64,{image_base64_mysql}" alt="MySQL">
            </div>
            <div class="grid-item">
                <p>버전 관리 : Github</p>
                <img src="data:image/jpeg;base64,{image_base64_github}" alt="Github">
            </div>
            <div class="grid-item">
                <p>기타 : Slack</p>
                <img src="data:image/jpeg;base64,{image_base64_slack}" alt="Slack">
            </div>
        </div>

        <div class="section-title">Flow Chart</div>
        <div class="flowchart-container">
            <img src="data:image/png;base64,{image_base64_flowchart}" alt="Flow Chart">
        </div>
        
         <!-- 자동매매 프로그램 소개 섹션 추가 -->
       <div class="section-title">자동매매 프로그램 소개</div>
       <p>키움증권 Open API와 연동하여 관심 종목 코드와 변동성 계수(K-Value)를 입력하면 실시간으로 주식 현재가 데이터를 받아서 표출합니다.</p> 
       <p>목표 가격이 되면 매수 및 매도 주문을 하고 로그는 DB에 저장되며 Slack 메신저로 알람을 보냅니다.</p>
       
        
        <div class="program-intro">
            <img src="data:image/png;base64,{image_base64_sample4}" alt="Automated Trading Program">
        </div>
        
        
        """,
        unsafe_allow_html=True
    )