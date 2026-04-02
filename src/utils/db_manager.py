import sqlite3
import os
import json
from datetime import datetime
from contextlib import contextmanager
from .mahwous_logging import get_logger

_logger = get_logger(__name__)

class DatabaseManager:
    """إدارة قاعدة البيانات المركزية لـ Mahwous V27"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """سياق اتصال آمن وقابل لإعادة الاستخدام مع وضع WAL"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """إنشاء الجداول الأساسية لـ V27"""
        with self.get_connection() as conn:
            # 1. جدول الأحداث (UI Events)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (datetime('now','localtime')),
                    page TEXT,
                    action TEXT,
                    details TEXT
                )
            """)
            
            # 2. جدول القرارات (Pricing Decisions)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (datetime('now','localtime')),
                    product_id TEXT,
                    product_name TEXT,
                    competitor TEXT,
                    old_price REAL,
                    new_price REAL,
                    action TEXT,
                    reason TEXT,
                    pushed_to_make INTEGER DEFAULT 0
                )
            """)
            
            # 3. جدول كتالوج المنافسين (Competitor Catalog)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS comp_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competitor TEXT,
                    product_name TEXT,
                    price REAL,
                    product_url TEXT,
                    image_url TEXT,
                    last_update TEXT,
                    UNIQUE(competitor, product_name)
                )
            """)
            
            # 4. جدول كتالوجنا (Our Catalog)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS our_catalog (
                    product_id TEXT PRIMARY KEY,
                    product_name TEXT,
                    price REAL,
                    cost_price REAL,
                    category TEXT,
                    brand TEXT,
                    last_sync TEXT
                )
            """)

            # 5. جدول روابط المنافسين (Link Library)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS competitor_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_url TEXT,
                    product_url TEXT,
                    discovered_at TEXT,
                    UNIQUE(store_url, product_url)
                )
            """)
            
            conn.commit()
            _logger.info("تم تهيئة قاعدة البيانات V27 بنجاح.")

    def save_competitor_urls(self, store_url, urls):
        """حفظ قائمة الروابط في المكتبة"""
        if not urls: return
        try:
            with self.get_connection() as conn:
                timestamp = datetime.now().isoformat()
                for url in urls:
                    conn.execute("""
                        INSERT OR IGNORE INTO competitor_links (store_url, product_url, discovered_at)
                        VALUES (?, ?, ?)
                    """, (store_url, url, timestamp))
                conn.commit()
                _logger.info(f"تم حفظ {len(urls)} رابط لـ {store_url}")
        except Exception as e:
            _logger.error(f"Error saving competitor urls: {e}")

    def get_competitor_urls(self, store_url):
        """جلب الروابط المحفوظة لمتجر معين"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT product_url FROM competitor_links WHERE store_url = ?", (store_url,))
                return [row['product_url'] for row in cursor.fetchall()]
        except Exception as e:
            _logger.error(f"Error fetching competitor urls: {e}")
            return []

    def get_all_managed_stores(self):
        """جلب قائمة المتاجر المحفوظة وعدد روابطها"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT store_url, COUNT(*) as link_count, MAX(discovered_at) as last_discovery
                    FROM competitor_links
                    GROUP BY store_url
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            _logger.error(f"Error fetching managed stores: {e}")
            return []

    # ... [Keep previous methods log_event, log_decision, upsert_our_catalog]
    def log_event(self, page, action, details=""):
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO events (page, action, details) VALUES (?,?,?)",
                    (page, action, details)
                )
                conn.commit()
        except Exception as e:
            _logger.error(f"Failing to log event: {e}")

    def log_decision(self, decision_dict):
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO decisions 
                    (product_id, product_name, competitor, old_price, new_price, action, reason, pushed_to_make)
                    VALUES (:pid, :name, :comp, :old, :new, :action, :reason, :pushed)
                """, decision_dict)
                conn.commit()
        except Exception as e:
            _logger.error(f"Failing to log decision: {e}")

    def get_stats(self):
        """جلب إحصائيات سريعة للوحة التحكم"""
        try:
            with self.get_connection() as conn:
                our_count = conn.execute("SELECT COUNT(*) FROM our_catalog").fetchone()[0]
                comp_count = conn.execute("SELECT COUNT(DISTINCT competitor) FROM comp_catalog").fetchone()[0]
                total_comp_prods = conn.execute("SELECT COUNT(*) FROM comp_catalog").fetchone()[0]
                today = datetime.now().strftime('%Y-%m-%d')
                updates_today = conn.execute("SELECT COUNT(*) FROM comp_catalog WHERE last_update LIKE ?", (f"{today}%",)).fetchone()[0]
                
                return {
                    "our_products": our_count,
                    "active_competitors": comp_count,
                    "total_competitor_products": total_comp_prods,
                    "updates_today": updates_today
                }
        except Exception as e:
            _logger.error(f"Error fetching stats: {e}")
            return {"our_products": 0, "active_competitors": 0, "total_competitor_products": 0, "updates_today": 0}

    def upsert_our_catalog(self, df):
        """تحديث منتجاتنا بالجملة"""
        if df is None or df.empty: return
        try:
            with self.get_connection() as conn:
                for _, row in df.iterrows():
                    conn.execute("""
                        INSERT INTO our_catalog (product_id, product_name, price, last_sync)
                        VALUES (?,?,?,?)
                        ON CONFLICT(product_id) DO UPDATE SET
                        product_name=excluded.product_name,
                        price=excluded.price,
                        last_sync=excluded.last_sync
                    """, (
                        str(row.get('معرف المنتج', row.get('id', ''))),
                        str(row.get('اسم المنتج', row.get('name', ''))),
                        float(row.get('السعر', 0)),
                        datetime.now().isoformat()
                    ))
                conn.commit()
                _logger.info(f"تم تحديث {len(df)} منتج في كتالوجنا.")
        except Exception as e:
            _logger.error(f"Error in upsert_our_catalog: {e}")

# تصدير الكائن الافتراضي
from config import DB_PATH
db = DatabaseManager(DB_PATH)
