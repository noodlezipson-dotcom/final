import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

# 页面配置
st.set_page_config(
    page_title="Movie Quote Finder & Analyzer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .quote-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .movie-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        transition: transform 0.3s;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    .character-badge {
        background-color: #4a90e2;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .sentiment-positive {
        color: #2ecc71;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #e74c3c;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #f39c12;
        font-weight: bold;
    }
    .highlight {
        background-color: #fff3cd;
        padding: 2px 5px;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'favorite_quotes' not in st.session_state:
    st.session_state.favorite_quotes = []

def main():
    # 应用标题
    st.markdown('<div class="main-header">🎬 Movie Quote Finder & Analyzer</div>', unsafe_allow_html=True)
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search Quotes", "📊 Analysis", "⭐ Favorites", "ℹ️ About"])
    
    with tab1:
        display_search_tab()
    
    with tab2:
        display_analysis_tab()
    
    with tab3:
        display_favorites_tab()
    
    with tab4:
        display_about_tab()

def display_search_tab():
    """显示搜索标签页"""
    st.subheader("Find Movie Quotes")
    
    # 搜索区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "Search for quotes, movies, or characters:",
            placeholder="e.g., 'You talking to me?' or 'The Godfather' or 'Tony Montana'",
            key="search_input"
        )
    
    with col2:
        search_type = st.selectbox(
            "Search in:",
            ["All Fields", "Quotes Only", "Movie Titles", "Characters"],
            key="search_type"
        )
    
    # 高级筛选
    with st.expander("🔧 Advanced Filters"):
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            year_from = st.number_input("From Year", min_value=1900, max_value=2024, value=1950)
        
        with filter_col2:
            year_to = st.number_input("To Year", min_value=1900, max_value=2024, value=2024)
        
        with filter_col3:
            sentiment_filter = st.selectbox(
                "Sentiment:",
                ["All", "Positive", "Negative", "Neutral"]
            )
    
    # 搜索按钮
    if st.button("🔍 Search Quotes", type="primary", use_container_width=True):
        if search_query:
            search_quotes(search_query, search_type, year_from, year_to, sentiment_filter)
        else:
            st.info("Please enter a search query to find movie quotes.")
    
    # 热门搜索建议
    st.markdown("### Popular Searches:")
    popular_cols = st.columns(5)
    popular_searches = [
        "Love quotes", "Famous monologues", "Scarface", 
        "The Dark Knight", "Forrest Gump"
    ]
    
    for idx, search in enumerate(popular_searches):
        with popular_cols[idx]:
            if st.button(search, use_container_width=True):
                st.session_state.search_input = search
                st.rerun()

