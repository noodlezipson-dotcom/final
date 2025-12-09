import streamlit as st
import pandas as pd
import plotly.express as px

# 页面配置
st.set_page_config(
    page_title="Movie Quote Finder",
    page_icon="🎬",
    layout="wide"
)

# 初始化数据
def init_data():
    """初始化电影台词数据"""
    movies = [
        {
            "title": "The Godfather",
            "year": 1972,
            "quote": "I'm going to make him an offer he can't refuse.",
            "character": "Michael Corleone",
            "sentiment": "neutral",
            "tags": "mafia, power, negotiation"
        },
        {
            "title": "The Dark Knight",
            "year": 2008,
            "quote": "Why so serious?",
            "character": "Joker",
            "sentiment": "negative",
            "tags": "chaos, violence, philosophy"
        },
        {
            "title": "Forrest Gump",
            "year": 1994,
            "quote": "Life is like a box of chocolates. You never know what you're gonna get.",
            "character": "Forrest Gump",
            "sentiment": "positive",
            "tags": "life, wisdom, innocence"
        },
        {
            "title": "Scarface",
            "year": 1983,
            "quote": "Say hello to my little friend!",
            "character": "Tony Montana",
            "sentiment": "negative",
            "tags": "violence, drugs, power"
        },
        {
            "title": "Titanic",
            "year": 1997,
            "quote": "I'm the king of the world!",
            "character": "Jack Dawson",
            "sentiment": "positive",
            "tags": "love, freedom, ocean"
        },
        {
            "title": "The Shawshank Redemption",
            "year": 1994,
            "quote": "Get busy living, or get busy dying.",
            "character": "Andy Dufresne",
            "sentiment": "positive",
            "tags": "hope, perseverance, freedom"
        },
        {
            "title": "Pulp Fiction",
            "year": 1994,
            "quote": "Say 'what' again! I dare you, I double dare you!",
            "character": "Jules Winnfield",
            "sentiment": "negative",
            "tags": "violence, humor, threat"
        },
        {
            "title": "Star Wars",
            "year": 1980,
            "quote": "I am your father.",
            "character": "Darth Vader",
            "sentiment": "negative",
            "tags": "family, reveal, drama"
        },
        {
            "title": "The Matrix",
            "year": 1999,
            "quote": "I know kung fu.",
            "character": "Neo",
            "sentiment": "neutral",
            "tags": "action, learning, technology"
        },
        {
            "title": "Inception",
            "year": 2010,
            "quote": "You mustn't be afraid to dream a little bigger, darling.",
            "character": "Dom Cobb",
            "sentiment": "positive",
            "tags": "dreams, ambition, reality"
        }
    ]
    return pd.DataFrame(movies)

