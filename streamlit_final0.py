import mysql.connector
import pandas as pd
import streamlit as st
import plotly.express as px
import portfolio
import trade_data
import math

# 페이지 레이아웃 설정
st.set_page_config(layout="wide")


# Header 추가 함수
def add_header():
    st.markdown(
        """
        <style>
        .header-title {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .header-description {
            font-size: 18px;
            text-align: center;
            margin-bottom: 40px;
            color: #777777;
        }
        </style>
        <div class="header-title">국내주식 자동매매 대시보드</div>
        <div class="header-description"> 키움증권 API를 이용한 자동매매 시스템의 투자 현황과 성과를 직관적인 차트로 시각화합니다</div>
        """,
        unsafe_allow_html=True
    )

# Footer 추가 함수
def add_footer():
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #555555;
            z-index: 100;
        }
        </style>
        <div class="footer">
            국내주식 자동매매 및 투자 리포트 제공 — 키움증권 OPEN API+ 활용
        </div>
        """,
        unsafe_allow_html=True
    )

def load_data_from_db():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="test"
    )

    query = "SELECT * FROM trade_data"
    data = pd.read_sql(query, connection)
    connection.close()

    # 날짜 형식 변환
    if 'tradeDate' in data.columns:
        data['tradeDate'] = pd.to_datetime(data['tradeDate'], format='%Y-%m-%d')

    # 수익률 계산 (예시: (sellAmount - buyAmount) / buyAmount)
    data['returnRate'] = (data['sellAmount'] - data['buyAmount']) / data['buyAmount'] * 100
    data['returnRate'] = data['returnRate'].fillna(0)

    return data


def display_data_with_pagination(data, page_size=10):
    if not data.empty:
        # 총 페이지 수 계산
        total_pages = math.ceil(len(data) / page_size)

        # 현재 페이지를 세션 상태로 유지
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

        # 페이지 선택을 위한 셀렉트 박스를 우상단에 배치
        col1, col2 = st.columns([10, 1])  # 왼쪽 열: 데이터, 오른쪽 열: 페이지 선택
        with col2:
            page_selection = st.selectbox(
                '페이지 선택', list(range(1, total_pages + 1)),
                index=st.session_state.current_page - 1,
                key='page_select'
            )
            if page_selection != st.session_state.current_page:
                st.session_state.current_page = page_selection

        # 데이터프레임 표시
        start_idx = (st.session_state.current_page - 1) * page_size
        end_idx = start_idx + page_size
        st.write(f'총 {len(data)}개의 데이터 중 {start_idx + 1} ~ {min(end_idx, len(data))}번째 데이터 표시')
        st.dataframe(data.iloc[start_idx:end_idx])

    else:
        st.write("데이터가 없습니다.")


def calculate_pie_data(data):
    return data.groupby('stockName')['orderQuantity'].sum().reset_index()

def calculate_bar_data(data):
    return data.groupby('stockName')['orderPrice'].mean().reset_index()

def calculate_return_rate_comparison(data):
    return data.groupby('stockName')['returnRate'].mean().reset_index()

def calculate_daily_return_rate(data):
    return data.groupby(['tradeDate', 'stockName'])['returnRate'].mean().reset_index()

def calculate_portfolio_cumulative_return(data):
    data['cumulativeReturn'] = (data['returnRate'] / 100 + 1).cumprod() - 1
    return data.groupby('tradeDate')['cumulativeReturn'].sum().reset_index()

def calculate_portfolio_allocation(data):
    data['allocation'] = data['buyAmount'] - data['sellAmount']
    return data.groupby('stockName')['allocation'].sum().reset_index()

def main():
    # Header 추가
    add_header()

    # 사이드바에 내비게이션 메뉴 추가
    st.sidebar.title("목 록")
    menu_selection = st.sidebar.radio(" ", ["Home", "portfolio", "tradeData"])

    # 선택된 메뉴에 따라 다른 콘텐츠 표시
    if menu_selection == "Home":
        st.write('자동매매 현황')

        # DB에서 데이터 로드
        data = load_data_from_db()

        # 데이터를 페이징과 함께 표시
        display_data_with_pagination(data, page_size=10)

        pie_data = calculate_pie_data(data)
        bar_data = calculate_bar_data(data)
        return_rate_data = calculate_return_rate_comparison(data)
        daily_return_rate_data = calculate_daily_return_rate(data)
        cumulative_return_data = calculate_portfolio_cumulative_return(data)
        portfolio_allocation_data = calculate_portfolio_allocation(data)

        col1, col2 = st.columns(2)

        with col1:
            pie_chart = px.pie(
                pie_data, values='orderQuantity', names='stockName', title='종목별 매수수량 비율',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            pie_chart.update_traces(textinfo='percent+label')
            pie_chart.update_layout(title={'text': '종목별 매수수량 비율', 'x': 0.5, 'xanchor': 'center'})
            st.plotly_chart(pie_chart, use_container_width=True)

        with col2:
            bar_chart = px.bar(
                bar_data, x='stockName', y='orderPrice', title='종목별 평균 매수 가격',
                color='stockName', color_discrete_sequence=px.colors.qualitative.Set2
            )
            bar_chart.update_yaxes(title_text='평균 매수 가격 (원)', tickprefix='₩', separatethousands=True, tickformat=',')
            bar_chart.update_xaxes(title_text='종목명', tickformat=",")  # x축도 숫자 그대로 표시
            bar_chart.update_layout(title={'text': '종목별 평균 매수 가격', 'x': 0.5, 'xanchor': 'center'})
            st.plotly_chart(bar_chart, use_container_width=True)

        st.subheader('종목별 수익률 비교')
        if return_rate_data['returnRate'].sum() != 0:
            return_rate_chart = px.line(
                return_rate_data, x='stockName', y='returnRate', markers=True, title='종목별 수익률 비교',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            return_rate_chart.update_yaxes(title_text='수익률 (%)')
            return_rate_chart.update_xaxes(title_text='종목명', tickformat=",")  # x축도 숫자 그대로 표시
            return_rate_chart.update_layout(title={'text': '종목별 수익률 비교', 'x': 0.5, 'xanchor': 'center'})
            return_rate_chart.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(return_rate_chart, use_container_width=True)
        else:
            st.write("수익률 데이터가 없습니다.")

        st.subheader('날짜별 종목 수익률')
        if not daily_return_rate_data.empty:
            daily_return_rate_chart = px.line(
                daily_return_rate_data, x='tradeDate', y='returnRate', color='stockName',
                markers=True, title='날짜별 종목 수익률', color_discrete_sequence=px.colors.qualitative.D3
            )
            daily_return_rate_chart.update_yaxes(title_text='수익률 (%)')
            daily_return_rate_chart.update_xaxes(title_text='거래일자', tickformat="%Y-%m-%d")  # 날짜 형식 설정
            daily_return_rate_chart.update_layout(title={'text': '날짜별 종목 수익률', 'x': 0.5, 'xanchor': 'center'})
            daily_return_rate_chart.update_traces(line=dict(width=2), marker=dict(size=7))
            st.plotly_chart(daily_return_rate_chart, use_container_width=True)
        else:
            st.write("날짜별 수익률 데이터가 없습니다.")

        st.subheader('포트폴리오 누적 수익률')
        if not cumulative_return_data.empty:
            cumulative_return_chart = px.line(
                cumulative_return_data, x='tradeDate', y='cumulativeReturn',
                markers=True, title='포트폴리오 누적 수익률'
            )
            cumulative_return_chart.update_yaxes(title_text='누적 수익률 (%)')
            cumulative_return_chart.update_xaxes(title_text='거래일자', tickformat="%Y-%m-%d")  # 날짜 형식 설정
            cumulative_return_chart.update_layout(title={'text': '포트폴리오 누적 수익률', 'x': 0.5, 'xanchor': 'center'})
            cumulative_return_chart.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(cumulative_return_chart, use_container_width=True)
        else:
            st.write("누적 수익률 데이터가 없습니다.")

    elif menu_selection == "portfolio":
        portfolio.show_portfolio()

    elif menu_selection == "tradeData":
        trade_data.show_tradeData()

    # Footer 추가
    add_footer()

if __name__ == "__main__":
    main()