def search_quotes(query, search_type, year_from, year_to, sentiment):
    """搜索电影台词"""
    # 加载数据
    quotes_df = load_movie_quotes()
    
    if quotes_df.empty:
        st.warning("No movie quotes database found. Please check data files.")
        return
    
    # 根据搜索类型过滤
    filtered_df = quotes_df.copy()
    
    # 年份过滤
    filtered_df = filtered_df[
        (filtered_df['year'] >= year_from) & 
        (filtered_df['year'] <= year_to)
    ]
    
    # 情感过滤
    if sentiment != "All":
        filtered_df = filtered_df[filtered_df['sentiment'] == sentiment.lower()]
    
    # 关键词搜索
    if query:
        if search_type == "All Fields":
            mask = (
                filtered_df['quote'].str.contains(query, case=False, na=False) |
                filtered_df['movie_title'].str.contains(query, case=False, na=False) |
                filtered_df['character'].str.contains(query, case=False, na=False)
            )
        elif search_type == "Quotes Only":
            mask = filtered_df['quote'].str.contains(query, case=False, na=False)
        elif search_type == "Movie Titles":
            mask = filtered_df['movie_title'].str.contains(query, case=False, na=False)
        elif search_type == "Characters":
            mask = filtered_df['character'].str.contains(query, case=False, na=False)
        
        filtered_df = filtered_df[mask]
    
    # 显示结果
    if len(filtered_df) > 0:
        st.success(f"Found {len(filtered_df)} quotes matching your search")
        
        # 添加到搜索历史
        st.session_state.search_history.append({
            "query": query,
            "type": search_type,
            "results": len(filtered_df),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # 显示结果
        for idx, row in filtered_df.iterrows():
            display_quote_card(row, idx)
    else:
        st.warning("No quotes found matching your criteria.")

def display_quote_card(quote_data, index):
    """显示单个台词卡片"""
    with st.container():
        st.markdown(f"""
        <div class="quote-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h4 style="margin: 0; color: #2c3e50;">"{quote_data['quote']}"</h4>
                </div>
                <div>
                    <span class="character-badge">{quote_data['character']}</span>
                </div>
            </div>
            
            <div style="margin-top: 1rem; color: #555;">
                <strong>🎬 Movie:</strong> {quote_data['movie_title']} ({quote_data['year']})<br>
                <strong>🎭 Scene:</strong> {quote_data['scene_description']}<br>
                <strong>📊 Sentiment:</strong> <span class="sentiment-{quote_data['sentiment']}">{quote_data['sentiment'].title()}</span>
            </div>
            
            <div style="margin-top: 1rem;">
                <strong>🏷️ Tags:</strong> {', '.join(quote_data['tags'].split(','))}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 操作按钮
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("⭐ Favorite", key=f"fav_{index}"):
                add_to_favorites(quote_data)
                st.success("Added to favorites!")
        
        with col2:
            if st.button("🔍 Context", key=f"context_{index}"):
                show_quote_context(quote_data)
        
        with col3:
            st.write(f"**Length:** {len(quote_data['quote'])} characters")
        
        st.markdown("---")

def display_analysis_tab():
    """显示分析标签页"""
    st.subheader("Movie Quotes Analysis")
    
    # 加载数据
    quotes_df = load_movie_quotes()
    
    if quotes_df.empty:
        st.warning("No data available for analysis.")
        return
    
    # 分析选项
    analysis_type = st.selectbox(
        "Select Analysis Type:",
        ["Sentiment Distribution", "Most Quoted Characters", "Quotes by Year", "Word Cloud Analysis"]
    )
    
    if analysis_type == "Sentiment Distribution":
        # 情感分布饼图
        sentiment_counts = quotes_df['sentiment'].value_counts()
        
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Sentiment Distribution of Movie Quotes",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Most Quoted Characters":
        # 最常被引用的角色
        top_characters = quotes_df['character'].value_counts().head(10)
        
        fig = px.bar(
            x=top_characters.values,
            y=top_characters.index,
            orientation='h',
            title="Top 10 Most Quoted Characters",
            labels={'x': 'Number of Quotes', 'y': 'Character'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Quotes by Year":
        # 按年份的台词数量
        quotes_by_year = quotes_df.groupby('year').size().reset_index(name='count')
        
        fig = px.line(
            quotes_by_year,
            x='year',
            y='count',
            title="Movie Quotes Trend by Year",
            markers=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Word Cloud Analysis":
        # 词频分析
        all_quotes = ' '.join(quotes_df['quote'].tolist())
        words = re.findall(r'\b\w+\b', all_quotes.lower())
        
        # 移除停用词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        word_freq = Counter(filtered_words).most_common(20)
        
        words_df = pd.DataFrame(word_freq, columns=['Word', 'Frequency'])
        
        fig = px.bar(
            words_df,
            x='Frequency',
            y='Word',
            orientation='h',
            title="Top 20 Most Common Words in Movie Quotes",
            color='Frequency'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 统计信息
    st.subheader("Database Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Quotes", len(quotes_df))
    
    with col2:
        st.metric("Unique Movies", quotes_df['movie_title'].nunique())
    
    with col3:
        st.metric("Unique Characters", quotes_df['character'].nunique())
    
    with col4:
        st.metric("Average Quote Length", f"{quotes_df['quote'].str.len().mean():.0f} chars")

def display_favorites_tab():
    """显示收藏标签页"""
    st.subheader("⭐ Favorite Quotes")
    
    if not st.session_state.favorite_quotes:
        st.info("You haven't added any quotes to favorites yet.")
        return
    
    # 显示收藏的台词
    for idx, quote in enumerate(st.session_state.favorite_quotes):
        with st.container():
            st.markdown(f"""
            <div class="movie-card">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <h4 style="margin: 0;">"{quote['quote'][:100]}..."</h4>
                        <p style="margin: 0.5rem 0; color: #666;">
                            <strong>{quote['character']}</strong> in <em>{quote['movie_title']}</em>
                        </p>
                    </div>
                    <div>
                        {st.button("🗑️", key=f"remove_{idx}", help="Remove from favorites")}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_about_tab():
    """显示关于标签页"""
    st.subheader("About Movie Quote Finder")
    
    st.markdown("""
    ### 🎬 What is Movie Quote Finder?
    
    Movie Quote Finder is an interactive web application that allows you to:
    
    - 🔍 **Search** through thousands of famous movie quotes
    - 🎭 **Analyze** quotes by sentiment, character, and year
    - 📊 **Visualize** trends and patterns in cinematic dialogue
    - ⭐ **Save** your favorite quotes for later reference
    
    ### 📚 How It Works
    
    1. **Search**: Enter keywords, movie titles, or character names
    2. **Filter**: Use advanced filters to narrow down results
    3. **Analyze**: Explore visualizations and statistics
    4. **Save**: Create your personal collection of favorite quotes
    
    ### 🛠️ Technical Details
    
    - **Built with**: Streamlit, Python, Plotly, Pandas
    - **Data Source**: Curated movie quotes database
    - **Features**: Real-time search, sentiment analysis, data visualization
    - **Deployment**: Ready for Streamlit Cloud deployment
    
    ### 📊 Database Information
    
    The application includes quotes from:
    - Classic films (1950s-1990s)
    - Modern cinema (2000s-present)
    - Various genres and languages
    - Iconic characters and memorable scenes
    
    ### 🎓 Educational Purpose
    
    This project was developed as part of the "Arts and Advanced Big Data" course, 
    demonstrating how data science techniques can be applied to creative fields.
    
    ### 👨‍🏫 Instructor
    
    **Prof. Jahwan Koo**  
    Sungkyunkwan University (SKKU)
    """)
    
    # 版本信息
    st.markdown("---")
    st.markdown("**Version:** 1.0.0 | **Last Updated:** November 2024")

def load_movie_quotes():
    """加载电影台词数据"""
    try:
        # 示例数据 - 实际应用中应该从文件加载
        sample_data = {
            'movie_title': ['The Godfather', 'The Dark Knight', 'Forrest Gump', 'Scarface', 'Titanic'],
            'character': ['Michael Corleone', 'Joker', 'Forrest Gump', 'Tony Montana', 'Jack Dawson'],
            'quote': [
                "I'm going to make him an offer he can't refuse.",
                "Why so serious?",
                "Life is like a box of chocolates. You never know what you're gonna get.",
                "Say hello to my little friend!",
                "I'm the king of the world!"
            ],
            'year': [1972, 2008, 1994, 1983, 1997],
            'sentiment': ['neutral', 'negative', 'positive', 'negative', 'positive'],
            'scene_description': [
                'Business negotiation scene',
                'Hospital scene with Harvey Dent',
                'Bench conversation',
                'Final showdown',
                'Ship bow scene'
            ],
            'tags': ['mafia,power,negotiation', 'chaos,violence,philosophy', 'life,wisdom,innocence', 'violence,drugs,power', 'love,freedom,ocean']
        }
        
        return pd.DataFrame(sample_data)
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def add_to_favorites(quote_data):
    """添加台词到收藏"""
    if quote_data not in st.session_state.favorite_quotes:
        st.session_state.favorite_quotes.append(quote_data)

def show_quote_context(quote_data):
    """显示台词上下文"""
    st.info(f"**Context for:** {quote_data['movie_title']}")
    st.write(f"**Character:** {quote_data['character']}")
    st.write(f"**Scene:** {quote_data['scene_description']}")
    st.write(f"**Full Quote:** {quote_data['quote']}")

if __name__ == "__main__":
    main()