def main():
    # 标题
    st.title("🎬 Movie Quote Finder")
    
    # 初始化数据
    movies_df = init_data()
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["Search", "Analysis", "Info"])
    
    with tab1:
        # 搜索功能
        st.header("Search Movie Quotes")
        
        # 搜索框
        search_query = st.text_input(
            "Enter keywords:",
            placeholder="Search by quote, character, or movie...",
            help="Try searching for 'love', 'power', or a movie title"
        )
        
        # 筛选选项
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sentiment_filter = st.selectbox(
                "Sentiment",
                ["All", "Positive", "Neutral", "Negative"]
            )
        
        with col2:
            year_filter = st.selectbox(
                "Decade",
                ["All", "1970s", "1980s", "1990s", "2000s", "2010s+"]
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Relevance", "Year (Newest)", "Year (Oldest)", "Title"]
            )
        
        # 热门搜索按钮
        st.write("**Quick searches:**")
        quick_cols = st.columns(4)
        
        quick_searches = ["love", "power", "freedom", "life"]
        for i, search in enumerate(quick_searches):
            with quick_cols[i]:
                if st.button(search.capitalize(), use_container_width=True):
                    # 直接使用搜索查询，不修改session_state
                    st.experimental_set_query_params(search=search)
                    st.rerun()
        
        # 执行搜索
        if search_query:
            results = search_movies(movies_df, search_query, sentiment_filter, year_filter)
            display_results(results)
        else:
            # 如果没有搜索词，显示所有电影
            display_results(movies_df)
    
    with tab2:
        # 分析功能
        st.header("Quote Analysis")
        
        # 情感分布图
        st.subheader("Sentiment Distribution")
        
        sentiment_counts = movies_df['sentiment'].value_counts()
        fig1 = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Sentiment Distribution",
            color_discrete_map={
                'positive': '#2ecc71',
                'neutral': '#f39c12', 
                'negative': '#e74c3c'
            }
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # 按年份分布
        st.subheader("Quotes by Year")
        
        year_counts = movies_df.groupby('year').size().reset_index(name='count')
        fig2 = px.bar(
            year_counts,
            x='year',
            y='count',
            title="Number of Quotes by Year"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # 统计信息
        st.subheader("Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Quotes", len(movies_df))
        with col2:
            st.metric("Unique Movies", movies_df['title'].nunique())
        with col3:
            avg_len = movies_df['quote'].str.len().mean()
            st.metric("Avg. Quote Length", f"{avg_len:.0f} chars")
    
    with tab3:
        # 信息页面
        st.header("About This App")
        
        st.markdown("""
        ### 🎬 Movie Quote Finder
        
        This application helps you search and analyze famous movie quotes from classic and modern cinema.
        
        **Features:**
        - 🔍 **Search** by keywords, characters, or movies
        - 🎭 **Filter** by sentiment and decade
        - 📊 **Analyze** sentiment distribution and trends
        - 🏷️ **View** detailed information about each quote
        
        **How to use:**
        1. Enter keywords in the search box
        2. Use filters to narrow down results
        3. Click on quick search buttons for common themes
        4. View analysis in the Analysis tab
        
        **Data Source:**  
        The database contains 10 iconic movie quotes from various genres and time periods.
        
        **Note:** This is a demonstration app for educational purposes.
        
        ---
        
        **Developed for:** Arts and Advanced Big Data Course  
        **Instructor:** Prof. Jahwan Koo  
        **University:** Sungkyunkwan University (SKKU)
        
        © 2024 Movie Quote Finder
        """)

def search_movies(df, query, sentiment, decade):
    """搜索电影台词"""
    # 转换为小写进行不区分大小写的搜索
    query_lower = query.lower()
    
    # 基础过滤
    filtered = df.copy()
    
    # 按关键词过滤
    if query:
        mask = (
            filtered['quote'].str.lower().str.contains(query_lower) |
            filtered['character'].str.lower().str.contains(query_lower) |
            filtered['title'].str.lower().str.contains(query_lower) |
            filtered['tags'].str.lower().str.contains(query_lower)
        )
        filtered = filtered[mask]
    
    # 按情感过滤
    if sentiment != "All":
        filtered = filtered[filtered['sentiment'] == sentiment.lower()]
    
    # 按年代过滤
    if decade != "All":
        decade_map = {
            "1970s": (1970, 1979),
            "1980s": (1980, 1989),
            "1990s": (1990, 1999),
            "2000s": (2000, 2009),
            "2010s+": (2010, 2024)
        }
        if decade in decade_map:
            start_year, end_year = decade_map[decade]
            filtered = filtered[(filtered['year'] >= start_year) & (filtered['year'] <= end_year)]
    
    return filtered

def display_results(df):
    """显示搜索结果"""
    if len(df) == 0:
        st.warning("No quotes found. Try different keywords or filters.")
        return
    
    st.success(f"Found {len(df)} quotes")
    
    # 显示每一条结果
    for i, row in df.iterrows():
        # 使用卡片式布局
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # 主内容
                st.write(f"**\"{row['quote']}\"**")
                st.write(f"🎭 **Character:** {row['character']}")
                st.write(f"🎬 **Movie:** {row['title']} ({row['year']})")
                
                # 情感标签
                sentiment_color = {
                    "positive": "🟢",
                    "neutral": "🟡", 
                    "negative": "🔴"
                }
                st.write(f"📊 **Sentiment:** {sentiment_color[row['sentiment']]} {row['sentiment'].title()}")
                
                # 标签
                st.write(f"🏷️ **Tags:** {row['tags']}")
            
            with col2:
                # 简单的操作按钮
                if st.button("⭐", key=f"fav_{i}", help="Add to favorites"):
                    st.info("Added to favorites!")
                
                if st.button("📋", key=f"copy_{i}", help="Copy quote"):
                    st.info("Quote copied!")
            
            st.divider()

if __name__ == "__main__":
    main()
