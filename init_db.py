import sqlite3
import os

# 数据库路径
DB_PATH = 'notes.db'

# 如果已有数据库文件可选择删除（可选）
# if os.path.exists(DB_PATH):
#     os.remove(DB_PATH)

# 初始化数据库
with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()

    # 创建分类表
    c.execute('''
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # 创建消息表
    c.execute('''
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES category(id)
        )
    ''')

    # 初始化三个默认分类
    default_categories = ['日记', '灵感', '学习笔记']
    for name in default_categories:
        c.execute("INSERT OR IGNORE INTO category (name) VALUES (?)", (name,))

    conn.commit()

print("📦 数据库初始化完成 ✅")
